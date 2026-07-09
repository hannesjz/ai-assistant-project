"""
Audioanalys för instrumentaler.

Analyserar en ljudfil (wav, mp3, flac, ogg, m4a m.fl.) och kännetecknar
ljudet: tempo, tonart, klangfärg, frekvensbalans, dynamik, rytmisk
aktivitet och låtstruktur. Resultatet kan skrivas ut som en läsbar
rapport på svenska eller exporteras som JSON.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import librosa

logger = logging.getLogger(__name__)

# Krumhansl-Schmuckler tonartsprofiler (dur och moll)
_MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
_MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Frekvensband (Hz) för energifördelningen
_FREQUENCY_BANDS = {
    "sub_bas (20-60 Hz)": (20, 60),
    "bas (60-250 Hz)": (60, 250),
    "lägre_mellanregister (250-500 Hz)": (250, 500),
    "mellanregister (500-2000 Hz)": (500, 2000),
    "övre_mellanregister (2-4 kHz)": (2000, 4000),
    "presens (4-6 kHz)": (4000, 6000),
    "briljans (6-20 kHz)": (6000, 20000),
}


@dataclass
class AnalysisResult:
    """Samlat resultat från en analys av en ljudfil."""

    fil: str = ""
    längd_sekunder: float = 0.0
    samplingsfrekvens: int = 0
    tempo: dict = field(default_factory=dict)
    tonart: dict = field(default_factory=dict)
    klangfärg: dict = field(default_factory=dict)
    frekvensbalans: dict = field(default_factory=dict)
    dynamik: dict = field(default_factory=dict)
    rytm: dict = field(default_factory=dict)
    struktur: list = field(default_factory=list)
    beskrivning: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class AudioAnalyzer:
    """Analyserar instrumentaler och kännetecknar ljudet."""

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def analyze(self, file_path: str) -> AnalysisResult:
        """Kör hela analysen på en ljudfil och returnerar resultatet."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Hittar inte filen: {file_path}")

        logger.info("Läser in %s ...", path.name)
        y, sr = librosa.load(str(path), sr=self.sample_rate, mono=True)
        if y.size == 0:
            raise ValueError(f"Filen innehåller inget ljud: {file_path}")

        result = AnalysisResult(
            fil=str(path),
            längd_sekunder=round(float(len(y) / sr), 2),
            samplingsfrekvens=sr,
        )

        # Harmonisk/perkussiv separation återanvänds av flera delanalyser
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        result.tempo = self._analyze_tempo(y, sr)
        result.tonart = self._analyze_key(y_harmonic, sr)
        result.klangfärg = self._analyze_timbre(y, sr)
        result.frekvensbalans = self._analyze_frequency_balance(y, sr)
        result.dynamik = self._analyze_dynamics(y, sr)
        result.rytm = self._analyze_rhythm(y, y_harmonic, y_percussive, sr)
        result.struktur = self._analyze_structure(y, sr)
        result.beskrivning = self._describe(result)
        return result

    # ------------------------------------------------------------------
    # Delanalyser
    # ------------------------------------------------------------------

    def _analyze_tempo(self, y: np.ndarray, sr: int) -> dict:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        tempo = float(np.atleast_1d(tempo)[0])
        beat_times = librosa.frames_to_time(beats, sr=sr)

        # Jämnhet i pulsen: variation i avstånd mellan taktslag
        if len(beat_times) > 2:
            intervals = np.diff(beat_times)
            regularity = float(1.0 - np.clip(np.std(intervals) / (np.mean(intervals) + 1e-9), 0, 1))
        else:
            regularity = 0.0

        return {
            "bpm": round(tempo, 1),
            "antal_taktslag": int(len(beats)),
            "puls_jämnhet": round(regularity, 2),  # 1.0 = helt jämn puls
        }

    def _analyze_key(self, y_harmonic: np.ndarray, sr: int) -> dict:
        chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
        chroma_mean = chroma.mean(axis=1)

        best = {"korrelation": -2.0}
        for shift in range(12):
            rotated = np.roll(chroma_mean, -shift)
            for mode_name, profile in (("dur", _MAJOR_PROFILE), ("moll", _MINOR_PROFILE)):
                corr = float(np.corrcoef(rotated, profile)[0, 1])
                if corr > best["korrelation"]:
                    best = {
                        "grundton": _NOTE_NAMES[shift],
                        "skala": mode_name,
                        "korrelation": round(corr, 3),
                    }

        best["tonart"] = f"{best['grundton']}-{best['skala']}"
        # Mest framträdande toner i fallande ordning
        order = np.argsort(chroma_mean)[::-1]
        best["mest_framträdande_toner"] = [_NOTE_NAMES[i] for i in order[:4]]
        return best

    def _analyze_timbre(self, y: np.ndarray, sr: int) -> dict:
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        return {
            "spektral_centroid_hz": round(float(centroid.mean()), 1),
            "spektral_bandbredd_hz": round(float(bandwidth.mean()), 1),
            "rolloff_85_hz": round(float(rolloff.mean()), 1),
            "spektral_platthet": round(float(flatness.mean()), 4),  # nära 1 = brusigt
            "nollgenomgångar": round(float(zcr.mean()), 4),
            "mfcc_medel": [round(float(v), 2) for v in mfcc.mean(axis=1)],
        }

    def _analyze_frequency_balance(self, y: np.ndarray, sr: int) -> dict:
        spec = np.abs(librosa.stft(y)) ** 2
        freqs = librosa.fft_frequencies(sr=sr)
        total = float(spec.sum()) + 1e-12

        balance = {}
        for name, (lo, hi) in _FREQUENCY_BANDS.items():
            mask = (freqs >= lo) & (freqs < hi)
            share = float(spec[mask].sum()) / total
            balance[name] = round(share * 100, 1)  # procent av total energi
        return balance

    def _analyze_dynamics(self, y: np.ndarray, sr: int) -> dict:
        rms = librosa.feature.rms(y=y)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        peak = float(np.abs(y).max())
        rms_total = float(np.sqrt(np.mean(y**2)))
        crest = float(peak / (rms_total + 1e-12))

        # Andel nästan tyst tid (under -40 dB relativt max)
        silent_share = float((rms_db < -40).mean())

        return {
            "rms_medel_db": round(float(rms_db.mean()), 1),
            "dynamiskt_omfång_db": round(float(rms_db.max() - rms_db.min()), 1),
            "crest_faktor": round(crest, 2),  # högt = odämpade transienter
            "andel_tystnad": round(silent_share, 3),
        }

    def _analyze_rhythm(
        self, y: np.ndarray, y_harmonic: np.ndarray, y_percussive: np.ndarray, sr: int
    ) -> dict:
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        duration = len(y) / sr
        onset_density = float(len(onsets) / duration) if duration > 0 else 0.0

        harmonic_energy = float(np.sum(y_harmonic**2))
        percussive_energy = float(np.sum(y_percussive**2))
        total = harmonic_energy + percussive_energy + 1e-12

        return {
            "anslag_per_sekund": round(onset_density, 2),
            "antal_anslag": int(len(onsets)),
            "harmonisk_andel": round(harmonic_energy / total, 2),
            "perkussiv_andel": round(percussive_energy / total, 2),
        }

    def _analyze_structure(self, y: np.ndarray, sr: int, n_sections: int = 6) -> list:
        """Delar upp låten i sektioner utifrån förändringar i klangen."""
        duration = len(y) / sr
        n_sections = max(2, min(n_sections, int(duration // 10) + 2))

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        try:
            bounds = librosa.segment.agglomerative(chroma, n_sections)
        except Exception:
            return []
        bound_times = librosa.frames_to_time(bounds, sr=sr)
        bound_times = np.append(bound_times, duration)

        rms = librosa.feature.rms(y=y)[0]
        rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr)

        sections = []
        for i in range(len(bound_times) - 1):
            start, end = float(bound_times[i]), float(bound_times[i + 1])
            mask = (rms_times >= start) & (rms_times < end)
            energy = float(rms[mask].mean()) if mask.any() else 0.0
            sections.append(
                {
                    "sektion": i + 1,
                    "start": round(start, 1),
                    "slut": round(end, 1),
                    "energi": round(energy, 4),
                }
            )

        # Märk sektioner relativt låtens medel-energi
        if sections:
            mean_energy = np.mean([s["energi"] for s in sections]) + 1e-12
            for s in sections:
                ratio = s["energi"] / mean_energy
                if ratio > 1.15:
                    s["karaktär"] = "energisk"
                elif ratio < 0.85:
                    s["karaktär"] = "lugn"
                else:
                    s["karaktär"] = "medel"
        return sections

    # ------------------------------------------------------------------
    # Läsbar beskrivning
    # ------------------------------------------------------------------

    def _describe(self, r: AnalysisResult) -> list:
        desc = []

        bpm = r.tempo.get("bpm", 0)
        if bpm < 70:
            tempo_ord = "långsamt"
        elif bpm < 100:
            tempo_ord = "lugnt"
        elif bpm < 130:
            tempo_ord = "medeltempo"
        elif bpm < 160:
            tempo_ord = "uppdrivet"
        else:
            tempo_ord = "mycket snabbt"
        desc.append(f"Tempot är {tempo_ord} ({bpm} BPM).")

        desc.append(
            f"Tonarten uppskattas till {r.tonart.get('tonart', 'okänd')} "
            f"(säkerhet: {r.tonart.get('korrelation', 0)})."
        )

        centroid = r.klangfärg.get("spektral_centroid_hz", 0)
        if centroid < 1200:
            klang = "mörk och basig"
        elif centroid < 2500:
            klang = "varm och balanserad"
        else:
            klang = "ljus och luftig"
        desc.append(f"Klangen är {klang} (spektral tyngdpunkt kring {int(centroid)} Hz).")

        flatness = r.klangfärg.get("spektral_platthet", 0)
        if flatness > 0.1:
            desc.append("Ljudbilden innehåller mycket brus/atmosfär.")
        else:
            desc.append("Ljudbilden är tonal med tydliga toner.")

        bands = r.frekvensbalans
        if bands:
            dominant = max(bands, key=bands.get)
            desc.append(
                f"Mest energi ligger i {dominant.replace('_', ' ')} "
                f"({bands[dominant]} % av totalen)."
            )

        perc = r.rytm.get("perkussiv_andel", 0)
        if perc > 0.5:
            desc.append("Låten är rytmiskt driven — trummor/perkussion dominerar.")
        elif perc > 0.25:
            desc.append("Bra balans mellan melodiska och rytmiska element.")
        else:
            desc.append("Låten domineras av melodiska/harmoniska element.")

        dyn = r.dynamik.get("dynamiskt_omfång_db", 0)
        if dyn > 40:
            desc.append("Stor dynamik — tydlig skillnad mellan starka och svaga partier.")
        elif dyn > 20:
            desc.append("Måttlig dynamik.")
        else:
            desc.append("Komprimerad ljudbild med jämn styrka rakt igenom.")

        if r.struktur:
            energetic = sum(1 for s in r.struktur if s.get("karaktär") == "energisk")
            desc.append(
                f"Låten delas in i {len(r.struktur)} sektioner, "
                f"varav {energetic} med hög energi."
            )
        return desc

    # ------------------------------------------------------------------
    # Visualisering
    # ------------------------------------------------------------------

    def visualize(self, file_path: str, output_path: str) -> str:
        """Skapar en bild med vågform, spektrogram och kromagram."""
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import librosa.display

        y, sr = librosa.load(str(file_path), sr=self.sample_rate, mono=True)

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        librosa.display.waveshow(y, sr=sr, ax=axes[0])
        axes[0].set_title("Vågform")

        S_db = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        img = librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="log", ax=axes[1])
        axes[1].set_title("Spektrogram (log-frekvens)")
        fig.colorbar(img, ax=axes[1], format="%+2.0f dB")

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        img2 = librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma", ax=axes[2])
        axes[2].set_title("Kromagram (tonernas styrka över tid)")
        fig.colorbar(img2, ax=axes[2])

        fig.suptitle(Path(file_path).name)
        fig.tight_layout()
        fig.savefig(output_path, dpi=120)
        plt.close(fig)
        return output_path
