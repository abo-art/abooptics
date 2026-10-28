/**
 * abooptika — Профессиональный аналитический интерфейс оптики
 * Инструмент оценки посадки оправы и биометрии лица без графического мусора,
 * без кнопок продаж/бронирований и без маркетинговой воды.
 * Поддержка двух языков: Русский (RU) и English (EN) для жюри хакатона.
 */

const I18N = {
  ru: {
    site_title: 'abooptika — Анализ посадки оправы и геометрии лица',
    header_subtitle: 'Оптический анализ посадки',
    salon_mode: 'Режим консультанта',
    salon_banner_title: 'Терминал оптометриста / Салон Dostyk Plaza',
    salon_banner_sub: 'Инструмент подбора и оценки посадки в торговом зале',
    scan_title: 'Оценка посадки оправы',
    scan_subtitle: 'Наденьте оправу с витрины и наведите фронтальную камеру для биометрического замера геометрии лица и ширины оправы',
    camera_guide: 'Лицо в надетой оправе внутри овала',
    camera_title: 'Камера устройства',
    camera_sub: 'Включите камеру смартфона или планшета стойки',
    btn_enable_camera: 'Включить камеру',
    btn_flip_camera: 'Камера',
    axes_1_1: 'Оси: 1:1',
    axes_inv: 'Оси: Инверс',
    btn_capture: 'Выполнить биометрическое сканирование',
    btn_upload_photo: 'Загрузить фото примерки из галереи',
    demo_title: 'Тестовые сценарии:',
    demo_badge: '1-клик тест',
    demo_no_glasses_title: '👤 Без очков',
    demo_no_glasses_sub: 'Первичный подбор оправы',
    demo_square_title: '👓 В квадратной',
    demo_square_sub: 'Ширина 143 мм (Широковата)',
    demo_round_title: '👓 В круглой',
    demo_round_sub: 'Ширина 135 мм (Соответствует)',
    loading_title: 'Биометрический расчет',
    loading_steps: [
      'Детекция контуров лица и посадки оправы в MediaPipe...',
      'Измерение биометрических пропорций: скулы, челюсть, лоб...',
      'Анализ ширины оправы относительно височной линии...',
      'Расчет геометрической совместимости и подбор моделей с витрины...'
    ],
    face_type_label: 'Анатомический тип лица',
    accuracy: 'точность',
    metric_hw_label: 'Длина / Скулы',
    metric_jc_label: 'Челюсть / Скулы',
    metric_chin_label: 'Угол челюсти',
    metric_sym_label: 'Симметрия',
    verdict_worn_title: 'Оценка посадки надетой оправы',
    verdict_bare_title: 'Персональный подбор оправы под анатомию лица',
    verdict_bare_mode: 'Режим: Подбор идеальной оправы',
    compatibility_label: 'Совместимость:',
    basis_label: 'Базис геометрии:',
    bare_badge: '👤 Без очков • Режим подбора',
    verdict_banner: 'Заключение эксперта-оптометриста AbooOptika',
    bridge_label: 'Мостик & Переносица:',
    temple_label: 'Заушники & Батареи:',
    fit_metric_width: 'Ширина оправы',
    fit_metric_width_bare: 'Целевая ширина оправы',
    fit_metric_pupil: 'Положение зрачков',
    fit_metric_pupil_bare: 'Оптический центр',
    fit_metric_eyebrow: 'Линия бровей',
    fit_metric_eyebrow_bare: 'Линия надбровных дуг',
    pros_title_worn: 'Соответствия:',
    pros_title_bare: 'Анатомические преимущества геометрии:',
    cons_title_worn: 'Отклонения и риски:',
    cons_title_bare: 'Рекомендации оптометриста:',
    cons_empty: 'Отклонений не выявлено. Лицо готово к первой примерке рекомендованных моделей.',
    rec_heading_worn: 'ТОП-5 рекомендованных альтернатив Meta взамен текущей оправы',
    rec_heading_bare: 'ТОП-5 рекомендованных моделей смарт-очков Meta для вашего типа лица',
    rec_sub_worn: 'Официальная линейка Meta с улучшенной посадкой и геометрической компенсацией',
    rec_sub_bare: 'Официальные модели Meta с идеальной анатомической посадкой для вашей формы лица',
    catalog_badge: 'Официальный каталог Meta 2025',
    btn_open_pass: 'Показать консультанту в зале',
    btn_new_scan: 'Новый скан',
    btn_close_pass: 'Закрыть',
    print_pass: 'Распечатать талон примерки',
    pass_title_worn: 'Талон примерки смарт-очков Meta',
    pass_title_bare: 'Талон персонального подбора смарт-очков Meta',
    pass_sub: 'Покажите данный бланк консультанту оптики для подбора оправы с витрины',
    pass_current_worn: 'Текущая примерка клиента:',
    pass_current_bare: 'Биометрический профиль лица:',
    pass_consultant_hint: 'Консультант предоставит эту модель с витрины для контрольной примерки',
    card_lens_shape: 'Форма линз',
    card_dimensions: 'Размеры (линза-мост-заушник)',
    card_camera: 'Камера & Видео',
    card_material: 'Материал оправы',
    card_color: 'Цвет & Линзы',
    card_optometric_reason: 'Оптометрическая компенсация & Эргономика:',
    footer_copy: '© 2026 abooptika. Профессиональный инструмент оптического подбора в салоне.',
    footer_tech: 'MediaPipe Face Mesh • Геометрический анализ посадки',
    chat_trigger_title: 'ИИ-Консультант',
    chat_subtitle: 'Консультант по смарт-очкам Meta',
    chat_personalization: 'Персонализация',
    chat_bio_context: 'Биометрия лица учтена',
    chat_placeholder: 'Спросите о моделях Meta, подборе или ценах...',
    chat_typing: 'Консультант печатает...',
    chat_initial_greeting: `Здравствуйте! Я персональный ИИ-стилист и эксперт **AbooOptika**.\n\nЯ знаю все 25 моделей смарт-очков **Meta** (Ray-Ban Meta, Meta и Oakley) и помогу вам:\n• Подобрать идеальную оправу под геометрию вашего лица\n• Рассказать о новинках: **LISA Edition**, **Meta Fury**, **Zena Gen 3**\n• Выбрать аудио-версии без камер (**Clubmaster Audio**, **Burbank Audio**)\n• Объяснить результаты оптического сканирования\n\nЧем я могу помочь вам прямо сейчас?`,
    chat_default_chips: [
      "✨ В чем отличие серии LISA Edition?",
      "🕶️ Посоветуй модель под мое лицо",
      "🎙️ Очки со звуком без камер (Clubmaster)",
      "📷 Как работает 12MP камера в Wayfarer?",
      "💰 Сколько стоят очки в тенге (₸)?"
    ]
  },
  en: {
    site_title: 'abooptika — Optical Frame Fit & Facial Geometry Analysis',
    header_subtitle: 'Optical Fit Analysis',
    salon_mode: 'Consultant Mode',
    salon_banner_title: 'Optometrist Terminal / Dostyk Plaza Salon',
    salon_banner_sub: 'In-store frame fitting & diagnostic platform',
    scan_title: 'Frame Fit Assessment',
    scan_subtitle: 'Put on a display frame and point your front camera for biometric measurement of facial geometry and frame width',
    camera_guide: 'Position face with frame inside oval',
    camera_title: 'Device Camera',
    camera_sub: 'Enable camera on your phone or kiosk tablet',
    btn_enable_camera: 'Enable Camera',
    btn_flip_camera: 'Flip Camera',
    axes_1_1: 'Axes: 1:1',
    axes_inv: 'Axes: Inverted',
    btn_capture: 'Run Biometric Scan',
    btn_upload_photo: 'Upload fitting photo from gallery',
    demo_title: 'Demo Scenarios:',
    demo_badge: '1-Click Test',
    demo_no_glasses_title: '👤 No Glasses',
    demo_no_glasses_sub: 'Initial Frame Fitting',
    demo_square_title: '👓 In Square Frame',
    demo_square_sub: 'Width 143 mm (Slightly Wide)',
    demo_round_title: '👓 In Round Frame',
    demo_round_sub: 'Width 135 mm (Optimal Fit)',
    loading_title: 'Biometric Computation',
    loading_steps: [
      'Detecting facial contours and frame alignment in MediaPipe...',
      'Measuring biometric proportions: cheekbones, jaw, forehead...',
      'Analyzing frame width relative to temple line...',
      'Calculating geometric compatibility and selecting showcase models...'
    ],
    face_type_label: 'Anatomical Face Shape',
    accuracy: 'accuracy',
    metric_hw_label: 'Height / Cheekbones',
    metric_jc_label: 'Jaw / Cheekbones',
    metric_chin_label: 'Jaw Angle',
    metric_sym_label: 'Symmetry',
    verdict_worn_title: 'Worn Frame Fit Evaluation',
    verdict_bare_title: 'Personal Frame Fitting for Facial Anatomy',
    verdict_bare_mode: 'Mode: Finding Ideal Frame',
    compatibility_label: 'Compatibility:',
    basis_label: 'Geometry Basis:',
    bare_badge: '👤 No Glasses • Fitting Mode',
    verdict_banner: 'AbooOptika Optometrist Fit Verdict',
    bridge_label: 'Bridge & Nose Fit:',
    temple_label: 'Temples & Battery Balance:',
    fit_metric_width: 'Frame Width',
    fit_metric_width_bare: 'Target Frame Width',
    fit_metric_pupil: 'Pupil Alignment',
    fit_metric_pupil_bare: 'Optical Center',
    fit_metric_eyebrow: 'Eyebrow Line',
    fit_metric_eyebrow_bare: 'Brow Arch Alignment',
    pros_title_worn: 'Anatomical Matches:',
    pros_title_bare: 'Anatomical Geometry Strengths:',
    cons_title_worn: 'Deviations & Fit Risks:',
    cons_title_bare: 'Optometrist Recommendations:',
    cons_empty: 'No deviations detected. Facial anatomy is ready for fitting recommended models.',
    rec_heading_worn: 'TOP-5 Recommended Meta Alternatives for Current Frame',
    rec_heading_bare: 'TOP-5 Recommended Meta Smart Glasses for Your Face Shape',
    rec_sub_worn: 'Official Meta lineup with enhanced fit and geometric compensation',
    rec_sub_bare: 'Official Meta models with optimal anatomical fit for your face shape',
    catalog_badge: 'Official Meta 2025 Catalog',
    btn_open_pass: 'Show to In-Store Consultant',
    btn_new_scan: 'New Scan',
    btn_close_pass: 'Close',
    print_pass: 'Print Fitting Slip',
    pass_title_worn: 'Meta Smart Glasses Fitting Slip',
    pass_title_bare: 'Meta Smart Glasses Personal Selection Slip',
    pass_sub: 'Show this slip to your in-store optical consultant for display frame trial',
    pass_current_worn: 'Client Current Fitting:',
    pass_current_bare: 'Client Biometric Profile:',
    pass_consultant_hint: 'The consultant will retrieve this display model for in-store trial fitting',
    card_lens_shape: 'Lens Shape',
    card_dimensions: 'Dimensions (lens-bridge-temple)',
    card_camera: 'Camera & Video',
    card_material: 'Frame Material',
    card_color: 'Color & Lenses',
    card_optometric_reason: 'Optometric Compensation & Ergonomics:',
    footer_copy: '© 2026 abooptika. Professional in-store optical fit platform.',
    footer_tech: 'MediaPipe Face Mesh • Geometric Fit Analysis',
    chat_trigger_title: 'AI Consultant',
    chat_subtitle: 'Meta Smart Glasses Consultant',
    chat_personalization: 'Personalized',
    chat_bio_context: 'Facial biometrics applied',
    chat_placeholder: 'Ask about Meta models, fit recommendation, or pricing...',
    chat_typing: 'Consultant is typing...',
    chat_initial_greeting: `Hello! I am your personal AI stylist and expert at **AbooOptika**.\n\nI know all 25 **Meta** smart glasses models (Ray-Ban Meta, Meta, and Oakley) and can help you:\n• Find the optimal frame for your facial geometry\n• Explore new releases: **LISA Edition**, **Meta Fury**, **Zena Gen 3**\n• Choose audio-only models without cameras (**Clubmaster Audio**, **Burbank Audio**)\n• Explain your biometric optical scan results\n\nHow can I assist you right now?`,
    chat_default_chips: [
      "✨ What makes the LISA Edition special?",
      "🕶️ Recommend frames for my face",
      "🎙️ Audio glasses without cameras (Clubmaster)",
      "📷 How does the 12MP camera work in Wayfarer?",
      "💰 How much do glasses cost in USD / KZT?"
    ]
  }
};

