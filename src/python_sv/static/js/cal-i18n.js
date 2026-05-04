(function() {
  var en = {
    cal_label: 'Events',
    cal_title: 'Calendar',
    cal_subtitle: 'Upcoming meetups and events from the Python SV community.',
    cal_back: 'Back to home',
    footer_coc: 'Code of Conduct',
    nav_coc: 'Code of Conduct'
  };

  var esCache = {};
  var currentLang = 'es';
  var btn = document.getElementById('langToggle');

  function applyEN() {
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
      var key = el.getAttribute('data-i18n');
      if (!esCache[key]) esCache[key] = el.innerHTML;
      if (en[key]) el.innerHTML = en[key];
    });
  }

  function applyES() {
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
      var key = el.getAttribute('data-i18n');
      if (esCache[key]) el.innerHTML = esCache[key];
    });
  }

  var saved = localStorage.getItem('pysv-lang');
  if (saved === 'en') {
    applyEN();
    currentLang = 'en';
    btn.textContent = 'ES';
    document.documentElement.lang = 'en';
  }

  btn.addEventListener('click', function() {
    if (currentLang === 'es') {
      applyEN();
      currentLang = 'en';
      btn.textContent = 'ES';
      document.documentElement.lang = 'en';
      localStorage.setItem('pysv-lang', 'en');
    } else {
      applyES();
      currentLang = 'es';
      btn.textContent = 'EN';
      document.documentElement.lang = 'es';
      localStorage.setItem('pysv-lang', 'es');
    }
  });
})();
