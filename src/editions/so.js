/* Format: src/EDITION_SPEC.md. Somalia edition, base language English, researched up to 16 October 2026. Notes: src/notes/so.md */
const SRC_SO = {
  dawan_dates: { o: "Dawan Africa", t: "Somalia Sets Presidential Vote for 15 May 2027", d: "15 Oct 2026", u: "https://www.dawan.africa/news/somalia-sets-presidential-vote-for-15-may-2027" },
  aj_2027: { o: "Al Jazeera (AFP)", t: "Somalia says it will hold elections in 2027", d: "15 Oct 2026", u: "https://www.aljazeera.com/news/2026/10/15/somalia-says-it-will-hold-elections-in-2027" },
  digest_dates: { o: "The Somali Digest", t: "The Electoral Commission Sets Somalia’s Vote for 15 May 2027 and the Opposition Rejects It", d: "15 Oct 2026", u: "https://thesomalidigest.com/electoral-commission-2027-election-timetable/" },
  garowe_dates: { o: "Garowe Online", t: "Somalia’s 2027 Election Plan Faces Fresh Uncertainty as Opposition Rejects Timetable", d: "15 Oct 2026", u: "https://www.garoweonline.com/en/news/somalia/somalia-s-2027-election-plan-faces-fresh-uncertainty-as-opposition-rejects-timetable" },
  reuters_const: { o: "Citizen Digital (Reuters)", t: "Somali parliament approves constitution change to extend president’s term, delay election", d: "6 Mar 2026", u: "https://citizen.digital/news/somali-parliament-approves-constitution-change-to-extend-presidents-term-delay-election-n378547" },
  standard_sign: { o: "The Standard (Xinhua)", t: "Somalia president signs new constitution into law", d: "Mar 2026", u: "https://standardmedia.co.ke/business/africa/article/2001542645/somalia-president-signs-new-constitution-into-law" },
  acss: { o: "Africa Center for Strategic Studies", t: "Somalia: Electoral Process Under Construction Amid a Security Crisis", d: "26 May 2026", u: "https://africacenter.org/spotlight/en-elections-2026/somalia/" },
  iss_may: { o: "ISS Today", t: "More instability for Somalia as another election deadline lapses", d: "20 May 2026", u: "https://issafrica.org/iss-today/more-instability-for-somalia-as-another-election-deadline-lapses" },
  ea_proposals: { o: "The EastAfrican", t: "Somalia stakeholders table three proposals to resolve political impasse", d: "14 Jul 2026", u: "https://www.theeastafrican.co.ke/tea/news/east-africa/somalia-stakeholders-table-three-proposals-political-impasse-5526762" },
  dalsan_op: { o: "Radio Dalsan (via AllAfrica), opinion by a federal MP", t: "Somalia’s Political Crossroads – Reformists Leaders Embraced Universal Suffrage As the Old Guard Rendered to Clan Insurgency", d: "14 Jul 2026", u: "https://allafrica.com/stories/202607160100.html" },
  nova_talks: { o: "Agenzia Nova", t: "Somalia: Government-opposition talks fail, universal suffrage elections go ahead", d: "15 May 2026", u: "https://www.agenzianova.com/en/news/Somalia%3A-Government-opposition-talks-fail--universal-suffrage-elections-go-ahead/" },
  dawan_nodeal: { o: "Dawan Africa", t: "Somalia’s opposition says no election deal reached with government", d: "23 Sep 2026", u: "https://www.dawan.africa/news/somalias-opposition-says-no-election-deal-reached-with-government" },
  sg_collapse: { o: "Somali Guardian", t: "Somalia election talks collapse over constitutional row", d: "23 Feb 2026", u: "https://www.somaliguardian.com/news/somalia-news/somalia-election-talks-collapse-over-constitutional-row/" },
  geeska_timeline: { o: "Geeska", t: "New electoral timeline risks derailing Somalia’s planned election talks", d: "4 May 2026", u: "https://www.geeska.com/en/new-electoral-timeline-risks-derailing-somalias-planned-election-talks" },
  geeska_poll: { o: "Geeska", t: "Somalia’s elections in question as poll body seeks backing", d: "18 Nov 2025", u: "https://www.geeska.com/en/somalias-elections-question-poll-body-seeks-backing" },
  dawan_niebc: { o: "Dawan Africa", t: "Somalia Electoral Commission Briefs Diplomats on One-Person, One-Vote Progress", d: "10 Aug 2026", u: "https://www.dawan.africa/news/somalia-electoral-commission-briefs-diplomats-on-one-person-one-vote-progress" },
  dawan_galmudug: { o: "Dawan Africa", t: "Somalia’s ruling JSP accepts Galmudug vote rerun after Supreme Court annulment", d: "25 Aug 2026", u: "https://www.dawan.africa/news/somalias-ruling-jsp-accepts-galmudug-vote-rerun-after-supreme-court-annulment" },
  ap_mogadishu: { o: "ABC News (AP)", t: "Somalis vote in the first one-person, one-vote local election in decades", d: "Dec 2025", u: "https://abcnews.go.com/amp/International/wireStory/somalis-vote-person-vote-local-election-decades-128690490" },
  sg_alliance: { o: "Somali Guardian", t: "Somalia’s opposition, regional leaders form new alliance", d: "2 Oct 2025", u: "https://www.somaliguardian.com/news/somalia-news/somalias-opposition-regional-leaders-form-new-alliance/" },
  sg_ssf: { o: "Somali Guardian", t: "Somalia’s opposition accuses president of abandoning al-Shabaab war for divisive political agendas", d: "1 Sep 2025", u: "https://www.somaliguardian.com/news/somalia-news/somalias-opposition-accuses-president-of-abandoning-al-shabaab-war-for-divisive-political-agendas/" },
  sg_sharif_shabaab: { o: "Somali Guardian", t: "Al-Shabaab ‘taking over’ Somalia as army disintegrates, warns former president", d: "3 Sep 2025", u: "https://www.somaliguardian.com/news/somalia-news/al-shabaab-taking-over-somalia-as-army-disintegrates-warns-former-president/" },
  sg_evict: { o: "Somali Guardian", t: "Somalia: Opposition calls for mass demonstration over evictions in Mogadishu", d: "8 Oct 2025", u: "https://www.somaliguardian.com/news/somalia-news/somalia-opposition-calls-for-mass-demonstration-over-evictions-in-mogadishu/" },
  sg_jubaland: { o: "Somali Guardian", t: "Somalia’s Jubaland withdraws from federal system, calls itself independent government", d: "8 Dec 2025", u: "https://www.somaliguardian.com/news/somalia-news/somalias-jubaland-withdraws-from-federal-system-calls-itself-independent-government/" },
  geeska_land: { o: "Geeska", t: "Mogadishu’s land reclamation drive exposes deep corruption scandal", d: "6 Nov 2025", u: "https://www.geeska.com/en/mogadishus-land-reclamation-drive-exposes-deep-corruption-scandal" },
  aj_uae: { o: "Al Jazeera", t: "Somalia cancels all agreements with UAE over alleged sovereignty violations", d: "12 Jan 2026", u: "https://www.aljazeera.com/news/2026/1/12/somalia-cancels-all-agreements-with-uae-over-alleged-sovereignty-violations" },
  geeska_uae: { o: "Geeska", t: "Somalia revokes all agreements with UAE", d: "13 Jan 2026", u: "https://www.geeska.com/en/somalia-revokes-all-agreements-uae" },
  newarab_uae: { o: "The New Arab", t: "Somali regions dismiss government decision to sever UAE ties", d: "13 Jan 2026", u: "https://www.newarab.com/news/somali-regions-dismiss-government-decision-sever-uae-ties" },
  aj_somaliland: { o: "Al Jazeera", t: "Somalis rally against Israel’s world-first recognition of Somaliland", d: "30 Dec 2025", u: "https://aljazeera.com/news/2025/12/30/somalis-rally-against-israels-world-first-recognition-of-somaliland" },
  sg_turkey_oil: { o: "Somali Guardian (Nordic Monitor)", t: "Turkey secures rights to 90 percent of oil and gas output in Somalia deal, document shows", d: "24 Apr 2025", u: "https://www.somaliguardian.com/news/somalia-news/turkey-secures-rights-to-90-percent-of-oil-and-gas-output-in-somalia-deal-document-shows/" }
};