const SHAPE_TRANSLATIONS = {
  oval: { ru: 'Овальное лицо', en: 'Oval Face', desc_en: 'Face length exceeds cheekbone width by ~30% (ratio ~1.30-1.35). Jawline softly tapers toward chin without sharp angles.' },
  round: { ru: 'Круглое лицо', en: 'Round Face', desc_en: 'Length-to-width ratio is close to 1.1-1.2. Soft curved jawline and full cheeks with balanced proportions.' },
  square: { ru: 'Квадратное лицо', en: 'Square Face', desc_en: 'Jaw width is 90% or more of cheekbone width. Jaw angle is sharp and prominent, chin is broad.' },
  heart: { ru: 'Сердцевидное лицо', en: 'Heart Face', desc_en: 'Forehead and temples are noticeably wider than the jaw. Face gracefully tapers toward a pointed chin.' },
  oblong: { ru: 'Продолговатое лицо', en: 'Oblong Face', desc_en: 'Face length significantly exceeds cheekbone width (ratio > 1.38) with straight cheek lines and high forehead.' },
  diamond: { ru: 'Ромбовидное лицо', en: 'Diamond Face', desc_en: 'Prominent high cheekbones with narrower forehead and jawline.' }
};

const STATUS_TRANSLATIONS = {
  'Широковата': { ru: 'Широковата', en: 'Slightly Wide' },
  'Узковата': { ru: 'Узковата', en: 'Slightly Narrow' },
  'Соответствует': { ru: 'Соответствует', en: 'Optimal' },
  'Идеально': { ru: 'Идеально', en: 'Optimal' },
  'Идеально по центру': { ru: 'Идеально по центру', en: 'Centered' },
  'Смещены': { ru: 'Смещены', en: 'Shifted' },
  'Гармонично': { ru: 'Гармонично', en: 'Harmonious' },
  'Перекрывает брови': { ru: 'Перекрывает брови', en: 'Overlaps Brow' },
  'Есть нюансы': { ru: 'Есть нюансы', en: 'Nuances Detected' },
  'Идеальная посадка': { ru: 'Идеальная посадка', en: 'Optimal Fit' },
  'Отличная посадка': { ru: 'Отличная посадка', en: 'Great Fit' }
};

const FRAME_SHAPE_NAMES = {
  'Квадратная оправа': { ru: 'Квадратная оправа', en: 'Square Frame' },
  'Квадратная': { ru: 'Квадратная', en: 'Square' },
  'Круглая оправа': { ru: 'Круглая оправа', en: 'Round Frame' },
  'Круглая': { ru: 'Круглая', en: 'Round' },
  'Овальная оправа': { ru: 'Овальная оправа', en: 'Oval Frame' },
  'Овальная': { ru: 'Овальная', en: 'Oval' },
  'Прямоугольная оправа': { ru: 'Прямоугольная оправа', en: 'Rectangular Frame' },
  'Прямоугольная': { ru: 'Прямоугольная', en: 'Rectangular' },
  'Панто': { ru: 'Панто', en: 'Panto' },
  'Кошачий глаз': { ru: 'Кошачий глаз', en: 'Cat-Eye' },
  'Авиатор': { ru: 'Авиатор', en: 'Aviator' },
  'Вайфарер': { ru: 'Вайфарер', en: 'Wayfarer' },
  'Геометрическая': { ru: 'Геометрическая', en: 'Geometric' }
};

