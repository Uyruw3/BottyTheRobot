#!/bin/bash
# ── Configura Raspberry Pi 5 como USB Ethernet Gadget ──
#
# Permite que la Pi aparezca como un adaptador de red
# cuando se conecta al PC por el puerto USB-C.
#
# Asi podemos flashear Botty con solo conectar un cable USB.
#
# Uso:
#   bash scripts/setup_usb_gadget.sh
#
# Requiere: Raspberry Pi 5 (o Pi Zero 2W con OTG)
# ─────────────────────────────────────────────────────────

set -e

echo "=============================="
echo "  USB Gadget — Configuracion"
echo "=============================="

if [ "$(id -u)" -ne 0 ]; then
    echo "Ejecutar como root: sudo bash $0"
    exit 1
fi

# ── 1. Habilitar dwc2 driver ──
echo ""
echo "[1/4] Habilitando driver USB gadget..."
if ! grep -q "dtoverlay=dwc2" /boot/firmware/config.txt 2>/dev/null; then
    echo "dtoverlay=dwc2" >> /boot/firmware/config.txt
    echo "  -> dtoverlay=dwc2 anadido a config.txt"
else
    echo "  -> dtoverlay=dwc2 ya existe"
fi

if ! grep -q "dwc2" /etc/modules 2>/dev/null; then
    echo "dwc2" >> /etc/modules
    echo "  -> dwc2 anadido a modules"
fi

if ! grep -q "libcomposite" /etc/modules 2>/dev/null; then
    echo "libcomposite" >> /etc/modules
    echo "  -> libcomposite anadido a modules"
fi

# ── 2. Crear script de gadget ──
echo ""
echo "[2/4] Creando script de gadget USB..."
GADGET_SCRIPT="/usr/local/bin/usb-gadget.sh"

cat > "$GADGET_SCRIPT" << 'GADGET'
#!/bin/bash
# USB Ethernet Gadget — Pi aparece como adaptador de red USB

modprobe dwc2
modprobe libcomposite

sleep 1

cd /sys/kernel/config/usb_gadget/
mkdir -p g1
cd g1

# IDs USB (Raspberry Pi)
echo 0x1d6b > idVendor   # Linux Foundation
echo 0x0104 > idProduct  # Multifunction Composite Gadget
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB

# Strings
mkdir -p strings/0x409
echo "1234567890" > serialnumber
echo "Raspberry Pi" > manufacturer
echo "Botty Robot" > product

# Configuration
mkdir -p configs/c.1/strings/0x409
echo "ECM" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# Ethernet (ECM) — aparece como adaptador de red en el PC
mkdir -p functions/ecm.usb0
echo "02:11:22:33:44:55" > functions/ecm.usb0/host_addr
echo "02:11:22:33:44:56" > functions/ecm.usb0/dev_addr

ln -s functions/ecm.usb0 configs/c.1/

# Activar
echo 0x0010 > os_desc/b_vendor_code
echo MSFT100 > os_desc/qw_sign
echo 1 > os_desc/use
ln -s configs/c.1 os_desc

# Usar UDC (el controlador USB disponible)
UDC=$(ls /sys/class/udc/ | head -1)
echo "$UDC" > UDC

# Configurar IP en la interfaz
sleep 2
ip addr add 10.0.0.2/24 dev usb0 2>/dev/null || true
ip link set usb0 up

echo "USB Gadget activado: $UDC"
GADGET

chmod +x "$GADGET_SCRIPT"
echo "  -> Creado $GADGET_SCRIPT"

# ── 3. Crear servicio systemd ──
echo ""
echo "[3/4] Creando servicio systemd..."

cat > /etc/systemd/system/usb-gadget.service << 'SERVICE'
[Unit]
Description=USB Ethernet Gadget
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/usb-gadget.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable usb-gadget.service
echo "  -> Servicio usb-gadget activado"

# ── 4. Habilitar SSH ──
echo ""
echo "[4/4] Asegurando SSH activado..."
systemctl enable ssh 2>/dev/null || true
systemctl start ssh 2>/dev/null || true
echo "  -> SSH activado"

# ── Fin ──
echo ""
echo "=============================="
echo "  Configuracion completada!"
echo "=============================="
echo ""
echo "  Ahora cuando conectes la Pi al PC por USB-C:"
echo "  1. La Pi aparecera como adaptador de red"
echo "  2. IP de la Pi: 10.0.0.2"
echo "  3. Conectate: ssh pi@10.0.0.2"
echo "  4. O usa el flasher: flash_botty.exe"
echo ""
echo "  REINICIA para aplicar: sudo reboot"
