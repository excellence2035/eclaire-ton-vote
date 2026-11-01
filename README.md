# Vote

Plateforme d’aide au vote pour les jeunes, en Afrique : une carte des élections, puis un questionnaire par ministère qui compare les **partis politiques** (présidentielles et législatives), sujet par sujet.

- Carte des 54 pays africains : élection nationale prévue d’ici fin 2027 (vert, aplat) ou non (rouge, hachuré). Chaque pays avec un questionnaire (✓) ou une fiche (ⓘ), et chaque île, a un repère tactile d’au moins 24 px ; les repères qui se touchent (Gambie, Guinée-Bissau, Sénégal, Cap-Vert) sont écartés, reliés à leur vrai emplacement par un trait. Au clavier, le premier arrêt est le lien « Aller à la liste des pays » ; seuls les pays avec une élection ou un contenu sont dans l’ordre de tabulation (par nom), les autres restent accessibles par la liste (recherche sans accents, avec les noms usuels : Ivory Coast, Cape Verde, Swaziland, RDC…).
- Édition pilote : Nigeria 2027, 38 questions, 9 thèmes, en anglais, français, portugais, swahili et arabe.
- Prototype : présidentielle française 2027.

**Prototype.** Les positions sont codées à partir de sources publiques datées (liens dans l’onglet « Méthode et sources ») et n’ont pas encore été validées par les partis ni par un comité indépendant. Aucune réponse n’est enregistrée : tout reste dans le navigateur.

- Pays où l’on ne peut pas encore comparer les partis honnêtement : une fiche d’information (faits, règles, principaux acteurs, sources).

Écran de question pensé pour une main sur un téléphone de 360 × 640 : une ligne de progression (« 12 / 38 », barre fine, bouton « Questions » qui ouvre la liste de toutes les questions avec leur état), l’énoncé, ★ et « Contexte » sur une ligne, puis les cinq réponses, toutes visibles sans défiler. Compatibilité : le JavaScript livré ne dépasse pas ES2019 (anciens téléphones) ; sans JavaScript, la page affiche une phrase et la liste des pays disponibles, générée par le build.

Adresses (partageables) : `#/` la carte, `#/ke` un pays (choix de la langue), `#/ke/sw` son départ, `#/ke/sw/q/3` une question, `#/ke/sw/results` (ou `/results/method`…) les résultats ; formes courtes `#ke`, `#cv-pt`. Le bouton Retour passe d’un écran à l’autre (le questionnaire n’occupe qu’une entrée). Le questionnaire en cours est gardé dans l’onglet (`sessionStorage`) et la langue choisie sur l’appareil (`localStorage`, clé `etv.ui`) ; les réponses ne vont jamais dans l’adresse ni sur le réseau.

Le site est publié avec GitHub Pages : `index.html` (l’application, sans les données des pays), `data/<cc>.json` (la langue de base d’un pays, ses sources et sa carte « Prépare ton vote ») et `data/<cc>.<langue>.json` (une traduction, téléchargée seulement quand on choisit cette langue). Les adresses publiques du site et du dépôt (`SITE_URL`, `REPO_URL`) ne sont écrites qu’une fois, en haut de `tools/build.js` ; le nom du site (`BRAND`) aussi.

## Structure et construction

