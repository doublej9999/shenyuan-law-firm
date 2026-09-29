"""Enrich backend/apps/content/data/site_content.json with full 4-lang (ar & es) translations."""
import json
from pathlib import Path

DATA_PATH = Path("/opt/shenyuan-law-firm/backend/apps/content/data/site_content.json")

SERVICES_I18N = {
    "trade": {
        "ar": {
            "title": "النزاعات التجارية الدولية",
            "intro": "معالجة النزاعات الناشئة عن تنفيذ الصفقات، الفواتير غير المسددة، عقود الوكالة والتوزيع والعقود عبر الحدود، مع تقييم مسارات التفاوض أو التحصيل أو التقاضي بناءً على وقائع الدين والأدلة المتاحة.",
            "items": [
                "تأخر سداد الفواتير / إخلال الموردين بالالتزامات",
                "صياغة ومراجعة عقود الوكالة والتوزيع والعقود التجارية الدولية",
                "نزاعات الجمارك، اللوجستيات ومطابقة جودة البضائع",
                "كشف الاحتيال التجاري الدولي وآليات التعامل القانوني معه"
            ],
            "materials": [
                "العقود، أوامر الشراء، الفواتير وسجلات التحويل المالي",
                "بوالص الشحن، مستندات التخليص الجمركي وتقارير فحص الجودة",
                "المراسلات عبر البريد الإلكتروني، واتساب أو أي قنوات تواصل أخرى",
                "اسم الشركة الطرف الآخر، العنوان وتفاصيل الاتصال بالمسؤولين"
            ]
        },
        "es": {
            "title": "Disputas de Comercio Internacional",
            "intro": "Gestionamos disputas sobre cumplimiento comercial, impago de facturas, agencias, distribución y contratos transfronterizos — evaluando vías de negociación, recobro o litigio a partir de las pruebas documentales.",
            "items": [
                "Impago de facturas / incumplimiento contractual de proveedores",
                "Revisión de contratos de agencia, distribución y comercio exterior",
                "Disputas aduaneras, logísticas y de disconformidad de calidad",
                "Identificación y respuesta legal ante fraudes comerciales internacionales"
            ],
            "materials": [
                "Contratos, órdenes de compra, facturas y comprobantes de pago",
                "Conocimientos de embarque (B/L), despachos aduaneros y actas de inspección",
                "Comunicaciones por correo electrónico, WhatsApp u otros canales",
                "Denominación de la empresa contraparte, domicilio y datos de contacto"
            ]
        }
    },
    "recovery": {
        "ar": {
            "title": "التقاضي وتحصيل الديون عبر الحدود",
            "intro": "تقييم خيارات التحصيل والتقاضي والتنفيذ القضائي استناداً إلى وقائع المديونية وتتبع الأصول، بما يشمل الأصول داخل البر الرئيسي للصين وخارجها.",
            "items": [
                "تحصيل ديون العملاء والشركات في الخارج",
                "التحري عن الأصول وتتبعها في الصين وخارجها",
                "تنفيذ الأحكام القضائية وقرارات التحكيم عبر الحدود",
                "التحقيق في وقائع الاحتيال التجاري والمالي"
            ],
            "materials": [
                "قيمة الدين وتاريخ الاستحقاق",
                "بيانات الشركة أو الشخص المدين",
                "العقود، كشوف الحساب وسجلات الإخطارات والمطالبات",
                "الأحكام القضائية أو قرارات التحكيم السابقة أو دلائل الأصول"
            ]
        },
        "es": {
            "title": "Litigios y Recobro Transfronterizo de Deudas",
            "intro": "Evaluamos opciones de cobro, litigio y ejecución a partir de los hechos del impago y el rastreo patrimonial, abarcando activos tanto en China continental como en el extranjero.",
            "items": [
                "Cobro de deudas a clientes extranjeros y empresas morosas",
                "Investigación y rastreo de activos en China y en el exterior",
                "Reconocimiento y ejecución transfronteriza de sentencias y laudos arbitrales",
                "Investigación de fraude comercial y patrimonial"
            ],
            "materials": [
                "Importe adeudado y fecha de vencimiento",
                "Datos de la empresa deudora o persona física",
                "Contratos, facturas, estados de cuenta y requerimientos de pago",
                "Sentencias o laudos existentes o pistas sobre bienes y activos"
            ]
        }
    },
    "legacy": {
        "ar": {
            "title": "الميراث ونزاعات الأصول العائلية",
            "intro": "المساعدة في حل نزاعات التركات والميراث والعقارات والأسهم والأصول العائلية عبر اختصاصات قضائية متعددة بين الصين والخارج، مع توضيح المستندات والاختصاصات والترتيب الإجرائي.",
            "items": [
                "الميراث عبر الحدود بين الصين ودول متعددة",
                "حصر تركات العقارات وحصص الشركات والحسابات المصرفية",
                "تنفيذ الوصايا وتقسيم التركات العائلية",
                "إجراءات حالات غياب الورثة أو الخلافات بين أفراد الأسرة"
            ],
            "materials": [
                "إثبات صلة القرابة (شجرة العائلة / القيود الرسمية)",
                "شهادة الوفاة، الوصية أو وثائق حصر التركة",
                "بيانات ودلائل الأصول (عقارات، أسهم، حسابات بنكية)",
                "الدول أو الأقاليم المعنية وبيانات الاتصال بأفراد الأسرة"
            ]
        },
        "es": {
            "title": "Herencias y Disputas de Activos Familiares",
            "intro": "Facilitamos la tramitación de herencias multijurisdiccionales, inmuebles, participaciones societarias y conflictos familiares entre China y el exterior, clarificando requisitos documentales y orden procesal.",
            "items": [
                "Herencias transfronterizas entre China continental y terceros países",
                "Transmisión de bienes inmuebles, acciones corporativas y cuentas bancarias",
                "Testamentos y partición judicial o notarial de herencias",
                "Gestión de herederos no localizables o desacuerdos familiares"
            ],
            "materials": [
                "Certificados y actas que acrediten el parentesco",
                "Certificado de defunción, testamento o inventario de bienes",
                "Pistas o documentación sobre activos (inmuebles, acciones, depósitos)",
                "Países involucrados e información de contacto de los herederos"
            ]
        }
    }
}

