/**
 * Background System
 * Animated gradient orbs + floating dust particles + grain overlay.
 */

(function () {
  'use strict';

  // --- Canvas setup ---
  const canvas = document.createElement('canvas');
  canvas.id = 'dust-canvas';
  document.body.prepend(canvas);
  const ctx = canvas.getContext('2d');

  let W, H;
  const particles = [];
  const orbs = [];
  const PARTICLE_COUNT = 50;
  const ORB_COUNT = 5;
  let time = 0;
  let mouse = { x: -1000, y: -1000 };

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  // --- Gradient Orbs ---
  class Orb {
    constructor(index) {
      this.index = index;
      this.reset();
    }

    reset() {
      // Warm muted palette: dusty amber, burnt sienna, faded copper, deep mauve
      const palettes = [
        [180, 130, 80],   // dusty amber
        [140, 90, 70],    // burnt sienna
        [160, 120, 100],  // faded copper
        [120, 90, 130],   // deep mauve
        [100, 110, 140],  // slate blue
      ];
      this.color = palettes[this.index % palettes.length];
      this.baseX = Math.random() * W;
      this.baseY = Math.random() * H;
      this.radius = Math.random() * 300 + 200;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.2;
      this.phaseX = Math.random() * Math.PI * 2;
      this.phaseY = Math.random() * Math.PI * 2;
      this.freqX = Math.random() * 0.0003 + 0.0001;
      this.freqY = Math.random() * 0.0003 + 0.0001;
      this.pulseFreq = Math.random() * 0.0005 + 0.0002;
      this.opacity = Math.random() * 0.06 + 0.03;
    }

    update(t) {
      this.x = this.baseX + Math.sin(t * this.freqX + this.phaseX) * 200;
      this.y = this.baseY + Math.cos(t * this.freqY + this.phaseY) * 150;
      this.currentRadius = this.radius + Math.sin(t * this.pulseFreq) * 60;
      this.currentOpacity = this.opacity + Math.sin(t * this.pulseFreq * 0.7) * 0.015;

      // Subtle mouse repel
      const dx = this.x - mouse.x;
      const dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 400) {
        const force = (400 - dist) / 400 * 30;
        this.x += (dx / dist) * force;
        this.y += (dy / dist) * force;
      }
    }

    draw() {
      const [r, g, b] = this.color;
      const gradient = ctx.createRadialGradient(
        this.x, this.y, 0,
        this.x, this.y, this.currentRadius
      );
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${this.currentOpacity})`);
      gradient.addColorStop(0.4, `rgba(${r}, ${g}, ${b}, ${this.currentOpacity * 0.5})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

      ctx.beginPath();
      ctx.arc(this.x, this.y, this.currentRadius, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
    }
  }

  // --- Dust Particles ---
  class Particle {
    constructor() {
      this.reset(true);
    }

    reset(initial) {
      this.x = Math.random() * W;
      this.y = initial ? Math.random() * H : -10;
      this.size = Math.random() * 1.8 + 0.3;
      this.speedX = (Math.random() - 0.5) * 0.25;
      this.speedY = Math.random() * 0.15 + 0.03;
      this.opacity = Math.random() * 0.4 + 0.05;
      this.wobbleAmp = Math.random() * 0.4 + 0.1;
      this.wobbleFreq = Math.random() * 0.015 + 0.003;
      this.phase = Math.random() * Math.PI * 2;
      this.life = 0;
      // Slightly warmer tones
      const tones = [
        [210, 180, 140],
        [190, 165, 135],
        [230, 210, 180],
        [170, 155, 135],
        [200, 190, 170],
      ];
      this.color = tones[Math.floor(Math.random() * tones.length)];
    }

    update() {
      this.life++;
      this.x += this.speedX + Math.sin(this.life * this.wobbleFreq + this.phase) * this.wobbleAmp;
      this.y += this.speedY;

      const fadeIn = Math.min(this.life * 0.008, 1);
      const fadeOut = this.y > H * 0.85 ? 1 - (this.y - H * 0.85) / (H * 0.15) : 1;
      this.currentOpacity = this.opacity * fadeIn * Math.max(fadeOut, 0);

      if (this.y > H + 10 || this.x < -20 || this.x > W + 20) {
        this.reset(false);
      }
    }

    draw() {
      if (this.currentOpacity <= 0) return;
      const [r, g, b] = this.color;

      // Glow
      ctx.beginPath();
      const gradient = ctx.createRadialGradient(
        this.x, this.y, 0,
        this.x, this.y, this.size * 4
      );
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${this.currentOpacity * 0.6})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      ctx.fillStyle = gradient;
      ctx.arc(this.x, this.y, this.size * 4, 0, Math.PI * 2);
      ctx.fill();

      // Core
      ctx.beginPath();
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${this.currentOpacity})`;
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // --- Main loop ---
  function init() {
    resize();

    for (let i = 0; i < ORB_COUNT; i++) {
      orbs.push(new Orb(i));
    }
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle());
    }

    animate();
  }

  function animate() {
    time++;
    ctx.clearRect(0, 0, W, H);

    // Draw orbs (background layer)
    for (const orb of orbs) {
      orb.update(time);
      orb.draw();
    }

    // Draw particles (foreground layer)
    for (const p of particles) {
      p.update();
      p.draw();
    }

    requestAnimationFrame(animate);
  }

  // Mouse tracking for orb interaction
  document.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('resize', () => {
    resize();
    // Reposition orbs
    for (const orb of orbs) {
      orb.baseX = Math.random() * W;
      orb.baseY = Math.random() * H;
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
