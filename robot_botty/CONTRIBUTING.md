# Contributing to Botty Prototype

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd BottyRobot
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Install dev dependencies:
   ```bash
   pip install pytest
   ```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names in Spanish
- Write docstrings for public functions and classes
- Keep functions focused on a single responsibility
- Mimic existing code patterns for consistency

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test file:
```bash
python -m pytest tests/test_emotion.py -v
```

## Adding a Plugin

1. Create a new file in `botty/plugins/examples/`
2. Extend `BasePlugin` and implement `on_event()`
3. Set appropriate events and priority
4. Test with `python -m pytest tests/test_plugins.py -v`

## Commit Messages

Use the format: `tipo(alcance): descripcion`

Types: feat, fix, docs, style, refactor, test, chore

Examples:
- `feat(eyes): add new expression for winking`
- `fix(plugins): handle missing plugin directory`
- `docs(readme): update installation instructions`

## Pull Request Process

1. Create a feature branch from main
2. Add tests for new functionality
3. Ensure all existing tests pass
4. Update documentation if needed
5. Submit PR with clear description of changes

## Project Structure

```
botty/
  __main__.py          # Entry point
  main.py              # Robot main loop
  config.py            # Runtime and hardware configuration
  ai/                  # Ollama/OpenAI and tool calling
  audio/               # Speech recognition and synthesis
  display/             # Pygame and OLED displays
  emotion/             # Emotion system
  eyes/                # Eye rendering and animations
  memory/              # Conversation and face memory
  movement/            # Motor control
  plugins/             # Plugin system and examples
  rl/                  # Reinforcement learning
  sensors/             # Ultrasonic sensors
  vision/              # Camera and face recognition
  web/                 # Optional web dashboard
botty-robot/           # Stand-alone GPIO test console
tests/                 # Test suite
scripts/               # Launchers and utilities
```
