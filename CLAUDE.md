# Voice Dictation — project entry point

Windows push-to-talk dictation tool. Press a hotkey anywhere, talk (English, Spanish, or mixed), press
again, and the transcribed text lands at the cursor and on the clipboard. Replaces the "open ChatGPT in a
Chrome tab, talk, copy, paste into VS Code" loop so dictating to an LLM is one keystroke.

This is an independent project under `personal/`, NOT versioned by the AIOS root (it is in the AIOS
`.gitignore`). It can carry its own git later.

## How to work here

**The plan is the manual.** Read [PLANNING.md](PLANNING.md) and execute it phase by phase, in order. Each
step has a "Done when" to verify against. Do not redesign; the decisions below are settled.

## Settled decisions (do not relitigate)

- **Tool:** WhisperWriter (savbell/whisper-writer), Python, open source. Cloned into `whisper-writer/`
  (gitignored, keeps its own `.git`).
- **Engine: cloud, Groq Whisper Large V3 Turbo.** Near-instant even on this weak laptop (no GPU), free
  tier plus sub-cent/min, and `large-v3` handles EN/ES code-switching. Local inference was rejected: the
  i5-1135G7 with no GPU runs local models at realtime-or-slower.
- **Fallback engine:** OpenRouter with the existing key. Swap by changing `base_url` + `api_key` + `model`
  in `whisper-writer/config.yaml`, no code change.
- **Output:** always copy to clipboard (a small `pyperclip` patch) AND type at the cursor. So talking with
  no focused field still leaves the text in the clipboard for a later Ctrl+V.
- **Recording mode:** `press_to_toggle` (press to start, stay silent to think, keep talking, press to
  stop and transcribe).

## Hard rules

- **Python 3.11 only** for the venv: `py -3.11 -m venv venv`. The default `python` here is 3.12, do not
  use it.
- **Never commit the API key.** It lives in `.env` (gitignored). Keep it out of any tracked file.
- The `pyperclip` patch edits the gitignored `whisper-writer/`, so document it in README to survive a
  re-clone.
- All `.md` files in English. No em-dashes anywhere (responses, code, commits, docs). Use commas, periods,
  colons, parentheses.
- Git: plain commit messages, no co-author / no Claude signature trailers. Never `git add .` or `-A`, add
  files by name. Do not commit or push unless asked.

## Config reference (verified against the project's `config_schema.yaml`)

In `whisper-writer/config.yaml`:
- `model_options.use_api: true`
- `model_options.common.language: null` (leave null for EN/ES auto-detect)
- `model_options.api.base_url: https://api.groq.com/openai/v1`
- `model_options.api.model: whisper-large-v3-turbo`
- `model_options.api.api_key: <Groq key>`
- `recording_options.recording_mode: press_to_toggle`
- `recording_options.activation_key: ctrl+shift+space` (change if it clashes with VS Code)

Confirm the exact YAML nesting when the file is generated on first run; adjust field paths if it differs.
