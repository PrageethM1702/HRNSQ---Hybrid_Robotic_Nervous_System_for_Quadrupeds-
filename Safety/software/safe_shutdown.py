def build_shutdown_command(reason):
    return {
        "mode": "shutdown",
        "reason": reason,
        "motor_enable": False,
        "cpg_enable": False,
        "reflex_gain": 0.0,
        "pwm": 0.0,
    }
