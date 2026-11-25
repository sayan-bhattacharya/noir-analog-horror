# PROJECT NOIR: TECHNICAL EXECUTION BRIDGE & ENGINE ARCHITECTURE
### Translating the Master Screenplay to Real-Time Procedural Cinema
**Author**: Lead Screenplay & Analog Horror Narrative Architect  
**Target Codebase**: `e:\betweenthenotes\noir_film_project\noir_film`

---

## 1. ARCHITECTURAL OVERVIEW

The Project Noir engine renders high-throughput analog horror cinema at 24/30 FPS in 720p HD / 1080p FHD using pure NumPy, OpenCV, and SciPy/SoundFile. It eliminates heavy external 3D software dependencies, allowing instant execution on standard cloud GPU VMs (Google Colab T4) or local development machines.

```
                      ┌────────────────────────────────────────┐
                      │          MASTER TIMELINE (t)           │
                      └───────────────────┬────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
   [AUDIO DSP ANALYZER]         [SCENE COMPOSITOR]            [PROCEDURAL ACTORS]
   Reads Noir.wav RMS &         Selects background plate      Draws DD logo, banana
   20-80Hz sub-bass energy      Applies affine zoom/pan       trees, Kafka legs, cat
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                             [ANALOG SHADER PIPELINE]
                             1. VHS Tracking & Head-Switch
                             2. Sub-Bass Scanline Jitter
                             3. Chromatic RGB Aberration
                             4. Spherical CRT Curvature
                             5. Green/Cyan Phosphor OSD
                                          │
                                          ▼
                             [FFMPEG STREAMING CONTAINER]
                             Direct libx264 pipe + 100%
                             pure original Noir.wav muxing
```

---

## 2. SCENE-BY-SCENE PROCEDURAL IMPLEMENTATION

### Scene 1: Doordarshan Emergency Interruption (t: 0.0s – 15.0s)
* **Target Function**: `actors.draw_doordarshan_alert(frame, t)`
* **Procedural Mechanics**:
  1. *Raster Canvas*: Indigo/midnight-blue CRT field (`[45, 18, 12]` BGR).
  2. *Swirling Spiral Eye*: Parametric Archimedean spirals evaluated across polar coordinates:
     $$r(\theta) = r_0 + \frac{\theta}{\theta_{\max}} (R - r_0)$$
     Pulsed by low-frequency sine modulation: $\text{pulse} = 1.0 + 0.08 \sin(5t)$.
  3. *Typewriter Typography*: Bengali transliterated glyphs and English emergency warnings rendered at 38 characters per second via dynamic string slicing.
  4. *CRT Breakdown*: At $t > 12.0\text{s}$, `shaders.apply_white_noise(frame, amount=0.55 * fade)` introduces progressive cathode static burst before hard cut.

### Scene 2: Courage in Rural Bengal — The Solitary Homestead (t: 15.0s – 35.0s)
* **Target Plate**: `plates["homestead"]` (`bengal_courage_homestead.jpg`)
* **Target Function**: `actors.draw_bengal_banana_trees(frame, t, cx, cy, scale)`
* **Procedural Mechanics**:
  1. *Optical Push-In*: Affine transformation matrix:
     $$M = \begin{bmatrix} s & 0 & (1-s) c_x \\ 0 & s & (1-s) c_y \end{bmatrix}, \quad s = 1.0 + 0.007(t - 15)$$
  2. *Banana Fronds Sway*: Multi-segmented Bezier-approximated polygons with differential phase offsets:
     $$\Delta \theta = 6.0^\circ \sin(1.5t + \phi_i)$$
  3. *Tubewell Handpump*: Silhouette iron casting with sinusoidal handle sway and stroboscopic phantom water droplets falling into mud.

### Scene 3: Kafka in Bengal — Bimal Babu's Room (t: 35.0s – 65.0s)
* **Target Plate**: `plates["bedroom"]` (`bengal_bedroom.jpg`)
* **Target Function**: `actors.draw_bimal_kafka_bengal(frame, t, cx, cy, stage)`
* **Procedural Mechanics**:
  1. *Mosquito Net Canopy*: Semi-transparent high-frequency lattice with sagging gravitational catenary curves.
  2. *Carapace Swelling*: Horizontal ellipse dilation based on metamorphosis stage ($0.0 \to 1.0$):
     $$w_{\text{torso}} = 24 + 38 \cdot \text{stage}, \quad h_{\text{torso}} = 55 + 24 \cdot \text{stage}$$
  3. *Stop-Motion Beetle Limbs*: Multi-segmented kinematic chains with high-frequency twitch:
     $$\text{twitch} = \sin(22t + 1.8i) \cdot (18.0 \cdot \max(0.3, \text{stage}))$$
  4. *Red-Oxide Floor Reflection*: Subtle inverted duplicate of chitinous limbs with vertical blur and 40% opacity on the polished floor plane.

