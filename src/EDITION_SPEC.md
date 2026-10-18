# Country edition spec — Éclaire ton vote

Éclaire ton vote is a youth Voting Advice Application for Africa. A young voter picks a country, picks up to three priority issues, answers precise policy statements (strongly agree … strongly disagree), and sees which **political parties** are closest to their answers, overall and issue by issue. Elections are presidential and/or parliamentary, so the platform compares **parties, not personalities**. The reference edition is Nigeria: read `src/parts/part-ng.js` and `src/parts/ng-extra.js` before starting; your edition must reach the same depth and quality.

## Output

One file, `src/editions/<cc>.js` (`<cc>` = lower-case ISO alpha-2 code, e.g. `ke`), defining exactly three globals, with `<CC>` upper-case:

```js
const SRC_<CC> = { key: { o: "Outlet", t: "Exact article/document title", d: "12 Sep 2026", u: "https://…" }, … };
const META_<CC> = { ev: [{ t: "presidential", d: "2026-11-15", q: "exact" }], src: "key", note: "optional one-line caveat" };
const ED_<CC> = { … };
```

Write the base text in **English** (translations are done later). Plain UTF-8, curly apostrophes (’) and quotes (“ ”) inside strings, never a raw `"` inside a double-quoted string.

### META (the election itself — verify it, it may have changed)
- `t`: one of `general` (president + parliament same day), `presidential`, `legislative`, `pres_leg`, `referendum`, `national` (other national vote).
- `d`: ISO date `YYYY-MM-DD`, or `YYYY-MM` if only the month is known. `q`: `exact`, `month` (month known), `by` (no later than that month), `before` (before that date, not fixed), `range` (then also `d2`).
- Several events allowed (e.g. presidential then legislative). `src` = key in SRC of the most recent reliable source for the date. `note` only if the vote is in serious doubt (postponement, coup, war).

### ED fields
```js
const ED_<CC> = {
  id: "<cc>", name: "Country name in English", lang: "en",          // lang: base language of this file, always "en"
  role: "pres",            // "pres" if a presidential vote is part of this election, else "leader" (party leader shown instead)
  strip: "Presidential election 2026",                  // short name of the election
  stripDate: "Sunday 15 November 2026",                 // when, in words; mention both races if two
  facts: [["Presidential vote", "Sun 15 Nov 2026"], ["Second round (if needed)", "…"], ["Parties compared", "5"]],   // exactly 3 rows
  factsSrc: ["key", …],
  system: [[title, text], …],     // 4–6 rows: political system; how the president/parliament is elected (rounds, thresholds, seats, electoral system); who can vote; rules/institutions of this election (electoral commission, recent reforms); key context (security, transition, boycotts) when relevant
  systemSrc: ["key", …],
  status: "Party positions in this edition were coded from manifestos, speeches, votes and government records published up to <date>. They have not yet been validated by the parties or by an independent committee.",
  others: ["PARTY · Name", …, "and N other candidates/parties"],   // other contenders not compared
  othersSrc: "key",
  parties: [ … ],
  themes: [ … ],
  questions: [ … ]
};
```

**Parties** (3 to 6: the main parties or coalitions contesting this election, always including the governing party and the main opposition forces; a coalition can be one “party” if it runs jointly):
```js
{ id: "<cc>_abc", sigle: "ABC", nom: "Official full name (original language)", cand: "Presidential candidate, or party leader if role is leader / not yet designated", vp: "Running mate (optional)",
  tag: "Governing party | Main opposition | Opposition | Opposition coalition …",
  col: ["#2F5D8C", "#9DBBE6"],   // badge colour: [light theme: dark enough for white text, contrast ≥ 4.5:1 ; dark theme: light enough for near-black text]. Use the party’s identity hue when known; keep hues distinct within the country.
  commit: [["Key commitment in one line", "srcKey"], …] }   // 4–6 documented commitments
```
If the candidate is not designated yet, set `cand` to the party leader and add `candNote: "Candidate not yet designated"`.

**Themes** (8 to 10), each tied to the **real ministries of the current government** of that country (use their actual names):
```js
{ id: "econ", name: "Economy & public finance", min: "Finance · Budget · Planning" }
```
Use these ids where they fit: `econ`, `security`, `gov`, `integrity` (corruption & civil liberties), `edu`, `health`, `social` (social protection & jobs), `agri`, `energy` (energy & environment), `land` (land & housing), `youth` (youth, digital & culture), `foreign`, `infra` (transport & infrastructure), `water`. Add a new short id only if none fits.

**Questions** (25 to 40 in total; 3 to 6 per theme; fewer well-sourced questions beat many thin ones):
```js
{ theme: "econ", short: "Short title (≤ 6 words)",
  text: "One clear policy statement a young voter can agree or disagree with.",
  ctx: "2–4 factual sentences: what exists today, what is debated, the main argument on each side. Neutral.",
  cells: { "<cc>_abc": { p: 2, k: "stated", s: "srcKey", n: "1–2 sentences: who said/did what, when, in your own words; short quotes allowed in “ ”." }, … },
  nd: { "<cc>_xyz": "Optional: why this party has no documented position, or the closest thing it said." } }
```

