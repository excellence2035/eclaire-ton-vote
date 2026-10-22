# Tunisia (tn) — research notes

**STATUS (22 Oct 2026): DONE, validator OK. Second pass finished; coverage is now acceptable but four questions are still single-force.**
`src/editions/tn.js` is an `ED_TN` with 4 forces, 8 themes and 26 questions, and it validates (warnings only). Coverage: 25 July camp 19/26, Echaab 16/26, UGTT 14/26, Ennahdha 10/26. Single-force questions: Constitutional Court (Echaab), voluntary returns (25 July), no foreign backing (Echaab), gas/renewables (Echaab).
**The "22 Oct 2026 second pass" section at the end supersedes the "18 Oct 2026 run" section**, whose coverage figures, "What is missing" list and "unopened" labels are out of date. The older sections of this file ("Verified", "Seen in search results") are kept for the record.
Budget of the second pass: 20 WebSearch and 28 WebFetch used (1 refused by the session limit, then retried successfully). Every cell in the edition is now backed by a page opened in this or an earlier pass, except where the section at the end says otherwise.
Everything under "Verified" below comes from a page that was opened. URLs under "Seen in results, NOT opened" must be opened before anyone cites them.

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

---

## 18 Oct 2026 run — what was built and on what

### Decision: ED_TN (rule 5)
- **Forces compared (4):**
  - `tn_25j`: President Saïed's camp, coded only from his and his government's record and statements.
  - `tn_echaab`: Echaab, now in opposition, coded from its statements.
  - `tn_nahdha`: Ennahdha, which boycotted in 2022–23 and whose leaders are in prison, coded from its statements.
  - `tn_ugtt`: the UGTT, a union that fields no candidates.
  - At least 3 forces can be coded, so rule 5 requires an ED. `status` and the system row "Not a competitive vote in the usual sense" say plainly that the vote is not competitive, who boycotted and how coding was done.
- **PDL not compared.** No policy statement for 2025–26 was found; we only have sentences, the congress title (3–4 Oct 2026) and a 2022 headline. It is listed in `others`.
- **META** keeps the 16 Oct choice: `{ legislative, 2027-11, range, d2 2028-03 }`, src `ayachi`. This could not be re-checked on 18 Oct (the fetch was refused).

### Sources added to SRC by the 16 Oct researcher (not in the notes above)
These are in `SRC_TN`, and the researcher who added them evidently opened them: their 16 Oct system text quotes details that are not in the titles. Their content is NOT recorded anywhere except as follows. A fact-checker should reopen them first.
- **ayachi** (Webdo, 13 Oct 2026). The title says municipal elections are possible before end 2026, otherwise by March 2027. The 16 Oct text says ISIE board member Belgacem Ayachi said the legislative vote would be in Nov 2027, "not an officially adopted calendar". This is used for META, the facts and a system row.
- **hrw_sep26** (HRW, 4 Sep 2026). From the 16 Oct text:
  - 37 people sentenced to 4–66 years in the "conspiracy" case in Apr 2025.
  - At least 20 associations suspended by court order between Jul 2025 and Apr 2026.
  - Used in a system row and in Q "Suspending associations" (`tn_25j` +1).
- **boycott22** (Le360/AFP, 20 Sep 2022). The 16 Oct text says Ennahdha within the NSF, the Workers' Party and Al Joumhouri boycotted. It is used for the Ennahdha tag, a commit and the boycott cell. **Check that this page actually names Ennahdha/NSF.**
- **ugtt_selmi** (La Presse, 28 Mar 2026). From the title, Selmi "tend la main au gouvernement" (holds out a hand to the government). The 16 Oct text says the Mar 2026 congress elected him secretary general.
- **Used at headline level only** (cells say no more than the title):
  - **nahdha_jan26**: Ennahdha denounces political decline and calls for an inclusive national dialogue.
  - **public_assets**: Saïed rules out any sale of public assets.
  - **d54_bill**: the Decree 54 amendment still hits a "wall" in Parliament, according to MP Mohamed Ali.
  - **grads**: the State is accelerating the recruitment of unemployed graduates.
  - **returns**: a target of 10,000 voluntary repatriations of migrants in 2026.
  - **labour25**: fixed-term contracts (CDD) and labour subcontracting banned in May 2025.
  - **norm_bill**: Saïed opposed the anti-normalisation law in Nov 2023.
  - **ugtt_imf**: the UGTT lambasted the IMF loan negotiations in May 2023.
  - **imf_diktats**: Saïed rejected IMF "diktats" in Apr 2023.
