/* Contact et lecture — STP Terrassement
 *
 * 1. Ordinateur : le bouton WhatsApp flottant devient un bouton « Contact » qui ouvre un petit
 *    menu (devis en ligne, WhatsApp, telephone, prix). Sans JavaScript, il reste un lien WhatsApp.
 * 2. Mobile : un troisieme bouton « Devis » dans la barre du bas.
 * 3. Mobile : un rappel discret (une carte en bas d'ecran, jamais un plein ecran : Google
 *    sanctionne les interstitiels sur mobile) quand le lecteur a lu la page puis remonte vite,
 *    signe qu'il s'apprete a partir. Une fois par session.
 * 4. Pages longues : barre de progression de lecture.
 */
(function () {
  'use strict';

  var TEL = 'tel:+33745142049';
  var WA = 'https://wa.me/33745142049';
  var QUOTE = '/devis-gratuit.html';
  var NO_PROMPT = /(devis-gratuit|contact|mentions-legales|politique-confidentialite)\.html$/;
  var track = function (name) { if (window.stpTrack) window.stpTrack(name); };

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html) e.innerHTML = html;
    return e;
  }

  // le formulaire de la page, s'il y en a un : on y conduit plutot que de changer de page
  function pageForm() {
    return document.querySelector('#devis form, form.lead-form');
  }

  function goToForm(e) {
    var f = pageForm();
    if (!f) return;                      // pas de formulaire ici : le lien mene a la page devis
    e.preventDefault();
    f.scrollIntoView({ behavior: 'smooth', block: 'center' });
    var input = f.querySelector('input[type="tel"], input:not([type="hidden"])');
    if (input) setTimeout(function () { input.focus({ preventScroll: true }); }, 500);
  }

  /* ---------- 1. menu de contact (ordinateur et tablette) ---------- */
  function dock() {
    var wrap = document.querySelector('.float-wa-wrap');
    var fab = wrap && wrap.querySelector('.float-wa');
    if (!fab) return;

    var panel = el('div', 'dock-panel');
    panel.id = 'dock-panel';
    panel.hidden = true;
    panel.innerHTML =
      '<p class="dock-title">Une question, un devis&nbsp;?</p>' +
      '<p class="dock-sub">Réponse sous 24&nbsp;h, devis gratuit.</p>' +
      '<a class="dock-item dock-item--main" data-dock="devis" href="' + QUOTE + '"><i class="fa-solid fa-calculator" aria-hidden="true"></i><span><strong>Demander un devis</strong><small>Formulaire en 1 minute</small></span></a>' +
      '<a class="dock-item" data-dock="whatsapp" href="' + WA + '" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i><span><strong>WhatsApp</strong><small>Envoyez une photo du terrain</small></span></a>' +
      '<a class="dock-item" data-dock="tel" href="' + TEL + '"><i class="fa-solid fa-phone" aria-hidden="true"></i><span><strong>07&nbsp;45&nbsp;14&nbsp;20&nbsp;49</strong><small>Lundi au samedi</small></span></a>' +
      '<a class="dock-item" data-dock="prix" href="/tarifs-terrassement-2026.html"><i class="fa-solid fa-arrow-right" aria-hidden="true"></i><span><strong>Voir les prix 2027</strong><small>83 tarifs vérifiés</small></span></a>';
    wrap.insertBefore(panel, fab);
    wrap.classList.add('dock');

    fab.setAttribute('role', 'button');
    fab.setAttribute('aria-expanded', 'false');
    fab.setAttribute('aria-controls', 'dock-panel');
    fab.setAttribute('aria-label', 'Ouvrir le menu de contact');
    fab.insertAdjacentHTML('beforeend', '<span class="dock-label" aria-hidden="true">Contact</span>');

    function set(open) {
      panel.hidden = !open;
      wrap.classList.toggle('dock--open', open);
      fab.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) track('dock_open');
    }

    fab.addEventListener('click', function (e) {
      if (window.innerWidth < 768) return;          // mobile : la barre du bas fait ce travail
      e.preventDefault();
      set(panel.hidden);
    });
    panel.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      track('dock_' + a.getAttribute('data-dock'));
      if (a.getAttribute('data-dock') === 'devis') goToForm(e);
      set(false);
    });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { set(false); fab.focus(); } });
  }

  /* ---------- 2. bouton « Devis » dans la barre mobile ---------- */
  function callbar() {
    var bar = document.querySelector('.callbar');
    if (!bar || bar.querySelector('.callbar__btn--quote')) return;
    var a = el('a', 'callbar__btn callbar__btn--quote', '<i class="fa-solid fa-calculator" aria-hidden="true"></i> Devis');
    a.href = QUOTE;
    a.addEventListener('click', function (e) { track('callbar_devis'); goToForm(e); });
    var wa = bar.querySelector('.callbar__btn--wa');
    bar.insertBefore(a, wa || null);
  }

  /* ---------- 3. rappel discret sur mobile ---------- */
  function saveSheet() {
    var KEY = 'stp-sheet-shown';
    if (window.innerWidth >= 1024 || NO_PROMPT.test(location.pathname)) return;
    try { if (sessionStorage.getItem(KEY)) return; } catch (e) { /* mode prive */ }

    var start = Date.now(), maxDepth = 0, lastY = window.scrollY, upRun = 0, shown = false, ticking = false;

    function show() {
      if (shown) return;
      shown = true;
      try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
      var canShare = !!navigator.share;
      var s = el('div', 'save-sheet');
      s.setAttribute('role', 'region');
      s.setAttribute('aria-label', 'Garder cette page');
      s.innerHTML =
        '<button type="button" class="save-sheet__close" aria-label="Fermer">&times;</button>' +
        '<p class="save-sheet__title">Gardez cette page sous la main</p>' +
        '<div class="save-sheet__actions">' +
          '<button type="button" class="save-sheet__btn" data-act="share"><i class="fa-solid fa-arrow-right" aria-hidden="true"></i> ' + (canShare ? 'Enregistrer ou partager' : 'Copier le lien') + '</button>' +
          '<a class="save-sheet__btn save-sheet__btn--main" href="' + QUOTE + '"><i class="fa-solid fa-calculator" aria-hidden="true"></i> Devis gratuit</a>' +
        '</div>' +
        '<p class="save-sheet__follow">Nos chantiers&nbsp;: ' +
          '<a href="https://www.instagram.com/stp.terrassement/" target="_blank" rel="noopener noreferrer">Instagram</a> · ' +
          '<a href="https://www.facebook.com/STPTerrassement" target="_blank" rel="noopener noreferrer">Facebook</a> · ' +
          '<a href="https://www.youtube.com/@STPTerrassement" target="_blank" rel="noopener noreferrer">YouTube</a></p>';
      document.body.appendChild(s);
      requestAnimationFrame(function () { s.classList.add('save-sheet--in'); });
      track('save_sheet_shown');

      s.addEventListener('click', function (e) {
        if (e.target.closest('.save-sheet__close')) { s.remove(); return; }
        var b = e.target.closest('[data-act="share"]');
        if (b) {
          track('save_sheet_share');
          if (canShare) {
            navigator.share({ title: document.title, url: location.href }).catch(function () {});
          } else if (navigator.clipboard) {
            navigator.clipboard.writeText(location.href).then(function () { b.textContent = 'Lien copié'; });
          }
          return;
        }
        var a = e.target.closest('a.save-sheet__btn--main');
        if (a) { track('save_sheet_devis'); goToForm(e); s.remove(); }
      });
    }

    window.addEventListener('scroll', function () {
      if (shown || ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        var y = window.scrollY;
        var h = document.documentElement.scrollHeight - window.innerHeight;
        if (h > 0) maxDepth = Math.max(maxDepth, y / h);
        upRun = y < lastY ? upRun + (lastY - y) : 0;
        lastY = y;
        // a lu au moins 45 % de la page pendant 25 s, puis remonte de plus de 600 px d'un trait
        if (maxDepth > 0.45 && Date.now() - start > 25000 && upRun > 600) show();
      });
    }, { passive: true });
  }

  /* ---------- 4. progression de lecture ---------- */
  function progress() {
    var art = document.querySelector('.article-content');
    if (!art || art.offsetHeight < window.innerHeight * 2) return;
    var bar = el('div', 'read-progress');
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var ticking = false;
    function update() {
      ticking = false;
      var r = art.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var done = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      bar.style.transform = 'scaleX(' + done + ')';
    }
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  function init() { dock(); callbar(); saveSheet(); progress(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
