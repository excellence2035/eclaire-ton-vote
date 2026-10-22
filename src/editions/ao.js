/* Format: src/EDITION_SPEC.md. Angola edition, base language English, researched up to 18 October 2026. Notes: src/notes/ao.md
   STATUS: INFO page written because research was cut off (WebFetch session limit on 18 Oct 2026). The target is a full ED_AO questionnaire: see the notes for the verified draft coding and what is missing. */
const SRC_AO = {
  plataforma: { o: "Plataforma Media", t: "Angola vai a eleições em 2027 e prepara sucessão de João Lourenço", d: "24 Aug 2026", u: "https://www.plataformamedia.com/2026/08/24/angola-vai-a-eleicoes-em-2027-e-prepara-sucessao-de-joao-lourenco/" },
  const_rev: { o: "Lex.ao", t: "Lei n.º 18/21, de 16 de Agosto (Lei de Revisão Constitucional)", d: "16 Aug 2021", u: "https://lex.ao/docs/assembleia-nacional/2021/lei-n-o-18-21-de-16-de-agosto/" },
  conv_system: { o: "The Conversation", t: "Angola’s peculiar electoral system needs reforms. How it could be done", d: "2021", u: "https://theconversation.com/angolas-peculiar-electoral-system-needs-reforms-how-it-could-be-done-163528" },
  eguide: { o: "IFES ElectionGuide", t: "Angola: National Assembly general election, 24 August 2022", d: "2022", u: "https://electionguide.org/elections/id/3954/" },
  dpa: { o: "Forbes África Lusófona", t: "Parlamento angolano aprova na globalidade divisão administrativa mas UNITA exige autarquias", d: "15 Aug 2024", u: "https://forbesafricalusofona.com/?p=107406" },
  registo: { o: "ANGOP (via AllAfrica)", t: "Angola: Over 16 Million Citizens Expected to Update Voter Registration", d: "15 Jun 2026", u: "https://allafrica.com/stories/202606160634.html" },
  jumartins: { o: "Expansão", t: "Jú Martins oficializa recandidatura de João Lourenço e avisa: ser candidato do MPLA à Presidência da República “não é para quem quer”", d: "11 May 2026", u: "https://expansao.co.ao/angola/detalhe/ju-martins-oficializa-recandidatura-de-joao-lourenco-e-avisa-ser-candidato-do-mpla-a-presidencia-da-republica-nao-e-para-quem-quer-71740.html" },
  subsidy26: { o: "Forbes África Lusófona", t: "Retirada dos subsídios aos combustíveis deverá aliviar contas públicas angolanas em 2,6 biliões kz", d: "17 Dec 2025", u: "https://forbesafricalusofona.com/?p=166705" },
  unita_front: { o: "Ver Angola", t: "UNITA approves new patriotic front heading towards the 2027 elections", d: "Dec 2025", u: "https://www.verangola.net/va/en/122025/Politics/46954/UNITA-approves-new-patriotic-front-heading-towards-the-2027-elections.htm" },
  fpu_2026: { o: "Ver Angola", t: "The Patriotic Front is moving forward in the 2027 elections seeking a change in power", d: "Sep 2026", u: "https://www.verangola.net/va/en/02026/Politics/50054/The-Patriotic-Front-is-moving-forward-in-the-2027-elections-seeking-a-change-in-power.htm" },
  praja_rtp: { o: "RTP (Lusa)", t: "PRA-JA Servir Angola aceita coligação em 2027 mas “nunca agregação” – Chivukuvuku", d: "22 May 2025", u: "https://www.rtp.pt/noticias/mundo/pra-ja-servir-angola-aceita-coligacao-em-2027-mas-nunca-agregacao-chivukuvuku_n1656844" },
  elec_package: { o: "Forbes África Lusófona", t: "Parlamento angolano aprova pacote legislativo eleitoral", d: "14 Aug 2025", u: "https://forbesafricalusofona.com/?p=160990" },
  elec_law: { o: "Expansão", t: "MPLA e UNITA chegam a um consenso em alguns pontos da Lei Eleitoral", d: "5 Aug 2025", u: "https://expansao.co.ao/angola/detalhe/mpla-e-unita-chegam-a-um-consenso-em-alguns-pontos-da-lei-eleitoral-66663.html" },
  protests: { o: "Al Jazeera", t: "At least 22 killed at Angola fuel price hike protests, authorities say", d: "30 Jul 2025", u: "https://www.aljazeera.com/news/2025/7/30/at-least-22-killed-at-angola-fuel-price-hike-protests-authorities-say" },
  unita_riots: { o: "RTP (Lusa)", t: "UNITA diz que balanço dos tumultos em Angola é superior ao divulgado pelo Governo", d: "9 Aug 2025", u: "https://www.rtp.pt/noticias/mundo/unita-diz-que-balanco-dos-tumultos-em-angola-e-superior-ao-divulgado-pelo-governo_n1675316" },
  autarq26: { o: "Expansão", t: "Futuro das Autarquias continua pendurado nas comissões de especialidade", d: "17 Aug 2026", u: "https://expansao.co.ao/angola/detalhe/futuro-das-autarquias-continua-pendurado-nas-comissoes-de-especialidade-73988.html" }
};

const META_AO = { ev: [{ t: "general", d: "2027-08", q: "month" }], src: "plataforma" };

