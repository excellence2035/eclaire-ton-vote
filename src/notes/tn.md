# Tunisia (tn) — research notes

**Status: INCOMPLETE (11 Oct 2026, ~14:15 Paris).** Research stopped early on both tools. First, the shared WebSearch budget for this turn ran out ("limit: 200 WebSearch calls per turn, shared by every agent"). Then WebFetch returned "session limit · resets 4:40pm (Europe/Paris)". About 20 searches and 22 fetches were done before that.
`src/editions/tn.js` is a **draft that does not validate yet**: it has too few questions, Ennahda and the PDL have too few documented commitments, and Afek Tounes and a left-wing party are still missing.
Everything under "Verified" below comes from a page I opened. URLs under "Seen in results, NOT opened" must be opened before anyone cites them.

---

## Verified — election facts

- **Constitution 2022 (English, Constitute Project)**: https://www.constituteproject.org/constitution/Tunisia_2022.pdf?lang=en
  - Art. 60: deputies of the Assembly of the Representatives of the People (ARP) are elected by universal, free, direct and secret suffrage for **five years**, with the vote held **during the last three months of the parliamentary term**, as the electoral law sets out.
  - Art. 61: a deputy's mandate can be **revoked** (withdrawn) under conditions set by the electoral law.
  - Art. 81: the second chamber, the **National Council of Regions and Districts** ("Provinces" in this translation), is made up of members chosen from the regional and district councils. Each regional council elects 3 of its members, and each district elects 1 representative from its regional councillors.
  - Art. 90: the President is elected for **5 years**, during the last three months of the term, for at most **two complete terms**, consecutive or not.
  - Art. 125: the Constitutional Court has 9 members appointed by order: the most senior judges of the Court of Cassation, the Administrative Court and the Court of Accounts.
  - Art. 134: the electoral authority (ISIE) has **9 members** serving **6-year non-renewable** terms, with one third renewed every 2 years.
  - Art. 135: a Supreme Council for Education.
- **First sitting of the current ARP: Monday 13 March 2023.** Turnout in the Dec 2022 / Jan 2023 election was about **11%**. Most parties boycotted, candidates appeared on ballots **without party affiliation**, and the National Salvation Front refused to recognise the parliament. Saied shut the previous parliament by decree in July 2021 and wrote the 2022 constitution. Source: Reuters via Polity, 13 Mar 2023, https://www.polity.org.za/article/new-tunisian-parliament-begins-its-first-session-2023-03-13
  - So the five-year term ends around March 2028, and under Art. 60 the vote falls roughly between **December 2027 and early March 2028**. (The 2022–23 vote was held on 17 Dec 2022 and 29 Jan 2023. Those dates are from memory and were not confirmed on an opened page.)
- **ISIE plans legislative AND municipal elections in 2027.** At an 11 May 2026 meeting on the ISIE's 2027 budget, it said 2027 will bring "des échéances électorales majeures avec l'organisation des élections législatives et des élections municipales". **No date was given.** President Farouk Bouasker asked for an austerity budget. Source: La Presse, 12 May 2026, https://www.lapresse.tn/2026/05/12/isie-elections-de-2027-un-budget-sous-le-signe-de-lausterite-et-de-lefficacite/
- **Electoral law (Decree-law 55 of 15 Sept 2022)** amended the 2014 law. It brought in two-round single-member (uninominal) contests, **400 voter sponsorships** per candidate and **no public campaign funding**, so candidates pay for themselves or use private money. Art. 39 lets voters withdraw confidence from a deputy, and Art. 34 fills vacancies by by-election. The source is Al-Bawsala's critique as reported by Kapitalis, 20 Sep 2022: https://kapitalis.com/tunisie/?p=4177470
- **By-elections continue under this system.** The ISIE ruled on 29 Jun 2026 on first-round results of a partial legislative election in El Kabaria (Tunis). The page has no figures because the decision is a PDF: https://www.isie.tn/en/isie-decision-of-june-29-2026-on-the-proclamation-of-the-preliminary-results-of-the-first-round-of-the-2026-partial-legislative-elections-in-the-el-kabaria-constituency-tunis-governorate/

### Date coding decision
- The listing says Dec 2027 (month). The verified picture is that the **date is not set**. The ISIE is planning for 2027, and the constitutional window is about Dec 2027 to Mar 2028.
- The draft codes `{ t: "legislative", d: "2027-12", q: "range", d2: "2028-03" }` with `src: "isie_2027"`.
- Difference from the listing: the month is **not** officially known, so the vote could slip into early 2028.

## Verified — governing side (President Kaïs Saïed, no party)

