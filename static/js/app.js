/* Saúde Pessoal — Bootstrap */

// Apply saved theme on initial load (before Alpine)
(function () {
  const saved = localStorage.getItem('sp-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
})();

// Default datetime-local inputs to "now" if empty
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
    if (!input.value) {
      const now = new Date();
      now.setSeconds(0, 0);
      // toISOString gives UTC; adjust to local
      const offset = now.getTimezoneOffset() * 60000;
      input.value = new Date(now - offset).toISOString().slice(0, 16);
    }
  });
});

// Chart.js global defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = getComputedStyle(document.documentElement)
    .getPropertyValue('--font-body').trim() || 'system-ui';
  Chart.defaults.color = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-text-muted').trim() || '#94A3B8';

  // Re-apply defaults when theme changes
  const observer = new MutationObserver(() => {
    const muted = getComputedStyle(document.documentElement)
      .getPropertyValue('--color-text-muted').trim();
    Chart.defaults.color = muted;
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
}
