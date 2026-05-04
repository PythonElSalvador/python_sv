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

  // Bilingual toggle (ES/EN)
  var en = {
    nav_contexto: 'Context',
    hero_title: 'We\'re building the <strong>Python</strong> community in El Salvador',
    hero_schedule: 'See full schedule',
    hero_date: 'Saturday, March 14th, 2PM\u20135PM \u2014 Millenium Plaza, Alveare, San Salvador',
    hero_meetup: 'Register on Meetup',
    talk_1_title: 'Data Processing with Pandas vs Polars',
    talk_2_title: 'Introduction to Forecasting with Python',
    talk_3_title: 'Code Optimization with AI',
    schedule_label: 'Full schedule',
    schedule_title: 'Agenda',
    schedule_meetup: 'Register on Meetup',
    sched_1: 'Doors open \u00b7 arrival and chat',
    sched_2: 'Welcome and organizer announcements',
    sched_3: 'Talk 1 \u00b7 Nelson Zepeda',
    sched_4: 'Break',
    sched_5: 'Talk 2 \u00b7 Daniel Zaldaña',
    sched_6: 'Talk 3 \u00b7 Kevin Turcios',
    sched_7: 'Open networking / closing',
    ctx_label: 'Context',
    ctx_title: 'Why now',
    ctx_1_title: 'The communities disappeared',
    ctx_1_body: 'Most Python communities in Latin America died during COVID and never recovered. In El Salvador there\'s no active community dedicated to Python — the last activity was in 2019.',
    ctx_2_title: 'But they can come back',
    ctx_2_body: 'In the Dominican Republic we helped organize <a href="https://pyday.do" target="_blank" rel="noopener">PyDay DO</a>\u2009—\u2009students, professors, professionals, and companies in a single event. The same is happening in Colombia, Mexico, and other countries. Communities are coming back.',
    ctx_3_title: 'El Salvador is next',
    ctx_3_body: 'We\'re putting together the first meetup\u2009—\u2009San Salvador, San Miguel, or wherever there are people. If you use Python, you\'re learning, or you\'re just curious, this is for you.',
    footer: 'Python SV &copy; {{ current_year }} \u2014 Made with Python and FastAPI in El Salvador.',
    error_back: 'Back to home',
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

  btn.addEventListener('click', function() {
    if (currentLang === 'es') {
      applyEN();
      currentLang = 'en';
      btn.textContent = 'ES';
      document.documentElement.lang = 'en';
    } else {
      applyES();
      currentLang = 'es';
      btn.textContent = 'EN';
      document.documentElement.lang = 'es';
    }
  });

})();
