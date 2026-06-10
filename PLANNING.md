# Voice Dictation (Windows push-to-talk) — Plan

## Goal
Press a hotkey anywhere in Windows, talk (English, Spanish, or mixed), press again, and have the
transcribed text land at the cursor in whatever app has focus. Replaces the "open ChatGPT in a Chrome
tab, talk, copy, paste into VS Code" loop so dictating to Claude/an LLM is one keystroke away.

## Scope
- In scope: install WhisperWriter (savbell/whisper-writer), wire it to a cloud Whisper engine, set a
  toggle hotkey, confirm it types at the cursor, add an always-copy-to-clipboard patch so the text is
  never lost when no field is focused, make it launchable, document it.
- Out of scope / non-goals: building any tool from scratch; reusing the Discord transcription bot's code
  (only its lesson, that cloud Whisper works, carries over); local GPU/CPU inference; summarization or
  any LLM post-processing of the transcript (the LLM downstream already cleans it up).
- Key decisions & assumptions (settled by the council):
  - **Engine: cloud, via Groq Whisper Large V3 Turbo.** Reasons: ~164x realtime so a 3-min monologue
    transcribes in 1-2s regardless of this laptop's weak CPU, free tier plus sub-cent/min so the cost
    anxiety disappears, and `large-v3` handles EN/ES code-switching that a local `small` model mangles.
  - **Hardware:** i5-1135G7, 4 cores, no GPU. This is why local inference was rejected: `small` runs at
    realtime-or-slower and eats RAM next to VS Code + browser.
  - **Fallback engine:** OpenRouter with the existing key (`https://openrouter.ai/api/v1`), already
    proven working by the Discord bot. Swappable by changing two config fields, no code change.
  - **WhisperWriter is OpenAI-API-compatible**, so any OpenAI-compatible STT endpoint (Groq, OpenRouter)
    works by overriding `base_url` + `api_key` + `model`.
  - **Output: always copy to clipboard + still type at cursor.** Upstream only types via keyboard
    simulation (`input_method: pynput`), so with no focused field the text is lost. A small `pyperclip`
    patch makes it copy to clipboard on every transcription, so the user can talk while moving around the
    PC and paste later with Ctrl+V, while keeping type-at-cursor when a field is focused.

## Stack & constraints
- WhisperWriter: Python **3.11 required** (confirmed available here via `py -3.11`; default `python` is
  3.12, do not use it for the venv). Installs from `requirements.txt`, runs with `python run.py`, has a
  Settings GUI on first launch.
