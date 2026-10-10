// Minimal value tweens driven by the render loop.
export const ease = {
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  out: (t) => 1 - Math.pow(1 - t, 3),
  linear: (t) => t,
};

export class Tweens {
  constructor() { this.items = new Set(); }
  // Animate fn(t) for t in 0..1 over `ms`; resolves when done. A tween with the
  // same key replaces the running one.
  run(key, ms, fn, curve = ease.inOut) {
    for (const item of this.items) if (item.key === key) { this.items.delete(item); item.resolve(false); }
    return new Promise((resolve) => {
      if (ms <= 0) { fn(1); resolve(true); return; }
      this.items.add({ key, ms, fn, curve, start: performance.now(), resolve });
    });
  }
  get active() { return this.items.size > 0; }
  update(now) {
    for (const item of [...this.items]) {
      const t = Math.min(1, (now - item.start) / item.ms);
      item.fn(item.curve(t));
      if (t >= 1) { this.items.delete(item); item.resolve(true); }
    }
  }
}

export const lerp = (a, b, t) => a + (b - a) * t;
