# Botty: tres proyectos independientes

Este repositorio conserva tres proyectos distintos; no son versiones
intercambiables ni se combinan en una sola aplicación. Cada uno tiene su propia
carpeta y se publicará con un Release y un archivo fuente independiente.

| Proyecto | Carpeta | Destino |
| --- | --- | --- |
| Botty Prototype | `robot_botty/` | Prototipo completo del robot físico: movimiento, sensores, voz, visión, emociones y dashboard |
| Botty Robot Hardware | `botty-robot/` | Controlador GPIO y consola segura para probar motores, sonar y buzzer en Raspberry Pi |
| Botty Desktop | `botty-desktop/` | Aplicación de escritorio para Windows con ojos animados, conversación y acciones de pantalla |

Los tres son proyectos experimentales. Revisa el README de cada carpeta antes
de instalar o conectar hardware.

## Botty Prototype

```powershell
cd robot_botty
python -m pip install -e ".[web]"
python -m botty
```

Para instalar sus pruebas:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

Los extras `vision`, `rl` y `oled` instalan reconocimiento facial, aprendizaje
por refuerzo y pantalla OLED, respectivamente. No instales `vision` en Windows
sin las herramientas nativas que necesita `dlib`.

## Botty Robot Hardware

```bash
cd botty-robot
python -m pip install -e .
botty-robot
```

La consola detiene automáticamente los motores después de cada movimiento.
Consulta `botty-robot/README.md` para el mapa de pines BCM y las advertencias
eléctricas; el eco de 5 V de un HC-SR04 requiere adaptación antes de conectarlo
a una Raspberry Pi.

## Botty Desktop

```powershell
cd botty-desktop
python -m pip install -e ".[voice]"
botty
```

Instala Tesseract OCR para leer la pantalla. La entrada por micrófono es
opcional: `python -m pip install -e ".[microphone]"`. Consulta
`botty-desktop/README.md` para los extras de voz e IA local y sus requisitos.
