if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js', { scope: '/', updateViaCache: 'none' }).catch(() => {});
  }, { once: true });
}
if (document.documentElement.dataset.page === 'offline') {
  const retry = document.getElementById('retry-connection');
  let checking = false, leaving = false;
  window.addEventListener('beforeunload', () => { leaving = true; });
  window.addEventListener('pageshow', () => { leaving = false; });
  const reconnect = async () => {
    if (checking || leaving) return;
    checking = true;
    if (retry) retry.disabled = true;
    try {
      // HEAD bypasses the GET-only service worker cache and checks the network.
      const response = await fetch('/project.json', { method: 'HEAD', cache: 'no-store' });
      if (response.ok && !leaving) window.location.reload();
    } catch {
      // Stay on the usable offline page when an online signal is premature.
    } finally {
      checking = false;
      if (retry) retry.disabled = false;
    }
  };
  retry?.addEventListener('click', reconnect);
  window.addEventListener('online', reconnect);
}
// Old cached documents predate the static page marker used by the shared CSS.
if (!document.documentElement.dataset.page)
  document.documentElement.dataset.page = (location.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '');
const kalivPage = document.documentElement.dataset.page;
document.documentElement.classList.add('page-' + kalivPage);
if (['brief', 'hub', 'architecture', 'proofs', 'progress'].includes(kalivPage))
  document.documentElement.classList.add('site-document', ['brief', 'hub'].includes(kalivPage) ? 'layout-dossier' : 'layout-system');
