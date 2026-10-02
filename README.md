# Botty: dos ediciones y una herramienta de hardware

Botty Prototype y Botty Desktop son el mismo compañero en dos ediciones: una
para el robot físico y otra para Windows. `botty-robot/` es una herramienta
complementaria e independiente para probar/controlar hardware Raspberry Pi.
El código de cada edición se mantiene en su propia carpeta y tiene un Release
independiente.

## Sitio web

La [página de presentación de Botty](https://uyruw3.github.io/BottyTheRobot/)
está publicada con GitHub Pages desde [`docs/`](docs/) en la rama
`uyruw3-botty-project`. Presenta las dos ediciones del mismo Botty y su
herramienta complementaria, explica el flujo de interacción, los requisitos,
la configuración de IA, la privacidad y las precauciones de hardware. Después
de integrar el cambio en `main`, se puede cambiar la fuente de Pages a `main`
y conservar `/docs` como carpeta.

| Producto / edición | Carpeta | Destino |
| --- | --- | --- |
| Botty Prototype | `robot_botty/` | Edición física de Botty para Raspberry Pi: sensores, movimiento, voz, visión, emociones y dashboard |
| Botty Desktop | `botty-desktop/` | Edición de escritorio del mismo Botty para Windows: ojos animados, conversación y acciones de pantalla |
| Botty Robot Hardware | `botty-robot/` | Herramienta complementaria para probar motores, sonar y buzzer en Raspberry Pi |

Botty y su controlador son proyectos experimentales. Revisa el README de cada
carpeta antes de instalar software o conectar hardware.

## Botty Prototype (edición física)

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

## Botty Desktop (edición Windows del mismo Botty)

```powershell
cd botty-desktop
python -m pip install -e ".[voice]"
botty
```

Instala Tesseract OCR para leer la pantalla. La entrada por micrófono es
opcional: `python -m pip install -e ".[microphone]"`. Consulta
`botty-desktop/README.md` para los extras de voz e IA local y sus requisitos.
