# Botty Desktop

Botty Desktop is the Windows desktop companion: an animated Pygame face with
local conversation memory, optional speech, and Windows app, web-search, and
screen-reading actions. It is a separate product from both Raspberry Pi robot
projects in this repository.

## Requirements

- Windows 10 or newer
- Python 3.10 or newer
- Tesseract OCR installed and available on `PATH` for screen-reading actions

## Install and run

```powershell
cd botty-desktop
python -m pip install -e ".[voice]"
botty
```

Speech recognition and online text-to-speech are optional. Install
`python -m pip install -e ".[microphone]"` to enable microphone input; Windows
may require a compatible PyAudio wheel. Local GGUF model support is available
with `python -m pip install -e ".[local-ai]"`; place the model in `botty/models/`.

To run tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Privacy and safety

Screen-reading uses Tesseract on a screenshot captured only when requested.
Voice recognition may use Google's online speech service. Keep API keys and
personal model files out of source control. App-launch commands can start
programs on the Windows machine; review actions before enabling voice control.