- **Removed from SRC as unused** (content unknown; reopen before using):
  - pdl_congress (L'Économiste Maghrébin, 13 Aug 2026): https://www.leconomistemaghrebin.com/2026/08/13/pdl-annonce-tenue-congres-national-3-et-4-octobre-2026/
  - pdl_prog (Webdo, 14 Nov 2022, "Moussi : Kais Saied a copié le programme économique du PDL"): https://www.webdo.tn/fr/actualite/national/moussi-saied-a-copie-le-programme-economique-du-pdl/198884/
  - ugtt_prio (La Presse via AllAfrica, 1 Apr 2026, "UGTT - Les priorités du nouveau bureau exécutif"): https://fr.allafrica.com/stories/202604010594.html
  - lf2026 (Le Courrier de l'Atlas, 16 Oct 2025, "Loi de finances 2026 : promesses sociales, angles morts économiques"): https://www.lecourrierdelatlas.com/loi-de-finances-2026-promesses-sociales-angles-morts-economiques/
  - fsn_2022 (Al Jazeera Net, 30 Oct 2022, the Salvation Front announces "political mobilisation"): https://www.ajnet.me/news/2022/10/30/%d8%aa%d9%88%d9%86%d8%b3-%d8%ac%d8%a8%d9%87%d8%a9-%d8%a7%d9%84%d8%ae%d9%84%d8%a7%d8%b5-%d8%aa%d8%b9%d9%84%d9%86-%d8%a7%d9%84%d8%aa%d8%b9%d8%a8%d8%a6%d8%a9
- **Blocked on 18 Oct** (the fetch was refused, not because the page failed): ayachi, hrw_sep26, nahdha_jan26.
- **Dropped from the 16 Oct text because they were not verified on an opened page:**
  - "161 seats".
  - The name of the head of government (Sarra Zaâfrani Zenzri, appointed Mar 2025; still in office in Oct 2026? not checked).

### Context facts used from general knowledge (flag for fact-check)
- Decree-law 54 was issued by the President in 2022 (Q "Repeal Decree 54" ctx).
- Saïed has been President since 2019 (candNote).
- Ministry names in `themes[].min` are not verified on an opened page.

### Seen in search results on 18 Oct, NOT opened
- PLF 2026 expert panel (Business News, 20 Oct 2025): https://businessnews.com.tn/2025/10/20/le-plf-2026-sous-la-loupe-des-experts-entre-incoherence-dependance-a-la-bct-et-risques-dinflation/1368249/
- PLF 2026, BCT loan of 11,000 MD (Managers, 16 Oct 2025): https://managers.tn/2025/10/16/plf2026-la-bct-est-autorisee-a-accorder-un-pret-de-11000-millions-de-dinars-a-letat/
- The Afek Tounes search returned no page about Afek itself.

### What is missing (priority order for a follow-up)
1. **Reopen ayachi** to confirm the date (Nov 2027?) and whether municipal elections are held separately.
2. **Ennahdha** needs more cells (only 4 now). Reopen nahdha_jan26 for its full content. Find 2025–26 statements on the economy, the IMF, the 2027 vote (boycott or not) and Decree 54.
3. **The UGTT** needs more cells (7 now). Reopen ugtt_prio (privatisation, subsidies, wages) and ugtt_selmi.
4. **PDL**: congress outcome of 3–4 Oct 2026, its programme and its stance on 2027. It could become a 5th force.
5. **Afek Tounes** (liberal, likely pro-reform/IMF) and the **Workers' Party**: none researched yet.
6. **Government record still unsourced**:
   - Fuel and bread subsidies 2025–26
   - Price controls
   - Community companies
   - Gabès phosphate
   - EU migration MoU
   - Energy and renewables plan
   - Draft finance law 2027 (Oct 2026)
7. **Single-coded questions to strengthen** (13): Central Bank lending, wealth tax, monopolies, spending for wages, party lists, campaign funding, recall, Constitutional Court, voluntary returns, foreign backing, price interventions, gas/renewables, sale of public companies.

---

## 22 Oct 2026 second pass — what changed (supersedes the 18 Oct section)

### Verification of the items flagged for the fact-checker on 18 Oct
- **ayachi** (Webdo, 13 Oct 2026, https://www.webdo.tn/fr/actualite/national/municipales-un-scrutin-possible-avant-fin-2026-sinon-dici-mars-2027/405501/), OPENED. Author Mohamed Fethi. Belgacem Ayachi is a **member of the ISIE council**, not its head. He says municipal elections are possible before end 2026 or by March 2027, depending on a decree convening voters; he indicates the **legislative vote in November 2027**, and the article stresses it is "distinct from an officially adopted calendar". No mention of electoral law changes, seat numbers or party participation. META and facts confirmed.
- **boycott22** (Le360/AFP, 20 Sep 2022), OPENED. It names Al-Joumhouri (Issam Chebbi) and the Workers' Party (Hamma Hammami) as part of a coalition of five parties; it says the **National Salvation Front, which includes Ennahdha, announced a boycott in early September 2022, before the new electoral law was published**. It also says the 2022 parliament has **161 seats**. It does not mention the PDL. Used for the 161 seats and the FSN boycott.
- **boycott_webdo** (Webdo, 5 Oct 2022), OPENED. FSN boycott announced 7 Sep 2022 (reason: law drafted unilaterally; ISIE accused of loyalty to the power that installed it); Moussi: PDL will not recognise or take part in the elections, "un crime d'État"; Attayar boycott on 26 Sep; five-party coalition Al Joumhouri, Workers' Party, Attayar, Al Qotb, Ettakatol. Echaab, Courant populaire and Afek Tounes are not in the article. Used for `othersSrc`, the system row and Q "Keep the 2022 electoral law".
- **kap5** (Kapitalis, 3 Dec 2022), OPENED: the five parties' joint message, "boycott the electoral masquerade to bring down the coup", law drafted unilaterally, and no mention of individual candidacies, constitution or economy.
- **nahdha_jan26** (Business News, 14 Jan 2026), OPENED. It reports a communiqué of "the Ennahdha movement" (no body or leader named). It calls the 2021 measures a "coup d'État", demands "la libération de tous les détenus politiques" and an end to "procès injustes", calls for "un dialogue national inclusif", says elections were held "en deçà des standards de la démocratie libre et équitable", describes an acute economic and social crisis (prices, living costs, unemployment) **without proposing measures**, and praises forces that joined the **10 Jan 2026 national march**. It does NOT address the IMF, finance law, wages, subsidies, Decree 54 by name, the judiciary as an institution, the constitution, the 2027 vote, migration or foreign policy. So the Ennahdha cells on Decree 54, Parliament's powers and the Constitutional Court (nd) are leans, and are labelled as such in the notes.
- **ugtt_selmi** (La Presse via AllAfrica, 28 Mar 2026), OPENED. Selmi, list "Stabilité et Défi", won the 26th congress (Monastir, 25–27 Mar 2026). Quotes: "la main de l'Union est tendue au dialogue"; "il n'est pas possible de continuer dans un état de rupture avec le gouvernement". It says **nothing** on wages, public companies, subsidies or the IMF.
- **ugtt_prio** (La Presse via AllAfrica, 1 Apr 2026), OPENED. Priorities: internal reform, transparency, independence of the union "face à toutes les tensions politiques". Selmi on Mosaïque FM: wants to "remettre le dialogue social sur sa trajectoire normale". Nothing on wages, privatisation, subsidies or the IMF.
- **Webdo 29 Mar 2026** (https://www.webdo.tn/fr/actualite/national/la-nouvelle-direction-de-lugtt-veut-relancer-le-dialogue-avec-le-gouvernement/395407/), OPENED but not used: dialogue is an "urgent" priority; the UGTT will ask for a meeting. Nothing on the 21 Jan strike.
- **HRW Sep 2026 briefing**: the hrw.org URL never appeared in a search result of this pass, so it was **not opened** and was removed from SRC. The Africanews piece of ~8 Jul 2026 (https://www.africanews.com/2026/07/08/human-rights-watch-raises-alarm-over-tunisian-crackdown-on-activists/) was opened: it says HRW found the situation "deteriorated dramatically" five years on, and that courts sentenced eight rights defenders; it gives **no** association counts or "conspiracy" figures and no title/date on the page. Not cited.
- **Therefore removed from the edition**: "37 people sentenced to 4–66 years", "at least 20 associations suspended between July 2025 and April 2026" (both came from the unverified 16 Oct text). TIMEP (opened) gives: 37 defendants convicted in April 2025 with sentences of **4 to 74 years**, upheld on appeal in November 2025 except for three appellants; at least **25 organisations** suspended over the past year under Decree 88; LTDH suspended April 2026. The question ctx for "Political trials are fair" uses "37 defendants" without a range.
- **Decree-law 54 year (2022)**: still not verified on an opened page. The edition no longer states the year anywhere (the ctx now says only "Decree-law 54"). Check if wanted.
- **161 seats**: confirmed by Le360/AFP (boycott22).
- **Wealth tax**: the 2026 draft proposed 1% above 5 million dinars (Ecofin, Oct 2025), but a Kapitalis piece of 12 Feb 2026 (opened) says the adopted tax varies "between 0.5% and 1%" with estimated wealth, from 1 Jan 2026, and gives no threshold. The edition therefore no longer states a rate or threshold (Bloomberg commit says only "a wealth tax"). The question on the wealth tax was dropped.

### New sources opened in this pass (all in SRC_TN; read these first when fact-checking)
- **ugtt_2027** (Tunisie Numérique/TAP, 2 Jul 2026): UGTT proposals to the Finance Minister for the 2027 budget: raise the income-tax exemption ceiling from 5,000 to 7,000 dinars and go from 7 to 9 brackets; "limit state use of Central Bank facilities to fund investment spending" (paraphrased by the fetch tool; the original sentence was not seen, so the cell is a lean, p=-1); rebalance domestic and external borrowing and restore national bond issuance; shift public companies from financing deficits to financing investments, rescue plan for CPG (Gafsa phosphate) and Tunisair, national reform fund; investment credits to 8 bn dinars; criticises the absence of measures protecting purchasing power and against precarious employment; asks for genuine dialogue on the 2027 bill. Does NOT mention a wealth tax, VAT, debt audit, IMF, wages, subsidies or privatisation.
- **bud27** (WebManagerCenter, 16 Oct 2026): draft 2027 law: spending 68.895 bn dinars (+8.37% on 63.575 bn in 2026), revenue 54.28 bn, **deficit 14.615 bn**, BCT facilities of **up to 9.8 bn dinars**, interest-free, 15 years, 3-year grace (Art. 12; "proposed authorisation"; departs from Art. 25 of the 2016 BCT statute). No wealth tax, no wages, no subsidies, no IMF in the article.
- **managers_b26** (Managers.tn, 8 Jan 2026): adopted 2026 budget: BCT lends the State **11 bn dinars** over 15 years, interest-free, 3-year grace, covering the whole deficit (>11 bn dinars; total budget ~79 bn); wealth tax plus an exceptional 4% contribution; **wage rises written into the law, bypassing UGTT/UTICA talks**; oil price assumption $63.3. No IMF mention.
- **ugtt_art15** (Business News, 26 Nov 2025): spokesman Sami Tahri on Express FM: art. 15 freezes or fixes wage rises by decree in public and private sectors, "une première historique", "l'État ne veut plus des syndicats"; 17 letters since 2022 unanswered; National Council early Dec; general strike not excluded. No government reply reported.
- **ugtt_imf** (AFP via Arab News, 1 May 2023): Taboubi: IMF conditions (sale of public companies, lifting subsidies on basic goods) would "impoverish the Tunisian people even more"; asks if negotiating has any value; the union backs Saïed's rejection of IMF "diktats"; talks stalled because Saïed had not committed to restructuring public bodies or lifting subsidies; IMF wants legislation to restructure 100+ state firms; Taboubi also demanded release of detained unionists.
- **public_assets** (La Presse, 6 Apr 2026, lapresse.tn URL): Saïed at the Bourguiba commemoration: some parties had considered selling the El Menzah Olympic complex and the Central Pharmacy; "Nous ne céderons pas nos institutions ni nos infrastructures publiques"; talks of "lobbies". The article does not use "privatisation" and does not name health, education or transport.
- **grads** (La Presse via AllAfrica, 8 Oct 2026): law **n° 2025-18 of 22 Dec 2025** on exceptional recruitment of long-term unemployed graduates, "portée par le Chef de l'État", recruitment in tranches over up to three years, competitions resumed at Health, Education, Transport, Security; Saïed received PM Sarra Zaâfrani Zenzri and Employment minister Riadh Chaouad. No numbers. It does not mention "Law 38" (Echaab's 2022 call is about Law 38; the relation between the two laws is not established here).
- **labour25** (APAnews, 21 May 2025): ARP adopted the ban on CDD and subcontracting for permanent tasks (guarding, cleaning, gardening) with **121 of 151 deputies for, none against, 4 abstentions**; exceptions for seasonal work and replacements; fines and up to 6 months' prison; business circles worried. No UGTT/UTICA/party reaction in the article.
- **migr25** (AllAfrica/La Presse? "Tunisie: Migration irrégulière – A la propagande mensongère…", mid-April 2025 by the URL id; page shows no date or outlet): Saïed denies any agreement on returns with the EU beyond the 2008 and 2011 ones; relies on international bodies incl. the IOM to speed voluntary returns (the article calls the pace "lent et faible"); refuses to be Europe's border guard or a resettlement country. **The date is inferred from the AllAfrica story id (20250414...); the outlet is not shown.** Check before publication.
- **norm_analysis** (The New Arab, 28 Nov 2023, by Basma El Atti): bill criminalising trade/communication/cooperation with Israel, 6–12 years and fines up to 100,000 dinars; 97 MPs asked urgent consideration; Saïed's letter: "endangers Tunisia's external security and interests"; "The word normalisation does not exist for me when it comes to Israel"; FM Nabil Ammar called the debate redundant. Does not mention Ennahdha, Echaab, PDL or UGTT.
- **gabes** (Kapitalis, 21 Oct 2025): Gabès regional UGTT (secretary Salaheddine Ben Hamed) called a general strike on 21 Oct 2025 for the immediate closure or relocation of the most polluting GCT units; ministers of Health and Equipment presented emergency measures and a roadmap for six unfinished projects, incl. suspending phosphogypsum discharges into the sea; tear gas and dozens arrested incl. minors. (Business News 22 Jan 2026, opened, adds: Gabès bar référé to suspend GCT units, hearing postponed to 12 Feb 2026; an expert says dismantling one unit would cost 5 bn dinars; 40,000–45,000 people reportedly at the 21 Oct strike. Not cited in SRC.)
- **timep** (TIMEP, 29 Jul 2026): public debt above 80% of GDP; inflation peaked above 10% in early 2023, now above 5%; youth unemployment ~38%; Decree 88 used to suspend NGOs, at least 25 over the past year, LTDH suspended April 2026, appeal postponed to 29 Jul; Saadia Mosbah 8 years (March 2026); lawyers' national strike June 2026; "conspiracy" case 37 convicted (4–74 years), upheld Nov 2025 except three; Ghannouchi life + 30; Moussi detained since Oct 2023, 10 years in March 2026; Saïed quoted calling opponents "traitors and terrorists"; EU border externalisation deal; a state of emergency "extended for the tenth time in January 2026" (not used).
- **pdl_congress** (Business News, 13 Aug 2026): PDL congress announced for 3–4 Oct 2026 to elect a new leadership; Moussi detained since 3 Oct 2023 (arrested near Carthage trying to file a challenge to presidential decrees on electoral districting); sentenced to 12 years in Dec 2025, reduced to 10 in March 2026, plus 2 years for criticising the electoral process. No policy statement.
- **march10** (Business News, 9 Jan 2026): PDL confirms taking part in the 10 Jan 2026 march "of opposition parties and movements" against the drift of executive power; it supports any peaceful citizens' movement, defends the right to political and associative organisation, calls itself attached to the Constitution and the "régime civil"; **Ennahdha will also take part**; internal PDL reservations about marching with Ennahdha. Another Business News article of 2 Jan 2026 (opened) announces the march but names no organiser. **The congress outcome (3–4 Oct 2026) was not found.**
- **PDL on 10 Jul 2026** (Business News, https://businessnews.com.tn/2026/07/11/le-pdl-defend-la-candidature-dabir-moussi-a-un-nouveau-mandat-elle-est-en-droit-de-se-presenter/1409759/), OPENED, not in SRC: only about Moussi's eligibility for a new party mandate under the statutes.

### Decision on a fifth force: NOT added
- **PDL**: three or four usable facts (2022 boycott, 10 Jan 2026 march, Moussi's detention and sentences, congress announced). No policy statement on economy, institutions, social issues or foreign policy found. About 5 of 26 questions could be coded, far from 12.
- **Attayar, Al Joumhouri, Ettakatol, Workers' Party, Al-Qotb**: only the 2022 joint boycott message (boycott, legitimacy, unilateral law) and the 2022 boycott list. Nothing from 2025–26 in the pages opened. They stay under "others".
- **Afek Tounes**: the only search returned no page about Afek itself.

### Question-set changes since 18 Oct (27 → 26 questions)
- **Dropped** (single-force or stale, not strengthened): "Annual tax on large fortunes", "Break the hold of monopolies", "Drop the 400 sponsorships", "Bring back party lists", "Public money for campaigns", "Voters can recall deputies" (the three electoral-law items are merged into "Keep the 2022 electoral law"), "Raise fuel prices gradually" (2022 only; replaced by "Keep subsidies on basic goods"), "Fight high prices case by case" (Echaab only), "Spend more to raise wages" (replaced by "Purchasing power before deficit").
- **Added**: "Keep subsidies on basic goods", "Purchasing power before deficit", "Keep public companies public", "Keep the ban on fixed-term jobs" (back, now with APAnews opened), "A legitimate Assembly", "Political trials are fair", "Freedom to march and strike", "Suspend associations under Decree 88", "Speed up voluntary returns" (back, with migr25), "Close polluting Gabès units".
- **Cells downgraded or removed as headline-only**: all `grads`/`public_assets`/`returns`/`d54_bill` cells now rest on opened pages. The "fuel price" cell for the 25 July camp (it was inferred from Echaab's 2022 statement) was removed. The `norm_bill` (New Arab 3 Nov 2023) page was never opened: the normalisation cell now cites `norm_analysis` (opened).

### Thin or inferred cells (check first)
1. `tn_25j` on "A legitimate Assembly" (+1, record, kabaria): no statement by Saïed; it is a lean from the ISIE continuing by-elections.
2. `tn_25j` on "Political trials are fair" (+1, record, aj_ghannouchi): "the authorities deny holding political prisoners" is an authorities' line, not a statement on trial fairness.
3. `tn_nahdha` on Decree 54 (+1), Parliament's powers (+1), electoral law (-1, via the FSN's reasons) and `tn_ugtt` on Decree 54 (+1): none names the topic; notes say "lean".
4. `tn_ugtt` on the Central Bank (-1): relies on the fetch tool's paraphrase of a TAP report (ugtt_2027).
5. `tn_ugtt` on "Close polluting Gabès units" (+2): this is the **regional** Gabès union, not the national leadership (the note says so).
6. `tn_25j` on "Keep subsidies" (+1, older): inferred from AFP 2023 ("had not committed to lifting subsidies"); no 2025–26 source.
7. `tn_echaab` on subsidies (+1, older), fixed-term jobs (+1, older), Parliament's powers (+1, older, from Dec 2021) are loose matches to the statements.
8. `tn_25j` on "Release jailed opponents" (-2) combines a TIMEP quote ("traitors and terrorists") with the authorities' denial.
9. Ministry names in `themes[].min` remain unverified on an opened page (only Social Affairs, Employment, Health, Equipment, Finance, Foreign Affairs and Justice appear in opened pages).
10. The UGTT strike of 21 Jan 2026: still not known whether it went ahead (webdo/businessnews pages on its postponement were never surfaced).

### Still thin (what a follow-up should do)
- Single-force questions: Constitutional Court (Echaab), voluntary returns (25 July), no foreign backing (Echaab), gas/renewables (Echaab).
- Ennahdha is coded on 10/26, mostly from one communiqué (14 Jan 2026) and 2022 boycott facts. A fuller programme or interview (economy, subsidies, migration, Decree 54) would let it be coded on more.
- Echaab's economic positions: no 2025–26 statement on the finance law, the IMF or the Central Bank was found (the search returned none).
- Government record not covered: bread/fuel subsidy decisions for 2025–26, the EU migration memorandum text, community companies, energy plan; the 2027 budget's wage and subsidy lines (not in the bud27 article).
- Municipal elections: Ayachi's timing could be confirmed with an ISIE statement.
