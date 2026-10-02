#!/usr/bin/env python3
"""
Botty Flasher — Instala Botty en una Raspberry Pi automaticamente.
Modos de conexion:
  1. USB Gadget (auto): Pi conectada por USB-C, IP 10.0.0.2
  2. Red local: busca raspberrypi.local o IP manual
  3. SD Card: copia directamente a una unidad montada

Uso:
  flash_botty.exe              # modo automatico
  flash_botty.exe --ip 10.0.0.2
  flash_botty.exe --drive D:
  flash_botty.exe --help
"""

import argparse
import getpass
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

try:
    import paramiko
except ImportError:
    paramiko = None


# ── Config ──────────────────────────────────────────────

PROJECT_NAME = "botty-robot"
PI_USER = "pi"
PI_PASS = "raspberry"
PI_HOSTNAME = "raspberrypi"
USB_GADGET_IP = "10.0.0.2"
USB_GADGET_PORT = 22
PI_INSTALL_DIR = f"/home/{PI_USER}/{PROJECT_NAME}"

BANNER = """
╔══════════════════════════════════════════╗
║         Botty Flasher v1.0              ║
║   Instala tu robot en Raspberry Pi      ║
╚══════════════════════════════════════════╝
"""


# ── Utils ───────────────────────────────────────────────

def _find_project_root() -> Path:
    """Encuentra la raiz del proyecto (donde esta pyproject.toml)."""
    d = Path(__file__).resolve().parent.parent
    if (d / "pyproject.toml").exists():
        return d
    # Cuando se ejecuta desde .exe con PyInstaller, los archivos estan en _MEIPASS
    if getattr(sys, "frozen", False):
        meipass = Path(sys._MEIPASS)
        if (meipass / "pyproject.toml").exists():
            return meipass
    return d


def _get_files_to_copy(root: Path) -> list[Path]:
    """Lista todos los archivos del proyecto a copiar."""
    exclude = {
        "__pycache__", ".git", ".venv", "venv", ".env",
        "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db",
        "build", "dist", "*.spec",
    }
    files = []
    for f in root.rglob("*"):
        if f.is_dir():
            continue
        rel = f.relative_to(root)
        parts = set(rel.parts)
        if exclude & parts:
            continue
        if any(f.match(p) for p in exclude if "*" in p):
            continue
        if f.suffix in (".pyc", ".pyo"):
            continue
        files.append(f)
    return files


def _print_status(msg: str, ok: bool | None = None):
    prefix = {True: "  ✓", False: "  ✗", None: "  →"}.get(ok, "  →")
    print(f"{prefix} {msg}")


# ── Connection Detectors ────────────────────────────────

