if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js', { scope: '/', updateViaCache: 'none' }).catch(() => {});
  }, { once: true });
}
if (document.documentElement.dataset.page === 'offline') {
  window.addEventListener('online', () => window.location.reload(), { once: true });
}
// Old cached documents predate the static page marker used by the shared CSS.
if (!document.documentElement.dataset.page)
  document.documentElement.dataset.page = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '');
const kalivPage = document.documentElement.dataset.page;
document.documentElement.classList.add('page-' + kalivPage);
if (['brief', 'hub', 'architecture', 'proofs', 'progress', 'download'].includes(kalivPage))
  document.documentElement.classList.add('site-document', ['brief', 'hub', 'download'].includes(kalivPage) ? 'layout-dossier' : 'layout-system');
