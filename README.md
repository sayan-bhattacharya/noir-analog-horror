# PROJECT NOIR / NISHIDAK VISUAL ENGINE
## নিশিডাক — THE NISHIDAK BROADCAST

A minimal, highly controllable, modular Python visual engine for the current 5:52 NOIR compositor workprint:
**“নিশিডাক — THE NISHIDAK BROADCAST”**.

Simulates a corrupted 1994 Doordarshan Kendra Calcutta (DD-1 Bangla) emergency transmission interrupted by cosmic, folk-horror signals from rural Bengal (Nistobdhopur).

The separate master screenplay and `Noir.wav` score run 30:22; the current compositor timeline ends at 05:52. The Colab notebook renders the implemented workprint only and requires the original `Noir.wav` file (it never substitutes podcast audio).

---

## 1. Quickstart & Installation

```bash
# Clone the repository
git clone https://github.com/sayan-bhattacharya/noir-analog-horror.git
cd noir-analog-horror

# Install lightweight dependencies
pip install -r requirements.txt
```

---

## 2. Rendering CLI Commands

### ⚡ Fast Low-Resolution Preview (All Scenes)
```bash
python -m noir_film.render_noir --preview
```

### 🎬 Render Full 180-Second Master
```bash
python -m noir_film.render_noir --full
```

### 🔍 Render Individual Scene Only
```bash
# Scene 1: Doordarshan Signal Interrupt (00:00 - 00:15)
python -m noir_film.render_noir --scene 1

# Scene 2: Nistobdhopur Solitary Homestead (00:15 - 00:35)
python -m noir_film.render_noir --scene 2

# Scene 3: The Mosquito Net Metamorphosis (00:35 - 01:05)
python -m noir_film.render_noir --scene 3

# Scene 4: The Fall & The Repeating Alarm (01:05 - 01:35)
python -m noir_film.render_noir --scene 4

# Scene 5: The Uncanny Feline (01:35 - 02:05)
python -m noir_film.render_noir --scene 5

# Scene 6: Tantric Cosmic Dread: The Celestial Eye (02:05 - 02:45)
python -m noir_film.render_noir --scene 6

# Scene 7: Terminal Carrier & Phosphor Decay (02:45 - 03:00)
python -m noir_film.render_noir --scene 7
```

### ⚙️ Render from Custom Scene Config
```bash
python -m noir_film.render_noir --config config/scene_06_trinetra_cosmic.yaml
```

### 🔇 Silent Render (No Audio Sync)
```bash
python -m noir_film.render_noir --full --no-audio
```

### 💎 Final High-Resolution Export
```bash
python -m noir_film.render_noir --full --quality final
```

---

## 3. Directory Structure

```text
noir_film/
├── config/
│   ├── global.yaml
│   ├── scene_01_signal_interrupt.yaml
│   ├── scene_02_homestead_banana.yaml
│   ├── scene_03_kafka_bedroom.yaml
│   ├── scene_04_abyss_alarm.yaml
│   ├── scene_05_hulo_cat.yaml
│   ├── scene_06_trinetra_cosmic.yaml
│   └── scene_07_cathode_collapse.yaml
├── noir_film/
│   ├── __init__.py
│   ├── render_noir.py
│   ├── timeline.py
│   ├── audio_map.py
│   ├── palette.py
│   ├── crt.py
│   ├── vhs.py
│   ├── noise.py
│   ├── distortion.py
│   ├── cosmic.py
│   ├── text_overlay.py
│   ├── actors/
│   │   ├── doordarshan_alert.py
│   │   ├── banana_trees.py
│   │   ├── bimal_metamorphosis.py
│   │   ├── hulo_cat.py
│   │   └── trinetra_eye.py
│   └── utils/
│       ├── easing.py
│       ├── rng.py
│       ├── video_io.py
│       └── config_loader.py
├── plates/
│   ├── bengal_courage_homestead.jpg
│   ├── moshari_bedroom_realistic.jpg
│   └── bengal_cosmic_eye.jpg
├── audio/
│   └── Noir.wav
├── output/
├── requirements.txt
├── README.md
└── pyproject.toml
```

---

## 4. Hyperparameter Controls

All visual and audio-reactive parameters are exposed in `config/global.yaml` and scene-specific YAML files:
* **Broadcast Decay**: `barrel_distortion`, `scanline_strength`, `vignette_strength`, `chromatic_aberration_px`, `head_switching_band_px`
* **Audio Reactivity**: `bass_to_zoom`, `bass_to_shake`, `bass_to_pupil_dilation`, `chime_to_flash`, `rms_to_grain`
* **Atmosphere**: `wind_strength`, `banana_leaf_sway_amplitude`, `handpump_motion_amplitude`, `drip_interval_seconds`
* **Body Horror Restraint**: `metamorphosis_progress`, `limb_count`, `limb_jitter_hz`, `cataract_glow_intensity`
* **Cosmic Scaling**: `eye_scale`, `pupil_dilation_max`, `capillary_branch_density`
