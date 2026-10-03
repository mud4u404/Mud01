import Phaser from 'phaser';
import type { Element, Skill } from '../../core/types';

const ELEMENT_COLORS: Record<string, number> = {
  fire: 0xff7a3d, ice: 0x7cd8ff, thunder: 0xfff06a, wind: 0x8af0a8,
  light: 0xffe9a8, dark: 0xb07ae0, none: 0xffffff, heal: 0x6af0a0,
};

// ===== 特效系统：粒子、伤害数字、元素爆发、震屏 =====
export class FXSystem {
  private scene: Phaser.Scene;
  private popLayer: Phaser.GameObjects.Container;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.popLayer = scene.add.container(0, 0).setDepth(300);
  }

  // ===== 伤害数字 =====
  damagePopup(x: number, y: number, amount: number, opts: { crit?: boolean; heal?: boolean; miss?: boolean; effective?: boolean } = {}) {
    let text: string;
    let color = '#ffffff';
    let size = 26;
    if (opts.miss) { text = 'MISS'; color = '#9aa4b8'; size = 22; }
    else if (opts.heal) { text = `+${amount}`; color = '#6af0a0'; }
    else { text = `${amount}`; color = opts.crit ? '#ffd24a' : '#ffffff'; size = opts.crit ? 36 : 26; }

    const t = this.scene.add.text(x, y, text, {
      fontFamily: '"Noto Sans SC", sans-serif', fontSize: `${size}px`,
      color, stroke: '#05070d', strokeThickness: 4, fontStyle: 'bold',
    }).setOrigin(0.5).setDepth(300).setScale(0.3);

    if (opts.effective) {
      const eff = this.scene.add.text(x, y - 30, '克制!', {
        fontSize: '15px', color: '#ffd24a', stroke: '#05070d', strokeThickness: 3, fontStyle: 'bold',
      }).setOrigin(0.5).setDepth(300);
      this.scene.tweens.add({
        targets: eff, y: y - 46, alpha: 0, duration: 800, ease: 'Cubic.easeOut',
        onComplete: () => eff.destroy(),
      });
    }

    this.popLayer.add(t);
    this.scene.tweens.add({
      targets: t, scale: opts.crit ? 1.35 : 1, duration: 130, ease: 'Back.easeOut',
      onComplete: () => {
        this.scene.tweens.add({
          targets: t, y: y - 44, alpha: 0, duration: 750, delay: 220, ease: 'Cubic.easeOut',
          onComplete: () => t.destroy(),
        });
      },
    });
    if (opts.crit) {
      const critLabel = this.scene.add.text(x, y - (size + 8), '会心一击!', {
        fontSize: '17px', color: '#ffd24a', stroke: '#7a3000', strokeThickness: 4, fontStyle: 'bold',
      }).setOrigin(0.5).setDepth(300);
      this.scene.tweens.add({
        targets: critLabel, angle: { from: -8, to: 4 }, duration: 100, yoyo: true, repeat: 2,
        onComplete: () => {
          this.scene.tweens.add({ targets: critLabel, alpha: 0, y: critLabel.y - 16, duration: 400, onComplete: () => critLabel.destroy() });
        },
      });
    }
  }

  expPopup(x: number, y: number, amount: number) {
    const t = this.scene.add.text(x, y, `EXP +${amount}`, {
      fontSize: '16px', color: '#b8c6ff', stroke: '#05070d', strokeThickness: 3,
    }).setOrigin(0.5).setDepth(300);
    this.scene.tweens.add({
      targets: t, y: y - 34, alpha: 0, duration: 900, ease: 'Cubic.easeOut',
      onComplete: () => t.destroy(),
    });
  }

  // ===== 元素爆发 =====
  burst(x: number, y: number, fx: Skill['fx'], element: Element) {
    const color = ELEMENT_COLORS[element] ?? 0xffffff;
    switch (fx) {
      case 'slash': this.slashBurst(x, y, color); break;
      case 'fire': this.fireBurst(x, y); break;
      case 'ice': this.iceBurst(x, y); break;
      case 'thunder': this.thunderStrike(x, y); break;
      case 'wind': this.windSwirl(x, y, color); break;
      case 'light': this.lightRays(x, y); break;
      case 'dark': this.darkPulse(x, y); break;
      case 'heal': this.healSparkle(x, y); break;
      case 'buff': this.buffAura(x, y, color); break;
    }
  }

  private slashBurst(x: number, y: number, color: number) {
    const s = this.scene.add.image(x, y - 30, 'fx-slash').setTint(color).setDepth(120).setScale(0.4).setAngle(-20);
    this.scene.tweens.add({ targets: s, scale: 1.5, angle: 24, alpha: 0, duration: 260, ease: 'Cubic.easeOut', onComplete: () => s.destroy() });
    const s2 = this.scene.add.image(x, y - 30, 'fx-slash').setTint(0xffffff).setDepth(121).setScale(0.3).setAngle(160).setFlipY(true);
    this.scene.tweens.add({ targets: s2, scale: 1.2, angle: 120, alpha: 0, duration: 300, delay: 60, onComplete: () => s2.destroy() });
    this.sparkBurst(x, y - 30, color, 14, 240);
    this.impactRing(x, y, color);
  }

  private fireBurst(x: number, y: number) {
    const flash = this.scene.add.image(x, y - 26, 'fx-glow').setTint(0xff9a4d).setScale(0.4).setDepth(119).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: flash, scale: 1.6, alpha: 0, duration: 340, onComplete: () => flash.destroy() });
    this.scene.add.particles(x, y - 10, 'fx-dot', {
      speed: { min: 60, max: 190 }, angle: { min: 220, max: 320 },
      scale: { start: 0.55, end: 0 }, lifespan: 700, quantity: 16,
      tint: [0xff7a3d, 0xffc23d, 0xff5252], blendMode: Phaser.BlendModes.ADD,
      gravityY: -140, emitting: false,
    }).explode(16);
    this.impactRing(x, y, 0xff8a4d);
  }

  private iceBurst(x: number, y: number) {
    this.scene.add.particles(x, y - 24, 'fx-spark', {
      speed: { min: 90, max: 230 }, angle: { min: 180, max: 360 },
      scale: { start: 0.6, end: 0 }, lifespan: 640, quantity: 14,
      tint: [0x9fe8ff, 0x5ec8f2, 0xffffff], blendMode: Phaser.BlendModes.ADD,
      gravityY: 420, rotate: { min: 0, max: 360 }, emitting: false,
    }).explode(14);
    const flash = this.scene.add.image(x, y - 24, 'fx-glow').setTint(0x9fe8ff).setScale(0.3).setDepth(119).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: flash, scale: 1.15, alpha: 0, duration: 300, onComplete: () => flash.destroy() });
  }

  private thunderStrike(x: number, y: number) {
    // 天雷：从天而降的锯齿闪电
    const g = this.scene.add.graphics().setDepth(150).setBlendMode(Phaser.BlendModes.ADD);
    let cx = x, cy = y - 420;
    const pts: number[] = [cx, cy];
    while (cy < y - 10) {
      cy += 55 + Math.random() * 35;
      cx = x + (Math.random() - 0.5) * 60;
      pts.push(cx, cy);
    }
    g.lineStyle(7, 0xfff6b0, 1);
    g.beginPath(); g.moveTo(pts[0], pts[1]);
    for (let i = 2; i < pts.length; i += 2) g.lineTo(pts[i], pts[i + 1]);
    g.strokePath();
    g.lineStyle(18, 0xfff06a, 0.35);
    g.beginPath(); g.moveTo(pts[0], pts[1]);
    for (let i = 2; i < pts.length; i += 2) g.lineTo(pts[i], pts[i + 1]);
    g.strokePath();
    this.scene.cameras.main.flash(90, 255, 250, 200);
    this.scene.tweens.add({ targets: g, alpha: 0, duration: 260, delay: 110, onComplete: () => g.destroy() });
    this.sparkBurst(x, y - 20, 0xfff06a, 12, 260);
  }

  private windSwirl(x: number, y: number, color: number) {
    const swirl = this.scene.add.particles(x, y - 20, 'fx-dot', {
      speed: { min: 120, max: 240 }, angle: { min: 0, max: 360 },
      scale: { start: 0.4, end: 0 }, lifespan: 600, quantity: 18,
      tint: [0x8af0a8, 0xd8ffb0, 0xffffff], blendMode: Phaser.BlendModes.ADD, emitting: false,
    });
    swirl.explode(18);
    const streak = this.scene.add.image(x, y - 24, 'fx-ring').setTint(color).setScale(0.2).setDepth(119).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: streak, scale: 1.1, alpha: 0, duration: 380, onComplete: () => streak.destroy() });
  }

  private lightRays(x: number, y: number) {
    const rays = this.scene.add.image(x, y - 40, 'fx-glow').setTint(0xffe9a8).setScale(0.5).setDepth(119).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: rays, scale: 2.0, alpha: 0, duration: 500, onComplete: () => rays.destroy() });
    this.scene.add.particles(x, y - 30, 'fx-spark', {
      speedY: { min: -160, max: -60 }, speedX: { min: -50, max: 50 },
      scale: { start: 0.45, end: 0 }, lifespan: 800, quantity: 12,
      tint: [0xffe9a8, 0xfff6d8, 0xffd24a], blendMode: Phaser.BlendModes.ADD, emitting: false,
    }).explode(12);
  }

  private darkPulse(x: number, y: number) {
    const pulse = this.scene.add.image(x, y - 20, 'fx-glow').setTint(0x8450c8).setScale(0.35).setDepth(118).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: pulse, scale: 1.8, alpha: 0, duration: 460, onComplete: () => pulse.destroy() });
    this.scene.add.particles(x, y - 14, 'fx-dot', {
      speed: { min: 20, max: 90 }, angle: { min: 0, max: 360 },
      scale: { start: 0.7, end: 0 }, lifespan: 900, quantity: 14,
      tint: [0x6a3da8, 0xb07ae0, 0x2a1244], alpha: 0.7, emitting: false,
    }).explode(14);
  }

  private healSparkle(x: number, y: number) {
    this.scene.add.particles(x, y, 'fx-spark', {
      speedY: { min: -120, max: -40 }, speedX: { min: -40, max: 40 },
      scale: { start: 0.4, end: 0 }, lifespan: 900, quantity: 12,
      tint: [0x6af0a0, 0xc8ffd8, 0xffffff], blendMode: Phaser.BlendModes.ADD, emitting: false,
    }).explode(12);
    const glow = this.scene.add.image(x, y - 30, 'fx-glow').setTint(0x6af0a0).setScale(0.3).setDepth(118).setBlendMode(Phaser.BlendModes.ADD);
    this.scene.tweens.add({ targets: glow, scale: 1.0, alpha: 0, duration: 600, onComplete: () => glow.destroy() });
  }

  private buffAura(x: number, y: number, color: number) {
    this.scene.add.particles(x, y - 10, 'fx-dot', {
      speedY: { min: -140, max: -80 }, speedX: { min: -24, max: 24 },
      scale: { start: 0.35, end: 0 }, lifespan: 700, quantity: 10,
      tint: color, blendMode: Phaser.BlendModes.ADD, emitting: false,
    }).explode(10);
  }

  sparkBurst(x: number, y: number, color: number, count = 10, speed = 220) {
    this.scene.add.particles(x, y, 'fx-spark', {
      speed: { min: speed * 0.4, max: speed }, angle: { min: 0, max: 360 },
      scale: { start: 0.5, end: 0 }, lifespan: 480, quantity: count,
      tint: color, blendMode: Phaser.BlendModes.ADD,
      gravityY: 300, emitting: false,
    }).explode(count);
  }

  impactRing(x: number, y: number, color: number) {
    const ring = this.scene.add.image(x, y - 8, 'fx-ring').setTint(color).setScale(0.15).setDepth(122).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0.9);
    this.scene.tweens.add({
      targets: ring, scaleX: 0.95, scaleY: 0.5, alpha: 0, duration: 320, ease: 'Cubic.easeOut',
      onComplete: () => ring.destroy(),
    });
  }

  /** 攻击冲撞闪光（近战冲刺落点） */
  dashGhost(x: number, y: number, spriteKey: string, flipX: boolean) {
    const ghost = this.scene.add.image(x, y - 62, spriteKey).setDepth(119).setAlpha(0.5).setFlipX(flipX);
    ghost.setScale(110 / ghost.height);
    this.scene.tweens.add({ targets: ghost, alpha: 0, scaleX: ghost.scaleX * 1.15, duration: 240, onComplete: () => ghost.destroy() });
  }

  /** 死亡粒子 */
  deathBurst(x: number, y: number, color: number) {
    this.scene.add.particles(x, y - 40, 'fx-dot', {
      speed: { min: 40, max: 160 }, angle: { min: 0, max: 360 },
      scale: { start: 0.5, end: 0 }, lifespan: 700, quantity: 18,
      tint: [color, 0xffffff], blendMode: Phaser.BlendModes.ADD,
      gravityY: -60, emitting: false,
    }).explode(18);
  }

  /** 升级金色爆发 */
  levelUpBurst(x: number, y: number) {
    this.scene.add.particles(x, y - 30, 'fx-spark', {
      speed: { min: 80, max: 220 }, angle: { min: 200, max: 340 },
      scale: { start: 0.55, end: 0 }, lifespan: 900, quantity: 22,
      tint: [0xffd24a, 0xfff6d8, 0xffffff], blendMode: Phaser.BlendModes.ADD,
      gravityY: -120, emitting: false,
    }).explode(22);
  }

  /** 屏幕震动 */
  shake(intensity = 0.008, duration = 160) {
    this.scene.cameras.main.shake(duration, intensity);
  }

  /** 打击停顿（时间缩放骤降再恢复） */
  hitStop(ms = 70) {
    this.scene.time.timeScale = 0.05;
    this.scene.time.delayedCall(ms / 0.05, () => { this.scene.time.timeScale = 1; });
  }

  // ===== 环境粒子 =====
  weather(kind: 'pollen' | 'fireflies' | 'embers') {
    const cam = this.scene.cameras.main;
    const conf: Phaser.Types.GameObjects.Particles.ParticleEmitterConfig =
      kind === 'pollen' ? {
        x: { min: 0, max: cam.width }, y: { min: 0, max: cam.height },
        lifespan: 6000, speedY: { min: -12, max: -4 }, speedX: { min: -10, max: 10 },
        scale: { min: 0.12, max: 0.3 }, alpha: { start: 0.5, end: 0 },
        tint: [0xfff6d8, 0xffe9a8], blendMode: Phaser.BlendModes.ADD,
        frequency: 320
      } : kind === 'fireflies' ? {
        x: { min: 0, max: cam.width }, y: { min: 0, max: cam.height },
        lifespan: 5000, speedY: { min: -18, max: 6 }, speedX: { min: -14, max: 14 },
        scale: { min: 0.1, max: 0.26 }, alpha: { start: 0, end: 0.75, ease: 'Sine.easeInOut' },
        tint: [0xa8ff9e, 0xd8ffb0], blendMode: Phaser.BlendModes.ADD,
        frequency: 420
      } : {
        x: { min: 0, max: cam.width }, y: -20,
        lifespan: 4200, speedY: { min: 40, max: 90 }, speedX: { min: -24, max: 24 },
        scale: { min: 0.1, max: 0.24 }, alpha: { start: 0.75, end: 0 },
        tint: [0xff7a3d, 0xffb46a], blendMode: Phaser.BlendModes.ADD,
        frequency: 200
      };
    this.scene.add.particles(0, 0, 'fx-dot', conf).setScrollFactor(0).setDepth(180);
  }

  /** 光照氛围：暗角 */
  vignette() {
    const g = this.scene.make.graphics({ x: 0, y: 0 }, false);
    const w = this.scene.scale.gameSize.width, h = this.scene.scale.gameSize.height;
    // 径向暗角近似：四角渐暗矩形
    g.fillStyle(0x06080f, 0.28);
    g.fillRect(0, 0, w, 90);
    g.fillRect(0, h - 110, w, 110);
    g.fillRect(0, 0, 130, h);
    g.fillRect(w - 130, 0, 130, h);
    g.generateTexture('vignette', w, h);
    g.destroy();
    this.scene.add.image(w / 2, h / 2, 'vignette').setScrollFactor(0).setDepth(170).setAlpha(0.85);
  }
}
