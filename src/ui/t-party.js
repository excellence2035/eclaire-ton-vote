
/* ================== Logique de partis : textes revus (fr, en) ================== */
Object.assign(T.fr, {
  heroKicker: "Présidentielles et législatives · 54 pays",
  mapLead: "Réponds à des questions précises sur les grands sujets de chaque ministère et découvre quels partis pensent comme toi, sujet par sujet.",
  tagline: "Anonyme · Des partis, pas des personnes · Sources publiques · Aucune consigne de vote",
  footer1: "Prototype. Les positions sont codées à partir de sources publiques et n’ont pas encore été validées par les partis ni par un comité indépendant.",
  prepText: "Nous rassemblons les programmes et les positions des partis. En attendant, tu peux découvrir le fonctionnement avec l’exemple du Nigeria.",
  whoCompared: n => `Les ${n} partis comparés`,
  alsoRunning: "Autres partis et candidatures",
  presCand: "Candidat·e à la présidentielle",
  partyBasis: "On compare des partis, pas des personnes. La position d’un parti vient de son programme, de ses votes ou de son action au pouvoir, et des déclarations de son ou sa candidate à la présidentielle, qui porte aussi ses idées aux législatives.",
  resClosest: p => `Le parti le plus proche de tes idées : ${p}.`,
  resTie: ps => `Plusieurs partis sont à égalité : ${ps}.`,
  resNoneText: "Réponds à au moins deux questions sur lesquelles les partis ont une position documentée.",
  seeProfile: "Voir le parti",
  rankCaveat: "Le pourcentage mesure la proximité entre tes réponses et les positions documentées de chaque parti. Ce n’est pas une consigne de vote. Un parti dont peu de positions sont connues est ramené vers 50 % pour ne pas arriver en tête sur deux ou trois questions seulement.",
  byThemeIntro: "Pour chaque sujet, le parti dont les positions documentées ressemblent le plus à tes réponses. Tes sujets prioritaires viennent en premier.",
  themeTie: (t, ps, pct) => `Si « ${t} » compte pour toi, plusieurs partis sont à égalité : ${ps} (${pct}).`,
  themeNoData: "Aucun parti n’a de position documentée sur les questions auxquelles tu as répondu ici.",
  whatTheySay: "Ce que disent les partis, avec les sources",
  mFormula1: "Chaque réponse est placée sur une échelle de −2 (pas du tout d’accord) à +2 (tout à fait d’accord). Pour chaque question, on mesure l’écart entre ta position et celle du parti : accord = 1 − |écart| ÷ 4.",
  mFormula2: "Une question d’un sujet prioritaire pèse deux fois plus, comme une question marquée « compte double ». On ne compte que les questions où le parti a une position documentée. Les « + 3 × 50 % » ajoutent l’équivalent de trois réponses neutres : un parti peu documenté reste près de 50 % tant qu’on ne connaît pas assez ses positions. Par sujet, on ajoute une seule réponse neutre.",
  mCoding: [
    "Chaque position est codée à partir d’un document public daté : programme du parti, déclaration de son ou sa candidate, vote au Parlement ou action au pouvoir.",
    "Quatre types de preuve : programme ou déclaration récente, vote ou action, position officielle du parti, position antérieure à la campagne.",
    "Quand aucune source fiable n’existe, la position est « non documentée » et la question ne compte pas pour ce parti.",
    "Étape suivante : faire vérifier ce codage par un comité indépendant, puis envoyer le questionnaire aux partis pour qu’ils répondent et justifient eux-mêmes."
  ],
  mCovTitle: "Positions documentées par parti",
  mCovParty: "Parti",
  mNot: ["Elle ne dit pas pour qui voter.", "Elle ne juge pas les personnes : aucun profil psychologique, aucune note sur les candidats.", "Elle n’enregistre pas tes réponses."]
});
Object.assign(T.en, {
  heroKicker: "Presidential & parliamentary elections · 54 countries",
  mapLead: "Answer precise questions on the issues each ministry handles, and see which parties think like you, issue by issue.",
  tagline: "Anonymous · Parties, not personalities · Public sources · No voting advice",
  footer1: "Prototype. Positions are coded from public sources and have not yet been validated by the parties or by an independent committee.",
  prepText: "We are gathering the parties’ manifestos and positions. In the meantime, you can see how it works with the Nigeria example.",
  whoCompared: n => `The ${n} parties compared`,
  alsoRunning: "Other parties and candidates",
  presCand: "Presidential candidate",
  partyBasis: "We compare parties, not personalities. A party’s position comes from its manifesto, its votes or record in office, and statements by its presidential candidate, who also carries its platform into the parliamentary race.",
  resClosest: p => `The party closest to your views: ${p}.`,
  resTie: ps => `Several parties are tied: ${ps}.`,
  resNoneText: "Answer at least two questions where parties have a documented position.",
  seeProfile: "See party",
  rankCaveat: "The percentage measures how close your answers are to each party’s documented positions. It is not voting advice. A party with few known positions is pulled towards 50% so it cannot come first on two or three questions alone.",
  byThemeIntro: "For each issue, the party whose documented positions are closest to your answers. Your priority issues come first.",
  themeTie: (t, ps, pct) => `If “${t}” matters to you, several parties are tied: ${ps} (${pct}).`,
  themeNoData: "No party has a documented position on the questions you answered here.",
  whatTheySay: "What the parties say, with sources",
  mFormula1: "Each answer sits on a scale from −2 (strongly disagree) to +2 (strongly agree). For each question we measure the gap between your position and the party’s: agreement = 1 − |gap| ÷ 4.",
  mFormula2: "Questions in your priority issues count twice, as do questions you mark “counts double”. Only questions where the party has a documented position count. The “+ 3 × 50%” adds the equivalent of three neutral answers, so a thinly documented party stays near 50% until enough is known. Issue by issue, we add one neutral answer.",
  mCoding: [
    "Each position is coded from a dated public document: party manifesto, statement by its presidential candidate, parliamentary vote or record in office.",
    "Four kinds of evidence: recent manifesto or statement, vote or record, official party position, earlier position.",
    "Where no reliable source exists, the position is “not documented” and the question does not count for that party.",
    "Next step: have the coding checked by an independent committee, then send the questionnaire to the parties so they answer and justify it themselves."
  ],
  mCovTitle: "Documented positions per party",
  mCovParty: "Party",
  mNot: ["It does not tell you who to vote for.", "It does not judge individuals: no psychological profiles, no ratings of candidates.", "It does not store your answers."]
});

