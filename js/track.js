/* Suivi des micro-conversions (spec SEO-01) — agnostique de l'outil de mesure.
   Aucune donnee ne part tant qu'aucun outil (Plausible ou GA4) n'est charge sur la page. */
(function () {
  'use strict';
  function send(name, props) {
    if (window.plausible) window.plausible(name, { props: props });
    if (window.gtag) window.gtag('event', name, props);
  }
  function zone(el) {
    if (el.closest('.callbar')) return 'barre_mobile';
    if (el.closest('.float-wa')) return 'bouton_flottant';
    if (el.closest('nav, header.navbar')) return 'entete';
    if (el.closest('footer')) return 'pied_de_page';
    if (el.closest('.hero, #accueil')) return 'hero';
    return 'contenu';
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var props = { zone: zone(a), page: location.pathname };
    if (href.indexOf('tel:') === 0) send('appel_telephone', props);
    else if (/wa\.me|api\.whatsapp\.com/.test(href)) send('clic_whatsapp', props);
    else if (href.indexOf('mailto:') === 0) send('clic_email', props);
  }, { passive: true });
  /* Le formulaire emet stp:lead APRES la reponse OK de Web3Forms (voir js/script.js) : une seule conversion par envoi. */
  document.addEventListener('stp:lead', function (e) {
    var d = (e && e.detail) || {};
    send('devis_envoye', { service: d.service || 'non_precise', page: location.pathname });
  });
})();
