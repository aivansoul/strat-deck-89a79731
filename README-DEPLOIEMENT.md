# Déploiement — alexia.spitup.be (site AlexIA · SpitUP)

Site 100 % statique : aucun build, aucune base de données. Uploadez les fichiers, c'est en ligne.

## Contenu du paquet
- `telesecretariat-ia.html` — page principale (pilier). **À servir comme index du domaine.**
- `telesecretariat-medical.html` — page SEO médicale
- `demo-{medical,avocats,immobilier,construction,horeca,automobile}.html` — 6 démos métier interactives
- `telesecretariat-medical-guide-2026.html`, `ia-ou-secretaire-humaine.html` — articles
- `404.html` — page d'erreur (autonome)
- `styles.css`, `anim.js` — feuille de style et animations partagées
- `assets/` — images, vidéos, logos + `assets/vo/*.mp3` (voix des démos, déjà câblées)
- `sitemap.xml`, `robots.txt`, `llms.txt`

## Checklist de mise en ligne
1. **DNS** : créer le sous-domaine `alexia.spitup.be` → votre hébergement.
   Toutes les URLs canoniques, le sitemap et les schemas pointent déjà dessus.
2. **Index** : renommer `telesecretariat-ia.html` en `index.html`
   (ou règle de réécriture `/` → `/telesecretariat-ia.html`).
   Si renommage : remplacer les liens internes `telesecretariat-ia.html` par `./`
   (`grep -rl "telesecretariat-ia.html" *.html`).
3. **HTTPS** obligatoire (Let's Encrypt).
4. **Page 404** :
   - Apache : `ErrorDocument 404 /404.html`
   - nginx : `error_page 404 /404.html;`
   - Netlify/Vercel : automatique (fichier `404.html` à la racine).
5. **Après mise en ligne** : Google Search Console → vérifier la propriété,
   soumettre `sitemap.xml`.
6. **Cache** : à chaque modification de `styles.css`/`anim.js`, incrémenter le
   paramètre `?v=` dans les balises `<link>`/`<script>` de toutes les pages.

## Notes
- Les démos audio se lancent au clic sur le micro de chaque page métier ;
  les bulles du chat sont synchronisées sur l'audio (`assets/vo/<metier>.mp3`).
- `llms.txt` et les schemas JSON-LD font partie de la stratégie SEO/GEO : ne pas les retirer.
- Formulaire devis : les CTA pointent vers https://spitup.be/contactez-spitup/ (existant).

Contact agence : Banana Navy · Svetlana