- Config is a `config.yaml` at the cloned repo root, with these relevant fields (verified against the
  project's `config_schema.yaml`):
  - `model_options.use_api` (bool) — `true` to use a cloud API instead of a local model.
  - `model_options.common.language` (ISO-639-1 string, default `null`) — leave `null` for EN/ES
    auto-detect; setting it forces one language and breaks code-switching.
  - `model_options.common.initial_prompt` (string) — optional priming text.
  - `model_options.api.model` (string, default `whisper-1`) — set to the Groq model name.
  - `model_options.api.base_url` (string, default `https://api.openai.com/v1`).
  - `model_options.api.api_key` (string).
  - `recording_options.activation_key` (default `ctrl+shift+space`).
  - `recording_options.recording_mode` (`continuous` | `voice_activity_detection` | `press_to_toggle` |
    `hold_to_record`) — use `press_to_toggle` for the "press, talk, think, keep talking, press" flow.
- Groq endpoint: `base_url = https://api.groq.com/openai/v1`, `model = whisper-large-v3-turbo`, key from
  console.groq.com (free signup).
- Repo convention (AIOS): this is a **new independent project** living under `personal/` but NOT versioned
  by the AIOS root. It must be added to the AIOS `.gitignore` nested-repos block, same as
  `weekly-transcription-bot/`. It can carry its own git later.
- Hard rules: never commit the API key (`.env` and `*.key` are already globally gitignored; keep the key
  out of any tracked file). The cloned `whisper-writer/` brings its own `.git`, so it stays gitignored
  inside this project. No em-dashes, docs in English.

## Plan

### Phase 1 — Scaffold and register the project
1.1 Register the folder in the AIOS `.gitignore`.
   - What: add `/voice-dictation/` to the "Nested project repos" block.
   - Where: `personal/.gitignore` (lines 22-31, alphabetical-ish list).
   - How: insert the line so the AIOS root never tracks this project's contents.
   - Done when: `git -C personal status` does not show `voice-dictation/` as untracked content.
   - Depends on: none.

1.2 Lay down the project skeleton.
   - What: create `README.md` (English, what this is and how to launch), `.gitignore` (ignore
     `whisper-writer/`, `*.key`, `.env`), and a `.env.example` documenting `GROQ_API_KEY=`.
   - Where: `personal/voice-dictation/`.
   - How: README states the engine decision in one line and points at this PLANNING.md for detail.
   - Done when: the three files exist and README explains the launch step.
   - Depends on: 1.1.

### Phase 2 — Install WhisperWriter
2.1 Clone WhisperWriter into the project.
   - What: `git clone https://github.com/savbell/whisper-writer` inside `personal/voice-dictation/`.
   - Where: `personal/voice-dictation/whisper-writer/`.
   - How: run from the project folder; this nested repo keeps its own `.git` and is gitignored by 1.2.
   - Done when: `whisper-writer/run.py` and `whisper-writer/requirements.txt` exist.
   - Depends on: 1.2.

2.2 Create the Python 3.11 venv and install dependencies.
   - What: `py -3.11 -m venv venv` then activate and `pip install -r requirements.txt`.
   - Where: inside `whisper-writer/`.
   - How: must use `py -3.11`, not the default 3.12 `python`, or dependencies may fail. On Windows
     activate with `venv\Scripts\activate`.
   - Done when: `pip install` finishes with no errors and `python -c "import faster_whisper"` (or the
     project's main import) succeeds.
   - Depends on: 2.1.

2.3 Confirm a clean first launch.
   - What: run `python run.py` once.
   - Where: `whisper-writer/`, venv active.
   - How: the Settings GUI should appear (first run) or the app should sit in the tray/background.
   - Done when: the app starts without a stack trace; close it after confirming.
   - Depends on: 2.2.

### Phase 3 — Configure the cloud engine, hotkey, and paste
3.1 Get a Groq API key.
   - What: sign up at console.groq.com, create an API key.
   - Where: external (browser). User action; suggest running the browser login themselves.
   - How: store the key in `personal/voice-dictation/.env` as `GROQ_API_KEY=...` (gitignored). Never
     paste it into a tracked file.
   - Done when: the key exists locally and is not tracked by git.
   - Depends on: none (can run in parallel with Phase 2).

3.2 Point WhisperWriter at Groq.
   - What: set `use_api: true`, `api.base_url: https://api.groq.com/openai/v1`,
     `api.model: whisper-large-v3-turbo`, `api.api_key:` to the Groq key, `common.language: null`.
   - Where: `whisper-writer/config.yaml` (or via the Settings GUI from 2.3).
   - How: editing the YAML directly is the reliable path; the GUI is a fallback. Keep the key only here
     locally, since this config file lives inside the gitignored `whisper-writer/`.
   - Done when: `config.yaml` reflects all five values.
   - Depends on: 2.3, 3.1.

3.3 Set the toggle hotkey and paste behavior.
   - What: set `recording_options.recording_mode: press_to_toggle` and pick `activation_key` (default
     `ctrl+shift+space`; change if it clashes with VS Code). Confirm the output method types/pastes at the
     cursor (WhisperWriter types into the focused field by default).
   - Where: `whisper-writer/config.yaml`.
   - How: `press_to_toggle` gives the "press to start, stay silent to think, keep talking, press to stop
     and transcribe" loop the user wants.
   - Done when: config saved with the chosen mode and key.
   - Depends on: 3.2.

3.4 Patch: always copy the transcription to the clipboard.
   - What: after a transcription is produced, copy the text to the system clipboard in addition to the
     existing keyboard-simulation typing, so nothing is lost when no field has focus.
   - Where: the function in `whisper-writer/src/` that outputs the transcribed text (the keyboard-input /
     result-handling code that today calls the `pynput` typing path). Add `pip install pyperclip` to the
     venv and a `pyperclip.copy(text)` call at that point.
   - How: keep the existing typing behavior untouched and add the clipboard copy alongside it, so both
     happen on every transcription. This is a tiny local change to the cloned (gitignored) repo; note it
     in README so it survives a future re-clone.
   - Done when: with no text field focused, after dictating, Ctrl+V in any app pastes the transcript; and
     with a field focused, the text still types in as before.
   - Depends on: 3.3.

### Phase 4 — Test against real use
4.1 Short-clip test.
   - What: focus a text field (e.g. VS Code), press the hotkey, say a one-line idea in English, press
     again.
   - Done when: text appears at the cursor within ~2s, readable.
   - Depends on: 3.3.

4.2 Long monologue + bilingual test.
   - What: press, talk for ~2-3 minutes including at least one mid-sentence EN/ES switch and a few
     seconds of silence (thinking), press again.
   - Done when: full transcript lands, the silence did not cut it off, and the EN/ES switch is handled
     without garbling. If silence cut it, raise `silence_duration` is irrelevant in `press_to_toggle`,
     so confirm the mode is actually toggle, not VAD.
   - Depends on: 4.1.

4.3 Decide on fallback only if Groq disappoints.
   - What: if latency or quality is unacceptable, switch `base_url` to `https://openrouter.ai/api/v1`,
     `api_key` to the OpenRouter key, `model` to an OpenRouter Whisper model.
   - Done when: either Groq is accepted as-is, or the OpenRouter swap is tested and works. Document the
     winner in README.
   - Depends on: 4.2.

### Phase 5 — Make it stick
5.1 One-click launch.
   - What: write `start.bat` at the project root that activates the venv and runs `python run.py` (mirror
     the pattern from `weekly-transcription-bot/start.bat`).
   - Where: `personal/voice-dictation/start.bat`.
   - Done when: double-clicking it launches the tool with no terminal fiddling.
   - Depends on: 3.3.

5.2 Optional autostart.
   - What: decide whether it launches on Windows login (Startup folder shortcut to `start.bat`).
   - Done when: user confirms yes/no; if yes, shortcut is placed in `shell:startup`.
   - Depends on: 5.1.

5.3 Finalize docs.
   - What: README records the chosen engine, the hotkey, how to launch, where the key lives, and the
     one-line fallback recipe.
   - Done when: README is enough to re-set-up on a fresh machine without re-reading this plan.
   - Depends on: 4.3, 5.1.

## Open questions
- `activation_key` choice: keep `ctrl+shift+space` or pick something that never clashes with VS Code /
  Claude Code bindings? Decide at 3.3.
- Autostart on login: wanted or not? Decide at 5.2.
- Does WhisperWriter's current `config.yaml` nest fields under `model_options` / `recording_options` (per
  schema) or flatten them? Confirm the exact nesting when the file is generated at 2.3 and adjust 3.2-3.3
  field paths accordingly.
