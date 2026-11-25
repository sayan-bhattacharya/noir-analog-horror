"""
Full 30-Minute Librosa Music & Orchestration Transcription for Project NOIR (Noir.wav).
Generates:
1. noir_audio_features_24fps.npy (24fps multi-band matrix matching SHE's analyze_she_audio.py standard)
2. NOIR_30MIN_MUSIC_TRANSCRIPTION.json (complete 15s-window orchestration, chroma/MIDI pitches, onsets)
3. NOIR_30MIN_MUSIC_TRANSCRIPTION.md (human-readable timestamped score & instrumentation breakdown)
"""
import os
import json
import numpy as np
import librosa

ROOT = r"e:\betweenthenotes\noir_film_project"
PATH_AUDIO = os.path.join(ROOT, "Noir.wav")
PATH_NPY = os.path.join(ROOT, "noir_audio_features_24fps.npy")
PATH_JSON = os.path.join(ROOT, "NOIR_30MIN_MUSIC_TRANSCRIPTION.json")
PATH_MD = os.path.join(ROOT, "NOIR_30MIN_MUSIC_TRANSCRIPTION.md")

SR = 22050
FPS = 24
HOP_LENGTH = int(round(SR / FPS))  # ~919 samples per 24fps frame
N_FFT = 2048

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

print(f"Loading {PATH_AUDIO} at sr={SR}...", flush=True)
y, sr = librosa.load(PATH_AUDIO, sr=SR, mono=True)
duration = float(len(y) / sr)
total_frames = int(duration * FPS)
print(f"Loaded {duration:.2f}s ({total_frames} frames @ {FPS}fps).", flush=True)

print("Computing STFT, RMS, Centroid, Flatness, Chroma, and Onset Strength...", flush=True)
D = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)

rms = librosa.feature.rms(S=D, frame_length=N_FFT)[0]
centroid = librosa.feature.spectral_centroid(S=D, sr=sr)[0]
flatness = librosa.feature.spectral_flatness(S=D)[0]
chroma = librosa.feature.chroma_stft(S=D ** 2, sr=sr)
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP_LENGTH)
onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=HOP_LENGTH, backtrack=False)
onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=HOP_LENGTH)

def band_energy(f_low, f_high):
    idx = np.where((freqs >= f_low) & (freqs <= f_high))[0]
    if len(idx) == 0:
        return np.zeros(D.shape[1], dtype=np.float32)
    return np.mean(D[idx, :], axis=0).astype(np.float32)

sub_bass = band_energy(20, 70)
bass = band_energy(70, 250)
low_mid = band_energy(250, 500)
mid = band_energy(500, 2000)
high_mid = band_energy(2000, 4000)
high = band_energy(4000, 8000)
air = band_energy(8000, 11025)

def norm_band(b):
    p99 = np.percentile(b, 99.5)
    return np.clip(b / (p99 if p99 > 1e-6 else 1.0), 0.0, 1.0)

n_sub = norm_band(sub_bass)
n_bass = norm_band(bass)
n_lmid = norm_band(low_mid)
n_mid = norm_band(mid)
n_hmid = norm_band(high_mid)
n_high = norm_band(high)
n_air = norm_band(air)
n_rms = norm_band(rms)

# Save 24fps feature matrix (matching SHE project convention)
n_len = min(total_frames, D.shape[1], len(onset_env))
feat_matrix = np.column_stack([
    n_rms[:n_len], n_sub[:n_len], n_bass[:n_len], n_lmid[:n_len],
    n_mid[:n_len], n_hmid[:n_len], n_high[:n_len], n_air[:n_len],
    np.clip(onset_env[:n_len] / max(1e-6, np.percentile(onset_env, 99.5)), 0.0, 1.0)
]).astype(np.float32)
np.save(PATH_NPY, feat_matrix)
print(f"Saved 24fps matrix: {PATH_NPY} shape={feat_matrix.shape}", flush=True)

def fmt_ts(sec: float) -> str:
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"

def infer_orchestration(sub, b, lm, m, hm, hi, cent, flat, onset_rate, rms_val):
    if rms_val < 0.03:
        return "Near-Silence / Sub-Audible Room Tone"
    layers = []
    if sub > 0.25 or b > 0.28:
        layers.append("Deep Sub-Bass / Bowed Drone")
    if (m > 0.22 or lm > 0.25) and flat < 0.12:
        if onset_rate > 1.2:
            layers.append("Piano / Plucked Mid-Harmony")
        else:
            layers.append("Sustained Pad / Strings / Brass Swell")
    if hm > 0.20 or hi > 0.18:
        if flat > 0.18:
            layers.append("Industrial Static / Analog Noise")
        else:
            layers.append("Metallic Overtones / High Synth Shimmer")
    if onset_rate > 2.2:
        layers.append("Rhythmic Percussive Hits / Pulses")
    if not layers:
        layers.append("Sparse Dark Ambient Texture")
    return " + ".join(layers)

