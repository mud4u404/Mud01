import Phaser from 'phaser';
import { TILE_H, TILE_RISE, TILE_W } from '../../core/constants';
import type { Terrain, TilePos } from '../../core/types';
import { diamondPoints, tileToWorld } from './Iso';

type RangeKind = 'move' | 'attack' | 'heal' | 'teleport';

// ===== 战场网格渲染器（等距菱形）=====
export class GridRenderer {
  private scene: Phaser.Scene;
  private tileLayer: Phaser.GameObjects.Container;
  private decorLayer: Phaser.GameObjects.Container;
  private highlightLayer: Phaser.GameObjects.Container;
  private pathLayer: Phaser.GameObjects.Container;
  private tiles: Array<{ pos: TilePos; terrain: Terrain; tinted: Phaser.GameObjects.Image }> = [];

  constructor(scene: Phaser.Scene, terrain: Terrain[][], cols: number, rows: number) {
    this.scene = scene;
    this.tileLayer = scene.add.container(0, 0).setDepth(0);
    this.decorLayer = scene.add.container(0, 0).setDepth(5);
    this.highlightLayer = scene.add.container(0, 0).setDepth(40);
    this.pathLayer = scene.add.container(0, 0).setDepth(45);

    // 网格底阴影（整体厚度感）
    const g = scene.make.graphics({ x: 0, y: 0 }, false);
    g.fillStyle(0x000000, 0.35);
    g.fillPoints(this.mapPoints(cols - 1, rows - 1).flat(), true);
    g.generateTexture('grid-shadow', 1900, 1100);
    g.destroy();
    scene.add.image(864, 130, 'grid-shadow').setDepth(-1).setAlpha(0.5);

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        this.addTile({ x, y }, terrain[y][x]);
      }
    }
  }

  private mapPoints(cx: number, cy: number): number[][] {
    // 生成从 (0,0) 到 (cx,cy) 的整体菱形轮廓（用于底阴影）
    const p0 = tileToWorld({ x: 0, y: 0 });
    const p1 = tileToWorld({ x: cx, y: 0 });
    const p2 = tileToWorld({ x: cx, y: cy });
    const p3 = tileToWorld({ x: 0, y: cy });
    return [[p0.x, p0.y + 24], [p1.x, p1.y + 24], [p2.x, p2.y + 24], [p3.x, p3.y + 24]];
  }

  private addTile(pos: TilePos, terrain: Terrain) {
    const { x, y } = tileToWorld(pos);
    const key = `tile-${terrain}`;
    const img = this.scene.add.image(x, y, key);
    // 每格轻微色差，打破平铺感
    const v = 0.92 + ((pos.x * 7 + pos.y * 13) % 5) * 0.035;
    img.setTint(Phaser.Display.Color.GetColor(
      Math.min(255, 255 * v), Math.min(255, 255 * (v * 0.99 + 0.01)), 255 * (2 - v) > 255 ? 255 : Math.min(255, 255 * (v + 0.06))
    ));
    this.tileLayer.add(img);
    this.tiles.push({ pos, terrain, tinted: img });

    // 山体与屏障：抬升 + 侧壁
    if (terrain === 'mountain') {
      const side = this.scene.add.image(x, y - TILE_RISE + TILE_H / 2 + 48, 'tile-mountain-side');
      side.setOrigin(0.5, 1);
      side.setDepth((pos.x + pos.y) * 10 + 2);
      this.tileLayer.add(side);
      img.y -= TILE_RISE;
      img.setDepth((pos.x + pos.y) * 10 + 3);
    } else if (terrain === 'wall') {
      const side = this.scene.add.image(x, y - 60 + TILE_H / 2 + 62, 'tile-wall-side');
      side.setOrigin(0.5, 1);
      side.setDepth((pos.x + pos.y) * 10 + 2);
      this.tileLayer.add(side);
      img.y -= 60;
      img.setDepth((pos.x + pos.y) * 10 + 3);
    } else {
      img.setDepth((pos.x + pos.y) * 10 + 1);
    }

    // 地形装饰
    if (terrain === 'forest' && this.scene.textures.exists('decor-tree')) {
      const n = 1 + ((pos.x * 3 + pos.y * 5) % 2);
      for (let i = 0; i < n; i++) {
        const tx = x + (((pos.x * 11 + pos.y * 17 + i * 29) % 30) - 15);
        const ty = y + (((pos.x * 13 + pos.y * 7 + i * 23) % 14) - 7);
        const s = this.scene.add.image(tx, ty + 18, 'decor-tree');
        const sc = 0.55 + ((pos.x + pos.y + i) % 3) * 0.07;
        s.setScale(sc).setOrigin(0.5, 0.92);
        s.setDepth((pos.x + pos.y) * 10 + 4 + i);
        this.decorLayer.add(s);
      }
    }
    if (terrain === 'mountain' && this.scene.textures.exists('decor-rock')) {
      const s = this.scene.add.image(x, y - TILE_RISE + 6, 'decor-rock');
      s.setScale(0.85 + ((pos.x + pos.y) % 3) * 0.08).setOrigin(0.5, 0.9);
      s.setDepth((pos.x + pos.y) * 10 + 4);
      this.decorLayer.add(s);
    }
  }

  tileElevation(pos: TilePos, terrain: Terrain): number {
    return terrain === 'mountain' ? TILE_RISE : terrain === 'wall' ? 60 : 0;
  }

  // ===== 范围高亮 =====
  clearHighlights() {
    this.highlightLayer.removeAll(true);
    this.pathLayer.removeAll(true);
  }

  showRange(pos: TilePos[], kind: RangeKind, occupiedByAlly: Set<string> = new Set()) {
    this.clearHighlights();
    const colors: Record<RangeKind, number> = {
      move: 0x3d8bff, attack: 0xff4d5e, heal: 0x54e08c, teleport: 0xb07ae0,
    };
    for (const p of pos) {
      const { x, y } = tileToWorld(p);
      const poly = this.scene.add.graphics();
      const c = colors[kind];
      poly.fillStyle(c, 0.28);
      poly.fillPoints(this.diamond(x, y), true);
      poly.lineStyle(2, c, 0.85);
      poly.strokePoints(this.diamond(x, y), true, true);
      poly.setDepth(40);
      this.highlightLayer.add(poly);
      // 呼吸动画
      this.scene.tweens.add({
        targets: poly, alpha: { from: 0.75, to: 1 }, duration: 650,
        yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
        delay: (p.x + p.y) * 35 % 300,
      });
      if (occupiedByAlly.has(`${p.x},${p.y}`)) {
        poly.setAlpha(0.35);
        this.scene.tweens.killTweensOf(poly);
      }
    }
  }

  private diamond(x: number, y: number): Phaser.Geom.Point[] {
    const pts = diamondPoints(x, y, TILE_W - 8, TILE_H - 4);
    const out: Phaser.Geom.Point[] = [];
    for (let i = 0; i < pts.length; i += 2) out.push(new Phaser.Geom.Point(pts[i], pts[i + 1]));
    return out;
  }

  /** 路径预览（起点→终点的足迹点） */
  showPath(path: TilePos[]) {
    this.pathLayer.removeAll(true);
    if (path.length < 2) return;
    for (let i = 1; i < path.length; i++) {
      const p = path[i];
      const { x, y } = tileToWorld(p);
      const dot = this.scene.add.image(x, y, 'fx-dot').setScale(0.9).setTint(0xffe9a8).setDepth(45).setAlpha(0.95);
      this.pathLayer.add(dot);
      this.scene.tweens.add({
        targets: dot, scale: { from: 0.6, to: 1.05 }, duration: 500,
        yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
      });
    }
    // 终点标记
    const last = path[path.length - 1];
    const { x: lx, y: ly } = tileToWorld(last);
    const ring = this.scene.add.image(lx, ly, 'fx-ring').setScale(0.42, 0.21).setTint(0xffe9a8).setDepth(46);
    this.pathLayer.add(ring);
    this.scene.tweens.add({
      targets: ring, scale: { from: 0.38, to: 0.5 }, scaleX: { from: 0.38, to: 0.46 }, duration: 600,
      yoyo: true, repeat: -1,
    });
  }

  /** 目标选中光标 */
  showTargetCursor(pos: TilePos, elevation: number) {
    const { x, y } = tileToWorld(pos);
    const cursor = this.scene.add.image(x, y - elevation, 'fx-ring').setScale(0.52, 0.26).setTint(0xffd24a).setDepth(90);
    this.pathLayer.add(cursor);
    this.scene.tweens.add({
      targets: cursor, scaleX: { from: 0.46, to: 0.58 }, scaleY: { from: 0.22, to: 0.3 },
      duration: 380, yoyo: true, repeat: -1, ease: 'Sine.easeInOut',
    });
    return cursor;
  }

  /** 章节开幕扫光 */
  revealSweep(delayMs = 0) {
    const cover = this.scene.add.rectangle(0, 0, 4000, 2400, 0x06080f, 1).setDepth(200).setScrollFactor(0).setOrigin(0);
    this.scene.tweens.add({
      targets: cover, alpha: 0, duration: 1400, delay: delayMs, ease: 'Cubic.easeOut',
      onComplete: () => cover.destroy(),
    });
  }
}
