/* "Prépare ton vote" data: official electoral body, check page and 2–4 dated, sourced facts per country.
   Researched 18 Oct 2026. Every item has a source key in the country's src. d = ISO date of the fact (deadline or announcement) or null. */
const PREP = {
  cv: {
    emb: { name: "Comissão Nacional de Eleições", short: "CNE", url: "https://www.cne.cv" },
    items: [
      { d: "2026-09-11", src: "lusa_cal", t: {
        en: "Voter registration has been suspended since 11 September 2026. You can vote on 15 November only if you are already registered.",
        fr: "Les inscriptions sur les listes électorales sont suspendues depuis le 11 septembre 2026. Tu peux voter le 15 novembre seulement si tu figures déjà sur les listes.",
        pt: "O recenseamento eleitoral está suspenso desde 11 de setembro de 2026. Só podes votar a 15 de novembro se o teu nome já constar dos cadernos eleitorais.",
        sw: "Usajili wa wapiga kura umesitishwa tangu tarehe 11 Septemba 2026. Unaweza kupiga kura tarehe 15 Novemba tu ikiwa tayari umesajiliwa.",
        ar: "عُلِّق تسجيل الناخبين منذ 11 سبتمبر 2026. لا يمكنك التصويت في 15 نوفمبر إلا إذا كنت مسجَّلًا من قبل."
      } },
      { d: "2026-10-26", src: "lusa_cal", t: {
        en: "Living abroad? The CNE sets the polling stations outside Cabo Verde by 26 October 2026.",
        fr: "Tu vis à l’étranger ? La CNE fixe les bureaux de vote hors du Cap-Vert au plus tard le 26 octobre 2026.",
        pt: "Vives no estrangeiro? A CNE define as assembleias de voto fora de Cabo Verde até 26 de outubro de 2026.",
        sw: "Unaishi nje ya nchi? CNE itapanga vituo vya kupigia kura nje ya Cabo Verde kufikia tarehe 26 Oktoba 2026.",
        ar: "هل تقيم في الخارج؟ تحدد CNE مكاتب الاقتراع خارج الرأس الأخضر في موعد أقصاه 26 أكتوبر 2026."
      } },
      { d: "2026-11-15", src: "lusa_cal", t: {
        en: "You vote on Sunday 15 November 2026. The official campaign runs from 29 October to 13 November.",
        fr: "Tu votes le dimanche 15 novembre 2026. La campagne officielle se déroule du 29 octobre au 13 novembre.",
        pt: "Votas no domingo, 15 de novembro de 2026. A campanha oficial decorre de 29 de outubro a 13 de novembro.",
        sw: "Utapiga kura Jumapili tarehe 15 Novemba 2026. Kampeni rasmi ni kuanzia tarehe 29 Oktoba hadi 13 Novemba.",
        ar: "تُدلي بصوتك يوم الأحد 15 نوفمبر 2026. وتمتد الحملة الرسمية من 29 أكتوبر إلى 13 نوفمبر."
      } },
      { d: null, src: "cne_guide", t: {
        en: "You can vote if you are a Cabo Verdean citizen aged 18 or over and registered on the voter roll.",
        fr: "Tu peux voter dès 18 ans si tu as la nationalité cap-verdienne et que tu figures sur les listes électorales.",
        pt: "Podes votar a partir dos 18 anos se tiveres nacionalidade cabo-verdiana e o teu nome constar dos cadernos eleitorais.",
        sw: "Unaweza kupiga kura ukiwa raia wa Cabo Verde mwenye umri wa miaka 18 au zaidi na umesajiliwa kama mpiga kura.",
        ar: "يمكنك التصويت إذا كنت مواطنًا من الرأس الأخضر بلغ 18 عامًا فأكثر ومسجَّلًا في قوائم الناخبين."
      } }
    ],
    src: {
      lusa_cal: { o: "Lusa (via CM Jornal)", t: "Candidaturas às presidenciais de Cabo Verde devem ser entregues até 16 de setembro", d: "3 Aug 2026", u: "https://www.cmjornal.pt/mundo/detalhe/candidaturas-as-presidenciais-de-cabo-verde-devem-ser-entregues-ate-16-de-setembro" },
      cne_guide: { o: "Comissão Nacional de Eleições (CNE)", t: "Cartilha do Eleitor", d: "2019", u: "https://cne.cv/wp-content/uploads/2020/04/CARTILHA-DO-ELEITOR-VS-FINAL.pdf" }
    }
  },

  gm: {
    emb: { name: "Independent Electoral Commission", short: "IEC", url: "https://iec.gm" },
    items: [
      { d: "2026-05-21", src: "dubawa_reg", t: {
        en: "Supplementary voter registration was scheduled from 8 April to 21 May 2026. It is now closed.",
        fr: "L’inscription électorale complémentaire était prévue du 8 avril au 21 mai 2026. Elle est maintenant close.",
        pt: "O recenseamento eleitoral suplementar estava previsto de 8 de abril a 21 de maio de 2026. Já está encerrado.",
        sw: "Usajili wa ziada wa wapiga kura ulipangwa kuanzia tarehe 8 Aprili hadi 21 Mei 2026. Sasa umefungwa.",
        ar: "كان التسجيل التكميلي للناخبين مقررًا من 8 أبريل إلى 21 مايو 2026. وقد أُغلق الآن."
      } },
      { d: "2026-07-03", src: "point_list", t: {
        en: "The IEC said the provisional voter list would be published from 7 July 2026 at registration centres nationwide.",
        fr: "L’IEC a annoncé la publication de la liste électorale provisoire à partir du 7 juillet 2026, dans les centres d’inscription du pays.",
        pt: "A IEC anunciou a lista eleitoral provisória a partir de 7 de julho de 2026, nos centros de recenseamento de todo o país.",
        sw: "IEC ilisema orodha ya muda ya wapiga kura ingechapishwa kuanzia tarehe 7 Julai 2026 katika vituo vya usajili kote nchini.",
        ar: "أعلنت IEC أن قائمة الناخبين المؤقتة ستُنشر ابتداءً من 7 يوليو 2026 في مراكز التسجيل في أنحاء البلاد."
      } },
      { d: "2026-07-03", src: "point_list", t: {
        en: "Lost or damaged voter card? The IEC announced a short replacement window before polling day. No dates were given.",
        fr: "Ta carte d’électeur est perdue ou abîmée ? L’IEC a annoncé une courte période de remplacement avant le vote, sans donner de dates.",
        pt: "Perdeste ou estragaste o cartão de eleitor? A IEC anunciou um curto período de substituição antes da votação, sem indicar datas.",
        sw: "Kadi yako ya mpiga kura imepotea au kuharibika? IEC ilitangaza muda mfupi wa kubadilisha kadi kabla ya kupiga kura, bila kutaja tarehe.",
        ar: "هل فقدت بطاقة الناخب أو تلفت؟ أعلنت IEC عن فترة قصيرة لاستبدالها قبل الاقتراع دون تحديد مواعيد."
      } },
      { d: "2026-12-05", src: "point_list", t: {
        en: "You vote on Saturday 5 December 2026 if you are Gambian, registered and 18 by that day.",
        fr: "Tu votes le samedi 5 décembre 2026 si tu es gambien, inscrit sur les listes et âgé de 18 ans à cette date.",
        pt: "Votas no sábado, 5 de dezembro de 2026, se fores gambiano, estiveres recenseado e tiveres 18 anos nessa data.",
        sw: "Utapiga kura Jumamosi tarehe 5 Desemba 2026 ikiwa wewe ni Mgambia, umesajiliwa na umefikisha miaka 18 kufikia siku hiyo.",
        ar: "تُدلي بصوتك يوم السبت 5 ديسمبر 2026 إذا كنت غامبيًا ومسجَّلًا وبلغت 18 عامًا في ذلك اليوم."
      } }
    ],
    src: {
      dubawa_reg: { o: "Dubawa", t: "What you need to know about 2026 supplementary voter registration in Gambia", d: "9 May 2026", u: "https://dubawa.org/what-you-need-to-know-about-2026-supplementary-voter-registration-in-gambia/?amp=1" },
      point_list: { o: "The Point", t: "IEC deletes names of over 14,000 voters for multiple registrations in 2026", d: "3 Jul 2026", u: "https://thepoint.gm/africa/gambia/headlines/iec-deletes-names-of-over-14000-voters-for-multiple-registrations-in-2026" }
    }
  },

  ng: {
    emb: { name: "Independent National Electoral Commission", short: "INEC", url: "https://inecnigeria.org" },
    check: { url: "https://cvr.inecnigeria.org/vvs", src: "bella_guide" },
    items: [
      { d: "2026-10-09", src: "techeconomy_pvc", t: {
        en: "INEC set 9 October 2026 as the start of nationwide Permanent Voter Card (PVC) collection, at local government centres. No end date is published.",
        fr: "L’INEC a fixé au 9 octobre 2026 le début du retrait national des cartes d’électeur permanentes (PVC), dans les centres des collectivités locales. Aucune date de fin n’est publiée.",
        pt: "A INEC fixou 9 de outubro de 2026 como início do levantamento nacional dos cartões de eleitor permanentes (PVC), nos centros das autarquias locais. Não há data final publicada.",
        sw: "INEC iliweka tarehe 9 Oktoba 2026 kuwa mwanzo wa kuchukua Kadi za Kudumu za Mpiga Kura (PVC) nchini kote, katika vituo vya serikali za mitaa. Hakuna tarehe ya mwisho iliyochapishwa.",
        ar: "حددت INEC يوم 9 أكتوبر 2026 بداية لاستلام بطاقات الناخب الدائمة (PVC) في أنحاء البلاد، في مراكز الحكومات المحلية. ولم يُنشر موعد للانتهاء."
      } },
      { d: "2026-07-26", src: "opinion_cvr", t: {
        en: "The third phase of Continuous Voter Registration (CVR) closed on 26 July 2026. INEC says you must be registered to vote in 2027.",
        fr: "La troisième phase de l’inscription continue des électeurs (CVR) a pris fin le 26 juillet 2026. L’INEC indique qu’il faut être inscrit pour voter en 2027.",
        pt: "A terceira fase do recenseamento contínuo de eleitores (CVR) terminou a 26 de julho de 2026. A INEC diz que é preciso estar recenseado para votar em 2027.",
        sw: "Awamu ya tatu ya Usajili Endelevu wa Wapiga Kura (CVR) ilifungwa tarehe 26 Julai 2026. INEC inasema lazima uwe umesajiliwa ili kupiga kura mwaka 2027.",
        ar: "أُغلقت المرحلة الثالثة من التسجيل المستمر للناخبين (CVR) في 26 يوليو 2026. وتقول INEC إنه يجب أن تكون مسجَّلًا للتصويت في 2027."
      } },
      { d: "2027-01-16", src: "techeconomy_pvc", t: {
        en: "You vote for President and National Assembly on 16 January 2027, then for Governor and State Assembly on 6 February 2027.",
        fr: "Tu votes pour le président et l’Assemblée nationale le 16 janvier 2027, puis pour le gouverneur et l’assemblée de l’État le 6 février 2027.",
        pt: "Votas para Presidente e Assembleia Nacional a 16 de janeiro de 2027 e para governador e assembleia estadual a 6 de fevereiro de 2027.",
        sw: "Utampigia kura Rais na Bunge la Taifa tarehe 16 Januari 2027, kisha Gavana na Bunge la Jimbo tarehe 6 Februari 2027.",
        ar: "تصوّت لانتخاب الرئيس والجمعية الوطنية في 16 يناير 2027، ثم لانتخاب الحاكم وبرلمان الولاية في 6 فبراير 2027."
      } }
    ],
    src: {
      techeconomy_pvc: { o: "TechEconomy", t: "INEC Voter Register Crosses 103m as PVC Collection Begins Nationwide Friday", d: "6 Oct 2026", u: "https://techeconomy.ng/inec-voter-register-crosses-103m-as-pvc-collection-begins-nationwide-friday" },
      legit_pvc: { o: "Legit.ng", t: "INEC Announces Date for Voter’s Card Collection Ahead of 2027 Election", d: "28 Sep 2026", u: "https://www.legit.ng/politics/1733273-breaking-inec-announces-date-voters-card-collection/" },
      opinion_cvr: { o: "Opinion Nigeria", t: "INEC Tells Nigerians to Complete Voter Registration as CVR Ends Today", d: "26 Jul 2026", u: "https://www.opinionnigeria.com/inec-tells-nigerians-to-complete-voter-registration-as-cvr-ends-today/" },
      bella_guide: { o: "BellaNaija", t: "Voter Transfer, New Cards & Correction: Everything You Need to Know Before the August 30 Deadline", d: "15 Apr 2026", u: "https://www.bellanaija.com/2026/04/nigeria-2027-election-dates-inec-pvc-registration-guide/" }
    }
  },
  cm: {
    emb: { name: "Elections Cameroon", short: "ELECAM", url: null },
    items: [
      { d: "2026-08-31", src: "jdc_roll", t: {
        en: "Registration on the 2026 electoral roll closed on 31 August 2026. It had been open since 2 January.",
        fr: "L’inscription sur les listes électorales 2026 a pris fin le 31 août 2026. Elle était ouverte depuis le 2 janvier.",
        pt: "A inscrição nos cadernos eleitorais de 2026 terminou a 31 de agosto de 2026. Estava aberta desde 2 de janeiro.",
        sw: "Usajili katika orodha ya wapiga kura ya 2026 ulifungwa tarehe 31 Agosti 2026. Ulikuwa wazi tangu tarehe 2 Januari.",
        ar: "انتهى التسجيل في القوائم الانتخابية لعام 2026 في 31 أغسطس 2026، وكان مفتوحًا منذ 2 يناير."
      } },
      { d: "2026-10-20", src: "jdc_roll", t: {
        en: "ELECAM had to publish the provisional lists by 20 October 2026. The national electoral list is due on 30 December.",
        fr: "ELECAM devait publier les listes provisoires au plus tard le 20 octobre 2026. La liste électorale nationale est attendue le 30 décembre.",
        pt: "A ELECAM devia publicar as listas provisórias até 20 de outubro de 2026. A lista eleitoral nacional está prevista para 30 de dezembro.",
        sw: "ELECAM ilitakiwa kuchapisha orodha za muda kabla ya tarehe 20 Oktoba 2026. Orodha ya kitaifa inatarajiwa tarehe 30 Desemba.",
        ar: "كان على ELECAM نشر القوائم المؤقتة في موعد أقصاه 20 أكتوبر 2026، ومن المقرر صدور القائمة الانتخابية الوطنية في 30 ديسمبر."
      } },
      { d: "2026-09-02", src: "jdc_roll", t: {
        en: "You can collect your voter card at the ELECAM communal offices. ELECAM also visits homes and sends SMS to people who have not collected theirs.",
        fr: "Tu peux retirer ta carte d’électeur dans les bureaux communaux d’ELECAM. ELECAM passe aussi à domicile et envoie des SMS à ceux qui ne l’ont pas retirée.",
        pt: "Podes levantar o teu cartão de eleitor nos escritórios comunais da ELECAM. A ELECAM também visita casas e envia SMS a quem ainda não o levantou.",
        sw: "Unaweza kuchukua kadi yako ya mpiga kura katika ofisi za ELECAM za halmashauri. ELECAM pia hutembelea nyumba na kutuma SMS kwa wasiochukua kadi.",
        ar: "يمكنك استلام بطاقة الناخب من مكاتب ELECAM البلدية. كما تزور ELECAM المنازل وترسل رسائل SMS لمن لم يستلموا بطاقاتهم."
      } },
      { d: "2026-09-02", src: "investir_roll", t: {
        en: "No date is set for the legislative and municipal elections. The Electoral Code requires at least 90 days between the decree and the vote.",
        fr: "Aucune date n’est fixée pour les législatives et les municipales. Le Code électoral exige au moins 90 jours entre le décret et le scrutin.",
        pt: "Não há data marcada para as eleições legislativas e municipais. O Código Eleitoral exige pelo menos 90 dias entre o decreto e a votação.",
        sw: "Hakuna tarehe iliyopangwa ya uchaguzi wa wabunge na wa manispaa. Sheria ya Uchaguzi inahitaji siku 90 angalau kati ya amri na kura.",
        ar: "لم يُحدَّد موعد للانتخابات التشريعية والبلدية. ويشترط القانون الانتخابي مرور 90 يومًا على الأقل بين المرسوم والاقتراع."
      } }
    ],
    src: {
      jdc_roll: { o: "Journal du Cameroun", t: "Cameroun : 252 800 nouveaux électeurs inscrits sur les listes électorales en 2026", d: "2 Sep 2026", u: "https://fr.journalducameroun.com/cameroun-252-800-nouveaux-electeurs-inscrits-sur-les-listes-electorales-en-2026/" },
      investir_roll: { o: "Investir au Cameroun", t: "Cameroon Adds 252,830 Voters to Electoral Roll Ahead of Legislative and Municipal Elections", d: "2 Sep 2026", u: "https://m.investiraucameroun.com/stopblabla/i/16753/cameroon-adds-252830-voters-electoral-roll-ahead-legislative-and-municipal-elections" }
    }
  },

  so: {
    emb: { name: "National Independent Electoral and Boundaries Commission", short: "NIEBC", url: null },
    items: [
      { d: "2026-10-15", src: "dawan_dates", t: {
        en: "Voter registration is set for 1 to 22 November 2026, according to the electoral commission’s timetable.",
        fr: "L’inscription des électeurs est prévue du 1er au 22 novembre 2026, selon le calendrier de la commission électorale.",
        pt: "O recenseamento de eleitores está previsto de 1 a 22 de novembro de 2026, segundo o calendário da comissão eleitoral.",
        sw: "Usajili wa wapiga kura umepangwa kuanzia tarehe 1 hadi 22 Novemba 2026, kulingana na ratiba ya tume ya uchaguzi.",
        ar: "التسجيل للناخبين مقرر من 1 إلى 22 نوفمبر 2026 وفق جدول اللجنة الانتخابية."
      } },
      { d: "2026-10-15", src: "digest_dates", t: {
        en: "The provisional voter list is due on 21 January 2027 and the final register on 15 March 2027.",
        fr: "La liste provisoire des électeurs est attendue le 21 janvier 2027 et le registre définitif le 15 mars 2027.",
        pt: "A lista provisória de eleitores está prevista para 21 de janeiro de 2027 e o registo definitivo para 15 de março de 2027.",
        sw: "Orodha ya muda ya wapiga kura inatarajiwa tarehe 21 Januari 2027 na daftari la mwisho tarehe 15 Machi 2027.",
        ar: "من المقرر صدور قائمة الناخبين المؤقتة في 21 يناير 2027 والسجل النهائي في 15 مارس 2027."
      } },
      { d: "2026-10-15", src: "dawan_dates", t: {
        en: "According to the commission, Parliament would be elected on 15 April 2027 and the president on 15 May 2027.",
        fr: "Selon la commission, le Parlement serait élu le 15 avril 2027 et le président le 15 mai 2027.",
        pt: "Segundo a comissão, o Parlamento seria eleito a 15 de abril de 2027 e o presidente a 15 de maio de 2027.",
        sw: "Kulingana na tume, Bunge lingechaguliwa tarehe 15 Aprili 2027 na rais tarehe 15 Mei 2027.",
        ar: "وفق اللجنة، يُنتخب البرلمان في 15 أبريل 2027 والرئيس في 15 مايو 2027."
      } },
      { d: "2026-10-15", src: "dawan_dates", t: {
        en: "The opposition rejects this timetable, so the vote is uncertain: follow the electoral commission’s announcements.",
        fr: "L’opposition rejette ce calendrier, donc le scrutin reste incertain : suis les annonces de la commission électorale.",
        pt: "A oposição rejeita este calendário, por isso a votação é incerta: acompanha os anúncios da comissão eleitoral.",
        sw: "Upinzani unakataa ratiba hii, kwa hiyo kura haina uhakika: fuatilia matangazo ya tume ya uchaguzi.",
        ar: "تعارض المعارضة هذا الجدول، لذا فإن التصويت غير مؤكد: تابع إعلانات اللجنة الانتخابية."
      } }
    ],
    src: {
      dawan_dates: { o: "Dawan Africa", t: "Somalia Sets Presidential Vote for 15 May 2027", d: "15 Oct 2026", u: "https://www.dawan.africa/news/somalia-sets-presidential-vote-for-15-may-2027" },
      digest_dates: { o: "The Somali Digest", t: "The Electoral Commission Sets Somalia’s Vote for 15 May 2027 and the Opposition Rejects It", d: "15 Oct 2026", u: "https://thesomalidigest.com/electoral-commission-2027-election-timetable/" }
    }
  },

  bi: {
    emb: { name: "Commission électorale nationale indépendante", short: "CENI", url: null },
    items: [
      { d: "2026-05-08", src: "benin_budget", t: {
        en: "You vote for President on 3 May 2027. A second round, if needed, is planned for 1 June 2027.",
        fr: "Tu votes pour le président le 3 mai 2027. Un second tour, si nécessaire, est prévu le 1er juin 2027.",
        pt: "Votas para Presidente a 3 de maio de 2027. Uma segunda volta, se necessária, está prevista para 1 de junho de 2027.",
        sw: "Utampigia kura Rais tarehe 3 Mei 2027. Duru ya pili, ikihitajika, imepangwa tarehe 1 Juni 2027.",
        ar: "تصوّت لانتخاب الرئيس في 3 مايو 2027، وتُجرى جولة ثانية عند الحاجة في 1 يونيو 2027."
      } },
      { d: "2026-05-12", src: "ecofin_vote", t: {
        en: "The decree convening voters is due between 4 November and 4 December 2026.",
        fr: "Le décret de convocation des électeurs est attendu entre le 4 novembre et le 4 décembre 2026.",
        pt: "O decreto de convocação dos eleitores está previsto entre 4 de novembro e 4 de dezembro de 2026.",
        sw: "Amri ya kuwaita wapiga kura inatarajiwa kati ya tarehe 4 Novemba na 4 Desemba 2026.",
        ar: "يُنتظر صدور مرسوم دعوة الناخبين بين 4 نوفمبر و4 ديسمبر 2026."
      } }
    ],
    src: {
      benin_budget: { o: "Bénin Web TV", t: "Burundi : un budget de 38,9 millions $ pour l’organisation de la présidentielle 2027", d: "12 May 2026", u: "https://beninwebtv.bj/burundi-un-budget-de-389-millions-pour-lorganisation-de-presidentielle-2027/" },
      ecofin_vote: { o: "Ecofin Agency", t: "Burundi Sets May 2027 Presidential Vote With $38.9 Million Budget", d: "12 May 2026", u: "https://www.ecofinagency.com/news/1205-55485-burundi-sets-may-2027-presidential-vote-with-38-9-million-budget" }
    }
  },

  ke: {
    emb: { name: "Independent Electoral and Boundaries Commission", short: "IEBC", url: "https://www.iebc.or.ke" },
    check: { url: "https://verify.iebc.or.ke", src: "verify" },
    items: [
      { d: "2026-08-20", src: "gazette", t: {
        en: "Continuous voter registration began on 29 September 2025 and was still open in August 2026. No closing date is published.",
        fr: "L’inscription continue des électeurs a commencé le 29 septembre 2025 et restait ouverte en août 2026. Aucune date de clôture n’est publiée.",
        pt: "O recenseamento contínuo começou a 29 de setembro de 2025 e continuava aberto em agosto de 2026. Não há data de encerramento publicada.",
        sw: "Usajili endelevu wa wapiga kura ulianza tarehe 29 Septemba 2025 na bado ulikuwa wazi Agosti 2026. Hakuna tarehe ya kufunga iliyochapishwa.",
        ar: "بدأ التسجيل المستمر للناخبين في 29 سبتمبر 2025 وكان لا يزال مفتوحًا في أغسطس 2026. ولم يُنشر موعد للإغلاق."
      } },
      { d: "2025-09-30", src: "register_how", t: {
        en: "Register at any IEBC constituency office if you are Kenyan, 18 or over, with a valid national ID or passport.",
        fr: "Tu peux t’inscrire dans un bureau de circonscription de l’IEBC, dès 18 ans, avec une carte d’identité ou un passeport kényan valide.",
        pt: "Podes recensear-te em qualquer escritório de círculo da IEBC, se fores queniano, com 18 anos ou mais e BI ou passaporte válido.",
        sw: "Jisajili katika ofisi yoyote ya jimbo ya IEBC ikiwa wewe ni Mkenya mwenye miaka 18 au zaidi na kitambulisho au pasipoti halali.",
        ar: "يمكنك التسجيل في أي مكتب دائرة تابع لـ IEBC إذا كنت كينيًا بعمر 18 عامًا فأكثر ولديك هوية وطنية أو جواز سفر ساريان."
      } },
      { d: "2025-07-10", src: "verify", t: {
        en: "Check your registration: send your ID number to 70000, or use verify.iebc.or.ke with your ID number and year of birth.",
        fr: "Vérifie ton inscription : envoie ton numéro de pièce d’identité au 70000, ou va sur verify.iebc.or.ke avec ce numéro et ton année de naissance.",
        pt: "Verifica o teu recenseamento: envia o número do documento para 70000 ou usa verify.iebc.or.ke com esse número e o ano de nascimento.",
        sw: "Angalia usajili wako: tuma nambari ya kitambulisho kwa 70000, au tumia verify.iebc.or.ke kwa nambari hiyo na mwaka wa kuzaliwa.",
        ar: "تحقق من تسجيلك: أرسل رقم هويتك إلى 70000 أو استخدم verify.iebc.or.ke برقم الهوية وسنة الميلاد."
      } },
      { d: "2026-06-24", src: "iebc_date", t: {
        en: "The general election is on Tuesday 10 August 2027.",
        fr: "Les élections générales ont lieu le mardi 10 août 2027.",
        pt: "As eleições gerais realizam-se na terça-feira, 10 de agosto de 2027.",
        sw: "Uchaguzi mkuu utafanyika Jumanne tarehe 10 Agosti 2027.",
        ar: "تُجرى الانتخابات العامة يوم الثلاثاء 10 أغسطس 2027."
      } }
    ],
    src: {
      gazette: { o: "Citizen Digital", t: "IEBC gazettes 2027 election period, unveils key timelines for aspirants and campaigns", d: "After 20 Aug 2026", u: "https://citizen.digital/article/iebc-gazettes-2027-election-period-unveils-key-timelines-for-aspirants-and-campaigns-n388705" },
      register_how: { o: "Citizen Digital", t: "How and where you can register as a voter", d: "30 Sep 2025", u: "https://citizen.digital/article/how-and-where-you-can-register-as-a-voter-n370574" },
      verify: { o: "Citizen Digital", t: "How to verify your IEBC voter registration details online", d: "10 Jul 2025", u: "https://citizen.digital/article/how-to-verify-your-iebc-voter-registration-details-online-n366049" },
      iebc_date: { o: "Kenyans.co.ke", t: "IEBC Sets August 10, 2027 Election Date, Orders Public Officers to Resign by February 9", d: "24 Jun 2026", u: "https://www.kenyans.co.ke/news/124581-iebc-sets-august-10-2027-election-date-orders-public-officers-resign-february-9" }
    }
  },

  mg: {
    emb: { name: "Commission électorale nationale indépendante", short: "CENI", url: "https://www.ceni-madagascar.mg" },
    items: [
      { d: "2026-11-25", src: "allafrica_refonte", t: {
        en: "You can register on the new voter list until 25 November 2026. The provisional list is due to close on 9 January 2027.",
        fr: "Tu peux t’inscrire sur la nouvelle liste électorale jusqu’au 25 novembre 2026. L’arrêtage provisoire de la liste est prévu le 9 janvier 2027.",
        pt: "Podes inscrever-te na nova lista eleitoral até 25 de novembro de 2026. O fecho provisório da lista está previsto para 9 de janeiro de 2027.",
        sw: "Unaweza kujisajili kwenye orodha mpya ya wapiga kura hadi tarehe 25 Novemba 2026. Orodha ya muda inatarajiwa kufungwa tarehe 9 Januari 2027.",
        ar: "يمكنك التسجيل في قائمة الناخبين الجديدة حتى 25 نوفمبر 2026. ومن المقرر إغلاق القائمة المؤقتة في 9 يناير 2027."
      } },
      { d: "2026-06-30", src: "newsmada_lists", t: {
        en: "Register at your fokontany office with your CIN. You must be Malagasy, of age and hold your civil and political rights.",
        fr: "Inscris-toi au bureau de ton fokontany avec ta CIN. Il faut être malgache, majeur et jouir de tes droits civils et politiques.",
        pt: "Inscreve-te no gabinete do teu fokontany com o teu CIN. Tens de ser malgaxe, maior de idade e gozar dos direitos civis e políticos.",
        sw: "Jisajili katika ofisi ya fokontany yako ukiwa na CIN. Lazima uwe raia wa Madagascar, mtu mzima na mwenye haki zako za kiraia na kisiasa.",
        ar: "سجّل في مكتب الفوكونتاني التابع لك ومعك CIN. يجب أن تكون مدغشقريًا بالغًا ومتمتعًا بحقوقك المدنية والسياسية."
      } },
      { d: "2026-06-30", src: "newsmada_lists", t: {
        en: "The old electoral lists are no longer valid. To vote in future elections, you must register on the new list.",
        fr: "Les anciennes listes électorales ne sont plus valables. Pour voter aux prochains scrutins, tu dois t’inscrire sur la nouvelle liste.",
        pt: "As antigas listas eleitorais deixaram de ser válidas. Para votares nas próximas eleições, tens de te inscrever na nova lista.",
        sw: "Orodha za zamani za wapiga kura hazifai tena. Ili kupiga kura katika chaguzi zijazo, lazima ujisajili kwenye orodha mpya.",
        ar: "لم تعد القوائم الانتخابية القديمة صالحة. وللتصويت في الانتخابات القادمة عليك التسجيل في القائمة الجديدة."
      } },
      { d: "2026-05-09", src: "ceni_may", t: {
        en: "The CENI proposed a referendum in June 2027 and a presidential vote in October 2027. The dates are not fixed yet.",
        fr: "La CENI a proposé un référendum en juin 2027 et une présidentielle en octobre 2027. Les dates ne sont pas encore fixées.",
        pt: "A CENI propôs um referendo em junho de 2027 e uma presidencial em outubro de 2027. As datas ainda não estão fixadas.",
        sw: "CENI ilipendekeza kura ya maoni Juni 2027 na uchaguzi wa rais Oktoba 2027. Tarehe bado hazijapangwa rasmi.",
        ar: "اقترحت CENI استفتاءً في يونيو 2027 وانتخابات رئاسية في أكتوبر 2027. ولم تُحدَّد المواعيد بعد."
      } }
    ],
    src: {
      allafrica_refonte: { o: "L’Express de Madagascar (via AllAfrica)", t: "Madagascar: Refonte de la liste électorale - La CENI en appelle à l’engagement des citoyens", d: "29 Jul 2026", u: "https://fr.allafrica.com/stories/202607290354.html" },
      newsmada_lists: { o: "Les Nouvelles (Newsmada)", t: "Ceni : les anciennes listes électorales ne sont plus valables", d: "30 Jun 2026", u: "https://newsmada.com/?p=185727" },
      ceni_may: { o: "RFI (via AllAfrica)", t: "Madagascar: La Céni annonce un référendum constitutionnel en juin 2027 suivi d’une présidentielle en octobre", d: "9 May 2026", u: "https://fr.allafrica.com/stories/202605110742.html" }
    }
  },

  gw: {
    emb: { name: "Comissão Nacional de Eleições", short: "CNE", url: null },
    items: [
      { d: "2026-10-08", src: "forbes_gw", t: {
        en: "The transitional government said elections cannot be held on 6 December 2026. The Presidency is to announce a new calendar.",
        fr: "Le gouvernement de transition a dit que les élections ne peuvent pas avoir lieu le 6 décembre 2026. La présidence doit annoncer un nouveau calendrier.",
        pt: "O governo de transição disse que as eleições não podem realizar-se a 6 de dezembro de 2026. A Presidência vai anunciar um novo calendário.",
        sw: "Serikali ya mpito ilisema uchaguzi hauwezi kufanyika tarehe 6 Desemba 2026. Ikulu itatangaza ratiba mpya.",
        ar: "قالت الحكومة الانتقالية إنه لا يمكن إجراء الانتخابات في 6 ديسمبر 2026. وستعلن الرئاسة جدولًا جديدًا."
      } },
      { d: "2026-10-08", src: "forbes_gw", t: {
        en: "The CNE called a 6 December vote technically unlikely. The transitional Presidency will decide: follow the CNE for official news.",
        fr: "La CNE juge un scrutin le 6 décembre techniquement improbable. La présidence de transition tranchera : suis la CNE pour les infos officielles.",
        pt: "A CNE considera tecnicamente improvável votar a 6 de dezembro. A Presidência de transição decidirá: acompanha a CNE para notícias oficiais.",
        sw: "CNE ilisema kura ya tarehe 6 Desemba haiwezekani kiufundi. Ikulu ya mpito itaamua: fuatilia CNE kwa habari rasmi.",
        ar: "رأت CNE أن التصويت في 6 ديسمبر غير مرجح تقنيًا. وستقرر الرئاسة الانتقالية: تابع CNE للأخبار الرسمية."
      } }
    ],
    src: {
      forbes_gw: { o: "Forbes África Lusófona", t: "Governo de transição admite adiamento das eleições na Guiné-Bissau", d: "8 Oct 2026", u: "https://forbesafricalusofona.com/?p=177319" }
    }
  },

  ss: {
    emb: { name: "National Elections Commission", short: "NEC", url: null },
    items: [
      { d: "2026-10-07", src: "ryei_reg", t: {
        en: "As of 7 October 2026, the election commission said no voter had been registered anywhere in South Sudan.",
        fr: "Au 7 octobre 2026, la commission électorale indiquait qu’aucun électeur n’était encore enregistré au Soudan du Sud.",
        pt: "A 7 de outubro de 2026, a comissão eleitoral dizia que nenhum eleitor estava ainda recenseado no Sudão do Sul.",
        sw: "Hadi tarehe 7 Oktoba 2026, tume ya uchaguzi ilisema hakuna mpiga kura aliyekuwa amesajiliwa popote Sudan Kusini.",
        ar: "حتى 7 أكتوبر 2026، قالت اللجنة الانتخابية إنه لم يُسجَّل أي ناخب في أي مكان في جنوب السودان."
      } },
      { d: "2026-10-07", src: "ryei_reg", t: {
        en: "No registration period or centres had been announced. Registration is planned manually, in person and on paper.",
        fr: "Aucune période ni aucun centre d’inscription n’avait été annoncé. L’inscription est prévue à la main, en personne, sur papier.",
        pt: "Ainda não tinham sido anunciados período nem centros de recenseamento. O recenseamento está previsto de forma manual, presencial e em papel.",
        sw: "Muda wala vituo vya usajili havikuwa vimetangazwa. Usajili umepangwa kufanywa kwa mkono, ana kwa ana, kwenye karatasi.",
        ar: "لم يُعلن عن فترة أو مراكز للتسجيل بعد. ومن المقرر أن يجري التسجيل يدويًا وشخصيًا وعلى الورق."
      } },
      { d: null, src: "nea_2012", t: {
        en: "Under the 2012 National Elections Act, you can vote if you are a South Sudanese citizen, 18 or over, and registered.",
        fr: "Selon la loi électorale de 2012, tu peux voter si tu es sud-soudanais, âgé de 18 ans ou plus et inscrit.",
        pt: "Segundo a Lei Eleitoral Nacional de 2012, podes votar se fores sul-sudanês, tiveres 18 anos ou mais e estiveres recenseado.",
        sw: "Kwa Sheria ya Uchaguzi ya Kitaifa ya 2012, unaweza kupiga kura ukiwa raia wa Sudan Kusini, miaka 18 au zaidi, na umesajiliwa.",
        ar: "وفق قانون الانتخابات الوطني لعام 2012، يمكنك التصويت إذا كنت مواطنًا من جنوب السودان بعمر 18 عامًا فأكثر ومسجَّلًا."
      } },
      { d: "2026-08-21", src: "rt_io_reject", t: {
        en: "Polling day is set for 22 December 2026, but the SPLM-IO (Machar faction) rejects the plan. The vote is uncertain: follow the NEC.",
        fr: "Le scrutin est fixé au 22 décembre 2026, mais le SPLM-IO (faction Machar) rejette le plan. Le vote est incertain : suis la NEC.",
        pt: "A votação está marcada para 22 de dezembro de 2026, mas o SPLM-IO (fação de Machar) rejeita o plano. A votação é incerta: acompanha a NEC.",
        sw: "Siku ya kupiga kura ni tarehe 22 Desemba 2026, lakini SPLM-IO (kundi la Machar) inakataa mpango huo. Kura haina uhakika: fuatilia NEC.",
        ar: "حُدد 22 ديسمبر 2026 موعدًا للاقتراع، لكن الحركة الشعبية-المعارضة (جناح مشار) ترفض الخطة. التصويت غير مؤكد: تابع NEC."
      } }
    ],
    src: {
      ryei_reg: { o: "Radio Yei", t: "No Voter Has Registered Yet – Election Commission", d: "7 Oct 2026", u: "https://radioyei.org/news/2026-south-sudan-elections/no-voter-has-registered-yet-election-commission/" },
      nea_2012: { o: "Republic of South Sudan (copy on the Ministry of Foreign Affairs website)", t: "National Elections Act, 2012 (Act No. 39 of 2012)", d: "2012", u: "https://mofaic.gov.ss/wp-content/uploads/2023/03/National-Elections-Act-39-of-2012.pdf" },
      rt_io_reject: { o: "Radio Tamazuj", t: "SPLM-IO rejects election plan, warns of renewed conflict", d: "21 Aug 2026", u: "https://radiotamazuj.org/en/news/article/machars-group-rejects-election-plan-warns-of-renewed-conflict" }
    }
  },

  ly: {
    emb: { name: "High National Elections Commission", short: "HNEC", url: null },
    items: [
      { d: "2026-08-30", src: "reuters_44", t: {
        en: "No date is set for national elections. A deal signed on 30 August 2026 requires them within 24 months.",
        fr: "Aucune date n’est fixée pour les élections nationales. Un accord signé le 30 août 2026 les exige dans un délai de 24 mois.",
        pt: "Não há data marcada para as eleições nacionais. Um acordo assinado a 30 de agosto de 2026 exige-as no prazo de 24 meses.",
        sw: "Hakuna tarehe iliyopangwa ya uchaguzi wa kitaifa. Makubaliano ya tarehe 30 Agosti 2026 yanahitaji ufanyike ndani ya miezi 24.",
        ar: "لم يُحدَّد موعد للانتخابات الوطنية. ويشترط اتفاق وُقِّع في 30 أغسطس 2026 إجراءها خلال 24 شهرًا."
      } },
      { d: "2026-08-30", src: "marsad_44", t: {
        en: "The 4+4 deal and a Presidential Council decree name different heads for the electoral commission (HNEC). Follow HNEC for official news.",
        fr: "L’accord 4+4 et un décret du Conseil présidentiel nomment des présidents différents pour la commission électorale (HNEC). Suis la HNEC pour les infos officielles.",
        pt: "O acordo 4+4 e um decreto do Conselho Presidencial nomeiam presidentes diferentes para a comissão eleitoral (HNEC). Acompanha a HNEC para notícias oficiais.",
        sw: "Makubaliano ya 4+4 na amri ya Baraza la Urais yanataja wakuu tofauti wa tume ya uchaguzi (HNEC). Fuatilia HNEC kwa habari rasmi.",
        ar: "يسمّي اتفاق 4+4 ومرسوم للمجلس الرئاسي رئيسين مختلفين للمفوضية الوطنية العليا للانتخابات (HNEC). تابع HNEC للأخبار الرسمية."
      } }
    ],
    src: {
      reuters_44: { o: "Reuters (via Internazionale)", t: "Libya rivals agree roadmap for elections within 24 months at UN-led talks", d: "30 Aug 2026", u: "https://www.internazionale.it/ultime-notizie-reuters/2026/08/30/libya-rivals-agree-roadmap-for-elections-within-24-months-at-un-led-talks" },
      marsad_44: { o: "Al Marsad", t: "“4+4” Deal Reshapes Libya’s Electoral Roadmap", d: "30 Aug 2026", u: "https://en.almarsad.co/44-deal-reshapes-libyas-electoral-roadmap/" }
    }
  },

  ls: {
    emb: { name: "Independent Electoral Commission", short: "IEC", url: "https://iec.org.ls" },
    items: [
      { d: "2026-06-15", src: "iec_news", t: {
        en: "On 15 June 2026 the IEC began constituency assessment visits ahead of a voter registration intensification programme. No dates are published.",
        fr: "Le 15 juin 2026, l’IEC a commencé des visites d’évaluation des circonscriptions avant un programme intensif d’inscription. Aucune date n’est publiée.",
        pt: "A 15 de junho de 2026, a IEC iniciou visitas de avaliação aos círculos antes de um programa intensivo de recenseamento. Não há datas publicadas.",
        sw: "Tarehe 15 Juni 2026, IEC ilianza ziara za tathmini za majimbo kabla ya mpango mkubwa wa usajili wa wapiga kura. Hakuna tarehe zilizochapishwa.",
        ar: "في 15 يونيو 2026 بدأت IEC زيارات تقييم للدوائر قبل برنامج مكثف لتسجيل الناخبين. ولم تُنشر أي مواعيد."
      } },
      { d: "2026-02-13", src: "iec_vision", t: {
        en: "The IEC chair’s priorities include a stable voter register and automatic registration, with SMS or email alerts for young people turning 18.",
        fr: "Le président de l’IEC vise un registre stable et l’inscription automatique, avec alertes SMS ou e-mail pour les jeunes atteignant 18 ans.",
        pt: "O presidente da IEC prioriza um registo estável e o recenseamento automático, com alertas por SMS ou e-mail para jovens que fazem 18 anos.",
        sw: "Mwenyekiti wa IEC anaweka kipaumbele kwenye daftari thabiti na usajili wa kiotomatiki, na arifa za SMS au barua pepe kwa vijana wanaofikisha miaka 18.",
        ar: "من أولويات رئيس IEC سجل ناخبين مستقر وتسجيل تلقائي مع تنبيهات SMS أو بريد إلكتروني للشباب الذين يبلغون 18 عامًا."
      } },
      { d: "2026-10-11", src: "iec_news", t: {
        en: "The IEC has not yet published a polling day for the next National Assembly election.",
        fr: "L’IEC n’a pas encore publié de date de scrutin pour les prochaines élections à l’Assemblée nationale.",
        pt: "A IEC ainda não publicou o dia da votação para as próximas eleições da Assembleia Nacional.",
        sw: "IEC bado haijachapisha siku ya kupiga kura kwa uchaguzi ujao wa Bunge la Taifa.",
        ar: "لم تنشر IEC بعد يوم الاقتراع للانتخابات المقبلة للجمعية الوطنية."
      } }
    ],
    src: {
      iec_news: { o: "Independent Electoral Commission (IEC) Lesotho", t: "News & Media", d: "Oct 2026", u: "https://iec.org.ls/news-and-media/" },
      iec_vision: { o: "Lesotho Times", t: "Maphephe outlines vision for IEC", d: "13 Feb 2026", u: "https://lestimes.com/?p=89702" }
    }
  },

  tn: {
    emb: { name: "Instance supérieure indépendante pour les élections", short: "ISIE", url: "https://www.isie.tn" },
    items: [
      { d: "2026-10-13", src: "ayachi", t: {
        en: "Municipal elections could take place before the end of 2026, or by March 2027. No official date is set.",
        fr: "Les élections municipales pourraient avoir lieu avant la fin 2026, ou d’ici mars 2027. Aucune date officielle n’est fixée.",
        pt: "As eleições municipais podem realizar-se antes do fim de 2026 ou até março de 2027. Não há data oficial marcada.",
        sw: "Uchaguzi wa manispaa unaweza kufanyika kabla ya mwisho wa 2026, au kufikia Machi 2027. Hakuna tarehe rasmi iliyopangwa.",
        ar: "قد تُجرى الانتخابات البلدية قبل نهاية 2026 أو بحلول مارس 2027. ولم يُحدَّد موعد رسمي."
      } },
      { d: "2026-10-13", src: "ayachi", t: {
        en: "The ISIE is waiting for the decree convening voters. A board member expects legislative elections in November 2027, not yet official.",
        fr: "L’ISIE attend le décret de convocation des électeurs. Un membre de son conseil prévoit les législatives en novembre 2027, sans calendrier officiel.",
        pt: "A ISIE aguarda o decreto de convocação dos eleitores. Um membro do conselho prevê legislativas em novembro de 2027, sem calendário oficial.",
        sw: "ISIE inasubiri amri ya kuwaita wapiga kura. Mjumbe wa bodi anatarajia uchaguzi wa wabunge Novemba 2027, bila ratiba rasmi.",
        ar: "تنتظر ISIE صدور مرسوم دعوة الناخبين. ويتوقع أحد أعضاء مجلسها انتخابات تشريعية في نوفمبر 2027 دون جدول رسمي."
      } }
    ],
    src: {
      ayachi: { o: "Webdo", t: "Municipales : Un scrutin possible avant fin 2026, sinon d’ici mars 2027", d: "13 Oct 2026", u: "https://www.webdo.tn/fr/actualite/national/municipales-un-scrutin-possible-avant-fin-2026-sinon-dici-mars-2027/405501/" }
    }
  },

  ao: {
    emb: { name: "Comissão Nacional Eleitoral", short: "CNE", url: null },
    items: [
      { d: "2027-03-31", src: "forbes_ao", t: {
        en: "The voter registration update runs from 15 June 2026 to 31 March 2027.",
        fr: "L’actualisation du registre électoral se déroule du 15 juin 2026 au 31 mars 2027.",
        pt: "A atualização do registo eleitoral decorre de 15 de junho de 2026 a 31 de março de 2027.",
        sw: "Usasishaji wa daftari la wapiga kura unafanyika kuanzia tarehe 15 Juni 2026 hadi 31 Machi 2027.",
        ar: "يجري تحديث السجل الانتخابي من 15 يونيو 2026 إلى 31 مارس 2027."
      } },
      { d: "2026-06-15", src: "forbes_ao", t: {
        en: "You can register if you are 18 or over and hold full political rights. Registration is at BUAP desks and some consulates.",
        fr: "Tu peux t’inscrire si tu as 18 ans ou plus et jouis de tous tes droits politiques. L’inscription se fait aux guichets BUAP et dans certains consulats.",
        pt: "Podes recensear-te se tiveres 18 anos ou mais e gozares de todos os direitos políticos. O recenseamento faz-se nos balcões BUAP e em alguns consulados.",
        sw: "Unaweza kujisajili ukiwa na miaka 18 au zaidi na una haki zote za kisiasa. Usajili unafanywa kwenye madawati ya BUAP na baadhi ya balozi ndogo.",
        ar: "يمكنك التسجيل إذا كنت بعمر 18 عامًا فأكثر وتتمتع بكامل حقوقك السياسية. ويتم التسجيل في مكاتب BUAP وبعض القنصليات."
      } },
      { d: "2026-06-15", src: "forbes_ao", t: {
        en: "Bring your voter card, your Bilhete de Identidade (BI) or, abroad, a passport. Expired documents are accepted.",
        fr: "Apporte ta carte d’électeur, ton Bilhete de Identidade (BI) ou, à l’étranger, un passeport. Les documents périmés sont acceptés.",
        pt: "Leva o teu cartão de eleitor, o Bilhete de Identidade (BI) ou, no estrangeiro, o passaporte. Aceitam-se documentos caducados.",
        sw: "Beba kadi yako ya mpiga kura, Bilhete de Identidade (BI) au, ukiwa nje ya nchi, pasipoti. Hati zilizokwisha muda zinakubaliwa.",
        ar: "أحضر بطاقة الناخب أو Bilhete de Identidade (BI) أو جواز السفر إن كنت في الخارج. وتُقبل الوثائق منتهية الصلاحية."
      } },
      { d: "2026-06-15", src: "forbes_ao", t: {
        en: "Desks open in phases: 254 of 634 were set to open first, including all of Luanda’s municipalities.",
        fr: "Les guichets ouvrent par phases : 254 sur 634 devaient ouvrir en premier, dont toutes les communes de Luanda.",
        pt: "Os balcões abrem por fases: 254 de 634 abririam primeiro, incluindo todos os municípios de Luanda.",
        sw: "Madawati yanafunguliwa kwa awamu: 254 kati ya 634 yalipangwa kufunguliwa kwanza, ikiwemo manispaa zote za Luanda.",
        ar: "تفتح المكاتب على مراحل: كان من المقرر أن يُفتح 254 من أصل 634 أولًا، بما في ذلك جميع بلديات لواندا."
      } }
    ],
    src: {
      forbes_ao: { o: "Forbes África Lusófona", t: "Angola arranca actualização do registo eleitoral esta Segunda-feira", d: "15 Jun 2026", u: "https://forbesafricalusofona.com/?p=173069" }
    }
  }
};
