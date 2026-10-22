
/* ================== Version 2 de l'interface : textes ajoutés ou revus (fr, en, pt, sw, ar) ==================
   Navigation (reprise, confirmation avant d'effacer), « compte double » en bouton, lecture des résultats
   (premier aperçu, égalité, aucun parti proche, partis peu documentés, réponses identiques), règles de la méthode,
   confidentialité (sessionStorage), pluriels du swahili et de l'arabe. Chargé après les autres fichiers ui/. */

/* Pluriels : Intl.PluralRules quand il existe, sinon une règle simple (1 → « one »). */
const plCat = (lang, n) => { try { return new Intl.PluralRules(lang).select(n); } catch (e) { return n === 1 ? "one" : "other"; } };
/* Swahili : le nom précède le nombre (« maswali 5 », « swali 1 »). */
const swN = (n, one, many) => `${plCat("sw", n) === "one" ? one : many} ${n}`;
/* Arabe : six catégories (zero, one, two, few, many, other) ; « # » est remplacé par le nombre. */
const arN = (n, f) => (f[plCat("ar", n)] || f.other).replace("#", n);
const AR_Q_NOM = { one: "سؤال واحد", two: "سؤالان", few: "# أسئلة", many: "# سؤالًا", other: "# سؤال" };
const AR_Q_GEN = { one: "سؤال واحد", two: "سؤالين", few: "# أسئلة", many: "# سؤالًا", other: "# سؤال" };
const AR_ANS_GEN = { one: "إجابة واحدة", two: "إجابتين", few: "# إجابات", many: "# إجابة", other: "# إجابة" };
const AR_COUNTRY = { one: "بلد واحد", two: "بلدان", few: "# بلدان", many: "# بلدًا", other: "# بلد" };

