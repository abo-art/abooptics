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
      soundEnabled: true
    };

    this.audioCtx = null;
    this.initElements();
    this.initAudio();
    this.initEventListeners();
    this.initCamera();
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

      // Вердикт оптометриста
      verdictCard: document.getElementById('verdict-card'),
      wornShapeName: document.getElementById('worn-shape-name'),
      wornScore: document.getElementById('worn-compatibility-score'),
      wornBadge: document.getElementById('worn-match-badge'),
      stylistQuote: document.getElementById('stylist-quote'),
      fitWidthStatus: document.getElementById('fit-width-status'),
      fitWidthDesc: document.getElementById('fit-width-desc'),
      fitPupilStatus: document.getElementById('fit-pupil-status'),
      fitPupilDesc: document.getElementById('fit-pupil-desc'),
      fitEyebrowStatus: document.getElementById('fit-eyebrow-status'),
      fitEyebrowDesc: document.getElementById('fit-eyebrow-desc'),
      prosList: document.getElementById('pros-list'),
      consList: document.getElementById('cons-list'),

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
      salonBanner: document.getElementById('salon-banner')
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

    // 3. Заключение оптометриста по надетой оправе
    if (worn) {
      if (this.el.wornShapeName) this.el.wornShapeName.textContent = worn.detected_shape_name_ru;
      if (this.el.wornScore) this.el.wornScore.textContent = `${worn.compatibility_score}%`;
      if (this.el.wornBadge) this.el.wornBadge.textContent = worn.match_badge;
      if (this.el.stylistQuote) this.el.stylistQuote.textContent = worn.verdict_quote_ru;

      const fm = worn.fit_metrics;
      if (this.el.fitWidthStatus) {
        this.el.fitWidthStatus.textContent = fm.width_status;
        this.el.fitWidthStatus.className = fm.width_status === 'Широковата' || fm.width_status === 'Узковата'
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
        this.el.consList.innerHTML = worn.cons_ru.map(c => `<li>${c}</li>`).join('');
      }
    }

    // 4. Каталог рекомендованных альтернатив (строго текстовые карточки)
    this.renderAlternatives(alternatives);
  }

  renderAlternatives(alternatives) {
    const container = this.el.alternativesContainer;
    container.innerHTML = '';

    if (!alternatives || alternatives.length === 0) return;

    alternatives.forEach(alt => {
      const card = document.createElement('div');
      card.className = 'bg-white brand-card brand-card-hover rounded-2xl p-5 flex flex-col justify-between border border-navy-900/15 shadow-sm transition-all';
      card.dataset.id = alt.frame_id;

      // Строго текстовое представление модели (без мультяшных картинок, без кнопок продаж)
      card.innerHTML = `
        <div>
          <!-- Заголовок карточки: Бренд и процент совместимости -->
          <div class="flex items-center justify-between gap-2 pb-3 mb-3 border-b border-navy-900/10">
            <span class="text-xs font-extrabold text-navy-900/70 uppercase tracking-wider">${alt.brand}</span>
            <span class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              ${alt.match_score}% Совместимость
            </span>
          </div>

          <!-- Название модели -->
          <h4 class="text-base font-extrabold text-navy-900 mb-2 leading-snug">${alt.name}</h4>

          <!-- Технические параметры оправы -->
          <div class="grid grid-cols-2 gap-2 text-xs mb-3">
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Форма линз</span>
              <span class="font-bold text-navy-900">${alt.shape_name_ru}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Размеры (линза-мост-заушник)</span>
              <span class="font-bold text-navy-900">${alt.dimensions} мм</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Материал</span>
              <span class="font-bold text-slate-700">${alt.material}</span>
            </div>
            <div class="bg-navy-50/70 p-2.5 rounded-xl border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Цвет рамки</span>
              <span class="font-bold text-slate-700">${alt.color}</span>
            </div>
          </div>

          <!-- Оптометрическое обоснование геометрии -->
          <div class="p-3.5 rounded-xl bg-navy-50 border-l-4 border-navy-900 text-xs text-navy-950 leading-relaxed mb-3">
            <strong class="text-navy-900 text-[11px] block uppercase tracking-wider font-extrabold mb-1">Геометрическая компенсация:</strong>
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

    this.el.passContent.innerHTML = `
      <div class="text-center pb-4 border-b border-navy-900/15">
        <!-- Official Logo in Pass Modal -->
        <img src="/static/images/brand/logo.png" alt="abooptika" class="h-8 w-auto mx-auto object-contain mb-2">
        <span class="inline-block text-[11px] uppercase font-extrabold px-3 py-0.5 rounded bg-navy-50 text-navy-900 border border-navy-900/15">
          Талон примерки в салоне оптики
        </span>
        <p class="text-xs text-slate-500 mt-1.5">Покажите данный бланк консультанту оптики для подбора оправы с витрины</p>
      </div>

      <div class="my-4 space-y-3">
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
        </div>

        <!-- 2. Рекомендованная модель с витрины салона -->
        ${frame ? `
        <div class="p-4 rounded-xl bg-white border-2 border-navy-900 shadow-sm">
          <div class="flex items-center justify-between text-xs mb-2">
            <span class="text-navy-900 font-extrabold uppercase tracking-wider text-[10px]">Рекомендованная альтернатива с витрины:</span>
            <span class="font-black text-emerald-700 text-sm">${frame.match_score}% Совместимость</span>
          </div>
          <h5 class="text-base font-extrabold text-navy-900">${frame.brand} — ${frame.name}</h5>
          
          <div class="grid grid-cols-2 gap-2 text-xs my-2.5">
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Форма</span>
              <span class="font-bold text-navy-900">${frame.shape_name_ru}</span>
            </div>
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Параметры</span>
              <span class="font-bold text-navy-900">${frame.dimensions} мм</span>
            </div>
            <div class="bg-navy-50/70 p-2 rounded-lg border border-navy-900/10">
              <span class="text-[10px] text-slate-500 font-medium block">Материал / Цвет</span>
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
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new AboOptikaApp();
});
