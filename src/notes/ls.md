# Lesotho — National Assembly election (due 2027) — research notes

STATUS: INCOMPLETE (research run interrupted 11 Oct 2026, 14:17 CEST).
- Web search budget for the turn was exhausted after 8 searches (budget shared with other agents).
- WebFetch then returned "session limit · resets 4:40pm (Europe/Paris)".
- Direct HTTPS to lestimes.com, lena.gov.ls, newsdayonline.co.ls, iec.org.ls is denied by the egress proxy (403), so no workaround.
- `src/editions/ls.js` has NOT been written yet: no party position has been verified so far.

Everything under "Verified" below was opened with WebFetch on 11 Oct 2026. Items under "Hypotheses" are NOT verified and must not be cited until opened.

---

## 1. Election facts (verified)

- **Wikipedia, “Next Lesotho general election”** (background only): https://en.wikipedia.org/wiki/Next_Lesotho_general_election
  - Election of the 120-member National Assembly “by October 2027”. No polling day announced.
  - MMP (mixed single vote with seat linkage): 80 single-member constituencies (FPTP) plus 40 nationwide compensatory PR seats.
  - Incumbent PM: Sam Matekane (RFP).
  - 2022 seats and leaders as listed on the page: RFP 57 (Sam Matekane), DC 29 (Mathibeli Mokhothu), ABC 8 (Nkaku Kabi), BAP 6 (Nqosa Mahao), AD 5 (Ntoi Rapapa), MEC 4 (Selibe Mochoboroane), LCD 3 (Mothetjoa Metsing), SR 2 (Teboho Mojapela), BNP 1 (Machesetsa Mofomobe), PFD 1 (Lekhetho Rakuoane), MPS 1 (Remaketse Sehlabaka), BCM 1 (Ts’epo Lipholo), HOPE 1 (Machabana Lemphane-Letsie), NIP 1 (Kimetso Mathaba).
  - Note: the SSRC/Kujenga Amani piece (below) says RFP won 56 seats; the 57 figure probably includes a later PR adjustment (see the IEC PR recount, Newsday 2023). To confirm.
