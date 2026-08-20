/* ==========================================================
   Nolus Consulting — interactions
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

  /* ---- Contact form (mailto handoff — no backend) ---- */
  const contactForm = document.getElementById('contactForm');
  const formSuccess = document.getElementById('formSuccess');
  if (contactForm && formSuccess) {
    contactForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!contactForm.checkValidity()) {
        contactForm.reportValidity();
        return;
      }
      const data = new FormData(contactForm);
      const topicLabel = contactForm.querySelector('#topic').selectedOptions[0]?.textContent || '';
      const lines = [
        `Name: ${data.get('firstName')} ${data.get('lastName')}`,
        data.get('company') ? `Company: ${data.get('company')}` : null,
        data.get('phone') ? `Phone: ${data.get('phone')}` : null,
        `Email: ${data.get('email')}`,
        `Topic: ${topicLabel}`,
        '',
        data.get('message')
      ].filter(Boolean).join('\n');
      const subject = `Nolus Consulting enquiry — ${data.get('firstName')} ${data.get('lastName')}`;
      window.location.href = `mailto:info@nolus.net?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines)}`;
      formSuccess.textContent = 'Opening your email client to send this to info@nolus.net — please hit send there to complete your request.';
      formSuccess.classList.add('is-visible');
      formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  }

  /* ---- Cookie banner ---- */
  const cookieBanner = document.getElementById('cookieBanner');
  const cookieAccept = document.getElementById('cookieAccept');
  if (cookieBanner && cookieAccept) {
    if (!localStorage.getItem('nolus_cookie_consent')) {
      cookieBanner.classList.add('is-visible');
    }
    cookieAccept.addEventListener('click', () => {
      localStorage.setItem('nolus_cookie_consent', '1');
      cookieBanner.classList.remove('is-visible');
    });
  }

  /* ---- Scroll reveal ---- */
  const revealTargets = document.querySelectorAll(
    '.feature-card, .step, .country-chip, .problem-list li'
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
