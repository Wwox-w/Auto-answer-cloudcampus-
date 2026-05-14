"""简单的日志工具"""

import time


def log(msg: str, level: str = "INFO"):
    t = time.strftime("%H:%M:%S")
    print(f"[{t}] [{level}] {msg}")


def info(msg: str):
    log(msg, "INFO")


def warn(msg: str):
    log(msg, "WARN")


def error(msg: str):
    log(msg, "ERROR")