Object.assign(T.fr, {
  footer2: "Tes réponses restent sur ton appareil, dans cet onglet : elles ne sont envoyées nulle part.",
  mNot: [T.fr.mNot[0], T.fr.mNot[1], "Elle n’envoie tes réponses nulle part : elles restent sur ton appareil, dans cet onglet."],
  double: "Compte double pour moi",
  resReady: "Résultats prêts",
  resTie: (ps, pct) => `${ps} sont au coude à coude (${pct}).`,
  resEarly: (n, who, k) => `Premier aperçu après ${n} réponse${n > 1 ? "s" : ""} : ${who} en tête.`,
  resFar: (who, pct, k) => `Aucun parti n’est vraiment proche de tes réponses. ${k > 1 ? "Les moins éloignés" : "Le moins éloigné"} : ${who} (${pct}).`,
  resThin: "Aucun parti n’a assez de positions connues sur tes réponses.",
  resThinText: "Leurs pourcentages figurent plus bas, à titre indicatif, sous « Peu de positions connues sur tes réponses ». Réponds à d’autres questions pour obtenir un classement.",
  earlyText: n => `Réponds à au moins ${n} questions pour un résultat solide.`,
  earlyBtn: "Continuer le questionnaire",
  straight: "Tu as donné presque partout la même réponse : le résultat montre surtout quels partis ont pris position sur ces sujets.",
  thinTitle: "Peu de positions connues sur tes réponses",
  thinText: "Ces partis ont une position documentée sur moins de 40 % de tes réponses. Leur pourcentage est peu fiable : ils ne sont pas classés.",
  themeThin: "Trop peu de positions connues sur tes réponses à ce sujet pour désigner un parti.",
  posTie: "ex æquo à la 1re place",
  confirmLose: n => n > 1 ? `Tes ${n} réponses seront effacées.` : "Ta réponse sera effacée.",
  confirmRestart: "Effacer et recommencer",
  confirmHome: "Effacer et changer de pays",
  resumeText: n => `Tu as déjà répondu à ${n} question${n > 1 ? "s" : ""}.`,
  resumeBtn: "Reprendre",
  mRulesTitle: "Comment lire le classement",
  mRules: [
    "Un parti n’est classé que s’il a une position documentée sur au moins 2 de tes réponses et sur au moins 40 % d’entre elles. Sinon, il apparaît à part (« Peu de positions connues sur tes réponses »), sans rang, et jamais dans le titre.",
    "Les partis à moins de 3 points du premier sont à égalité avec lui : ils partagent la 1re place (« 1= »). À score égal, l’ordre est alphabétique (par sigle), jamais celui de l’édition.",
    "Avec moins de 8 réponses, le résultat n’est qu’un premier aperçu. Si le premier parti est sous 50 %, aucun parti n’est vraiment proche de tes réponses.",
    "Un sujet prioritaire (×2) et une question « compte double » (×2) se cumulent : une telle question pèse 4 fois plus qu’une autre.",
    "Sujet par sujet, les mêmes règles s’appliquent (égalité à 3 points, partis peu documentés signalés), avec au moins 1 réponse au lieu de 2."
  ]
});
Object.assign(T.en, {
  footer2: "Your answers stay on your device, in this tab, and are sent nowhere.",
  mNot: [T.en.mNot[0], T.en.mNot[1], "It sends your answers nowhere: they stay on your device, in this tab."],
  double: "Counts double for me",
  resReady: "Results ready",
  resTie: (ps, pct) => `${ps} are neck and neck (${pct}).`,
  resEarly: (n, who, k) => `First look after ${n} answer${n > 1 ? "s" : ""}: ${who} ${k > 1 ? "lead" : "leads"}.`,
  resFar: (who, pct, k) => `No party is really close to your answers. The least distant: ${who} (${pct}).`,
  resThin: "No party has enough known positions on your answers.",
  resThinText: "Their percentages are shown below as a rough guide, under “Few known positions on your answers”. Answer more questions to get a ranking.",
  earlyText: n => `Answer at least ${n} questions for a solid result.`,
  earlyBtn: "Keep answering",
  straight: "You gave almost the same answer everywhere, so the result mostly shows which parties took positions on these issues.",
  thinTitle: "Few known positions on your answers",
  thinText: "These parties have a documented position on fewer than 40% of your answers. Their percentage is unreliable, so they are not ranked.",
  themeThin: "Too few known positions on your answers in this issue to name a party.",
  posTie: "joint first",
  confirmLose: n => n > 1 ? `Your ${n} answers will be erased.` : "Your answer will be erased.",
  confirmRestart: "Erase and start over",
  confirmHome: "Erase and change country",
  resumeText: n => `You have already answered ${n} question${n > 1 ? "s" : ""}.`,
  resumeBtn: "Resume",
  mRulesTitle: "How to read the ranking",
  mRules: [
    "A party is ranked only if it has a documented position on at least 2 of your answers and on at least 40% of them. Otherwise it is listed separately (“Few known positions on your answers”), without a rank, and never in the headline.",
    "Parties within 3 points of the leader are tied with it and share first place (“1=”). Equal scores are listed alphabetically by abbreviation, never in the edition’s order.",
    "With fewer than 8 answers, the result is only a first look. If the leading party is below 50%, no party is really close to your answers.",
    "A priority issue (×2) and a question marked “counts double” (×2) combine: such a question weighs 4 times as much as another.",
    "Issue by issue, the same rules apply (3-point ties, thinly documented parties flagged), with at least 1 answer instead of 2."
  ]
});
Object.assign(T.pt, {
  footer2: "As tuas respostas ficam no teu dispositivo, neste separador, e não são enviadas para lado nenhum.",
  mNot: [T.pt.mNot[0], T.pt.mNot[1], "Não envia as tuas respostas para lado nenhum: ficam no teu dispositivo, neste separador."],
  double: "Conta a dobrar para mim",
  resReady: "Resultados prontos",
  resTie: (ps, pct) => `${ps} estão taco a taco (${pct}).`,
  resEarly: (n, who, k) => `Primeira ideia após ${n} resposta${n > 1 ? "s" : ""}: ${who} à frente.`,
  resFar: (who, pct, k) => `Nenhum partido está realmente próximo das tuas respostas. ${k > 1 ? "Os menos distantes" : "O menos distante"}: ${who} (${pct}).`,
  resThin: "Nenhum partido tem posições conhecidas suficientes nas tuas respostas.",
  resThinText: "As percentagens aparecem mais abaixo, só como indicação, em «Poucas posições conhecidas nas tuas respostas». Responde a mais perguntas para teres uma classificação.",
  earlyText: n => `Responde a pelo menos ${n} perguntas para teres um resultado sólido.`,
  earlyBtn: "Continuar o questionário",
  straight: "Deste quase sempre a mesma resposta: o resultado mostra sobretudo que partidos tomaram posição sobre estes temas.",
  thinTitle: "Poucas posições conhecidas nas tuas respostas",
  thinText: "Estes partidos têm posição documentada em menos de 40% das tuas respostas. A percentagem é pouco fiável, por isso não são classificados.",
  themeThin: "Há demasiado poucas posições conhecidas nas tuas respostas a este tema para indicar um partido.",
  posTie: "empatado em 1.º lugar",
  confirmLose: n => n > 1 ? `As tuas ${n} respostas vão ser apagadas.` : "A tua resposta vai ser apagada.",
  confirmRestart: "Apagar e recomeçar",
  confirmHome: "Apagar e mudar de país",
  resumeText: n => `Já respondeste a ${n} pergunta${n > 1 ? "s" : ""}.`,
  resumeBtn: "Retomar",
  mRulesTitle: "Como ler a classificação",
  mRules: [
    "Um partido só é classificado se tiver posição documentada em pelo menos 2 das tuas respostas e em pelo menos 40% delas. Caso contrário, aparece à parte («Poucas posições conhecidas nas tuas respostas»), sem lugar, e nunca no título.",
    "Os partidos a menos de 3 pontos do primeiro ficam empatados com ele e partilham o 1.º lugar («1=»). Em caso de igualdade, a ordem é alfabética (pela sigla), nunca a da edição.",
    "Com menos de 8 respostas, o resultado é só uma primeira ideia. Se o primeiro partido estiver abaixo dos 50%, nenhum partido está realmente próximo das tuas respostas.",
    "Um tema prioritário (×2) e uma pergunta marcada «conta a dobrar» (×2) acumulam-se: essa pergunta pesa 4 vezes mais do que outra.",
    "Tema a tema, aplicam-se as mesmas regras (empate a 3 pontos, partidos pouco documentados assinalados), com pelo menos 1 resposta em vez de 2."
  ]
});
Object.assign(T.sw, {
  footer2: "Majibu yako yanabaki kwenye kifaa chako, katika kichupo hiki, na hayatumwi popote.",
  mNot: [T.sw.mNot[0], T.sw.mNot[1], "Halitumi majibu yako popote: yanabaki kwenye kifaa chako, katika kichupo hiki."],
  double: "Inahesabiwa mara mbili kwangu",
  resReady: "Matokeo yako tayari",
  resTie: (ps, pct) => `${ps} vinakaribiana sana (${pct}).`,
  resEarly: (n, who, k) => `Mtazamo wa kwanza baada ya ${swN(n, "jibu", "majibu")}: ${k > 1 ? "vinavyoongoza ni" : "kinachoongoza ni"} ${who}.`,
  resFar: (who, pct, k) => `Hakuna chama kilicho karibu kweli na majibu yako. ${k > 1 ? "Vilivyo karibu zaidi" : "Kilicho karibu zaidi"}: ${who} (${pct}).`,
  resThin: "Hakuna chama chenye misimamo ya kutosha inayojulikana kwenye majibu yako.",
  resThinText: "Asilimia zao ziko hapa chini kama makadirio tu, chini ya «Misimamo michache inayojulikana kwenye majibu yako». Jibu maswali zaidi ili upate mpangilio.",
  earlyText: n => `Jibu angalau maswali ${n} ili upate matokeo ya kuaminika.`,
  earlyBtn: "Endelea kujibu",
  straight: "Umetoa karibu jibu lilelile kila mahali, kwa hiyo matokeo yanaonyesha zaidi ni vyama gani vilivyochukua msimamo kuhusu masuala haya.",
  thinTitle: "Misimamo michache inayojulikana kwenye majibu yako",
  thinText: "Vyama hivi vina msimamo uliorekodiwa kwa chini ya asilimia 40 ya majibu yako. Asilimia yao si ya kuaminika, kwa hiyo havijapangwa.",
  themeThin: "Misimamo inayojulikana kwenye majibu yako ya suala hili ni michache mno kuweza kutaja chama.",
  posTie: "sawa katika nafasi ya kwanza",
  confirmLose: n => n > 1 ? `Majibu yako ${n} yatafutwa.` : "Jibu lako litafutwa.",
  confirmRestart: "Futa na uanze upya",
  confirmHome: "Futa na ubadilishe nchi",
  resumeText: n => `Tayari umejibu ${swN(n, "swali", "maswali")}.`,
  resumeBtn: "Endelea ulipoishia",
  mRulesTitle: "Jinsi ya kusoma mpangilio",
  mRules: [
    "Chama kinapangwa tu kikiwa na msimamo uliorekodiwa kwa angalau majibu yako 2 na kwa angalau asilimia 40 ya majibu hayo. La sivyo, kinaonyeshwa kando («Misimamo michache inayojulikana kwenye majibu yako»), bila nafasi, na hakitajwi kamwe kwenye kichwa cha matokeo.",
    "Vyama vilivyo ndani ya pointi 3 kutoka cha kwanza vinalingana nacho na vinashiriki nafasi ya kwanza («1=»). Alama zikiwa sawa, mpangilio ni wa kialfabeti (kwa kifupisho), si ule wa toleo.",
    "Ukiwa na majibu chini ya 8, matokeo ni mtazamo wa kwanza tu. Chama cha kwanza kikiwa chini ya asilimia 50, hakuna chama kilicho karibu kweli na majibu yako.",
    "Suala la kipaumbele (×2) na swali lenye alama «mara mbili» (×2) vinajumlishwa: swali kama hilo lina uzito mara 4 zaidi ya jingine.",
    "Kwa kila suala, kanuni hizo hizo zinatumika (kulingana ndani ya pointi 3, vyama vyenye taarifa chache vinawekewa alama), kwa angalau jibu 1 badala ya 2."
  ],
  // Pluriels
  nQ: n => swN(n, "swali", "maswali"),
  chosen: n => n === 0 ? "Hakuna suala lililochaguliwa · hadi 3" : n === 1 ? "Suala 1 kati ya 3 limechaguliwa" : `Masuala ${n} kati ya 3 yamechaguliwa`,
  resSummary: (a, n, pr) => `Imehesabiwa kwa ${swN(a, "jibu", "majibu")} (kati ya maswali ${n}). Masuala ya kipaumbele: ${pr}.`,
  compared: (k, a) => `Imelinganishwa kwa ${swN(k, "jibu", "majibu")} kati ya ${a}`,
  themeVerdict: (t, p, pct, k) => `Kama «${t}» ni muhimu kwako, kilicho karibu zaidi ni <b>${p}</b> (${pct}, kwa ${swN(k, "swali", "maswali")}).`,
  ficheDoc: (k, n) => `Misimamo iliyorekodiwa: ${swN(k, "swali", "maswali")} kati ya ${n}`
});
Object.assign(T.ar, {
  footer2: "تبقى إجاباتك على جهازك، في علامة التبويب هذه، ولا تُرسَل إلى أي مكان.",
  mNot: [T.ar.mNot[0], T.ar.mNot[1], "لا ترسل إجاباتك إلى أي مكان: تبقى على جهازك، في علامة التبويب هذه."],
  double: "يُحتسب مضاعفًا بالنسبة إليّ",
  resReady: "النتائج جاهزة",
  resTie: (ps, pct) => `تقارب شديد بين ${ps} (${pct}).`,
  resEarly: (n, who, k) => `نظرة أولى بعد ${arN(n, AR_ANS_GEN)}: ${who} في المقدمة.`,
  resFar: (who, pct, k) => `لا يوجد حزب قريب حقًا من إجاباتك. الأقل ابتعادًا: ${who} (${pct}).`,
  resThin: "لا يوجد حزب لديه ما يكفي من المواقف المعروفة في إجاباتك.",
  resThinText: "تظهر نسبها أدناه على سبيل الاستئناس، تحت «مواقف معروفة قليلة في إجاباتك». أجب عن أسئلة أخرى للحصول على ترتيب.",
  earlyText: n => `أجب عن ${arN(n, AR_Q_GEN)} على الأقل للحصول على نتيجة متينة.`,
  earlyBtn: "تابع الإجابة",
  straight: "قدّمت الإجابة نفسها تقريبًا في كل مكان، لذا تُظهر النتيجة أساسًا الأحزاب التي اتخذت مواقف من هذه القضايا.",
  thinTitle: "مواقف معروفة قليلة في إجاباتك",
  thinText: "لهذه الأحزاب موقف موثّق في أقل من 40% من إجاباتك. نسبتها غير موثوقة، لذا لا تدخل في الترتيب.",
  themeThin: "المواقف المعروفة في إجاباتك عن هذه القضية أقل من أن تسمح بتسمية حزب.",
  posTie: "متعادل في المركز الأول",
  confirmLose: n => `ستُحذف إجاباتك (${n}).`,
  confirmRestart: "احذف وابدأ من جديد",
  confirmHome: "احذف وغيّر البلد",
  resumeText: n => `أجبت حتى الآن عن ${arN(n, AR_Q_GEN)}.`,
  resumeBtn: "تابع من حيث توقفت",
  mRulesTitle: "كيف تقرأ الترتيب",
  mRules: [
    "لا يدخل الحزب في الترتيب إلا إذا كان له موقف موثّق في إجابتين على الأقل من إجاباتك، وفي 40% منها على الأقل. وإلا فإنه يظهر على حدة («مواقف معروفة قليلة في إجاباتك») دون رتبة، ولا يُذكر أبدًا في العنوان.",
    "الأحزاب التي يقل فارقها عن الأول عن 3 نقاط متعادلة معه وتتقاسم المركز الأول («1=»). وعند تساوي النتائج يكون الترتيب أبجديًا بحسب الاختصار، لا بحسب ترتيب النسخة.",
    "مع أقل من 8 إجابات، لا تكون النتيجة إلا نظرة أولى. وإذا كان الحزب الأول دون 50%، فلا يوجد حزب قريب حقًا من إجاباتك.",
    "تتراكم القضية ذات الأولوية (×2) وعلامة «مضاعف» (×2): فيزن مثل هذا السؤال 4 أضعاف سؤال آخر.",
    "في كل قضية على حدة تنطبق القواعد نفسها (التعادل ضمن 3 نقاط، والإشارة إلى الأحزاب قليلة التوثيق)، مع إجابة واحدة على الأقل بدلًا من اثنتين."
  ],
  // Pluriels
  nQ: n => arN(n, AR_Q_NOM),
  nCountries: n => arN(n, AR_COUNTRY),
  resSummary: (a, n, pr) => `محسوبة على ${arN(a, AR_ANS_GEN)} (من أصل ${arN(n, AR_Q_GEN)}). القضايا ذات الأولوية: ${pr}.`,
  themeVerdict: (t, p, pct, k) => `إذا كانت «${t}» مهمة لك، فالأقرب هو <b>${p}</b> (${pct}، على ${arN(k, AR_Q_GEN)}).`
});