- **IMF / central bank / wealth tax (2026 budget).** The 2026 draft finance law planned about **$3.7bn** in exceptional direct borrowing from the Central Bank (after about $2.3bn in 2025). Talks on an IMF programme have been stalled since 2023. The draft also brought in a **1% "solidarity" tax on assets above 5 million dinars** and a **7bn-dinar sukuk** (a first for Tunisia). The budget deficit is 6.3% of GDP, public debt is about 81% of GDP, and spending rises from 59.8bn to 63.5bn dinars, mainly for wage increases. Economists warned about inflation and crowding out of private credit. Sources:
  - Ecofin, 16 Oct 2025: https://www.ecofinagency.com/news-finances/1610-49625-tunisia-to-seek-3-7bln-exceptional-central-bank-loan-in-2026-amid-persistent-budget-strains
  - Bloomberg, 16 Oct 2025 ("after spurning a potential IMF bailout"; about $4bn from the central bank; deficit 11bn dinars): https://www.bloomberg.com/news/articles/2025-10-16/tunisia-turns-to-central-bank-wealth-tax-after-snubbing-imf
- **Wages set by decree, not negotiation.** Under the 2026 finance law, wage increases for the public and private sectors and for pensions in 2026, 2027 and 2028 are set by the government, bypassing tripartite bargaining with the UGTT and UTICA. Labour Minister Issam Lahmar said the increases are spread over 2026–2028.
  - Business News, 17 Nov 2025 (an opinion-leaning feature): https://businessnews.com.tn/2025/11/17/augmentations-de-salaires-kais-saied-balaie-un-demi-siecle-de-dialogue-social-pour-imposer-sa-loi/1373217/
  - La Presse via AllAfrica, 24 Mar 2026 (three-year increase; the Social Affairs minister says legal procedures were followed; 2026 public wage bill 25.267bn dinars): https://fr.allafrica.com/stories/202603250361.html
- **UGTT called a general strike for 21 Jan 2026** to demand wage negotiations and to protest the crackdown on critics. Africanews, Dec 2025: https://www.africanews.com/amp/2025/12/07/tunisias-powerful-ugtt-union-calls-nationwide-strike-for-january-21/
  - Search results suggest the strike was postponed after an internal UGTT crisis, but these pages were NOT opened: businessnews 14 Jan 2026 "le bureau exécutif de l'UGTT impute à Noureddine Taboubi le report de la grève générale" https://businessnews.com.tn/2026/01/14/le-bureau-executif-de-lugtt-impute-a-noureddine-taboubi-le-report-de-la-greve-generale/1382842/ ; webdo "UGTT : grève générale reportée selon Sami Tahri" https://www.webdo.tn/fr/actualite/national/ugtt-greve-generale-reportee-selon-sami-tahri/391262/
- **Parties that backed the 25 July 2021 measures** were La Tunisie en avant, Echaab, Courant populaire, Coalition pour la Tunisie, Mouvement Al Baath and the Parti patriotique démocratique socialiste, in a joint statement. Webdo, 24 Sep 2021: https://www.webdo.tn/fr/actualite/national/tunisie-six-partis-politiques-soutiennent-kais-saied/135922/
  - Open doubt: which of these still back Saied in 2026? Echaab has moved into opposition (see below). No 2025–26 source was found for the others, so no pro-Saied party could be documented as the governing side. The draft therefore uses a "presidential camp" entry (`tn_25j`) coded only from government and presidential records.

## Verified — parties

### Echaab (Mouvement du Peuple / Harakat Echaab) — Zouhair Maghzaoui
- **2 Jan 2026** (Business News, "La Tunisie n'a pas besoin de slogans, mais d'actes"), https://businessnews.com.tn/?p=1381185
  - The 25 July process has not delivered on its anti-monopoly and anti-rent promises: "aucune réforme structurelle majeure n'a été engagée".
  - Freedoms are a priority, especially the **revision or repeal of Decree 54**. It is "difficile de parler de justice indépendante", and party activity is increasingly restricted.
  - Seeking foreign backing is a "ligne rouge". Sovereignty must lead to concrete choices on economic partnerships, international ties and **migration policy**.
  - The party now places itself **in opposition**; it backed the process at first. Its third congress is coming.
- **17 Apr 2026** (Business News, "Il n'y a pas d'alternative"), https://businessnews.com.tn/2026/04/17/il-ny-a-pas-dalternative-zouhair-maghzaoui-appelle-a-se-rallier-au-mouvement-echaab/1397184/
  - Concern that the **Supreme Council of the Judiciary and the Constitutional Court** are still missing; he urges the President to set them up.
  - Criticises ad hoc price interventions and wants coherent policies.
  - Quality **public health, education and transport** are "une condition sine qua non" of democratic progress; he opposes treating them as goods for sale.
  - Asks about gas supply towards 2030 and energy ties with Algeria; says the shift to alternative energy should be anticipated.
  - Lists the Palestinian cause among the party's goals. A congress with economic and social programme documents is coming.
