/**
 * abooptika — Профессиональный аналитический интерфейс оптики
 * Инструмент оценки посадки оправы и биометрии лица без графического мусора,
 * без кнопок продаж/бронирований и без маркетинговой воды.
 */

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

    this.audioCtx = null;
    this.initElements();
    this.initAudio();
    this.initEventListeners();
    this.initCamera();
    this.initChat();
  }

  initElements() {
    this.el = {
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

      // Топ-3 альтернативы
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
        this.el.btnToggleMirror.textContent = isMirrored ? 'Оси: 1:1' : 'Оси: Инверс';
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

    const steps = [
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
        alert(result.message || 'Лицо не обнаружено в кадре. Пожалуйста, посмотрите прямо в камеру.');
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
      alert('Ошибка при анализе: ' + err.message);
      this.showScreen('scan');
    } finally {
      this.state.isAnalyzing = false;
    }
  }

  displayResults(result) {
    const shape = result.face_shape;
    const metrics = result.metrics;
    const worn = result.worn_frame_evaluation;
    const alternatives = result.top_alternatives;

    // 1. Реальное фото примерки без графических наложений
    if (this.el.clientRealPhoto) {
      this.el.clientRealPhoto.src = this.state.imageSrc;
    }

    // 2. Биометрические параметры лица
    if (this.el.shapeTitle) {
      this.el.shapeTitle.textContent = shape.shape_name_ru;
    }
    if (this.el.shapeConfidence) {
      this.el.shapeConfidence.textContent = `${shape.confidence}% точность`;
    }
    if (this.el.shapeDescription) {
      this.el.shapeDescription.textContent = shape.description_ru;
    }

    if (this.el.metricHw) this.el.metricHw.textContent = metrics.height_to_width_ratio.toFixed(2);
    if (this.el.metricJc) this.el.metricJc.textContent = metrics.jaw_to_cheek_ratio.toFixed(2);
    if (this.el.metricChin) this.el.metricChin.textContent = `${metrics.chin_sharpness_deg}°`;
    if (this.el.metricSym) this.el.metricSym.textContent = `${metrics.symmetry_score}%`;

    // 3. Заключение оптометриста (Оценка надетой оправы ИЛИ Режим первичного подбора без очков)
    if (worn) {
      const isWearing = Boolean(worn.has_glasses);

      if (this.el.verdictSectionModeTitle) {
        this.el.verdictSectionModeTitle.textContent = isWearing
          ? 'Оценка посадки надетой оправы'
          : 'Персональный подбор оправы под анатомию лица';
      }

      if (this.el.wornShapeName) {
        this.el.wornShapeName.textContent = isWearing
          ? worn.detected_shape_name_ru
          : 'Режим: Подбор идеальной оправы';
      }

      if (this.el.wornScoreLabel) {
        this.el.wornScoreLabel.textContent = isWearing ? 'Совместимость:' : 'Базис геометрии:';
      }

      if (this.el.wornScore) {
        this.el.wornScore.textContent = isWearing ? `${worn.compatibility_score}%` : '98%';
      }

      if (this.el.wornBadge) {
        this.el.wornBadge.textContent = isWearing ? worn.match_badge : '👤 Без очков • Режим подбора';
        this.el.wornBadge.className = isWearing
          ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-white text-navy-900 border border-navy-900/15 shadow-sm'
          : 'text-[10px] font-bold px-2 py-0.5 rounded bg-sky-50 text-sky-800 border border-sky-200 shadow-sm';
      }

      if (this.el.stylistQuote) {
        this.el.stylistQuote.textContent = worn.verdict_quote_ru;
      }

      // Чистый брендовый бейдж AbooOptika (без Smart Meta Lab и без сырых имен моделей)
      if (this.el.aiModelPill) {
        this.el.aiModelPill.textContent = 'AbooOptika AI Biometrics';
        this.el.aiModelPill.className = 'text-[10px] font-bold text-navy-900/70 bg-navy-100/60 px-2 py-0.5 rounded border border-navy-900/10';
      }

      // Нюансы по мостику и заушникам смарт-очков
      if (this.el.bridgeNuanceText && worn.bridge_nuance_ru) {
        this.el.bridgeNuanceText.textContent = worn.bridge_nuance_ru;
      }
      if (this.el.templeNuanceText && worn.temple_nuance_ru) {
        this.el.templeNuanceText.textContent = worn.temple_nuance_ru;
      }

      const fm = worn.fit_metrics;
      if (this.el.fitMetric1Title) this.el.fitMetric1Title.textContent = isWearing ? 'Ширина оправы' : 'Целевая ширина оправы';
      if (this.el.fitMetric2Title) this.el.fitMetric2Title.textContent = isWearing ? 'Положение зрачков' : 'Оптический центр';
      if (this.el.fitMetric3Title) this.el.fitMetric3Title.textContent = isWearing ? 'Линия бровей' : 'Линия надбровных дуг';
      if (this.el.prosTitle) this.el.prosTitle.textContent = isWearing ? 'Соответствия:' : 'Анатомические преимущества геометрии:';
      if (this.el.consTitle) this.el.consTitle.textContent = isWearing ? 'Отклонения и риски:' : 'Рекомендации оптометриста:';

      if (this.el.fitWidthStatus) {
        this.el.fitWidthStatus.textContent = fm.width_status;
        this.el.fitWidthStatus.className = (fm.width_status === 'Широковата' || fm.width_status === 'Узковата')
          ? 'font-bold text-amber-700'
          : 'font-bold text-emerald-700';
      }
      if (this.el.fitWidthDesc) this.el.fitWidthDesc.textContent = fm.width_feedback_ru;

      if (this.el.fitPupilStatus) this.el.fitPupilStatus.textContent = fm.pupil_status;
      if (this.el.fitPupilDesc) this.el.fitPupilDesc.textContent = fm.pupil_feedback_ru;

      if (this.el.fitEyebrowStatus) this.el.fitEyebrowStatus.textContent = fm.eyebrow_status;
      if (this.el.fitEyebrowDesc) this.el.fitEyebrowDesc.textContent = fm.eyebrow_feedback_ru;

      if (this.el.prosList) {
        this.el.prosList.innerHTML = worn.pros_ru.map(p => `<li>${p}</li>`).join('');
      }
      if (this.el.consList) {
        if (worn.cons_ru && worn.cons_ru.length > 0) {
          this.el.consList.innerHTML = worn.cons_ru.map(c => `<li>${c}</li>`).join('');
        } else {
          this.el.consList.innerHTML = `<li>Отклонений не выявлено. Лицо готово к первой примерке рекомендованных моделей.</li>`;
        }
      }

      // Адаптация заголовков списка моделей
      if (this.el.recommendationsHeading) {
        this.el.recommendationsHeading.textContent = isWearing
          ? 'ТОП-5 рекомендованных альтернатив Meta взамен текущей оправы'
          : 'ТОП-5 рекомендованных моделей смарт-очков Meta для вашего типа лица';
      }
      if (this.el.recommendationsSubheading) {
        this.el.recommendationsSubheading.textContent = isWearing
          ? 'Официальная линейка Meta с улучшенной посадкой и геометрической компенсацией'
          : 'Официальные модели Meta с идеальной анатомической посадкой для вашей формы лица';
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

    alternatives.forEach(alt => {
      const card = document.createElement('div');
      card.className = 'bg-white brand-card brand-card-hover rounded-2xl p-5 flex flex-col justify-between border border-navy-900/15 shadow-sm transition-all hover:shadow-md';
      card.dataset.id = alt.frame_id;

      const genBadge = alt.generation ? `<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-navy-100/70 text-navy-900 border border-navy-900/10">${alt.generation}</span>` : '';
      const cameraInfo = alt.camera ? `<div class="bg-navy-50/80 p-2.5 rounded-xl border border-navy-900/10 text-xs col-span-2"><span class="text-[10px] text-slate-500 font-semibold block uppercase tracking-wider">Камера & Видео</span><span class="font-bold text-navy-900">📷 ${alt.camera}</span></div>` : '';
      const priceTag = alt.price ? `<span class="text-xs font-extrabold text-navy-900 bg-navy-50 px-2.5 py-1 rounded-lg border border-navy-900/10">${Number(alt.price).toLocaleString('ru-RU')} ${alt.currency || '₸'}</span>` : '';

      card.innerHTML = `
        <div>
          <!-- Заголовок карточки: Бренд, Поколение и процент совместимости -->
          <div class="flex items-center justify-between gap-2 pb-3 mb-3 border-b border-navy-900/10">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-extrabold text-navy-900/80 uppercase tracking-wider">${alt.brand}</span>
              ${genBadge}
            </div>
            <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 shrink-0">
              ${alt.match_score}% Совместимость
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
              <span class="text-[10px] text-slate-500 font-medium block">Форма линз</span>
              <span class="font-bold text-navy-900">${alt.shape_name_ru}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Размеры (линза-мост-заушник)</span>
              <span class="font-bold text-navy-900">${alt.dimensions} мм</span>
            </div>
            ${cameraInfo}
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Материал оправы</span>
              <span class="font-bold text-slate-700">${alt.material}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Цвет & Линзы</span>
              <span class="font-bold text-slate-700">${alt.color}</span>
            </div>
          </div>

          <!-- Оптометрическое обоснование геометрии и смарт-функций -->
          <div class="p-3.5 rounded-xl bg-navy-50 border-l-4 border-navy-900 text-xs text-navy-950 leading-relaxed mb-3">
            <strong class="text-navy-900 text-[11px] block uppercase tracking-wider font-extrabold mb-1">Оптометрическая компенсация & Эргономика:</strong>
            ${alt.why_better_ru}
          </div>
        </div>

        <div class="pt-3 border-t border-navy-900/10 mt-1">
          <!-- Единственное действие: Показать консультанту в зале -->
          <button class="btn-alt-consultant btn-brand-primary w-full py-2.5 px-3 rounded-xl font-bold text-xs transition-all text-center">
            Показать консультанту в зале
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

    const frame = alternative || this.state.selectedAlternative || (analysis.top_alternatives && analysis.top_alternatives[0]);
    const worn = analysis.worn_frame_evaluation;
    const metrics = analysis.metrics;
    const isWearing = Boolean(worn && worn.has_glasses);

    const clientCard = isWearing ? `
        <!-- 1. Текущая надетая оправа клиента -->
        <div class="p-4 rounded-xl bg-navy-50/70 border border-navy-900/15">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-navy-900/70 uppercase tracking-wider text-[10px] font-extrabold">Текущая примерка клиента:</span>
            <span class="font-extrabold text-navy-900">${worn ? worn.compatibility_score : 80}% совместимость</span>
          </div>
          <p class="text-sm font-extrabold text-navy-900">${worn ? worn.detected_shape_name_ru : 'Текущая модель'}</p>
          <p class="text-xs text-slate-700 mt-1">${worn ? worn.verdict_quote_ru : ''}</p>
          <div class="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
            <span>Ширина: <strong class="text-navy-900">${worn ? worn.fit_metrics.width_status : 'Широковата'}</strong></span>
            <span>Зрачки: <strong class="text-navy-900">${worn ? worn.fit_metrics.pupil_status : 'Идеально'}</strong></span>
            <span>Угол челюсти: <strong class="text-navy-900">${metrics ? metrics.chin_sharpness_deg : 170}°</strong></span>
          </div>
          ${worn && (worn.bridge_nuance_ru || worn.temple_nuance_ru) ? `
          <div class="mt-2.5 pt-2 border-t border-navy-900/10 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            ${worn.bridge_nuance_ru ? `<div class="bg-white/90 p-2 rounded-lg border border-navy-900/10"><strong class="text-[10px] text-navy-900 block uppercase font-bold mb-0.5">Нюанс мостика:</strong><span class="text-slate-700">${worn.bridge_nuance_ru}</span></div>` : ''}
            ${worn.temple_nuance_ru ? `<div class="bg-white/90 p-2 rounded-lg border border-navy-900/10"><strong class="text-[10px] text-navy-900 block uppercase font-bold mb-0.5">Нюанс заушников:</strong><span class="text-slate-700">${worn.temple_nuance_ru}</span></div>` : ''}
          </div>` : ''}
        </div>
    ` : `
        <!-- 1. Первичный биометрический профиль лица клиента (без очков) -->
        <div class="p-4 rounded-xl bg-navy-50/70 border border-navy-900/15">
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-navy-900/70 uppercase tracking-wider text-[10px] font-extrabold">Биометрический профиль лица:</span>
            <span class="font-extrabold text-navy-900 bg-white px-2 py-0.5 rounded border border-navy-900/10">Без очков</span>
          </div>
          <p class="text-sm font-extrabold text-navy-900">${analysis.face_shape_ru || 'Анатомический тип'}</p>
          <p class="text-xs text-slate-700 mt-1">${worn ? worn.verdict_quote_ru : 'Выполнено первичное сканирование геометрии лица для подбора первой идеальной смарт-оправы.'}</p>
          <div class="mt-2 text-[11px] text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
            <span>Ширина скул: <strong class="text-navy-900">${metrics ? (metrics.temple_width_mm || 135) : 135} мм</strong></span>
            <span>Индекс пропорций: <strong class="text-navy-900">${metrics ? metrics.height_to_width_ratio : '1.30'}</strong></span>
            <span>Угол челюсти: <strong class="text-navy-900">${metrics ? metrics.chin_sharpness_deg : 170}°</strong></span>
          </div>
          ${worn && (worn.bridge_nuance_ru || worn.temple_nuance_ru) ? `
          <div class="mt-2.5 pt-2 border-t border-navy-900/10 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            ${worn.bridge_nuance_ru ? `<div class="bg-white/90 p-2 rounded-lg border border-navy-900/10"><strong class="text-[10px] text-navy-900 block uppercase font-bold mb-0.5">Рекомендация по мостику:</strong><span class="text-slate-700">${worn.bridge_nuance_ru}</span></div>` : ''}
            ${worn.temple_nuance_ru ? `<div class="bg-white/90 p-2 rounded-lg border border-navy-900/10"><strong class="text-[10px] text-navy-900 block uppercase font-bold mb-0.5">Рекомендация по заушникам:</strong><span class="text-slate-700">${worn.temple_nuance_ru}</span></div>` : ''}
          </div>` : ''}
        </div>
    `;

    this.el.passContent.innerHTML = `
      <div class="text-center pb-4 border-b border-navy-900/15">
        <!-- Official Logo in Pass Modal -->
        <img src="/static/images/brand/logo.png" alt="abooptika" class="h-8 w-auto mx-auto object-contain mb-2">
        <span class="inline-block text-[11px] uppercase font-extrabold px-3 py-0.5 rounded bg-navy-50 text-navy-900 border border-navy-900/15">
          ${isWearing ? 'Талон примерки смарт-очков Meta' : 'Талон персонального подбора смарт-очков Meta'}
        </span>
        <p class="text-xs text-slate-500 mt-1.5">Покажите данный бланк консультанту оптики для подбора оправы с витрины</p>
      </div>

      <div class="my-4 space-y-3">
        ${clientCard}

        <!-- 2. Рекомендованная модель с витрины салона -->
        ${frame ? `
        <div class="p-4 rounded-xl bg-white border-2 border-navy-900 shadow-sm">
          <div class="flex items-center justify-between text-xs mb-2">
            <span class="text-navy-900 font-extrabold uppercase tracking-wider text-[10px]">Рекомендованная модель смарт-очков:</span>
            <span class="font-black text-emerald-700 text-sm">${frame.match_score}% Совместимость</span>
          </div>
          <h5 class="text-base font-extrabold text-navy-900">${frame.brand} — ${frame.name}</h5>
          ${frame.generation ? `<p class="text-xs text-navy-900/70 font-semibold mb-2">${frame.generation} ${frame.price ? '• ' + Number(frame.price).toLocaleString('ru-RU') + ' ' + (frame.currency || '₸') : ''}</p>` : ''}
          
          <div class="grid grid-cols-2 gap-2 text-xs my-2.5">
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Форма оправы</span>
              <span class="font-bold text-navy-900">${frame.shape_name_ru}</span>
            </div>
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Размеры (линза-мост-дужка)</span>
              <span class="font-bold text-navy-900">${frame.dimensions} мм</span>
            </div>
            ${frame.camera ? `
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10 col-span-2">
              <span class="text-[10px] text-slate-500 font-medium block">Камера & Видео</span>
              <span class="font-bold text-navy-900">📷 ${frame.camera}</span>
            </div>` : ''}
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10 col-span-2">
              <span class="text-[10px] text-slate-500 font-medium block">Материал / Отделка</span>
              <span class="font-bold text-slate-700">${frame.material}, ${frame.color}</span>
            </div>
          </div>

          <div class="text-[11px] text-navy-950 bg-navy-50 p-3 rounded-lg border-l-3 border-navy-900 leading-relaxed">
            <strong class="text-navy-900 block mb-0.5 uppercase tracking-wider font-extrabold text-[10px]">Оптометрическая причина рекомендации:</strong>
            ${frame.why_better_ru}
          </div>
        </div>
        ` : ''}
      </div>

      <div class="text-center pt-2">
        <p class="text-[11px] text-slate-500 mb-2.5">Консультант предоставит эту модель с витрины для контрольной примерки</p>
        <button onclick="window.print()" class="btn-brand-primary px-5 py-2.5 rounded-xl font-bold text-xs inline-flex items-center gap-2 shadow-md">
          Распечатать талон примерки
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
        content: `Здравствуйте! Я персональный ИИ-стилист и эксперт **AbooOptika**.\n\nЯ знаю все 25 моделей смарт-очков **Meta** (Ray-Ban Meta, Meta и Oakley) и помогу вам:\n• Подобрать идеальную оправу под геометрию вашего лица\n• Рассказать о новинках: **LISA Edition**, **Meta Fury**, **Zena Gen 3**\n• Выбрать аудио-версии без камер (**Clubmaster Audio**, **Burbank Audio**)\n• Объяснить результаты оптического сканирования\n\nЧем я могу помочь вам прямо сейчас?`
      }
    ];

    if (this.el.chatMessages) {
      this.el.chatMessages.innerHTML = '';
      this.appendMessageToUI(this.state.chatMessages[0]);
    }

    this.renderChatChips([
      "✨ В чем отличие серии LISA Edition?",
      "🕶️ Посоветуй модель под мое лицо",
      "🎙️ Очки со звуком без камер (Clubmaster)",
      "📷 Как работает 12MP камера в Wayfarer?",
      "💰 Сколько стоят очки в тенге (₸)?"
    ]);
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
    const shape = an.face_shape_ru || 'Лицо определено';
    const pd = an.metrics?.pupillary_distance_mm ? ` • PD ${an.metrics.pupillary_distance_mm} мм` : '';
    
    this.el.chatBiometricBanner.classList.remove('hidden');
    if (this.el.chatBioContextText) {
      this.el.chatBioContextText.textContent = `${shape}${pd}`;
    }

    // Предлагаем персонализированные подсказки с учетом геометрии
    this.renderChatChips([
      `🕶️ Какие смарт-очки лучше для ${shape}?`,
      "✨ В чем отличие серии LISA Edition?",
      "🎙️ Очки со звуком без камер (Clubmaster)",
      "📄 Распечатать талон с витрины"
    ]);
  }

  renderChatChips(chips) {
    if (!this.el.chatChipsBar) return;
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
        face_shape_ru: an.face_shape_ru,
        metrics: an.metrics,
        worn_frame: an.worn_frame_evaluation,
        top_recommendations: an.top_alternatives?.map(a => `${a.brand} ${a.name}`)
      };
    }

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: this.state.chatMessages,
          client_context: clientContext
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
          content: 'Прошу прощения, произошла задержка связи. Пожалуйста, повторите вопрос или проконсультируйтесь со стилистом в зале.'
        });
      }
    } catch (err) {
      console.error('Ошибка чата:', err);
      this.hideTypingIndicator();
      this.state.chatLoading = false;
      this.appendMessageToUI({
        role: 'assistant',
        content: 'Временный сбой связи. Консультант AbooOptika всегда готов продемонстрировать очки с витрины салона.'
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
