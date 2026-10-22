/* ================== Module « valeurs » : 10 énoncés identiques dans tous les pays ==================
   Ne sert pas à comparer les partis. Chaque réponse (échelle à 5 points, d’accord / pas d’accord) alimente
   uniquement le compteur anonyme « où se situent les électeurs sur les valeurs » (libéral–progressiste vs conservateur–nationaliste).
   ax = +1 : être d’accord est la position libérale–progressiste ; ax = −1 : être d’accord est la position conservatrice–nationaliste.
   Les cinq énoncés +1 et les cinq énoncés −1 sont mêlés pour que l’ordre ne favorise aucun pôle. */
const VALUES = [
  {
    id: "v1", ax: 1, topic: "gender",
    en: { short: "Equal rights for women and men", text: "Women and men should have exactly the same rights in law, including the right to inherit and to own land." },
    fr: { short: "Droits égaux pour femmes et hommes", text: "Les femmes et les hommes devraient avoir exactement les mêmes droits devant la loi, y compris le droit d’hériter et de posséder des terres." },
    pt: { short: "Direitos iguais para mulheres e homens", text: "As mulheres e os homens devem ter exatamente os mesmos direitos perante a lei, incluindo o direito de herdar e de possuir terras." },
    sw: { short: "Haki sawa kwa wanawake na wanaume", text: "Wanawake na wanaume wanapaswa kuwa na haki zilezile kabisa mbele ya sheria, zikiwemo haki ya kurithi na kumiliki ardhi." },
    ar: { short: "حقوق متساوية للنساء والرجال", text: "يجب أن يتمتع النساء والرجال بالحقوق نفسها تمامًا في القانون، بما في ذلك حق الإرث وحق تملك الأراضي." }
  },
  {
    id: "v2", ax: -1, topic: "religion",
    en: { short: "Religion should guide the law", text: "The values of the country’s main religion should guide its laws." },
    fr: { short: "La religion doit guider la loi", text: "Les valeurs de la principale religion du pays devraient guider ses lois." },
    pt: { short: "A religião deve orientar a lei", text: "Os valores da principal religião do país devem orientar as suas leis." },
    sw: { short: "Dini iongoze sheria", text: "Maadili ya dini kuu ya nchi yanapaswa kuongoza sheria zake." },
    ar: { short: "يجب أن يوجّه الدين القوانين", text: "يجب أن توجّه قيم الدين الرئيسي في البلد قوانينه." }
  },
  {
    id: "v3", ax: 1, topic: "speech",
    en: { short: "Freedom to criticise leaders", text: "People should be free to criticise the government in public, even when many people find it offensive." },
    fr: { short: "Liberté de critiquer les dirigeants", text: "Chacun devrait être libre de critiquer le gouvernement en public, même quand beaucoup de personnes trouvent cela offensant." },
    pt: { short: "Liberdade de criticar os governantes", text: "As pessoas devem ter a liberdade de criticar o governo em público, mesmo quando muita gente acha isso ofensivo." },
    sw: { short: "Uhuru wa kukosoa viongozi", text: "Watu wanapaswa kuwa huru kuikosoa serikali hadharani, hata kama jambo hilo linawakwaza watu wengi." },
    ar: { short: "حرية انتقاد القادة", text: "يجب أن يكون الناس أحرارًا في انتقاد الحكومة علنًا، حتى لو رأى كثير من الناس ذلك مسيئًا." }
  },
  {
    id: "v4", ax: -1, topic: "order",
    en: { short: "Order before some freedoms", text: "When the country is insecure, it is acceptable to limit some freedoms in exchange for order." },
    fr: { short: "L’ordre avant certaines libertés", text: "Lorsque le pays est en situation d’insécurité, il est acceptable de limiter certaines libertés en échange de l’ordre." },
    pt: { short: "Ordem antes de algumas liberdades", text: "Quando o país vive em insegurança, é aceitável limitar algumas liberdades em troca da ordem." },
    sw: { short: "Utulivu kabla ya uhuru fulani", text: "Nchi inapokabiliwa na ukosefu wa usalama, inakubalika kupunguza baadhi ya uhuru ili kupata utulivu." },
    ar: { short: "النظام قبل بعض الحريات", text: "عندما يعاني البلد من انعدام الأمن، يكون من المقبول تقييد بعض الحريات مقابل استتباب النظام." }
  },
  {
    id: "v5", ax: 1, topic: "family",
    en: { short: "Choosing your own spouse", text: "Whom a person marries should be their own decision, not their family’s." },
    fr: { short: "Choisir soi-même son conjoint", text: "Le choix de la personne que l’on épouse devrait être sa propre décision, et non celle de sa famille." },
    pt: { short: "Escolher o próprio cônjuge", text: "Com quem uma pessoa se casa deve ser decisão sua, e não da sua família." },
    sw: { short: "Kuchagua mwenzi wa ndoa mwenyewe", text: "Mtu anapaswa kuamua mwenyewe atafunga ndoa na nani, na si familia yake." },
    ar: { short: "اختيار الزوج أو الزوجة", text: "يجب أن يكون اختيار من يتزوجه الشخص قراره هو، لا قرار أسرته." }
  },
  {
    id: "v6", ax: -1, topic: "sovereignty",
    en: { short: "Refuse foreign conditions", text: "My country should make its own decisions, even if that means refusing the conditions that foreign governments and lenders attach to their help." },
    fr: { short: "Refuser les conditions étrangères", text: "Mon pays devrait prendre ses propres décisions, même si cela signifie refuser les conditions dont les gouvernements étrangers et les prêteurs assortissent leur aide." },
    pt: { short: "Recusar condições estrangeiras", text: "O meu país deve tomar as suas próprias decisões, mesmo que isso signifique recusar as condições que os governos estrangeiros e os credores associam à sua ajuda." },
    sw: { short: "Kukataa masharti ya nje", text: "Nchi yangu inapaswa kufanya maamuzi yake yenyewe, hata kama hilo linamaanisha kukataa masharti ambayo serikali za kigeni na wakopeshaji huyaambatanisha na msaada wao." },
    ar: { short: "رفض الشروط الأجنبية", text: "يجب أن يتخذ بلدي قراراته بنفسه، حتى لو كان ذلك يعني رفض الشروط التي تقرنها الحكومات الأجنبية والجهات المقرضة بمساعدتها." }
  },
  {
    id: "v7", ax: 1, topic: "movement",
    en: { short: "Free movement in Africa", text: "Citizens of other African countries should be able to live and work in my country without special restrictions." },
    fr: { short: "Libre circulation en Afrique", text: "Les citoyens des autres pays africains devraient pouvoir vivre et travailler dans mon pays sans restrictions particulières." },
    pt: { short: "Livre circulação em África", text: "Os cidadãos de outros países africanos devem poder viver e trabalhar no meu país sem restrições especiais." },
    sw: { short: "Uhuru wa kutembea ndani ya Afrika", text: "Raia wa nchi nyingine za Afrika wanapaswa kuruhusiwa kuishi na kufanya kazi katika nchi yangu bila vizuizi maalum." },
    ar: { short: "حرية التنقل داخل أفريقيا", text: "يجب أن يتمكن مواطنو الدول الأفريقية الأخرى من العيش والعمل في بلدي دون قيود خاصة." }
  },
  {
    id: "v8", ax: -1, topic: "preference",
    en: { short: "Citizens first for jobs", text: "Jobs and public contracts should go to citizens before foreigners." },
    fr: { short: "Emplois d’abord aux citoyens", text: "Les emplois et les marchés publics devraient revenir aux citoyens avant les étrangers." },
    pt: { short: "Empregos primeiro para os cidadãos", text: "Os empregos e os contratos públicos devem ser atribuídos aos cidadãos antes dos estrangeiros." },
    sw: { short: "Raia kwanza kwa ajira", text: "Ajira na mikataba ya umma zinapaswa kutolewa kwa raia kabla ya wageni." },
    ar: { short: "الوظائف للمواطنين أولًا", text: "يجب أن تُمنح الوظائف والعقود العامة للمواطنين قبل الأجانب." }
  },
  {
    id: "v9", ax: 1, topic: "pluralism",
    en: { short: "Many cultures, one country", text: "A country is stronger when it welcomes many cultures, languages and ways of life." },
    fr: { short: "Plusieurs cultures, un seul pays", text: "Un pays est plus fort lorsqu’il accueille de nombreuses cultures, langues et façons de vivre." },
    pt: { short: "Muitas culturas, um só país", text: "Um país é mais forte quando acolhe muitas culturas, línguas e modos de vida." },
    sw: { short: "Tamaduni nyingi, nchi moja", text: "Nchi huwa na nguvu zaidi inapokaribisha tamaduni nyingi, lugha nyingi na mitindo mingi ya maisha." },
    ar: { short: "ثقافات متعددة في بلد واحد", text: "يكون البلد أقوى عندما يرحّب بالعديد من الثقافات واللغات وأنماط الحياة." }
  },
  {
    id: "v10", ax: -1, topic: "tradition",
    en: { short: "Hold on to traditions", text: "A society that holds on to its traditions is stronger than one that keeps changing." },
    fr: { short: "S’attacher aux traditions", text: "Une société qui reste attachée à ses traditions est plus forte qu’une société qui ne cesse de changer." },
    pt: { short: "Manter-se ligado às tradições", text: "Uma sociedade que se mantém ligada às suas tradições é mais forte do que uma que está sempre a mudar." },
    sw: { short: "Kushikilia mila na desturi", text: "Jamii inayoshikilia mila na desturi zake ina nguvu zaidi kuliko jamii inayobadilika kila mara." },
    ar: { short: "التمسك بالتقاليد", text: "المجتمع المتمسك بتقاليده أقوى من المجتمع الذي يتغير باستمرار." }
  }
];
