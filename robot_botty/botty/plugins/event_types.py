"""
Plugin event types — eventos que los plugins pueden escuchar.
"""


class PluginEvent:
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    EYE_EXPRESSION_CHANGED = "eye_expression_changed"
    FACE_DETECTED = "face_detected"
    FACE_RECOGNIZED = "face_recognized"
    FACE_LOST = "face_lost"
    VOICE_COMMAND = "voice_command"
    AI_RESPONSE = "ai_response"
    MODE_CHANGED = "mode_changed"
    MOTOR_COMMAND = "motor_command"
    SENSOR_READING = "sensor_reading"
    OBSTACLE_DETECTED = "obstacle_detected"
    OBJECT_DETECTED = "object_detected"
    MUSIC_STARTED = "music_started"
    MUSIC_STOPPED = "music_stopped"
    CONTROLLER_ACTION = "controller_action"
    DEVELOPER_MODE_ON = "developer_mode_on"
    DEVELOPER_MODE_OFF = "developer_mode_off"
    USER_GREETED = "user_greeted"
    EMOTION_CHANGED = "emotion_changed"
    BATTERY_STATUS = "battery_status"
    TICK = "tick"
    WEB_COMMAND = "web_command"

    ALL = [
        STARTUP, SHUTDOWN, EYE_EXPRESSION_CHANGED,
        FACE_DETECTED, FACE_RECOGNIZED, FACE_LOST,
        VOICE_COMMAND, AI_RESPONSE, MODE_CHANGED,
        MOTOR_COMMAND, SENSOR_READING, OBSTACLE_DETECTED,
        OBJECT_DETECTED, MUSIC_STARTED, MUSIC_STOPPED,
        CONTROLLER_ACTION, DEVELOPER_MODE_ON, DEVELOPER_MODE_OFF,
        USER_GREETED, EMOTION_CHANGED, BATTERY_STATUS,
        TICK, WEB_COMMAND,
    ]