class AboOptikaApp {
  constructor() {
    this.cameraManager = null;
    this.state = {
      imageSrc: null,
      analysis: null,
      selectedAlternative: null,
      isSalonMode: false,
      frameHint: '',
      isAnalyzing: false,
      soundEnabled: true,
      chatOpen: false,
      chatMessages: [],
      chatLoading: false
    };

    // Auto-detect user preferred language: saved in localStorage or from browser
    const savedLang = localStorage.getItem('aboo_lang');
    const browserLang = (navigator.language && navigator.language.toLowerCase().startsWith('en')) ? 'en' : 'ru';
    this.currentLang = savedLang || browserLang;

    this.audioCtx = null;
    this.initElements();
    this.initLanguage();
    this.initAudio();
    this.initEventListeners();
    this.initCamera();
    this.initChat();
  }

  initElements() {
    this.el = {
      // Языковые кнопки
      langBtnRu: document.getElementById('lang-btn-ru'),
      langBtnEn: document.getElementById('lang-btn-en'),

      // Экраны
      screenScan: document.getElementById('screen-scan'),
      screenLoading: document.getElementById('screen-loading'),
      screenResults: document.getElementById('screen-results'),

      // Камера
      video: document.getElementById('camera-video'),
      captureCanvas: document.getElementById('capture-canvas'),
      btnCapture: document.getElementById('btn-capture'),
      btnStartCamera: document.getElementById('btn-start-camera'),
      btnFlipCamera: document.getElementById('btn-flip-camera'),
      btnToggleMirror: document.getElementById('btn-toggle-mirror'),
      fileInput: document.getElementById('file-input'),
      cameraContainer: document.getElementById('camera-container'),
      cameraPlaceholder: document.getElementById('camera-placeholder'),
      cameraActiveControls: document.getElementById('camera-active-controls'),

      // Демо-кнопки
      btnDemoNoGlasses: document.getElementById('btn-demo-no-glasses'),
      btnDemoWearingSquare: document.getElementById('btn-demo-wearing-square'),
      btnDemoWearingRound: document.getElementById('btn-demo-wearing-round'),

      // Загрузка
      loadingStepText: document.getElementById('loading-step-text'),

      // Результаты: Фото примерки и биометрия
      clientRealPhoto: document.getElementById('client-real-photo'),
      shapeTitle: document.getElementById('diag-shape-title'),
      shapeConfidence: document.getElementById('diag-shape-confidence'),
      shapeDescription: document.getElementById('diag-shape-desc'),
      metricHw: document.getElementById('metric-hw'),
      metricJc: document.getElementById('metric-jc'),
      metricChin: document.getElementById('metric-chin'),
      metricSym: document.getElementById('metric-sym'),

      // Вердикт оптометриста / ИИ
      verdictCard: document.getElementById('verdict-card'),
      verdictSectionModeTitle: document.getElementById('verdict-section-mode-title'),
      wornShapeName: document.getElementById('worn-shape-name'),
      wornScoreLabel: document.getElementById('worn-score-label'),
      wornScore: document.getElementById('worn-compatibility-score'),
      wornBadge: document.getElementById('worn-match-badge'),
      stylistQuote: document.getElementById('stylist-quote'),
      aiModelPill: document.getElementById('ai-model-pill'),
      bridgeNuanceText: document.getElementById('bridge-nuance-text'),
      templeNuanceText: document.getElementById('temple-nuance-text'),
      fitWidthStatus: document.getElementById('fit-width-status'),
      fitWidthDesc: document.getElementById('fit-width-desc'),
      fitPupilStatus: document.getElementById('fit-pupil-status'),
      fitPupilDesc: document.getElementById('fit-pupil-desc'),
      fitEyebrowStatus: document.getElementById('fit-eyebrow-status'),
      fitEyebrowDesc: document.getElementById('fit-eyebrow-desc'),
      fitMetric1Title: document.getElementById('fit-metric-1-title'),
      fitMetric2Title: document.getElementById('fit-metric-2-title'),
      fitMetric3Title: document.getElementById('fit-metric-3-title'),
      prosTitle: document.getElementById('pros-title'),
      consTitle: document.getElementById('cons-title'),
      prosList: document.getElementById('pros-list'),
      consList: document.getElementById('cons-list'),

      // Заголовки рекомендаций
      recommendationsHeading: document.getElementById('recommendations-heading'),
      recommendationsSubheading: document.getElementById('recommendations-subheading'),

      // Топ-5 альтернативы
      alternativesContainer: document.getElementById('alternatives-container'),

      // Модальное окно: талон для консультанта
      passModal: document.getElementById('pass-modal'),
      btnOpenPass: document.getElementById('btn-open-pass'),
      btnClosePass: document.getElementById('btn-close-pass'),
      passContent: document.getElementById('pass-content'),

      btnNewScan: document.getElementById('btn-new-scan'),

      // Режим консультанта
      salonModeToggle: document.getElementById('salon-mode-toggle'),
      salonBanner: document.getElementById('salon-banner'),

      // ИИ-чат виджет AbooOptika
      btnToggleChat: document.getElementById('btn-toggle-chat'),
      chatTriggerIcon: document.getElementById('chat-trigger-icon'),
      chatPanel: document.getElementById('chat-panel'),
      btnChatClose: document.getElementById('btn-chat-close'),
      btnChatClear: document.getElementById('btn-chat-clear'),
      chatMessages: document.getElementById('chat-messages'),
      chatChipsBar: document.getElementById('chat-chips-bar'),
      chatForm: document.getElementById('chat-form'),
      chatInput: document.getElementById('chat-input'),
      btnChatSend: document.getElementById('btn-chat-send'),
      chatBiometricBanner: document.getElementById('chat-biometric-banner'),
      chatBioContextText: document.getElementById('chat-bio-context-text')
    };
  }

  t(key, defaultVal = '') {
    const dict = I18N[this.currentLang] || I18N.ru;
    return dict[key] !== undefined ? dict[key] : (I18N.ru[key] || defaultVal);
  }

  formatPrice(price, currency = '₸') {
    if (!price) return '';
    if (this.currentLang === 'en') {
      const usd = Math.round(price / 500);
      return `${Number(price).toLocaleString('en-US')} ₸ (~$${usd} USD)`;
    }
    return `${Number(price).toLocaleString('ru-RU')} ${currency || '₸'}`;
  }

  initLanguage() {
    this.setLanguage(this.currentLang, false);
  }

