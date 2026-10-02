# Botty

**Botty es un compañero expresivo que puede vivir en tu PC Windows o en un
robot Raspberry Pi.** Tiene ojos animados, conversación, voz y memoria; la
edición física puede conectarse además a una cámara, sensores y motores.
Prototype y Desktop son dos ediciones del mismo Botty, no productos distintos.
El controlador `botty-robot/` es una herramienta separada para probar el
hardware del robot.

[Visita la página web de Botty](https://uyruw3.github.io/BottyTheRobot/) ·
[Explora los Releases](https://github.com/Uyruw3/BottyTheRobot/releases) ·
[Lee cómo funciona](https://uyruw3.github.io/BottyTheRobot/#funcionamiento)

## Cómo funciona

Botty repite un ciclo de interacción:

1. **Recibe una entrada.** Puedes escribir o hablarle; en la edición física
   también puede percibir imágenes de una cámara y entradas de sensores.
2. **Interpreta lo que ocurre.** Las funciones sencillas, como saludos y
   comandos reconocidos, se resuelven directamente. Para preguntas abiertas,
   envía el texto y el contexto de la conversación al motor de IA configurado.
3. **Decide qué hacer.** Puede responder, mostrar una expresión, usar una
   herramienta disponible o, si está configurado y habilitado, interactuar con
   el hardware.
4. **Responde.** Los ojos animados expresan el estado de Botty. La voz es
   opcional; las conversaciones y recuerdos se guardan localmente.

Las funciones disponibles dependen de la edición, del hardware conectado y de
los extras que instales. No todas las funciones descritas requieren estar
activadas ni vienen habilitadas por defecto.

## Dos ediciones del mismo Botty

| Edición | Carpeta | Qué incluye |
| --- | --- | --- |
| **Botty Desktop** — Windows | [`botty-desktop/`](botty-desktop/) | Ventana de ojos animados, chat por teclado, memoria local, acciones de escritorio y voz opcional. |
| **Botty Prototype** — Raspberry Pi | [`robot_botty/`](robot_botty/) | El mismo compañero adaptado al robot: voz, cámara, visión, emociones, memoria, plugins y dashboard web; el movimiento físico requiere hardware y configuración. |
| **Botty Robot Hardware** — herramienta | [`botty-robot/`](botty-robot/) | Consola independiente para probar motores, sonar y buzzer de Raspberry Pi, con movimientos temporizados y modo de simulación. |

Los Releases de cada edición también son independientes: [Desktop](https://github.com/Uyruw3/BottyTheRobot/releases/tag/botty-desktop-v0.1.0),
[Prototype](https://github.com/Uyruw3/BottyTheRobot/releases/tag/robot_botty-v0.1.0)
y [Robot Hardware](https://github.com/Uyruw3/BottyTheRobot/releases/tag/botty-robot-v0.1.0).

## Empezar en Windows

Necesitas Python 3.10 o superior:

```powershell
cd botty-desktop
python -m pip install -e ".[voice]"
botty
```

Se abre la ventana de Botty. Pulsa `Enter` para escribir y otra vez para enviar;
`V` inicia una escucha puntual; `Esc` cierra la aplicación. Si instalas los
extras `voice` y `microphone` con un dispositivo compatible, el micrófono queda
escuchando y puedes comenzar la frase con “Boti”. Al hacer clic en la ventana,
Botty reacciona.

El motor generativo de esta edición requiere opcionalmente `local-ai` y un
modelo GGUF en `botty/models/`. Sin ese modelo, las acciones directas siguen
disponibles, pero no las respuestas generativas. La lectura de pantalla
requiere Tesseract OCR instalado en Windows.

## Empezar con el prototipo físico

Necesitas Raspberry Pi y los periféricos que quieras usar:

```bash
cd robot_botty
python -m pip install -e ".[web]"
python -m botty
```

El dashboard Flask es opcional; con el extra `web` puedes iniciarlo con
`botty-web`. El motor de IA usa Ollama local por defecto; también se puede
configurar OpenAI con una clave propia. Cámara, micrófono, voz, OLED, sensores,
dashboard y motores dependen de sus requisitos y ajustes específicos. Los
motores y el sonar están desactivados inicialmente: revisa la configuración y
el cableado antes de habilitarlos.

Para probar el hardware por separado, instala la herramienta:

```bash
cd botty-robot
python -m pip install -e .
botty-robot
```

La consola ofrece `forward`, `backward`, `left`, `right`, `stop`, `distance` y
`beep`. Cada movimiento se detiene automáticamente: 0,3 segundos por defecto
y un máximo de 2 segundos. Sin `RPi.GPIO`, solo simula y no mueve motores.

## IA, datos y privacidad

- **Botty Desktop:** el chat generativo usa un modelo GGUF local opcional. El
  reconocimiento de voz y la síntesis se instalan por separado; el
  reconocedor de voz puede usar el servicio en línea de Google.
- **Botty Prototype:** Ollama local es el proveedor predeterminado. Si
  configuras OpenAI, las consultas se envían a ese servicio usando tu propia
  clave. La voz puede usar un reconocedor en línea, según la configuración.
- **Memoria:** los recuerdos y el historial persistente se guardan localmente.
  No incluyas archivos de memoria, modelos ni claves en commits o Releases.
- **Acciones de escritorio:** Botty puede abrir aplicaciones y, cuando se lo
  pides, leer la pantalla con OCR. Revisa qué acciones habilitas y evita
  introducir información sensible en servicios en línea.

## Seguridad del hardware

Los proyectos son prototipos experimentales, no productos certificados.
Levanta las ruedas antes de probar motores, ten un corte de alimentación a mano
y confirma la dirección de giro y el cableado. **No conectes directamente el
eco de 5 V de un HC-SR04 a una Raspberry Pi**: utiliza un divisor de tensión o
un adaptador de nivel lógico de 3,3 V. Consulta
[`botty-robot/README.md`](botty-robot/README.md) y
[`robot_botty/README.md`](robot_botty/README.md) antes de conectar periféricos.

## Pruebas

Cada proyecto tiene su propio entorno y pruebas:

```powershell
# En robot_botty/
python -m pip install -e ".[dev]"
python -m pytest

# En botty-desktop/ o botty-robot/
python -m pip install -e ".[dev]"
python -m pytest
```

## Página web

La página de presentación está en [`docs/`](docs/) y publicada con
[GitHub Pages](https://uyruw3.github.io/BottyTheRobot/). Explica el flujo de
interacción, las ediciones, la instalación, privacidad y precauciones del
hardware.
