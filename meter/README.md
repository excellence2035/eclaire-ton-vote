# Compteur collectif : mise en service pas à pas

Ce dossier contient le petit serveur qui reçoit, **de façon anonyme et facultative**, la position sur les valeurs de ceux qui choisissent de l'ajouter au compteur d'Afrique, et qui redonne les totaux au site. Il tourne sur **Cloudflare Workers** avec une base **D1** : gratuit pour un usage de ce volume, sans machine à gérer.

Tant que ce serveur n'est pas en ligne, le site marche normalement : la carte personnelle « Où tu te situes sur les valeurs » s'affiche, mais le compteur collectif et le bouton d'envoi sont absents (`meter.config.json` contient `"endpoint": ""`). **Rien n'est envoyé nulle part.**

## Ce qui est reçu, ce qui est gardé

À chaque envoi, le site transmet **uniquement** le code du pays (par exemple `ng`) et **un niveau parmi cinq** (de −2 à 2), sous la forme `{"c":"ng","l":1}`. Jamais les réponses aux énoncés, jamais de nom, d'identifiant, de cookie ni d'appareil.

Le serveur garde :

| Où | Quoi | Combien de temps |
|---|---|---|
| table `counts` | un compteur par pays et par niveau (« 53 personnes au Nigeria, niveau 1 ») | tant que le compteur existe |
| table `limits` | une **empreinte** (SHA-256 de « sel du jour + adresse IP », tronquée) et un nombre d'envois, pour refuser plus de 10 envois par jour et par connexion | 48 heures au plus, puis supprimée |
| table `meta` | le sel du jour (tiré au hasard) et la date de dernière mise à jour | le sel : 48 heures au plus |

L'adresse IP **n'est jamais écrite** (ni en clair dans la base, ni dans un journal) ; comme le sel change chaque jour et disparaît au bout de 48 heures, l'empreinte ne permet pas de retrouver l'adresse. Le Worker n'écrit **rien dans les journaux** (`[observability] enabled = false` dans `wrangler.toml`), n'utilise **aucun cookie** et **aucun outil de mesure d'audience**. Les réponses sont ouvertes à tous les sites (`Access-Control-Allow-Origin: *`) : c'est ce qui permet à la page de lire les totaux.

Limites à connaître : c'est un compteur de **volontaires**, pas un sondage. Rien n'empêche quelqu'un de s'y prendre à plusieurs reprises depuis des connexions différentes ; le plafond de 10 envois par jour et par connexion limite seulement les abus faciles. Le site le dit à côté des chiffres (« Des personnes qui ont choisi de participer, pas un sondage représentatif »).

## Mise en service (environ 20 minutes, sans programmer)

