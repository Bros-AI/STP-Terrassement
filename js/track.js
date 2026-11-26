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
  /* Origine de la visite (spec ERP SEO-09) : la premiere page vue, le site d'ou l'on vient
     (son nom d'hote seulement, jamais l'adresse complete ni ce qui a ete cherche) et les
     parametres utm. Garde dans l'onglet (sessionStorage) : aucun cookie, aucun identifiant,
     rien n'est envoye sans qu'un formulaire le soit. Ajoute en champs caches aux
     formulaires de devis, pour savoir quelles pages amenent des demandes. */
  var UTM = ['utm_source', 'utm_medium', 'utm_campaign'];
  function origin() {
    try {
      var s = window.sessionStorage;
      if (!s.getItem('stp_landing')) {
        var host = '';
        try { host = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) { host = ''; }
        if (host === location.hostname) host = '';
        s.setItem('stp_landing', location.pathname);
        s.setItem('stp_ref', host);
        var q = new URLSearchParams(location.search);
        UTM.forEach(function (k) { var v = q.get(k); if (v) s.setItem('stp_' + k, v.slice(0, 80)); });
      }
      /* « - » : visite directe. Le champ existe ainsi toujours, vide ou non. */
      var o = { landing: s.getItem('stp_landing') || location.pathname, ref: s.getItem('stp_ref') || '-' };
      UTM.forEach(function (k) { var v = s.getItem('stp_' + k); if (v) o[k] = v; });
      return o;
    } catch (e) { return null; } /* navigation privee stricte : pas de stockage, pas de champ */
  }
  function tagForms() {
    var o = origin();
    if (!o) return;
    document.querySelectorAll('form').forEach(function (f) {
      if (!f.querySelector('input[name="access_key"]')) return;
      Object.keys(o).forEach(function (k) {
        if (f.querySelector('input[name="' + k + '"]')) return;
        var i = document.createElement('input');
        i.type = 'hidden'; i.name = k; i.value = o[k];
        f.appendChild(i);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tagForms);
  else tagForms();
  /* Le formulaire emet stp:lead APRES la reponse OK de Web3Forms (voir js/script.js) : une seule conversion par envoi. */
  document.addEventListener('stp:lead', function (e) {
    var d = (e && e.detail) || {};
    send('devis_envoye', { service: d.service || 'non_precise', page: location.pathname });
  });
})();