# High-fidelity translations for jurisdictions
COUNTRY_METADATA = {
    "united-states": {
        "ar": {"name": "الولايات المتحدة", "title": "الخدمات القانونية في الولايات المتحدة: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري"},
        "es": {"name": "Estados Unidos", "title": "Servicios Legales en EE. UU.: Cobro de Deudas · Ejecución de Sentencias · Herencias"}
    },
    "canada": {
        "ar": {"name": "كندا", "title": "الخدمات القانونية في كندا: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري"},
        "es": {"name": "Canadá", "title": "Servicios Legales en Canadá: Cobro de Deudas · Ejecución de Sentencias · Herencias"}
    },
    "australia": {
        "ar": {"name": "أستراليا", "title": "الخدمات القانونية في أستراليا: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري"},
        "es": {"name": "Australia", "title": "Servicios Legales en Australia: Cobro de Deudas · Ejecución de Sentencias · Herencias"}
    },
    "singapore": {
        "ar": {"name": "سنغافورة", "title": "الخدمات القانونية في سنغافورة: تحصيل الديون · التحكيم الدولي · إدارة الأصول"},
        "es": {"name": "Singapur", "title": "Servicios Legales en Singapur: Cobro de Deudas · Arbitraje Internacional · Gestión Patrimonial"}
    },
    "united-kingdom": {
        "ar": {"name": "المملكة المتحدة", "title": "الخدمات القانونية في بريطانيا: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري"},
        "es": {"name": "Reino Unido", "title": "Servicios Legales en el Reino Unido: Cobro de Deudas · Ejecución de Sentencias · Herencias"}
    },
    "hong-kong": {
        "ar": {"name": "هونغ كونغ", "title": "الخدمات القانونية في هونغ كونغ: النزاعات التجارية · تنفيذ الأحكام عبر الحدود · الصناديق الاستئمانية"},
        "es": {"name": "Hong Kong", "title": "Servicios Legales en Hong Kong: Disputas Comerciales · Ejecución Transfronteriza · Fideicomisos"}
    },
    "germany": {
        "ar": {"name": "ألمانيا", "title": "الخدمات القانونية في ألمانيا: التجارة الدولية · تحصيل الديون · تنفيذ الأحكام"},
        "es": {"name": "Alemania", "title": "Servicios Legales en Alemania: Comercio Internacional · Cobro de Deudas · Ejecución de Sentencias"}
    },
    "japan": {
        "ar": {"name": "اليابان", "title": "الخدمات القانونية في اليابان: التجارة الدولية · تحصيل الديون · التركات العقارية"},
        "es": {"name": "Japón", "title": "Servicios Legales en Japón: Comercio Internacional · Cobro de Deudas · Sucesiones Inmobiliarias"}
    },
    "united-arab-emirates": {
        "ar": {
            "name": "الإمارات (دبي)",
            "title": "الخدمات القانونية في الإمارات: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري في دبي",
            "intro": "تعد دبي مركز التجارة الإقليمي في الشرق الأوسط ومقراً رئيسياً لمجتمع الأعمال الدولي. تتركز فيها نزاعات الشحن والتحصيل وميراث الاستثمارات العقارية.",
            "items": [
                "تحصيل الديون من المشترين والوسطاء التجاريين في الإمارات",
                "الاعتراف بالأحكام القضائية الصينية والأجنبية وتنفيذها في الإمارات",
                "تتبع والتحري عن الأصول العقارية والحسابات المصرفية في دبي",
                "تسوية التركات والميراث العائلي وتسجيل العقارات في دبي"
            ],
            "points": [
                "اتفاقية المساعدة القضائية بين الصين والإمارات لعام 2004 تشمل الاعتراف بالأحكام وتنفيذها",
                "نظام قضائي مزدوج: المحاكم الاتحادية ومحاكم مركز دبي المالي العالمي (DIFC)",
                "إعفاء كامل من ضريبة الدخل وضريبة التركات؛ يخضع غير المسلمين لقانون الأحوال الشخصية المدني مع حرية الوصية",
                "يخضع المسلمون لقواعد الميراث الشرعي مع تنظيم الوصايا في الحدود المقررة",
                "يتطلب التحري عن الحسابات البنكية وحركة الأموال أوامر قضائية نظامية"
            ],
            "faq": [
                {
                    "question": "هل يمكن تنفيذ حكم قضائي أجنبي أو صيني في دولة الإمارات؟",
                    "answer": "نعم، بموجب اتفاقية المساعدة القضائية المدنية والتجارية لعام 2004 وقوانين الإجراءات المدنية الإماراتية، يمكن تقديم طلب التنفيذ أمام المحاكم الاتحادية أو محاكم مركز دبي المالي العالمي (DIFC) بحسب طبيعة النزاع وموقع الأصول."
                },
                {
                    "question": "هل توجد ضريبة تركات أو ميراث في دولة الإمارات؟",
                    "answer": "لا تفرض الإمارات أي ضريبة تركات أو ميراث. بالنسبة لغير المسلمين، يتم تطبيق قانون الأحوال الشخصية المدني مع الاعتراف بالوصايا المسجلة، بينما يطبق على المسلمين نظام الميراث الشرعي."
                },
                {
                    "question": "ما هي الخطوات الأساسية لتحصيل الديون التجارية في دبي؟",
                    "answer": "تتميز دبي ببيئة قانونية فعالة لحماية الدائنين؛ يوصى بتوثيق الأدلة مبكراً وتوجيه إنذار قانوني عبر محامٍ معتمد وتقييم سرعة مسار محاكم DIFC أو القضاء المحلي."
                }
            ]
        },
        "es": {
            "name": "EAU (Dubái)",
            "title": "Servicios Legales en EAU: Cobro de Deudas · Ejecución de Sentencias · Herencias en Dubái",
            "intro": "Dubái es el principal nodo comercial de Oriente Medio. Aquí se concentran disputas por facturas comerciales, cobro a intermediarios y sucesiones de inversiones inmobiliarias.",
            "items": [
                "Cobro de deudas a compradores e intermediarios comerciales en EAU",
                "Reconocimiento y ejecución de sentencias extranjeras en los EAU",
                "Rastreo e investigación de bienes inmuebles y cuentas bancarias en Dubái",
                "Planificación de herencias transfronterizas y transmisión inmobiliaria en Dubái"
            ],
            "points": [
                "El tratado de asistencia judicial China-EAU de 2004 ampara la ejecución de sentencias",
                "Vía dual: Tribunales Federales y Tribunales del DIFC (Centro Financiero Internacional de Dubái)",
                "Sin impuestos sobre sucesiones ni sobre la renta; ley civil de sucesiones para no musulmanes con validez del testamento",
                "La sucesión de musulmanes se rige por el derecho sucesorio islámico",
                "El rastreo bancario requiere mandamiento judicial previo"
            ],
            "faq": [
                {
                    "question": "¿Se puede ejecutar una sentencia china o extranjera en los Emiratos Árabes Unidos?",
                    "answer": "Sí, en virtud del tratado bilateral de asistencia judicial de 2004 y la normativa procesal civil de EAU, se puede instar el reconocimiento ante los tribunales locales o ante las cortes del DIFC."
                },
                {
                    "question": "¿Existe impuesto de sucesiones o herencias en EAU?",
                    "answer": "No existe impuesto de sucesiones en EAU. Los no musulmanes pueden inscribir testamentos conforme al régimen civil especial, mientras que para musulmanes rige la ley islámica."
                },
                {
                    "question": "¿Qué aspectos son clave para reclamar una deuda comercial en Dubái?",
                    "answer": "El marco legal de Dubái ofrece sólidas garantías al acreedor. Conviene preservar la prueba documental con prontitud, emitir requerimiento formal y evaluar la vía de las cortes del DIFC."
                }
            ]
        }
    },
    "spain": {
        "ar": {
            "name": "إسبانيا",
            "title": "الخدمات القانونية في إسبانيا: تحصيل الديون · تنفيذ الأحكام · الميراث العقاري",
            "intro": "تعتبر إسبانيا وجهة استثمارية وتجارية رئيسية في جنوب أوروبا؛ تتطلب النزاعات التجارية والتركات العقارية في مدريد وبرشلونة معرفة دقيقة بالإجراءات القانونية الإسبانية.",
            "items": [
                "تحصيل الديون التجارية وتوجيه الإنذارات القانونية للمدينين في إسبانيا",
                "الاعتراف بالأحكام القضائية الصينية وتنفيذها في إسبانيا",
                "التحري عن الأصول العقارية والشركات الإسبانية",
                "إجراءات الميراث الدولي والتخطيط لضريبة التركات الإسبانية"
            ],
            "points": [
                "اتفاقية المساعدة القضائية بين الصين وإسبانيا لعام 1992 تغطي الاعتراف بالأحكام المدنية والتجارية",
                "التقادم العام للديون والمطالبات العقدية هو 5 سنوات (وفق تعديل 2015)",
                "تختلف ضريبة التركات باختلاف الأقاليم ذات الحكم الذاتي، مع وجود إعفاءات مهمة في بعض المناطق",
                "يلعب كاتب العدل (Notario) دوراً جوهرياً وإلزامياً في المعاملات العقارية",
                "السجل العقاري والتجاري في إسبانيا علني مما يسهل التحري عن الأصول"
            ],
            "faq": [
                {
                    "question": "هل يمكن تنفيذ الأحكام القضائية الصينية في إسبانيا؟",
                    "answer": "نعم، تغطي اتفاقية المساعدة القضائية الموقعة عام 1992 بين البلدين الاعتراف المتبادل بالأحكام المدنية والتجارية وتنفيذها أمام المحاكم الإسبانية."
                },
                {
                    "question": "ما هي المدة الزمنية لسقوط الحق في المطالبة بالديون التجارية في إسبانيا؟",
                    "answer": "مدة التقادم العام للمطالبات التعاقدية والشخصية هي 5 سنوات من تاريخ استحقاق الدين."
                },
                {
                    "question": "هل ضريبة التركات مرتفعة في إسبانيا؟",
                    "answer": "تخضع ضريبة التركات لتقدير كل إقليم ذي حكم ذاتي؛ وتصل النسبة الوطنية القصوى إلى 34% تقريباً، غير أن أقاليم مثل مدريد توفر إعفاءات تكاد تصل إلى 99% للأقارب من الدرجة الأولى."
                }
            ]
        },
        "es": {
            "name": "España",
            "title": "Servicios Legales en España: Cobro de Deudas · Ejecución de Sentencias · Herencias",
            "intro": "Los bienes inmuebles en España y las relaciones comerciales bilaterales generan una demanda constante de asistencia en litigios, reclamaciones de cantidad y sucesiones en Madrid y Barcelona.",
            "items": [
                "Cobro de deudas a clientes españoles y emisión de burofax / requerimientos formales",
                "Reconocimiento y ejecución (exequátur) de sentencias chinas y extranjeras en España",
                "Investigación patrimonial y localización de bienes inmuebles y mercantiles",
                "Herencias transfronterizas y optimización del Impuesto sobre Sucesiones"
            ],
            "points": [
                "Tratado de asistencia judicial China-España de 1992 para sentencias civiles y mercantiles",
                "Plazo de prescripción general de acciones personales de 5 años (art. 1964 CC reformado)",
                "El Impuesto sobre Sucesiones varía según la Comunidad Autónoma, con importantes bonificaciones en regiones como Madrid",
                "Intervención preceptiva del Notario en transmisiones de dominio y actos de herencia",
                "El Registro de la Propiedad y Registro Mercantil son públicos y facilitan la investigación patrimonial"
            ],
            "faq": [
                {
                    "question": "¿Se pueden ejecutar sentencias chinas en España?",
                    "answer": "Sí, conforme al tratado bilateral de auxilio judicial de 1992, se puede instar el correspondiente procedimiento de exequátur ante los juzgados españoles de primera instancia."
                },
                {
                    "question": "¿Cuál es el plazo de prescripción para reclamar una deuda en España?",
                    "answer": "El plazo general de prescripción de las deudas comerciales de carácter personal es de 5 años desde su vencimiento."
                },
                {
                    "question": "¿Es elevado el Impuesto sobre Sucesiones en España?",
                    "answer": "Depende fundamentalmente de la Comunidad Autónoma donde radican los bienes; el tipo estatal alcanza el 34%, pero comunidades como Madrid bonifican hasta el 99% de la cuota para herederos directos."
                }
            ]
        }
    },
    "new-zealand": {
        "ar": {"name": "نيوزيلندا", "title": "الخدمات القانونية في نيوزيلندا: تحصيل الديون · تنفيذ الأحكام · الميراث"},
        "es": {"name": "Nueva Zelanda", "title": "Servicios Legales en Nueva Zelanda: Cobro de Deudas · Ejecución de Sentencias · Herencias"}
    },
    "malaysia": {
        "ar": {"name": "ماليزيا", "title": "الخدمات القانونية في ماليزيا: التجارة والاستثمار · تحصيل الديون · الأصول العائلية"},
        "es": {"name": "Malasia", "title": "Servicios Legales en Malasia: Comercio e Inversión · Cobro de Deudas · Activos Familiares"}
    },
    "france": {
        "ar": {"name": "فرنسا", "title": "الخدمات القانونية في فرنسا: النزاعات التجارية · تحصيل الديون · الميراث العقاري"},
        "es": {"name": "Francia", "title": "Servicios Legales en Francia: Disputas Comerciales · Cobro de Deudas · Herencias Inmobiliarias"}
    },
    "switzerland": {
        "ar": {"name": "سويسرا", "title": "الخدمات القانونية في سويسرا: الحسابات المصرفية · النزاعات التجارية · الصناديق الاستئمانية"},
        "es": {"name": "Suiza", "title": "Servicios Legales en Suiza: Cuentas Bancarias · Disputas Comerciales · Fideicomisos"}
    },
    "south-korea": {
        "ar": {"name": "كوريا الجنوبية", "title": "الخدمات القانونية في كوريا الجنوبية: التجارة الدولية · تحصيل الديون · حماية الملكية الفكرية"},
        "es": {"name": "Corea del Sur", "title": "Servicios Legales en Corea del Sur: Comercio Internacional · Cobro de Deudas · Propiedad Intelectual"}
    },
    "thailand": {
        "ar": {"name": "تايلاند", "title": "الخدمات القانونية في تايلاند: النزاعات التجارية · الأصول العقارية · تأسيس الشركات"},
        "es": {"name": "Tailandia", "title": "Servicios Legales en Tailandia: Disputas Comerciales · Activos Inmobiliarios · Constitución Societaria"}
    },
    "vietnam": {
        "ar": {"name": "فيتنام", "title": "الخدمات القانونية في فيتنام: الاستثمار والتصنيع · النزاعات التعاقدية · تحصيل الديون"},
        "es": {"name": "Vietnam", "title": "Servicios Legales en Vietnam: Inversión y Fabricación · Disputas Contractuales · Cobro de Deudas"}
    },
    "netherlands": {
        "ar": {"name": "هولندا", "title": "الخدمات القانونية في هولندا: الخدمات اللوجستية البحرية · النزاعات التجارية · تحصيل الديون"},
        "es": {"name": "Países Bajos", "title": "Servicios Legales en los Países Bajos: Logística y Puertos · Disputas Comerciales · Cobro de Deudas"}
    },
    "italy": {
        "ar": {"name": "إيطاليا", "title": "الخدمات القانونية في إيطاليا: التجارة والتوريد · تحصيل الديون · الميراث العقاري"},
        "es": {"name": "Italia", "title": "Servicios Legales en Italia: Comercio y Suministro · Cobro de Deudas · Herencias Inmobiliarias"}
    },
    "brazil": {
        "ar": {"name": "البرازيل", "title": "الخدمات القانونية في البرازيل: السلع الأساسية · النزاعات الجمركية والتجارية · تحصيل الديون"},
        "es": {"name": "Brasil", "title": "Servicios Legales en Brasil: Materias Primas · Disputas Aduaneras y Comerciales · Cobro de Deudas"}
    },
    "india": {
        "ar": {"name": "الهند", "title": "الخدمات القانونية في الهند: التجارة عبر الحدود · تحصيل الديون · النزاعات التعاقدية"},
        "es": {"name": "India", "title": "Servicios Legales en la India: Comercio Transfronterizo · Cobro de Deudas · Disputas Contractuales"}
    },
    "ireland": {
        "ar": {"name": "أيرلندا", "title": "الخدمات القانونية في أيرلندا: الشركات متعددة الجنسيات · الملكية الفكرية · النزاعات التجارية"},
        "es": {"name": "Irlanda", "title": "Servicios Legales en Irlanda: Empresas Multinacionales · Propiedad Intelectual · Disputas Comerciales"}
    }
}

