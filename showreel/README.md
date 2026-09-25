# Motion Reel 26

A 15-second motion-graphics showreel drawn entirely with the Canvas 2D API, with a soundtrack synthesized in Web Audio (120 BPM).

- `index.html` — open over HTTP (`python -m http.server -d showreel`) and press **Play reel** to watch it live.
- `export.js` — renders frames at 120 fps via Playwright and pipes them to ffmpeg (2-frame motion blur → 60 fps H.264 + AAC).
- `showreel.mp4` — the rendered result.

Fonts: Inter Tight, Instrument Serif, JetBrains Mono (SIL Open Font License, via Fontsource).
