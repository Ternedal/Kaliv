(() => {
  const params = new URLSearchParams(window.location.search);
  const lang = params.get('lang') === 'en' ? 'en' : 'da';
  const body = document.body;

  document.documentElement.lang = lang;
  document.title = lang === 'en' ? body.dataset.titleEn : body.dataset.titleDa;

  document.querySelectorAll('[data-da][data-en]').forEach((element) => {
    element.textContent = lang === 'en' ? element.dataset.en : element.dataset.da;
  });

  document.querySelectorAll('[data-da-label][data-en-label]').forEach((element) => {
    element.setAttribute('aria-label', lang === 'en' ? element.dataset.enLabel : element.dataset.daLabel);
  });

  document.querySelectorAll('[data-da-alt][data-en-alt]').forEach((element) => {
    element.setAttribute('alt', lang === 'en' ? element.dataset.enAlt : element.dataset.daAlt);
  });

  const description = lang === 'en' ? body.dataset.descriptionEn : body.dataset.descriptionDa;
  const descriptionMeta = document.querySelector('meta[name="description"]');
  if (descriptionMeta) descriptionMeta.setAttribute('content', description);

  const title = document.title;
  const shareDescription = lang === 'en'
    ? 'The same personal AI across computer, phone, home and VR — built on ModelRig.'
    : 'Den samme personlige AI på computer, telefon, i hjemmet og i VR — bygget på ModelRig.';

  document.querySelectorAll('meta[property="og:title"], meta[name="twitter:title"]').forEach((meta) => meta.setAttribute('content', title));
  document.querySelectorAll('meta[property="og:description"], meta[name="twitter:description"]').forEach((meta) => meta.setAttribute('content', shareDescription));
  const localeMeta = document.querySelector('meta[property="og:locale"]');
  if (localeMeta) localeMeta.setAttribute('content', lang === 'en' ? 'en_US' : 'da_DK');

  document.querySelectorAll('a.local-link').forEach((anchor) => {
    const raw = anchor.getAttribute('href');
    if (!raw || raw.startsWith('#') || raw.startsWith('http') || raw.startsWith('mailto:')) return;

    const url = new URL(raw, window.location.href);
    if (lang === 'en') url.searchParams.set('lang', 'en');
    else url.searchParams.delete('lang');

    anchor.setAttribute('href', `${url.pathname.split('/').pop() || './'}${url.search}${url.hash}`);
  });

  document.querySelectorAll('[data-lang]').forEach((anchor) => {
    anchor.toggleAttribute('aria-current', anchor.dataset.lang === lang);
  });

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js'));
  }
})();
