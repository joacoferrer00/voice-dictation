# Voice Dictation

Windows push-to-talk dictation. Press `Ctrl+Shift+Space`, talk (English, Spanish, or mixed), press again.
The transcript types at the cursor AND lands on the clipboard.

Engine: OpenRouter `openai/whisper-large-v3` (working now). Swap to Groq for lower latency (see below).

## Launch

Double-click `start.bat`, or from PowerShell:

```powershell
cd whisper-writer
.\venv\Scripts\activate
python run.py
```

## Configuration

Config lives at `whisper-writer/src/config.yaml`. API key is in `whisper-writer/.env` as `OPENAI_API_KEY`.

### Swap to Groq (recommended when you have the key)

1. Get a free key at `console.groq.com`.
2. In `whisper-writer/.env`, replace the value of `OPENAI_API_KEY` with the Groq key.
3. In `whisper-writer/src/config.yaml`, change:
   - `api.model` to `whisper-large-v3-turbo`
   - `api.base_url` to `https://api.groq.com/openai/v1`

## Clipboard patch

`whisper-writer/src/main.py` has a one-line `pyperclip.copy(result)` added to `on_transcription_complete`,
so the transcript is always on the clipboard even when no text field is focused. Re-apply this if you
re-clone `whisper-writer/`.

## Setup from scratch

```powershell
git clone https://github.com/savbell/whisper-writer whisper-writer
cd whisper-writer

# Install av binary first (no MSVC needed)
py -3.11 -m venv venv
.\venv\Scripts\pip install av --prefer-binary

# Relax pinned av version in requirements.txt (av==11.0.0 has no Windows wheel)
(Get-Content requirements.txt -Raw -Encoding Unicode) -replace 'av==11\.0\.0','av>=11.0.0' |
    Set-Content requirements.txt -Encoding Unicode

.\venv\Scripts\pip install -r requirements.txt
```

Then re-create `src/config.yaml` and `.env` from this README.
