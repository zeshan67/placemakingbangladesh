// Placemaking Bangladesh — behaviour. Every page reads fine with this file missing.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ── Menu ──
  const btn = $('.menu-btn'), nav = $('#nav');
  const setMenu = open => {
    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', open);
  };
  btn.addEventListener('click', () => setMenu(btn.getAttribute('aria-expanded') !== 'true'));
  addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) { setMenu(false); btn.focus(); } });
  matchMedia('(min-width: 901px)').addEventListener('change', () => setMenu(false));

  // ── Header: always on screen, with a rule under it once the page has moved ──
  const head = $('.site-head');
  addEventListener('scroll', () => head.classList.toggle('scrolled', scrollY > 8), { passive: true });

  // ── Videos: the player loads only when a story is pressed ──
  document.addEventListener('click', e => {
    const b = e.target.closest('.play'); if (!b) return;
    const f = document.createElement('iframe');
    f.className = 'video-frame';
    f.src = 'https://www.youtube-nocookie.com/embed/' + b.dataset.video + '?autoplay=1&rel=0&playsinline=1';
    f.title = b.getAttribute('aria-label').replace(/^Play: /, '');
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    b.replaceWith(f); f.focus();
  });

  // ── Stories rail ──
  const rail = $('[data-rail]');
  if (rail) {
    const prev = $('[data-rail-prev]'), next = $('[data-rail-next]');
    const step = () => ($('.story', rail)?.offsetWidth || 400) + 24;
    const go = d => rail.scrollBy({ left: d * step(), behavior: calm ? 'auto' : 'smooth' });
    prev.onclick = () => go(-1); next.onclick = () => go(1);
    const sync = () => {
      prev.disabled = rail.scrollLeft < 8;
      next.disabled = rail.scrollLeft + rail.clientWidth > rail.scrollWidth - 8;
    };
    rail.addEventListener('scroll', sync, { passive: true }); addEventListener('resize', sync); sync();
  }

  if (!window.gsap || calm) return;
  gsap.registerPlugin(ScrollTrigger);

  // ── "A place can be": the word changes on a timer ──
  const word = $('#place-word'), gloss = $('#place-gloss');
  if (word) {
    const places = JSON.parse($('#places').textContent);
    let i = 0, running = false;
    const turn = () => {
      gsap.timeline({ onComplete: () => running && gsap.delayedCall(1.9, turn) })
        .to(word, { yPercent: -110, duration: .45, ease: 'power3.in' })
        .to(gloss, { opacity: 0, duration: .25 }, 0)
        .add(() => { i = (i + 1) % places.length; word.textContent = places[i][0]; gloss.textContent = places[i][1]; })
        .fromTo(word, { yPercent: 110 }, { yPercent: 0, duration: .7, ease: 'expo.out' })
        .to(gloss, { opacity: 1, duration: .4 }, '<.15');
    };
    // Only while the band is on screen.
    ScrollTrigger.create({
      trigger: '.place', start: 'top 80%', end: 'bottom 10%',
      onToggle: self => { if (self.isActive && !running) { running = true; gsap.delayedCall(1.4, turn); } else if (!self.isActive) { running = false; } },
    });
    // The wheel is driven by the page: scrolling pushes it, and when the page stops it
    // coasts down to a slow idle turn instead of stopping dead, like a wheel with slack
    // in its bearings.
    const wheel = $('#wheel');
    const IDLE = 2.2;      // degrees per second when nothing is moving
    const PUSH = 0.16;     // degrees per pixel scrolled
    const DRAG = 0.045;    // how quickly it gives up speed (smaller = longer coast)
    let angle = 0, speed = 0, lastY = scrollY, onScreen = false;
    ScrollTrigger.create({ trigger: '.place', start: 'top bottom', end: 'bottom top', onToggle: self => { onScreen = self.isActive; lastY = scrollY; } });
    gsap.set(wheel, { transformOrigin: '50% 50%' });
    gsap.ticker.add((time, delta) => {
      if (!onScreen) return;
      const frames = delta / 16.67;
      const pushed = (scrollY - lastY) * PUSH; lastY = scrollY;
      speed += (pushed - speed) * Math.min(1, DRAG * frames);
      angle += speed * frames + IDLE * delta / 1000;
      gsap.set(wheel, { rotation: angle });
    });
  }

  // ── Home: the photograph drifts as the hero leaves, the poster settles into place ──
  if ($('[data-hero]')) {
    gsap.to('.hero-photo img', { yPercent: 10, scale: 1.06, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
    gsap.from('.intro-poster', { y: 70, ease: 'none',
      scrollTrigger: { trigger: '.intro', start: 'top bottom', end: 'top 45%', scrub: .5 } });
  }

  // ── Photographs move a little slower than the page ──
  $$('[data-parallax]').forEach(img => {
    gsap.fromTo(img, { yPercent: -5 }, { yPercent: 5, ease: 'none',
      scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  // ── About: the line fills in word by word as it is read ──
  $$('[data-fill]').forEach(line => {
    const wrap = node => {
      if (node.nodeType === 3) {
        const frag = document.createDocumentFragment();
        node.textContent.split(/(\s+)/).forEach(t => {
          if (!t.trim()) { frag.append(t); return; }
          const s = document.createElement('span'); s.className = 'w'; s.textContent = t; frag.append(s);
        });
        node.replaceWith(frag);
      } else [...node.childNodes].forEach(wrap);
    };
    wrap(line);
    gsap.fromTo($$('.w', line), { opacity: .22 }, { opacity: 1, stagger: .12, ease: 'none',
      scrollTrigger: { trigger: line, start: 'top 82%', end: 'bottom 48%', scrub: .4 } });
  });

  addEventListener('load', () => ScrollTrigger.refresh());
})();
