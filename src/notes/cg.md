# Republic of the Congo (cg) — research notes

STATUS: COMPLETE as an ED questionnaire (role "leader"), 22 Oct 2026. `src/editions/cg.js` validates OK: 5 parties, 8 themes, 27 questions, 45 sources. Budget used: 25/25 WebSearch, about 35/35 WebFetch (one fetch failed on a session limit, not on a refusal). Prior dump: scratchpad/prior/cg.md (Oct 11–12), reused for pages marked FETCHED.

Coverage: PCT 20/27, Alliance 13/27, Souverainistes 13/27, UPADS 7/27, ARD 5/27. Warnings left: 4 questions with one party coded (IMF programme, 30,000 teachers, scholarships/orphans, carbon credits), health theme has 2 questions, UPADS and ARD below 35% coverage (their published positions are about election rules and institutions only).

## Election (what is next)
- Next national vote: legislative (National Assembly, 151 seats, single-member constituencies, two rounds, 5-year term) plus local elections, due by July 2027. NO official date found in any source. Assembly elected 10 & 31 Jul 2022 (PCT 111 of 151 per Le360; 112 in Wikipedia’s count). In 2022 legislative and local elections were held together (Africanews, May 2022).
  - META_CG uses d 2027-07, q "by" (source: Wikipedia “by July 2027”, background only). `src/africa.js` row "178" says `ev: legislative 2027-07, q: "month", src: af_rio`: slightly stronger than what was verified (month not confirmed). Not touched.
  - UPADS says it is preparing “the legislative and local elections of 2027” (Les Dépêches, 31 Jan 2026).
- Presidential vote 12 Mar (security forces) and 15 Mar 2026 (civilians) VERIFIED: Sassou Nguesso (PCT) 94.90% (2,509,456 votes), turnout 84.99% of 3,155,751 registered (Constitutional Court, 28 Mar 2026). Others: Mabio Mavoungou-Zinga 1.40%, Mafoula 1.03%, Gavet Elengo 0.87%, Kignoumbi 0.86%, Manangou 0.61%, Nganguia Engambé 0.33% (sum of the six = 5.10%). Mafoula’s annulment request (20 Mar) rejected. https://fr.allafrica.com/stories/202603300213.html
  - Provisional: 94.82%, turnout 84.65% (Interior Minister, 17 Mar). Inaugurated 16 Apr 2026 at Kintélé. Makosso reappointed PM 23 Apr (decree 2026-175); government decree 2026-176 of 24 Apr 2026, JO 18 of 30 Apr 2026, 41 posts. https://sgg.cg/JO/2026/congo-jo-2026-18.pdf
  - UPADS and UDH-Yuki did not field candidates (AFP/EcoMatin 11 Mar 2026). Internet and phone cut all day 15 Mar 2026, no official reason (RFI).
- Sassou Nguesso’s term limit: the Africa Center says he circumvented age and term limits in 2015. Wikipedia (background) says he cannot run in 2031. Neither used as a party position.

