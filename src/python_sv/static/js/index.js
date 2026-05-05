(function() {
  var reveals = document.querySelectorAll('.reveal');

  if (!('IntersectionObserver' in window)) {
    reveals.forEach(function(el) { el.classList.add('visible'); });
    return;
  }

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0 });

  reveals.forEach(function(el) { observer.observe(el); });

  // Fallback: reveal anything near viewport after 500ms
  setTimeout(function() {
    reveals.forEach(function(el) {
      if (!el.classList.contains('visible')) {
        var rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight + 100) {
          el.classList.add('visible');
          observer.unobserve(el);
        }
      }
    });
  }, 500);

  // Lazy-load section background images
  var bgObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.style.backgroundImage = 'url(' + entry.target.dataset.bg + ')';
        bgObserver.unobserve(entry.target);
      }
    });
  }, { rootMargin: '600px' });

  document.querySelectorAll('[data-bg]').forEach(function(el) {
    bgObserver.observe(el);
  });

  // Hide signup form after successful submission
  var signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('htmx:afterRequest', function(evt) {
      if (evt.detail.successful) signupForm.style.display = 'none';
    });
  }
})();