```
src/shell.html          titre, CSS (thèmes clair et sombre), squelette HTML
src/ui/*.js             textes de l’interface (fr, en, pt, sw, ar) ; t-multi.js : chargement, fiches d’information…
src/africa.js           calendrier électoral des 54 pays + sources ; src/mapdata.js : la carte
src/app.js              toute l’application (carte, questionnaire, calcul, résultats, bandeau du pays, valeurs, compteur)
src/values.js           les 10 énoncés du module « valeurs », communs à tous les pays (5 langues)
src/ui/t-meter.js       textes du module « valeurs » et du compteur (5 langues)
src/ui/t-v3.js          textes de « Pourquoi ce score ? », « Prépare ton vote », du partage et de « Signaler une erreur » (5 langues)
src/prep.js             « Prépare ton vote » : organisme électoral, lien d’inscription, dates et démarches sourcées, par pays (PREP)
src/editions/<cc>.js    une édition par pays (format : src/EDITION_SPEC.md)
src/i18n/<cc>.js        ses traductions (facultatif)
flags/<cc>.svg          drapeaux (55 : 54 pays africains + France), licence MIT dans flags/LICENSE
fonts/                  polices hébergées (WOFF2 : Bricolage Grotesque et Readex Pro, licence SIL OFL dans fonts/LICENSE-*.txt)
icons/, og.png          icônes du manifeste et image de partage 1200 × 630 (générées par tools/og.py)
manifest.webmanifest    généré par tools/build.js ; <cc>/index.html : une page de partage par pays, générée aussi
meter.config.json       adresse du compteur collectif ({ "endpoint": "" } = fonctions collectives éteintes)
meter/                  serveur du compteur (Cloudflare Worker + D1) : worker.js, schema.sql, wrangler.toml, README.md, test.mjs
tools/build.js          construit index.html, artifact.html, data/*.json, manifest.webmanifest et <cc>/index.html, copie flags/, fonts/, icons/ et og.png, écrit meter/countries.json
tools/flags.js          (re)génère flags/ depuis le paquet npm « flag-icons »
tools/fonts.js          (re)génère fonts/ depuis les paquets npm « @fontsource-variable/* » (Bricolage Grotesque, Readex Pro)
tools/og.py             (re)génère og.png et icons/ (Playwright ; le nom du site vient de BRAND dans tools/build.js)
tools/test.py           tests de bout en bout (Playwright)
```

**Ajouter un pays**

1. Écrire `src/editions/<cc>.js` selon `src/EDITION_SPEC.md` (`<cc>` = code ISO alpha-2 en minuscules) : `SRC_<CC>`, `META_<CC>` et soit `ED_<CC>` (questionnaire), soit `INFO_<CC>` (fiche d’information). Vérifier avec `node src/tools/validate-edition.js src/editions/<cc>.js`.
2. Facultatif : ses traductions dans `src/i18n/<cc>.js` (`I18N_<CC> = { fr: {…}, ar: {…} }`, mêmes positions que les questions).
3. `node tools/build.js` : valide chaque édition, écarte (avec un avertissement) celles qui ne passent pas et les traductions incomplètes, écrit `data/<cc>.json` (+ une traduction par langue gardée : `data/<cc>.<langue>.json`), `manifest.webmanifest`, `<cc>/index.html`, `index.html` et `artifact.html` (même page sans `<html>/<head>/<body>`, pour un hébergeur qui ajoute son propre squelette ; elle a aussi besoin du dossier `data/`, de `flags/` pour les drapeaux (sans lui, ils disparaissent et le reste marche) et de `fonts/` (sans lui, les polices du système prennent le relais) ; elle garde des adresses relatives `fonts/…` et `flags/…`). Le pays apparaît alors sur la carte avec sa coche (questionnaire) ou son repère « i » (fiche), dans les langues disponibles.
4. `python3 tools/test.py` (Python 3 + Playwright avec Chromium) : sert le dépôt en local et teste la carte, le Nigeria dans les 5 langues, la France, le thème sombre, une fiche d’information et une édition « leader » de test, l’écran hors ligne, les adresses et le bouton Retour, la reprise après rechargement, la langue de départ, le focus et les annonces, le bouton ★ « compte double », la confirmation avant d’effacer, les titres des résultats (premier aperçu, égalité, aucun parti proche, partis peu documentés), les cibles tactiles de la carte à 320, 390 et 1280 px, le clavier sur la carte, l’écran de question à 360 × 640 pour toutes les questions du Nigeria et du Kenya, l’absence de défilement horizontal à 320 px (carte, départ, question, résultats ; Nigeria, Kenya, Cameroun ; anglais et arabe), la recherche de pays, les textes, les contrastes (les deux thèmes), les couleurs des partis, le script ES2019 et le bloc `<noscript>`, puis : « Pourquoi ce score ? » (3 accords et 3 désaccords par parti, recalculés à part en Python), « Prépare ton vote » (ordre, éléments passés, compte à rebours, `.ics`, 14 pays, validation par le build), le bouton Partager (natif, copie, champ de secours, artefact), les liens « Signaler une erreur » et « Quoi de neuf », les balises d’aperçu, le manifeste, les pages `<cc>/`, les polices (aucun serveur de polices, moins de 120 Ko pour un visiteur en alphabet latin), le chargement d’une langue à la demande (échec, délai dépassé, choix périmé) et la présence des nouveaux textes dans les cinq langues. Captures d’écran : `--shots <dossier>`.

