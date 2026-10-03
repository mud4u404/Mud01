import Phaser from 'phaser';
import { WORLD_H, WORLD_W } from './Iso';

// ===== 战术镜头：拖拽平移 + 滚轮缩放 + 目标聚焦 =====
export class CameraRig {
  private scene: Phaser.Scene;
  private cam: Phaser.Cameras.Scene2D.Camera;
  private dragging = false;
  private dragStart = { x: 0, y: 0 };
  private scrollStart = { x: 0, y: 0 };
  private userInteracted = 0;
  zoom = 0.85;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.cam = scene.cameras.main;
    this.cam.setBounds(-160, -140, WORLD_W + 320, WORLD_H + 300);
    this.cam.setZoom(this.zoom);
    this.cam.centerOn(880, 420);

    const pad = scene.input.activePointer;

    scene.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      if (p.rightButtonReleased()) return;
      this.dragging = true;
      this.dragStart = { x: p.x, y: p.y };
      this.scrollStart = { x: this.cam.scrollX, y: this.cam.scrollY };
    });

    scene.input.on('pointermove', (p: Phaser.Input.Pointer) => {
      if (!this.dragging || !p.isDown) return;
      const dx = (p.x - this.dragStart.x) / this.cam.zoom;
      const dy = (p.y - this.dragStart.y) / this.cam.zoom;
      if (Math.abs(p.x - this.dragStart.x) + Math.abs(p.y - this.dragStart.y) > 6) {
        this.userInteracted = this.scene.time.now;
      }
      this.cam.setScroll(this.scrollStart.x - dx, this.scrollStart.y - dy);
    });

    const endDrag = () => { this.dragging = false; };
    scene.input.on('pointerup', endDrag);
    scene.input.on('gameout', endDrag);

    scene.input.on('wheel', (p: Phaser.Input.Pointer, _o: unknown, _dx: number, dy: number) => {
      const old = this.cam.zoom;
      const next = Phaser.Math.Clamp(old * (dy > 0 ? 0.92 : 1.08), 0.55, 1.6);
      this.zoom = next;
      this.cam.zoomTo(next, 90, 'Cubic.easeOut');
      this.userInteracted = this.scene.time.now;
    });
  }

  /** 聚焦世界坐标（不打断用户刚操作过的镜头） */
  focus(x: number, y: number, force = false) {
    if (!force && this.scene.time.now - this.userInteracted < 1600) return;
    this.scene.tweens.add({
      targets: this.cam,
      scrollX: x - this.cam.width / (2 * this.cam.zoom),
      scrollY: y - this.cam.height / (2 * this.cam.zoom),
      duration: 480, ease: 'Cubic.easeOut',
    });
  }

  punch(intensity = 0.006, duration = 140) {
    this.cam.shake(duration, intensity);
  }
}