/* ================== Version 2, suite : carte, écran de question d'une main, libellés, recherche ==================
   Lien d'évitement, accroche et slogan, légende, liste des questions, réponses « ni d'accord ni pas d'accord »,
   états des sujets, langues non traduites. */
Object.assign(T.fr, {
  skipList: "Aller à la liste des pays",
  heroKicker: n => `Élections en Afrique · ${n} pays à explorer`,
  tagline: "Anonyme · Sources publiques · On ne te dit pas pour qui voter",
  legNone: "Pas d’élection nationale avant fin 2027",
  noCountry: "Aucun pays ne correspond.",
  qList: "Questions",
  qJumpTitle: "Aller à une question",
  qStateDone: "répondue",
  qStateSkip: "passée",
  qStateOpen: "pas encore répondue",
  startHint: "Choisis au moins un sujet",
  ans: { "2": "Tout à fait d’accord", "1": "Plutôt d’accord", "0": "Ni d’accord ni pas d’accord", "-1": "Plutôt pas d’accord", "-2": "Pas du tout d’accord" },
  ansShort: { "2": "D’accord ++", "1": "D’accord", "0": "Ni l’un ni l’autre", "-1": "Pas d’accord", "-2": "Pas d’accord ++" },
  themeSkipped: "Tu as passé les questions de ce sujet.",
  langWhy: "Pas encore traduit"
});
Object.assign(T.en, {
  skipList: "Skip to the list of countries",
  heroKicker: n => `Elections in Africa · ${n} countries to explore`,
  tagline: "Anonymous · Public sources · We don’t tell you who to vote for",
  legNone: "No national election before end of 2027",
  noCountry: "No country matches.",
  qList: "Questions",
  qJumpTitle: "Jump to a question",
  qStateDone: "answered",
  qStateSkip: "skipped",
  qStateOpen: "not answered yet",
  startHint: "Choose at least one issue",
  ans: { "2": "Strongly agree", "1": "Agree", "0": "Neither agree nor disagree", "-1": "Disagree", "-2": "Strongly disagree" },
  ansShort: { "2": "Strongly agree", "1": "Agree", "0": "Neither", "-1": "Disagree", "-2": "Strongly disagree" },
  themeSkipped: "You skipped this issue’s questions.",
  langWhy: "Not translated yet"
});
Object.assign(T.pt, {
  skipList: "Ir para a lista de países",
  heroKicker: n => `Eleições em África · ${n} países para explorar`,
  tagline: "Anónimo · Fontes públicas · Não te dizemos em quem votar",
  legNone: "Sem eleição nacional antes do fim de 2027",
  noCountry: "Nenhum país corresponde.",
  qList: "Perguntas",
  qJumpTitle: "Ir para uma pergunta",
  qStateDone: "respondida",
  qStateSkip: "saltada",
  qStateOpen: "ainda por responder",
  startHint: "Escolhe pelo menos um tema",
  ans: { "2": "Concordo totalmente", "1": "Concordo", "0": "Nem concordo nem discordo", "-1": "Discordo", "-2": "Discordo totalmente" },
  ansShort: { "2": "Concordo muito", "1": "Concordo", "0": "Nem um nem outro", "-1": "Discordo", "-2": "Discordo muito" },
  themeSkipped: "Saltaste as perguntas deste tema.",
  langWhy: "Ainda não traduzido"
});
Object.assign(T.sw, {
  skipList: "Nenda kwenye orodha ya nchi",
  heroKicker: n => `Uchaguzi barani Afrika · nchi ${n} za kuchunguza`,
  tagline: "Bila kujulikana · Vyanzo vya umma · Hatukuambii umpigie nani kura",
  legNone: "Hakuna uchaguzi wa kitaifa kabla ya mwisho wa 2027",
  noCountry: "Hakuna nchi inayolingana.",
  qList: "Maswali",
  qJumpTitle: "Nenda kwenye swali",
  qStateDone: "imejibiwa",
  qStateSkip: "imerukwa",
  qStateOpen: "bado haijajibiwa",
  startHint: "Chagua angalau suala moja",
  ans: { "2": "Nakubali kabisa", "1": "Nakubali", "0": "Sikubali wala sikatai", "-1": "Sikubali", "-2": "Sikubali kabisa" },
  ansShort: { "2": "Nakubali sana", "1": "Nakubali", "0": "Kati na kati", "-1": "Sikubali", "-2": "Sikubali kabisa" },
  themeSkipped: "Umeruka maswali ya suala hili.",
  langWhy: "Bado haijatafsiriwa"
});
Object.assign(T.ar, {
  skipList: "انتقل إلى قائمة البلدان",
  heroKicker: n => `انتخابات في أفريقيا · ${arN(n, AR_COUNTRY)} للاستكشاف`,
  tagline: "مجهول الهوية · مصادر عامة · لا نقول لك لمن تصوّت",
  legNone: "لا انتخابات وطنية قبل نهاية 2027",
  noCountry: "لا يوجد بلد مطابق.",
  qList: "الأسئلة",
  qJumpTitle: "انتقل إلى سؤال",
  qStateDone: "تمت الإجابة",
  qStateSkip: "تم التخطي",
  qStateOpen: "لم تتم الإجابة بعد",
  startHint: "اختر قضية واحدة على الأقل",
  ans: { "2": "موافق تمامًا", "1": "موافق", "0": "لا أوافق ولا أعارض", "-1": "غير موافق", "-2": "غير موافق إطلاقًا" },
  ansShort: { "2": "موافق بشدة", "1": "موافق", "0": "لا هذا ولا ذاك", "-1": "غير موافق", "-2": "غير موافق بشدة" },
  themeSkipped: "تخطّيت أسئلة هذه القضية.",
  langWhy: "لم تُترجم بعد"
});
