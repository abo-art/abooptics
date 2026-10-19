/**
 * Camera Controller for abooptika MVP
 * Manages MediaDevices API, front/back switching, video stream, and frame capture.
 * Supports direct 1:1 user motion alignment (scaleX(-1)) and non-mirrored back camera (scaleX(1)).
 */

class CameraManager {
  constructor(videoElement, canvasElement, options = {}) {
    this.video = videoElement;
    this.canvas = canvasElement;
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.stream = null;
    this.facingMode = 'user'; // 'user' (front) or 'environment' (back)
    this.isMirrored = options.isMirrored !== undefined ? options.isMirrored : true; // Default true: motions match 1:1 with user
    this.isActive = false;
    this.onStatusChange = options.onStatusChange || (() => {});
    this.onError = options.onError || (() => {});
  }

  applyOrientation() {
    if (!this.video) return;
    // Для фронтальной камеры по умолчанию зеркалим по горизонтали (-1),
    // чтобы движения пользователя совпадали 1:1 (рука влево -> рука на экране влево)
    if (this.facingMode === 'user' && this.isMirrored) {
      this.video.style.transform = 'scaleX(-1)';
      this.video.style.webkitTransform = 'scaleX(-1)';
    } else {
      this.video.style.transform = 'scaleX(1)';
      this.video.style.webkitTransform = 'scaleX(1)';
    }
  }

  toggleMirror() {
    this.isMirrored = !this.isMirrored;
    this.applyOrientation();
    return this.isMirrored;
  }

  async start() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const err = new Error('Ваш браузер не поддерживает доступ к камере (MediaDevices API). Используйте загрузку фото.');
      this.onError(err);
      return false;
    }

    try {
      this.stop(); // Stop any existing stream first

      const constraints = {
        video: {
          facingMode: this.facingMode,
          width: { ideal: 1280 },
          height: { ideal: 1280 }
        },
        audio: false
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;
      this.applyOrientation();
      await this.video.play();
      this.isActive = true;
      this.onStatusChange({ active: true, facingMode: this.facingMode });
      return true;
    } catch (err) {
      console.warn('Camera access error:', err);
      this.isActive = false;
      this.onStatusChange({ active: false, error: err });
      this.onError(err);
      return false;
    }
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.video) {
      this.video.srcObject = null;
    }
    this.isActive = false;
    this.onStatusChange({ active: false });
  }

  async toggleFacingMode() {
    this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
    this.applyOrientation();
    if (this.isActive) {
      return await this.start();
    }
    return true;
  }

  captureFrameDataUrl(maxWidth = 1000, quality = 0.9) {
    if (!this.isActive || !this.video.videoWidth) {
      throw new Error('Камера не активна для захвата кадра');
    }

    const vw = this.video.videoWidth;
    const vh = this.video.videoHeight;

    // Масштабируем до удобного размера для высокой скорости передачи
    let targetW = vw;
    let targetH = vh;
    if (targetW > maxWidth) {
      targetH = Math.round((vh * maxWidth) / targetW);
      targetW = maxWidth;
    }

    this.canvas.width = targetW;
    this.canvas.height = targetH;
    
    // Синхронизация кадра: снимок должен в точности соответствовать тому, что видит пользователь
    if (this.facingMode === 'user' && this.isMirrored) {
      this.ctx.save();
      this.ctx.translate(targetW, 0);
      this.ctx.scale(-1, 1);
      this.ctx.drawImage(this.video, 0, 0, targetW, targetH);
      this.ctx.restore();
    } else {
      this.ctx.drawImage(this.video, 0, 0, targetW, targetH);
    }
    
    return this.canvas.toDataURL('image/jpeg', quality);
  }

  async loadDemoImage(url) {
    const res = await fetch(url);
    const blob = await res.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  loadFileAsDataUrl(file) {
    return new Promise((resolve, reject) => {
      if (!file) return reject(new Error('Файл не выбран'));
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}

window.CameraManager = CameraManager;