Le build vérifie aussi, et avertit (donc `--strict` échoue) quand : une ligne d’`src/africa.js` et la `META` de l’édition ne disent pas la même chose (élection prévue d’ici fin 2027, dates, prochaine échéance), une clé de source manque, ou le script livré contient une syntaxe plus récente qu’ES2019 (`??`, `?.`). En cas de désaccord, on corrige la ligne d’`africa.js`, pas l’édition. Les couleurs des partis sont ajustées à l’exécution dans chaque édition (écart ΔE ≥ 20 entre deux partis, sigle à 4,5:1, thèmes clair et sombre ; la couleur de l’édition est gardée si elle convient déjà).

Options de `tools/build.js` : `--extra <dossier>` ajoute des éditions (`<dossier>/editions`, `<dossier>/i18n`) et peut apporter `<dossier>/prep.js` (utilisé par les tests), `--out <dossier>` écrit ailleurs qu’à la racine (en y recopiant `flags/`, `fonts/`, `icons/` et `og.png`), `--endpoint <url>` remplace l’adresse de `meter.config.json` (utilisé par les tests), `--strict` échoue au moindre avertissement. La France est dispensée de validation (elle dépasse volontairement les limites du validateur).

## Pourquoi ce score ?

Sous chaque parti du classement (repliée, « Pourquoi ce score ? ») et dans sa fiche : jusqu’à **3 accords** (réponses où l’écart avec la position du parti est ≤ 1, de l’écart le plus petit au plus grand) et jusqu’à **3 désaccords** (écart ≥ 2, du plus grand au plus petit) ; à égalité, l’ordre des questions de l’édition. Seules comptent tes réponses chiffrées sur des questions où le parti a une position documentée : une question passée ou sans position n’est jamais citée. Chaque ligne montre l’énoncé, la position du parti et ta réponse, avec « Voir la question » (onglet « Par question », la question prise par le focus). Le texte « Comparé sur 21 de tes 38 réponses » est affiché à côté de chaque pourcentage (classement, onglet « Par sujet » avec les chiffres du sujet, fiche).

## Prépare ton vote

Une carte au départ (et sur les fiches d’information) des pays qui ont des données dans `src/prep.js` (`PREP`, 14 pays ; aucune carte pour les autres) : l’organisme électoral (avec un lien quand il a un site, sans lien sinon), un lien pour vérifier son inscription, 2 à 4 éléments datés et sourcés, une phrase de réserve. Les éléments à venir (ou sans date) viennent d’abord, les passés ensuite, en retrait avec la mention « passé » ; l’ordre du fichier est gardé dans chaque groupe. « Passé » est jugé à la **date du jour de l’appareil, à l’exécution** : aucune date n’est écrite dans le code. Le champ `d` d’un élément est la date du fait (échéance, annonce) ou `null`, pas forcément celle du scrutin. La ligne du haut est un compte à rebours (« Vote dans 76 jours ») **seulement** pour une date `q: "exact"` de la `META` de l’édition ; pour un mois, une période, « d’ici » ou « avant », elle dit « Vote prévu en… (date à confirmer) » ; elle disparaît quand l’échéance est passée. Pour une date exacte à venir, « Ajouter à mon agenda » télécharge un fichier `.ics` (journée entière, rappel la veille ; lien `data:`), caché dans `artifact.html` (cadre isolé : pas de téléchargement).

