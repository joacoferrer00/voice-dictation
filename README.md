# Voice Dictation

Windows push-to-talk dictation. Press `Ctrl+Shift+Space`, talk (English, Spanish, or mixed), press again.
The transcript is copied to the clipboard. Paste anywhere with `Ctrl+V`.

Engine: Groq `whisper-large-v3-turbo` (~1s for a 10s clip). Falls back to OpenRouter if needed.

Autostart: registered as a Windows Scheduled Task (`WhisperWriter`), runs silently at login, no popup.

## Usage

- `Ctrl+Shift+Space` to start recording
- Talk (pause as long as you want, it does not cut off)
- `Ctrl+Shift+Space` again to stop and transcribe
- `Ctrl+V` to paste the result wherever you want

## Config

- API key: `whisper-writer/.env` as `OPENAI_API_KEY`
- Engine settings: `whisper-writer/src/config.yaml`
- Hotkey: `activation_key` in `config.yaml` (default `ctrl+shift+space`)

### Swap engine

In `whisper-writer/.env`:
```
OPENAI_API_KEY=your_key_here
```

In `whisper-writer/src/config.yaml`:
```yaml
model_options:
  api:
    model: whisper-large-v3-turbo
    base_url: https://api.groq.com/openai/v1
```

For OpenRouter fallback: `base_url: https://openrouter.ai/api/v1`, model: `openai/whisper-large-v3`
(note: OpenRouter does not support the audio transcription endpoint via the OpenAI SDK).

## Manage the autostart task

```powershell
Start-ScheduledTask -TaskName "WhisperWriter"   # start now
Stop-Process -Name "pythonw" -ErrorAction SilentlyContinue  # stop
```

## Setup from scratch

```powershell
git clone https://github.com/savbell/whisper-writer whisper-writer
cd whisper-writer

py -3.11 -m venv venv
.\venv\Scripts\pip install av --prefer-binary

# Relax pinned av version (no Windows wheel for av==11.0.0)
(Get-Content requirements.txt -Raw -Encoding Unicode) -replace 'av==11\.0\.0','av>=11.0.0' |
    Set-Content requirements.txt -Encoding Unicode

.\venv\Scripts\pip install -r requirements.txt
```

Then restore `src/config.yaml` and `.env` (see Config section above).

### Code patches (re-apply after re-clone)

`src/main.py` has two changes vs upstream:

1. `on_transcription_complete`: copies result to clipboard with `pyperclip.copy(result)`, no typewrite.
2. `initialize_components`: calls `self.key_listener.start()` at the end instead of `self.main_window.show()`,
   so the app starts silently in the tray.

`src/key_listener.py`: `_on_keyboard_press` / `_on_keyboard_release` in `PynputBackend` skip unknown keys
instead of falling back to `KeyCode.SPACE` (which caused `Ctrl+Shift` alone to trigger the hotkey).
