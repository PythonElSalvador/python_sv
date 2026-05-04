var translations = {
  en: {
    cal_label: 'Events',
    cal_title: 'Calendar',
    cal_subtitle: 'Upcoming meetups and events from the Python SV community.',
    cal_back: 'Back to home'
  }
};
document.addEventListener('DOMContentLoaded', function() {
  var saved = localStorage.getItem('pysv-lang');
  if (saved === 'en') {
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
      var key = el.getAttribute('data-i18n');
      if (translations.en[key]) el.innerHTML = translations.en[key];
    });
  }
});
