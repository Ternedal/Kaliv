// Development tools are installed in the CI runner's temporary directory.
// The site and its Python build have no npm dependencies.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve, extname } from 'node:path';
import { pathToFileURL } from 'node:url';

const requireQA = createRequire(resolve(process.env.QA_TOOLS, 'package.json'));
const { chromium } = requireQA('playwright');
const { default: AxeBuilder } = requireQA('@axe-core/playwright');
const { HtmlValidate } = requireQA('html-validate');
const { default: lighthouse } = await import(pathToFileURL(requireQA.resolve('lighthouse')));
const { launch: launchChrome } = requireQA('chrome-launcher');
const root = resolve('_site');
const reports = resolve(process.env.QA_REPORTS);
await mkdir(reports, { recursive: true });
const pages = ['index.html', 'brief.html', 'hub.html', 'proofs.html', 'architecture.html', 'progress.html', 'download.html'];
const errors = [];
const check = (ok, message) => { if (!ok) errors.push(message); };
const json = (name, data) => writeFile(resolve(reports, name), JSON.stringify(data, null, 2));
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.webp': 'image/webp' };
const server = createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const file = resolve(root, '.' + (pathname.endsWith('/') ? pathname + 'index.html' : pathname));
    if (!file.startsWith(root + '/')) throw new Error('Outside public site');
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': `${types[extname(file)] || 'text/plain'}; charset=utf-8`, 'Cache-Control': 'no-store' });
    res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(await readFile(resolve(root, '404.html')));
  }
});
await new Promise(done => server.listen(0, '127.0.0.1', done));
const base = `http://127.0.0.1:${server.address().port}`;
let browser, chrome;
try {
  const validator = new HtmlValidate({ extends: [], rules: { 'wcag/h63': 'error', 'aria-label-misuse': 'error' } });
  const markup = [];
  for (const page of [...pages, '404.html', 'offline.html', ...[...pages, '404.html', 'offline.html'].map(name => 'en/' + name)]) {
    const report = await validator.validateString(await readFile(resolve(root, page), 'utf8'), page);
    markup.push({ page, valid: report.valid, results: report.results });
    check(report.valid, `Markup: ${page}`);
  }
  await json('markup.json', markup);
  for (const path of ['/README.md', '/LICENSE', '/dist/', '/tools/build.py'])
    check((await fetch(base + path)).status === 404, `Unexpected publication: ${path}`);
  for (const path of [...pages, 'project.json', 'llms.txt', 'sitemap.xml', 'robots.txt', 'site.webmanifest', 'service-worker.js'])
    check((await fetch(`${base}/${path}`)).status === 200, `Missing public file: ${path}`);

  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
  const firstPaint = [];
  // Slow language scripts must not allow a Danish first paint on any English URL.
  for (const name of pages) for (let attempt = 0; attempt < 3; attempt++) {
    const paintContext = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 390, height: 900 } });
    const paintPage = await paintContext.newPage();
    await paintPage.route('**/*.js*', async route => {
      await new Promise(done => setTimeout(done, 750));
      await route.continue();
    });
    await paintPage.addInitScript(() => {
      window.kalivPaintCheck = { firstLanguage: null, cls: 0 };
      new PerformanceObserver(list => {
        if (list.getEntries().some(entry => entry.name === 'first-contentful-paint'))
          window.kalivPaintCheck.firstLanguage = document.documentElement.lang;
      }).observe({ type: 'paint', buffered: true });
      new PerformanceObserver(list => {
        for (const entry of list.getEntries())
          if (!entry.hadRecentInput) window.kalivPaintCheck.cls += entry.value;
      }).observe({ type: 'layout-shift', buffered: true });
    });
    await paintPage.goto(`${base}/${name}?lang=en`, { waitUntil: 'networkidle' });
    await paintPage.waitForFunction(() => window.kalivPaintCheck.firstLanguage !== null);
    const result = await paintPage.evaluate(() => window.kalivPaintCheck);
    firstPaint.push({ page: name, attempt, scriptDelayMs: 750, ...result });
    check(result.firstLanguage === 'en', `Wrong first-paint language: ${name}/${result.firstLanguage}`);
    check(result.cls === 0, `Language-script layout shift: ${name}/${result.cls}`);
    await paintContext.close();
  }
  await json('first-paint.json', firstPaint);
  const context = await browser.newContext({ serviceWorkers: 'block' });
  await context.addInitScript(() => {
    window.kalivPolicyViolations = [];
    document.addEventListener('securitypolicyviolation', event => {
      window.kalivPolicyViolations.push({ directive: event.effectiveDirective, blocked: event.blockedURI });
    });
  });
  const page = await context.newPage();
  const layout = [], accessibility = [], links = new Set();
  for (const width of [320, 360, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    for (const name of pages) for (const lang of ['da', 'en']) {
      const url = `${base}/${lang === 'en' ? 'en/' : ''}${name}`;
      await page.goto(url, { waitUntil: 'networkidle' });
      const result = await page.evaluate(() => {
        const rect = e => { const r = e.getBoundingClientRect(); return { x: r.x, width: r.width, height: r.height }; };
        return {
          language: document.documentElement.lang,
          width: document.documentElement.clientWidth,
          scrollWidth: document.documentElement.scrollWidth,
          policyViolations: window.kalivPolicyViolations,
          languageLinks: [...document.querySelectorAll('.language a, .lang a')]
            .map(e => ({ ...rect(e), current: e.getAttribute('aria-current') })),
          footerLinks: [...document.querySelectorAll('footer a')].map(rect),
          localLinks: [...document.querySelectorAll('a[href], link[href], img[src], script[src]')]
            .map(e => e.href || e.src).filter(href => href && new URL(href).origin === location.origin),
        };
      });
      layout.push({ page: name, lang, viewport: width, ...result });
      check(result.language === lang, `Wrong language: ${name}/${lang}`);
      check(result.scrollWidth === result.width, `Overflow: ${name}/${lang}/${width}: ${result.scrollWidth}`);
      check(result.policyViolations.length === 0, `Unexpected CSP violation: ${name}/${lang}/${width}: ${JSON.stringify(result.policyViolations)}`);
      check(result.languageLinks.length === 2, `Missing language links: ${name}/${lang}`);
      check(result.languageLinks.filter(link => link.current === 'page').length === 1, `Current language: ${name}/${lang}`);
      for (const r of result.languageLinks)
        check(r.width >= 24 && r.height >= 24 && r.x >= 0 && r.x + r.width <= result.width + 0.5, `Language target: ${name}/${lang}/${width}`);
      for (const r of result.footerLinks)
        check(r.height >= 24, `Footer target: ${name}/${lang}/${width}`);
      result.localLinks.forEach(link => links.add(link.split('#')[0]));
      if (width === 390) {
        const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']).analyze();
        accessibility.push({ page: name, lang, violations: audit.violations, incomplete: audit.incomplete });
        check(audit.violations.length === 0, `Axe: ${name}/${lang}: ${audit.violations.map(v => v.id).join(', ')}`);
        if (lang === 'da') await page.screenshot({ path: resolve(reports, `${name}-390.png`) });
      }
    }
  }
  await json('layout.json', layout);
  await json('accessibility.json', accessibility);
  for (const link of links) check((await fetch(link)).status === 200, `Broken local link: ${link}`);
  await json('links.json', [...links]);
  // English, canonical URLs, previews and language controls also work with JS off.
  const noJS = await browser.newContext({ javaScriptEnabled: false, serviceWorkers: 'block', viewport: { width: 390, height: 900 } });
  const plain = await noJS.newPage();
  const staticLanguages = [];
  for (const name of pages) {
    const path = name === 'index.html' ? '/en/' : '/en/' + name;
    await plain.goto(base + path);
    const facts = {
      page: name,
      language: await plain.locator('html').getAttribute('lang'),
      heading: await plain.locator('h1').textContent(),
      canonical: await plain.locator('link[rel="canonical"]').getAttribute('href'),
      locale: await plain.locator('meta[property="og:locale"]').getAttribute('content'),
    };
    check(facts.language === 'en' && facts.heading.length > 0, `Static English: ${name}`);
    check(facts.canonical === 'https://kaliv.dk' + path && facts.locale === 'en_US', `English metadata: ${name}`);
    await plain.locator('.language a, .lang a').filter({ hasText: 'DA' }).click();
    check((await plain.locator('html').getAttribute('lang')) === 'da', `No-JS Danish control: ${name}`);
    await plain.locator('.language a, .lang a').filter({ hasText: 'EN' }).click();
    check((await plain.locator('html').getAttribute('lang')) === 'en', `No-JS English control: ${name}`);
    staticLanguages.push(facts);
  }
  await json('static-languages.json', staticLanguages);
  await noJS.close();
  // Click the mobile EN control, so a visible rectangle alone cannot pass.
  for (const name of pages) {
    await page.setViewportSize({ width: 320, height: 900 });
    await page.goto(`${base}/${name}`);
    await page.locator('.language a, .lang a').filter({ hasText: 'EN' }).click();
    await page.waitForFunction(() => document.documentElement.lang === 'en');
  }
  for (const name of pages) {
    await page.goto(`${base}/${name}?lang=en&source=legacy#content`, { waitUntil: 'networkidle' });
    const path = name === 'index.html' ? '/en/' : '/en/' + name;
    check(page.url() === base + path + '?source=legacy#content', `Legacy English redirect: ${name}`);
  }
  await context.close();

  // Check enforcement, not just the presence of a policy string.
  const policyContext = await browser.newContext({ serviceWorkers: 'block' });
  const policyPage = await policyContext.newPage();
  await policyPage.addInitScript(() => {
    window.kalivPolicyViolations = [];
    document.addEventListener('securitypolicyviolation', event => {
      window.kalivPolicyViolations.push({ directive: event.effectiveDirective, blocked: event.blockedURI });
    });
  });
  await policyPage.goto(base + '/');
  const color = await policyPage.evaluate(() => getComputedStyle(document.body).color);
  await policyPage.evaluate(() => {
    const inline = document.createElement('script');
    inline.textContent = 'window.kalivUntrustedScriptRan = true';
    document.head.append(inline);
    const external = document.createElement('script');
    external.src = 'https://blocked.invalid/kaliv-csp-probe.js';
    document.head.append(external);
    const style = document.createElement('style');
    style.textContent = 'body { color: rgb(1, 2, 3) !important; }';
    document.head.append(style);
    const base = document.createElement('base');
    base.href = 'https://blocked.invalid/';
    document.head.append(base);
  });
  await policyPage.waitForFunction(() => window.kalivPolicyViolations.length >= 4);
  const enforcement = await policyPage.evaluate(() => ({
    inlineScriptRan: window.kalivUntrustedScriptRan === true,
    color: getComputedStyle(document.body).color,
    baseURI: document.baseURI,
    violations: window.kalivPolicyViolations,
  }));
  check(!enforcement.inlineScriptRan, 'CSP allowed an untrusted inline script');
  check(enforcement.color === color, 'CSP allowed an untrusted inline style');
  check(enforcement.baseURI === base + '/', 'CSP allowed a changed document base');
  check(enforcement.violations.some(v => v.blocked === 'https://blocked.invalid' || v.blocked.startsWith('https://blocked.invalid/')), 'CSP did not block an external script');
  await json('content-security-policy.json', enforcement);
  await policyContext.close();

  // Simulate an existing v75 cache, then install the new worker at the same URL.
  const offline = await browser.newContext();
  const offlinePage = await offline.newPage();
  const offlineEvents = [];
  offlinePage.on('framenavigated', frame => { if (frame === offlinePage.mainFrame()) offlineEvents.push({ type: 'navigation', url: frame.url() }); });
  offlinePage.on('requestfailed', request => offlineEvents.push({ type: 'failed', url: request.url(), failure: request.failure() }));
  offlinePage.on('console', message => offlineEvents.push({ type: 'console', level: message.type(), message: message.text() }));
  offlinePage.on('pageerror', error => offlineEvents.push({ type: 'error', message: error.message }));
  await offlinePage.addInitScript(() => {
    for (const type of ['online', 'offline', 'beforeunload', 'pagehide', 'pageshow'])
      window.addEventListener(type, () => console.info('kaliv-offline-event ' + JSON.stringify({type, url: location.href, online: navigator.onLine})));
  });
  await offlinePage.goto(`${base}/offline.html`);
  await offlinePage.evaluate(async () => {
    const old = await caches.open('kaliv-shell-v75');
    await old.put('/home.css?v=72', new Response('/* stale v75 asset */'));
  });
  await offlinePage.goto(base + '/');
  await offlinePage.evaluate(() => navigator.serviceWorker.ready);
  await offlinePage.waitForFunction(() => navigator.serviceWorker.controller !== null);
  const activeWorker = offline.serviceWorkers().find(worker => worker.url().endsWith('/service-worker.js'));
  const cacheState = await offlinePage.evaluate(async () => {
    const names = await caches.keys();
    const current = names.find(name => name.startsWith('kaliv-shell-') && name !== 'kaliv-shell-v75');
    if (!current) throw new Error('Current service worker cache missing');
    const cache = await caches.open(current);
    const entries = await Promise.all((await cache.keys()).map(async request => ({
      url: request.url, bytes: (await (await cache.match(request)).arrayBuffer()).byteLength,
    })));
    return { names, current, entries, bytes: entries.reduce((sum, entry) => sum + entry.bytes, 0) };
  });
  check(!cacheState.names.includes('kaliv-shell-v75'), 'Old service worker cache remains');
  // Runtime requests can add hero images; measure the actual install list separately.
  const workerSource = await readFile(resolve(root, 'service-worker.js'), 'utf8');
  const coreMatch = workerSource.match(/const CORE_ASSETS\s*=\s*(\[[\s\S]*?\]);/);
  assert.ok(coreMatch, 'Generated precache list missing');
  const coreAssets = JSON.parse(coreMatch[1]);
  check(coreAssets.length > 0, 'Generated precache list is empty');
  let coreBytes = 0;
  for (const asset of coreAssets) coreBytes += (await (await fetch(new URL(asset, base + '/'))).arrayBuffer()).byteLength;
  check(coreBytes < 600 * 1024, `Precache over budget: ${coreBytes}`);
  await offline.setOffline(true);
  const offlineNavigations = [];
  const recordOffline = async response => {
    offlineNavigations.push({
      url: offlinePage.url(), responseURL: response?.url(), status: response?.status(), fromWorker: response?.fromServiceWorker(), fallbackLanguage: response?.headers()['x-kaliv-offline-language'],
      ...await offlinePage.evaluate(() => ({ language: document.documentElement.lang, title: document.title, online: navigator.onLine, controller: navigator.serviceWorker.controller?.scriptURL })),
    });
  };
  await offlinePage.goto(`${base}/hub.html?lang=en`);
  await offlinePage.waitForFunction(() => document.documentElement.lang === 'en');
  check((await offlinePage.locator('h1').textContent()).includes('Kaliv'), 'Offline English page failed');
  await recordOffline(await offlinePage.goto(`${base}/unvisited-route`));
  check((await offlinePage.title()).toLowerCase().includes('offline'), 'Offline fallback failed');
  await recordOffline(await offlinePage.goto(`${base}/en/unvisited-route`));
  check((await offlinePage.locator('html').getAttribute('lang')) === 'en', 'English offline fallback failed');
  const workerEvidence = await activeWorker.evaluate(async () => {
    const page = await caches.match(new URL('/en/offline.html', self.location.href));
    return { englishCached: { url: page?.url, headers: page ? Object.fromEntries(page.headers) : {}, html: page ? await page.text() : '' } };
  });
  console.log(JSON.stringify({ offlineNavigations, offlineEvents, workerEvidence }, null, 2));
  for (let i = 0; i < 6; i++) for (const language of ['da', 'en']) {
    const path = `${language === 'en' ? '/en' : ''}/offline-probe-${i}`;
    const response = await offlinePage.goto(base + path);
    await recordOffline(response);
    check(offlinePage.url() === base + path && response?.fromServiceWorker(), `Offline navigation did not commit: ${path}`);
    check((await offlinePage.locator('html').getAttribute('lang')) === language, `Offline language: ${path}`);
    check(response?.headers()['x-kaliv-offline-language'] === language, `Offline response language: ${path}`);
  }
  await offlinePage.goto(`${base}/en/offline.html`);
  const retryError = await Promise.all([offlinePage.waitForNavigation(), offlinePage.locator('#retry-connection').click()]).then(() => null, error => error.message);
  if (retryError) console.log(JSON.stringify({ retryError, offlineEvents }, null, 2));
  check(!retryError, 'Offline retry navigation failed');
  check((await offlinePage.locator('html').getAttribute('lang')) === 'en', 'Offline retry changed language');
  check(await offlinePage.locator('.symbol img').evaluate(img => img.complete && img.naturalWidth > 0), 'Offline illustration unavailable');
  await json('service-worker.json', { ...cacheState, coreAssets, coreBytes, offlineNavigations, workerEvidence, offlineEnglish: true, offlineFallback: true });
  console.log(JSON.stringify({ offlineNavigations, offlineEvents, workerEvidence, cachedOfflinePages: cacheState.entries.filter(entry => entry.url.includes('offline.html')) }, null, 2));
  await offline.close();
  await browser.close();
  browser = null;

  // Mobile Lighthouse on both languages; reports retain individual audit results.
  chrome = await launchChrome({ chromePath: process.env.CHROME_PATH, chromeFlags: ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage'] });
  const scores = [];
  for (const name of pages) for (const lang of ['da', 'en']) {
    const { lhr } = await lighthouse(`${base}/${lang === 'en' ? 'en/' : ''}${name}`, {
      port: chrome.port, onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'], logLevel: 'error',
    });
    const summary = { page: name, lang, performance: lhr.categories.performance.score, accessibility: lhr.categories.accessibility.score, cls: lhr.audits['cumulative-layout-shift'].numericValue };
    scores.push(summary);
    await json(`lighthouse-${name}-${lang}.json`, lhr);
    check(summary.performance >= 0.95, `Lighthouse performance: ${name}/${lang}: ${summary.performance}`);
    check(summary.accessibility >= 0.98, `Lighthouse accessibility: ${name}/${lang}: ${summary.accessibility}`);
    check(summary.cls === 0, `Layout shift: ${name}/${lang}: ${summary.cls}`);
    for (const id of ['color-contrast', 'image-aspect-ratio', 'label-content-name-mismatch', 'canonical']) {
      const audit = lhr.audits[id];
      check(audit && (audit.score === 1 || audit.scoreDisplayMode === 'notApplicable'), `Lighthouse audit: ${name}/${lang}/${id}`);
    }
  }
  await json('lighthouse-summary.json', scores);
  await json('summary.json', { layoutCases: layout.length, localLinks: links.size, errors });
  console.log(JSON.stringify({ layoutCases: layout.length, localLinks: links.size, firstPaint, lighthouse: scores, errors }, null, 2));
  assert.equal(errors.length, 0, errors.join('\n'));
} finally {
  if (browser) await browser.close();
  if (chrome) await chrome.kill();
  await new Promise(done => server.close(done));
}