- **Legal deadline: NOT YET VERIFIED.** The usual reading of the Constitution (s. 83: Parliament lasts five years from its first sitting, then stands dissolved; s. 84: general election within three months of dissolution) would put the vote between late 2027 and early 2028, not necessarily “by October 2027”. The WIPO text opened (https://www.wipo.int/wipolex/ru/text/476265) is the 1993 original and was truncated before ss. 83–84; it did not confirm this. Needs the consolidated constitution and the date of the first sitting of the 11th Parliament (October/November 2022).
- **IEC preparations (LENA, “Lesotho on track with constituency demarcation, voter registry”, dated 23 Aug, year not shown, probably 2025):** https://www.lena.gov.ls/lesotho-on-track-with-constituency-demarcation-voter-registry/
  - IEC says Lesotho is “on the right path in preparing for the 2027 general elections”. Lydia Macheli (IEC) flags “the absence of formal regulations on constituency demarcation”.
- **IEC website, News & Media** (opened 11 Oct 2026): https://iec.org.ls/news-and-media/
  - 20 Jul 2026: IEC chair and a commissioner met the Minister of Local Government and Chieftainship on **harmonising National Assembly and local government elections, to be held on the same day**.
  - 15 Jun 2026: constituency assessment visits ahead of a voter registration intensification programme.
  - 18 Aug 2026: Tebello Nthakong appointed Director of Elections.
  - 1 Oct 2026: two-day High-Level Electoral Dialogue in Maseru (electoral reform, inclusion, public confidence).
  - No general election date published.
- **IEC website, Commission page**: https://iec.org.ls/commission/ — Chair Rev. Dr John Maphephe; commissioners Pontšo ’Mamatlere Matete and Dr Chelete Monyane.
- **IEC home page**: https://iec.org.ls/ — 59 registered political parties, 80 constituencies, more than 1,650 voting stations.
- **Lesotho Times, “Govt pushes for IEC commissioners’ appointment”, 16 Jan 2026**: https://lestimes.com/?p=89431
  - Recruitment of commissioners began in July 2025. The Forum of Political Parties sent five names to the Council of State, which recommends three. Two unsuccessful applicants (Tumisang Mosotho, Peshoane Tsikoane) lost in the Constitutional Court and appealed.
  - Law Minister Richard Ramoeletsi: the appeal “does not stay the process”; the IEC cannot run elections without commissioners.
  - DC: the delay threatens the integrity of the electoral system. BNP leader Machesetsa Mofomobe petitioned the Council of State and threatened court action. Yearn for Economic Sustainability (YES) also wrote to the Council of State.
- **Lesotho Times, “Maphephe outlines vision for IEC”, 13 Feb 2026**: https://lestimes.com/?p=89702
  - New five-year commission: Maphephe (chair), Matete, Monyane. Priorities: a stable voter register (“first priority”), an Electoral Register Bill linked to the national ID system, automatic registration with SMS or email alerts to young people turning 18, higher turnout, procurement controls.
- **Lesotho Times, “Matlanyane relents to IEC pressure”, 13 Jun 2026**: https://lestimes.com/?p=90738
  - Director of Elections Mpaiphele Maqutu resigned in February 2026. Finance Minister Retšelisitsoe Matlanyane first refused, then on 4 Jun 2026 accepted, acting director Lydia Macheli as the IEC’s chief accounting officer.
- **Newsday, “DC wants IEC dissolved”, 26 Jun 2023** (older background): https://newsdayonline.co.ls/dc-wants-iec-dissolved/
  - The IEC admitted miscalculating PR seats after the 2022 election (DC 11→8, AD 3→2). DC leader Mokhothu threatened to ask a court to declare the IEC incompetent.
- **Lesotho Times, “Mokhochane decries power vacuum at IEC”** (undated, about 2025): https://lestimes.com/mokhochane-decries-power-vacuum-at-iec/
  - Outgoing chair Mphasa Mokhochane: the voters’ roll is “unclean”. Registration restarted with a target of about 800,000 registrants, against 1.4 million on the old roll.

## 2. National reforms and the Omnibus bill (verified)

- **Mayet & Associates (law firm), “Lesotho enacts landmark Tenth Constitutional Amendment”, 19 Aug 2025**: https://zmayetlaw.co.ls/lesotho-enacts-landmark-tenth-constitutional-amendment/
  - Tenth Amendment to the Constitution Act, 2025 (Act No. 2 of 2025), published 13 Aug 2025.
  - Contents: official languages extended (Sesotho, English, isiXhosa, isiPhuthi, sign language); age of majority 18; affirmative action; public-interest standing; Parliament made an independent institution (Parliamentary Service, Service Commission, Parliament Budget Office); a Supreme Audit Institution replaces the Auditor-General, with rules on debt management and supplementary budgets; a more independent Human Rights Commission; anti-corruption commission entrenched in the Constitution; National Security Council, National Security Commission and Independent Security Sector Oversight Authority; Media Council and Media Ombudsman; **treaties to be approved by Parliament before ratification**.
  - The article says nothing about PM powers, floor-crossing, no-confidence votes, the Senate or the electoral model. These are probably in the parts not yet enacted (special-majority and referendum parts). To verify.
- **Lesotho Times, “Govt accelerates Tenth Amendment implementation”, 8 Aug 2026**: https://lestimes.com/?p=91227
  - Consultations (about 7 Aug 2026) on a National Reforms Implementation Authority (NRIA) to replace the National Reforms Authority, with an 18-month mandate to get the enabling laws passed.
  - DPM Nthomeng Majara: “These reforms belong to Basotho.” Law Minister Ramoeletsi says delays came from legal challenges, institutional transitions, resources and political differences. The remaining constitutional amendments are to follow after that.
- **SSRC Kujenga Amani, “Lesotho’s National Assembly and Senate at loggerheads over peace reforms”, 3 Sep 2025** (author Sean Maliehe): https://kujenga-amani.ssrc.org/2025/09/03/lesothos-national-assembly-and-senate-at-loggerheads-over-peace-reforms/
  - Omnibus bill (10th and 11th amendments) tabled May 2023, with 90 amendments grouped by threshold: simple majority, two-thirds, referendum. Stuck between the National Assembly and the Senate. Section 83 dissolution advice has been used to block no-confidence motions. Public demand to limit PM powers.
- **ConstitutionNet, “The State of Lesotho’s Constitutional Reforms: Progress or Stagnation?”, 29 Jun 2023** (Hoolo ’Nyane, older background): https://constitutionnet.org/news/state-lesothos-constitutional-reforms-progress-or-stagnation
  - The 2022 recall of the dissolved Parliament to pass the Tenth Amendment was voided by the courts. The Matekane government planned to split the bill into three (ordinary, special-majority, referendum).

## 3. Parties: NOTHING VERIFIED YET

Planned set (to confirm after research): RFP (governing, Matekane) · DC (main opposition, Mokhothu) · ABC (Kabi) · BAP · LCD (Metsing) and/or MEC (Mochoboroane). Confirm which parties are inside the governing coalition in 2026 (AD? MEC? BNP?), and whether BAP’s leader is still Nqosa Mahao.

## 4. Candidate URLs seen in search results but NOT yet opened (open before citing)

- https://lestimes.com/disgruntled-rfp-mps-petition-matekane/
- https://lestimes.com/matekane-admits-trouble-in-rfp/
- https://lestimes.com/?p=91345 (“Matekane challenged!”)
- https://lestimes.com/birds-eye-view-of-lesotho-politics/
- https://lestimes.com/iec-commissioner-delays-spark-political-alarm/ (first fetch failed)
- https://lestimes.com/court-suspends-iec-commissioners-appointments/
- https://lestimes.com/mosotho-tsikoane-escalate-iec-fight-to-appeal-court/
- https://lestimes.com/?p=89661 (“Why Maqutu resigned”)
- https://www.lena.gov.ls/pm-calls-for-swift-action-on-electoral-reforms-ahead-of-2027-elections/ (fetch returned a server error; retry)
- https://www.gov.ls/download/king-letsie-111-appointed-independent-electoral-commission-chairperson-and-commissioners/
- https://www.channelafrica.co.za/channelafrica/news/lesotho-appoints-new-iec-commissioner/
- https://bti-project.org/en/reports/country-report/LSO (BTI 2026 country report)
- https://constitutionnet.org/news/lesotho-government-announces-intent-split-failed-omnibus-constitutional-reform-bill-three
- https://constitutionnet.org/news/lesothos-government-proposes-constitutional-amendments-while-civil-society-pushes-new
- https://theconversation.com/lesotho-needs-constitutional-reforms-to-help-gain-political-stability-but-the-latest-attempt-is-flawed-237905
- https://www.eeas.europa.eu/delegations/lesotho/roadmap-lesothos-future-elections-eu-electoral-follow-mission-final-report-published_en
- https://www.idea.int/news/lesotho-takes-strategic-step-towards-inclusive-electoral-participation
- https://en.wikipedia.org/wiki/Cabinet_of_Sam_Matekane (ministry names for themes; background only)
- https://allafrica.com/stories/202210090017.html (Matekane, 2022: “None of the parties share the RFP’s revolutionary ideology”)

## 5. Hypotheses to check (model background knowledge, UNVERIFIED, do not cite)

- US “reciprocal” tariff on Lesotho announced at 50% in April 2025, later cut to 15%. AGOA lapsed on 30 Sep 2025; status of any 2026 renewal unclear. Textile job losses in Maseru and Maputsoe.
- The government declared a state of disaster over youth unemployment in mid-2025.
- Lesotho Highlands Water Project Phase II (Polihali dam, Mohale and Polihali tunnel): delays, royalties from South Africa, possible water sales to Botswana.
- RFP internal splits and petitions by MPs (2025–2026); contracts linked to the PM’s business group.
- Floor-crossing, no-confidence and Section 83 dissolution rules sit in the unpassed parts of the Omnibus bill.
- Possible new parties before 2027 (breakaways from RFP or ABC).

## 6. Open doubts

- Exact legal deadline (October 2027, or up to about three months after Parliament’s five-year term ends?).
- Whether national and local government elections will be merged, which could move the date.
- Current coalition membership and the opposition line-up for 2027.

---

# RUN 2 (16 Oct 2026) — new verified items (opened with WebFetch this run)

## Party landscape
- **Wikipedia, Cabinet of Sam Matekane** (background, ministries): https://en.wikipedia.org/wiki/Cabinet_of_Sam_Matekane — coalition formed 4 Nov 2022: RFP, AD, MEC; BAP joined after failed no-confidence vote Oct 2023; LCD and LPC listed as members (no date). Ministries (as listed, Nov 2023): Defence & National Security; Health (Mochoboroane, MEC); Education & Training (Rapapa, AD); Information, Communications, Science, Technology & Innovation (Nthati Moorosi); Finance & Development Planning (Matlanyane); Trade, Industry & Small Business (Shelile); Local Government, Chieftainship, Home Affairs & Police (Lephema); Foreign Affairs & International Relations (Mpotjoane); Agriculture, Food Security & Nutrition (Mofosi); Natural Resources (Moleko); Gender, Youth & Social Development (Lesaoana); Public Works & Transport (Moteane); Labour & Employment (Mokhosi); Energy (Mahao, BAP — at that time); Tourism, Sports, Arts & Culture; Public Service; Environment & Forestry; Law & Justice (Ramoeletsi). No 2024–26 reshuffles on page.
- **Lesotho Times, "Matekane challenged!", 22 Aug 2026** (Mohloai Mpesi): https://lestimes.com/?p=91345 — RFP members Takane and Letuka threaten court over an 11 Aug 2026 circular requiring HQ approval for gatherings outside own constituencies; "We are not against Mr Matekane as a leader at all." SG = Nthati Moorosi. No other parties.
- https://lestimes.com/birds-eye-view-of-lesotho-politics/ = 2017 column (Sejanamane) — useless.

## Budget 2026/27 (Feb 2026)
- **Lesotho Times, "National budget faces opposition challenge", 13 Feb 2026** (Mpesi): https://lestimes.com/?p=89723 — DC/Mokhothu (Leader of the Opposition) wants budget deferred until contingency-fund spending is investigated; asked Speaker for special audit; "about 99%" of contingency spending fails constitutional tests. BAP/Mahao (opposition): poverty rose 49% (2017) → 57%; "Structurally, more and more people are getting poorer over time." AGOA extended one year; MCC II termination cost US$400–500m (Hakane). Speaker Tlohang Sekhamane.
- **Lesotho Times, "Budget fails to address unemployment and poverty – MPs", 19 Feb 2026** (Mpesi): https://lestimes.com/?p=89734 — agriculture M1.1bn (from M1.3bn); National Volunteer Corps +2,500 graduate placements, 50% stipend subsidy for private hosts; 2% civil-service raise; Youth Development Bill (youth reps on boards); PM pledged 62,000 youth jobs after declaring unemployment a national disaster. DC/Mokhothu: no job numbers, 2,500 too few, 2% too low vs 4.5–4.7% inflation, ID/passport delays, fertiliser shortages. ABC/Kabi: agriculture cut "shot itself in the foot"; shift infrastructure money to reach M5bn for agriculture. BAP (Tšeliso Moroko, Matala MP, defected from RFP to BAP that week): rhetoric, no detail on jobs. HOPE/Lemphane-Letsie: "discipline" 30+ times.
## Jobs
- **EWN/AFP, "Lesotho invokes state of disaster to tackle unemployment", 8 Jul 2025**: https://www.ewn.co.za/2025/07/08/lesotho-invokes-state-of-disaster-to-tackle-unemployment — two-year state of disaster (notice 7 Jul 2025); ministries told to put 2% of budgets to job creation; 50% US "Liberation Day" tariff (paused); up to 40,000 jobs at risk if AGOA not renewed; youth unemployment 38% (Feb 2025, finance minister); activist charged with sedition after video criticising govt inaction.
- **The Reporter, "Youth jobs crisis: govt under fire", 5 Aug 2025**: https://www.thereporter.co.ls/2025/08/05/youth-jobs-crisis-govt-under-fire/ — youth coalition (BachaShutDown) says govt too slow; no parties named.

## Opposition statements (verified, run 2)
- **Lesotho Times, "Govt failing Basotho – Mahao", 13 Feb 2026** (Seithati Motsoeneng): https://lestimes.com/?p=89689 — BAP leader Mahao at Likileng rally: >20,000 jobs lost since govt took office; handouts "to buy loyalty"; M3.5bn spent without parliamentary approval; M22m for Ha-Belo factories missing. **Mahao fired as Energy Minister Nov 2024; BAP "remains in the coalition because four of its six MPs stayed"; Mahao's challenge to Speaker's ruling on opposition status pending at ConCourt.** Govt spokesperson Boitelo Rabele: claims unproven, political.
- **The Reporter, "Youth scoff at PM's promises", 12 Jun 2025** (Neo Kolane): https://www.thereporter.co.ls/2025/06/12/youth-scoff-at-pms-promises/ — PM pledged at least **70,000** youth job opportunities (public works, agriculture, energy, sanitation, ICT), SEBABATSO programme, procurement reserved for youth/women/disabled, possible early retirement. DC/Mokhothu: "the government claims it will employ 70,000 youth. That is simply not true." (Note: Feb 2026 Lesotho Times says 62,000.)
- **Newsday, "Opposition seeks SADC intervention", 12 Aug 2026**: https://newsdayonline.co.ls/opposition-seeks-sadc-intervention/ — Mokhothu letter 3 Aug 2026 to SADC chair Mnangagwa, co-signed ABC, BNP, BAP, Mpulule Political Summit, UAT, PFD: executive non-compliance with court orders (DPP suspension ruled unlawful, RSL commissioner reinstatement, 77 NSS officers expelled unlawfully, Ombudsman barred, Correctional salaries, chiefs). Threaten to stop participating in reform meetings.
- **Lesotho Times, "Opposition blasts Matekane over diamond benefit pledge", 27 Jun 2026** (Mpesi): https://lestimes.com/?p=90835 — PM in Botswana says diamonds should benefit citizens; Botswana–Lesotho Bi-National Commission. VAT Amendment Bill (VAT on imported mining equipment, now zero-rated) revived in 11th Parliament; opposition says governing party defeated reintroduction. DC/Mokhothu: four years of inaction on beneficiation; sale of mining machinery to foreigners. BAP/Mahao: Botswana cutting & polishing model; mine owners lobbied/bribed MPs against VAT bill. BNP/Mofomobe: PM never discussed bigger shareholding or auction house; "bluffing". Minister of Energy and Mining **Lejone Mpotjoane**: new Mining Bill for local benefits; VAT bill would raise costs and could close mines.
- **Public Eye, "Mokhothu calls for action as job panic looms", 22 Apr 2025**: https://publiceyenews.com/2025/04/22/mokhothu-calls-for-action-as-job-panic-looms/ — DC press conf 11 Apr 2025: diplomatic engagement with Washington; emergency economic council; diversify markets incl. AfCFTA; short-term worker protections and subsidies for affected households. Textile >30,000 workers.
- **Newsday, "Opposition tears into budget speech", 27 Feb 2024** (older, 2024/25 budget): https://newsdayonline.co.ls/opposition-tears-into-budget-speech/ — BNP/Mofomobe: PM has personal mining interests, stop PM striking deals with mining companies; UAT/Phamotse: contracts to officials' businesses.
- **Public Eye, "PM unleashes army to curb Famo terror", 6 Aug 2024** (older): https://publiceyenews.com/2024/08/06/pm-unleashes-army-to-curb-famo-terror/ — 12 famo groups outlawed May 2024, gazetted as terrorist orgs; PM told LDF commander to end killings "by any means necessary". BNP/Mofomobe: order "illegitimate". DC/Mokhothu: agencies must act "within the perimeters of law". PFD/Rakuoane: "militarising community safety".
- https://lestimes.com/major-defections-rock-parties-ahead-of-polls/ = 2022 article (useless).

## Reforms (run 2)
- **LENA, "Efforts to reinstate 11th Amendment to Constitution underway"** (dated "Jun. 21", year not shown; likely 2025 or 2026): https://www.lena.gov.ls/efforts-to-reinstate-11th-amendment-to-constitution-underway/ — DPM Majara: amend Standing Order 105 to let Parliament reinstate the 11th Amendment.
- **AllAfrica, "Lesotho: More Pressure to Scrap Tenth Amendment", 15 Sep 2025**: https://allafrica.com/stories/202509150672.html — activist Kananelo Boloetse + Advocates for the Supremacy of the Constitution, and Law Society, sue: Tenth Amendment needed a referendum (s.85(3)); unnamed parties call it unlawful. SADC: Act "removes the Kingdom of Lesotho from the agenda of the Organ Troika".

## Water / human rights (run 2)
- **IJR (Crystal Orderson), "Time to Rethink Water Deal, Says Lesotho", 10 Apr 2026**: https://www.ijr.org.za/home/wp-content/uploads/2026/04/Time-to-Rethink-Water-Deal-Says-Lesotho_10-Apr-2026-1.pdf — Natural Resources Minister Mohlomi Moleko leads LHWP treaty/royalty review; royalties ~US$300m/yr (~10% of budget); compensation framework expires 2044; Phase 2 completion 2028; Moleko: "These dams could have been built in South Africa"; affected communities should be better off.
- **EWN, "Lesotho pushes for bigger share in key water deal with South Africa", 30 Mar 2026**: https://www.ewn.co.za/2026/03/30/lesotho-pushes-for-bigger-share-in-key-water-deal-with-south-africa — LHWP ~10% of economy; only Prof Mike Muller quoted.
- **Amnesty International, Lesotho 2025 (via ecoi.net)**: https://www.ecoi.net/en/document/2139341.html — Tšolo Thakeli arrested June 2025, re-arrested, charged with sedition; protest permits denied from June 2025 (textile job losses); Polihali workers' strike Sept 2025; Correctional Services commission report 16 Jun 2025 (assaults, one death), tabled redacted Aug 2025; USAID cuts Jan 2025: ~1,500 donor-funded health workers lost jobs; Polihali: 18 communities (~1,600 people) complaint to AfDB IRM Sept 2025; Phase II ~US$3bn, now 2029; unemployment ~30%, ~50% for ages 15–24 (LFS 2024); UPR Sept 2025: noted (did not accept) abolition of death penalty and decriminalising same-sex relations.

## More verified items (run 2, opened 16 Oct 2026)
- **Lesotho Times, "ABC unveils 'strategic plan'", 13 Feb 2026** (Sekoboto): https://lestimes.com/?p=89691 — youth corporations; restructure decentralisation to empower local/district/community councils (Kabi: "We have to strengthen local governance..."); 70,000-jobs plan "relies mainly on the public service"; SADC/AU/UN standing; membership 100,000.
- **Lesotho Times, "Kabi petitions Speaker to recall Parly over fuel crisis", 2 Apr 2026**: https://lestimes.com/?p=90146 — petrol +M6.70/7.35, diesel +M13.10, paraffin +M13.30; govt subsidy M2 (petrol, diesel), M5 (paraffin), announced by PM. Kabi: recall Parliament, direct govt to subsidise; no fuel or food reserves; 15% public pay rise instead of 2%; M250 pension increase instead of M50; fund via SACU, LHWP royalties, taxes. ABC spokesperson Mphonyane Lebesa: ~6,000 of 7,000 census enumerator posts went to ruling coalition parties.
- **Lesotho Times, "Kabi warns Matekane over youth joblessness", 2025 (undated; refers to 19 Feb budget and July tariff deadline)**: https://lestimes.com/kabi-warns-matekane-over-youth-joblessness/ — ABC: each ministry M20m for youth jobs; redirect land from housing to agriculture (arable land 11%); raise factory wages (ABC-led govt raised lowest wage M1,500→>M2,000); block farming; textiles 31,000 workers.
- **Lesotho Times, "SADC snubs opposition", 22 Aug 2026**: https://lestimes.com/?p=91352 — SADC summit communique silent; PM: no contempt where courts did not expressly order remedies; appealed to opposition to return to reforms table. Mokhothu: "Until the government changes, we will continue to suspend our participation in the reforms process."
- **Lesotho Times, "Opposition hits back at Matekane", 15 Aug 2026**: https://lestimes.com/?p=91295 — Mokhothu 16-page reply (10 Aug); "We remain committed to the reforms process; however, our position has not changed"; PM relies on sub judice, says ConCourt didn't expressly order DPP Motinyane's reinstatement.
- **GroundUp via Bizcommunity, "Lesotho aims for 10% tariff on exports to US", 6 Aug 2025**: https://www.bizcommunity.com/article/lesotho-aims-for-10-tariff-on-exports-to-us-624641a — 50% → 10% (90 days) → 15% from 7 Aug 2025; Trade Minister Mokhethi Shelile (Trade, Industry and Business Development): continue negotiating for minimum tariffs; "relationship needs continuous nurturing".
- **Lesotho Tribune, "Basotho Face in South Africa What Palestinians Face in Israel — Mofomobe", 17 Aug 2025**: https://lesothotribune.co.ls/basotho-face-in-south-africa-what-palestinians-face-in-israel-mofomobe/ — BNP: permanent immigration arrangement with SA (San Marino/Vatican/Andorra models), not temporary permits.
- **Lesotho Times, "Mofomobe slams Matekane", 4 Jul 2026**: https://lestimes.com/?p=90910 — anti-immigrant violence in SA; govt buses only to Durban; Mofomobe: repatriation across SA; 80% of Basotho don't qualify for general work permits. Matekane (Accountability Summit): passports in 4 days, backlog cleared in 3 months; "cannot continue relying on other countries" for jobs; "The most sustainable solution is to create home-based opportunities." DPM Majara: 42% below poverty line, 30% youth unemployment, at least 10,000 jobs a year, commercialise agriculture. Former minister Lebona Lephema (bus initiative).
- **Lesotho Times, "Govt to increase minimum wage", 23 Apr 2026**: https://lestimes.com/?p=90265 — Labour Minister Tšeliso Mokhosi: Wages and Conditions of Employment Advisory Board (Labour Act 2024); textile/factory +4%, private sector +3%, others +4.5%, retroactive 1 Apr 2026; employers and workers agreed; ~27 labour inspectors for 33,000 businesses.
- **Lesotho Times, "'Corruption has worsened under Matekane' – Mokhothu", 11 Jun 2025**: https://lestimes.com/?p=87249 — cabinet a "tender committee"; road, fertiliser tenders; Maseru main circle contractor; LEC; PAC recommended dismissing Public Works Minister Matjato Moteane (former company and airport refurbishment). Matekane: bring evidence and he will "expel them and ensure they are prosecuted". Mokhothu says DC will win "the 2028 elections" (sic).
- **Lesotho Times, "Govt, IEC at war", 4 Jun 2026**: https://lestimes.com/?p=90697 — Finance Minister refused to designate acting director Macheli as CAO citing DCEO probe that DCEO denies.
- **Lesotho Times, "MPs call for drastic curbing of international trips", 26 Mar 2025**: https://lestimes.com/mps-call-for-drastic-curbing-of-international-trips/ — RFP MPs Tšeliso Moroke (Matala) and Moeketsi Motšoane moved 50% cut; trips budget +102% in 2024/25, +72% in 2025/26; DC MP Thabiso Lekitla: drop business class?; BNP Mofomobe: benchmarking trips unjustified; LCD Metsing: case-by-case instead of blanket cut. Committee report 10 Mar 2025.
- **GroundUp, "Health Minister confident Lesotho can manage without US funding...", 26 Mar 2025**: https://groundup.news/article/health-minister-confident-lesotho-can-manage-without-us-funding-but-jobs-are-already-being-lost — Mochoboroane: absorb workers on payroll "but our current budget does not cover them"; ≥805 health workers lost jobs. (Not used: no opposition position found.)
- https://lestimes.com/opposition-leaders-vow-to-narrow-ideological-differences/ — undated, DC–BNP rapprochement, no policies (not used).