Le build valide `PREP` : organisme (nom, sigle, `url` en https ou `null`), sources en https, `check` avec une source existante, chaque élément avec `d` valide ou `null`, une source de **ce** pays et le texte dans les 5 langues. Une fiche invalide, ou un pays sans édition, donne un avertissement (pas un échec, sauf `--strict`) et le pays est servi sans carte. `<extra>/prep.js` complète ou remplace `src/prep.js` (c’est ce que font les tests).

## Partager

Le bouton « Partager » des résultats envoie « Mon parti le plus proche pour Nigeria 2027 : NDC (61 %) — et toi ? » et l’adresse du pays (`SITE_URL + <cc>/#/<cc>/<langue>`), jamais les réponses. Partage natif (`navigator.share`) quand la page est en contexte sécurisé et hors cadre isolé ; sinon copie dans le presse-papiers, lancée dans le clic (« Copié ») ; si elle est refusée, un champ de texte visible, déjà sélectionné. Pas de bouton tant qu’aucun parti n’est classé.

## Aperçus de liens, manifeste, pages par pays

`index.html` porte les balises `og:*`, `twitter:*`, l’adresse canonique, `theme-color`, le manifeste et l’icône Apple ; `og.png` fait 1200 × 630 (moins de 300 Ko : certains aperçus refusent plus). `<cc>/index.html` (généré, un par édition) donne à chaque pays son titre, sa description et la même image, puis redirige tout de suite vers `../#/<cc>` (ou le `#/<cc>/<langue>` du lien partagé) : les robots d’aperçu lisent les balises sans exécuter le script. `python3 tools/og.py` refait `og.png` et `icons/` (carte de l’Afrique tirée de `src/mapdata.js`, pays à élection d’ici fin 2027 en ambre).

## Polices et données par langue

Aucune requête vers un serveur de polices : `fonts/` contient 5 fichiers WOFF2 (Bricolage Grotesque pour les titres, Readex Pro pour le texte ; latin, latin étendu, arabe) déclarés dans `src/shell.html` avec `unicode-range` et `font-display: swap`. Seul le latin du texte courant est préchargé ; un visiteur en alphabet latin télécharge 107 Ko de polices (objectif : moins de 120 Ko), l’arabe n’est demandé qu’en interface arabe (le nom « العربية » du choix de langue utilise une police du système pour ne pas le déclencher). `node tools/fonts.js` refait `fonts/` (npm et accès au registre ; Google Fonts n’est pas nécessaire).

Un pays se charge en deux temps : `data/<cc>.json` (base) puis, si la langue choisie n’est pas la langue de base, `data/<cc>.<langue>.json`. Changer de langue dans un pays déjà ouvert télécharge la traduction d’abord (le bouton est « occupé », l’écran ne bouge pas) ; en cas d’échec ou de délai dépassé, la langue reste l’ancienne et un message le dit. Un seul téléchargement par fichier à la fois (`inflight`), abandon au bout de `LOAD_TIMEOUT`, écran d’erreur avec « Réessayer » pour la base.

## Signaler une erreur, quoi de neuf

Sous chaque position codée de l’onglet « Par question », « Signaler une erreur » ouvre (nouvel onglet) un nouveau ticket GitHub déjà rempli (pays, question, parti, position codée, source, langue) ; rien ne part tant que la personne ne l’envoie pas, et ses réponses n’y figurent jamais. Le pied de page a un lien « Quoi de neuf » vers `CHANGELOG.md` sur GitHub.

## Bandeau du pays et drapeaux

Choisir un pays ouvre un grand bandeau : drapeau (72 × 54), silhouette du pays en une couleur, nom dans la langue de l’interface (Bricolage Grotesque), ligne d’élection (ou « pas d’élection nationale avant fin 2027 »), puis les boutons de langue. Le départ, les résultats et les pages d’information portent un bandeau compact (drapeau 32 × 24 + nom) ; l’écran de question garde seulement le drapeau (24 × 18) dans l’en-tête, le nom étant dans un texte caché pour les lecteurs d’écran. Les 54 pays de la carte ont leur bandeau ; la France a le sien (hors choix de langue, puisqu’elle n’a qu’une langue).

