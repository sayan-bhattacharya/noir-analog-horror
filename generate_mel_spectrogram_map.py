"""Generate an aesthetic Mel Spectrogram with a laser-pointer visual journey map for N Oir."""
import os
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter


AUDIO_PATH = r"e:\betweenthenotes\noir_film_project\Noir.wav"
OUT_PATH = r"e:\betweenthenotes\noir_film_project\assets\noir_mel_spectrogram_journey_map.png"


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    # Load mono at 22050 Hz for fast, crisp mel-spectrogram computation across the full track
    y, sr = librosa.load(AUDIO_PATH, sr=22050, mono=True)
    duration = len(y) / sr
    print(f"Loaded Noir.wav: duration={duration:.2f}s, sr={sr}")

    # Compute Mel Spectrogram (hop_length=2048 -> ~10.7 fps across 30 min, very clean)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=4096, hop_length=2048, n_mels=128, fmax=8000)
    S_db = librosa.power_to_db(S, ref=np.max)

    # Print RMS energy profile in 6 equal segments to ground the narrative map
    seg_len = len(y) // 6
    for i in range(6):
        seg = y[i * seg_len : (i + 1) * seg_len]
        rms = float(np.sqrt(np.mean(seg ** 2)))
        t0 = i * duration / 6.0
        t1 = (i + 1) * duration / 6.0
        print(f"Segment {i+1} ({t0/60:.1f}m - {t1/60:.1f}m): RMS={rms:.4f}")

    # Custom N Oir aesthetic colormap: pitch black -> bruised violet -> crimson -> warm amber
    cmap = LinearSegmentedColormap.from_list(
        "noir_mel",
        [
            (0.00, "#050508"),
            (0.25, "#150B24"),
            (0.50, "#4B1238"),
            (0.72, "#A81C2E"),
            (0.88, "#E3682C"),
            (1.00, "#FFE0A3"),
        ],
    )

    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="#060609")
    ax = fig.add_axes([0.055, 0.16, 0.90, 0.68], facecolor="#060609")

    times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=2048)
    freqs = librosa.mel_frequencies(n_mels=128, fmin=0, fmax=8000)

    ax.pcolormesh(times / 60.0, freqs, S_db, shading="auto", cmap=cmap, vmin=-72, vmax=0)
    ax.set_yscale("symlog", linthresh=120)
    ax.set_ylim(20, 8000)
    ax.set_xlim(0, duration / 60.0)

    # Subtle grid & axis styling
    ax.tick_params(colors="#9A8F85", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#2A2226")
    ax.set_ylabel("FREQUENCY (Hz)", color="#C8B8A6", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_xlabel("N OIR TIMELINE (MINUTES)", color="#C8B8A6", fontsize=11, fontweight="bold", labelpad=10)

    # Title & subtitle
    fig.text(
        0.055, 0.915,
        "N O I R  —  MEL SPECTROGRAM & LASER POINTER VISUAL JOURNEY MAP",
        color="#F2D7A5", fontsize=21, fontweight="bold", family="sans-serif"
    )
    fig.text(
        0.055, 0.878,
        "FROM SUKUMAR RAY COSMIC FOLK-DREAD & THE BLACK-LIQUID ABYSS  ->  TO THE LIMINAL EXIT 8 CORRIDOR",
        color="#A68C7C", fontsize=12, family="sans-serif"
    )

    # Define the 6 narrative stages mapped across the timeline
    total_min = duration / 60.0
    stages = [
        (0.00 * total_min, 0.08 * total_min, "0. SILENT OMEN", "CRT hairline drop &\neye-aperture cue"),
        (0.08 * total_min, 0.26 * total_min, "I. NISHIDAK", "Homestead dread &\nbamboo-grove call"),
        (0.26 * total_min, 0.44 * total_min, "II. BLACK CONDUIT", "Tubewell pumps black\nliquid -> black hole"),
        (0.44 * total_min, 0.62 * total_min, "III. HYPER-OBJECT", "Elongated-neck cat &\nTrinetra 3rd Eye"),
        (0.62 * total_min, 0.76 * total_min, "IV. ABYSS FALL", "Twilight Zone descent\ninto the unknown"),
        (0.76 * total_min, 1.00 * total_min, "V. EXIT 8 SHIFT", "Fluorescent corridor &\nthe staring man"),
    ]

    for idx, (m0, m1, title, desc) in enumerate(stages):
        if idx > 0:
            ax.axvline(m0, color="#6B4C44", linestyle="--", linewidth=1.0, alpha=0.65)
        mid = 0.5 * (m0 + m1)
        ax.text(
            mid, 6300, title,
            color="#F7DFB4", fontsize=10.5, fontweight="bold",
            ha="center", va="top",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#120C10", edgecolor="#75333A", alpha=0.88)
        )
        ax.text(
            mid, 42, desc,
            color="#D2C2B4", fontsize=8.5, ha="center", va="bottom",
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#0A080C", edgecolor="#3A282D", alpha=0.80)
        )

    # Laser pointer motif: active playhead at the Abyss Fall -> Exit 8 Vibe Shift hinge
    laser_min = 0.68 * total_min
    laser_freq = 420.0
    for lw, al in [(14, 0.10), (7, 0.22), (2.5, 0.65), (1.0, 0.98)]:
        ax.axvline(laser_min, color="#FF2442", linewidth=lw, alpha=al, zorder=9)
    ax.scatter([laser_min], [laser_freq], s=420, color="#FF2442", alpha=0.22, zorder=10)
    ax.scatter([laser_min], [laser_freq], s=140, color="#FF4D6A", alpha=0.65, zorder=11)
    ax.scatter([laser_min], [laser_freq], s=36, color="#FFFFFF", alpha=1.0, zorder=12)

    ax.annotate(
        "LASER PLAYHEAD: DESCENT -> VIBE SHIFT",
        xy=(laser_min, laser_freq),
        xytext=(laser_min - 0.14 * total_min, 1450),
        color="#FF8C9A",
        fontsize=10,
        fontweight="bold",
        ha="center",
        arrowprops=dict(arrowstyle="->", color="#FF2442", lw=1.8),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#1A080D", edgecolor="#FF2442", alpha=0.92),
        zorder=13,
    )

    fig.savefig(OUT_PATH, dpi=100, facecolor="#060609")
    plt.close(fig)
    print(f"Saved Mel Spectrogram map to {OUT_PATH}")


if __name__ == "__main__":
    main()
