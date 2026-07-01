(function() {
  var en = {
    // Layout (nav + footer)
    nav_cal: 'Calendar',
    nav_proposals: 'Proposals',
    nav_coc: 'Code of Conduct',
    footer: 'Python SV &copy; ' + new Date().getFullYear() + ' — Made with Python and FastAPI in El Salvador.',
    footer_cal: 'Calendar',
    footer_proposals: 'Proposals',
    footer_coc: 'Code of Conduct',

    // Homepage hero
    hero_title: 'We\'re building the <strong>Python</strong> community in El Salvador',
    hero_date: 'Saturday July 18, 2PM–5PM — UEES, San Salvador',
    talk_1_title: 'Introduction to FastAPI',
    talk_1_desc: 'Build your first modern API with FastAPI: routes, Pydantic validation, automatic documentation, and basic deployment — all in one session.',
    talk_1_tag: '2:00 PM · Talk + Demo',

    // Homepage upcoming events
    upcoming_label: 'Upcoming',
    upcoming_title: 'Upcoming events',
    talk_2_date: 'Saturday August 22, 2PM–5PM — UEES, San Salvador',
    talk_2_title: 'Data Processing with Pandas',
    talk_2_desc: 'Learn to clean, transform, and analyze real data with Pandas: DataFrames, groupby, merges, and quick visualization — with a live demo.',
    talk_3_date: 'Saturday September 19, 2PM–5PM — UEES, San Salvador',
    talk_3_title: 'Web Scraping in Python: A Toolkit for Data Extraction',
    talk_3_desc: 'Master the main Python web scraping tools: requests, BeautifulSoup, Scrapy, and Playwright — with hands-on examples for extracting data from real sites.',

    // Homepage context
    ctx_label: 'Context',
    ctx_title: 'Why now',
    ctx_1_title: 'The communities disappeared',
    ctx_1_body: 'Most Python communities in Latin America died during COVID and never recovered. In El Salvador there was no active Python community since 2019.',
    ctx_2_title: 'We brought it back',
    ctx_2_body: 'In March 2026 we launched the first Python SV meetup with 30+ attendees in San Salvador. Now we\'re part of the network of Python communities in Latin America alongside Colombia, Mexico, and the Dominican Republic.',
    ctx_3_title: 'And we\'re just getting started',
    ctx_3_body: 'Talks, workshops, live demos — every month. If you use Python, you\'re learning, or you\'re just curious, this is for you.',

    // Homepage signup
    signup_label: 'Community',
    signup_title: 'Join Python SV',
    signup_subtitle: 'Get updates and access the community WhatsApp group.',
    form_type_placeholder: 'Member type',
    form_type_student: 'Student',
    form_type_pro: 'Professional',
    form_type_other: 'Other',
    form_role_placeholder: 'How do you want to participate?',
    form_role_attend: 'Attend events',
    form_role_speak: 'Give talks',
    form_role_organize: 'Help organize',
    form_submit: 'Join',
    form_done: 'you\'re on the list.',
    form_whatsapp: 'Join the group',
    form_exists_msg: 'That email is already on the list.',

    // Calendar
    cal_label: 'Events',
    cal_title: 'Calendar',
    cal_subtitle: 'Upcoming meetups and events from the Python SV community.',
    cal_back: 'Back to home',

    // Error page
    error_back: 'Back to home'
  };

  var esCache = {};
  var currentLang = 'es';
  var btn = document.getElementById('langToggle');
  if (!btn) return;

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
