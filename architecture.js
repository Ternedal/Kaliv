(() => {
  const isEnglish = new URLSearchParams(location.search).get('lang') === 'en';
  if (!isEnglish) return;
  document.documentElement.lang = 'en';
  document.querySelectorAll('[data-en]').forEach(node => { node.textContent = node.dataset.en; });
  document.querySelectorAll('[data-en-href]').forEach(node => { node.href = node.dataset.enHref; });
  document.querySelectorAll('[data-language]').forEach(link => { const current = link.dataset.language === 'en'; link.classList.toggle('is-current',current); if (current) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current'); });
  document.querySelector('.lang')?.setAttribute('aria-label','Choose language');
  document.querySelector('.hero-map')?.setAttribute('aria-label','ModelRig layered system architecture');
  document.querySelector('.signal-band')?.setAttribute('aria-label','Four architecture properties');
  document.querySelector('.closing-aside img')?.setAttribute('alt','Kaliv’s futuristic ankh symbol');
  document.title = 'Kaliv — system architecture';
  const description = 'How Kaliv fits together: one identity and memory in ModelRig, four clients and a replaceable AI model under explicit control.';
  const setMeta = (selector,value) => { const el = document.querySelector(selector); if (el) el.content = value; };
  setMeta('meta[name="description"]',description); setMeta('meta[property="og:title"]','Kaliv — system architecture'); setMeta('meta[property="og:description"]','Kaliv is the AI you meet. ModelRig preserves identity, memory and permissions across computer, phone, home and VR.'); setMeta('meta[property="og:locale"]','en_US'); setMeta('meta[name="twitter:title"]','Kaliv — system architecture'); setMeta('meta[name="twitter:description"]','One Kaliv across four surfaces — with identity and memory outside the replaceable model.');
  const url = new URL('https://kaliv.dk/architecture.html?lang=en'); document.querySelector('link[rel="canonical"]').href = url.href; setMeta('meta[property="og:url"]',url.href);
  const structured = document.querySelector('script[type="application/ld+json"]'); if (structured) { try { const data = JSON.parse(structured.textContent); data.name = 'Kaliv — system architecture'; data.description = description; data.inLanguage = 'en'; data.url = url.href; structured.textContent = JSON.stringify(data); } catch {} }
})();

if ('serviceWorker' in navigator && location.protocol === 'https:') window.addEventListener('load', () => navigator.serviceWorker.register('./service-worker.js',{scope:'./',updateViaCache:'none'}).catch(()=>{}),{once:true});
