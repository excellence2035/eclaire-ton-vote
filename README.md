# Éclaire ton vote

Plateforme d’aide au vote pour les jeunes, en Afrique : une carte des élections, puis un questionnaire par ministère qui compare les **partis politiques** (présidentielles et législatives), sujet par sujet.

- Carte des 54 pays africains : élection nationale prévue d’ici fin 2027 (vert) ou non (rouge).
- Édition pilote : Nigeria 2027, 38 questions, 9 thèmes, en anglais, français, portugais, swahili et arabe.
- Prototype : présidentielle française 2027.

**Prototype.** Les positions sont codées à partir de sources publiques datées (liens dans l’onglet « Méthode et sources ») et n’ont pas encore été validées par les partis ni par un comité indépendant. Aucune réponse n’est enregistrée : tout reste dans le navigateur.

- Pays où l’on ne peut pas encore comparer les partis honnêtement : une fiche d’information (faits, règles, principaux acteurs, sources).

Adresses (partageables) : `#/` la carte, `#/ke` un pays (choix de la langue), `#/ke/sw` son départ, `#/ke/sw/q/3` une question, `#/ke/sw/results` (ou `/results/method`…) les résultats ; formes courtes `#ke`, `#cv-pt`. Le bouton Retour passe d’un écran à l’autre (le questionnaire n’occupe qu’une entrée). Le questionnaire en cours est gardé dans l’onglet (`sessionStorage`) et la langue choisie sur l’appareil (`localStorage`, clé `etv.ui`) ; les réponses ne vont jamais dans l’adresse ni sur le réseau.

Le site est publié avec GitHub Pages : `index.html` (l’application, sans les données des pays) et `data/<cc>.json` (une édition par pays, chargée à la demande).

## Structure et construction

```
src/shell.html          titre, CSS (thèmes clair et sombre), squelette HTML
src/ui/*.js             textes de l’interface (fr, en, pt, sw, ar) ; t-multi.js : chargement, fiches d’information…
src/africa.js           calendrier électoral des 54 pays + sources ; src/mapdata.js : la carte
src/app.js              toute l’application (carte, questionnaire, calcul, résultats)
src/editions/<cc>.js    une édition par pays (format : src/EDITION_SPEC.md)
src/i18n/<cc>.js        ses traductions (facultatif)
tools/build.js          construit index.html, artifact.html et data/*.json
tools/test.py           tests de bout en bout (Playwright)
```

**Ajouter un pays**

1. Écrire `src/editions/<cc>.js` selon `src/EDITION_SPEC.md` (`<cc>` = code ISO alpha-2 en minuscules) : `SRC_<CC>`, `META_<CC>` et soit `ED_<CC>` (questionnaire), soit `INFO_<CC>` (fiche d’information). Vérifier avec `node src/tools/validate-edition.js src/editions/<cc>.js`.
2. Facultatif : ses traductions dans `src/i18n/<cc>.js` (`I18N_<CC> = { fr: {…}, ar: {…} }`, mêmes positions que les questions).
3. `node tools/build.js` : valide chaque édition, écarte (avec un avertissement) celles qui ne passent pas et les traductions incomplètes, écrit `data/<cc>.json`, `index.html` et `artifact.html` (même page sans `<html>/<head>/<body>`, pour un hébergeur qui ajoute son propre squelette ; elle a aussi besoin du dossier `data/`). Le pays apparaît alors sur la carte avec sa coche (questionnaire) ou son repère « i » (fiche), dans les langues disponibles.
4. `python3 tools/test.py` (Python 3 + Playwright avec Chromium) : sert le dépôt en local et teste la carte, le Nigeria dans les 5 langues, la France, le thème sombre, une fiche d’information et une édition « leader » de test, l’écran hors ligne, les adresses et le bouton Retour, la reprise après rechargement, la langue de départ, le focus et les annonces, le bouton ★ « compte double », la confirmation avant d’effacer, et les titres des résultats (premier aperçu, égalité, aucun parti proche, partis peu documentés). Captures d’écran : `--shots <dossier>`.

Options de `tools/build.js` : `--extra <dossier>` ajoute des éditions (`<dossier>/editions`, `<dossier>/i18n`, utilisé par les tests), `--out <dossier>` écrit ailleurs qu’à la racine, `--strict` échoue au moindre avertissement. La France est dispensée de validation (elle dépasse volontairement les limites du validateur).