def detect_usb_gadget() -> str | None:
    """Detecta Pi en modo USB Ethernet gadget (IP 10.0.0.2)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((USB_GADGET_IP, USB_GADGET_PORT))
        sock.close()
        if result == 0:
            return USB_GADGET_IP
    except Exception:
        pass
    return None


def detect_mdns() -> str | None:
    """Intenta resolver raspberrypi.local via mDNS."""
    candidates = [
        f"{PI_HOSTNAME}.local",
        "raspberrypi",
        "botty.local",
    ]
    for host in candidates:
        try:
            ip = socket.gethostbyname(host)
            # Verify SSH is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, USB_GADGET_PORT))
            sock.close()
            if result == 0:
                return ip
        except Exception:
            continue
    return None


def detect_sd_card() -> str | None:
    """Busca una unidad montada con partition boot de Raspberry Pi."""
    if platform.system() == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:"
            try:
                if os.path.exists(f"{drive}\\boot"):
                    return drive
                if os.path.exists(f"{drive}\\kernel.img"):
                    return drive
                if os.path.exists(f"{drive}\\kernel8.img"):
                    return drive
                if os.path.exists(f"{drive}\\config.txt"):
                    return drive if os.path.isfile(f"{drive}\\config.txt") else None
            except Exception:
                continue
    else:
        for mnt in Path("/media").iterdir():
            if mnt.is_dir() and (mnt / "config.txt").exists():
                return str(mnt)
        if Path("/boot/config.txt").exists():
            return "/boot"
    return None


# ── SSH Installer ───────────────────────────────────────

class SSHInstaller:
    def __init__(self, host: str, port: int = 22, user: str = PI_USER,
                 password: str | None = None, key_file: str | None = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.key_file = key_file
        self.client: paramiko.SSHClient | None = None

    def connect(self) -> bool:
        if paramiko is None:
            _print_status("paramiko no instalado (pip install paramiko)", False)
            return False

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user,
            "timeout": 10,
        }

        if self.key_file:
            connect_kwargs["key_filename"] = self.key_file
        elif self.password:
            connect_kwargs["password"] = self.password
        else:
            connect_kwargs["password"] = PI_PASS

        try:
            self.client.connect(**connect_kwargs)
            _print_status(f"Conectado a {self.user}@{self.host}:{self.port}", True)
            return True
        except paramiko.AuthenticationException:
            _print_status("Autenticacion fallida", False)
            return False
        except Exception as e:
            _print_status(f"No se pudo conectar: {e}", False)
            return False

    def exec(self, command: str, timeout: int = 60) -> tuple[str, str, int]:
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code

    def is_installed(self) -> bool:
        """Verifica si Botty ya esta instalado en la Pi."""
        stdout, _, code = self.exec("test -f ~/.botty/venv/bin/activate && echo yes")
        return "yes" in stdout

    def check_missing_packages(self) -> list[str]:
        """Detecta que paquetes Python faltan en la Pi."""
        required = ["pygame", "opencv-python", "face_recognition",
                    "SpeechRecognition", "pyttsx3", "openai",
                    "duckduckgo_search", "yt-dlp"]
        missing = []
        for pkg in required:
            stdout, _, _ = self.exec(
                f"source ~/.botty/venv/bin/activate && "
                f"python -c \"import {pkg.replace('-', '_').split('[')[0]}\" 2>/dev/null && "
                f"echo ok || echo fail"
            )
            if "ok" not in stdout:
                missing.append(pkg)
        return missing

    def upload_files(self, root: Path, files: list[Path]):
        _print_status("Subiendo archivos a la Pi...")
        sftp = self.client.open_sftp()

        try:
            sftp.mkdir(PI_INSTALL_DIR)
        except IOError:
            pass

        total = len(files)
        for i, f in enumerate(files):
            rel = f.relative_to(root)
            dest = Path(PI_INSTALL_DIR) / rel
            try:
                sftp.mkdir(str(dest.parent))
            except IOError:
                pass
            sftp.put(str(f), str(dest))
            _print_progress(i + 1, total, f"  Subiendo {rel}")

        sftp.close()
        _print_status(f"Subidos {total} archivos", True)

    def run_install(self, force: bool = False):
        already = self.is_installed()

        if already and not force:
            _print_status("Botty ya estaba instalado — modo actualizacion", True)
            missing = self.check_missing_packages()
            if missing:
                _print_status(f"Faltan {len(missing)} paquetes: {', '.join(missing)}", None)
                _print_status("Ejecutando instalacion completa...")
                mode = ""
            else:
                _print_status("Todas las dependencias OK, solo actualizando codigo", True)
                mode = "--update"
        else:
            _print_status("Primera instalacion detectada", None)
            mode = ""

        cmd = (
            f"cd {PI_INSTALL_DIR} && "
            f"chmod +x scripts/install.sh && "
            f"sudo bash scripts/install.sh {mode}"
        )
        stdout, stderr, code = self.exec(cmd, timeout=300)

        for line in stdout.split("\n"):
            if line.strip():
                print(f"  [Pi] {line.strip()}")
        if stderr.strip():
            for line in stderr.split("\n"):
                line = line.strip()
                if line and "WARNING" not in line and "already" not in line:
                    print(f"  [Pi] {line}")

        if code == 0:
            _print_status("Instalacion completada en la Pi", True)
        else:
            _print_status(f"Instalacion fallo con codigo {code}", False)

    def close(self):
        if self.client:
            self.client.close()


# ── SD Card Installer ───────────────────────────────────

class SDCardInstaller:
    def __init__(self, mount_point: str):
        self.mount = Path(mount_point)
        self.dest = self.mount / PROJECT_NAME

    def install(self, root: Path, files: list[Path]):
        _print_status(f"Copiando a {self.dest}...")
        self.dest.mkdir(parents=True, exist_ok=True)

        total = len(files)
        for i, f in enumerate(files):
            rel = f.relative_to(root)
            dest = self.dest / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            _print_progress(i + 1, total, f"  Copiando {rel}")

        _print_status(f"Copiados {total} archivos a {self.dest}", True)

        # Crear script de instalacion para ejecutar en la Pi
        boot_script = self.mount / "botty_install.sh"
        boot_script.write_text(f"""#!/bin/bash
