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
