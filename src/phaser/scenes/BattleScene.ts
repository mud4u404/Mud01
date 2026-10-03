import Phaser from 'phaser';
import { GameState } from '../../core/gameState';
import { ELEMENT_INFO, TERRAIN_INFO, TILE_RISE } from '../../core/constants';
import type { BattleEvent, ChapterDef, Skill, Terrain, TilePos, Unit } from '../../core/types';
import { hud } from '../../ui/hud';
import { Sfx } from '../../audio/Sfx';
import { getChapter, TOTAL_CHAPTERS } from '../../simulation/content/story';
import { getSkill } from '../../simulation/content/skills';
import { getItem } from '../../simulation/content/items';
import { BattleSystem, type InventoryEntry } from '../../simulation/systems/BattleSystem';
import { CombatResolver } from '../../simulation/systems/CombatResolver';
import { SaveSystem } from '../../simulation/systems/SaveSystem';
import { CameraRig } from '../view/CameraRig';
import { FXSystem } from '../view/FXSystem';
import { GridRenderer } from '../view/GridRenderer';
import { UnitView } from '../view/UnitView';
import { tileToWorld, unitStandPos, worldToTile } from '../view/Iso';

type Mode = 'idle' | 'moveSelect' | 'command' | 'targetSelect' | 'busy';

interface PendingAction {
  kind: 'attack' | 'skill' | 'item' | 'teleport';
  skillId?: string;
  itemId?: string;
}

// ===== 主战场场景 =====
export class BattleScene extends Phaser.Scene {
  private chapter!: ChapterDef;
  private system!: BattleSystem;
  private grid!: GridRenderer;
  private fx!: FXSystem;
  private rig!: CameraRig;
  private views = new Map<string, UnitView>();

  private mode: Mode = 'idle';
  private pendingAction: PendingAction | null = null;
  private moveRange: Map<string, { cost: number; from: TilePos | null }> | null = null;
  private activeUnit: Unit | null = null;
  private playerResolve: (() => void) | null = null;

  private batchQueue: BattleEvent[] = [];
  private batching = false;
  private lastFaction: string = '';
  private hoverThrottle = 0;

  constructor() { super('Battle'); }

  init(data: { chapterId?: number }) {
    this.chapter = getChapter(data.chapterId ?? 1);
  }

