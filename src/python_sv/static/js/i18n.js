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
    hero_date: 'Saturday May 9, 2PM–4PM — UEES, San Salvador',
    talk_1_title: 'Image Processing with OpenCV',
    talk_1_desc: 'Learn to detect edges, filter colors, and track objects in real time using Python and OpenCV — with a live demo.',
    hero_meetup: 'Join the community',

    // Homepage context
    ctx_label: 'Context',
    ctx_title: 'Why now',
    ctx_1_title: 'The communities disappeared',
    ctx_1_body: 'Most Python communities in Latin America died during COVID and never recovered. In El Salvador there\'s no active community dedicated to Python — the last activity was in 2019.',
    ctx_2_title: 'But they can come back',
    ctx_2_body: 'In the Dominican Republic we helped organize <a href="https://pyday.do" target="_blank" rel="noopener">PyDay DO</a> — students, professors, professionals, and companies in a single event. The same is happening in Colombia, Mexico, and other countries. Communities are coming back.',
    ctx_3_title: 'El Salvador is next',
    ctx_3_body: 'We\'re putting together meetups — San Salvador, San Miguel, or wherever there are people. If you use Python, you\'re learning, or you\'re just curious, this is for you.',

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

    // Code of Conduct
    coc_label: 'Community',
    coc_title: 'Code of Conduct',
    coc_note: '(This code of conduct is adapted from the <a href="https://www.python.org/psf/conduct/" target="_blank" rel="noopener">Python Software Foundation</a> code of conduct.)',
    coc_updated: 'Last updated: March 2026',
    coc_toc_title: 'On this page',
    coc_toc_1: 'Our community',
    coc_toc_2: 'Our standards',
    coc_toc_3: 'Scope',
    coc_toc_4: 'Inappropriate behavior',
    coc_toc_5: 'Consequences',
    coc_toc_6: 'Resolution process',
    coc_toc_7: 'Contact',
    coc_intro: 'The Python SV community is made up of members with diverse skills, personalities, and experiences. Through these differences our community experiences great successes and continuous growth. This Code of Conduct aims to maintain a positive environment in the community and promote its growth and success.',
    coc_community_title: '\n          <a href="#comunidad" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Our community\n        ',
    coc_community_intro: 'Members of the Python SV community are considerate, respectful, and well-intentioned. Behaviors that reinforce these values and contribute to a positive environment include:',
    coc_val_1: '<strong>Being willing to collaborate.</strong> Community members are fully open to collaboration.',
    coc_val_2: '<strong>Acknowledging time and effort.</strong> We are respectful of the efforts of our volunteers, keeping in mind that often the work was done simply for the good of the community.',
    coc_val_3: '<strong>Respecting different viewpoints and experiences.</strong> We are receptive to constructive criticism and feedback, as the experiences and skills of other members contribute to our community.',
    coc_val_4: '<strong>Showing empathy towards other community members.</strong> Our communication, whether in person or online, is empathetic. When addressing different viewpoints, we do so with care.',
    coc_val_5: '<strong>Being considerate.</strong> Community members are considerate of their peers.',
    coc_val_6: '<strong>Being respectful.</strong> We are respectful of others, their work, their skills, their commitments, and their efforts.',
    coc_val_7: '<strong>Accepting constructive criticism gracefully.</strong> When we disagree, we are courteous in raising our differences.',
    coc_val_8: '<strong>Using welcoming and inclusive language.</strong> We welcome all who wish to participate in our activities, fostering an environment where everyone can participate and make a difference.',
    coc_standards_title: '\n          <a href="#normas" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Our standards\n        ',
    coc_standards_body: 'All community members have the right to have their identity respected. Our community seeks to generate positive experiences for everyone, regardless of age, gender identity and expression, sexual orientation, disability, physical appearance, body size, ethnicity, nationality, race or religion, education or socioeconomic status, and political ideology.',
    coc_scope_title: '\n          <a href="#alcance" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Scope\n        ',
    coc_scope_body: 'This code of conduct applies in all Python SV community spaces, both virtual and in-person. This includes the WhatsApp group, GitHub repositories, meetups, workshops, talks, and any other event organized by the community. It also applies in one-on-one communications related to community matters.',
    coc_inappropriate_title: '\n          <a href="#inapropiado" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Inappropriate behavior\n        ',
    coc_inappropriate_intro: 'Examples of unacceptable behavior by participants include:',
    coc_bad_1: 'Harassment of any participant in any form',
    coc_bad_2: 'Deliberate intimidation, stalking, or following',
    coc_bad_3: 'Violent threats or language directed against another person',
    coc_bad_4: 'Sexual language and imagery in any community space, whether online or in person',
    coc_bad_5: 'Insults, put-downs, or jokes based on stereotypes that are exclusionary or that ridicule others',
    coc_bad_6: 'Posting other people\'s private information, such as a physical or electronic address, without explicit permission',
    coc_bad_7: 'Unwanted physical contact',
    coc_bad_8: 'Unwelcome sexual attention or advances',
    coc_bad_9: 'Sustained disruption of talks, workshops, or other events',
    coc_bad_10: 'Other conduct that would be considered inappropriate in a professional context',
    coc_inappropriate_note: 'Community members asked to stop any inappropriate behavior are expected to comply immediately.',
    coc_consequences_title: '\n          <a href="#consecuencias" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Consequences\n        ',
    coc_consequences_body: 'If a participant engages in behavior that violates this code of conduct, Python SV organizers will take whatever action they deem appropriate, including warning the offender or expulsion from the community and its events.',
    coc_process_title: '\n          <a href="#proceso" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Resolution process\n        ',
    coc_process_intro: 'Upon receiving a report of a violation, the organizers will follow these steps:',
    coc_step_1: 'The report is received and evaluated.',
    coc_step_2: 'Conflicts of interest within the organizing team are verified.',
    coc_step_3: 'Both parties are contacted to understand their perspective.',
    coc_step_4: 'The situation is analyzed and appropriate consequences are determined.',
    coc_step_5: 'The outcome is communicated to both parties separately.',
    coc_step_6: 'The situation is followed up on for a determined period after resolution.',
    coc_contact_title: '\n          <a href="#contacto" class="pysv-coc-anchor" aria-hidden="true">#</a>\n          Contact\n        ',
    coc_contact_body: 'If you witness or are the victim of a violation of this code of conduct, or have any questions or comments, you can write to us at:',
    coc_contact_note: 'Email interactions will remain confidential between the person writing and the organizers.',
    coc_back: 'Back to home',

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
