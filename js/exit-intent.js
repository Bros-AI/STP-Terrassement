/* Rappel de contact a la sortie — STP Terrassement
 *
 * DESKTOP UNIQUEMENT, et c'est un choix, pas un oubli. Google sanctionne les interstitiels
 * intrusifs sur MOBILE : une fenetre qui recouvre le contenu a l'arrivee depuis la recherche
 * peut couter des positions. Sur ordinateur, declenchee au depart du curseur vers la barre
 * du navigateur, elle sort du champ de cette regle. Et sur ecran tactile l'intention de
 * sortie n'existe pas : il n'y a pas de curseur a suivre.
 *
 * Une seule apparition par session, jamais sur les pages qui convertissent deja (devis,
 * contact), et aucune sur demande du systeme si l'utilisateur a reduit les animations.
 */
(function () {
  'use strict';

  var MIN_WIDTH = 1024;          // en dessous, on considere que c'est tactile ou etroit
  var KEY = 'stp-exit-shown';
  var DELAY = 8000;              // ne rien proposer a quelqu'un qui part tout de suite
  var EXCLUDED = /(devis-gratuit|contact|mentions-legales|politique-confidentialite)\.html$/;

  if (window.innerWidth < MIN_WIDTH) return;
  if (!window.matchMedia || !window.matchMedia('(pointer: fine)').matches) return;
  if (EXCLUDED.test(location.pathname)) return;
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) { /* mode prive : on continue */ }

  var armed = false;
  var modal = null;
  var lastFocus = null;

  setTimeout(function () { armed = true; }, DELAY);

  function build() {
    var el = document.createElement('div');
    el.className = 'exit-modal';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-labelledby', 'exit-modal-title');
    el.hidden = true;
    el.innerHTML =
      '<div class="exit-modal__box">' +
        '<button type="button" class="exit-modal__close" aria-label="Fermer">&times;</button>' +
        '<h2 id="exit-modal-title">Une question sur votre projet&nbsp;?</h2>' +
        '<p>Un chiffrage se fait en quelques minutes au téléphone, et le devis est gratuit.</p>' +
        '<div class="exit-modal__actions">' +
          '<a class="btn btn-primary" href="tel:+33745142049"><i class="fa-solid fa-phone" aria-hidden="true"></i> 07&nbsp;45&nbsp;14&nbsp;20&nbsp;49</a>' +
          '<a class="btn btn-whatsapp" href="https://wa.me/33745142049" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i> WhatsApp</a>' +
        '</div>' +
        '<p class="exit-modal__alt"><a href="/devis-gratuit.html">Demander un devis en ligne</a></p>' +
        '<p class="exit-modal__follow">Suivez nos chantiers&nbsp;:' +
          '<a href="https://www.instagram.com/stp.terrassement/" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><i class="fa-brands fa-instagram" aria-hidden="true"></i></a>' +
          '<a href="https://www.facebook.com/STPTerrassement" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><i class="fa-brands fa-facebook-f" aria-hidden="true"></i></a>' +
          '<a href="https://www.youtube.com/@STPTerrassement" target="_blank" rel="noopener noreferrer" aria-label="YouTube"><i class="fa-brands fa-youtube" aria-hidden="true"></i></a>' +
          '<a href="https://www.linkedin.com/company/stpterrassement" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i class="fa-brands fa-linkedin-in" aria-hidden="true"></i></a>' +
        '</p>' +
      '</div>';
    document.body.appendChild(el);
    return el;
  }

  function close() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.removeEventListener('keydown', onKey, true);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function onKey(e) {
    if (e.key === 'Escape') { close(); return; }
    if (e.key !== 'Tab') return;
    var f = modal.querySelectorAll('a[href], button');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function open() {
    if (!armed) return;
    try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}
    armed = false;
    try { sessionStorage.setItem(KEY, '1'); } catch (e) {}

    if (!modal) {
      modal = build();
      modal.addEventListener('click', function (e) {
        if (e.target === modal || e.target.closest('.exit-modal__close')) close();
      });
    }
    lastFocus = document.activeElement;
    modal.hidden = false;
    var btn = modal.querySelector('.exit-modal__close');
    if (btn) btn.focus();
    document.addEventListener('keydown', onKey, true);
    if (window.stpTrack) window.stpTrack('exit_intent_shown');
  }

  // le curseur quitte la fenetre par le haut : il va vers les onglets ou la barre d'adresse
  document.addEventListener('mouseout', function (e) {
    if (e.relatedTarget || e.clientY > 8) return;
    open();
  });
})();