- **Silhouette** : le tracé de la carte (`src/mapdata.js`), cadre calculé sur le pays entier (`getBBox`) : les îles et archipels (Seychelles, Maurice, Comores, Cap-Vert, São Tomé) restent visibles, avec un contour d’au moins 1 px. La France n’est pas sur la carte : son contour est un tracé simplifié écrit dans `src/app.js` (`FR_PTS`, `FR_CORSE`).
- **Drapeaux** : fichiers `flags/<cc>.svg` (4 × 3, paquet npm `flag-icons`, licence MIT, passés à svgo), jamais incorporés à `index.html`, chargés par `<img>` (décoratifs, `alt=""`, `decoding="async"`, paresseux hors bandeau), aucune requête tierce. Un drapeau qui ne se charge pas disparaît et le reste du bandeau fonctionne. `node tools/flags.js` les refait (npm et accès au registre nécessaires) et signale tout fichier de plus de 15 Ko ; le build les recopie dans le dossier de sortie quand `--out` en change.

## Module « valeurs » et compteur collectif

Après la dernière question de partis, une invitation facultative (« Commencer les 10 » / « Passer à mes résultats », une fois par session) propose **10 énoncés communs à tous les pays** (`src/values.js`, réponses sur l’échelle habituelle à 5 points). Les mêmes questions sont aussi proposées par une carte « Où tu te situes sur les valeurs » sur les résultats et sur chaque page de pays sans questionnaire. Les réponses sont gardées à part (`state.vals`, dans la session de l’onglet, effacées par « Recommencer »), **n’entrent jamais dans les scores des partis**, et donnent une **position sur cinq niveaux**.

**Calcul** (`valuesLevel`, exposée en `window.__etv.valuesLevel(vals)`). Chaque énoncé a un sens `ax` : `+1` si être d’accord est la position libérale–progressiste, `−1` si c’est la position conservatrice–nationaliste. Pour une réponse `a` (−2 à +2), `v = ax × a / 2`. La position `s` est la moyenne des `v` sur les énoncés répondus (les passés sont ignorés) ; il faut **au moins 6 réponses**. Niveaux : `s ≥ 0,5` → 2 (clairement libérale–progressiste) ; `0,15 < s < 0,5` → 1 ; `|s| ≤ 0,15` → 0 (équilibrée) ; `−0,5 < s < −0,15` → −1 ; `s ≤ −0,5` → −2 (clairement conservatrice–nationaliste). Les seuils sont calculés en entiers (`S = Σ ax × a`, `s = S / 2n`) pour être exacts. Être d’accord (ou en désaccord) avec tout donne 0, puisque les sens sont mêlés.

**Grille de conception des énoncés** (à respecter pour tout changement de `src/values.js` ; le build vérifie le nombre, les identifiants, les sens et les langues) :

- Le module mesure des **valeurs** (libertés, égalité, place de la religion, ordre, souveraineté, tradition), **pas la gauche ou la droite économique** : aucun énoncé sur les impôts, les prix, les salaires, la dette ou le rôle de l’État dans l’économie, pour ne pas confondre avec les positions économiques des partis.
- **« Libérale–progressiste »** désigne ici l’attachement aux libertés individuelles, à l’égalité des droits (femmes–hommes, choix du conjoint), à la liberté de critiquer, à la circulation et au pluralisme culturel. **« Conservatrice–nationaliste »** désigne l’attachement à la tradition et à la religion comme guide de la loi, à l’ordre avant certaines libertés, à la souveraineté face aux conditions étrangères et à la préférence nationale. Ce sont deux pôles descriptifs, pas des jugements : l’interface les explique (« Que veulent dire ces mots ? ») et rappelle qu’aucun n’est bon ou mauvais.
- **Équilibre 5 / 5** : cinq énoncés `+1` et cinq `−1`, mêlés dans l’ordre (v1 `+1`, v2 `−1`, …), pour que l’ordre ne favorise aucun pôle et que tout approuver ne classe nulle part.
- **Aucun énoncé n’est attribué à un parti** ni ne cite un parti ou un candidat ; chacun tient en une phrase, écrite dans les cinq langues.
- **Pas d’énoncé sur l’orientation sexuelle (LGBTQ+)**, volontairement (décision du porteur du projet) : dans plusieurs pays, y répondre sur un appareil, ou ajouter sa réponse à un compteur, peut mettre des personnes en danger. Les 10 énoncés couvrent d’autres lignes de fracture (genre, famille, religion, parole, ordre, souveraineté, circulation, préférence nationale, pluralisme, tradition). Le texte « Comment ça marche ? » du site le dit en une phrase, dans les cinq langues.

