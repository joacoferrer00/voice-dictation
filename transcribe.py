"""
Transcribe audios (WhatsApp .opus/.ogg, .mp3, .m4a, .wav...) a texto via Groq Whisper.

Uso:
    python transcribe.py <carpeta_o_archivos...> [--out salida.md] [--lang es]

Ejemplos:
    # toda una carpeta, ordenada por nombre, a un .md al lado de la carpeta
    python transcribe.py "../chamba/bici-mania/audios"

    # archivos sueltos a un destino explicito
    python transcribe.py a.opus b.opus --out transcripcion.md

Reusa la API key de Groq y el venv de whisper-writer. No instala nada nuevo.
"""
import argparse
import os
import sys
from pathlib import Path

from openai import OpenAI

AUDIO_EXTS = {".opus", ".ogg", ".oga", ".mp3", ".m4a", ".wav", ".webm", ".flac", ".mp4", ".mpeg", ".mpga"}
HERE = Path(__file__).resolve().parent
ENV_FILE = HERE / "whisper-writer" / ".env"


def load_key():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip().strip("'\"")
    return os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")


def collect_files(inputs):
    files = []
    for raw in inputs:
        p = Path(raw)
        if p.is_dir():
            files += [f for f in p.iterdir() if f.suffix.lower() in AUDIO_EXTS]
        elif p.is_file():
            files.append(p)
        else:
            print(f"  ! no existe: {raw}", file=sys.stderr)
    # orden natural por nombre (WhatsApp suele numerarlos / timestamp)
    return sorted(files, key=lambda f: f.name.lower())


def main():
    ap = argparse.ArgumentParser(description="Transcribe audios a texto via Groq Whisper.")
    ap.add_argument("inputs", nargs="+", help="carpeta(s) y/o archivo(s) de audio")
    ap.add_argument("--out", help="archivo .md de salida (default: transcripcion.md junto al primer input)")
    ap.add_argument("--lang", default="es", help="idioma (default: es)")
    ap.add_argument("--model", default="whisper-large-v3-turbo", help="modelo Groq")
    args = ap.parse_args()

    key = load_key()
    if not key:
        sys.exit("No encontre API key (whisper-writer/.env o GROQ_API_KEY).")

    files = collect_files(args.inputs)
    if not files:
        sys.exit("No hay audios para transcribir.")

    if args.out:
        out = Path(args.out)
    else:
        first = Path(args.inputs[0])
        base = first if first.is_dir() else first.parent
        out = base.parent / "transcripcion.md" if first.is_dir() else base / "transcripcion.md"

    client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

    print(f"Transcribiendo {len(files)} audio(s) con {args.model}...\n")
    blocks = [f"# Transcripcion\n\n_{len(files)} audio(s), via Groq {args.model}_\n"]
    for i, f in enumerate(files, 1):
        print(f"  [{i}/{len(files)}] {f.name} ...", end=" ", flush=True)
        with open(f, "rb") as fh:
            r = client.audio.transcriptions.create(
                model=args.model, file=fh, language=args.lang, temperature=0.0
            )
        text = r.text.strip()
        print("ok")
        blocks.append(f"## {i}. {f.name}\n\n{text}\n")

    out.write_text("\n".join(blocks), encoding="utf-8")
    print(f"\nListo -> {out}")


if __name__ == "__main__":
    main()
