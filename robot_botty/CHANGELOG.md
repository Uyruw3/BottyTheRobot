# Changelog

## [0.1.0] - 2026-05-24

### Added
- Initial prototype release
- EMO-style eye renderer with rounded rects, arch mode, pupil tracking, asymmetric blink
- Emotion system with valence/arousal 2D mood model, 15 emotion states, personality presets
- Vector memory with TF-IDF, cosine similarity, JSON persistence
- Web dashboard with Flask, MJPEG camera stream, motor control, expression buttons, AI chat
- Plugin system with file-based discovery, priority ordering, 26 event types
- 16 example plugins (greeter, music, weather, timer, screenshot, volume, wallpaper, pomodoro,
  translator, calculator, dice, quote, compliment, alarm, notes, countdown, joke, reminder, echo, mood light)
- Reinforcement learning trainer with ObstacleAvoidanceEnv, curriculum learning
- Desktop window manipulation (wiggle, nudge, minimize, shake)
- Knowledge base with personality, trivia, jokes, Spanish responses
- Desktop mode with mouse tracking, touch reactions, text chat (ENTER key)
- Microphone always active via background thread + queue
- Idle behaviors: random complaints, blinks, desktop window manipulation
- 13+ test files covering all major subsystems
- Spanish voice interaction with pyttsx3/gTTS support
- Ollama (Qwen2.5 3B) and OpenAI GPT integration
- 13 test files with 144+ tests
- Comprehensive README with documentation

### Known Issues
- Full hardware features require Raspberry Pi (face_recognition, dlib, RPi.GPIO, luma.oled)
- Flask web dashboard requires optional `web` extra
- RL training requires gymnasium and stable-baselines3 (optional)
- Windows compatibility limited for hardware modules
- Voice output requires pyttsx3 or gTTS installation
