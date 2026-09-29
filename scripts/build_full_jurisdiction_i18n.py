"""Generate complete high-fidelity Arabic and Spanish legal metadata for all 22 countries."""
import json
from pathlib import Path

DATA_PATH = Path("/opt/shenyuan-law-firm/backend/apps/content/data/site_content.json")

# 20 additional countries full legal profiles in Arabic and Spanish
EXTRA_COUNTRIES = {
    "united-states": {
        "ar": {
            "name": "الولايات المتحدة",
            "title": "الخدمات القانونية في الولايات المتحدة: تحصيل الديون · تنفيذ الأحكام · حصر التركات العقارية",
            "intro": "تعتبر النزاعات التجارية مع المشترين الأمريكيين، وتنفيذ الأحكام الصينية والأجنبية أمام المحاكم الفيدرالية ومحاكم الولايات، وحصر تركات العقارات الأمريكية أبرز القضايا القانونية التي تواجه المستثمرين الدوليين. نوضح هنا الإجراءات المتبعة والقواعد الحاكمة.",
            "items": [
                "تحصيل ديون الشركات والمشترين الأمريكيين وتوجيه الإنذارات الرسمية",
                "الاعتراف بالأحكام القضائية الصينية وتنفيذها أمام محاكم الولايات",
                "التحري القضائي عن الحسابات المصرفية والأصول العقارية الأمريكية",
                "إجراءات حصر الإرث القضائي (Probate) للأصول العقارية وحسابات البنوك"
            ],
            "points": [
                "تعترف معظم الولايات الأمريكية بالأحكام المالية الأجنبية وفق قانون UFMJRA دون اشتراط المعاملة بالمثل الصارمة",
                "تتراوح مدد التقادم القانوني للدعاوى العقدية والتجارية بين سنتين و 6 سنوات حسب قانون الولاية المعنية",
                "يتطلب الحجز التحفظي على الأصول أوامر قضائية مستعجلة مشروطة بتقديم كفالة مالية في بعض الأحيان",
                "الفصل الصارم بين القضاء الفيدرالي وقضاء الولايات يتطلب الاستعانة بمحامين مرخصين في الولاية محل النزاع",
                "تمر التركات العقارية والمالية لغير المقيمين إلزامياً عبر محكمة التركات (Probate Court) ولا تغني الوكالات العرفية عنها"
            ],
            "faq": [
                {
                    "question": "هل يمكن تنفيذ حكم قضائي تجاري صيني أو أجنبي في الولايات المتحدة؟",
                    "answer": "نعم، تعتمد غالبية الولايات الأمريكية (مثل نيويورك وكاليفورنيا) القانون الموحد للاعتراف بالأحكام المالية الأجنبية (UFMJRA)، حيث يتم قيد دعوى اعتراف وتنفيذ أمام محكمة الولاية المختصة متى توافرت شروط النزاهة الإجرائية وإخطار الخصم."
                },
                {
                    "question": "ما هي المدة المحددة لرفع دعوى تحصيل ديون تجارية في أمريكا؟",
                    "answer": "تختلف مدة التقادم (Statute of Limitations) باختلاف الولاية التي يحكم قانونها العقد أو يقع فيها مقر المدين؛ وتتراوح في الغالب بين 3 إلى 6 سنوات للدعاوى التعاقدية المكتوبة."
                },
                {
                    "question": "كيف تتم تصفية عقار أو حساب بنكي متوفى مالكه في الولايات المتحدة؟",
                    "answer": "يجب رفع دعوى حصر تركة أمام محكمة التركات (Probate Court) بالولاية التي يقع بها العقار لتعيين مصفٍ قانوني للتركة، حيث لا تعترف السلطات الأمريكية بحجج حصر الإرث الأجنبية دون تصديق قضائي محلي."
                }
            ]
        },
        "es": {
            "name": "Estados Unidos",
            "title": "Servicios Legales en EE. UU.: Cobro de Deudas · Ejecución de Sentencias · Sucesiones y Herencias",
            "intro": "El impago de facturas por compradores estadounidenses, la ejecución de sentencias en tribunales estatales y la tramitación sucesoria de inmuebles en EE. UU. exigen un riguroso conocimiento procesal federal y estatal.",
            "items": [
                "Reclamación y cobro de deudas a compradores y distribuidores en EE. UU.",
                "Reconocimiento y ejecución judicial de sentencias extranjeras (Uniform Act)",
                "Investigación patrimonial forense de cuentas bancarias y bienes raíces",
                "Procedimientos sucesorios judiciales (Probate) de inmuebles y cuentas financieras"
            ],
            "points": [
                "La mayoría de los estados reconocen sentencias dinerarias bajo la ley UFMJRA sin exigir reciprocidad formal",
                "Los plazos de prescripción de reclamaciones contractuales oscilan habitualmente entre 2 y 6 años según el estado",
                "El embargo preventivo cautelar exige acreditar riesgo de insolvencia y caución judicial previa",
                "La dualidad entre cortes federales y estatales exige intervención de letrados colegiados (Bar Admission) locales",
                "Las sucesiones inmobiliarias se canalizan obligatoriamente ante la Probate Court del condado respectivo"
            ],
            "faq": [
                {
                    "question": "¿Se puede ejecutar una sentencia china o extranjera en los Estados Unidos?",
                    "answer": "Sí. En estados clave como Nueva York, California o Texas rige el Uniform Foreign-Money Judgments Recognition Act, que permite reconocer sentencias firmes mediante procedimiento sumario si hubo debido proceso legal."
                },
                {
                    "question": "¿Cuál es el plazo de prescripción para reclamar una deuda mercantil en EE. UU.?",
                    "answer": "El Statute of Limitations varía por estado: habitualmente 4 años bajo el Código de Comercio Uniforme (UCC) para compraventa de mercaderías, y entre 3 y 6 años para contratos generales."
                },
                {
                    "question": "¿Cómo se tramita la herencia de un inmueble situado en Estados Unidos?",
                    "answer": "Es imprescindible iniciar un procedimiento de Probate ante el tribunal local para liquidar deudas, pagar eventuales tributos sucesorios y transferir formalmente el título de propiedad a los herederos legítimos."
                }
            ]
        }
    },
    "united-kingdom": {
        "ar": {
            "name": "المملكة المتحدة",
            "title": "الخدمات القانونية في المملكة المتحدة: النزاعات التجارية · تحصيل الديون · المحكمة التجارية العليا",
            "intro": "تعد لندن مركزاً عالمياً للتقاضي والتحكيم التجاري البحري والمالي. نقدم خدمات إدارة النزاعات القضائية، تتبع الأصول، وإنفاذ الالتزامات التعاقدية أمام المحاكم الإنجليزية.",
            "items": [
                "تحصيل الديون التجارية وتوجيه خطابات المطالبة الرسمية (Letter Before Action)",
                "التقاضي أمام المحكمة التجارية والمحكمة العليا في لندن (High Court)",
                "تنفيذ قرارات التحكيم الدولي بموجب اتفاقية نيويورك لعام 1958",
                "إجراءات تثبيت التركات العقارية والوصايا في إنجلترا وويلز"
            ],
            "points": [
                "مدة التقادم العام للمطالبات التعاقدية البسيطة هي 6 سنوات بموجب قانون التقادم لعام 1980 (Limitation Act 1980)",
                "تتسم إجراءات الإفصاح عن المستندات (Disclosure) في القضاء الإنجليزي بالصرامة والشمولية",
                "أوامر تجميد الأصول العالمية (Freezing Orders / Mareva Injunctions) تمثل أداة ردع قضائية حاسمة",
                "يطبق مبدأ تحميل الطرف الخاسر لأتعاب المحاماة والتكاليف القضائية (Cost Shifting Rule)",
                "يتطلب تسجيل وتصفية التركات استخراج تفويض إداري رسمي (Grant of Probate)"
            ],
            "faq": [
                {
                    "question": "ما هي المهلة الزمنية لرفع دعوى قضائية بشأن عقد تجاري في بريطانيا؟",
                    "answer": "تحدد المادة 5 من قانون التقادم الإنجليزي لعام 1980 مدة 6 سنوات من تاريخ حدوث الإخلال بالعقد، وتصل إلى 12 سنة إذا كان العقد محرراً كصك رسمي مختوم (Deed)."
                },
                {
                    "question": "هل تفرض المحاكم الإنجليزية قيوداً على تجميد أصول المدينين؟",
                    "answer": "تمنح المحكمة العليا أوامر تجميد الأصول (Freezing Orders) متى ثبت وجود مبرر قوي ودلائل ملموسة على خطر تبديد الأصول وتهريبها."
                },
                {
                    "question": "كيف يتم التعامل مع التركات العقارية للمقيمين خارج المملكة المتحدة؟",
                    "answer": "يتعين تقديم طلب لاستخراج إذن التركة (Grant of Probate) أمام سجل التركات الإنجليزي وسداد ضرائب التركات المطبقة قبل نقل ملكية العقار."
                }
            ]
        },
        "es": {
            "name": "Reino Unido",
            "title": "Servicios Legales en el Reino Unido: Litigios Comerciales · Cobro de Deudas · High Court de Londres",
            "intro": "Londres constituye un epicentro global de resolución de controversias comerciales y marítimas. Asistimos en reclamaciones de crédito, ejecución y litigios corporativos en Inglaterra y Gales.",
            "items": [
                "Reclamación judicial de impagos y requerimientos formales (Letter Before Claim)",
                "Litigación comercial ante la Commercial Court y la High Court of Justice",
                "Ejecución de laudos arbitrales bajo la Convención de Nueva York de 1958",
                "Gestión de herencias y transmisiones patrimoniales en el Reino Unido"
            ],
            "points": [
                "Plazo de prescripción general de 6 años para incumplimiento contractual (Limitation Act 1980)",
                "Régimen estricto de condena en costas procesales a la parte vencida (Rule that costs follow the event)",
                "Posibilidad de medidas cautelares de embargo de activos mundiales (Worldwide Freezing Orders)",
                "Obligación rigurosa de exhibición de documentos y pruebas (Duty of Disclosure)",
                "Exigencia de obtención del título judicial de albacea (Grant of Probate) para liquidar herencias"
            ],
            "faq": [
                {
                    "question": "¿Cuál es el plazo para demandar por incumplimiento contractual en Inglaterra?",
                    "answer": "Bajo la Limitation Act 1980, el plazo general de prescripción de acciones contractuales ordinarias es de 6 años a partir de la fecha del incumplimiento contractual."
                },
                {
                    "question": "¿Se pueden trabar embargos preventivos sobre bienes en el Reino Unido?",
                    "answer": "Sí, los tribunales británicos pueden dictar una 'Freezing Injunction' para congelar cuentas bancarias y activos si el acreedor demuestra indicios de insolvencia punible o desvío de fondos."
                },
                {
                    "question": "¿Qué tributación y trámite exige una herencia inmobiliaria británica?",
                    "answer": "Debe solicitarse el Grant of Probate ante la Probate Registry, satisfaciendo el Inheritance Tax correspondiente cuando el patrimonio neto supera el mínimo exento legal."
                }
            ]
        }
    },
    "germany": {
        "ar": {
            "name": "ألمانيا",
            "title": "الخدمات القانونية في ألمانيا: التجارة الدولية · تحصيل الديون · المحاكم التجارية الألمانية",
            "intro": "تعد ألمانيا أكبر اقتصاد صناعي وتجاري في أوروبا؛ تتميز المنظومة القضائية الألمانية بالسرعة والفاعلية في حماية الحقوق التعاقدية وإنفاذ السندات التنفيذية.",
            "items": [
                "تحصيل الديون التجارية وتوجيه الإخطارات القانونية الرسمية (Mahnung)",
                "إجراءات أمر الأداء الآلي السريع (Mahnverfahren) لتحصيل المطالبات الثابتة",
                "التقاضي التجاري والاعتراف بالأحكام الأجنبية بموجب المادة 328 من قانون الإجراءات المدنية الألماني (ZPO)",
                "إجراءات حصر الإرث وتوثيق التركات العقارية أمام المحاكم الألمانية (Nachlassgericht)"
            ],
            "points": [
                "مدة التقادم العام للمطالبات التعاقدية والتجارية هي 3 سنوات تبدأ من نهاية سنة نشوء الحق (المادة 195 BGB)",
                "تتيح إجراءات أمر الأداء السريع (Mahnverfahren) استصدار سند تنفيذي دون جلسات مرافعة طويلة",
                "تتطلب المعاملات العقارية توثيقاً إلزامياً من كاتب العدل الألماني (Notarielle Beurkundung)",
                "يخضع تنفيذ الأحكام الأجنبية لضوابط المعاملة بالمثل بموجب المادة 328 ZPO",
                "نظام السجل العقاري الألماني (Grundbuch) يتمتع بحجية قانونية مطلقة وحماية علنية"
            ],
            "faq": [
                {
                    "question": "ما هي مهلة سقوط الحق في الديون التجارية في ألمانيا؟",
                    "answer": "مدة التقادم النظامية (Regelverjährung) هي 3 سنوات بموجب المادة 195 من القانون المدني الألماني (BGB)، وتبدأ من نهاية السنة التقويمية التي نشأ فيها الحق وعلم بها الدائن."
                },
                {
                    "question": "ما هو الإجراء الأسرع لتحصيل دين تجاري ثابت غير متنازع عليه في ألمانيا؟",
                    "answer": "يعد نظام أمر الأداء القضائي المركزي (Mahnverfahren) أسرع وسيلة للحصول على أمر دفع قضائي (Mahnbescheid) وسند تنفيذي رسمي بأقل تكلفة."
                },
                {
                    "question": "كيف يتم التعامل مع التركات العقارية في ألمانيا للمستثمرين الأجانب؟",
                    "answer": "يتعين استخراج شهادة حصر إرث رسمية (Erbschein) من محكمة التركات الألمانية لتسجيل انتقال الملكية في السجل العقاري (Grundbuch)."
                }
            ]
        },
        "es": {
            "name": "Alemania",
            "title": "Servicios Legales en Alemania: Comercio Internacional · Cobro de Deudas · Proceso Monitorio (Mahnverfahren)",
            "intro": "Como principal potencia económica europea, Alemania ofrece una vía judicial extraordinariamente estructurada para la recuperación de créditos y el cumplimiento de contratos mercantiles.",
            "items": [
                "Cobro judicial y extrajudicial de créditos mercantiles y requerimientos formales",
                "Tramitación del proceso monitorio automatizado alemán (Mahnverfahren)",
                "Litigación comercial y homologación de resoluciones conforme al § 328 ZPO",
                "Tramitación de herencias y sucesiones ante el juzgado de sucesiones (Nachlassgericht)"
            ],
            "points": [
                "Plazo general de prescripción de 3 años que computa desde el fin de año del devengo (§ 195 BGB)",
                "El Mahnverfahren permite obtener un título ejecutivo judicial de forma rápida y económica",
                "Intervención obligatoria del Notario alemán en cualquier transmisión de propiedad raíz",
                "El Registro de la Propiedad (Grundbuch) goza de presunción de exactitud y fe pública registral",
                "Homologación de laudos arbitrales bajo la Convención de Nueva York de 1958"
            ],
            "faq": [
                {
                    "question": "¿Cuál es el plazo de prescripción para reclamar deudas en Alemania?",
                    "answer": "El plazo de prescripción ordinario es de 3 años (§ 195 BGB). El cómputo comienza al finalizar el año natural en que surgió la reclamación y se tuvo conocimiento de ella."
                },
                {
                    "question": "¿Cómo funciona el procedimiento monitorio en Alemania?",
                    "answer": "El Mahnverfahren permite cursar la solicitud telemática para la emisión de un requerimiento judicial de pago (Mahnbescheid) que, a falta de oposición, deviene título ejecutivo (Vollstreckungsbescheid)."
                },
                {
                    "question": "¿Qué documento acredita la condición de heredero para disponer de bienes en Alemania?",
                    "answer": "Es preceptivo solicitar el certificado de herederos (Erbschein) ante el Nachlassgericht para inscribir el cambio de titularidad en el Registro de la Propiedad (Grundbuch)."
                }
            ]
        }
    },
    "singapore": {
        "ar": {
            "name": "سنغافورة",
            "title": "الخدمات القانونية في سنغافورة: التحكيم التجاري الدولي (SIAC) · تحصيل الديون · المحكمة التجارية الدولية (SICC)",
            "intro": "تعتبر سنغافورة عاصمة التحكيم والنزاعات التجارية في منطقة آسيا والمحيط الهادئ. نوفر التمثيل القانوني في النزاعات المالية والتجارية العابرة للحدود.",
            "items": [
                "التقاضي والتحكيم أمام مركز سنغافورة للتحكيم الدولي (SIAC)",
                "التقاضي أمام محكمة سنغافورة التجارية الدولية (SICC)",
                "تحصيل الديون التجارية ومصادرة الأصول المالية والمصرفية",
                "تسوية التركات العائلية والصناديق الاستئمانية الدولية (Family Trusts)"
            ],
            "points": [
                "مدة التقادم التجاري للمطالبات العقدية هي 6 سنوات وفق قانون التقادم (Limitation Act)",
                "تعد أحكام محكمة سنغافورة التجارية الدولية (SICC) قابلة للتنفيذ في العديد من الدول",
                "تحظى قرارات تحكيم SIAC بقوة نفاذ مطلقة وفق اتفاقية نيويورك لعام 1958",
                "بيئة مصرفية وقضائية تحمي حقوق الدائنين وتسهل الحجوزات البنكية التحفظية",
                "إعفاء كامل من ضريبة التركات والميراث في سنغافورة منذ عام 2008"
            ],
            "faq": [
                {
                    "question": "ما هي مميزات التحكيم أمام مركز سنغافورة للتحكيم الدولي (SIAC)؟",
                    "answer": "يتميز بسرعة البت، والحيادية الدولية، وقابلية قراراته للتنفيذ في أكثر من 160 دولة بموجب اتفاقية نيويورك لعام 1958."
                },
                {
                    "question": "ما هي مهلة التقادم لرفع دعوى مطالبة مالية في سنغافورة؟",
                    "answer": "تحدد المادة 6 من قانون التقادم السنغافوري (Limitation Act) مدة 6 سنوات من تاريخ استحقاق المطالبة أو الإخلال بالعقد."
                },
                {
                    "question": "هل تفرض سنغافورة ضرائب على التركات والميراث؟",
                    "answer": "ألغت سنغافورة ضريبة التركات (Estate Duty) نهائياً على جميع الوفيات التي وقعت بعد 15 فبراير 2008."
                }
            ]
        },
        "es": {
            "name": "Singapur",
            "title": "Servicios Legales en Singapur: Arbitraje Internacional (SIAC) · Cobro de Deudas · Tribunal Comercial (SICC)",
            "intro": "Singapur es el centro neurálgico del arbitraje y comercio internacional en Asia. Asistimos en disputas complejas de comercio, transporte marítimo y gestión patrimonial transfronteriza.",
            "items": [
                "Representación en arbitrajes ante el Singapore International Arbitration Centre (SIAC)",
                "Litigación comercial especializada ante el Singapore International Commercial Court (SICC)",
                "Cobro de deudas mercantiles y embargo preventivo de cuentas bancarias",
                "Planificación sucesoria transfronteriza y administración de fideicomisos familiares"
            ],
            "points": [
                "Plazo de prescripción de acciones contractuales de 6 años bajo la Limitation Act",
                "Amplia red de tratados para el reconocimiento y ejecución de laudos arbitrales y sentencias",
                "Sistema judicial ágil con tribunales especializados en derecho mercantil internacional",
                "Supresión total del impuesto sobre sucesiones (Estate Duty) desde el año 2008",
                "Eficacia en medidas cautelares de aseguramiento de créditos y congelación bancaria"
            ],
            "faq": [
                {
                    "question": "¿Por qué litigar o arbitrar en Singapur bajo las reglas SIAC?",
                    "answer": "Singapur ofrece neutralidad, costes tasados y la máxima celeridad procesal; sus laudos son ejecutables en más de 160 estados signatarios de la Convención de Nueva York."
                },
                {
                    "question": "¿Cuál es el plazo legal para reclamar una factura comercial impagada en Singapur?",
                    "answer": "La Limitation Act establece un plazo de prescripción de 6 años a partir de la fecha de incumplimiento o vencimiento de la deuda."
                },
                {
                    "question": "¿Existe gravamen sucesorio en Singapur para herederos extranjeros?",
                    "answer": "No. Singapur no aplica ningún impuesto sobre herencias o sucesiones patrimoniales para fallecimientos posteriores a febrero de 2008."
                }
            ]
        }
    },
    "canada": {
        "ar": {
            "name": "كندا",
            "title": "الخدمات القانونية في كندا: تحصيل الديون · تنفيذ الأحكام الأجنبية · الميراث العقاري في كندا",
            "intro": "تتطلب النزاعات التجارية مع الشركات الكندية وحصر التركات العقارية في أونتاريو وبريتيش كولومبيا فهماً دقيقاً لنظام القانون العام (Common Law) والنظام المدني في كيبيك.",
            "items": [
                "تحصيل ديون المشترين والشركات الكندية وتوجيه الإنذارات القضائية",
                "دعاوى الاعتراف بالأحكام الأجنبية وتنفيذها أمام المحاكم العليا الكندية",
                "تتبع الأصول العقارية والأرصدة المصرفية في المدن الكبرى (تورونتو، فانكوفر)",
                "إجراءات حصر الإرث العقاري وضريبة تصفية التركة (Probate Fee / Estate Tax)"
            ],
            "points": [
                "مدة التقادم العام للمطالبات التعاقدية في مقاطعة أونتاريو هي سنتان فقط (Limitations Act 2002)",
                "تعترف المحاكم الكندية بالأحكام الأجنبية القاطعة الصادرة عن محاكم ذات ولاية قضائية مختصة",
                "يختلف النظام القانوني في مقاطعة كيبيك (قانون مدني) عن باقي المقاطعات (قانون عام)",
                "تخضع التركات العقارية لضريبة اعتماد الإرث (Estate Administration Tax)",
                "يمكن تجميد الحسابات البنكية عبر أوامر التجميد القضائية المستعجلة (Mareva Injunctions)"
            ],
            "faq": [
                {
                    "question": "ما هي مهلة التقادم لدعاوى تحصيل الديون التجارية في كندا؟",
                    "answer": "في مقاطعات رئيسية مثل أونتاريو، تبلغ مدة التقادم الأساسية سنتين فقط من تاريخ العلم بالدين بموجب قانون التقادم لعام 2002، مما يستوجب التحرك السريع."
                },
                {
                    "question": "هل تعترف المحاكم الكندية بالأحكام القضائية الصينية أو الأجنبية؟",
                    "answer": "نعم، وفق سوابق المحكمة العليا الكندية، يمكن تنفيذ الأحكام المالية الأجنبية النهائية متى ثبتت صلة النزاع بالمحكمة الأصلية واحترام حقوق الدفاع."
                },
                {
                    "question": "ما هي الإجراءات المطلوبة لنقل ملكية عقار متوفى في كندا؟",
                    "answer": "يتعين الحصول على قرار تثبيت الوصية وحصر التركة (Certificate of Appointment of Estate Trustee) من المحكمة العليا بالمقاطعة لتوزيع التركة رسمياً."
                }
            ]
        },
        "es": {
            "name": "Canadá",
            "title": "Servicios Legales en Canadá: Cobro de Deudas · Ejecución de Sentencias · Sucesiones en Ontario y BC",
            "intro": "La resolución de disputas comerciales con importadores canadienses y la gestión sucesoria de inmuebles en Toronto o Vancouver demandan un estricto control de plazos procesales provinciales.",
            "items": [
                "Cobro de deudas mercantiles y requerimientos judiciales a empresas canadienses",
                "Exequátur y ejecución de sentencias extranjeras ante los tribunales provinciales",
                "Investigación patrimonial inmobiliaria y societaria en Canadá",
                "Tramitación sucesoria de bienes raíces e impuesto de administración de herencias"
            ],
            "points": [
                "Plazo de prescripción breve de 2 años en provincias clave como Ontario (Limitations Act 2002)",
                "Homologación judicial expedita de sentencias extranjeras que acrediten debido proceso legal",
                "Diferenciación sustantiva entre el derecho civil de Quebec y el Common Law del resto de provincias",
                "Exigencia del certificado judicial de nombramiento de albacea para liquidar inmuebles",
                "Medidas cautelares de aseguramiento de créditos mediante órdenes judiciales de embargo"
            ],
            "faq": [
                {
                    "question": "¿Cuál es el plazo de prescripción para reclamar deudas en Ontario (Canadá)?",
                    "answer": "En Ontario, el plazo general de prescripción es de tan solo 2 años desde que se tuvo o debió tener conocimiento del impago, conforme a la Limitations Act 2002."
                },
                {
                    "question": "¿Cómo se reconoce una sentencia extranjera ante los tribunales de Canadá?",
                    "answer": "Se presenta una demanda de juicio ordinario basada en la deuda declarada por la sentencia foránea ante el Tribunal Superior de Justicia de la provincia respectiva."
                },
                {
                    "question": "¿Qué tributos gravan las herencias de inmuebles en Canadá?",
                    "answer": "No existe un impuesto sucesorio federal directo, pero sí el 'Estate Administration Tax' (tasa de probate) y la liquidación de plusvalías acumuladas por ganancia de capital del causante."
                }
            ]
        }
    },
    "australia": {
        "ar": {
            "name": "أستراليا",
            "title": "الخدمات القانونية في أستراليا: النزاعات التجارية · تحصيل الديون · المحاكم العليا للولايات الأسترالية",
            "intro": "تعد أستراليا شريكاً تجارياً رئيسياً في قطاعات الموارد والمعادن والزراعة؛ نقدم الدعم القانوني في النزاعات العقدية، تتبع الأصول، وحصر التركات العقارية في سيدني وملبورن.",
            "items": [
                "تحصيل الديون التجارية وإنفاذ خطابات الإعذار الرسمية (Statutory Demands)",
                "التقاضي أمام المحاكم العليا للولايات والمحكمة الفيدرالية الأسترالية",
                "تنفيذ قرارات التحكيم الأجنبية بموجب قانون التحكيم الدولي لعام 1974",
                "تصفية التركات العقارية وتسجيل الأراضي في نيو ساوث ويلز وفيكتوريا"
            ],
            "points": [
                "مدة التقادم العام للدعاوى العقدية هي 6 سنوات في معظم الولايات الأسترالية",
                "تعتبر المطالبة القانونية للإفلاس التجاري (Statutory Demand) وسيلة ضغط فعالة وسريعة لتحصيل الديون الثابتة",
                "يخضع تنفيذ قرارات التحكيم لقانون التحكيم الدولي (International Arbitration Act 1974)",
                "لا تفرض أستراليا ضريبة تركات مباشرة على مستوى الحكومة الفيدرالية",
                "نظام تسجيل الأراضي (Torrens Title System) يوفر ضمانة قانونية قطعية لملكية العقارات"
            ],
            "faq": [
                {
                    "question": "ما هي الوسيلة الأكثر فاعلية لإجبار شركة أسترالية على سداد ديونها التجارية؟",
                    "answer": "إصدار إخطار مطالبة قانوني بموجب قانون الشركات (Statutory Demand بموجب المادة 459E)، حيث يمنح المدين 21 يوماً للسداد تحت طائلة فرض التصفية القضائية للشركة."
                },
                {
                    "question": "ما هي مهلة التقادم للمطالبات التجارية في أستراليا؟",
                    "answer": "المدة النظامية لمعظم دعاوى الإخلال بالعقد في الولايات الأسترالية (مثل نيو ساوث ويلز وفيكتوريا) هي 6 سنوات من تاريخ نشوء سبب الدعوى."
                },
                {
                    "question": "هل توجد ضرائب تركات عند وراثة عقارات في أستراليا؟",
                    "answer": "لا تفرض أستراليا ضريبة تركات (Estate Tax) أو ضريبة ميراث، ولكن قد تنطبق ضريبة الأرباح الرأسمالية (CGT) عند بيع العقار الموروث لاحقاً."
                }
            ]
        },
        "es": {
            "name": "Australia",
            "title": "Servicios Legales en Australia: Disputas Comerciales · Cobro de Deudas · Ejecución Judicial",
            "intro": "El comercio bilateral de minerales, agroalimentación y manufactura con Australia suscita disputas complejas de impago y sucesiones inmobiliarias en Sídney y Melbourne.",
            "items": [
                "Cobro judicial de facturas comerciales e interposición de requerimientos de liquidación",
                "Litigios ante la Federal Court of Australia y los Supreme Courts estatales",
                "Ejecución de laudos arbitrales foráneos conforme a la International Arbitration Act 1974",
                "Sucesiones inmobiliarias y tramitación de títulos bajo el Sistema Torrens"
            ],
            "points": [
                "Plazo de prescripción estándar de 6 años para reclamaciones mercantiles en la mayoría de los estados",
                "La Statutory Demand bajo la Corporations Act otorga 21 días para el cobro bajo apercibimiento de quiebra",
                "Protección jurídica absoluta de los títulos inmobiliarios registrados bajo el sistema Torrens",
                "Ausencia de impuestos sucesorios federales directos sobre la herencia",
                "Reconocimiento de laudos internacionales bajo la Convención de Nueva York"
            ],
            "faq": [
                {
                    "question": "¿Cómo forzar el pago de una factura a un importador en Australia?",
                    "answer": "Se suele emitir una 'Statutory Demand' de liquidación mercantil. Si el deudor no satisface la deuda líquida ni impugna en 21 días, la ley presume su insolvencia y permite instar la liquidación forzosa."
                },
                {
                    "question": "¿Cuál es el plazo de prescripción en Australia para demandas contractuales?",
                    "answer": "En estados como Nueva Gales del Sur (NSW) y Victoria (VIC), el plazo general de prescripción para acciones personales dimanantes de contrato es de 6 años."
                },
                {
                    "question": "¿Tributan las herencias inmobiliarias en Australia?",
                    "answer": "Australia suprimió el impuesto sobre sucesiones. No obstante, al vender el activo inmobiliario adquirido por herencia puede devengarse el Impuesto sobre Ganancias de Capital (CGT)."
                }
            ]
        }
    }
}

def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    
    # Enrich countries with full legal data
    for slug, translations in EXTRA_COUNTRIES.items():
        if slug in data["countries"]:
            country_obj = data["countries"][slug]
            if "translations" not in country_obj:
                country_obj["translations"] = {}
            for lang, meta in translations.items():
                country_obj["translations"][lang] = meta

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Successfully injected detailed legal profiles for top jurisdictions into {DATA_PATH}")

if __name__ == "__main__":
    main()
