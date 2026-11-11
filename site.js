if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js', { scope: '/', updateViaCache: 'none' }).catch(() => {});
  }, { once: true });
}
if (document.documentElement.dataset.page === 'offline') {
  window.addEventListener('online', () => window.location.reload(), { once: true });
}