windows = []
win_sec = 15
for s_t in range(0, int(duration), win_sec):
    e_t = min(int(duration), s_t + win_sec)
    f0 = int(s_t * FPS)
    f1 = min(n_len, int(e_t * FPS))
    if f1 <= f0:
        continue

    w_rms = float(np.mean(n_rms[f0:f1]))
    w_sub = float(np.mean(n_sub[f0:f1]))
    w_bass = float(np.mean(n_bass[f0:f1]))
    w_lmid = float(np.mean(n_lmid[f0:f1]))
    w_mid = float(np.mean(n_mid[f0:f1]))
    w_hmid = float(np.mean(n_hmid[f0:f1]))
    w_high = float(np.mean(n_high[f0:f1]))
    w_cent = float(np.mean(centroid[f0:f1]))
    w_flat = float(np.mean(flatness[f0:f1]))

    w_chroma = np.mean(chroma[:, f0:f1], axis=1)
    top3_idx = np.argsort(w_chroma)[::-1][:3]
    pitches = [NOTE_NAMES[i] for i in top3_idx if w_chroma[i] > 0.25]
    if not pitches:
        pitches = [NOTE_NAMES[int(top3_idx[0])]]

    win_onsets = onset_times[(onset_times >= s_t) & (onset_times < e_t)]
    onset_rate = float(len(win_onsets) / max(1, (e_t - s_t)))

    orch = infer_orchestration(w_sub, w_bass, w_lmid, w_mid, w_hmid, w_high, w_cent, w_flat, onset_rate, w_rms)

    windows.append({
        "start_s": s_t,
        "end_s": e_t,
        "window": f"{fmt_ts(s_t)} - {fmt_ts(e_t)}",
        "rms_norm": round(w_rms, 3),
        "sub_bass": round(w_sub, 3),
        "bass": round(w_bass, 3),
        "low_mid": round(w_lmid, 3),
        "mid": round(w_mid, 3),
        "high_mid": round(w_hmid, 3),
        "high": round(w_high, 3),
        "centroid_hz": round(w_cent, 1),
        "flatness": round(w_flat, 4),
        "onset_rate_hz": round(onset_rate, 2),
        "dominant_pitches": pitches,
        "orchestration": orch
    })

# Top 25 sharpest musical onset cues across the 30 minutes
onset_strengths = onset_env[onset_frames[onset_frames < n_len]]
top_cue_idx = np.argsort(onset_strengths)[::-1][:25]
top_cues = []
for idx in sorted(top_cue_idx, key=lambda k: onset_frames[k]):
    fr = int(onset_frames[idx])
    t_sec = float(fr / FPS)
    pitch = NOTE_NAMES[int(np.argmax(chroma[:, fr]))]
    top_cues.append({
        "time_s": round(t_sec, 2),
        "timestamp": fmt_ts(t_sec),
        "strength": round(float(onset_env[fr]), 2),
        "dominant_note": pitch,
        "centroid_hz": round(float(centroid[fr]), 1)
    })

with open(PATH_JSON, "w", encoding="utf-8") as f:
    json.dump({
        "source": PATH_AUDIO,
        "duration_s": round(duration, 2),
        "fps_features": FPS,
        "total_onsets": int(len(onset_times)),
        "top_25_cues": top_cues,
        "windows_15s": windows
    }, f, indent=2)

# Write Markdown Score & Orchestration Breakdown
md = [
    "# NOIR.wav — Complete 30-Minute Librosa Music & Orchestration Transcription",
    "",
    f"**Source:** `{PATH_AUDIO}` | **Duration:** `{fmt_ts(duration)}` (`{duration:.2f}s`) | **24fps Matrix:** `{PATH_NPY}` (`{feat_matrix.shape}`)",
    f"**Total Detected Musical Onsets:** `{len(onset_times)}` | **Temporal Resolution:** 15-second orchestration windows + top 25 transient cues",
    "",
    "---",
    "",
    "## 1. Top 25 Sharpest Musical Onset / Impact Cues (Exact Timing & Pitch)",
    "",
    "| Timestamp | Seconds | Dominant Pitch | Centroid (Hz) | Onset Strength |",
    "|---|---|---|---|---|",
]
for c in top_cues:
    md.append(f"| `{c['timestamp']}` | `{c['time_s']}s` | **{c['dominant_note']}** | `{c['centroid_hz']}` | `{c['strength']}` |")

md.extend([
    "",
    "---",
    "",
    "## 2. Full 30-Minute Orchestration, Pitch & Frequency-Band Score (15s Windows)",
    "",
    "| Window | RMS | Sub | Bass | Mid | High | Centroid | Onsets/s | Active Pitches | Inferred Instrumentation / Texture |",
    "|---|---|---|---|---|---|---|---|---|---|",
])
for w_item in windows:
    p_str = ", ".join(w_item["dominant_pitches"])
    md.append(
        f"| `{w_item['window']}` | `{w_item['rms_norm']:.2f}` | `{w_item['sub_bass']:.2f}` | `{w_item['bass']:.2f}` | "
        f"`{w_item['mid']:.2f}` | `{w_item['high']:.2f}` | `{w_item['centroid_hz']:.0f}Hz` | `{w_item['onset_rate_hz']:.1f}` | "
        f"**{p_str}** | {w_item['orchestration']} |"
    )

with open(PATH_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print(f"Saved {PATH_MD} and {PATH_JSON} ({len(windows)} windows).", flush=True)
