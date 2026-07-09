#!/usr/bin/env python3
"""
Analysera en instrumental och känneteckna ljudet.

Användning:
    python analyze_instrumental.py min_låt.mp3
    python analyze_instrumental.py min_låt.wav --json rapport.json --bild analys.png

Stöder wav, mp3, flac, ogg, m4a m.fl.
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from audio_analysis import AudioAnalyzer


def print_report(result) -> None:
    line = "=" * 60
    print(line)
    print(f"  ANALYS AV: {Path(result.fil).name}")
    print(line)

    minutes, seconds = divmod(int(result.längd_sekunder), 60)
    print(f"\nLängd: {minutes}:{seconds:02d}  |  Samplingsfrekvens: {result.samplingsfrekvens} Hz")

    print("\n--- SAMMANFATTNING " + "-" * 41)
    for row in result.beskrivning:
        print(f"  • {row}")

    print("\n--- TEMPO & RYTM " + "-" * 43)
    print(f"  BPM: {result.tempo['bpm']}   Pulsjämnhet: {result.tempo['puls_jämnhet']}")
    print(
        f"  Anslag/sekund: {result.rytm['anslag_per_sekund']}   "
        f"Harmoniskt: {int(result.rytm['harmonisk_andel'] * 100)} %   "
        f"Perkussivt: {int(result.rytm['perkussiv_andel'] * 100)} %"
    )

    print("\n--- TONART " + "-" * 49)
    print(
        f"  {result.tonart['tonart']}   "
        f"Mest framträdande toner: {', '.join(result.tonart['mest_framträdande_toner'])}"
    )

    print("\n--- KLANGFÄRG " + "-" * 46)
    k = result.klangfärg
    print(f"  Spektral tyngdpunkt: {k['spektral_centroid_hz']} Hz")
    print(f"  Bandbredd: {k['spektral_bandbredd_hz']} Hz   Rolloff (85 %): {k['rolloff_85_hz']} Hz")
    print(f"  Platthet (brusighet): {k['spektral_platthet']}")

    print("\n--- FREKVENSBALANS (andel av energin) " + "-" * 22)
    for band, share in result.frekvensbalans.items():
        bar = "█" * int(share / 2)
        print(f"  {band.replace('_', ' '):38s} {share:5.1f} %  {bar}")

    print("\n--- DYNAMIK " + "-" * 48)
    d = result.dynamik
    print(
        f"  RMS-medel: {d['rms_medel_db']} dB   Omfång: {d['dynamiskt_omfång_db']} dB   "
        f"Crest: {d['crest_faktor']}   Tystnad: {d['andel_tystnad'] * 100:.0f} %"
    )

    if result.struktur:
        print("\n--- STRUKTUR " + "-" * 47)
        for s in result.struktur:
            start_m, start_s = divmod(int(s["start"]), 60)
            end_m, end_s = divmod(int(s["slut"]), 60)
            print(
                f"  Sektion {s['sektion']}: {start_m}:{start_s:02d} - {end_m}:{end_s:02d}  "
                f"({s['karaktär']})"
            )
    print("\n" + line)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analysera en instrumental: tempo, tonart, klangfärg, dynamik m.m."
    )
    parser.add_argument("fil", help="Sökväg till ljudfilen (wav, mp3, flac, ogg ...)")
    parser.add_argument("--json", metavar="FIL", help="Spara hela analysen som JSON")
    parser.add_argument("--bild", metavar="FIL", help="Spara visualisering (PNG) med vågform, spektrogram och kromagram")
    parser.add_argument("-v", "--verbose", action="store_true", help="Visa detaljerad logg")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    analyzer = AudioAnalyzer()
    try:
        print(f"Analyserar {args.fil} ... (kan ta en stund för långa filer)")
        result = analyzer.analyze(args.fil)
    except FileNotFoundError as exc:
        print(f"Fel: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Kunde inte analysera filen: {exc}", file=sys.stderr)
        return 1

    print_report(result)

    if args.json:
        Path(args.json).write_text(result.to_json(), encoding="utf-8")
        print(f"JSON-rapport sparad: {args.json}")

    if args.bild:
        analyzer.visualize(args.fil, args.bild)
        print(f"Visualisering sparad: {args.bild}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