- **18 Apr 2022** (Kapitalis / Anbaa Tounes, political bureau), https://kapitalis.com/anbaa-tounes/?p=300455
  - Supports the 25 July path, with reservations.
  - Warns against a "liberal approach" that puts economic concerns before social ones.
  - Condemns fuel price hikes.
  - Calls for settling the files of temporary workers and substitute teachers, and for **activating Law 38** (hiring of long-term unemployed graduates).
  - Calls normalisation with Israel a betrayal.
- **4 Dec 2021** (Kapitalis), https://kapitalis.com/tunisie/?p=372321: wanted a deadline for the exceptional measures, dialogue with all national forces and democratic elections.
- **25 Jul 2024** (Webdo opinion column; use only for facts), https://www.webdo.tn/fr/?p=215469: Maghzaoui ran for president in 2024 and said the 25 July movement "n'a pas atteint ses objectifs".

### Ennahda — Rached Ghannouchi (imprisoned)
- **3 Jun 2026** (Al Jazeera), https://www.aljazeera.com/news/2026/6/3/tunisian-court-sentences-ennahdha-leader-rached-ghannouchi-to-life-in-prison
  - In the "secret apparatus" case, Ghannouchi was sentenced to **life plus 30 years** on terrorism-related charges. Ali Laarayedh and 10 others received life sentences.
  - On 15 Apr 2026 Ghannouchi and three other Ennahda leaders got 20 years in the "Ramadan soirée" case.
  - Ennahda calls the cases **politically motivated** and demanded his immediate release on health grounds; the National Salvation Front did the same. The authorities deny holding political prisoners.
- Not found yet: any 2025–26 Ennahda policy statement (economy, IMF, constitution, elections or boycott).

### PDL (Free Destourian Party) — Abir Moussi (imprisoned)
- **29 Sep 2026** (Business News), https://businessnews.com.tn/2026/09/29/abir-moussi-la-cour-de-cassation-rejette-deux-pourvois-de-sa-defense/1420655/
  - The Court of Cassation rejected her appeals. In the "bureau d'ordre" case she has **10 years**: 9 years for undermining the form of the state and inciting violence, 6 months for data processing and 6 months for obstructing freedom of work, all handed down on 13 Mar 2026.
  - In the ISIE case she has **2 years**, upheld on appeal on 30 Dec 2025.
- Not found yet: any PDL policy statement for 2025–26.

### Afek Tounes, Workers' Party (Hamma Hammami), Attayar, Al Joumhouri
- **Nothing verified yet.** Both searches for Afek were refused by the search limit.

## Seen in search results, NOT opened (open before citing)
- Opposition and boycott of 2022 legislative elections:
  - https://www.africanews.com/2022/09/09/tunisian-opposition-to-boycott-december-legislative-polls//
  - https://www.al-monitor.com/originals/2022/12/tunisias-election-campaigning-begins-quietly-boycotts-apathy-prevail
  - https://nationalinterest.org/blog/middle-east-watch/tunisian-opposition-boycotts-elections-over-saied%E2%80%99s-%E2%80%98coup-204707
  - https://www.newarab.com/news/tunisia-awaits-neutered-election-powerless-parliament?amp=1
  - https://www.africa-confidential.com/article/id/14128/president-saieds-election-plan-faces-mass-boycott-challenge
  - https://www.voanews.com/a/6738370.html
- 2021 anti-Saied coalition of Attayar, Al Joumhouri, Ettakatol and Afek Tounes:
  - https://www.aljazeera.com/news/2021/9/28/four-tunisian-parties-announce-coalition-to-counter-saeed
  - https://menaaffairs.com/four-tunisian-parties-announce-coalition-to-counter-president-saieds-decrees/
- Central bank and IMF:
  - https://www.centralbanking.com/central-banks/governance/7959700/tunisian-president-wants-central-bank-to-directly-finance-budget
  - https://www.globalcapital.com/article/2dxdohsusywjy89l65wxs/emerging-markets/ailing-tunisia-refuses-imf-medicine-as-default-nears
- UGTT strike and wages:
  - https://www.leconomistemaghrebin.com/2025/12/05/lugtt-appelle-a-une-greve-generale-le-21-janvier-2026/
  - https://businessnews.com.tn/2025/12/06/derive-autoritaire-violation-du-droit-syndical-lugtt-hausse-le-ton-lancant-son-appel-a-la-greve-generale/1377196/
  - https://businessnews.com.tn/2026/01/12/ugtt-la-desertion-qui-a-fait-tomber-la-greve-generale/1382334/
  - https://fr.allafrica.com/stories/202601160179.html
  - https://www.webdo.tn/fr/actualite/national/augmentations-salariales-lugtt-repond-au-ministre-des-affaires-sociales/387426/
  - https://managers.tn/2025/10/16/le-projet-de-loi-de-finances-2026-prevoit-une-hausse-des-salaires-dans-les-secteurs-public-et-prive/
