# Botty Robot v0.2.0 Alpha

Botty Robot is the Raspberry Pi edition of Botty, the same expressive
companion available as [Botty Desktop](https://github.com/Uyruw3/BottyDesktop).
This standalone repository contains the robot application and the separate
`botty-robot/` hardware test console.

Botty combines animated eyes, voice interaction, a configurable AI provider,
camera and vision modules, emotions, local memory, plugins, optional sensors,
and a Flask web dashboard. What works depends on the hardware and optional
dependencies you install; motors, sonar, OLED, and reinforcement learning
require explicit setup, and motor/sensor controls are disabled by default.

## Requirements

- Python 3.10 or newer
- Raspberry Pi OS for GPIO and physical peripherals
- Display and audio devices for their respective features
- Optional camera, face recognition, OLED, sonar, motor driver, and gamepad

The project can also run on Windows for development, but Raspberry Pi-specific
hardware features are not available there.

## Install and run

```bash
python -m pip install -e .
python -m botty
```

Install optional features as needed:

```bash
python -m pip install -e ".[web]"    # Flask dashboard
python -m pip install -e ".[vision]" # Face recognition (dlib required)
python -m pip install -e ".[oled]"   # SSD1306 OLED
python -m pip install -e ".[rl]"     # Reinforcement-learning tools
```

The dashboard is optional and, when installed and enabled, is available on
`http://127.0.0.1:5000` via `botty-web`.

## AI provider and credentials

Ollama is the default provider (`qwen2.5:3b`); install and start Ollama
separately, then pull the model on the robot. OpenAI is an alternative; set
`AI_PROVIDER=openai` and `OPENAI_API_KEY` in your local environment or `.env`.
Never commit API keys. Speech recognition may use Google's online service,
depending on the configured speech engine.

## Hardware safety

Motor and sonar support are off by default. Check `botty/config.py`, the
selected motor driver, and your wiring before enabling them. Test with the
wheels raised and keep a power cutoff within reach.

An HC-SR04 sensor has a 5 V echo output: **do not connect it directly to
Raspberry Pi GPIO**. Add a voltage divider or a logic-level shifter to 3.3 V.
Use a suitable external motor supply and share ground with the Pi.

The `botty-robot/` directory contains a stand-alone test console for motors,
sonar, and a buzzer. It automatically stops each movement after a short,
bounded interval. Read [`botty-robot/README.md`](botty-robot/README.md) for the
pinout and test commands before connecting peripherals.

## Tests

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Release and desktop edition

- [Botty Robot releases](https://github.com/Uyruw3/BottyRobot/releases)
- [Botty Desktop for Windows](https://github.com/Uyruw3/BottyDesktop)
- [Botty project website](https://uyruw3.github.io/BottyTheRobot/)