const INFO_AO = {
  id: "ao", name: "Angola", lang: "en",
  strip: "General election 2027",
  stripDate: "August 2027 (exact date not yet set)",
  facts: [
    ["General election (President + 220 MPs)", "Expected Aug 2027, date not set"],
    ["Voter register update", "15 Jun 2026 – 31 Mar 2027"],
    ["MPLA congress (party leader)", "9–10 Dec 2026"]
  ],
  factsSrc: ["plataforma", "registo", "jumartins"],
  system: [
    ["Political system", "Presidential republic: the President is head of state and of the government. President João Lourenço (MPLA), elected in 2017 and re-elected in 2022, cannot run again, because the Constitution bars presidents who have served two terms."],
    ["One ballot for President and parliament", "There is no separate presidential vote. Each voter makes a single mark for a party or coalition list. The first name on the winning list becomes President and the second becomes Vice-President. There is no run-off."],
    ["National Assembly", "220 deputies are elected for five years by closed-list proportional representation: 130 on a national list and 90 in provincial constituencies (five per province in 2022, when Angola had 18 provinces). A 2024 law raised the number of provinces to 21; the sources found do not say how provincial seats will be allocated in 2027."],
    ["Date and voters", "Under the Constitution as revised in 2021, general elections take place preferably in the second half of August of the year the mandates end, on a date set by the President after consulting the National Electoral Commission (CNE) and the Council of the Republic. As of late August 2026 the date had not been officially set. Citizens aged 18 and over can vote, including Angolans abroad; a national update of the voter register runs from 15 June 2026 to 31 March 2027."],
    ["Electoral rules for 2027", "In August 2025 parliament passed a new electoral package (general elections law, CNE law and voter registry law) with the votes of the MPLA, UNITA, PRS, FNLA and PHA. The voter card stays valid alongside the identity card in 2027 and results will be published by municipality on the CNE website. UNITA’s proposals for more broadcast airtime per candidacy and for state funding of national observer groups were rejected by the majority."],
    ["Context", "The MPLA has governed since independence. In 2022 it won 51.17% of the vote (124 seats) against 43.95% (90 seats) for UNITA and its allies, with 55% abstention. In July 2025 a taxi strike against higher diesel prices turned into riots and looting; official figures cited in August 2025 reported 30 deaths and more than 1,500 arrests. Local elections (autarquias) have never been held: the key law has been stuck in parliament for more than two years."]
  ],
  systemSrc: ["const_rev", "conv_system", "eguide", "dpa", "plataforma", "registo", "elec_package", "elec_law", "protests", "unita_riots", "autarq26"],
  actors: [
    ["MPLA · Movimento Popular de Libertação de Angola", "Governing party. Its IX Congress on 9–10 December 2026 will elect the party leader: João Lourenço is standing again, and Higino Carneiro, José Carlos Almeida and António Venâncio announced bids. In the sources found (May–August 2026) the MPLA had not named who will head its list for President in 2027.", "jumartins"],
    ["Government of President João Lourenço (MPLA)", "Has been phasing out fuel subsidies since June 2023, on IMF advice, and expects to save more than 2.6 trillion kwanzas in 2026. Its 2026 State Budget of 33.2 trillion kwanzas was passed in December 2025, with UNITA voting against.", "subsidy26"],
    ["UNITA · União Nacional para a Independência Total de Angola", "Main opposition party, led by Adalberto Costa Júnior, who was re-elected party president at the end of 2025 with 91% of the vote. Its congress resolved to unite Angolans in a “broad patriotic front” to bring about political change in 2027.", "unita_front"],
    ["Frente Patriótica Unida (FPU)", "The opposition platform that won 90 seats in 2022 on UNITA’s lists, with Bloco Democrático and PRA-JA Servir Angola. A UNITA statement reported in September 2026 says the front is moving forward under UNITA’s lead while its former partners pursue their own strategies; it calls for independent, credible international observation of the whole electoral process.", "fpu_2026"],
    ["PRA-JA Servir Angola", "Party of Abel Chivukuvuku, legalised in October 2024. Its first congress (May 2025) authorised it to run alone in 2027 if necessary; Chivukuvuku accepts a “coalition, never a merger” and wants the party to be in government, or part of it, after 2027.", "praja_rtp"],
    ["PRS, FNLA and PHA", "Smaller parties with seats in the National Assembly. All three voted, with the MPLA and UNITA, for the 2025 electoral law package; PRS leader Benedito Daniel said constitutional rules must keep pace with political change, and the PHA said the law brings relevant improvements in transparency.", "elec_package"],
    ["CNE · Comissão Nacional Eleitoral", "Runs the election. Chaired by Manuel Pereira da Silva, it approved the specifications for ballot boxes, voting booths and other materials in June 2026 and briefed the EU ambassador on its preparations in July 2026.", "plataforma"]
  ],
  why: "So far the parties’ positions for this vote have been documented on only a handful of issues (fuel subsidies, the 2026 budget, local elections, the new provinces and the electoral law), too few for a fair comparison. The MPLA will elect its leader on 9–10 December 2026 and had not named the head of its 2027 list, and the shape of the opposition alliance is not settled. A full questionnaire comparing the parties will replace this page once their positions on at least 25 policy questions are documented and sourced."
};