Il faut un ordinateur avec **Node.js 18 ou plus** ([nodejs.org](https://nodejs.org), version « LTS ») et une adresse e-mail.

1. **Créer un compte Cloudflare** (gratuit) sur [dash.cloudflare.com](https://dash.cloudflare.com/sign-up). Pas de carte bancaire nécessaire pour l'offre gratuite.

2. **Ouvrir un terminal dans ce dossier** (`meter/`). Sous Windows : ouvrir le dossier dans l'Explorateur, taper `cmd` dans la barre d'adresse, Entrée. Sous macOS : clic droit sur le dossier, « Nouveau terminal au dossier ».

3. **Se connecter à Cloudflare** :
   ```
   npx wrangler login
   ```
   Une page s'ouvre dans le navigateur : cliquer sur « Autoriser ». (La première fois, `npx` propose d'installer `wrangler` : répondre `y`.)

4. **Créer la base de données** :
   ```
   npx wrangler d1 create vote-meter
   ```
   Le terminal affiche un bloc avec une ligne `database_id = "xxxxxxxx-xxxx-…"`. **Copier cet identifiant** et le coller dans `wrangler.toml`, à la place de `REMPLACER-PAR-L-IDENTIFIANT-D1`. Enregistrer le fichier.

5. **Créer les tables** (fichier `schema.sql`) :
   ```
   npx wrangler d1 execute vote-meter --remote --file=schema.sql
   ```
   Répondre `y` si le terminal demande confirmation.

6. **Mettre le Worker en ligne** :
   ```
   npx wrangler deploy
   ```
   Le terminal affiche l'adresse du Worker, du genre `https://vote-meter.NOM-DU-COMPTE.workers.dev`. **La copier.**

7. **Vérifier** : ouvrir `https://vote-meter.NOM-DU-COMPTE.workers.dev/counts` dans le navigateur. On doit voir quelque chose comme
   ```
   {"updated":"","total":{"-2":0,"-1":0,"0":0,"1":0,"2":0},"byCountry":{}}
   ```

8. **Brancher le site** : dans `meter.config.json` (à la racine du dépôt, pas dans ce dossier), remplacer la valeur vide par l'adresse copiée, **sans slash final** :
   ```json
   { "endpoint": "https://vote-meter.NOM-DU-COMPTE.workers.dev" }
   ```
   Puis reconstruire et publier le site comme d'habitude (`node tools/build.js`, voir le README principal). Le bouton « Ajouter mon résultat au compteur d'Afrique (anonyme) » et le compteur apparaissent. Le compteur d'Afrique ne s'affiche qu'à partir de **30 contributions** ; avant, le site écrit « Le compteur s'ouvre à 30 réponses : N pour l'instant ».

## Au quotidien

- **Éteindre le compteur** : remettre `"endpoint": ""` dans `meter.config.json`, reconstruire, publier. Le site redevient entièrement local. (Pour supprimer aussi le serveur : `npx wrangler delete`, et supprimer la base dans le tableau de bord Cloudflare, rubrique « Storage & Databases › D1 ».)
- **Voir les totaux** : l'adresse `/counts` (étape 7). Ils sont mis en cache 60 secondes.
- **Repartir de zéro** (par exemple après les essais) :
  ```
  npx wrangler d1 execute vote-meter --remote --command "DELETE FROM counts; DELETE FROM limits; DELETE FROM meta;"
  ```
- **Ajouter un pays** : le Worker n'accepte que les codes de `meter/countries.json`, fichier **généré** depuis `src/africa.js` (plus la France) par `node tools/build.js`. Après un changement de la liste : reconstruire le site, puis `npx wrangler deploy` ici.
- **Mettre à jour le code du Worker** (`worker.js`) : `npx wrangler deploy` de nouveau.
- **Coût** : l'offre gratuite de Cloudflare (au moment de l'écriture : 100 000 requêtes par jour pour les Workers, 5 millions de lectures et 100 000 écritures de lignes par jour pour D1 ; à revérifier sur cloudflare.com) est très au-dessus des besoins d'un compteur de ce genre. En cas de dépassement, le Worker répond en erreur et le site masque simplement le compteur : rien ne casse.

## Le contrat avec le site

| Requête | Réponse |
|---|---|
| `POST /v`, corps `{"c":"ng","l":1}`, `Content-Type: text/plain` (200 octets au plus) | `204` si c'est compté ; `400` si le corps n'est pas exactement `{c, l}` avec un pays connu et un entier de −2 à 2 ; `413` si le corps est trop long ; `429` au-delà de 10 envois par jour et par connexion ; `405` pour une autre méthode |
| `GET /counts` | `200` `{"updated":"2026-10-20T08:00:00Z","total":{"-2":…,"-1":…,"0":…,"1":…,"2":…},"byCountry":{"ng":{…}}}`, avec `Cache-Control: public, max-age=60` |

Niveaux : `2` nettement libéral–progressiste, `1` plutôt libéral–progressiste, `0` équilibré, `-1` plutôt conservateur–nationaliste, `-2` nettement conservateur–nationaliste.

## Tests

```
node meter/test.mjs
```

Le test rejoue tout le contrat (validation, tailles, plafond quotidien, suppression après 48 heures, adresse jamais écrite, aucun journal, panne de la base) sur une fausse base D1 en mémoire et, avec Node 22 ou plus, sur un vrai SQLite qui exécute `schema.sql`. Il fait aussi partie de la suite `python3 tools/test.py` (test `meter_worker`).
