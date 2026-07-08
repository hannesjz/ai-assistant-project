# Audioanalys av instrumentaler

Analyserar en ljudfil och kännetecknar ljudet: tempo, tonart, klangfärg,
frekvensbalans, dynamik, rytmisk aktivitet och låtstruktur. Rapporten skrivs
ut på svenska direkt i terminalen och kan även sparas som JSON och bild.

## Installation

```bash
pip install librosa soundfile matplotlib
```

För mp3/m4a behövs `ffmpeg` på systemet (`brew install ffmpeg` på macOS,
`apt install ffmpeg` på Linux).

## Användning

```bash
# Grundläggande analys
python analyze_instrumental.py min_instrumental.mp3

# Spara även JSON-rapport och visualisering (vågform, spektrogram, kromagram)
python analyze_instrumental.py min_instrumental.wav --json rapport.json --bild analys.png
```

Stöder wav, mp3, flac, ogg, m4a m.fl.

## Vad analyseras?

| Del | Beskrivning |
|---|---|
| **Tempo & rytm** | BPM, pulsens jämnhet, anslag per sekund, balans mellan harmoniskt och perkussivt innehåll |
| **Tonart** | Uppskattad tonart (dur/moll) via Krumhansl-Schmuckler-profiler, mest framträdande toner |
| **Klangfärg** | Spektral tyngdpunkt (ljus/mörk klang), bandbredd, rolloff, brusighet, MFCC-profil |
| **Frekvensbalans** | Energifördelning över sju band från sub-bas till briljans |
| **Dynamik** | RMS-nivå, dynamiskt omfång, crest-faktor, andel tystnad |
| **Struktur** | Automatisk uppdelning i sektioner med energi-karaktär (lugn/medel/energisk) |

Analysen sammanfattas dessutom i läsbara meningar, t.ex.
*"Tempot är medeltempo (117.5 BPM)"* och *"Klangen är varm och balanserad"*.

## Använda i egen kod

```python
from src.audio_analysis import AudioAnalyzer

analyzer = AudioAnalyzer()
result = analyzer.analyze("min_instrumental.wav")

print(result.tempo["bpm"])
print(result.tonart["tonart"])
print(result.to_json())          # hela analysen som JSON
analyzer.visualize("min_instrumental.wav", "analys.png")
```

## Bra att veta

- Tonartsanalysen kan förväxla parallelltonarter (t.ex. C-dur och A-moll) —
  de innehåller samma toner. Fältet `mest_framträdande_toner` hjälper dig avgöra.
- BPM kan ibland detekteras som hälften eller dubbla verkliga tempot
  (vanligt för alla beat-trackers). Fältet `puls_jämnhet` visar hur stabil pulsen är.
- Långa filer tar längre tid; analysen körs i mono vid 22 050 Hz vilket räcker
  gott för de här måtten.
