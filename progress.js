(() => {
  const isEnglish = new URLSearchParams(location.search).get('lang') === 'en';
  if (!isEnglish) return;
  document.documentElement.lang = 'en';
  document.querySelectorAll('[data-en]').forEach(node => { node.textContent = node.dataset.en; });
  document.querySelectorAll('[data-en-href]').forEach(node => { node.href = node.dataset.enHref; });
  document.querySelectorAll('[data-language]').forEach(link => { const current = link.dataset.language === 'en'; link.classList.toggle('is-current',current); if (current) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current'); });
  document.querySelector('.lang')?.setAttribute('aria-label','Choose language');
  document.querySelector('.hero-signal')?.setAttribute('aria-label','Current V1 status');
  document.querySelector('.metrics')?.setAttribute('aria-label','Public project key points');
  document.querySelector('.repos')?.setAttribute('aria-label','Current repository heads');
  document.querySelector('.gates')?.setAttribute('aria-label','Next proof for the four V1 gates');
  document.querySelector('.closing-aside img')?.setAttribute('alt','Kaliv’s futuristic ankh symbol');
  document.title = 'Kaliv — status';
  const description = 'Kaliv and ModelRig right now: what works, what has been observed on real hardware and what remains before V1.';
  const setMeta = (selector,value) => { const el = document.querySelector(selector); if (el) el.content = value; };
  setMeta('meta[name="description"]',description); setMeta('meta[property="og:title"]','Kaliv — status'); setMeta('meta[property="og:description"]','A clear status for Kaliv: public release, physical partial proof and the open path to one persistent AI across four surfaces.'); setMeta('meta[property="og:locale"]','en_US'); setMeta('meta[name="twitter:title"]','Kaliv — status'); setMeta('meta[name="twitter:description"]','What works now, what has been physically observed and what remains before V1.');
  const url = new URL('https://kaliv.dk/progress.html?lang=en'); document.querySelector('link[rel="canonical"]').href = url.href; setMeta('meta[property="og:url"]',url.href);
  const structured = document.querySelector('script[type="application/ld+json"]'); if (structured) { try { const data = JSON.parse(structured.textContent); data.name = 'Kaliv — status'; data.description = description; data.inLanguage = 'en'; data.url = url.href; structured.textContent = JSON.stringify(data); } catch {} }
})();

if ('serviceWorker' in navigator && location.protocol === 'https:') window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js',{scope:'./',updateViaCache:'none'}).catch(()=>{}),{once:true});
