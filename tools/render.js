// usage: node render.js <html> <framesDir> <seconds> <fps>
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [html, dir, secs, fps] = [process.argv[2], process.argv[3], +process.argv[4], +process.argv[5]];
  fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(() => document.fonts.ready);
  const n = Math.round(secs * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.render(t), i / fps);
    await p.screenshot({ path: `${dir}/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
  console.log('frames', n);
})();
