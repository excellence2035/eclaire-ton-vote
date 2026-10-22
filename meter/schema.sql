-- Compteur collectif : à exécuter une fois (voir README.md).
-- counts : un compteur par pays et par niveau (2 = nettement libéral–progressiste, 1 = plutôt, 0 = équilibré, -1 = plutôt, -2 = nettement conservateur–nationaliste).
CREATE TABLE IF NOT EXISTS counts (
  country TEXT    NOT NULL,
  level   INTEGER NOT NULL CHECK (level BETWEEN -2 AND 2),
  n       INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (country, level)
);
-- limits : contributions par empreinte (SHA-256 salé, tronqué ; jamais l'adresse IP) et par jour ; supprimé après 48 h.
CREATE TABLE IF NOT EXISTS limits (
  h   TEXT    NOT NULL,
  day TEXT    NOT NULL,
  n   INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (h, day)
);
-- meta : le sel du jour (clé « salt:AAAA-MM-JJ », supprimé après 48 h) et la date de dernière mise à jour (clé « updated »).
CREATE TABLE IF NOT EXISTS meta (
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL
);
