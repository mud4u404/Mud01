import Phaser from 'phaser';
import { TILE_H, TILE_W } from '../../core/constants';

// ===== 启动场景：加载资源 + 程序化生成贴图 =====
export class BootScene extends Phaser.Scene {
  constructor() { super('Boot'); }

  preload() {
    const g = this.add.graphics();
    const { width, height } = this.scale.gameSize;
    g.fillStyle(0x0a0e1a, 1).fillRect(0, 0, width, height);
    g.destroy();

    const title = this.add.text(width / 2, height / 2 - 40, '星陨幻世录', {
      fontFamily: '"Noto Serif SC", serif', fontSize: '42px', color: '#e8d5a3'
    }).setOrigin(0.5);
    const sub = this.add.text(width / 2, height / 2 + 20, '载入星陨之力…', {
      fontSize: '16px', color: '#8a93a8'
    }).setOrigin(0.5);

    const barBg = this.add.rectangle(width / 2, height / 2 + 70, 420, 10, 0x1c2438).setStrokeStyle(1, 0x3a4664);
    const bar = this.add.rectangle(width / 2 - 209, height / 2 + 70, 0, 6, 0xd4af6a);
    bar.setOrigin(0, 0.5);

    this.load.on('progress', (v: number) => {
      bar.width = 418 * v;
    });

    // ---- 战场背景 ----
    this.load.image('bg-title', 'assets/bg-title.jpg');
    this.load.image('bg-plains', 'assets/bg-plains.jpg');
    this.load.image('bg-forest', 'assets/bg-forest.jpg');
    this.load.image('bg-fortress', 'assets/bg-fortress.jpg');

    // ---- 地形装饰 ----
    this.load.image('decor-tree', 'assets/decor-tree.png');
    this.load.image('decor-rock', 'assets/decor-rock.png');
    this.load.image('decor-wall', 'assets/decor-wall.png');

    // ---- 立绘 ----
    const portraits = ['ren', 'alice', 'roland', 'selena', 'kage', 'goblin', 'skeleton', 'orc', 'cultist', 'gargoyle', 'dark-priest', 'chaos-knight'];
    for (const p of portraits) this.load.image(`por-${p}`, `assets/portraits/${p}.png`);

    // ---- 战场单位 ----
    const sprites = ['ren', 'alice', 'roland', 'selena', 'kage', 'goblin', 'skeleton', 'orc', 'cultist', 'gargoyle', 'dark-priest', 'chaos-knight'];
    for (const s of sprites) this.load.image(`spr-${s}`, `assets/sprites/${s}.png`);

    this.load.on('complete', () => {
      this.generateTextures();
      title.destroy(); sub.destroy(); barBg.destroy(); bar.destroy();
      this.scene.start('Title');
    });

    // 资源缺失容错：加载失败时用占位贴图，保证游戏可运行
    this.load.on('loaderror', (file: Phaser.Loader.File) => {
      console.warn('[asset missing]', file.key, '→ using placeholder');
      this.pendingPlaceholders.add(file.key);
    });
  }

  private pendingPlaceholders = new Set<string>();