def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    
    # 1. Update services
    for svc_slug, svc_trans in SERVICES_I18N.items():
        if svc_slug in data["services"]:
            if "translations" not in data["services"][svc_slug]:
                data["services"][svc_slug]["translations"] = {}
            data["services"][svc_slug]["translations"].update(svc_trans)
    
    # 2. Update countries
    for c_slug, c_trans in COUNTRY_METADATA.items():
        if c_slug in data["countries"]:
            country_obj = data["countries"][c_slug]
            if "translations" not in country_obj:
                country_obj["translations"] = {}
            
            # Apply ar and es
            for lang in ["ar", "es"]:
                meta = c_trans.get(lang, {})
                lang_dict = country_obj["translations"].setdefault(lang, {})
                lang_dict["name"] = meta.get("name", country_obj.get("name_en", ""))
                lang_dict["title"] = meta.get("title", country_obj.get("en_title", ""))
                
                if "intro" in meta:
                    lang_dict["intro"] = meta["intro"]
                else:
                    lang_dict["intro"] = country_obj.get("en_intro", "")
                
                if "items" in meta:
                    lang_dict["items"] = meta["items"]
                else:
                    lang_dict["items"] = country_obj.get("items_en", [])
                    
                if "points" in meta:
                    lang_dict["points"] = meta["points"]
                else:
                    lang_dict["points"] = country_obj.get("points_en", [])
                    
                if "faq" in meta:
                    lang_dict["faq"] = meta["faq"]
                else:
                    # fallback to English parsed FAQs if not specifically defined
                    en_faqs = []
                    for item in country_obj.get("faq_en", []):
                        q, sep, a = item.partition("|")
                        en_faqs.append({"question": q.strip(), "answer": a.strip()})
                    lang_dict["faq"] = en_faqs

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Successfully enriched {DATA_PATH}")

if __name__ == "__main__":
    main()