## Sources OPENED in this run (all cited in cg.js)
- Mabio “Cap pour demain”, 8 Mar rally (pub. 10 Mar 2026): 200,000 jobs via SMEs, 100bn FCFA guarantee fund, 200,000 farmers, Sounda dam to end power cuts, CFCO railway, national airline, 30,000 teachers, classrooms/university residences, universal health insurance, 15,000 health professionals, justice independence, high anti-corruption authority; “L’État ne doit pas étouffer l’économie”. https://fr.allafrica.com/stories/202603100523.html
- Reuters factbox via AOL (Mar 2026; year not printed on page): Mavoungou-Zinga pledges to free Mokoko and Okombi Salissa; Kignoumbi (La Chaîne) diversification; Mafoula governance reform/jobs; Gavet transparency; Manangou independent; Nganguia (Party for Action of the Republic). https://www.aol.com/articles/factbox-opposition-candidates-congo-republics-080148181.html
- Fuel shortage Brazzaville, RFI 20 May 2026: government communiqué blames the Middle East crisis; no measures reported. https://fr.allafrica.com/stories/202605200242.html
- Dabafinance 14 Oct 2026: DGE survey Q2 2026, diesel hardest to get, black market, 30.4% say cash flow threatened. https://dabafinance.com/fr/nouvelles/fuel-shortages-threaten-companies-cash-flow-in-congo-2026-10-14
- Power cuts Brazzaville, RFI 13/14 Apr 2026: E²C blames urbanisation and overloaded substations. https://fr.allafrica.com/stories/202604140142.html
- Energy minister Itoua, 5 Jun 2026: fewer power cuts first; 3,000 MW in 2 years, 5,000 MW by 2030–31; review of “Eau pour tous”; 2003 laws may be revised. https://fr.allafrica.com/stories/202606060216.html
- Sounda dam, 14 Apr 2025 (spokesman Moungalla): 1,300bn FCFA, +600 MW vs 720 MW produced; works “dans les tous prochains temps”. https://fr.allafrica.com/stories/202504150093.html
- Bilan du quinquennat, 22 Dec 2025 (Makosso): ~40,000 youths into civil service 2021–2025 (25,049 to 2023 + 15,000 in progress); government claims unemployment 47%→42% and debt 83% of GDP in 2025. https://fr.allafrica.com/stories/202512230560.html
- Al Jazeera 13 Mar 2026: oil ~70% of exports, ~40% of GDP (World Bank); government urges self-employment; Makosso claims unemployment 44%→39%. https://aljazeera.com/features/2026/3/13/poor-in-an-oil-rich-country-republic-of-congos-youth-hope-for-change
- AP via WTOP (Mar 2026): youth unemployment 41% (15–24, World Bank); not defined as a key in cg.js. https://wtop.com/world/2026/03/young-people-expect-little-change-as-the-republic-of-congo-heads-to-a-presidential-election/
- Afrik 19 Mar 2026: IMF warns debt 97.2% of GDP end-2025; current account deficit 5.8%. https://www.afrik.com/congo-le-fmi-alerte-sur-une-dette-publique-proche-de-100-du-pib
- EcoMatin 9 Oct 2026 (2027 finance bill, presented by Yoka 8 Oct): revenue 3,120.8bn, spending 2,638.4bn, surplus 432.4bn, oil $71/bbl, investment 680bn, “external resources imperative”, depends on IMF programme. https://ecomatin.net/le-congo-table-sur-3-121-milliards-fcfa-de-recettes-budgetaires-en-2027-en-hausse-de-12
- EcoMatin 9 Oct 2026: investment 680bn vs 224.9bn disbursed in 2025 (execution 53.9%); “approved 7 Oct” there vs “presented 8 Oct” in the other article (cg.js says “early October”). https://ecomatin.net/congo-brazzaville-prevoit-de-tripler-ses-investissements-publics-en-2027
- Amended finance law 2026, presented 14 Jul 2026 (not cited): revenue 2,778bn; no salary/subsidy measure. https://fr.allafrica.com/stories/202607150140.html
- Decentralisation: Senate president met Interior/Decentralisation minister 30 Jul 2026; no statement; unresolved retrocession of “centimes additionnels”; territorial civil service raised by senators (not cited). https://fr.allafrica.com/stories/202608020064.html
- Carbon market forum, Brazzaville 16–19 Jun 2026 (CCBC, UNDP, Japan $580,000; minister Soudan-Nonault). https://fr.allafrica.com/stories/202606240492.html
- Kinkala youth meeting 3 Mar 2026: Sassou refers youth to his project, no concrete promise (not cited). https://fr.allafrica.com/stories/202603070059.html
- Africa Center 23 Feb 2026: term/age limits circumvented 2015; Assembly selects CENI; 15 opposition parties suspended Jun 2025; protests banned; Lassy Mbouity abducted May 2025; courts upheld Mokoko/Okombi convictions; debt to China $3.2bn; TI rank 151/180. https://africacenter.org/fr/spotlight/fr-elections-2026/repcongo/
- RFI 15/16 Mar 2026 on the shutdown: no official reason; radical opposition called the vote a “simulacre” and a boycott; parliamentary opposition gave no instruction. https://fr.allafrica.com/stories/202603160379.html
- Afrik 15 Mar 2026: many CSOs not accredited as observers; UPADS and UDH-Yuki gave no voting instruction. https://www.afrik.com/congo-brazzaville-un-scrutin-presidentiel-sous-le-signe-de-la-continuite
- RSF country profile: 68th/180 in 2026 (71st in 2025); CSLC president appointed by the President; self-censorship. https://rsf.org/fr/pays/congo-brazzaville
- CNR 26 Jan 2026 communiqué: war is past; asks respect of 23 Dec 2017 agreements; DGSP attacks 16 & 25 Jan (CNR claims, no government response). https://fr.allafrica.com/stories/202601270577.html
- Conader/UNDP “Tatoungueno” project, Pool (19 Apr; year inferred 2025 from AllAfrica story number): 7,500 to disarm, 10,000 to reintegrate, 8,000 weapons collected. https://fr.allafrica.com/stories/202504200010.html
- CAMU first biometric health cards, 31 Mar (year inferred 2025 from story number 202504020101); pilot in Brazzaville, Pointe-Noire, Oyo. https://fr.allafrica.com/stories/202504020101.html
- Allo Docteurs 20 Jul 2022 (updated Jun 2025): free caesarean kits; 2011 decree free caesareans in 30+ hospitals. https://www.allodocteurs.fr/au-congo-brazzaville-la-cesarienne-bientot-gratuite-43917.html
- Community teachers (Bénin Web TV, 4 Sep 2026): ~12,000, ten months of unpaid allowances, threat of strike in early Oct 2026, no government reply (used in ctx only). https://beninwebtv.bj/congo-12-000-enseignants-communautaires-reclament-leurs-arrieres-et-menacent-de-paralyser-la-rentree/
- EITI workshop Pointe-Noire 15 Dec 2025 (nothing usable on contracts or SNPC sales; not cited). https://fr.allafrica.com/stories/202512170622.html
- CAR (Clotaire Mboussa-Ellah) on biometric voter card, Jan 2025 (year inferred): opposition party outside the five compared (not cited). https://fr.allafrica.com/stories/202501170023.html
- UPADS 2007 “hold-up électoral” complaint after the 2007 legislative vote (Tsaty Mabiala then secretary general): old, not used. https://www.afrik.com/legislatives-au-congo-le-parti-de-lissouba-accuse-le-pouvoir-de-hold-up-electoral