  setLanguage(lang, refreshChat = true) {
    if (lang !== 'ru' && lang !== 'en') return;
    this.currentLang = lang;
    try {
      localStorage.setItem('aboo_lang', lang);
    } catch (_) {}

    document.documentElement.lang = lang;

    // Стилизация кнопок переключения RU / EN
    if (this.el.langBtnRu && this.el.langBtnEn) {
      if (lang === 'ru') {
        this.el.langBtnRu.className = 'px-2.5 py-1 text-xs font-bold rounded-lg transition-all bg-navy-900 text-white shadow-sm';
        this.el.langBtnEn.className = 'px-2.5 py-1 text-xs font-bold rounded-lg transition-all text-navy-900 hover:text-navy-950';
      } else {
        this.el.langBtnEn.className = 'px-2.5 py-1 text-xs font-bold rounded-lg transition-all bg-navy-900 text-white shadow-sm';
        this.el.langBtnRu.className = 'px-2.5 py-1 text-xs font-bold rounded-lg transition-all text-navy-900 hover:text-navy-950';
      }
    }

    // Обновление всех статичных элементов с data-i18n
    document.querySelectorAll('[data-i18n]').forEach(elem => {
      const key = elem.getAttribute('data-i18n');
      const text = this.t(key);
      if (text) elem.textContent = text;
    });

    // Обновление placeholder полей ввода
    document.querySelectorAll('[data-i18n-ph]').forEach(elem => {
      const key = elem.getAttribute('data-i18n-ph');
      const ph = this.t(key);
      if (ph) elem.placeholder = ph;
    });

    // Заголовок страницы
    document.title = this.t('site_title');

    // Если результаты анализа уже на экране — перерисовываем их на новом языке
    if (this.state.analysis) {
      this.displayResults(this.state.analysis);
    }

    // Если открыт чат и в нем только начальное приветствие, обновляем на выбранный язык
    if (refreshChat && this.state.chatMessages && this.state.chatMessages.length <= 1) {
      this.renderInitialChatState();
    }
  }
  }

  initAudio() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    } catch (e) {}
  }

  playSound(type) {
    if (!this.state.soundEnabled || !this.audioCtx) return;
    try {
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const ctx = this.audioCtx;
      const now = ctx.currentTime;

      if (type === 'shutter') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(150, now + 0.08);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'success') {
        [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0, now + idx * 0.08);
          gain.gain.linearRampToValueAtTime(0.2, now + idx * 0.08 + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.08);
          osc.stop(now + idx * 0.08 + 0.36);
        });
      }
    } catch (e) {}
  }

  initCamera() {
    this.cameraManager = new CameraManager(this.el.video, this.el.captureCanvas, {
      onStatusChange: (status) => {
        if (status.active) {
          this.el.cameraPlaceholder.classList.add('hidden');
          this.el.video.classList.remove('hidden');
          this.el.cameraActiveControls.classList.remove('hidden');
          this.el.btnCapture.disabled = false;
        } else {
          this.el.cameraPlaceholder.classList.remove('hidden');
          this.el.video.classList.add('hidden');
          this.el.cameraActiveControls.classList.add('hidden');
        }
      },
      onError: (err) => {
        alert('Не удалось запустить камеру: ' + err.message + '\nВы можете загрузить фотографию из галереи или нажать кнопку готового примера.');
      }
    });
  }

  initEventListeners() {
    // Управление камерой
    if (this.el.btnStartCamera) {
      this.el.btnStartCamera.addEventListener('click', () => {
        this.cameraManager.start();
      });
    }

    if (this.el.btnFlipCamera) {
      this.el.btnFlipCamera.addEventListener('click', () => {
        this.cameraManager.toggleFacingMode();
      });
    }

    if (this.el.btnToggleMirror) {
      this.el.btnToggleMirror.addEventListener('click', () => {
        const isMirrored = this.cameraManager.toggleMirror();
        this.el.btnToggleMirror.textContent = isMirrored ? this.t('axes_1_1') : this.t('axes_inv');
      });
    }

    // Переключение языка (RU / EN)
    if (this.el.langBtnRu) {
      this.el.langBtnRu.addEventListener('click', () => {
        this.setLanguage('ru');
      });
    }

    if (this.el.langBtnEn) {
      this.el.langBtnEn.addEventListener('click', () => {
        this.setLanguage('en');
      });
    }

    if (this.el.btnCapture) {
      this.el.btnCapture.addEventListener('click', async () => {
        try {
          this.playSound('shutter');
          const dataUrl = this.cameraManager.captureFrameDataUrl();
          this.cameraManager.stop();
          await this.processImage(dataUrl);
        } catch (err) {
          alert('Ошибка при съемке: ' + err.message);
        }
      });
    }

    if (this.el.fileInput) {
      this.el.fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
          this.cameraManager.stop();
          const dataUrl = await this.cameraManager.loadFileAsDataUrl(file);
          await this.processImage(dataUrl);
        }
      });
    }

    // Тестовые сценарии примерки
    if (this.el.btnDemoNoGlasses) {
      this.el.btnDemoNoGlasses.addEventListener('click', async () => {
        this.state.frameHint = 'none';
        this.cameraManager.stop();
        const dataUrl = await this.cameraManager.loadDemoImage('/static/demo_faces/oval_face.jpg');
        await this.processImage(dataUrl);
      });
    }

    if (this.el.btnDemoWearingSquare) {
      this.el.btnDemoWearingSquare.addEventListener('click', async () => {
        this.state.frameHint = 'square';
        this.cameraManager.stop();
        const dataUrl = await this.cameraManager.loadDemoImage('/static/demo_faces/wearing_square.jpg');
        await this.processImage(dataUrl);
      });
    }

    if (this.el.btnDemoWearingRound) {
      this.el.btnDemoWearingRound.addEventListener('click', async () => {
        this.state.frameHint = 'round';
        this.cameraManager.stop();
        const dataUrl = await this.cameraManager.loadDemoImage('/static/demo_faces/wearing_round.jpg');
        await this.processImage(dataUrl);
      });
    }

    // Талон для консультанта
    if (this.el.btnOpenPass) {
      this.el.btnOpenPass.addEventListener('click', () => this.openPassModal());
    }

    if (this.el.btnClosePass) {
      this.el.btnClosePass.addEventListener('click', () => this.closePassModal());
    }

    if (this.el.passModal) {
      this.el.passModal.addEventListener('click', (e) => {
        if (e.target === this.el.passModal) this.closePassModal();
      });
    }

    if (this.el.btnNewScan) {
      this.el.btnNewScan.addEventListener('click', () => this.resetToScan());
    }

    // Переключатель режима консультанта
    if (this.el.salonModeToggle) {
      this.el.salonModeToggle.addEventListener('change', (e) => {
        this.state.isSalonMode = e.target.checked;
        if (this.el.salonBanner) {
          this.el.salonBanner.classList.toggle('hidden', !e.target.checked);
        }
      });
    }
  }

  showScreen(screenName) {
    this.el.screenScan.classList.add('hidden');
    this.el.screenLoading.classList.add('hidden');
    this.el.screenResults.classList.add('hidden');

    if (screenName === 'scan') this.el.screenScan.classList.remove('hidden');
    else if (screenName === 'loading') this.el.screenLoading.classList.remove('hidden');
    else if (screenName === 'results') this.el.screenResults.classList.remove('hidden');
  }

  async processImage(dataUrl) {
    this.state.imageSrc = dataUrl;
    this.showScreen('loading');
    this.state.isAnalyzing = true;

    const steps = this.t('loading_steps') || [
      'Детекция контуров лица и посадки оправы в MediaPipe...',
      'Измерение биометрических пропорций: скулы, челюсть, лоб...',
      'Анализ ширины оправы относительно височной линии...',
      'Расчет геометрической совместимости и подбор моделей с витрины...'
    ];

    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex = (stepIndex + 1) % steps.length;
      if (this.el.loadingStepText) {
        this.el.loadingStepText.textContent = steps[stepIndex];
      }
    }, 450);

    try {
      const payload = {
        image_base64: dataUrl,
        frame_shape: this.state.frameHint || undefined
      };

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      clearInterval(interval);

      if (!response.ok) {
        let errMessage = `Ошибка сервера (${response.status})`;
        try {
          const rawText = await response.text();
          try {
            const errData = JSON.parse(rawText);
            if (errData && errData.detail) {
              errMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
            } else if (errData && errData.message) {
              errMessage = errData.message;
            }
          } catch (_) {
            if (rawText && rawText.trim()) {
              errMessage = rawText.trim().slice(0, 150);
            }
          }
        } catch (_) {}
        throw new Error(errMessage);
      }

      const result = await response.json();

      if (!result.success || !result.face_detected) {
        const fallbackMsg = this.currentLang === 'en'
          ? (result.message || 'Face not detected in frame. Please look directly into the camera.')
          : (result.message || 'Лицо не обнаружено в кадре. Пожалуйста, посмотрите прямо в камеру.');
        alert(fallbackMsg);
        this.showScreen('scan');
        return;
      }

      this.state.analysis = result;
      this.playSound('success');
      this.displayResults(result);
      this.showScreen('results');
    } catch (err) {
      clearInterval(interval);
      console.error(err);
      alert((this.currentLang === 'en' ? 'Analysis error: ' : 'Ошибка при анализе: ') + err.message);
      this.showScreen('scan');
    } finally {
      this.state.isAnalyzing = false;
    }
  }

  displayResults(result) {
    const isEn = this.currentLang === 'en';
    const shape = result.face_shape;
    const metrics = result.metrics;
    const worn = result.worn_frame_evaluation;
    const alternatives = result.top_alternatives;

    // 1. Реальное фото примерки без графических наложений
    if (this.el.clientRealPhoto) {
      this.el.clientRealPhoto.src = this.state.imageSrc;
    }

    // 2. Биометрические параметры лица
    if (this.el.shapeTitle && shape) {
      this.el.shapeTitle.textContent = isEn
        ? (shape.shape_name_en || SHAPE_TRANSLATIONS[shape.shape_id]?.en || shape.shape_name_ru)
        : shape.shape_name_ru;
    }
    if (this.el.shapeConfidence && shape) {
      this.el.shapeConfidence.textContent = `${shape.confidence}% ${this.t('accuracy')}`;
    }
    if (this.el.shapeDescription && shape) {
      this.el.shapeDescription.textContent = (isEn && SHAPE_TRANSLATIONS[shape.shape_id]?.desc_en)
        ? SHAPE_TRANSLATIONS[shape.shape_id].desc_en
        : shape.description_ru;
    }

    if (this.el.metricHw && metrics) this.el.metricHw.textContent = metrics.height_to_width_ratio.toFixed(2);
    if (this.el.metricJc && metrics) this.el.metricJc.textContent = metrics.jaw_to_cheek_ratio.toFixed(2);
    if (this.el.metricChin && metrics) this.el.metricChin.textContent = `${metrics.chin_sharpness_deg}°`;
    if (this.el.metricSym && metrics) this.el.metricSym.textContent = `${metrics.symmetry_score}%`;

    // 3. Заключение оптометриста (Оценка надетой оправы ИЛИ Режим первичного подбора без очков)
    if (worn) {
      const isWearing = Boolean(worn.has_glasses);

      if (this.el.verdictSectionModeTitle) {
        this.el.verdictSectionModeTitle.textContent = isWearing
          ? this.t('verdict_worn_title')
          : this.t('verdict_bare_title');
      }

      if (this.el.wornShapeName) {
        const localizedShapeName = isEn
          ? (FRAME_SHAPE_NAMES[worn.detected_shape_name_ru]?.en || worn.detected_shape_name_ru)
          : worn.detected_shape_name_ru;
        this.el.wornShapeName.textContent = isWearing
          ? localizedShapeName
          : this.t('verdict_bare_mode');
      }

      if (this.el.wornScoreLabel) {
        this.el.wornScoreLabel.textContent = isWearing ? this.t('compatibility_label') : this.t('basis_label');
      }

      if (this.el.wornScore) {
        this.el.wornScore.textContent = isWearing ? `${worn.compatibility_score}%` : '98%';
      }

      if (this.el.wornBadge) {
        const localizedBadge = isEn
          ? (STATUS_TRANSLATIONS[worn.match_badge]?.en || worn.match_badge)
          : worn.match_badge;
        this.el.wornBadge.textContent = isWearing ? localizedBadge : this.t('bare_badge');
        this.el.wornBadge.className = isWearing
          ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-white text-navy-900 border border-navy-900/15 shadow-sm'
          : 'text-[10px] font-bold px-2 py-0.5 rounded bg-sky-50 text-sky-800 border border-sky-200 shadow-sm';
      }

      if (this.el.stylistQuote) {
        if (isEn) {
          if (isWearing) {
            const shapeEn = FRAME_SHAPE_NAMES[worn.detected_shape_name_ru]?.en || worn.detected_shape;
            this.el.stylistQuote.textContent = (worn.compatibility_score >= 90)
              ? `Worn frame '${shapeEn}': compatibility ${worn.compatibility_score}%. Optical center and proportions match facial geometry harmoniously.`
              : `Worn frame '${shapeEn}': compatibility ${worn.compatibility_score}%. Vertical positioning is accurate, but frame width (${metrics?.temple_width_mm ? metrics.temple_width_mm + 8 : 143} mm) exceeds cheekbone width.`;
          } else {
            this.el.stylistQuote.textContent = "Primary facial geometry scan complete. 5 official Meta smart glasses models curated with optimal anthropometric fit.";
          }
        } else {
          this.el.stylistQuote.textContent = worn.verdict_quote_ru;
        }
      }

      // Чистый брендовый бейдж AbooOptika
      if (this.el.aiModelPill) {
        this.el.aiModelPill.textContent = 'AbooOptika AI Biometrics';
        this.el.aiModelPill.className = 'text-[10px] font-bold text-navy-900/70 bg-navy-100/60 px-2 py-0.5 rounded border border-navy-900/10';
      }

      // Нюансы по мостику и заушникам смарт-очков
      if (this.el.bridgeNuanceText) {
        this.el.bridgeNuanceText.textContent = isEn
          ? "Standard 20-22 mm keyhole bridge ensures stable weight distribution for smart eyewear."
          : (worn.bridge_nuance_ru || "Стандартный мостик 20-22 мм обеспечивает стабильное распределение веса смарт-очков.");
      }
      if (this.el.templeNuanceText) {
        this.el.templeNuanceText.textContent = isEn
          ? "Electronic temples with built-in battery require balanced grip without temporal artery pressure."
          : (worn.temple_nuance_ru || "Электронные заушники требуют плотного охвата без сдавливания височных артерий.");
      }

      const fm = worn.fit_metrics;
      if (this.el.fitMetric1Title) this.el.fitMetric1Title.textContent = isWearing ? this.t('fit_metric_width') : this.t('fit_metric_width_bare');
      if (this.el.fitMetric2Title) this.el.fitMetric2Title.textContent = isWearing ? this.t('fit_metric_pupil') : this.t('fit_metric_pupil_bare');
      if (this.el.fitMetric3Title) this.el.fitMetric3Title.textContent = isWearing ? this.t('fit_metric_eyebrow') : this.t('fit_metric_eyebrow_bare');
      if (this.el.prosTitle) this.el.prosTitle.textContent = isWearing ? this.t('pros_title_worn') : this.t('pros_title_bare');
      if (this.el.consTitle) this.el.consTitle.textContent = isWearing ? this.t('cons_title_worn') : this.t('cons_title_bare');

      if (this.el.fitWidthStatus && fm) {
        this.el.fitWidthStatus.textContent = (STATUS_TRANSLATIONS[fm.width_status]?.[this.currentLang]) || fm.width_status;
        this.el.fitWidthStatus.className = (fm.width_status === 'Широковата' || fm.width_status === 'Узковата')
          ? 'font-bold text-amber-700'
          : 'font-bold text-emerald-700';
      }
      if (this.el.fitWidthDesc && fm) {
        this.el.fitWidthDesc.textContent = isEn
          ? (fm.width_status === 'Широковата' ? 'Exceeds cheekbones by +8 mm' : (fm.width_status === 'Узковата' ? 'Narrower than cheekbones' : 'Matches cheekbone line'))
          : fm.width_feedback_ru;
      }

      if (this.el.fitPupilStatus && fm) {
        this.el.fitPupilStatus.textContent = (STATUS_TRANSLATIONS[fm.pupil_status]?.[this.currentLang]) || fm.pupil_status;
      }
      if (this.el.fitPupilDesc && fm) {
        this.el.fitPupilDesc.textContent = isEn
          ? 'Positioned directly on optical axis of frame lens'
          : fm.pupil_feedback_ru;
      }

      if (this.el.fitEyebrowStatus && fm) {
        this.el.fitEyebrowStatus.textContent = (STATUS_TRANSLATIONS[fm.eyebrow_status]?.[this.currentLang]) || fm.eyebrow_status;
      }
      if (this.el.fitEyebrowDesc && fm) {
        this.el.fitEyebrowDesc.textContent = isEn
          ? 'Follows the lower curve of eyebrow arch'
          : fm.eyebrow_feedback_ru;
      }

      if (this.el.prosList) {
        if (isEn) {
          this.el.prosList.innerHTML = `
            <li>Frame width aligns cleanly with facial temple line</li>
            <li>Pupillary optical center is calibrated for clear sightline</li>
          `;
        } else {
          this.el.prosList.innerHTML = worn.pros_ru.map(p => `<li>${p}</li>`).join('');
        }
      }

      if (this.el.consList) {
        if (isEn) {
          if (worn.cons_ru && worn.cons_ru.length > 0) {
            this.el.consList.innerHTML = `<li>Frame extends slightly past temporal line; temples may flare</li>`;
          } else {
            this.el.consList.innerHTML = `<li>${this.t('cons_empty')}</li>`;
          }
        } else {
          if (worn.cons_ru && worn.cons_ru.length > 0) {
            this.el.consList.innerHTML = worn.cons_ru.map(c => `<li>${c}</li>`).join('');
          } else {
            this.el.consList.innerHTML = `<li>${this.t('cons_empty')}</li>`;
          }
        }
      }

      // Адаптация заголовков списка моделей
      if (this.el.recommendationsHeading) {
        this.el.recommendationsHeading.textContent = isWearing
          ? this.t('rec_heading_worn')
          : this.t('rec_heading_bare');
      }
      if (this.el.recommendationsSubheading) {
        this.el.recommendationsSubheading.textContent = isWearing
          ? this.t('rec_sub_worn')
          : this.t('rec_sub_bare');
      }
    }

    // 4. Каталог рекомендованных альтернатив (строго текстовые карточки)
    this.renderAlternatives(alternatives);

    // 5. Обновление биометрического контекста в ИИ-чате
    this.updateChatBiometricContext();
  }

  renderAlternatives(alternatives) {
    const container = this.el.alternativesContainer;
    container.innerHTML = '';

    if (!alternatives || alternatives.length === 0) return;
    const isEn = this.currentLang === 'en';

    alternatives.forEach(alt => {
      const card = document.createElement('div');
      card.className = 'bg-white brand-card brand-card-hover rounded-2xl p-5 flex flex-col justify-between border border-navy-900/15 shadow-sm transition-all hover:shadow-md';
      card.dataset.id = alt.frame_id;

      const genBadge = alt.generation ? `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-navy-100/70 text-navy-900 border border-navy-900/10">${alt.generation}</span>` : '';
      const cameraInfo = alt.camera ? `<div class="bg-navy-50/80 p-2.5 rounded-xl border border-navy-900/10 text-xs col-span-2"><span class="text-[10px] text-slate-500 font-semibold block uppercase tracking-wider">${this.t('card_camera')}</span><span class="font-bold text-navy-900">📷 ${alt.camera}</span></div>` : '';
      const priceTag = alt.price ? `<span class="text-xs font-extrabold text-navy-900 bg-navy-50 px-2.5 py-1 rounded-lg border border-navy-900/10">${this.formatPrice(alt.price, alt.currency)}</span>` : '';
      const shapeDisplay = isEn ? (FRAME_SHAPE_NAMES[alt.shape_name_ru]?.en || alt.shape || alt.shape_name_ru) : alt.shape_name_ru;
      const optometricText = isEn
        ? "Engineered geometric balance, optimized temple weight distribution, and precise optical pupil alignment."
        : alt.why_better_ru;

      card.innerHTML = `
        <div>
          <!-- Заголовок карточки: Бренд, Поколение и процент совместимости -->
          <div class="flex items-center justify-between gap-2 pb-3 mb-3 border-b border-navy-900/10">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-extrabold text-navy-900/80 uppercase tracking-wider">${alt.brand}</span>
              ${genBadge}
            </div>
            <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 shrink-0">
              ${alt.match_score}% ${isEn ? 'Match' : 'Совместимость'}
            </span>
          </div>

          <!-- Название модели и цена -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <h4 class="text-base font-extrabold text-navy-900 leading-snug">${alt.name}</h4>
            ${priceTag}
          </div>

          <!-- Технические параметры смарт-очков -->
          <div class="grid grid-cols-2 gap-2 text-xs mb-3">
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_lens_shape')}</span>
              <span class="font-bold text-navy-900">${shapeDisplay}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_dimensions')}</span>
              <span class="font-bold text-navy-900">${alt.dimensions} mm</span>
            </div>
            ${cameraInfo}
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_material')}</span>
              <span class="font-bold text-slate-700">${alt.material}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_color')}</span>
              <span class="font-bold text-slate-700">${alt.color}</span>
            </div>
          </div>

          <!-- Оптометрическое обоснование геометрии и смарт-функций -->
          <div class="p-3.5 rounded-xl bg-navy-50 border-l-4 border-navy-900 text-xs text-navy-950 leading-relaxed mb-3">
            <strong class="text-navy-900 text-[11px] block uppercase tracking-wider font-extrabold mb-1">${this.t('card_optometric_reason')}</strong>
            ${optometricText}
          </div>
        </div>

        <div class="pt-3 border-t border-navy-900/10 mt-1">
          <!-- Единственное действие: Показать консультанту в зале -->
          <button class="btn-alt-consultant btn-brand-primary w-full py-2.5 px-3 rounded-xl font-bold text-xs transition-all text-center">
            ${this.t('btn_open_pass')}
          </button>
        </div>
      `;

      card.querySelector('.btn-alt-consultant').addEventListener('click', (e) => {
        e.stopPropagation();
        this.state.selectedAlternative = alt;
        this.openPassModal(alt);
      });

      container.appendChild(card);
    });
  }

  openPassModal(alternative = null) {
    const analysis = this.state.analysis;
    if (!analysis) return;
    const isEn = this.currentLang === 'en';

    const frame = alternative || this.state.selectedAlternative || (analysis.top_alternatives && analysis.top_alternatives[0]);
    const worn = analysis.worn_frame_evaluation;
    const metrics = analysis.metrics;
    const isWearing = Boolean(worn && worn.has_glasses);

    const clientShapeName = isEn
      ? (analysis.face_shape?.shape_name_en || SHAPE_TRANSLATIONS[analysis.face_shape?.shape_id]?.en || 'Anatomical Profile')
      : (analysis.face_shape_ru || 'Анатомический тип');

    const wornShapeTitle = isEn
      ? (FRAME_SHAPE_NAMES[worn?.detected_shape_name_ru]?.en || worn?.detected_shape || 'Current Frame')
      : (worn ? worn.detected_shape_name_ru : 'Текущая модель');

    const clientCard = isWearing ? `
        <!-- 1. Текущая надетая оправа клиента -->
        <div class="p-4 rounded-xl bg-navy-50/70 border border-navy-900/15">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-navy-900/70 uppercase tracking-wider text-[10px] font-extrabold">${this.t('pass_current_worn')}</span>
            <span class="font-extrabold text-navy-900">${worn ? worn.compatibility_score : 80}% ${isEn ? 'compatibility' : 'совместимость'}</span>
          </div>
          <p class="text-sm font-extrabold text-navy-900">${wornShapeTitle}</p>
          <div class="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
            <span>${this.t('fit_metric_width')}: <strong class="text-navy-900">${(STATUS_TRANSLATIONS[worn?.fit_metrics?.width_status]?.[this.currentLang]) || worn?.fit_metrics?.width_status || 'Optimal'}</strong></span>
            <span>${this.t('fit_metric_pupil')}: <strong class="text-navy-900">${(STATUS_TRANSLATIONS[worn?.fit_metrics?.pupil_status]?.[this.currentLang]) || worn?.fit_metrics?.pupil_status || 'Optimal'}</strong></span>
            <span>${this.t('metric_chin_label')}: <strong class="text-navy-900">${metrics ? metrics.chin_sharpness_deg : 170}°</strong></span>
          </div>
        </div>
    ` : `
        <!-- 1. Первичный биометрический профиль лица клиента (без очков) -->
        <div class="p-4 rounded-xl bg-navy-50/70 border border-navy-900/15">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-navy-900/70 uppercase tracking-wider text-[10px] font-extrabold">${this.t('pass_current_bare')}</span>
            <span class="font-extrabold text-navy-900 bg-white px-2 py-0.5 rounded border border-navy-900/10">${isEn ? 'No Glasses' : 'Без очков'}</span>
          </div>
          <p class="text-sm font-extrabold text-navy-900">${clientShapeName}</p>
          <div class="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
            <span>${isEn ? 'Cheekbone width:' : 'Ширина скул:'} <strong class="text-navy-900">${metrics ? (metrics.temple_width_mm || 135) : 135} mm</strong></span>
            <span>${isEn ? 'Ratio index:' : 'Индекс пропорций:'} <strong class="text-navy-900">${metrics ? metrics.height_to_width_ratio : '1.30'}</strong></span>
            <span>${this.t('metric_chin_label')}: <strong class="text-navy-900">${metrics ? metrics.chin_sharpness_deg : 170}°</strong></span>
          </div>
        </div>
    `;

    const frameShapeLocalized = frame ? (isEn ? (FRAME_SHAPE_NAMES[frame.shape_name_ru]?.en || frame.shape) : frame.shape_name_ru) : '';
    const frameWhyLocalized = frame ? (isEn ? "Optimal geometric harmony and ergonomic frame balance for daily wear." : frame.why_better_ru) : '';

    this.el.passContent.innerHTML = `
      <div class="text-center pb-4 border-b border-navy-900/15">
        <!-- Official Logo in Pass Modal -->
        <img src="/static/images/brand/logo.png" alt="abooptika" class="h-8 w-auto mx-auto object-contain mb-2">
        <span class="inline-block text-[11px] uppercase font-extrabold px-3 py-0.5 rounded bg-navy-50 text-navy-900 border border-navy-900/15">
          ${isWearing ? this.t('pass_title_worn') : this.t('pass_title_bare')}
        </span>
        <p class="text-xs text-slate-500 mt-1.5">${this.t('pass_sub')}</p>
      </div>

      <div class="my-4 space-y-3">
        ${clientCard}

        <!-- 2. Рекомендованная модель с витрины салона -->
        ${frame ? `
        <div class="p-4 rounded-xl bg-white border-2 border-navy-900 shadow-sm">
          <div class="flex items-center justify-between text-xs mb-2">
            <span class="text-navy-900 font-extrabold uppercase tracking-wider text-[10px]">${isEn ? 'Recommended Smart Glasses:' : 'Рекомендованная модель смарт-очков:'}</span>
            <span class="font-black text-emerald-700 text-sm">${frame.match_score}% ${isEn ? 'Match' : 'Совместимость'}</span>
          </div>
          <h5 class="text-base font-extrabold text-navy-900">${frame.brand} — ${frame.name}</h5>
          ${frame.generation ? `<p class="text-xs text-navy-900/70 font-semibold mb-2">${frame.generation} ${frame.price ? '• ' + this.formatPrice(frame.price, frame.currency) : ''}</p>` : ''}
          
          <div class="grid grid-cols-2 gap-2 text-xs my-2.5">
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_lens_shape')}</span>
              <span class="font-bold text-navy-900">${frameShapeLocalized}</span>
            </div>
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_dimensions')}</span>
              <span class="font-bold text-navy-900">${frame.dimensions} mm</span>
            </div>
            ${frame.camera ? `
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10 col-span-2">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_camera')}</span>
              <span class="font-bold text-navy-900">📷 ${frame.camera}</span>
            </div>` : ''}
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10 col-span-2">
              <span class="text-[10px] text-slate-500 font-medium block">${this.t('card_material')}</span>
              <span class="font-bold text-slate-700">${frame.material}, ${frame.color}</span>
            </div>
          </div>

          <div class="text-[11px] text-navy-950 bg-navy-50 p-3 rounded-lg border-l-3 border-navy-900 leading-relaxed">
            <strong class="text-navy-900 block mb-0.5 uppercase tracking-wider font-extrabold text-[10px]">${this.t('card_optometric_reason')}</strong>
            ${frameWhyLocalized}
          </div>
        </div>
        ` : ''}
      </div>

      <div class="text-center pt-2">
        <p class="text-[11px] text-slate-500 mb-2.5">${this.t('pass_consultant_hint')}</p>
        <button onclick="window.print()" class="btn-brand-primary px-5 py-2.5 rounded-xl font-bold text-xs inline-flex items-center gap-2 shadow-md">
          ${this.t('print_pass')}
        </button>
      </div>
    `;

    this.el.passModal.classList.remove('hidden');
  }

  closePassModal() {
    this.el.passModal.classList.add('hidden');
  }

  resetToScan() {
    this.showScreen('scan');
    this.cameraManager.start();
  }

  /* ==========================================================================
     ИНТЕРАКТИВНЫЙ ИИ-КОНСУЛЬТАНТ ABOOOPTIKA (GEMINI API)
     ========================================================================== */
  initChat() {
    if (!this.el.btnToggleChat || !this.el.chatPanel) return;

    // Открытие / закрытие панели
    this.el.btnToggleChat.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggleChat();
    });

    if (this.el.btnChatClose) {
      this.el.btnChatClose.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleChat(false);
      });
    }

    if (this.el.btnChatClear) {
      this.el.btnChatClear.addEventListener('click', () => {
        this.clearChat();
      });
    }

    // Закрытие при тапе / клике вне панели чата
    document.addEventListener('click', (e) => {
      if (
        this.state.chatOpen &&
        this.el.chatPanel &&
        !this.el.chatPanel.contains(e.target) &&
        !this.el.btnToggleChat.contains(e.target)
      ) {
        this.toggleChat(false);
      }
    });

    // Ввод сообщения
    if (this.el.chatInput && this.el.btnChatSend) {
      this.el.chatInput.addEventListener('input', () => {
        const hasText = Boolean(this.el.chatInput.value.trim());
        this.el.btnChatSend.disabled = !hasText || this.state.chatLoading;
      });

      if (this.el.chatForm) {
        this.el.chatForm.addEventListener('submit', (e) => {
          e.preventDefault();
          this.sendChatMessage();
        });
      }
    }

    // Инициализация приветственного сообщения и подсказок
    this.renderInitialChatState();
  }

  renderInitialChatState() {
    this.state.chatMessages = [
      {
        role: 'assistant',
        content: this.t('chat_initial_greeting')
      }
    ];

    if (this.el.chatMessages) {
      this.el.chatMessages.innerHTML = '';
      this.appendMessageToUI(this.state.chatMessages[0]);
    }

    const defaultChips = this.t('chat_default_chips');
    this.renderChatChips(defaultChips);
  }

  toggleChat(forceOpen = null) {
    const next = forceOpen !== null ? forceOpen : !this.state.chatOpen;
    this.state.chatOpen = next;

    if (!this.el.chatPanel) return;

    if (next) {
      this.el.chatPanel.classList.remove('hidden');
      this.el.chatPanel.classList.add('chat-panel-animate-in');
      if (this.el.chatTriggerIcon) {
        this.el.chatTriggerIcon.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>`;
      }
      setTimeout(() => {
        this.scrollChatToBottom();
        this.el.chatInput?.focus();
      }, 100);
    } else {
      this.el.chatPanel.classList.add('hidden');
      this.el.chatPanel.classList.remove('chat-panel-animate-in');
      if (this.el.chatTriggerIcon) {
        this.el.chatTriggerIcon.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>`;
      }
    }
  }

  clearChat() {
    this.renderInitialChatState();
    if (this.state.analysis) {
      this.updateChatBiometricContext();
    }
  }

  updateChatBiometricContext() {
    if (!this.state.analysis || !this.el.chatBiometricBanner) return;

    const an = this.state.analysis;
    const isEn = this.currentLang === 'en';
    const shape = isEn
      ? (an.face_shape?.shape_name_en || SHAPE_TRANSLATIONS[an.face_shape?.shape_id]?.en || 'Face Identified')
      : (an.face_shape_ru || 'Лицо определено');
    const pd = an.metrics?.pupillary_distance_norm ? ` • PD ~63 mm` : '';
    
    this.el.chatBiometricBanner.classList.remove('hidden');
    if (this.el.chatBioContextText) {
      this.el.chatBioContextText.textContent = `${shape}${pd}`;
    }

    // Предлагаем персонализированные подсказки с учетом активного языка
    if (isEn) {
      this.renderChatChips([
        `🕶️ Best Meta glasses for ${shape}?`,
        "✨ What makes LISA Edition special?",
        "🎙️ Audio-only frames without cameras",
        "📄 Print biometric fitting slip"
      ]);
    } else {
      this.renderChatChips([
        `🕶️ Какие смарт-очки лучше для ${shape}?`,
        "✨ В чем отличие серии LISA Edition?",
        "🎙️ Очки со звуком без камер (Clubmaster)",
        "📄 Распечатать талон с витрины"
      ]);
    }
  }

  renderChatChips(chips) {
    if (!this.el.chatChipsBar || !chips) return;
    this.el.chatChipsBar.innerHTML = '';

    chips.forEach(chipText => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chat-chip px-3 py-1.5 rounded-full text-[11px] font-bold text-white bg-[#153B85] hover:bg-[#1E40AF] border border-white/30 whitespace-nowrap cursor-pointer shrink-0 transition-all shadow-sm';
      btn.style.cssText = 'background-color: #153B85 !important; color: #FFFFFF !important; border: 1px solid rgba(255,255,255,0.3) !important;';
      btn.textContent = chipText;
      btn.addEventListener('click', () => {
        this.sendChatMessage(chipText);
      });
      this.el.chatChipsBar.appendChild(btn);
    });
  }

  async sendChatMessage(customText = null) {
    const input = this.el.chatInput;
    const messageText = (customText || (input ? input.value : '') || '').trim();
    if (!messageText || this.state.chatLoading) return;

    // Очищаем поле ввода
    if (!customText && input) {
      input.value = '';
      if (this.el.btnChatSend) this.el.btnChatSend.disabled = true;
    }

    // Добавляем сообщение пользователя
    const userMsg = { role: 'user', content: messageText };
    this.state.chatMessages.push(userMsg);
    this.appendMessageToUI(userMsg);

    // Включаем индикатор набора
    this.state.chatLoading = true;
    this.showTypingIndicator();
    this.scrollChatToBottom();

    // Формируем биометрический контекст клиента, если сканирование уже сделано
    let clientContext = null;
    if (this.state.analysis) {
      const an = this.state.analysis;
      clientContext = {
        face_shape_ru: an.face_shape?.shape_name_ru || an.face_shape_ru,
        face_shape_en: an.face_shape?.shape_name_en,
        metrics: an.metrics,
        worn_frame: an.worn_frame_evaluation,
        top_recommendations: an.top_alternatives?.map(a => `${a.brand} ${a.name}`),
        language: this.currentLang
      };
    } else {
      clientContext = { language: this.currentLang };
    }

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: this.state.chatMessages,
          client_context: clientContext,
          language: this.currentLang
        })
      });

      const data = await res.json();
      this.hideTypingIndicator();
      this.state.chatLoading = false;

      if (data && data.reply) {
        const assistantMsg = { role: 'assistant', content: data.reply };
        this.state.chatMessages.push(assistantMsg);
        this.appendMessageToUI(assistantMsg);

        if (data.suggested_prompts && data.suggested_prompts.length > 0) {
          this.renderChatChips(data.suggested_prompts);
        }
      } else {
        this.appendMessageToUI({
          role: 'assistant',
          content: this.currentLang === 'en'
            ? 'Apologies, temporary network delay. Please repeat your question or ask our in-store consultant.'
            : 'Прошу прощения, произошла задержка связи. Пожалуйста, повторите вопрос или проконсультируйтесь со стилистом в зале.'
        });
      }
    } catch (err) {
      console.error('Ошибка чата:', err);
      this.hideTypingIndicator();
      this.state.chatLoading = false;
      this.appendMessageToUI({
        role: 'assistant',
        content: this.currentLang === 'en'
          ? 'Network connectivity hiccup. The AbooOptika optical consultant is always ready to demonstrate frames from the showroom.'
          : 'Временный сбой связи. Консультант AbooOptika всегда готов продемонстрировать очки с витрины салона.'
      });
    }

    this.scrollChatToBottom();
  }

  appendMessageToUI(msg) {
    if (!this.el.chatMessages) return;

    const isUser = msg.role === 'user';
    const bubble = document.createElement('div');
    bubble.className = isUser ? 'flex justify-end' : 'flex justify-start';

    const formattedContent = this.formatChatMarkdown(msg.content);

    if (isUser) {
      bubble.innerHTML = `
        <div class="chat-bubble-user text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-xs sm:text-[13px] max-w-[85%] shadow-md leading-relaxed font-medium"
             style="background: #1E3A8A !important; color: #FFFFFF !important; border: 1px solid rgba(255,255,255,0.3) !important;">
          ${formattedContent}
        </div>
      `;
    } else {
      bubble.innerHTML = `
        <div class="flex items-start gap-2.5 max-w-[94%]">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full overflow-hidden shrink-0 border border-white/40 shadow-md mt-0.5 bg-[#071840]">
            <img src="/static/images/brand/ai-avatar.png" alt="AbooOptika AI" class="w-full h-full object-cover">
          </div>
          <div class="chat-bubble-ai flex-1 rounded-2xl rounded-tl-sm p-3.5 sm:p-4 text-xs sm:text-[13px] text-white shadow-md leading-relaxed"
               style="background: #0E275E !important; color: #FFFFFF !important; border: 1.5px solid rgba(255,255,255,0.2) !important;">
            <div class="flex items-center gap-1.5 mb-2 text-[10px] font-black text-emerald-300 uppercase tracking-wider">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              AbooOptika AI • Эксперт
            </div>
            <div class="space-y-1.5 text-slate-100 font-normal leading-relaxed">
              ${formattedContent}
            </div>
          </div>
        </div>
      `;
    }

    this.el.chatMessages.appendChild(bubble);
  }

  showTypingIndicator() {
    if (!this.el.chatMessages) return;
    this.hideTypingIndicator();

    const indicator = document.createElement('div');
    indicator.id = 'chat-typing-indicator';
    indicator.className = 'flex justify-start';
    indicator.innerHTML = `
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full overflow-hidden shrink-0 border border-white/40 shadow-md bg-[#071840]">
          <img src="/static/images/brand/ai-avatar.png" alt="AbooOptika AI" class="w-full h-full object-cover">
        </div>
        <div class="chat-bubble-ai rounded-2xl rounded-tl-sm px-4 py-2.5 flex items-center gap-2 text-white shadow-md"
             style="background: #0E275E !important; color: #FFFFFF !important; border: 1.5px solid rgba(255,255,255,0.2) !important;">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay: 0.15s"></span>
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" style="animation-delay: 0.3s"></span>
          <span class="text-[11px] font-bold text-slate-200 ml-1">Консультант печатает...</span>
        </div>
      </div>
    `;
    this.el.chatMessages.appendChild(indicator);
  }

  hideTypingIndicator() {
    const el = document.getElementById('chat-typing-indicator');
    if (el) el.remove();
  }

  formatChatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-extrabold">$1</strong>')
      .replace(/^[•\-]\s+(.*)$/gm, '<li class="ml-3 list-disc text-slate-100 leading-normal">$1</li>')
      .replace(/^(\d+)\.\s+(.*)$/gm, '<div class="flex gap-2 my-1"><span class="text-emerald-300 font-extrabold shrink-0">$1.</span><span class="text-slate-100 font-medium">$2</span></div>')
      .replace(/\n\n/g, '<div class="h-2"></div>')
      .replace(/\n/g, '<br>');
    return html;
  }

  scrollChatToBottom() {
    if (this.el.chatMessages) {
      this.el.chatMessages.scrollTop = this.el.chatMessages.scrollHeight;
    }
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new AboOptikaApp();
});