  private generateTextures() {
    // 任何缺失资源 → 生成占位图
    for (const key of this.pendingPlaceholders) {
      if (!this.textures.exists(key)) this.makePlaceholder(key);
    }

    const mk = (key: string, draw: (g: Phaser.GameObjects.Graphics) => void, w: number, h: number) => {
      if (this.textures.exists(key)) return;
      const g = this.make.graphics({ x: 0, y: 0 }, false);
      draw(g);
      g.generateTexture(key, w, h);
      g.destroy();
    };

    // 柔光圆
    mk('fx-glow', g => {
      for (let r = 64; r > 0; r -= 2) {
        const a = Math.pow(1 - r / 64, 2) * 255;
        g.fillStyle(Phaser.Display.Color.GetColor(255, 255, 255), a / 255);
        g.fillCircle(64, 64, r);
      }
    }, 128, 128);

    // 菱形火花
    mk('fx-spark', g => {
      g.fillStyle(0xffffff, 1);
      g.beginPath();
      g.moveTo(16, 0); g.lineTo(20, 12); g.lineTo(32, 16); g.lineTo(20, 20);
      g.lineTo(16, 32); g.lineTo(12, 20); g.lineTo(0, 16); g.lineTo(12, 12);
      g.closePath(); g.fillPath();
    }, 32, 32);

    // 小圆点
    mk('fx-dot', g => { g.fillStyle(0xffffff, 1); g.fillCircle(8, 8, 8); }, 16, 16);

    // 圆环
    mk('fx-ring', g => {
      g.lineStyle(6, 0xffffff, 1);
      g.strokeCircle(64, 64, 58);
    }, 128, 128);

    // 弧形斩击
    mk('fx-slash', g => {
      g.lineStyle(10, 0xffffff, 1);
      g.beginPath();
      g.arc(80, 80, 64, Phaser.Math.DegToRad(-60), Phaser.Math.DegToRad(60), false);
      g.strokePath();
      g.lineStyle(22, 0xffffff, 0.35);
      g.beginPath();
      g.arc(80, 80, 64, Phaser.Math.DegToRad(-55), Phaser.Math.DegToRad(55), false);
      g.strokePath();
    }, 160, 160);

    // 菱形格贴图（渐变 + 立体描边）
    const mkTile = (key: string, top: number, bottom: number, edge: number) => {
      const g = this.make.graphics({ x: 0, y: 0 }, false);
      const w = TILE_W, h = TILE_H;
      const pts = [w / 2, 2, w - 2, h / 2, w / 2, h - 2, 2, h / 2];
      // 主体渐变：手动分层
      for (let i = 0; i < 12; i++) {
        const t = i / 11;
        const col = Phaser.Display.Color.Interpolate.ColorWithColor(
          Phaser.Display.Color.IntegerToColor(top),
          Phaser.Display.Color.IntegerToColor(bottom), 11, i);
        const shrink = t * 3;
        const hh = (h - 4 - shrink * 2) / 12;
        g.fillStyle(Phaser.Display.Color.GetColor(col.r, col.g, col.b), 1);
        g.beginPath();
        // 每层一个扁菱形
        const cy = 2 + shrink + hh * i + hh / 2;
        const halfW = (w - 4) / 2 * (1 - Math.abs((cy - h / 2) / (h / 2)) * 0.98);
        const halfH = hh / 2 + 0.8;
        g.moveTo(w / 2, cy - halfH);
        g.lineTo(w / 2 + halfW, cy);
        g.lineTo(w / 2, cy + halfH);
        g.lineTo(w / 2 - halfW, cy);
        g.closePath(); g.fillPath();
      }
      // 高光边（左上）与阴影边（右下）
      g.lineStyle(2, edge, 0.9);
      g.beginPath();
      g.moveTo(w / 2, 2); g.lineTo(2, h / 2); g.lineTo(w / 2, h - 2); g.lineTo(w - 2, h / 2);
      g.closePath(); g.strokePath();
      g.lineStyle(2, 0xffffff, 0.28);
      g.beginPath(); g.moveTo(w / 2, 3); g.lineTo(3, h / 2); g.strokePath();
      g.generateTexture(key, w, h);
      g.destroy();
    };
    mkTile('tile-plain', 0x9fd08a, 0x5a9050, 0x3e7040);
    mkTile('tile-road', 0xd9c49a, 0xa3865e, 0x7c6544);
    mkTile('tile-forest', 0x63b06a, 0x2e6b44, 0x1f4d33);
    mkTile('tile-mountain', 0xb5a795, 0x6e6257, 0x4c4339);
    mkTile('tile-wall', 0x565a68, 0x2e3140, 0x1e2030);

    // 山体侧壁贴图（顶面 tile + 前侧两块深色面）
    mk('tile-mountain-side', g => {
      const w = TILE_W, h = TILE_H;
      const rise = 46;
      g.fillStyle(0x5a5148, 1);
      g.beginPath();
      g.moveTo(2, h / 2); g.lineTo(w / 2, h - 2); g.lineTo(w / 2, h - 2 + rise); g.lineTo(2, h / 2 + rise);
      g.closePath(); g.fillPath();
      g.fillStyle(0x433c35, 1);
      g.beginPath();
      g.moveTo(w - 2, h / 2); g.lineTo(w / 2, h - 2); g.lineTo(w / 2, h - 2 + rise); g.lineTo(w - 2, h / 2 + rise);
      g.closePath(); g.fillPath();
    }, TILE_W, TILE_H + 50);

    // 屏障侧壁
    mk('tile-wall-side', g => {
      const w = TILE_W, h = TILE_H;
      const rise = 60;
      g.fillStyle(0x3a3e50, 1);
      g.beginPath();
      g.moveTo(2, h / 2); g.lineTo(w / 2, h - 2); g.lineTo(w / 2, h - 2 + rise); g.lineTo(2, h / 2 + rise);
      g.closePath(); g.fillPath();
      g.fillStyle(0x262a38, 1);
      g.beginPath();
      g.moveTo(w - 2, h / 2); g.lineTo(w / 2, h - 2); g.lineTo(w / 2, h - 2 + rise); g.lineTo(w - 2, h / 2 + rise);
      g.closePath(); g.fillPath();
      // 砖缝
      g.lineStyle(1.5, 0x1a1d28, 0.8);
      for (let i = 1; i < 4; i++) {
        const yy = (h / 2) * (i / 4);
        g.beginPath(); g.moveTo(2 + yy, h / 2 + yy + rise * 0.5); g.lineTo(w / 2 + yy * 0.98, h - 2 + rise * 0.0); g.strokePath();
      }
    }, TILE_W, TILE_H + 64);
  }

  private makePlaceholder(key: string) {
    const isPortrait = key.startsWith('por-');
    const w = isPortrait ? 512 : 256;
    const h = isPortrait ? 512 : 384;
    const canvas = this.textures.createCanvas(key, w, h)!;
    const ctx = canvas.getContext();
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, '#3a4664');
    grad.addColorStop(1, '#141a2c');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#8a93a8';
    ctx.font = `${isPortrait ? 40 : 28}px sans-serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(key.replace(/^(por|spr)-/, ''), w / 2, h / 2);
    canvas.refresh();
  }
}
