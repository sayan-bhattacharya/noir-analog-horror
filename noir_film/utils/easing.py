"""
Deterministic easing functions for analog horror animations.
All functions take a normalized progress t in [0.0, 1.0].
"""
import math


def linear(t: float) -> float:
    return max(0.0, min(1.0, t))


def ease_in_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t


def ease_out_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * (2.0 - t)


def ease_in_out_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t


def ease_in_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * t


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    t -= 1.0
    return t * t * t + 1.0


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - edge0) / max(1e-6, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def pulse(t: float, frequency: float = 1.0, min_val: float = 0.0, max_val: float = 1.0) -> float:
    s = (math.sin(t * frequency * 2.0 * math.pi) + 1.0) * 0.5
    return min_val + s * (max_val - min_val)