- Ghannouchi:
  - https://fr.allafrica.com/stories/202604150360.html
  - https://www.newarab.com/news/tunisia-rached-ghannouchi-hit-longer-prison-sentence?amp
- Moussi:
  - https://amnesty.ca/urgent-actions/tunisia-opposition-figure-sentenced-after-unfair-trial/
  - https://gna.org.gh/2025/12/tunisian-opposition-party-leader-gets-12-years-in-jail/
- Echaab:
  - https://www.mosaiquefm.net/mobile/ar/ميدي-شو-أخبار/1037108/المغزاوي-قيس-سعيد-أساء-إدارة-البلاد-بعد-25-جويلية
  - https://www.tunisienumerique.com/zouhair-mghzaoui-vers-lorganisation-dun-dialogue-national/
  - https://businessnews.com.tn/2023/05/27/article-1198007/1198007/
  - https://kapitalis.com/tunisie/?p=13618195
- Courant populaire roadmap: https://kapitalis.com/tunisie/?p=3350679
- Government of PM Sarra Zaafrani Zenzri (March 2025), for the real ministry names behind the themes:
  - https://www.lapresse.tn/2025/03/21/changement-a-la-tete-du-gouvernement-sarra-zaafrani-zenzri-succede-a-kamel-maddouri/
  - https://businessnews.com.tn/2025/03/25/sarra-zaafrani-zanzri-limogera-t-elle-les-ministres-de-kamel-maddouri/1356463/
- Electoral law, no amendment announced:
  - https://www.webdo.tn/fr/actualite/national/tunisie-pas-damendement-de-la-loi-electoral/197983/
  - https://lapresse.tn/139709/amendement-de-la-loi-electorale-les-partis-politiques-a-rude-epreuve
- Parliamentary blocs:
  - https://www.webdo.tn/fr/actualite/national/tunisie-formation-de-six-blocs-parlementaires-au-sein-de-larp/167326/
  - https://www.webdo.tn/fr/actualite/national/arp-tout-savoir-sur-les-nouveaux-blocs-parlementaires/205626/
- HRW referendum Q&A (2022): https://www.hrw.org/fr/news/2022/07/14/referendum-constitutionnel-en-tunisie-questions-reponses

## Open doubts
1. **Election date**: none announced. Is the vote in Dec 2027 or early 2028? Will municipal elections be held on the same day?
2. **Electoral law**: will Decree-law 55 (individual candidacies, 400 sponsorships, no public funding) be amended before 2027? The 2023 Webdo pages say no amendment, but they are not opened and are old.
3. **Pro-Saied side**: which party or ARP bloc embodies it in 2026? Echaab has left it. The 2021 backers (Tunisie en avant, Courant populaire and others) have not been checked for 2026.
4. **Boycott in 2027**: will Ennahda, the PDL, the National Salvation Front and the left boycott again? Nothing verified for 2026.
5. Ennahda's current acting leadership while Ghannouchi is in prison is not verified.
6. Facts not checked on any opened page: the ARP's seat count (161, with 10 for Tunisians abroad) and the dates of the 2022–23 rounds.

## Question plan (for the follow-up)
Themes are tied to the Zenzri government; the ministry names still need checking.

- **econ**
  - No IMF programme / self-reliance (`tn_25j` record)
  - Direct central bank lending (`tn_25j`)
  - Wealth tax (`tn_25j`)
  - Bread and fuel subsidies
  - No privatisation of public firms
  - Community companies
- **gov**
  - Party lists instead of individual candidacies
  - Restore public campaign funding
  - Set up the Constitutional Court before 2027 (Echaab)
  - Independent ISIE
  - National dialogue (Echaab 2021)
  - Rebalance presidential powers
- **integrity**
  - Repeal Decree 54 (Echaab)
  - Release political detainees (Ennahda, `tn_25j`, Echaab)
  - No civilians before military courts
  - Elected judicial council
  - Foreign funding of associations
- **social**
  - Wages negotiated with the UGTT (`tn_25j` record)
  - Ban on subcontracting and fixed-term contracts (2025 Labour Code)
  - Hiring long-term unemployed graduates (Law 38; Echaab 2022)
- **foreign**
  - EU migration MoU
  - Voluntary return of migrants
  - Law criminalising normalisation with Israel
- **edu / health**
  - Keeping doctors and graduates in the country
  - Public services not commodities (Echaab)
- **energy**
  - Gabès phosphate units
  - Private solar concessions
  - Gas and Algeria (Echaab)
- **agri/water**
  - Water rationing and desalination
  - State land for community companies
