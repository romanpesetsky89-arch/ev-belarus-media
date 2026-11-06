// Рендер карусели: node tools/carousel.js <carousel.html> <outDir>
// В HTML — <section class="slide"> 1080x1350 каждая. Сохраняет slide_01.jpg, slide_02.jpg ...
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const [html, out] = [process.argv[2], process.argv[3]];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const n = await p.locator('section.slide').count();
  for (let i = 0; i < n; i++) {
    await p.locator('section.slide').nth(i).screenshot({ path: `${out}/slide_${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close(); console.log('slides', n);
})();
