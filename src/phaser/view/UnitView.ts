import Phaser from 'phaser';
import type { Terrain, TilePos, Unit } from '../../core/types';
import { depthOf, tileToWorld } from './Iso';

// ===== 战场单位视图 =====
export class UnitView {
  readonly container: Phaser.GameObjects.Container;
  private scene: Phaser.Scene;
  sprite: Phaser.GameObjects.Image;
  private shadow: Phaser.GameObjects.Ellipse;
  private ring: Phaser.GameObjects.Ellipse;
  private ringOuter: Phaser.GameObjects.Ellipse;
  private hpBg: Phaser.GameObjects.Rectangle;
  private hpFill: Phaser.GameObjects.Rectangle;
  private mpFill: Phaser.GameObjects.Rectangle;
  private nameText: Phaser.GameObjects.Text;
  private buffText: Phaser.GameObjects.Text;
  private activeArrow: Phaser.GameObjects.Text;
  unit: Unit;

  displayHp: number;
  private bobPhase = Math.random() * Math.PI * 2;
  private baseY = 0;

  constructor(scene: Phaser.Scene, unit: Unit, elevation: number) {
    this.scene = scene;
    this.unit = unit;
    this.displayHp = unit.hp;

    const w = tileToWorld(unit.pos);
    this.container = scene.add.container(w.x, w.y - elevation);
    this.container.setDepth(depthOf(unit.pos) + 8);

    const isBoss = !!unit.isBoss;
    const sc = isBoss ? 1.35 : 1;

    // 影子
    this.shadow = scene.add.ellipse(0, 4, isBoss ? 90 : 64, isBoss ? 40 : 28, 0x000000, 0.35);

    // 阵营环
    const ringColor = unit.faction === 'player' ? 0x3d8bff : 0xff4d5e;
    this.ring = scene.add.ellipse(0, 2, isBoss ? 96 : 70, isBoss ? 44 : 32).setStrokeStyle(3, ringColor, 0.9);
    this.ringOuter = scene.add.ellipse(0, 2, isBoss ? 112 : 82, isBoss ? 52 : 38).setStrokeStyle(1.5, ringColor, 0.35);

    // 本体立绘
    this.sprite = scene.add.image(0, -6, unit.spriteKey);
    const targetH = isBoss ? 190 : 132;
    const ratio = targetH / this.sprite.height;
    this.sprite.setScale(ratio * sc * 0.92);
    this.sprite.setOrigin(0.5, 0.95);

    // HP / MP 条
    const barY = -targetH - 14;
    this.hpBg = scene.add.rectangle(0, barY, isBoss ? 86 : 62, 8, 0x10141f, 0.9).setStrokeStyle(1, 0x000000, 0.6);
    this.hpFill = scene.add.rectangle(-(isBoss ? 42 : 30) + 1, barY, (isBoss ? 84 : 60) * Math.max(0, unit.hp / unit.stats.hp), 6, 0x54e08c);
    this.hpFill.setOrigin(0, 0.5);
    this.mpFill = scene.add.rectangle(-(isBoss ? 42 : 30) + 1, barY + 6, 0, 2.5, 0x5ea8f2);
    this.mpFill.setOrigin(0, 0.5);

    // 名字
    this.nameText = scene.add.text(0, barY - (isBoss ? 26 : 18), unit.name, {
      fontFamily: '"Noto Sans SC", sans-serif',
      fontSize: isBoss ? '17px' : '13px',
      color: unit.faction === 'player' ? '#9fd0ff' : '#ff9da6',
      stroke: '#05070d', strokeThickness: 3,
    }).setOrigin(0.5);

    // buff 图标行
    this.buffText = scene.add.text(0, barY + 12, '', {
      fontSize: '13px', color: '#ffe9a8', stroke: '#05070d', strokeThickness: 2,
    }).setOrigin(0.5);

    // 行动指示箭头
    this.activeArrow = scene.add.text(0, barY - (isBoss ? 52 : 38), '▼', {
      fontSize: '20px', color: '#ffd24a', stroke: '#05070d', strokeThickness: 3,
    }).setOrigin(0.5).setVisible(false);

    this.container.add([
      this.shadow, this.ring, this.ringOuter, this.sprite,
      this.hpBg, this.hpFill, this.mpFill, this.nameText, this.buffText, this.activeArrow,
    ]);

    this.baseY = w.y - elevation;
    this.refreshBars();
  }

