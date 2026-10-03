// ===== 星陨幻世录 · 入口 =====
import Phaser from 'phaser';
import { CANVAS_H, CANVAS_W } from './core/constants';
import { BootScene } from './phaser/scenes/BootScene';
import { TitleScene } from './phaser/scenes/TitleScene';
import { BattleScene } from './phaser/scenes/BattleScene';
import { Sfx } from './audio/Sfx';
import { SaveSystem } from './simulation/systems/SaveSystem';
import { GameState } from './core/gameState';

// 恢复存档
const save = SaveSystem.load();
if (save) {
  GameState.chapter = save.chapter;
  GameState.heroLevels = save.heroLevels ?? {};
  GameState.inventory = save.inventory ?? [];
  GameState.gold = save.gold ?? 0;
}

// 首次交互解锁 Web Audio
const unlock = () => Sfx.resume();
window.addEventListener('pointerdown', unlock);
window.addEventListener('keydown', unlock);

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game-root',
  width: CANVAS_W,
  height: CANVAS_H,
  backgroundColor: '#05070d',
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  render: {
    antialias: true,
    powerPreference: 'high-performance',
  },
  scene: [BootScene, TitleScene, BattleScene],
});

/** HUD 层与画布严格对齐：固定 1600×900 设计尺寸，随画布等比缩放 */
function syncHud() {
  const canvas = document.querySelector<HTMLCanvasElement>('#game-root canvas');
  const hudLayer = document.getElementById('hud-layer');
  if (!canvas || !hudLayer) return;
  const r = canvas.getBoundingClientRect();
  if (r.width < 2) return;
  hudLayer.style.left = `${r.left}px`;
  hudLayer.style.top = `${r.top}px`;
  hudLayer.style.width = `${CANVAS_W}px`;
  hudLayer.style.height = `${CANVAS_H}px`;
  hudLayer.style.transformOrigin = '0 0';
  hudLayer.style.transform = `scale(${r.width / CANVAS_W})`;
}

game.events.once('ready', () => requestAnimationFrame(syncHud));
window.addEventListener('resize', () => requestAnimationFrame(syncHud));
