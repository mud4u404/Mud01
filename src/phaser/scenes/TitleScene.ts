import Phaser from 'phaser';
import { Sfx } from '../../audio/Sfx';
import { GameState, resetGameState } from '../../core/gameState';
import { SaveSystem } from '../../simulation/systems/SaveSystem';
import { hud } from '../../ui/hud';

// ===== 标题场景 =====
export class TitleScene extends Phaser.Scene {
  constructor() { super('Title'); }

  create() {
    hud.hideAll();
    const W = this.scale.gameSize.width;
    const H = this.scale.gameSize.height;

    // ---- 背景 ----
    const bg = this.add.image(W / 2, H / 2, 'bg-title');
    bg.setScale(Math.max(W / bg.width, H / bg.height));
    this.tweens.add({
      targets: bg, y: H / 2 + 26, duration: 13000,
      yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
    });

    const shade = this.add.graphics().setDepth(1);
    shade.fillStyle(0x05070d, 0.38); shade.fillRect(0, 0, W, H);
    shade.fillStyle(0x05070d, 0.62); shade.fillRect(0, H * 0.52, W, H * 0.48);

    // ---- 升腾星屑 ----
    this.add.particles(0, 0, 'fx-dot', {
      x: { min: 0, max: W }, y: H + 30,
      lifespan: 9000, speedY: { min: -30, max: -10 }, speedX: { min: -8, max: 8 },
      scale: { min: 0.07, max: 0.2 }, alpha: { start: 0.75, end: 0 },
      tint: [0xfff6d8, 0x9fd0ff, 0xffe9a8], blendMode: Phaser.BlendModes.ADD,
      frequency: 240,
    }).setDepth(3);

    // ---- 流星 ----
    const meteor = () => {
      const x = Phaser.Math.Between(W * 0.35, W * 1.02);
      const y = Phaser.Math.Between(-30, H * 0.3);
      const dot = this.add.image(x, y, 'fx-glow')
        .setTint(0xffe9a8).setScale(0.26).setDepth(4)
        .setBlendMode(Phaser.BlendModes.ADD);
      this.tweens.add({
        targets: dot, x: x - 460, y: y + 300, alpha: 0, scale: 0.06,
        duration: 950, ease: 'Cubic.easeIn',
        onComplete: () => {
          dot.destroy();
          this.time.delayedCall(Phaser.Math.Between(2400, 5600), meteor);
        },
      });
    };
    this.time.delayedCall(1000, meteor);

    // ---- 标题 ----
    const title = this.add.text(W / 2, H * 0.3, '星陨幻世录', {
      fontFamily: '"Noto Serif SC", "Songti SC", serif',
      fontSize: '96px', color: '#f0e2b6',
      letterSpacing: 18,
    }).setOrigin(0.5).setDepth(6);
    title.setShadow(0, 0, '#d4af6a', 26, false, true);
    title.setScale(0.86);
    this.tweens.add({ targets: title, scale: 1, duration: 900, ease: 'Cubic.easeOut' });
    this.tweens.add({
      targets: title, alpha: 0.94, duration: 2600,
      yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
    });

    const sub = this.add.text(W / 2, H * 0.3 + 84, 'ASTRAL FANTASY CHRONICLE', {
      fontFamily: 'Georgia, serif', fontSize: '19px', color: '#8a93a8', letterSpacing: 12,
    }).setOrigin(0.5).setDepth(6);

    // 分隔饰线
    const deco = this.add.graphics().setDepth(6);
    deco.lineStyle(1.5, 0xd4af6a, 0.7);
    deco.lineBetween(W / 2 - 240, sub.y + 34, W / 2 - 16, sub.y + 34);
    deco.lineBetween(W / 2 + 16, sub.y + 34, W / 2 + 240, sub.y + 34);
    deco.fillStyle(0xd4af6a, 0.95);
    deco.fillTriangle(W / 2, sub.y + 28, W / 2 - 6, sub.y + 40, W / 2 + 6, sub.y + 40);

    // ---- 菜单 ----
    const hasSave = GameState.chapter > 1 || Object.keys(GameState.heroLevels).length > 0;
    let by = H * 0.615;
    if (hasSave) {
      this.menuButton(W / 2, by, `继续远征 · 第 ${GameState.chapter} 章`, () => this.startBattle(GameState.chapter));
      by += 96;
      this.menuButton(W / 2, by, '新 的 征 程', () => {
        resetGameState();
        SaveSystem.clear();
        this.startBattle(1);
      }, false);
    } else {
      this.menuButton(W / 2, by, '新 的 征 程', () => this.startBattle(1));
    }

    // ---- 页脚 ----
    this.add.text(W / 2, H - 46, '拖拽平移镜头 · 滚轮缩放 · M 静音 · ESC 取消', {
      fontSize: '14px', color: '#5d6678',
    }).setOrigin(0.5).setDepth(6);

    this.add.text(W / 2, H - 22, 'v0.1 · Phaser 3 战棋原型', {
      fontSize: '12px', color: '#3d4358',
    }).setOrigin(0.5).setDepth(6);

    // ENTER 快捷开始
    this.input.keyboard?.on('keydown-ENTER', () => {
      this.startBattle(hasSave ? GameState.chapter : 1);
    });
  }

  private startBattle(chapterId: number) {
    if (this.cameras.main.fadeEffect?.isRunning) return;
    this.cameras.main.fadeOut(560, 5, 7, 13);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      this.scene.start('Battle', { chapterId });
    });
  }

  private menuButton(x: number, y: number, label: string, onClick: () => void, primary = true) {
    const c = this.add.container(x, y).setDepth(7);
    const w = 380, h = 68;
    const g = this.add.graphics();
    const draw = (hover: boolean) => {
      g.clear();
      g.fillStyle(0x0c1120, hover ? 0.94 : 0.8);
      g.fillRoundedRect(-w / 2, -h / 2, w, h, 12);
      g.lineStyle(hover ? 2.5 : 1.5, hover ? 0xffd24a : 0xd4af6a, hover ? 1 : 0.55);
      g.strokeRoundedRect(-w / 2, -h / 2, w, h, 12);
      if (primary) {
        g.fillStyle(0xd4af6a, hover ? 0.16 : 0.07);
        g.fillRoundedRect(-w / 2 + 3, -h / 2 + 3, 5, h - 6, 3);
        g.fillRoundedRect(w / 2 - 8, -h / 2 + 3, 5, h - 6, 3);
      }
    };
    draw(false);
    const txt = this.add.text(0, 0, label, {
      fontFamily: '"Noto Serif SC", "Songti SC", serif',
      fontSize: '25px', color: '#e8eaf2', letterSpacing: 8,
    }).setOrigin(0.5);
    c.add([g, txt]);

    const zone = this.add.zone(x, y, w, h).setInteractive({ useHandCursor: true }).setDepth(8);
    zone.on('pointerover', () => {
      draw(true);
      txt.setColor('#ffd24a');
      this.tweens.add({ targets: c, scale: 1.045, duration: 130, ease: 'Cubic.easeOut' });
      Sfx.play('select');
    });
    zone.on('pointerout', () => {
      draw(false);
      txt.setColor('#e8eaf2');
      this.tweens.add({ targets: c, scale: 1, duration: 130 });
    });
    zone.on('pointerdown', () => {
      Sfx.play('confirm');
      onClick();
    });
  }
}
