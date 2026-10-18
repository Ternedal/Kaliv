(() => {
  const body = document.body;
  const isEnglish = new URLSearchParams(location.search).get('lang') === 'en';
  if (isEnglish) {
    document.documentElement.lang = 'en';
    document.querySelectorAll('[data-en]').forEach(node => { node.textContent = node.dataset.en; });
    document.querySelectorAll('[data-en-href]').forEach(node => { node.href = node.dataset.enHref; });
    document.querySelectorAll('[data-en-aria-label]').forEach(node => { node.setAttribute('aria-label', node.dataset.enAriaLabel); });
    document.querySelectorAll('[data-language]').forEach(link => {
      const current = link.dataset.language === 'en';
      link.classList.toggle('is-current', current);
      if (current) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
    });
    if (body.dataset.titleEn) document.title = body.dataset.titleEn;
    const description = body.dataset.descriptionEn;
    if (description) {
      const setMeta = (selector, value) => { const el = document.querySelector(selector); if (el) el.content = value; };
      if (body.dataset.titleEn) {
        setMeta('meta[property="og:title"]', body.dataset.titleEn);
        setMeta('meta[name="twitter:title"]', body.dataset.titleEn);
      }
      setMeta('meta[name="description"]', description);
      setMeta('meta[property="og:description"]', description);
      setMeta('meta[name="twitter:description"]', description);
      setMeta('meta[property="og:locale"]', 'en_US');
      const canonical = new URL(`https://kaliv.dk/${body.dataset.path}?lang=en`);
      const link = document.querySelector('link[rel="canonical"]'); if (link) link.href = canonical.href;
      setMeta('meta[property="og:url"]', canonical.href);
      const structured = document.querySelector('script[type="application/ld+json"]');
      if (structured) { try { const data = JSON.parse(structured.textContent); if (body.dataset.titleEn) data.name = body.dataset.titleEn; data.description = description; data.inLanguage = 'en'; data.url = canonical.href; structured.textContent = JSON.stringify(data); } catch {} }
    }
  }
  if ('serviceWorker' in navigator && location.protocol === 'https:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js', {scope:'./', updateViaCache:'none'}).catch(() => {}), {once:true});
  }
})();