## Sources reused from the prior dump (FETCHED by earlier researchers; summaries in scratchpad/prior/cg.md)
- IPU Parline (151 seats, 5 years, 30% women on lists); Wikipedia 2022 and 2027 pages (system background only); Le360 3 Aug 2022; Africanews May 2022 (ARD and Miérassa’s federation favoured a 2022 boycott; UPADS and UDH-Yuki ran).
- UPADS 26 Jan 2026 (no candidate; conditions: free expression, independent judiciary, neutral security forces, independent observers; biometric ID, spending cap, consensual roll, independent commission; pacte républicain) and 31 Jan 2026 (2026 programme for 2027 legislative and local elections).
- ARD 13 Dec 2025 (postpone, inclusive dialogue, commission with equal numbers majority/opposition); open letter 20 Sep 2025 (Dzon, Miérassa, Agnangoye).
- Afrik 16 Feb 2026 Djambala dialogue (16–19 Feb; UPADS and CNR took part; Dzon’s UPRN refused).
- Mafoula: rally 10 Mar 2026; Ouesso 5 Mar 2026; Africa24 23 Feb 2026.
- PCT congress (Pierre Moussa secretary general); inauguration speech 16 Apr 2026; PAG 22 Jun 2026; IMF request 11–12 May 2026; JO 18; EcoMatin 25 Apr 2026 (41 ministries).
- The Conversation/AllAfrica 5 Mar 2026 (opposition fragmented, UPADS/UDH-Yuki boycott).

## Not found / for a fact-checker to look at first
1. Legislative date: nothing official. “By July 2027” rests on the 5-year term and Wikipedia. Local elections assumed together (as in 2022), not confirmed.
2. Which forces will contest the 2027 vote (Alliance, Souverainistes, ARD, UPADS beyond the Jan 2026 council programme) is unknown. No party 2027 manifesto found. Opposition cells come from the March 2026 presidential campaign and Dec 2025–Jan 2026 statements.
3. UDH-Yuki: no published positions found, so not compared. Leader not verified.
4. PCT cells rest on government record (finance bill, ministers, Prime Minister) and the President’s inauguration speech, not on a party manifesto. Cells coded “record” from the Africa Center (protest ban, 15 parties suspended, term limits) and Afrik (observer accreditation) attribute State actions to the PCT.
5. Dates inferred from AllAfrica story numbers: Tatoungueno (Apr 2025) and CAMU cards (31 Mar 2025). The “Sounda” article title says “reportée sine die” while the text says works are to start soon (cg.js follows the text).
6. “Les Souverainistes”: AFP calls Mafoula’s movement this; the Constitutional Court lists him as independent. Alliance: Wikipedia (prior dump) says it is a coalition formed in 2023 by RDD, MR and PP; Les Dépêches calls Mavoungou-Zinga president of the “Alliance” party.
7. Debt figures differ by source (government 83% for 2025; IMF via Afrik 97.2%; Fitch about 92% end-2024). cg.js shows both government and IMF figures.
8. Brief said today = 18 Oct 2026; the system date moved to 22 Oct 2026, and cg.js `status` uses 22 Oct 2026.
9. Possible follow-ups not done (budget exhausted): oil revenue transparency and SNPC contracts (no party position found); salary arrears (only the community teachers’ case); decentralisation positions of the opposition; IMF positions of the opposition; UDH-Yuki and PCT 2027 candidate lists; Kinshasa–Brazzaville bridge; fuel pump prices and subsidies.
