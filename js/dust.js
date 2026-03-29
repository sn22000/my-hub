/**
 * Dust Particle System
 * Subtle floating dust particles with gentle drift and glow.
 */

(function () {
  const canvas = document.createElement('canvas');
  canvas.id = 'dust-canvas';
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');

  let W, H;
  const particles = [];
  const PARTICLE_COUNT = 60;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  class Particle {
    constructor() {
      this.reset(true);
    }

    reset(initial) {
      this.x = Math.random() * W;
      this.y = initial ? Math.random() * H : -10;
      this.size = Math.random() * 2 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = Math.random() * 0.2 + 0.05;
      this.opacity = Math.random() * 0.35 + 0.05;
      this.fadeSpeed = Math.random() * 0.002 + 0.001;
      this.wobbleAmp = Math.random() * 0.5 + 0.2;
      this.wobbleFreq = Math.random() * 0.02 + 0.005;
      this.phase = Math.random() * Math.PI * 2;
      this.life = 0;
      // Warm dusty tones
      const tones = [
        [200, 168, 130],  // warm sand
        [180, 160, 140],  // dust
        [220, 200, 170],  // light cream
        [160, 145, 125],  // muted brown
        [190, 180, 165],  // ash
      ];
      this.color = tones[Math.floor(Math.random() * tones.length)];
    }

    update() {
      this.life++;
      this.x += this.speedX + Math.sin(this.life * this.wobbleFreq + this.phase) * this.wobbleAmp;
      this.y += this.speedY;

      // Gentle fade in and out
      const fadeIn = Math.min(this.life * 0.01, 1);
      const fadeOut = this.y > H * 0.8 ? 1 - (this.y - H * 0.8) / (H * 0.2) : 1;
      this.currentOpacity = this.opacity * fadeIn * Math.max(fadeOut, 0);

      if (this.y > H + 10 || this.x < -20 || this.x > W + 20) {
        this.reset(false);
      }
    }

    draw() {
      if (this.currentOpacity <= 0) return;
      const [r, g, b] = this.color;

      // Soft glow
      ctx.beginPath();
      const gradient = ctx.createRadialGradient(
        this.x, this.y, 0,
        this.x, this.y, this.size * 3
      );
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${this.currentOpacity})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      ctx.fillStyle = gradient;
      ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${this.currentOpacity * 0.8})`;
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function init() {
    resize();
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle());
    }
    animate();
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    for (const p of particles) {
      p.update();
      p.draw();
    }
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
