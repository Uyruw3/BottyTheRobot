"""
Animation reference — documentation and reference data for eye animations.
Includes all expression parameter ranges, transition curves, and animation blueprints.
"""

EXPRESSION_PARAMETER_RANGES = {
    "scaleY": {
        "min": 0.0,
        "max": 2.0,
        "default": 1.0,
        "description": "Escala vertical del ojo. 0 = cerrado, 1 = normal, 2 = muy abierto",
    },
    "scaleX": {
        "min": 0.5,
        "max": 1.5,
        "default": 1.0,
        "description": "Escala horizontal del ojo. <1 = estrecho, >1 = ancho",
    },
    "squint": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Entrecerrar ojos. 0 = abierto, 1 = completamente entrecerrado",
    },
    "arch": {
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Arco de la ceja/párpado. Negativo = triste, Positivo = feliz",
    },
    "look_x": {
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Direccion horizontal de la mirada. -1 = izquierda, +1 = derecha",
    },
    "look_y": {
        "min": -1.0,
        "max": 1.0,
        "default": 0.0,
        "description": "Direccion vertical de la mirada. -1 = arriba, +1 = abajo",
    },
    "pupil_size": {
        "min": 4,
        "max": 24,
        "default": 14,
        "description": "Tamano de la pupila en pixeles",
    },
    "eye_color": {
        "type": "tuple(r,g,b)",
        "description": "Color del iris del ojo. Cada componente 0-255",
    },
    "duration": {
        "min": 0.01,
        "max": 5.0,
        "default": 0.3,
        "description": "Duracion de la expresion en segundos",
    },
}

EXPRESSION_GROUPS = {
    "alegria": {
        "name": "Alegria",
        "emotions": ["happy", "joyful", "excited", "ecstatic", "playful", "cheerful"],
        "typical_params": {"scaleY": 0.5, "scaleX": 1.1, "squint": 0.4, "arch": 0.7},
    },
    "tristeza": {
        "name": "Tristeza",
        "emotions": ["sad", "sorrowful", "mournful", "devastated", "grieving"],
        "typical_params": {"scaleY": 0.4, "scaleX": 0.9, "squint": 0.6, "arch": -0.3, "look_y": 0.2},
    },
    "enojo": {
        "name": "Enojo",
        "emotions": ["angry", "furious", "annoyed", "frustrated", "menacing"],
        "typical_params": {"scaleY": 0.6, "scaleX": 0.9, "squint": 0.6, "arch": 0.0, "look_y": -0.3},
    },
    "sorpresa": {
        "name": "Sorpresa",
        "emotions": ["surprised", "amazed", "shocked", "dramatic", "scared_pop"],
        "typical_params": {"scaleY": 1.5, "scaleX": 0.85, "squint": 0.0, "arch": 0.0},
    },
    "amor": {
        "name": "Amor",
        "emotions": ["loving", "grateful", "loving_soft", "loving_glow", "bashful"],
        "typical_params": {"scaleY": 0.75, "scaleX": 1.05, "squint": 0.3, "arch": 0.5},
    },
    "confusion": {
        "name": "Confusion",
        "emotions": ["confused", "suspicious", "side_eye", "contemplative"],
        "typical_params": {"scaleY": 0.85, "scaleX": 0.95, "squint": 0.15, "arch": 0.0, "look_x": -0.3},
    },
    "sueno": {
        "name": "Sueno",
        "emotions": ["sleepy", "tired", "bored", "sleepy_heavy", "half_mast"],
        "typical_params": {"scaleY": 0.2, "scaleX": 1.0, "squint": 0.85, "arch": 0.0, "look_y": 0.15},
    },
    "miedo": {
        "name": "Miedo",
        "emotions": ["scared", "terrified", "panicked", "fearful"],
        "typical_params": {"scaleY": 1.6, "scaleX": 0.8, "squint": 0.0, "arch": 0.0},
    },
}

TRANSITION_CURVES = {
    "linear": "Transicion lineal uniforme",
    "ease_in": "Comienza lento, acelera al final",
    "ease_out": "Comienza rapido, desacelera al final",
    "ease_in_out": "Suave al inicio y al final",
    "bounce": "Efecto rebote al llegar al destino",
    "elastic": "Efecto elastico con sobrepaso",
    "overshoot": "Sobrepasa ligeramente el destino antes de asentarse",
}

EASING_FUNCTIONS = {
    "linear": lambda t: t,
    "ease_in": lambda t: t * t,
    "ease_out": lambda t: t * (2 - t),
    "ease_in_out": lambda t: t * t * (3 - 2 * t) if t < 0.5 else (t - 1) * (t - 1) * (3 - 2 * (1 - t)) + 1,
}

BLINK_PATTERNS = {
    "normal": {
        "description": "Parpadeo normal y simetrico",
        "duration": 0.12,
        "left_offset": 0.0,
        "right_offset": 0.02,
    },
    "fast": {
        "description": "Parpadeo rapido (susto o sorpresa)",
        "duration": 0.05,
        "left_offset": 0.0,
        "right_offset": 0.0,
    },
    "slow": {
        "description": "Parpadeo lento (cansasio o sueno)",
        "duration": 0.3,
        "left_offset": 0.0,
        "right_offset": 0.05,
    },
    "asymmetric": {
        "description": "Parpadeo asimetrico (un ojo antes que el otro)",
        "duration": 0.15,
        "left_offset": 0.05,
        "right_offset": 0.0,
    },
    "wink_left": {
        "description": "Guino del ojo izquierdo",
        "duration": 0.2,
        "left_offset": 0.0,
        "right_offset": 999.0,
    },
    "wink_right": {
        "description": "Guino del ojo derecho",
        "duration": 0.2,
        "left_offset": 999.0,
        "right_offset": 0.0,
    },
    "double": {
        "description": "Doble parpadeo rapido",
        "duration": 0.06,
        "left_offset": 0.0,
        "right_offset": 0.01,
    },
}

