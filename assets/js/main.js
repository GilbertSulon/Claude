/* ==========================================================
   EZ receptionist — interactions
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---- Mobile nav toggle ---- */
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---- FAQ accordion ---- */
  document.querySelectorAll('.faq-item').forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    question.addEventListener('click', () => {
      const isOpen = item.classList.contains('is-open');
      document.querySelectorAll('.faq-item.is-open').forEach(openItem => {
        if (openItem !== item) {
          openItem.classList.remove('is-open');
          openItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
        }
      });
      item.classList.toggle('is-open', !isOpen);
      question.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  /* ---- Contact form (front-end only) ---- */
  const contactForm = document.getElementById('contactForm');
  const formSuccess = document.getElementById('formSuccess');
  if (contactForm && formSuccess) {
    contactForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!contactForm.checkValidity()) {
        contactForm.reportValidity();
        return;
      }
      // No backend wired up yet — replace with a real submission
      // (e.g. POST to your API, Netlify Forms, Formspree...).
      formSuccess.classList.add('is-visible');
      contactForm.reset();
      formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  }

  /* ---- Cookie banner ---- */
  const cookieBanner = document.getElementById('cookieBanner');
  const cookieAccept = document.getElementById('cookieAccept');
  if (cookieBanner && cookieAccept) {
    if (!localStorage.getItem('ezreceptionist_cookie_consent')) {
      cookieBanner.classList.add('is-visible');
    }
    cookieAccept.addEventListener('click', () => {
      localStorage.setItem('ezreceptionist_cookie_consent', '1');
      cookieBanner.classList.remove('is-visible');
    });
  }

  /* ---- Scroll reveal ---- */
  const revealTargets = document.querySelectorAll(
    '.feature-card, .step, .price-card, .sector-card, .problem-list li'
  );
  revealTargets.forEach(el => el.setAttribute('data-reveal', ''));

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    revealTargets.forEach(el => observer.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('is-visible'));
  }

  /* ---- Sticky header shadow on scroll ---- */
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
    document.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
});
