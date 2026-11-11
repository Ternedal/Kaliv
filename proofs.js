(() => {
  const isEnglish = new URLSearchParams(location.search).get('lang') === 'en';
  if (!isEnglish) return;
  document.documentElement.lang = 'en';
  document.querySelectorAll('[data-en]').forEach(node => { node.textContent = node.dataset.en; });
  document.querySelectorAll('[data-en-href]').forEach(node => { node.href = node.dataset.enHref; });
  document.querySelectorAll('[data-language]').forEach(link => { const current = link.dataset.language === 'en'; link.classList.toggle('is-current',current); if (current) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current'); });
  document.querySelector('.lang')?.setAttribute('aria-label','Choose language');
  document.querySelector('.hero-board')?.setAttribute('aria-label','Four open V1 proofs');
  document.querySelector('.score')?.setAttribute('aria-label','Proof ledger status');
  document.querySelector('.evidence-grid')?.setAttribute('aria-label','Documented partial proofs');
  document.querySelector('.rule-aside img')?.setAttribute('alt','Kaliv’s futuristic ankh symbol');
  document.title = 'Kaliv — V1 proof ledger';
  const description = 'What Kaliv and ModelRig can prove now — and the four concrete results still missing before V1.';
  const setMeta = (selector,value) => { const el = document.querySelector(selector); if (el) el.content = value; };
  setMeta('meta[name="description"]',description); setMeta('meta[property="og:title"]','Kaliv — V1 proof ledger'); setMeta('meta[property="og:description"]','An honest boundary between public release, physical observation, software tests and complete V1 proof.'); setMeta('meta[property="og:locale"]','en_US'); setMeta('meta[name="twitter:title"]','Kaliv — V1 proof ledger'); setMeta('meta[name="twitter:description"]','What is proven now — and the four concrete results still missing before V1.');
  const url = new URL('https://kaliv.dk/proofs.html?lang=en'); document.querySelector('link[rel="canonical"]').href = url.href; setMeta('meta[property="og:url"]',url.href);
  const structured = document.querySelector('script[type="application/ld+json"]'); if (structured) { try { const data = JSON.parse(structured.textContent); data.name = 'Kaliv — V1 proof ledger'; data.description = 'An honest boundary between what Kaliv and ModelRig can prove now and what remains before V1.'; data.inLanguage = 'en'; data.url = url.href; structured.textContent = JSON.stringify(data); } catch {} }
})();

if ('serviceWorker' in navigator && location.protocol === 'https:') window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js',{scope:'./',updateViaCache:'none'}).catch(()=>{}),{once:true});