LOOK_PATTERNS = {
    "idle_roam": {
        "description": "Mirada vaga aleatoria cuando esta inactivo",
        "speed": 2.0,
        "range_x": 0.3,
        "range_y": 0.2,
        "interval": 1.0,
    },
    "follow_cursor": {
        "description": "Sigue el cursor del mouse",
        "speed": 4.0,
        "range_x": 1.0,
        "range_y": 1.0,
    },
    "face_tracking": {
        "description": "Sigue una cara detectada",
        "speed": 3.0,
        "range_x": 0.8,
        "range_y": 0.6,
    },
    "scan": {
        "description": "Escanea el entorno de izquierda a derecha",
        "speed": 1.5,
        "range_x": 0.8,
        "range_y": 0.2,
        "interval": 2.0,
    },
    "suspicious": {
        "description": "Mirada sospechosa de lado a lado",
        "speed": 0.5,
        "range_x": 0.7,
        "range_y": 0.1,
        "interval": 3.0,
    },
}

ANIMATION_BLUEPRINTS = {
    "blink": {
        "description": "Parpadeo simple (cerrar y abrir ojos)",
        "phases": [
            {"from": "open", "to": "closed", "duration": 0.04, "easing": "ease_in"},
            {"from": "closed", "to": "open", "duration": 0.08, "easing": "ease_out"},
        ],
    },
    "surprise": {
        "description": "Reaccion de sorpresa (ojos se abren y luego se recuperan)",
        "phases": [
            {"from": "idle", "to": "wide", "duration": 0.1, "easing": "ease_out"},
            {"hold": True, "duration": 0.3},
            {"from": "wide", "to": "idle", "duration": 0.3, "easing": "ease_in_out"},
        ],
    },
    "happy_bounce": {
        "description": "Ojos felices con efecto rebote",
        "phases": [
            {"from": "idle", "to": "happy", "duration": 0.15, "easing": "ease_out"},
            {"hold": True, "duration": 0.4},
            {"from": "happy", "to": "happy_narrow", "duration": 0.1},
            {"from": "happy_narrow", "to": "happy", "duration": 0.1},
            {"from": "happy", "to": "idle", "duration": 0.2, "easing": "ease_in"},
        ],
    },
    "sad_cry": {
        "description": "Ojos tristes con lagrimas simuladas",
        "phases": [
            {"from": "idle", "to": "sad", "duration": 0.3, "easing": "ease_in"},
            {"hold": True, "duration": 0.5},
            {"from": "sad", "to": "sad_droop", "duration": 0.2},
            {"from": "sad_droop", "to": "sad", "duration": 0.2},
            {"from": "sad", "to": "idle", "duration": 0.4, "easing": "ease_out"},
        ],
    },
    "angry_flare": {
        "description": "Enojo con cambio de color de ojos",
        "phases": [
            {"from": "idle", "to": "angry_stare", "duration": 0.2, "easing": "ease_in"},
            {"color_change": [255, 40, 0], "duration": 0.1},
            {"hold": True, "duration": 0.4},
            {"color_change": [70, 130, 220], "duration": 0.2},
            {"from": "angry_stare", "to": "idle", "duration": 0.3, "easing": "ease_out"},
        ],
    },
    "wake_up": {
        "description": "Secuencia completa de despertar",
        "phases": [
            {"hold": True, "duration": 0.2},
            {"from": "closed", "to": "half_mast", "duration": 0.3, "easing": "ease_out"},
            {"from": "half_mast", "to": "searching", "duration": 0.2},
            {"from": "searching", "to": "idle", "duration": 0.2, "easing": "ease_in_out"},
        ],
    },
    "sleep_off": {
        "description": "Secuencia completa de dormirse",
        "phases": [
            {"from": "idle", "to": "sleepy", "duration": 0.5, "easing": "ease_in"},
            {"from": "sleepy", "to": "half_mast", "duration": 0.3},
            {"hold": True, "duration": 0.2},
            {"from": "half_mast", "to": "closed", "duration": 0.3, "easing": "ease_in"},
        ],
    },
    "confusion_cycle": {
        "description": "Ciclo de confusion (mirar de un lado a otro)",
        "phases": [
            {"look_to": [-0.5, 0.0], "duration": 0.4, "easing": "ease_in_out"},
            {"look_to": [0.5, 0.0], "duration": 0.4, "easing": "ease_in_out"},
            {"look_to": [-0.3, -0.2], "duration": 0.4, "easing": "ease_in_out"},
            {"look_to": [0.0, 0.0], "duration": 0.3, "easing": "ease_in_out"},
        ],
    },
}

EXPRESSION_SPEED_PRESETS = {
    "slow": {"factor": 0.5, "description": "Movimientos lentos y suaves"},
    "normal": {"factor": 1.0, "description": "Velocidad normal"},
    "fast": {"factor": 2.0, "description": "Movimientos rapidos"},
    "instant": {"factor": 10.0, "description": "Cambio instantaneo"},
}

BLINK_STATISTICS = {
    "average_interval": 4.0,
    "min_interval": 1.5,
    "max_interval": 8.0,
    "average_duration": 0.12,
    "blinks_per_minute": 15,
    "asymmetric_probability": 0.3,
}
