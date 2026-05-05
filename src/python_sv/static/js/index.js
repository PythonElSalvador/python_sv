(function() {
  // Reveal animations
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

  document.querySelectorAll('.reveal').forEach(function(el) {
    observer.observe(el);
  });

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
