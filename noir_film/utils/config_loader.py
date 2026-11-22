"""
YAML Configuration Loader for Project NOIR.
Loads global and scene-specific hyperparameters with safe defaults.
"""
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT, "config")


def load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_global_config() -> dict:
    global_path = os.path.join(CONFIG_DIR, "global.yaml")
    return load_yaml(global_path)


def load_scene_config(scene_id: int) -> dict:
    mapping = {
        1: "scene_01_signal_interrupt.yaml",
        2: "scene_02_homestead_banana.yaml",
        3: "scene_03_kafka_bedroom.yaml",
        4: "scene_04_abyss_alarm.yaml",
        5: "scene_05_hulo_cat.yaml",
        6: "scene_06_trinetra_cosmic.yaml",
        7: "scene_07_cathode_collapse.yaml",
    }
    fname = mapping.get(scene_id)
    if not fname:
        raise ValueError(f"Unknown scene_id {scene_id}. Must be 1 to 7.")
    path = os.path.join(CONFIG_DIR, fname)
    return load_yaml(path)