  /** 更新位置（含地形抬升） */
  syncPosition(elevation: number) {
    const w = tileToWorld(this.unit.pos);
    this.baseY = w.y - elevation;
    this.container.setPosition(w.x, this.baseY);
    this.container.setDepth(depthOf(this.unit.pos) + 8);
  }

  setFacing(dx: number) {
    if (dx !== 0) this.sprite.setFlipX(dx < 0);
  }

  setActive(active: boolean) {
    this.activeArrow.setVisible(active);
    if (active) {
      this.scene.tweens.add({
        targets: this.activeArrow, y: this.activeArrow.y - 6, duration: 380,
        yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
      });
    } else {
      this.scene.tweens.killTweensOf(this.activeArrow);
    }
  }

  refreshBars() {
    const isBoss = !!this.unit.isBoss;
    const maxW = isBoss ? 84 : 60;
    const ratio = Math.max(0, this.displayHp / this.unit.stats.hp);
    this.hpFill.width = maxW * Math.min(1, ratio);
    const hpCol = ratio > 0.55 ? 0x54e08c : ratio > 0.28 ? 0xf7d95a : 0xff5a5a;
    this.hpFill.fillColor = hpCol;
    if (this.unit.faction === 'player') {
      this.mpFill.width = maxW * Math.min(1, this.unit.mp / Math.max(1, this.unit.stats.mp));
    }
    const buffIcons = this.unit.buffs.map(b => b.stat === 'atk' ? '⚔️' : b.stat === 'def' ? '🛡️' : '🎯').join(' ');
    this.buffText.setText(this.unit.enraged ? '☠️' + buffIcons : buffIcons);
    if (this.unit.enraged) this.sprite.setTint(0xffb0b0);
  }

  /** HP 动画过渡 */
  tweenHp(scene: Phaser.Scene) {
    scene.tweens.add({
      targets: this, displayHp: this.unit.hp, duration: 420, ease: 'Cubic.easeOut',
      onUpdate: () => this.refreshBars(),
    });
  }

  /** 待机浮动 */
  startIdle() {
    this.scene.tweens.add({
      targets: this.sprite, y: '-=3', duration: 1300 + Math.random() * 500,
      yoyo: true, repeat: -1, ease: 'Sine.easeInOut', delay: this.bobPhase * 200,
    });
  }

  stopIdle() { this.scene.tweens.killTweensOf(this.sprite); this.sprite.y = -6; }

  flash(color = 0xffffff) {
    this.sprite.setTintFill(color);
    this.scene.time.delayedCall(90, () => {
      this.sprite.clearTint();
      if (this.unit.enraged) this.sprite.setTint(0xffb0b0);
    });
  }

  /** 受击抖动 */
  shake() {
    const ox = this.container.x;
    this.scene.tweens.add({
      targets: this.container, x: { from: ox - 7, to: ox + 7 }, duration: 40,
      yoyo: true, repeat: 3, onComplete: () => this.container.x = ox,
    });
  }

  /** 死亡消散 */
  playDeath(): Promise<void> {
    return new Promise(resolve => {
      this.scene.tweens.killTweensOf(this.sprite);
      this.scene.tweens.add({
        targets: [this.sprite, this.ring, this.ringOuter, this.shadow, this.hpBg, this.hpFill, this.mpFill, this.nameText, this.buffText],
        alpha: 0, duration: 600, ease: 'Cubic.easeIn',
        onComplete: () => { this.container.destroy(); resolve(); },
      });
    });
  }

  destroy() { this.container.destroy(); }
}