cd /home/{PI_USER}/{PROJECT_NAME}
bash scripts/install.sh
""")
        boot_script.chmod(0o755)
        _print_status("Script de instalacion listo en la tarjeta SD", True)


# ── Progress ─────────────────────────────────────────────

def _print_progress(current: int, total: int, label: str = ""):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    pct = int(100 * current / total)
    end = "\n" if current == total else "\r"
    print(f"\r  {bar} {pct}%  {label}", end=end, flush=True)


# ── Main ─────────────────────────────────────────────────

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Instala Botty Robot en una Raspberry Pi",
        epilog="Ejemplos:\n  flash_botty.exe\n  flash_botty.exe --ip 10.0.0.2\n  flash_botty.exe --drive D:",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--ip", help="Direccion IP de la Pi (SSH)")
    parser.add_argument("--port", type=int, default=22, help="Puerto SSH (default: 22)")
    parser.add_argument("--user", default=PI_USER, help=f"Usuario SSH (default: {PI_USER})")
    parser.add_argument("--password", help="Contrasena SSH")
    parser.add_argument("--key", help="Ruta a clave privada SSH")
    parser.add_argument("--drive", help="Unidad SD Card (ej: D:)")
    parser.add_argument("--no-auto", action="store_true",
                        help="Desactiva deteccion automatica")
    parser.add_argument("--force", action="store_true",
                        help="Forzar instalacion completa aunque ya exista")
    args = parser.parse_args()

    # ── Find project root ──
    root = _find_project_root()
    _print_status(f"Proyecto: {root}")
    files = _get_files_to_copy(root)
    _print_status(f"Archivos a copiar: {len(files)}")

    # ── Detect Pi connection ──
    target_ip = args.ip
    target_drive = args.drive

    if not target_ip and not target_drive and not args.no_auto:
        _print_status("Buscando Raspberry Pi...")

        # 1. Try USB gadget
        ip = detect_usb_gadget()
        if ip:
            _print_status(f"Pi detectada via USB gadget: {ip}", True)
            target_ip = ip

        # 2. Try mDNS
        if not target_ip:
            ip = detect_mdns()
            if ip:
                _print_status(f"Pi detectada por hostname: {ip}", True)
                target_ip = ip

        # 3. Try SD card
        if not target_ip:
            drive = detect_sd_card()
            if drive:
                _print_status(f"Tarjeta SD detectada: {drive}", True)
                target_drive = drive

        if not target_ip and not target_drive:
            _print_status("No se detecto ninguna Pi automaticamente", False)
            _print_status("Usa --ip <IP> o --drive <letra> para especificar manualmente")
            return 1

    # ── Install via SSH ──
    if target_ip:
        password = args.password
        if not password and not args.key:
            print()
            password = getpass.getpass(f"  Contrasena SSH para {args.user}@{target_ip}: ")
            if not password:
                password = PI_PASS

        installer = SSHInstaller(
            host=target_ip,
            port=args.port,
            user=args.user,
            password=password,
            key_file=args.key,
        )

        if not installer.connect():
            _print_status("No se pudo establecer conexion SSH", False)
            return 1

        installer.upload_files(root, files)
        installer.run_install(force=args.force)
        installer.close()

        print()
        _print_status("Instalacion completada por SSH", True)
        print(f"\n  Botty se lanzara automaticamente al reiniciar la Pi.")
        print(f"  O ejecuta: ssh {args.user}@{target_ip}")
        print(f"    cd {PI_INSTALL_DIR} && source ~/.botty/venv/bin/activate && botty")
        return 0

    # ── Install via SD Card ──
    if target_drive:
        installer = SDCardInstaller(target_drive)
        installer.install(root, files)

        print()
        _print_status("Archivos copiados a la tarjeta SD", True)
        print(f"\n  Pasos siguientes:")
        print(f"  1. Inserta la SD en la Pi y enciendela")
        print(f"  2. Conectate por SSH y ejecuta:")
        print(f"     cd {PROJECT_NAME} && bash scripts/install.sh")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
