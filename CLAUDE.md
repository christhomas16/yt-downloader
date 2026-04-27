# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run / dev

- `./run.sh` — sets up venv, installs deps, **upgrades yt-dlp**, then runs the Flask app on http://127.0.0.1:8080.
- The app uses Flask debug mode, so editing `app.py` triggers an auto-reload.
- There are no tests, no linter, no build step. Smoke-test by hitting endpoints with `curl` (see below) or using the browser UI.

## Architecture

Single-file Flask backend (`app.py`) + static UI (`index.html` + `script.js` + `style.css`). Downloaded files go to `downloads/` (gitignored).

**Two endpoints, both POST JSON `{"url": "..."}`:**

- `/download` — video. Used by all three UI tabs (YouTube/Reddit/X). yt-dlp auto-detects the source from the URL — there is no per-platform branching, despite what the UI suggests.
- `/download_audio` — audio-only. Accepts `{"url", "format": "native"|"mp3"}`. Native keeps source codec (Opus/m4a, no re-encode); `mp3` re-encodes to 320kbps.

Both endpoints share `_base_opts()` for yt-dlp config and `_resolve_filename()` for finding the post-processed output path (which is non-trivial — see below).

**Static-file serving** is whitelisted to `script.js`/`style.css` only. Don't loosen this — the route used to serve the entire project root, including `app.py`.

## yt-dlp gotchas (the real reason this file exists)

These are the things that broke during development; preserving the fix context here will save you the same debugging time.

1. **YouTube format extraction is fragile.** Three things must be in place or YouTube downloads degrade silently to lower quality (or fail outright with `"The following content is not available on this app"`):
   - **yt-dlp must be recent.** `run.sh` upgrades it on every launch — don't disable this. YouTube ships breaking changes monthly.
   - **Deno must be installed** (`brew install deno`). yt-dlp uses it as the JS runtime to solve YouTube's signature challenges.
   - **`remote_components: ['ejs:github']`** in `_base_opts()` fetches the EJS challenge-solver script from GitHub. Required alongside Deno.

2. **Output template uses `%(title)s.%(ext)s`** with `restrictfilenames: True`. Do NOT hardcode `.mp4` in the template — yt-dlp adds its own extension and you'll get `Title.mp4.mp4`. `restrictfilenames` strips slashes/emojis/etc. from titles.

3. **Resolving the final filename after post-processing is annoying.** yt-dlp may run multiple post-processors (merge, extract audio, embed thumbnail, embed metadata) and each can change the filename and extension. `_resolve_filename()` checks `requested_downloads[-1].filepath` first (most reliable post-processing), then falls back to `filepath` / `_filename`, then to `title.ext`. Don't simplify it.

4. **Video format selector explicitly prefers H.264 + AAC.** The "obvious" `bestvideo+bestaudio` selector picks AV1 + Opus on YouTube, which **does not play in QuickTime, Apple Music, iPhone, or AirDrop previews on macOS**. The current selector falls back gracefully when H.264/AAC isn't offered (e.g. Reddit/X clips). If you change this, manually verify on a Mac.

5. **Audio "native" mode** uses `FFmpegExtractAudio` with `preferredcodec: 'best'` — this re-muxes (no re-encode) into the right container per source codec (`.opus` for Opus, `.m4a` for AAC). Don't use `'merge_output_format'` for audio, and don't hardcode the extension.

6. **`mutagen` is a hard runtime dep** for the audio endpoint's `EmbedThumbnail` post-processor. yt-dlp doesn't enforce it; it crashes at post-processing time if missing.

## Testing changes

There's no test suite. Smoke-test with a known short YouTube video:

```bash
# video
curl -X POST http://127.0.0.1:8080/download \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.youtube.com/watch?v=jNQXAC9IVRw"}'

# audio (native — Opus or m4a)
curl -X POST http://127.0.0.1:8080/download_audio \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.youtube.com/watch?v=jNQXAC9IVRw","format":"native"}'

# audio (mp3 320)
curl -X POST http://127.0.0.1:8080/download_audio \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.youtube.com/watch?v=jNQXAC9IVRw","format":"mp3"}'
```

Verify the actual file with `ffprobe -v error -show_entries stream=codec_name,codec_type downloads/<file>` — yt-dlp will report success even if it silently fell back to a lower format.

To see what formats YouTube currently offers for a URL without downloading:

```bash
./venv/bin/yt-dlp -F "<url>"
```
