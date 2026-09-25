// Renders index.html to showreel.mp4: 1920x1080, 60 fps with 2-sample motion blur, synthesized stereo audio.
// usage: serve this folder over HTTP, then: node export.js <url> <ffmpeg> <out.mp4>
// (needs the `playwright` package; PW env var may point to it)
const { chromium } = require(process.env.PW || 'playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const [url, FF, out] = process.argv.slice(2);
const DUR = 15, RENDER_FPS = 120;
(async () => {
  const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.error('page error:', e.message));
  await p.goto(url + '?export'); await p.evaluate(() => window.ready);
  const wav = path.join(os.tmpdir(), 'showreel-audio.raw');
  fs.writeFileSync(wav, Buffer.from(await p.evaluate(() => window.renderAudioBase64()), 'base64'));
  const ff = spawn(FF, ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(RENDER_FPS), '-c:v', 'mjpeg', '-i', '-',
    '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', wav,
    '-vf', 'tmix=frames=2,fps=60', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'slow',
    '-af', 'alimiter=limit=0.89:level=false', '-c:a', 'aac', '-b:a', '256k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = DUR * RENDER_FPS;
  for (let i = 0; i < n; i++) {
    const u = await p.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', .96); }, i / RENDER_FPS);
    if (!ff.stdin.write(Buffer.from(u.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 240 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('wrote', out);
})();