## When a real comparison is impossible

If, after research, fewer than 3 parties or coalitions have positions you can document on most themes (for example: no parties on the ballot, indirect vote, vote run by a junta with the opposition banned, or no published programmes), do **not** invent a questionnaire. Write `src/editions/<cc>.js` with `SRC_<CC>`, `META_<CC>` and, instead of `ED_<CC>`, an `INFO_<CC>`:

```js
const INFO_<CC> = {
  id: "<cc>", name: "Country name in English", lang: "en",
  strip: "Legislative elections 2027", stripDate: "December 2027 (date not set)",
  facts: [[label, value], [label, value], [label, value]], factsSrc: ["key", …],
  system: [[title, text], …], systemSrc: ["key", …],          // 4–6 rows, as for ED
  actors: [["Name of party, coalition, movement or institution", "1–2 sentences: who they are, what they stand for or did, with the date", "srcKey"], …],   // 3–8 rows
  why: "2–4 sentences: why the platform cannot compare parties honestly for this vote yet, and what would change that."
};
```

## Coding rules

- `p` ∈ {2, 1, 0, −1, −2}: 2 = clearly agrees with the statement, 1 = leans agree / agrees with conditions, 0 = explicitly mixed or neutral, −1 = leans against, −2 = clearly against. Code what the party/candidate actually said or did, not what you guess.
- `k`: `stated` = manifesto, campaign statement or interview from the current campaign cycle (roughly the last 12–18 months); `record` = a vote, law, decree, budget or government action (the governing party’s record is a legitimate, often rich source); `party` = an official party document or party spokesperson; `older` = a position stated before the current cycle (state the year in the note, e.g. “Atiku (2022) said…”).
- A cell exists only with a source that supports it. If nothing reliable exists, leave the party out of `cells` (it shows as “not documented”); add an `nd` note when helpful.
- A party’s position may come from its presidential candidate or leader: the candidate speaks for the party.
- Coverage targets: every question has at least 2 parties coded, most have 3+; every party is coded on at least 35% of questions where the record allows (the governing party usually much more). Prefer questions where parties actually differ; a few consensus questions are fine.
- Questions must be pointed and concrete (ministries’ real files: budgets, subsidies, taxes, debt, IMF programmes, security operations, term limits, electoral rules, land, mining contracts, school fees, health insurance, fuel and power prices, youth jobs, internet shutdowns, press freedom, decentralisation, relations with neighbours/regional blocs, foreign military presence …). Reflect live debates of 2025–2027 in that country. No questions about a candidate’s person, health, ethnicity or religion. No question that targets an ethnic or religious group.
- Neutral wording: avoid loaded words; alternate statements that a governing-party voter would agree with and ones an opposition voter would agree with.
- Where the vote is non-competitive or uncertain (dominant party, junta-led transition, war, indirect vote): still build the questionnaire. Use the governing side’s record and the opposition’s published statements, say so plainly in `status`, and add a `system` row on the context.

## Research budget and saving your work

- Tool limits are shared with other agents working in parallel: use **at most 40 WebSearch calls and 50 WebFetch calls**. Plan searches carefully (one search per issue or party, in the country’s main language when it helps).
- Keep running notes in `src/notes/<cc>.md` (verified facts with their URLs; mark anything not yet opened). If a notes file already exists for your country, read it first and reuse what it verified.
- Write `src/editions/<cc>.js` early and extend it as you go. If a tool limit stops you, finish the file with what you have verified (fewer questions is better than unsourced ones), make it load, and write `STATUS: INCOMPLETE` plus what is missing at the top of the notes file.

## Source rules (strict)

- Use WebSearch/WebFetch. **Only cite URLs that appeared in search results or that you opened.** Never construct or guess a URL. Open (WebFetch) every page you cite at least once to confirm it supports the cell.
- Prefer: party manifestos and websites, electoral commission, government/official gazette, reputable national and international media (e.g. national dailies, AFP, Reuters, BBC, RFI, Jeune Afrique, Africanews, The Continent, ISS Africa, Crisis Group). Wikipedia only for background system facts, never for a party position.
- `d` = publication date as “12 Sep 2026” (or “Sep 2026”, “2026”). `o` = outlet name. `t` = article title (translate to English only if needed and keep it recognisable).
- Today is 11 October 2026. Do not state as fact anything you could not verify; if a date or candidate is unconfirmed, say so in the text.

## Validate

Run `node src/tools/validate-edition.js src/editions/<cc>.js` from the repository root and fix every error until it prints `OK`. Warnings are coverage hints: reduce them where research allows.