**Compteur collectif, facultatif et anonyme.** Si `meter.config.json` contient une adresse (`{ "endpoint": "https://…" }`, https obligatoire, sans slash final), la page :

- lit `GET <adresse>/counts` **une fois par session** (délai de 6 s, résultat gardé en mémoire ; en cas d’échec, la partie collective disparaît sans bruit et un lien « Réessayer » apparaît dans « Comment ça marche ? ») et affiche le **compteur** : une barre à deux sens (libéral–progressiste au début, conservateur–nationaliste à la fin, miroir en arabe), longueurs proportionnelles aux parts, part « équilibrée » écrite en texte, nombre de personnes et de pays, date de mise à jour. Le compteur d’Afrique est sous le titre de la carte et dans la carte des résultats ; celui du pays, dans la carte des résultats et sur l’écran de départ à partir de 30 contributions. **Sous 30 contributions** : « Le compteur s’ouvre à 30 réponses — N pour l’instant » et une ligne de progression, pas de pourcentages. Il est toujours accompagné de « Des personnes qui ont choisi de participer, pas un sondage représentatif » ;
- propose le bouton « Ajouter mon résultat au compteur d’Afrique (anonyme) » (un seul par pays et par navigateur, `localStorage` `etv.sent.<cc>`), qui envoie `POST <adresse>/v` avec `{"c":"ng","l":1}` (`Content-Type: text/plain`, `keepalive`, sans cookie) : seuls partent le code du pays et un niveau sur cinq, jamais les réponses.

**Adresse vide (le cas du dépôt tant que le serveur n’est pas déployé) : aucune requête n’est faite, ni compteur ni bouton d’envoi, mais la barre personnelle s’affiche.** Le serveur (Cloudflare Worker + D1, `meter/`) est écrit mais à déployer par le propriétaire : `meter/README.md` explique chaque étape sans programmer. Le build valide `src/values.js` (échec sinon), lit `meter.config.json` (`--endpoint` le remplace), écrit `meter/countries.json` (liste des pays acceptés par le Worker) et copie `flags/`.

Adresses : `#/<cc>/<langue>/values` (invitation), `…/values/<n>` (énoncé n sur 10), `…/values/done` (position).

**Tests** (en plus de la liste ci-dessus) : bandeau du choix de la langue pour Nigeria, Kenya, Cap-Vert, Libye (arabe), un pays sans élection, à 320, 390 et 1280 px en anglais, français et arabe ; les 54 pays (drapeau chargé depuis `flags/`, silhouette non vide et contenue dans le bandeau à 320 px) ; la France ; drapeau défaillant ; bandeaux compacts et drapeau de l’en-tête ; `valuesLevel` (tout d’accord, tout en désaccord, séries fabriquées, seuils exacts, moins de 6 réponses, réponses passées) ; scores des partis inchangés ; parcours complet de l’invitation, des 10 énoncés, de la carte, du rechargement et de « Recommencer » ; pages d’information et pays sans élection ; compteur avec une API simulée (moins de 30, majorité progressiste, majorité conservatrice, égalité, miroir en arabe, pourcentages, étiquette aria, mouvement réduit, une seule lecture par session) ; envoi (charge utile exacte `{c, l}`, un seul par pays et par navigateur, échec et nouvelle tentative) ; panne du compteur (réseau, 500, réponse absurde, délai de 6 s) sans erreur de page ; adresse vide sans requête externe ni bouton ; build (`--endpoint`, fichier de configuration, validation de `src/values.js`, `meter/countries.json`, `flags/` recopié) ; contrastes du compteur ; `node meter/test.mjs` (Worker, fausse base D1 et vrai SQLite).