### Scene 4: The Fall & The Repeating Alarm (t: 65.0s – 95.0s)
* **Acoustic Sync**: Tracks the recurring distillery/alarm bell identified in Atandra's voice notes.
* **Procedural Mechanics**:
  1. *Spatial Dissolution*: Alpha-blend cross-fade between `bedroom` and `cosmic_eye` driven by sub-bass RMS curve.
  2. *Gravitational Desynchronization*: Vertical rolling frame glitch (`np.roll(frame, roll_offset, axis=0)`) mimicking lost VCR vertical hold.
  3. *Alarm Pulse Glow*: Frame luminance flashes by $+15\%$ on each periodic chime peak.

### Scene 5: The Uncanny Black Tomcat (t: 95.0s – 125.0s)
* **Target Plate**: `plates["homestead"]` with night sky grade.
* **Target Function**: `actors.draw_bengal_hulo_cat(frame, t, cx, cy, stretch)`
* **Procedural Mechanics**:
  1. *Bamboo Fence*: Procedural vertical stakes with split-bamboo fibrous texture and horizontal rails.
  2. *Serpentine Tail*: Multi-point cubic spline oscillating with dual-frequency harmonic sines.
  3. *Elastic Neck Extension*: Vertical coordinate displacement:
     $$y_{\text{head}} = y_{\text{body}} - 28 - 360 \cdot \text{stretch}$$
  4. *Toxic Yellow Ocular Scan*: Feline slit pupil with Gaussian glow halo in phosphor amber (`BGR: [45, 235, 245]`).

### Scene 6: Tantric Cosmic Dread — The Trinetra (t: 125.0s – 165.0s)
* **Target Plate**: `plates["cosmic_eye"]` (`bengal_cosmic_eye.jpg`)
* **Procedural Mechanics**:
  1. *Pupil Dilation*: Sub-bass reactive aperture dilation ($R_{\text{pupil}} \propto \text{RMS}_{\text{sub}}$).
  2. *Celestial Static*: Perlin-approximated noise breathing with sine envelope.
  3. *Ground Framing*: Silhouetted banana fronds anchored at bottom corners ($cx_1=0.12W, cx_2=0.92W$) grounding cosmic scale against rural earth.

### Scene 7: Terminal Carrier Collapse (t: 165.0s – 180.0s)
* **Procedural Mechanics**:
  1. Horizontal collapsing line transform ($H \to 2\text{px}$).
  2. Inward pinch to single phosphor white dot $(W/2, H/2)$ with exponential decay.

---

## 3. REAL-TIME SHADER PIPELINE SPECIFICATION

All shaders run per frame in `shaders.py` with zero memory allocation inside the inner loop:

```python
# 1. Sub-bass reactive chromatic aberration
shift = int(2 + 4 * sub_bass)
out[:, :, 0] = np.roll(out[:, :, 0], -shift, axis=1)  # Red left
out[:, :, 2] = np.roll(out[:, :, 2], shift, axis=1)   # Blue right

# 2. VCR Head-switching noise (bottom 24 pixels)
glitch_h = int(20 + 12 * math.sin(t * 3.7))
y_start = max(0, h - glitch_h)
band = out[y_start:h, :]
shift_px = int(math.sin(t * 18.0) * 16.0 + np.random.uniform(-8, 8))
out[y_start:h, :] = np.roll(band, shift_px, axis=1)

# 3. Curved Glass CRT Distortion (Non-linear barrel)
distort = 1.0 + curvature * r2
curved = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# 4. Phosphor Scanline Attenuation (Alternating cathode beam decay)
curved *= scanlines  # Precomputed scanlines[::2] *= (1.0 - scanline_intensity)
```

---

## 4. BENGALI TYPOGRAPHY ENHANCEMENT VIA PILLOW

To render authentic Eastern Indic Bengali script (বাংলা লিপি) without OpenCV `putText` font limitations, the engine includes a lightweight PIL fallback module:

```python
from PIL import Image, ImageDraw, ImageFont

def draw_bengali_osd_text(frame, text, x, y, font_size=28, color=(245, 245, 245)):
    """Renders authentic Bengali Unicode typography onto OpenCV float32 frame."""
    img_pil = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(img_pil)
    # Uses standard Bengali system font (e.g. Nirmala UI / Vrinda / Lohit Bengali)
    try:
        font = ImageFont.truetype("Nirmala.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    draw.text((x, y), text, font=font, fill=color)
    frame[:] = np.array(img_pil).astype(np.float32)
```

---

## 5. REPRODUCIBLE RENDER INVOCATION

To execute the full 180-second Master Screenplay with 100% pure *"Noir"* soundtrack:

```bash
cd e:\betweenthenotes\noir_film_project
python -m noir_film.render_noir 180 0
```

The resulting `noir_720p_story_preview.mp4` contains zero external sound effects, adhering strictly to the pure audio doctrine established with Atandra.