  create() {
    this.input.removeAllListeners();
    this.views.clear();
    this.batchQueue = [];
    this.batching = false;
    this.mode = 'idle';
    this.lastFaction = '';

    this.cameras.main.setBackgroundColor('#080b14');
    hud.hideAll();

    this.system = new BattleSystem(
      this.chapter.mapId, this.chapter.roster,
      GameState.heroLevels, GameState.inventory
    );
    this.system.on(e => { if (this.batching) this.batchQueue.push(e); });

    // ---- 背景视差 ----
    const bg = this.add.image(900, 260, this.system.mapDef.bgKey).setDepth(-10).setScrollFactor(0.25);
    const s = Math.max(2600 / bg.width, 1500 / bg.height);
    bg.setScale(s);
    this.tweens.add({ targets: bg, y: 285, duration: 9000, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

    // ---- 网格 / 单位 / 特效 / 镜头 ----
    this.grid = new GridRenderer(this, this.system.terrain, this.system.mapDef.cols, this.system.mapDef.rows);
    this.fx = new FXSystem(this);
    this.rig = new CameraRig(this);
    this.fx.weather(this.system.mapDef.weather);
    this.fx.vignette();

    for (const u of this.system.units) {
      const elev = this.elevOf(u.pos);
      this.views.set(u.id, new UnitView(this, u, elev));
    }
    this.views.forEach(v => v.startIdle());

    // ---- 输入 ----
    this.input.on('pointerup', (p: Phaser.Input.Pointer) => {
      if (p.getDuration() > 420) return; // 长按拖拽不触发点击
      if (Math.abs(p.x - p.downX) + Math.abs(p.y - p.downY) > 12) return;
      if (hud.isDialogueActive()) { hud.advanceDialogue(); return; } // 对话中：画布点击也推进
      this.handleClick(p);
    });
    this.input.on('pointermove', (p: Phaser.Input.Pointer) => this.handleHover(p));
    this.input.keyboard?.on('keydown-ESC', () => this.handleCancel());
    this.input.keyboard?.on('keydown-M', () => hud.toggleMute());

    hud.showObjective(this.chapter);
    hud.setMuteState();
    this.grid.revealSweep();

    this.introFlow();
  }

  private elevOf(p: TilePos): number {
    const t = this.system.terrainAt(p);
    return t === 'mountain' ? TILE_RISE : t === 'wall' ? 60 : 0;
  }

  // ================= 开场 =================
  private async introFlow() {
    await this.wait(500);
    await hud.showChapterBanner(this.chapter);
    // 镜头扫过战场
    this.rig.focus(700, 300, true);
    await this.wait(900);
    this.rig.focus(880, 430, true);
    await this.wait(700);
    await new Promise<void>(res => hud.showDialogue(this.chapter.introDialogue, () => res()));

    hud.renderTurnOrder(this.system.getUpcoming(9), '', this.system.round);
    this.system.startBattle();
    this.runTurnLoop();
  }

  // ================= 回合主循环 =================
  private async runTurnLoop() {
    await this.wait(250);
    while (this.system.phase === 'battle') {
      const unit = this.system.currentUnit;
      if (!unit) break;
      await this.beginTurn(unit);
      if (unit.faction === 'player') await this.playerTurn(unit);
      else await this.enemyTurn(unit);
      if (this.system.phase !== 'battle') break;
      this.system.endUnitTurn(unit.id);
      await this.wait(100);
    }
    if (this.system.phase === 'victory') this.onVictory();
    else if (this.system.phase === 'defeat') this.onDefeat();
  }

  private async beginTurn(unit: Unit) {
    this.views.forEach(v => v.setActive(false));
    this.views.get(unit.id)?.setActive(true);
    this.activeUnit = unit;
    hud.renderTurnOrder(this.system.getUpcoming(9), unit.id, this.system.round);

    const w = tileToWorld(unit.pos);
    this.rig.focus(w.x, w.y - 40);

    if (unit.faction !== this.lastFaction) {
      this.lastFaction = unit.faction;
      Sfx.play('turn');
      await hud.showTurnBanner(unit.faction === 'player' ? '我方行动' : '敌方行动',
        unit.faction === 'player' ? '#3d8bff' : '#ff4d5e');
    }
  }

  // ================= 玩家回合 =================
  private playerTurn(unit: Unit): Promise<void> {
    return new Promise<void>(resolve => {
      this.playerResolve = resolve;
      this.enterMoveSelect(unit);
    });
  }

  private finishPlayerTurn() {
    const r = this.playerResolve;
    this.playerResolve = null;
    this.mode = 'idle';
    this.grid.clearHighlights();
    hud.closeMenus();
    hud.hideUnitCard();
    r?.();
  }

  private enterMoveSelect(unit: Unit) {
    this.mode = 'moveSelect';
    this.moveRange = this.system.getMoveRange(unit.id);
    const tiles: TilePos[] = [];
    const occupied = new Set<string>();
    for (const [k, v] of this.moveRange) {
      if (v.cost === Infinity) continue;
      const pos = { x: +k.split(',')[0], y: +k.split(',')[1] };
      tiles.push(pos);
      const other = this.system.unitAtPos(pos);
      if (other && other.id !== unit.id) occupied.add(k);
    }
    this.grid.showRange(tiles, 'move', occupied);
    hud.showHint('点击蓝色区域移动 · 点击行动单位打开菜单 · 右键取消');
  }

  private openCommandMenu(unit: Unit) {
    this.mode = 'command';
    this.grid.clearHighlights();
    const w = tileToWorld(unit.pos);
    const cam = this.cameras.main;
    const sx = (w.x - cam.scrollX) * cam.zoom;
    const sy = (w.y - this.elevOf(unit.pos) - 100 - cam.scrollY) * cam.zoom;

    const canAttack = this.system.getTargetsInSkillRange(unit.id).length > 0;
    const canSkill = unit.skills.some(sid => {
      const sk = getSkill(sid);
      return this.system.canUseSkill(unit, sid) && sk.shape.kind !== 'self';
    }) || unit.skills.some(sid => {
      const sk = getSkill(sid);
      return this.system.canUseSkill(unit, sid) && sk.shape.kind === 'self';
    });
    const canItem = this.system.inventory.length > 0;

    hud.openCommandMenu({
      x: sx, y: sy,
      canAttack, canSkill, canItem,
      canUndo: unit.hasMoved && !unit.hasActed,
      onAttack: () => this.enterTargetSelect({ kind: 'attack' }),
      onSkill: () => hud.openSkillMenu(unit, this.system, (sid) => this.enterTargetSelect({ kind: 'skill', skillId: sid }), () => this.openCommandMenu(unit)),
      onItem: () => hud.openItemMenu(this.system.inventory, (iid) => this.enterTargetSelect({ kind: 'item', itemId: iid }), () => this.openCommandMenu(unit)),
      onWait: () => { this.system.wait(unit.id); this.finishPlayerTurn(); },
      onUndo: () => {
        if (this.system.undoMove(unit.id)) {
          this.views.get(unit.id)?.syncPosition(this.elevOf(unit.pos));
          this.enterMoveSelect(unit);
        }
      },
    });
  }

  // ================= 目标选择 =================
  private enterTargetSelect(action: PendingAction) {
    const unit = this.activeUnit!;
    this.mode = 'targetSelect';
    this.pendingAction = action;
    hud.closeMenus();

    if (action.kind === 'attack') {
      const tiles = this.system.getSkillTargetTiles(unit.id).filter(t => {
        const u = this.system.unitAtPos(t);
        return u && u.faction !== unit.faction;
      });
      this.grid.showRange(tiles, 'attack');
      hud.showHint('选择攻击目标 · 点击敌人查看战斗预测');
    } else if (action.kind === 'skill') {
      const skill = getSkill(action.skillId!);
      if (skill.shape.kind === 'self') {
        // 自身增益：直接确认
        hud.showSkillConfirm(unit, skill, () => {
          this.executeBatch(() => this.system.useBuffSkill(unit.id, skill.id));
          this.finishPlayerTurn();
        }, () => this.openCommandMenu(unit));
        return;
      }
      if (skill.id === 'kag_shadow_step') {
        const tiles: TilePos[] = [];
        for (let y = 0; y < this.system.mapDef.rows; y++) for (let x = 0; x < this.system.mapDef.cols; x++) {
          const d = Math.abs(x - unit.pos.x) + Math.abs(y - unit.pos.y);
          if (d >= 1 && d <= skill.range && !this.system.unitAtPos({ x, y }) && this.system.terrainAt({ x, y }) !== 'wall') tiles.push({ x, y });
        }
        this.grid.showRange(tiles, 'teleport');
        hud.showHint('选择瞬步落点');
        return;
      }
      if (skill.shape.kind === 'line') {
        const tiles = this.system.getLineTargetTiles(unit.id, skill);
        this.grid.showRange(tiles, 'attack');
        hud.showHint('选择直线方向释放');
        return;
      }
      const isAlly = skill.damageType === 'heal' || (skill.damageType === 'buff' && skill.shape.kind === 'ally');
      const tiles = this.system.getSkillTargetTiles(unit.id, skill.id).filter(t => {
        const u = this.system.unitAtPos(t);
        if (skill.shape.kind === 'blast') return true;
        return isAlly ? (u && u.faction === unit.faction) : (u && u.faction !== unit.faction);
      });
      this.grid.showRange(tiles, isAlly ? 'heal' : 'attack');
      hud.showHint(isAlly ? '选择友方目标' : '选择技能目标');
    } else if (action.kind === 'item') {
      const tiles = this.system.getSkillTargetTiles(unit.id).filter(t => {
        const u = this.system.unitAtPos(t);
        return u && u.faction === unit.faction;
      });
      this.grid.showRange(tiles, 'heal');
      hud.showHint('选择道具目标');
    }
  }

  // ================= 点击 / 悬停 =================
  private handleClick(p: Phaser.Input.Pointer) {
    if (this.mode === 'idle' || this.mode === 'busy') return;
    const unit = this.pickUnit(p);
    const tile = this.pickTile(p);
    const act = this.activeUnit!;
    const action = this.pendingAction;

    if (this.mode === 'moveSelect') {
      if (unit && unit.id === act.id) { this.openCommandMenu(act); return; }
      if (tile && this.moveRange) {
        const key = `${tile.x},${tile.y}`;
        const node = this.moveRange.get(key);
        if (node && node.cost !== Infinity && !this.system.unitAtPos(tile)) {
          const path = this.system.buildPath(act.id, this.moveRange, key);
          if (path) { void this.doMove(act, path); return; }
        }
      }
      if (unit) hud.showUnitCard(unit, this.system.terrainAt(unit.pos));
      return;
    }

    if (this.mode === 'targetSelect' && action) {
      if (!unit && !tile) return;

      if (action.kind === 'attack') {
        if (unit && unit.faction !== act.faction && this.inSkillRange(act, unit.pos, undefined)) {
          this.confirmAttack(act, unit, undefined);
        }
        return;
      }
      if (action.kind === 'skill') {
        const skill = getSkill(action.skillId!);
        if (skill.id === 'kag_shadow_step') {
          if (tile && !this.system.unitAtPos(tile) && this.inSkillRange(act, tile, skill)) {
            this.executeBatch(() => this.system.useTeleportSkill(act.id, skill.id, tile));
            this.views.get(act.id)?.syncPosition(this.elevOf(tile));
            this.finishPlayerTurn();
          }
          return;
        }
        if (skill.shape.kind === 'line') {
          if (tile && this.inSkillRange(act, tile, skill)) {
            this.executeBatch(() => this.system.lineAttack(act.id, tile, skill.id));
            this.finishPlayerTurn();
          }
          return;
        }
        if (skill.shape.kind === 'blast') {
          if (tile && this.inSkillRange(act, tile, skill)) {
            const affected = this.system.resolveSkillAffected(act, tile, skill);
            hud.showBlastConfirm(act, skill, affected, this.system, () => {
              this.executeBatch(() => this.system.areaAttack(act.id, tile, skill.id));
              this.finishPlayerTurn();
            }, () => this.enterTargetSelect(action));
          }
          return;
        }
        const isAlly = skill.damageType === 'heal' || (skill.damageType === 'buff' && skill.shape.kind === 'ally');
        if (unit && this.inSkillRange(act, unit.pos, skill) && (isAlly ? unit.faction === act.faction : unit.faction !== act.faction)) {
          if (isAlly) {
            const amount = skill.damageType === 'heal'
              ? CombatResolver.healAmount(act, skill)
              : 0;
            hud.showForecast(act, unit, skill, amount, () => {
              this.executeBatch(() => this.system.useHealSkill(act.id, skill.id, unit.id));
              this.finishPlayerTurn();
            }, () => this.enterTargetSelect(action));
          } else {
            this.confirmAttack(act, unit, skill);
          }
        }
        return;
      }
      if (action.kind === 'item') {
        const item = getItem(action.itemId!);
        if (unit && unit.faction === act.faction && this.inSkillRange(act, unit.pos, undefined)) {
          hud.showItemConfirm(act, unit, item, () => {
            this.executeBatch(() => this.system.useItem(act.id, item.id, unit.id));
            this.finishPlayerTurn();
          }, () => this.enterTargetSelect(action));
        }
        return;
      }
    }
  }

  private confirmAttack(act: Unit, target: Unit, skill: Skill | undefined) {
    const fc = CombatResolver.forecast(act, target, this.system.terrainAt(target.pos), skill);
    hud.showForecast(act, target, skill, fc, () => {
      this.executeBatch(() => this.system.attack(act.id, target.id, skill?.id));
      this.finishPlayerTurn();
    }, () => this.enterTargetSelect(this.pendingAction!));
  }

  private inSkillRange(act: Unit, pos: TilePos, skill?: Skill): boolean {
    const range = skill ? skill.range : this.system.basicAttackRange(act);
    return Math.abs(act.pos.x - pos.x) + Math.abs(act.pos.y - pos.y) <= range;
  }

  private async doMove(unit: Unit, path: TilePos[]) {
    this.mode = 'busy';
    this.grid.clearHighlights();
    await this.executeBatch(() => this.system.moveUnit(unit.id, path));
    this.openCommandMenu(unit);
  }

  private handleHover(p: Phaser.Input.Pointer) {
    const now = this.time.now;
    if (now - this.hoverThrottle < 70) return;
    this.hoverThrottle = now;
    if (this.mode === 'idle' || this.mode === 'busy') return;
    const unit = this.pickUnit(p);
    if (unit) hud.showUnitCard(unit, this.system.terrainAt(unit.pos));
    else hud.hideUnitCard();

    // 移动路径预览
    if (this.mode === 'moveSelect' && this.moveRange) {
      const tile = this.pickTile(p);
      if (tile) {
        const key = `${tile.x},${tile.y}`;
        const node = this.moveRange.get(key);
        if (node && node.cost !== Infinity && !this.system.unitAtPos(tile)) {
          const path = this.system.buildPath(this.activeUnit!.id, this.moveRange, key);
          if (path) { this.grid.showPath(path); return; }
        }
      }
      this.grid.showPath([]);
    }
  }

  private handleCancel() {
    if (this.mode === 'targetSelect') {
      this.pendingAction = null;
      this.openCommandMenu(this.activeUnit!);
      Sfx.play('cancel');
    } else if (this.mode === 'command') {
      const u = this.activeUnit!;
      if (u.hasMoved && !u.hasActed) this.enterMoveSelect(u);
    }
  }

  // ================= 拾取 =================
  private pickUnit(p: Phaser.Input.Pointer): Unit | null {
    const wp = this.cameras.main.getWorldPoint(p.x, p.y);
    let best: Unit | null = null;
    let bestD = Infinity;
    for (const u of this.system.aliveUnits) {
      const v = this.views.get(u.id);
      if (!v) continue;
      const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
      const halfW = 46, top = w.y - (u.isBoss ? 200 : 140), bottom = w.y + 14;
      if (wp.x >= w.x - halfW && wp.x <= w.x + halfW && wp.y >= top && wp.y <= bottom) {
        const d = Math.abs(wp.x - w.x) + Math.abs(wp.y - (top + bottom) / 2);
        if (d < bestD) { bestD = d; best = u; }
      }
    }
    return best;
  }

  private pickTile(p: Phaser.Input.Pointer): TilePos | null {
    const wp = this.cameras.main.getWorldPoint(p.x, p.y);
    let tile = worldToTile(wp.x, wp.y);
    if (!this.inBounds(tile)) return null;
    // 山体贴图抬升修正
    if (this.system.terrainAt(tile) !== 'mountain') {
      const cand = { x: tile.x + 1, y: tile.y + 1 };
      if (this.inBounds(cand) && this.system.terrainAt(cand) === 'mountain') {
        const c = tileToWorld(cand);
        if (wp.y < c.y - 6) tile = cand;
      }
    }
    return this.inBounds(tile) ? tile : null;
  }

  private inBounds(t: TilePos): boolean {
    return t.x >= 0 && t.y >= 0 && t.x < this.system.mapDef.cols && t.y < this.system.mapDef.rows;
  }

  // ================= 敌方回合 =================
  private async enemyTurn(unit: Unit) {
    this.mode = 'busy';
    this.grid.clearHighlights();
    hud.closeMenus();
    hud.showHint(`${unit.name} 正在行动…`);
    await this.wait(420);

    const plan = this.system.planEnemyTurn(unit.id);
    await this.executeBatch(() => this.system.executeAIPlan(plan, unit.id));
    if (this.system.phase === 'battle' && !unit.hasActed && unit.alive) {
      this.system.wait(unit.id);
    }
    hud.showHint('');
  }

  // ================= 事件批处理动画 =================
  private async executeBatch(fn: () => void) {
    this.batching = true;
    fn();
    this.batching = false;
    const events = this.batchQueue;
    this.batchQueue = [];
    for (const e of events) {
      if (this.system.phase !== 'battle' && e.type !== 'death' && e.type !== 'hit') continue;
      await this.animateEvent(e);
    }
    await this.settleUnits();
  }

  private view(id: string): UnitView | undefined { return this.views.get(id); }

  private async animateEvent(e: BattleEvent): Promise<void> {
    switch (e.type) {
      case 'move': {
        const v = this.view(e.unitId);
        if (!v) return;
        v.stopIdle();
        Sfx.play('move');
        for (let i = 1; i < e.path.length; i++) {
          const from = e.path[i - 1], to = e.path[i];
          v.setFacing(to.x - from.x);
          const target = unitStandPos(to, this.system.terrainAt(to));
          await new Promise<void>(res => {
            this.tweens.add({
              targets: v.container, x: target.x, y: target.y,
              duration: 165, ease: 'Sine.easeInOut',
              onComplete: () => {
                v.container.setDepth((to.x + to.y) * 10 + 8);
                // 尘土
                this.fx.sparkBurst(target.x, target.y, 0xc9b48a, 3, 60);
                res();
              },
            });
          });
        }
        v.startIdle();
        hud.renderTurnOrder(this.system.getUpcoming(9), this.activeUnit?.id ?? '', this.system.round);
        return;
      }
      case 'attackStart': {
        const av = this.view(e.attackerId);
        const atkUnit = this.system.unitById(e.attackerId)!;
        const tv = e.targetId ? this.view(e.targetId) : undefined;
        if (!av) return;
        const skill = e.skillId ? getSkill(e.skillId) : undefined;
        av.setFacing(tv ? Math.sign(tv.container.x - av.container.x) : av.container.x);

        if (skill && atkUnit.faction === 'player') {
          Sfx.play(skill.fx === 'heal' || skill.fx === 'buff' ? 'buff' : 'confirm');
          await hud.showCutIn(atkUnit, skill);
        }

        if (tv) {
          const dist = Phaser.Math.Distance.Between(av.container.x, av.container.y, tv.container.x, tv.container.y);
          const isMelee = !skill || skill.fx === 'slash' || skill.fx === 'fire' || skill.fx === 'dark' || skill.fx === 'thunder' && skill.range <= 1;
          if (isMelee && dist < 200) {
            // 冲刺
            const dx = (tv.container.x - av.container.x) * 0.45;
            const dy = (tv.container.y - av.container.y) * 0.45;
            this.fx.dashGhost(av.container.x, av.container.y, atkUnit.spriteKey, av.sprite.flipX);
            await new Promise<void>(res => {
              this.tweens.add({
                targets: av.container, x: av.container.x + dx, y: av.container.y + dy,
                duration: 130, ease: 'Cubic.easeIn', onComplete: () => res(),
              });
            });
          } else {
            // 远程施法闪
            av.flash(0xffffff);
            const glow = this.add.image(av.container.x, av.container.y - 60, 'fx-glow')
              .setTint(ELEMENT_INFO[skill?.element ?? atkUnit.element].color)
              .setScale(0.35).setDepth(119).setBlendMode(Phaser.BlendModes.ADD);
            this.tweens.add({ targets: glow, scale: 0.8, alpha: 0, duration: 300, onComplete: () => glow.destroy() });
            await this.wait(160);
          }
        }
        return;
      }
      case 'hit': {
        const tv = this.view(e.targetId);
        const av = this.view(e.attackerId);
        const atkUnit = this.system.unitById(e.attackerId)!;
        if (tv) {
          const w = unitStandPos(this.system.unitById(e.targetId)!.pos, this.system.terrainAt(this.system.unitById(e.targetId)!.pos));
          tv.flash(0xff8888);
          tv.shake();
          this.fx.burst(w.x, w.y, e.fx, e.element);
          this.fx.damagePopup(w.x, w.y - 90, e.damage, { crit: e.crit, effective: e.effective });
          tv.tweenHp(this);
          if (e.crit) { this.fx.shake(0.011, 240); this.fx.hitStop(70); Sfx.play('crit'); }
          else { this.fx.shake(0.006, 140); Sfx.play('hit'); }
          Sfx.play(e.fx === 'heal' ? 'heal' : e.fx as 'slash');
          await this.wait(e.crit ? 500 : 360);
        }
        if (av && e.lethal) { /* 击杀者小跳 */ }
        return;
      }
      case 'miss': {
        const tv = this.view(e.targetId);
        if (tv) {
          const u = this.system.unitById(e.targetId)!;
          const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
          this.fx.damagePopup(w.x, w.y - 90, 0, { miss: true });
        }
        Sfx.play('cancel');
        await this.wait(280);
        return;
      }
      case 'heal': {
        const tv = this.view(e.targetId);
        if (tv) {
          const u = this.system.unitById(e.targetId)!;
          const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
          this.fx.burst(w.x, w.y, 'heal', 'light');
          this.fx.damagePopup(w.x, w.y - 90, e.amount, { heal: true });
          tv.tweenHp(this);
          Sfx.play('heal');
          await this.wait(420);
        }
        return;
      }
      case 'buff': {
        const tv = this.view(e.targetId);
        if (tv) {
          const u = this.system.unitById(e.targetId)!;
          const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
          this.fx.burst(w.x, w.y, 'buff', 'light');
          const label = e.buff.stat === 'atk' ? '攻击提升' : e.buff.stat === 'def' ? '防御提升' : '会心提升';
          this.fx.damagePopup(w.x, w.y - 110, 0, { miss: false });
          const t = this.add.text(w.x, w.y - 110, `↑ ${label}`, {
            fontSize: '16px', color: '#ffe9a8', stroke: '#05070d', strokeThickness: 3, fontStyle: 'bold',
          }).setOrigin(0.5).setDepth(300);
          this.tweens.add({ targets: t, y: t.y - 22, alpha: 0, duration: 700, onComplete: () => t.destroy() });
          tv.refreshBars();
          Sfx.play('buff');
          await this.wait(380);
        }
        return;
      }
      case 'death': {
        const v = this.view(e.unitId);
        const u = this.system.unitById(e.unitId)!;
        const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
        this.fx.deathBurst(w.x, w.y, u.color);
        Sfx.play('death');
        this.fx.shake(0.009, 300);
        if (v) await v.playDeath();
        this.views.delete(e.unitId);
        hud.renderTurnOrder(this.system.getUpcoming(9), this.activeUnit?.id ?? '', this.system.round);
        await this.wait(200);
        return;
      }
      case 'expGain': {
        const v = this.view(e.unitId);
        if (v) this.fx.expPopup(v.container.x, v.container.y - 120, e.amount);
        await this.wait(240);
        return;
      }
      case 'levelUp': {
        const v = this.view(e.unitId);
        const u = this.system.unitById(e.unitId)!;
        if (v) {
          this.fx.levelUpBurst(v.container.x, v.container.y - 40);
          v.refreshBars();
        }
        Sfx.play('levelup');
        hud.showLevelUp(u, e.gains);
        await this.wait(1100);
        return;
      }
      case 'enrage': {
        const v = this.view(e.unitId);
        if (v) {
          v.flash(0xff4444);
          this.fx.shake(0.016, 500);
        }
        Sfx.play('boss');
        hud.showHint('⚠ 堕落骑士·卡奥斯 陷入狂暴！');
        const u = this.system.unitById(e.unitId)!;
        const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
        const t = this.add.text(w.x, w.y - 160, '狂 暴 化', {
          fontSize: '30px', color: '#ff4d5e', stroke: '#2a0000', strokeThickness: 6, fontStyle: 'bold',
        }).setOrigin(0.5).setDepth(300).setScale(0.3);
        this.tweens.add({ targets: t, scale: 1, duration: 220, ease: 'Back.easeOut' });
        this.tweens.add({ targets: t, alpha: 0, y: t.y - 26, duration: 600, delay: 500, onComplete: () => t.destroy() });
        await this.wait(900);
        return;
      }
      default:
        return;
    }
  }

  /** 冲刺后归位 */
  private async settleUnits() {
    const jobs: Promise<void>[] = [];
    for (const [id, v] of this.views) {
      const u = this.system.unitById(id);
      if (!u || !u.alive) continue;
      const w = unitStandPos(u.pos, this.system.terrainAt(u.pos));
      if (Math.abs(v.container.x - w.x) > 2 || Math.abs(v.container.y - w.y) > 2) {
        jobs.push(new Promise<void>(res => {
          this.tweens.add({
            targets: v.container, x: w.x, y: w.y, duration: 170, ease: 'Sine.easeOut',
            onComplete: () => { v.container.setDepth((u.pos.x + u.pos.y) * 10 + 8); res(); },
          });
        }));
      }
    }
    await Promise.all(jobs);
  }

  private wait(ms: number): Promise<void> {
    return new Promise(res => this.time.delayedCall(ms, res));
  }

  // ================= 胜负结算 =================
  private async onVictory() {
    this.views.forEach(v => v.setActive(false));
    this.grid.clearHighlights();
    hud.closeMenus();
    Sfx.play('victory');
    await hud.showTurnBanner('胜  利', '#ffd24a');
    await this.wait(600);

    await new Promise<void>(res => hud.showDialogue(this.chapter.victoryDialogue, () => res()));

    // 结算数据
    GameState.heroLevels = this.system.exportHeroLevels();
    GameState.inventory = this.system.inventory as InventoryEntry[];
    GameState.gold += this.system.gold + this.chapter.reward.gold;
    for (const it of this.chapter.reward.items) {
      const e = GameState.inventory.find(i => i.id === it.id);
      if (e) e.count += it.count; else GameState.inventory.push({ ...it });
    }
    const isLast = this.chapter.id >= TOTAL_CHAPTERS;
    if (!isLast) {
      GameState.chapter = this.chapter.id + 1;
      SaveSystem.save({
        chapter: GameState.chapter,
        heroLevels: GameState.heroLevels,
        inventory: GameState.inventory,
        gold: GameState.gold,
      });
    } else {
      SaveSystem.clear();
    }

    hud.showResultScreen({
      victory: true,
      isEnding: isLast,
      chapter: this.chapter,
      round: this.system.round,
      gold: this.system.gold + this.chapter.reward.gold,
      units: this.system.units.filter(u => u.faction === 'player'),
      onContinue: () => {
        if (isLast) {
          hud.hideAll();
          this.scene.start('Title');
        } else {
          this.scene.start('Battle', { chapterId: this.chapter.id + 1 });
        }
      },
    });
  }

  private async onDefeat() {
    this.views.forEach(v => v.setActive(false));
    this.grid.clearHighlights();
    hud.closeMenus();
    Sfx.play('defeat');
    await hud.showTurnBanner('败  北', '#8a93a8');
    await this.wait(600);
    hud.showResultScreen({
      victory: false,
      isEnding: false,
      chapter: this.chapter,
      round: this.system.round,
      gold: 0,
      units: this.system.units.filter(u => u.faction === 'player'),
      onContinue: () => this.scene.start('Battle', { chapterId: this.chapter.id }),
    });
  }
}