const META_SO = {
  ev: [{ t: "legislative", d: "2027-04-15", q: "exact" }, { t: "presidential", d: "2027-05-15", q: "exact" }],
  src: "digest_dates",
  note: "Dates set by the electoral commission on 15 October 2026 without political agreement; the opposition, Puntland and Jubaland reject the process, so whether and where the vote takes place is uncertain."
};

const ED_SO = {
  id: "so", name: "Somalia", lang: "en",
  role: "pres",
  strip: "Federal elections 2027",
  stripDate: "Parliament: Thursday 15 April 2027 · President: Saturday 15 May 2027",
  facts: [
    ["Both houses of parliament", "Thu 15 Apr 2027"],
    ["President (chosen by the new parliament)", "Sat 15 May 2027"],
    ["Forces compared", "5"]
  ],
  factsSrc: ["digest_dates", "aj_2027", "ea_proposals"],
  system: [
    ["Political system", "Federal parliamentary republic. The Federal Parliament has two houses; the 275-seat House of the People and the Upper House elect the president, who appoints the prime minister. Somalia is divided into federal member states. President Hassan Sheikh Mohamud (JSP) was elected by parliament on 15 May 2022."],
    ["From clan selection to one person, one vote", "Until now MPs were chosen indirectly: clan elders named delegates for each seat under the “4.5” clan power-sharing formula, and MPs then elected the president. For 2027 the government wants both houses elected directly, through registered political organisations (57 parties were recognised in early 2026, with a 10% threshold); the new parliament would then elect the president."],
    ["2027 timetable", "The National Independent Electoral and Boundaries Commission (NIEBC), chaired by Abdikarim Ahmed Hassan, announced on 15 October 2026: registration of voters and political organisations 1–22 November 2026, candidate lists due 22 November, provisional voter list 21 January 2027, campaign from 27 February, final register 15 March, parliamentary vote 15 April and presidential vote 15 May 2027."],
    ["A disputed mandate", "In March 2026 parliament adopted a new constitution that lengthens federal terms from four to five years; the opposition boycotted the vote. The government declared a “transition period” in May 2026 and says the president’s term runs to May 2027. The opposition and Puntland say the mandates of parliament and president ended in April and May 2026."],
    ["First direct votes", "Mogadishu elected district councils by one person, one vote on 25 December 2025, the first such poll since 1969. In 2026 the NIEBC organised combined local and state assembly votes in South West, Galmudug and Hirshabelle; the Supreme Court annulled Galmudug’s first results, and the JSP won 67 of 89 seats in the September rerun."],
    ["A contested, partial vote", "Puntland and Jubaland have suspended cooperation with Mogadishu and reject the electoral framework, and al-Shabaab still holds territory in the south and centre. Turkish-led talks with the US, UK, EU and UN ended without a deal. No party has published a 2027 manifesto: this edition compares the governing party’s record with the published positions of the opposition and of Puntland and Jubaland, which are regional governments acting as political forces, not parties."]
  ],
  systemSrc: ["acss", "iss_may", "ea_proposals", "digest_dates", "aj_2027", "reuters_const", "ap_mogadishu", "dawan_galmudug", "sg_jubaland", "garowe_dates"],
  status: "Positions in this edition were coded from government decisions, parliamentary votes and the record of the ruling JSP, and from published statements of the Somali Future Council and its Salvation Forum, of Nabad iyo Nolol, and of the Puntland and Jubaland administrations, up to 16 October 2026. No party has published a manifesto for 2027. The vote is contested: the opposition and two federal member states reject the electoral framework and may not take part, so this comparison rests on records and statements, not on campaign programmes. Positions have not been validated by the parties or by an independent committee.",
  others: [
    "National Unity Council · Omar Abdirashid Sharmarke (opposition group; proposed its own one-person-one-vote model)",
    "Galmudug, Hirshabelle, South West and North East State administrations (take part in the federal process)",
    "and the other registered political organisations"
  ],
  othersSrc: "digest_dates",
  parties: [
    { id: "so_jsp", sigle: "JSP", nom: "Justice and Solidarity Party", cand: "Hassan Sheikh Mohamud", candNote: "Party leader and sitting president. Under the government’s model the new parliament elects the president; the sources found do not report a formal JSP nomination yet.",
      tag: "Governing party",
      col: ["#1F4E9C", "#9CC0F5"],
      commit: [
        ["Direct elections for both houses on 15 April 2027, through registered political organisations", "ea_proposals"],
        ["Adopted a new constitution in March 2026 with five-year terms", "reuters_const"],
        ["Cancelled all agreements with the UAE, including member states’ port and security deals", "geeska_uae"],
        ["Clearing state land in Mogadishu to reopen 52 closed roads", "geeska_land"],
        ["Accepted the Supreme Court’s annulment of the first Galmudug vote", "dawan_galmudug"],
        ["Calls the United States Somalia’s strongest partner against “terrorism”", "aj_2027"]
      ] },
    { id: "so_sfc", sigle: "SFC", nom: "Somali Future Council (Council for the Future of Somalia), including the Somali Salvation Forum", cand: "Sharif Sheikh Ahmed", candNote: "Former president and leader of the Salvation Forum. The Council has no joint candidate and rejects the 2027 timetable.",
      tag: "Opposition coalition (Puntland’s and Jubaland’s leaders are also members)",
      col: ["#6B2C91", "#D2A8EC"],
      commit: [
        ["Rejects the 2027 timetable as “election theft” without political agreement", "digest_dates"],
        ["Proposes direct voting by biometrically registered voters in clan-based seats, not through parties", "ea_proposals"],
        ["Says the president’s mandate expired on 15 May 2026 and rejects the 2026 constitution", "nova_talks"],
        ["Demands a national conference that includes Puntland and Jubaland", "digest_dates"],
        ["Opposes forced evictions and the sale of public land in Mogadishu", "sg_evict"],
        ["Wants the government to refocus on the war against al-Shabaab", "sg_ssf"]
      ] },
    { id: "so_nn", sigle: "NN", nom: "Nabad iyo Nolol (Peace and Life)", cand: "Mohamed Abdullahi Farmaajo", candNote: "Former president (2017–2022) and party leader; no 2027 candidate named.",
      tag: "Opposition",
      col: ["#1B6B3A", "#8FD9A8"],
      commit: [
        ["Calls one person, one vote “the most desirable scheme”, based on the model drawn up in 2018", "ea_proposals"],
        ["Rejects the 2027 timetable as unilateral and warns of rival elections", "digest_dates"],
        ["Wants all factions to agree before any decision on the polls", "aj_2027"]
      ] },
    { id: "so_pl", sigle: "Puntland", nom: "Puntland State of Somalia (administration of President Said Abdullahi Deni)", cand: "Said Abdullahi Deni", candNote: "President of Puntland, a regional government rather than a party, and a founding member of the Somali Future Council.",
      tag: "Federal member state in opposition",
      col: ["#8A4B00", "#F2B36B"],
      commit: [
        ["Stopped recognising President Hassan Sheikh as legitimate after 15 May 2026", "digest_dates"],
        ["Acts as an autonomous government until a national constitution is agreed", "sg_jubaland"],
        ["Rejected Mogadishu’s cancellation of the UAE agreements", "geeska_uae"],
        ["Fights Islamic State fighters with US and partner support", "acss"],
        ["Refused Turkish-mediated talks, saying Türkiye is not impartial", "ea_proposals"]
      ] },
    { id: "so_jl", sigle: "Jubaland", nom: "Jubaland State (administration of President Ahmed Mohamed Islam “Madobe”)", cand: "Ahmed Mohamed Islam “Madobe”", candNote: "President of Jubaland, a regional government rather than a party, and a member of the Somali Future Council.",
      tag: "Federal member state in opposition",
      col: ["#00626E", "#7FD4DE"],
      commit: [
        ["Demands federal recognition of Madobe’s 2024 re-election", "sg_alliance"],
        ["Redefined itself as a “government” outside the federal structure (December 2025)", "sg_jubaland"],
        ["Rejected Mogadishu’s cancellation of the UAE agreements", "newarab_uae"],
        ["Refused Turkish-mediated talks, saying Türkiye is not impartial", "ea_proposals"],
        ["Fought federal forces in December 2024 over who would run local elections", "acss"]
      ] }
  ],
  themes: [
    { id: "gov", name: "Elections & electoral system", min: "National Independent Electoral and Boundaries Commission (NIEBC) · Ministry of Interior, Federal Affairs and Reconciliation" },
    { id: "const", name: "Constitution & mandates", min: "Ministry of Constitutional Affairs · Federal Parliament · Supreme Court" },
    { id: "fed", name: "Federalism & member states", min: "Ministry of Interior, Federal Affairs and Reconciliation · National Consultative Council" },
    { id: "security", name: "Security & al-Shabaab", min: "Ministry of Defence · National Intelligence and Security Agency (NISA) · Ministry of Internal Security" },
    { id: "integrity", name: "Civil liberties & rule of law", min: "Ministry of Justice · Ministry of Internal Security · Somali Police Force" },
    { id: "land", name: "Land, housing & Mogadishu", min: "Banadir Regional Administration · Ministry of Public Works, Reconstruction and Housing" },
    { id: "foreign", name: "Foreign relations & sovereignty", min: "Ministry of Foreign Affairs and International Cooperation" },
    { id: "econ", name: "Ports, oil & resources", min: "Ministry of Petroleum and Mineral Resources · Ministry of Ports and Marine Transport · Ministry of Finance" }
  ],
  questions: [
    /* ---------- Elections & electoral system ---------- */
    { theme: "gov", short: "Vote on the set dates",
      text: "The parliamentary vote (15 April 2027) and the presidential vote (15 May 2027) should go ahead on the dates set by the electoral commission, even without a deal with the opposition.",
      ctx: "On 15 October 2026 the electoral commission (NIEBC) set elections for both houses of parliament on 15 April 2027 and the presidential vote on 15 May 2027, citing a legal rule that polls must be announced 180 days ahead. The government welcomed the calendar as a step towards one person, one vote. Opposition groups say it was set without political agreement and warn of rival elections; Puntland and Jubaland reject the legal framework it rests on.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "digest_dates", n: "Information Minister Abdifatah Qasim Mohamud welcomed the timetable (October 2026): “One person, one vote elections are your right and your country’s future.”" },
        so_sfc: { p: -2, k: "stated", s: "digest_dates", n: "Salvation Forum secretary Mohamed Aden Jimale rejected the timetable the day it was announced, calling it election theft and a seizure of power." },
        so_nn: { p: -2, k: "stated", s: "aj_2027", n: "Farmaajo called the decision a “dangerous threat to Somalia’s statehood and future” and urged agreement among all factions before any decision on the polls (October 2026)." },
        so_pl: { p: -2, k: "stated", s: "digest_dates", n: "Puntland rejects the electoral framework behind the dates and said in February 2026 it could hold its own elections if no national agreement was reached. It had not reacted to the new dates by 15 October." },
        so_jl: { p: -1, k: "stated", s: "digest_dates", n: "Jubaland rejects the 2026 constitutional amendments and the electoral framework built on them; it had not reacted to the new dates by 15 October 2026." }
      } },
    { theme: "gov", short: "Direct vote for MPs",
      text: "Members of parliament should be elected directly by voters (one person, one vote) in 2027, instead of being chosen by clan delegates.",
      ctx: "Somalia’s MPs have so far been selected indirectly: clan elders name delegates for each seat, and the delegates elect the 275 members of the House of the People. The government wants a direct vote in 2027. In mid-2026 the main opposition groups also tabled direct-vote models, but they disagree with the government on seats, parties and who runs the vote. Critics say insecurity makes a nationwide direct vote hard to organise.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "ea_proposals", n: "At the July 2026 talks the government delegation, led by Deputy Prime Minister Salah Jama, proposed direct votes for MPs through registered political organisations." },
        so_sfc: { p: 1, k: "stated", s: "ea_proposals", n: "The Council’s July 2026 model, presented by MP Abdirahman Abdishakur, has biometrically registered voters cast paper ballots, but in clan-based seats." },
        so_nn: { p: 2, k: "stated", s: "ea_proposals", n: "Farmaajo’s team, led by former foreign minister Mohamed Abdirizak, called one person, one vote “the most desirable scheme” (July 2026)." },
        so_pl: { p: 1, k: "stated", s: "digest_dates", n: "Puntland and Jubaland left the federal election talks in July 2026 after their “transitional direct-election model” was rejected." },
        so_jl: { p: 1, k: "stated", s: "digest_dates", n: "Jubaland and Puntland left the federal election talks in July 2026 after their “transitional direct-election model” was rejected." }
      } },
    { theme: "gov", short: "No return to indirect elections",
      text: "Even if a direct vote cannot be held everywhere, Somalia should not fall back on an expanded indirect (clan delegate) election in 2027.",
      ctx: "When talks failed in May 2026, the opposition demanded that the government drop one person, one vote and adopt an expanded indirect system. By October 2026 the Future Council, Farmaajo’s Nabad iyo Nolol and the National Unity Council said there would be “no return to indirect elections”, while still rejecting the government’s model. Supporters of a fallback say it would include areas where voting is impossible; opponents say it would entrench clan bargaining.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "nova_talks", n: "After talks failed in May 2026 the government said direct elections are needed to move beyond the clan-based indirect model." },
        so_sfc: { p: 1, k: "stated", s: "dawan_dates", n: "The Future Council agreed with other opposition groups on “no return to indirect elections” (reported October 2026). In May 2026 it had demanded an expanded indirect system." },
        so_nn: { p: 2, k: "stated", s: "dawan_dates", n: "Nabad iyo Nolol joined the opposition’s commitment to “no return to indirect elections” (reported October 2026)." }
      } },
    { theme: "gov", short: "Parties instead of clan seats",
      text: "Candidates for parliament should run on behalf of registered political parties, rather than for seats reserved to clans.",
      ctx: "Under the government’s model, contenders run under registered political organisations, and the largest become parties that can field presidential candidates. About 57 parties were officially recognised in early 2026, and a party needs 10% of the vote to win seats. The Somali Future Council rejects party-based elections and wants voting in clan-based seats. Supporters of parties say they move politics beyond clan; critics say the clan balance keeps the peace.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "ea_proposals", n: "The government’s model (July 2026) has contenders run under registered political organisations, the largest becoming national parties." },
        so_sfc: { p: -2, k: "stated", s: "ea_proposals", n: "The Council’s model “rejects elections through political parties” and keeps clan-based seat constituencies (July 2026)." },
        so_nn: { p: 1, k: "stated", s: "dalsan_op", n: "Nabad iyo Nolol proposed a proportional representation model, which usually relies on party lists; its full details were not published in the sources found (July 2026)." }
      } },
    { theme: "gov", short: "Mogadishu vote was credible",
      text: "The December 2025 Mogadishu district elections, the first one-person-one-vote poll in the capital since 1969, were a credible step forward.",
      ctx: "On 25 December 2025 voters in Mogadishu’s 16 districts elected 390 district councillors, with more than 900,000 people registered and about 10,000 soldiers securing the vote. The electoral commission says one person, one vote “has been successfully implemented”. Opposition parties called the poll flawed and one-sided, and Mogadishu’s mayor is still appointed.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "ea_proposals", n: "The government cited the December 2025 Mogadishu district polls as proof that direct elections work (July 2026)." },
        so_sfc: { p: -2, k: "stated", s: "sg_collapse", n: "The Council cited the Mogadishu vote as a model of “sham elections”, saying the committee, candidates and outcome were decided in advance (February 2026)." }
      } },
    { theme: "gov", short: "Keep the current commission",
      text: "The current electoral commission (NIEBC) should run the 2027 national elections.",
      ctx: "The NIEBC, chaired by Abdikarim Ahmed Hassan, organised the Mogadishu, South West, Galmudug and Hirshabelle polls and set the 2027 dates. The opposition says its members were picked by the government and wants agreement on its mandate and composition. In August 2026 the Supreme Court annulled Galmudug’s first results for breaching the constitution and the electoral law, and the commission organised a rerun.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "dawan_galmudug", n: "After the Galmudug annulment (August 2026) JSP leaders, including the president, agreed to support fresh polls organised by the commission." },
        so_sfc: { p: -2, k: "stated", s: "sg_ssf", n: "The Salvation Forum criticised the creation of the new commission and warned against an “election of gun and abduction” without consensus on its mandate and composition (2025)." }
      } },

    /* ---------- Constitution & mandates ---------- */
    { theme: "const", short: "Five-year terms",
      text: "Parliament was right to extend the terms of the president and MPs from four to five years in the 2026 constitution.",
      ctx: "In March 2026, 222 of 329 MPs and senators approved by acclamation a constitution that lengthens federal terms from four to five years, pushing elections back by a year. The government says the president’s term now runs to May 2027, counted from his swearing-in. The opposition boycotted the vote and says the mandates of parliament and president ended in April and May 2026.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "reuters_const", n: "President Hassan Sheikh (March 2026): “Today is a historic day for it is the official completion of the constitution which had dragged for a long period.”" },
        so_sfc: { p: -2, k: "stated", s: "nova_talks", n: "The Council does not recognise the amendments and says the president’s term expired on 15 May 2026 (May 2026)." },
        so_pl: { p: -2, k: "stated", s: "digest_dates", n: "Puntland’s cabinet said on 21 May 2026 that it no longer recognised President Hassan Sheikh, whose term it says ended on 15 May; parliament’s ended on 14 April." },
        so_jl: { p: -2, k: "stated", s: "digest_dates", n: "Jubaland rejects the constitutional amendments, including the term extension." }
      } },
    { theme: "const", short: "Keep the 2026 constitution",
      text: "The constitution adopted in 2026 should stay in force, rather than be renegotiated with the opposition and the member states.",
      ctx: "The 2012 provisional constitution was meant to be finalised by agreement among Somalia’s political forces. Parliament adopted a new text in March 2026 and the president signed it into law. Puntland and Jubaland reject the changes, and the opposition wants them reversed. On 12 October 2026 the Supreme Court accepted a legal challenge to the new constitution.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "reuters_const", n: "Hassan Sheikh called the vote “the official completion of the constitution” (March 2026)." },
        so_sfc: { p: -2, k: "stated", s: "sg_collapse", n: "The Council says constitutional amendments made unilaterally should not be cited in talks or implemented (February 2026)." },
        so_pl: { p: -2, k: "record", s: "sg_jubaland", n: "Puntland cut relations with Mogadishu and acts as an autonomous government until a unified national constitution is agreed." },
        so_jl: { p: -2, k: "record", s: "sg_jubaland", n: "In December 2025 Jubaland’s parliament amended the regional constitution to call Jubaland a “government” rather than a federal member state." }
      } },
    { theme: "const", short: "A national conference first",
      text: "A national conference including Puntland and Jubaland should agree on the electoral rules before any national vote is held.",
      ctx: "Somalia’s past elections were held under rules agreed by the federal government and the member states. The opposition and Puntland call for a national consultative meeting before any vote. The government held several rounds of talks with the Future Council, the latest mediated by Türkiye with the US, UK, EU and UN, but went ahead with its own timetable when no deal was reached.",
      cells: {
        so_jsp: { p: -1, k: "record", s: "sg_collapse", n: "After talks with the Future Council collapsed in February 2026, the government said it would proceed with its plans regardless of objections." },
        so_sfc: { p: 2, k: "stated", s: "digest_dates", n: "The Salvation Forum’s August 2025 demands include a national conference that includes Puntland and Jubaland." },
        so_nn: { p: 2, k: "stated", s: "aj_2027", n: "Farmaajo urged agreement among all factions before any decision on the polls (October 2026)." },
        so_pl: { p: 2, k: "stated", s: "digest_dates", n: "Puntland’s cabinet called for a national consultative meeting in May 2026." }
      } },

    /* ---------- Federalism & member states ---------- */
    { theme: "fed", short: "States run their own polls",
      text: "Each federal member state should organise its own state elections under its own constitution, rather than leave this to the national electoral commission.",
      ctx: "In 2026 the national electoral commission organised combined local and state assembly elections in South West, Galmudug and Hirshabelle, and scheduled local polls in Gedo and in the new North East State. Jubaland re-elected its president in 2024 under its own rules, a vote Mogadishu has not recognised. The 2012 constitution leaves the division of electoral powers unclear.",
      cells: {
        so_jsp: { p: -2, k: "record", s: "geeska_timeline", n: "The federal electoral commission scheduled state and local elections in South West, Hirshabelle, Galmudug, Banadir, Gedo and the North East State (May 2026)." },
        so_sfc: { p: 2, k: "stated", s: "sg_collapse", n: "The Council says elections in the regional states should follow the provisional federal constitution and the regional constitutions (February 2026)." },
        so_pl: { p: 1, k: "stated", s: "digest_dates", n: "Puntland said in February 2026 that it could hold its own elections if no national agreement was reached." },
        so_jl: { p: 2, k: "record", s: "acss", n: "In December 2024 Jubaland’s forces clashed with federal troops over who would administer district-level elections; dozens of soldiers were killed." }
      } },
    { theme: "fed", short: "Recognise Jubaland’s leader",
      text: "The federal government should recognise Ahmed Madobe’s 2024 re-election as president of Jubaland.",
      ctx: "Ahmed Madobe was re-elected by Jubaland’s parliament in 2024 in a process Mogadishu rejected. He refuses to meet the president unless the federal government recognises his re-election and his administration. Recognition would ease relations with Jubaland; the government argues the vote did not follow the agreed rules.",
      cells: {
        so_jl: { p: 2, k: "stated", s: "sg_alliance", n: "Madobe refuses to meet the president unless Mogadishu formally recognises his 2024 re-election and his administration (October 2025)." },
        so_jsp: { p: -2, k: "record", s: "sg_alliance", n: "The federal government has so far declined to recognise Madobe’s re-election (October 2025)." }
      } },
    { theme: "fed", short: "Federal-run polls in Gedo",
      text: "The federal government should organise elections in Gedo region itself, separately from the Jubaland administration in Kismayo.",
      ctx: "Gedo is part of Jubaland but its control is disputed between Kismayo and Mogadishu, and federal and Jubaland forces have been deployed there. In May 2026 the federal electoral commission scheduled local elections in Gedo separately from the rest of Jubaland, a move analysts called provocative. Supporters say it brings voting to Gedo’s residents; critics say it splits a member state without its consent.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "geeska_timeline", n: "The federal electoral commission listed Gedo for local council elections on 30 July 2026, apart from the Jubaland administration." }
      } },
    { theme: "fed", short: "States step back from the federation",
      text: "Puntland and Jubaland are right to act as autonomous governments until a national constitution is agreed.",
      ctx: "Puntland cut relations with Mogadishu in 2024 after constitutional amendments and says it will act alone until a national constitution is agreed. In December 2025 Jubaland’s parliament renamed the region a “government” rather than a federal member state. The federal government says the states seek unchecked autonomy; the states accuse Mogadishu of centralising power.",
      cells: {
        so_pl: { p: 2, k: "record", s: "sg_jubaland", n: "Puntland operates as an autonomous government until Somalia agrees on a unified constitution." },
        so_jl: { p: 2, k: "record", s: "sg_jubaland", n: "Jubaland declared itself a “government” and withdrew from the federal structure (December 2025)." },
        so_jsp: { p: -2, k: "record", s: "sg_jubaland", n: "The federal government argues that the states seek unchecked autonomy." }
      } },

    /* ---------- Security & al-Shabaab ---------- */
    { theme: "security", short: "Safe enough to vote nationwide",
      text: "Security is good enough to hold a nationwide one-person-one-vote election in 2027.",
      ctx: "Al-Shabaab still holds territory in southern and central Somalia, and a 2025 offensive reversed some government gains. The Mogadishu vote in December 2025 needed about 10,000 soldiers. The government says al-Shabaab has no presence in the major cities; critics say a direct vote would expose candidates and voters to attacks and leave out insecure areas.",
      cells: {
        so_jsp: { p: 2, k: "stated", s: "aj_2027", n: "Hassan Sheikh (October 2026) said al-Shabaab has no presence in the major cities and is unlikely to take control of Somalia, while acknowledging serious security challenges." },
        so_sfc: { p: -2, k: "stated", s: "sg_sharif_shabaab", n: "Sharif Sheikh Ahmed (September 2025): “The country has been captured by Al-Shabaab, it is taking over and the army has disintegrated.”" },
        so_pl: { p: -1, k: "party", s: "sg_alliance", n: "Deni co-founded the Council (October 2025), which opposes the push for nationwide one person, one vote, an approach critics call “unfeasible under current security and political conditions”." },
        so_jl: { p: -1, k: "party", s: "sg_alliance", n: "Madobe co-founded the Council (October 2025), which opposes the push for nationwide one person, one vote, an approach critics call “unfeasible under current security and political conditions”." }
      } },
    { theme: "security", short: "War first, reforms later",
      text: "The government should concentrate on the war against al-Shabaab before pushing ahead with electoral and constitutional reforms.",
      ctx: "The opposition accuses the government of neglecting the fight against al-Shabaab for elections, constitutional change and land deals, and says the group is retaking towns. The government is pressing on with direct elections and says al-Shabaab is unlikely to take over the country.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "sg_ssf", n: "The Salvation Forum (August 2025): “The government must prioritise the security and safety of its citizens over controversial and unilateral political undertakings.”" },
        so_jsp: { p: -1, k: "stated", s: "aj_2027", n: "Hassan Sheikh (October 2026) says al-Shabaab is unlikely to take control of Somalia, as his government presses on with the 2027 elections." }
      } },
    { theme: "security", short: "Rely on foreign partners",
      text: "Somalia should keep relying on foreign partners, such as the United States and Türkiye, for support and training against armed groups.",
      ctx: "About 11,000 African Union (AUSSOM) troops are deployed, and Egypt has offered more. Türkiye trains Somali forces at its TURKSOM base and has a defence and naval agreement with Mogadishu. Puntland fights Islamic State fighters with US support. Supporters say Somali forces cannot yet hold ground alone; critics fear dependence on outside powers with their own interests.",
      cells: {
        so_jsp: { p: 2, k: "stated", s: "aj_2027", n: "Hassan Sheikh (October 2026) called the United States Somalia’s strongest partner in the fight against “terrorism”." },
        so_pl: { p: 1, k: "record", s: "acss", n: "Puntland fights Islamic State in its territory with support from the United States and other partners." }
      } },

    /* ---------- Civil liberties & rule of law ---------- */
    { theme: "integrity", short: "Keep the army out of politics",
      text: "The army and the intelligence agency (NISA) should never be deployed against opposition leaders or their supporters.",
      ctx: "On 10 October 2026 federal troops were deployed around the Mogadishu homes of former President Sharif Sheikh Ahmed and former Prime Minister Hassan Ali Khaire; NISA accused Sharif’s guards of harassing its officers, and the defence minister said troops removed 260 armed young men from a site in the capital. In May 2026 tanks were deployed in Mogadishu after an opposition march was blocked. Many fear a repeat of the 2021 clashes between rival security units.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "digest_dates", n: "The Salvation Forum’s August 2025 demands include ending the army’s political use." },
        so_jsp: { p: -1, k: "record", s: "digest_dates", n: "Federal troops were deployed around Sharif’s and Khaire’s homes in October 2026; Defence Minister Fiqi said they removed 260 armed young men from a site in the capital." }
      } },
    { theme: "integrity", short: "Let the opposition march",
      text: "Opposition parties should be free to hold street protests in Mogadishu, including against evictions.",
      ctx: "The opposition has called several protests in Mogadishu against evictions and the government’s electoral plans. Some were postponed after officials threatened a harsh response; in May 2026 authorities blocked an opposition march and deployed tanks at key junctions. The government cites security risks in the capital.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "sg_evict", n: "Sharif (October 2025): “The protest will be entirely peaceful… Our goal is simply to express public opposition to the government’s policy of forcibly evicting residents.”" },
        so_jsp: { p: -1, k: "record", s: "nova_talks", n: "In May 2026 authorities blocked an opposition demonstration against land grabs and forced evictions and deployed armoured vehicles and tanks in Mogadishu." }
      } },
    { theme: "integrity", short: "No arrests for criticism",
      text: "No one, including clan elders, should be detained for publicly criticising the government.",
      ctx: "In 2025 clan elder Hussein Mohamed Hadole was arrested after voicing dissent, which the opposition condemned. Rights groups and the opposition accuse the security services of intimidating critics; the government has not commented on these cases in the sources found.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "sg_ssf", n: "The Salvation Forum (August 2025): “It is unacceptable in any democratic society to detain individuals simply for voicing their opinions.”" },
        so_jsp: { p: -1, k: "record", s: "sg_ssf", n: "Clan elder Hussein Mohamed Hadole was detained in 2025 after voicing dissent; the government had not responded to the opposition’s criticism." }
      } },

    /* ---------- Land, housing & Mogadishu ---------- */
    { theme: "land", short: "Reclaim state land",
      text: "The government should reclaim state-owned land in Mogadishu, even if this means evicting the families living on it.",
      ctx: "Since 2024 the authorities have cleared settlements, markets and a cemetery on what they call state land, saying this will reopen 52 closed roads and improve urban order. About 142,000 people were displaced in Mogadishu in 2025, according to Geeska, and some clearances ended in deadly clashes. Critics say families were evicted without due process or compensation and that some land was then sold to businessmen.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "geeska_land", n: "The government describes the land as state property and says the clearances will reopen 52 closed roads and improve urban order." },
        so_sfc: { p: -2, k: "stated", s: "sg_evict", n: "Sharif and Khaire (October 2025) called protests against forced evictions carried out, they say, without due process or compensation." }
      } },
    { theme: "land", short: "No sale of public land",
      text: "Public land cleared in Mogadishu should stay in public use and not be sold to private developers.",
      ctx: "A PeaceRep report alleges that public land, including former military camps and cemeteries, was sold to businessmen after residents were evicted. The government says reclaimed land will be used for roads, public facilities and parks. The opposition says the sales are unconstitutional.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "sg_sharif_shabaab", n: "Sharif (September 2025) called the land sales unconstitutional: public land should serve the public, not private profit." }
      }, nd: { so_jsp: "The government says cleared land is state property for roads and public facilities; this edition found no government statement on the sale allegations." } },
    { theme: "land", short: "Rehouse before evicting",
      text: "Families should be rehoused or compensated before they are evicted from public land.",
      ctx: "Most evictions from public land in Mogadishu took place without alternative housing, according to Geeska; rents for makeshift housing rose from about $30 to $50 a month. The opposition demands due process and compensation.",
      cells: {
        so_sfc: { p: 2, k: "stated", s: "sg_evict", n: "Sharif and Khaire (October 2025) object that evictions take place without due process or compensation, leaving thousands homeless." }
      } },

    /* ---------- Foreign relations & sovereignty ---------- */
    { theme: "foreign", short: "Cancel all UAE deals",
      text: "Somalia was right to cancel all agreements with the United Arab Emirates in January 2026, including those of member states.",
      ctx: "On 12 January 2026 the Council of Ministers annulled all agreements with the UAE, including security and defence cooperation and arrangements at the ports of Berbera, Bosaso and Kismayo, accusing Abu Dhabi of undermining Somalia’s sovereignty after Israel recognised Somaliland. The UAE has invested heavily in Puntland’s and Jubaland’s ports and has a base at Bosaso.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "geeska_uae", n: "The Council of Ministers “nullifies and revokes” all agreements with the UAE; Foreign Minister Ali Omar called it a sovereign, constitutional act (January 2026)." },
        so_pl: { p: -2, k: "stated", s: "geeska_uae", n: "Puntland rejected the decision and called Mogadishu’s claim of a signed Bosaso port and security deal with the UAE “completely untrue” (January 2026)." },
        so_jl: { p: -2, k: "stated", s: "newarab_uae", n: "Jubaland, where the UAE operates several ports, rejected the decision along with Puntland and Somaliland (January 2026)." }
      } },
    { theme: "foreign", short: "Türkiye as mediator",
      text: "Türkiye, Somalia’s closest security partner, is a suitable mediator for the dispute over the 2027 elections.",
      ctx: "Since June 2026 Türkiye has led mediation between the government and the opposition, with the US, UK, EU and UN. Türkiye trains Somali forces, has a defence and naval agreement with Mogadishu and an offshore oil deal. Puntland and Jubaland say it cannot be impartial because of its close ties with President Hassan Sheikh.",
      cells: {
        so_jsp: { p: 1, k: "record", s: "ea_proposals", n: "The government took part in the Turkish-led talks and presented its model there (July 2026)." },
        so_sfc: { p: 0, k: "stated", s: "dalsan_op", n: "The Council took part in the talks but asked for other international partners to be included (July 2026)." },
        so_nn: { p: 1, k: "stated", s: "ea_proposals", n: "Farmaajo’s team presented its model to the quartet of the US, UK, UN and EU, together with Türkiye (July 2026)." },
        so_pl: { p: -2, k: "stated", s: "ea_proposals", n: "Puntland said Türkiye could not be trusted as an impartial mediator because of its close ties with Hassan Sheikh (July 2026)." },
        so_jl: { p: -2, k: "stated", s: "ea_proposals", n: "Jubaland said Türkiye could not be trusted as an impartial mediator because of its close ties with Hassan Sheikh (July 2026)." }
      } },
    { theme: "foreign", short: "Ethiopian access to the sea",
      text: "Ethiopia should be given commercial access to the sea through Somali ports under a joint agreement.",
      ctx: "In January 2024 Ethiopia signed a memorandum with Somaliland on sea access, which Mogadishu condemned as a violation of its sovereignty. In December 2024 Somalia and Ethiopia agreed in Ankara on Ethiopian access to a commercial port; technical talks continue. President Hassan Sheikh said in October 2026 that Mogadishu does not object to Ethiopian sea access through Somali ports.",
      cells: {
        so_jsp: { p: 2, k: "stated", s: "aj_2027", n: "Hassan Sheikh (October 2026) said Mogadishu does not object to Ethiopia gaining sea access through a joint agreement to use Somali ports." }
      } },

    /* ---------- Ports, oil & resources ---------- */
    { theme: "econ", short: "States sign their own port deals",
      text: "Federal member states should be able to sign their own port and investment deals with foreign partners without Mogadishu’s approval.",
      ctx: "The provisional constitution gives foreign affairs to the federal government but leaves resource sharing unclear. The UAE has invested over $600 million in Somalia, mainly in the ports of Puntland and Jubaland. In January 2026 Mogadishu annulled all UAE agreements, including member states’ arrangements at Bosaso and Kismayo.",
      cells: {
        so_jsp: { p: -2, k: "record", s: "geeska_uae", n: "The January 2026 decision annulled agreements with the UAE signed by federal member states, including port arrangements at Bosaso and Kismayo." },
        so_pl: { p: 1, k: "stated", s: "geeska_uae", n: "Puntland rejected the decision, while denying that it had signed the Bosaso port and security deal Mogadishu cited (January 2026)." },
        so_jl: { p: 1, k: "record", s: "newarab_uae", n: "Jubaland, where the UAE operates several ports, rejected Mogadishu’s decision (January 2026)." }
      } },
    { theme: "econ", short: "The Turkish oil deal",
      text: "The 2024 oil and gas agreement with Türkiye, which lets Turkish firms recover up to 90% of output as costs, is a good deal for Somalia.",
      ctx: "The agreement signed in March 2024 lets Türkiye recover up to 90% of annual output as “cost petroleum”, caps Somalia’s royalty at 5% and charges no signature bonus. Somali officials say it will bring investment and that Türkiye will get up to 30% of revenue in proportion to its contribution. Critics call the terms unbalanced.",
      cells: {
        so_jsp: { p: 2, k: "record", s: "sg_turkey_oil", n: "The federal Petroleum Minister signed the agreement in Istanbul in March 2024; officials say Türkiye’s share will be proportional to its contribution." }
      } },
    { theme: "econ", short: "Separate elections if no deal",
      text: "If no national agreement is reached, member states should be free to organise their own separate elections.",
      ctx: "Puntland has said it could hold its own elections if no national agreement is reached. Opposition leaders warn that the government’s timetable could lead to “parallel elections” and even civil conflict. The government says the NIEBC timetable applies nationwide.",
      cells: {
        so_pl: { p: 2, k: "stated", s: "digest_dates", n: "Puntland said in February 2026 that it could hold its own elections if no national agreement was reached." },
        so_nn: { p: -1, k: "stated", s: "digest_dates", n: "Farmaajo warned that the unilateral timetable could produce rival elections and civil conflict and asked federal leaders to unite for one credible vote (October 2026)." }
      } }
  ]
};
