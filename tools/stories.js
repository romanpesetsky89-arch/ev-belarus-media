// Рендер сторис 1080x1920: node tools/stories.js <html> <outDir> <prefix>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const [html, out, pre] = [process.argv[2], process.argv[3], process.argv[4] || 'story'];
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const els = p.locator('section.story'); const n = await els.count();
  for (let i = 0; i < n; i++) {
    const id = await els.nth(i).getAttribute('id');
    await els.nth(i).screenshot({ path: `${out}/${id}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close(); console.log('stories', n);
})();
