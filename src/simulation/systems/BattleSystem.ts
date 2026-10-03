import { ELEMENT_ADVANTAGE, EXP_CURVE, MAX_LEVEL, TERRAIN_INFO } from '../../core/constants';
import type {
  BattleEvent, Buff, Faction, ItemDef, MapDef, Skill, Stats, Terrain, TilePos, Unit,
} from '../../core/types';
import { getCharacter } from '../content/characters';
import { getEnemy } from '../content/enemies';
import { getItem } from '../content/items';
import { getSkill } from '../content/skills';
import { getMap } from '../content/maps';
import { CombatResolver } from './CombatResolver';
import { PathFinding, dist } from './PathFinding';

export type BattleEventListener = (e: BattleEvent) => void;

export interface InventoryEntry { id: string; count: number; }

/** AI 回合计划 */
export interface AIPlan {
  kind: 'attack' | 'skill' | 'heal' | 'wait';
  moveTo: TilePos;
  path: TilePos[] | null;
  targetId?: string;
  skillId?: string;
}

let unitSeq = 0;

export class BattleSystem {
  readonly mapDef: MapDef;
  units: Unit[] = [];
  terrain: Terrain[][] = [];
  round = 1;
  phase: 'intro' | 'battle' | 'victory' | 'defeat' = 'intro';
  inventory: InventoryEntry[] = [];
  gold = 0;

  private turnQueue: Unit[] = [];
  private actedThisRound = new Set<string>();
  private listeners: BattleEventListener[] = [];
  private pf = new PathFinding();
  private preMovePos: Map<string, TilePos> = new Map();

  constructor(mapId: string, rosterIds: string[], heroLevels: Record<string, number> = {}, inventory?: InventoryEntry[]) {
    this.mapDef = getMap(mapId);
    this.parseGrid();
    this.spawnPlayers(rosterIds, heroLevels);
    this.spawnEnemies();
    this.inventory = inventory ? inventory.map(e => ({ ...e })) : [
      { id: 'herb', count: 3 }, { id: 'mana_potion', count: 2 },
    ];
    this.pf.setTerrain(this.terrain);
    this.refreshUnitMap();
  }

  // ===== 初始化 =====
  private parseGrid() {
    const g = this.mapDef.grid;
    // 先替换出生点为平原并记录
    const cleaned: string[] = [];
    const playerSpawns: TilePos[] = [];
    for (let y = 0; y < g.length; y++) {
      let row = '';
      for (let x = 0; x < g[y].length; x++) {
        const c = g[y][x];
        if (c === 'P') { playerSpawns.push({ x, y }); row += '.'; }
        else if (c === 'E' || c === 'B') { row += '.'; }
        else row += c;
      }
      cleaned.push(row);
    }
    this.terrain = cleaned.map(row =>
      row.split('').map(c => {
        switch (c) {
          case 'f': return 'forest' as Terrain;
          case 'm': return 'mountain' as Terrain;
          case '#': return 'wall' as Terrain;
          case 'r': return 'road' as Terrain;
          default: return 'plain' as Terrain;
        }
      })
    );
    this.playerSpawns = playerSpawns;
  }

  private playerSpawns: TilePos[] = [];

  private statsAtLevel(base: Stats, growth: Partial<Record<keyof Stats, number>>, level: number): Stats {
    const s = { ...base };
    for (let lv = 1; lv < level; lv++) {
      for (const k of Object.keys(growth) as Array<keyof Stats>) {
        const rate = growth[k]!;
        if (Math.random() < rate) s[k] += 1;
      }
    }
    return s;
  }

  private spawnPlayers(rosterIds: string[], heroLevels: Record<string, number>) {
    rosterIds.forEach((cid, i) => {
      const def = getCharacter(cid);
      const level = heroLevels[cid] ?? 1;
      const stats = this.statsAtLevel(def.baseStats, def.growth, level);
      const pos = this.playerSpawns[i] ?? { x: 1, y: 8 + i };
      const skills = def.skills.filter(sid => getSkill(sid).learnLevel <= level);
      this.units.push({
        id: `u${++unitSeq}`, defId: def.id, name: def.name, title: def.title,
        faction: 'player', element: def.element, cls: def.cls,
        level, exp: 0, stats, hp: stats.hp, mp: stats.mp,
        pos, skills, buffs: [], alive: true, hasMoved: false, hasActed: false,
        expReward: 0, goldReward: 0,
        spriteKey: def.spriteKey, portraitKey: def.portraitKey, color: def.color, kills: 0,
      });
    });
  }

  private spawnEnemies() {
    for (const e of this.mapDef.enemies) {
      const def = getEnemy(e.defId);
      const [x, y] = e.at.split(',').map(Number);
      this.units.push({
        id: `u${++unitSeq}`, defId: def.id, name: def.name,
        faction: 'enemy', element: def.element, cls: def.aiRole === 'boss' ? '魔王' : '魔物',
        level: def.level, exp: 0, stats: { ...def.stats },
        hp: def.stats.hp, mp: def.stats.mp,
        pos: { x, y }, skills: [...def.skills], buffs: [], alive: true,
        hasMoved: false, hasActed: false,
        aiRole: def.aiRole, isBoss: def.boss,
        expReward: def.expReward, goldReward: def.goldReward,
        spriteKey: def.spriteKey, portraitKey: def.portraitKey, color: def.color, kills: 0,
      });
    }
  }

  // ===== 订阅 =====
  on(fn: BattleEventListener) { this.listeners.push(fn); }
  private emit(e: BattleEvent) { for (const fn of this.listeners) fn(e); }

  // ===== 查询 =====
  get aliveUnits() { return this.units.filter(u => u.alive); }
  get alivePlayers() { return this.aliveUnits.filter(u => u.faction === 'player'); }
  get aliveEnemies() { return this.aliveUnits.filter(u => u.faction === 'enemy'); }
  unit(id: string) { return this.units.find(u => u.id === id); }
  unitById(id: string): Unit | undefined { return this.units.find(u => u.id === id); }
  unitAtPos(p: TilePos): Unit | undefined {
    return this.aliveUnits.find(u => u.pos.x === p.x && u.pos.y === p.y);
  }
  terrainAt(p: TilePos): Terrain { return this.terrain[p.y]?.[p.x] ?? 'wall'; }

  refreshUnitMap() { this.pf.setUnits(this.aliveUnits); }

  // ===== 回合管理（速度序个人行动）=====
  startBattle() {
    this.phase = 'battle';
    this.buildQueue();
    this.nextTurn();
  }

  private buildQueue() {
    this.turnQueue = [...this.aliveUnits].sort((a, b) =>
      b.stats.spd - a.stats.spd || (a.faction === 'player' ? -1 : 1)
    );
    this.actedThisRound.clear();
  }

  get currentUnit(): Unit | undefined { return this.turnQueue[0]; }

  /** 展示用：本回合队列 + 下回合预览 */
  getUpcoming(n = 8): Unit[] {
    const out: Unit[] = [];
    for (const u of this.turnQueue) { if (out.length >= n) break; out.push(u); }
    if (out.length < n) {
      const next = [...this.aliveUnits].filter(u => !this.turnQueue.includes(u))
        .sort((a, b) => b.stats.spd - a.stats.spd);
      for (const u of next) { if (out.length >= n) break; out.push(u); }
    }
    return out;
  }

  nextTurn() {
    if (this.phase !== 'battle') return;
    // 清理队列中已死亡单位
    this.turnQueue = this.turnQueue.filter(u => u.alive);

    if (this.turnQueue.length === 0) {
      this.round++;
      this.buildQueue();
      this.emit({ type: 'roundStart', round: this.round });
    }

    const unit = this.turnQueue[0];
    if (!unit) return;

    unit.hasMoved = false;
    unit.hasActed = false;
    this.tickBuffs(unit);
    this.emit({ type: 'unitTurnStart', unitId: unit.id, round: this.round });
  }

  private tickBuffs(unit: Unit) {
    unit.buffs = unit.buffs.filter(b => --b.turns > 0);
  }

  endUnitTurn(unitId: string) {
    const idx = this.turnQueue.findIndex(u => u.id === unitId);
    if (idx >= 0) this.turnQueue.splice(idx, 1);
    this.actedThisRound.add(unitId);
    this.emit({ type: 'turnEnd', unitId });

    this.checkBattleEnd();
    if (this.phase === 'battle') this.nextTurn();
  }

  private checkBattleEnd() {
    const boss = this.units.find(u => u.isBoss);
    if (this.aliveEnemies.length === 0 || (boss && !boss.alive)) {
      this.phase = 'victory';
      this.emit({ type: 'victory', round: this.round });
    } else {
      const ren = this.units.find(u => u.defId === 'ren');
      if (this.alivePlayers.length === 0 || (ren && !ren.alive)) {
        this.phase = 'defeat';
        this.emit({ type: 'defeat', round: this.round });
      }
    }
  }

  // ===== 玩家行动 API =====
  getMoveRange(unitId: string): Map<string, { cost: number; from: TilePos | null }> {
    const u = this.unitById(unitId)!;
    return this.pf.computeMoveRange(u);
  }

  buildPath(unitId: string, range: Map<string, { cost: number; from: TilePos | null }>, targetKey: string): TilePos[] | null {
    return this.pf.buildPath(range, targetKey);
  }

  moveUnit(unitId: string, path: TilePos[]) {
    const u = this.unitById(unitId)!;
    this.preMovePos.set(unitId, { ...u.pos });
    u.pos = path[path.length - 1];
    u.hasMoved = true;
    this.refreshUnitMap();
    this.emit({ type: 'move', unitId, path });
  }

  /** 撤销移动（未行动前） */
  undoMove(unitId: string): boolean {
    const u = this.unitById(unitId)!;
    if (u.hasActed || !u.hasMoved) return false;
    const prev = this.preMovePos.get(unitId);
    if (!prev) return false;
    u.pos = { ...prev };
    u.hasMoved = false;
    this.refreshUnitMap();
    return true;
  }

  /** 获取攻击目标（基础攻击或指定技能） */
  getTargetsInSkillRange(unitId: string, skillId?: string): Unit[] {
    const u = this.unitById(unitId)!;
    const skill = skillId ? getSkill(skillId) : null;
    const range = skill ? skill.range : this.basicAttackRange(u);
    const targetsAllies = !!skill && (skill.damageType === 'heal' ||
      (skill.damageType === 'buff' && skill.shape.kind === 'ally'));
    const allowSelf = !!skill && (skill.shape.kind === 'ally' || skill.shape.kind === 'self');
    return this.aliveUnits.filter(t => {
      const d = dist(u.pos, t.pos);
      if (d > range) return false;
      if (d === 0 && !allowSelf) return false;
      if (targetsAllies) return t.faction === u.faction;
      return t.faction !== u.faction;
    });
  }

  basicAttackRange(u: Unit): number {
    // 法系敌人基础射程 2，近战 1；玩家法师/祭司普攻也为远程魔法弹
    if (u.faction === 'enemy') return u.aiRole === 'ranged' ? 2 : 1;
    return (u.cls === '法师' || u.cls === '祭司') ? 2 : 1;
  }

  /** 技能/普攻的目标格集合（用于渲染红圈） */
  getSkillTargetTiles(unitId: string, skillId?: string): TilePos[] {
    const u = this.unitById(unitId)!;
    const skill = skillId ? getSkill(skillId) : null;
    const range = skill ? skill.range : this.basicAttackRange(u);
    const tiles: TilePos[] = [];
    for (let y = 0; y < this.mapDef.rows; y++) {
      for (let x = 0; x < this.mapDef.cols; x++) {
        const d = dist(u.pos, { x, y });
        if (d >= 1 && d <= range) tiles.push({ x, y });
      }
    }
    return tiles;
  }

  /** 直线穿透技能的目标格（四个方向各 length 格） */
  getLineTargetTiles(unitId: string, skill: Skill): TilePos[] {
    const u = this.unitById(unitId)!;
    const length = skill.shape.kind === 'line' ? (skill.shape as { length: number }).length : 0;
    const tiles: TilePos[] = [];
    for (const dir of [{ x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 }]) {
      for (let i = 1; i <= length; i++) {
        const x = u.pos.x + dir.x * i;
        const y = u.pos.y + dir.y * i;
        if (x < 0 || y < 0 || x >= this.mapDef.cols || y >= this.mapDef.rows) break;
        tiles.push({ x, y });
      }
    }
    return tiles;
  }

  /** 技能影响的实际单位集合 */
  resolveSkillAffected(actor: Unit, target: TilePos, skill?: Skill): Unit[] {
    if (!skill) return [this.unitAtPos(target)!].filter(Boolean);
    switch (skill.shape.kind) {
      case 'single':
      case 'ally': {
        const t = this.unitAtPos(target);
        return t ? [t] : [];
      }
      case 'blast': {
        const r = (skill.shape as { radius: number }).radius;
        return this.aliveUnits.filter(t => {
          const d = dist(target, t.pos);
          if (d > r) return false;
          if (skill.damageType === 'heal') return t.faction === actor.faction;
          return t.faction !== actor.faction;
        });
      }
      case 'line': {
        // 由 view 层传入具体命中线；此处退化为主目标
        const t = this.unitAtPos(target);
        return t ? [t] : [];
      }
      default:
        return [];
    }
  }

  // ===== 行动执行 =====
  canUseSkill(unit: Unit, skillId: string): boolean {
    const skill = getSkill(skillId);
    return unit.mp >= skill.mp && unit.skills.includes(skillId);
  }

  attack(attackerId: string, targetId: string, skillId?: string) {
    const attacker = this.unitById(attackerId)!;
    const target = this.unitById(targetId)!;
    const skill = skillId ? getSkill(skillId) : undefined;
    if (skill) attacker.mp -= skill.mp;
    attacker.hasActed = true;
    this.emit({ type: 'attackStart', attackerId, targetId, skillId });

    const hits = skill?.hits ?? 1;
    let lethal = false;
    let dealtDamage = false;

    for (let h = 0; h < hits; h++) {
      if (!target.alive) break;
      const r = CombatResolver.rollDamage(attacker, target, this.terrainAt(target.pos), skill);
      if (!r.hit) {
        this.emit({ type: 'miss', attackerId, targetId });
        continue;
      }
      target.hp = Math.max(0, target.hp - r.damage);
      dealtDamage = true;
      lethal = target.hp <= 0;
      this.emit({
        type: 'hit', attackerId, targetId, skillId,
        damage: r.damage, crit: r.crit, lethal, element: skill?.element ?? attacker.element,
        fx: skill?.fx ?? 'slash', effective: r.effective,
      });
      if (lethal) break;
    }

    // 反击（目标存活且在反击范围内）
    if (!lethal && target.alive && this.inCounterRange(attacker, target) && Math.random() < 0.85) {
      const cr = CombatResolver.rollDamage(target, attacker, this.terrainAt(attacker.pos));
      if (cr.hit) {
        attacker.hp = Math.max(0, attacker.hp - Math.round(cr.damage * 0.75));
        this.emit({
          type: 'hit', attackerId: targetId, targetId: attackerId, damage: Math.round(cr.damage * 0.75),
          crit: cr.crit, lethal: attacker.hp <= 0, element: target.element, fx: 'slash', effective: cr.effective,
        });
      }
    }

    this.grantExp(attacker, target, lethal, dealtDamage);
    this.postAction(attacker, target);
  }

  /** 范围攻击（暴风雪/多重箭等 blast 技能） */
  areaAttack(attackerId: string, center: TilePos, skillId: string) {
    const attacker = this.unitById(attackerId)!;
    const skill = getSkill(skillId);
    attacker.mp -= skill.mp;
    attacker.hasActed = true;
    const affected = this.resolveSkillAffected(attacker, center, skill);
    const first = affected[0];
    this.emit({ type: 'attackStart', attackerId, targetId: first?.id, skillId });

    let anyLethal = false;
    let dealtDamage = false;
    for (const target of affected) {
      if (!target.alive) continue;
      const r = CombatResolver.rollDamage(attacker, target, this.terrainAt(target.pos), skill);
      if (!r.hit) { this.emit({ type: 'miss', attackerId, targetId: target.id }); continue; }
      target.hp = Math.max(0, target.hp - r.damage);
      dealtDamage = true;
      const lethal = target.hp <= 0;
      anyLethal = anyLethal || lethal;
      this.emit({
        type: 'hit', attackerId, targetId: target.id, skillId,
        damage: r.damage, crit: r.crit, lethal, element: skill.element,
        fx: skill.fx, effective: r.effective,
      });
    }
    this.grantExp(attacker, null, false, dealtDamage, 0);
    // 逐个目标结算经验
    for (const target of affected) {
      if (!target.alive && target.hp <= 0) this.grantExp(attacker, target, true, true);
    }
    this.postAction(attacker, null);
  }

  /** 直线穿透攻击（剑气纵横/贯穿箭） */
  lineAttack(attackerId: string, targetTile: TilePos, skillId: string) {
    const attacker = this.unitById(attackerId)!;
    const skill = getSkill(skillId);
    attacker.mp -= skill.mp;
    attacker.hasActed = true;

    // 计算方向
    const dx = Math.sign(targetTile.x - attacker.pos.x);
    const dy = Math.sign(targetTile.y - attacker.pos.y);
    const length = skill.shape.kind === 'line' ? (skill.shape as { length: number }).length : 0;
    const affected: Unit[] = [];
    for (let i = 1; i <= length; i++) {
      const t = this.unitAtPos({ x: attacker.pos.x + dx * i, y: attacker.pos.y + dy * i });
      if (t && t.faction !== attacker.faction) affected.push(t);
    }
    const first = affected[0];
    this.emit({ type: 'attackStart', attackerId, targetId: first?.id, skillId });

    let dealtDamage = false;
    for (const target of affected) {
      if (!target.alive) continue;
      const r = CombatResolver.rollDamage(attacker, target, this.terrainAt(target.pos), skill);
      if (!r.hit) { this.emit({ type: 'miss', attackerId, targetId: target.id }); continue; }
      target.hp = Math.max(0, target.hp - r.damage);
      dealtDamage = true;
      const lethal = target.hp <= 0;
      this.emit({
        type: 'hit', attackerId, targetId: target.id, skillId,
        damage: r.damage, crit: r.crit, lethal, element: skill.element,
        fx: skill.fx, effective: r.effective,
      });
    }
    this.grantExp(attacker, null, false, dealtDamage, 0);
    for (const target of affected) {
      if (!target.alive && target.hp <= 0) this.grantExp(attacker, target, true, true);
    }
    this.postAction(attacker, null);
  }

  private inCounterRange(attacker: Unit, target: Unit): boolean {
    if (target.faction === attacker.faction) return false;
    const d = dist(attacker.pos, target.pos);
    return d <= this.basicAttackRange(target) || (d <= 2 && target.cls === '魔王');
  }

  useHealSkill(actorId: string, skillId: string, targetId: string) {
    const actor = this.unitById(actorId)!;
    const target = this.unitById(targetId)!;
    const skill = getSkill(skillId);
    actor.mp -= skill.mp;
    actor.hasActed = true;
    const amount = CombatResolver.healAmount(actor, skill);
    target.hp = Math.min(target.stats.hp, target.hp + amount);
    this.emit({ type: 'heal', actorId, targetId, amount });
    if (skill.buff) {
      target.buffs.push({ ...skill.buff, label: skill.name });
      this.emit({ type: 'buff', actorId, targetId, buff: { ...skill.buff, label: skill.name } });
    }
    this.grantExp(actor, null, false, false, 14);
    this.postAction(actor, null);
  }

  useBuffSkill(actorId: string, skillId: string) {
    const actor = this.unitById(actorId)!;
    const skill = getSkill(skillId);
    actor.mp -= skill.mp;
    actor.hasActed = true;
    actor.buffs.push({ stat: skill.buff!.stat, mult: skill.buff!.mult, turns: skill.buff!.turns + 1, label: skill.name });
    this.emit({ type: 'buff', actorId, targetId: actorId, buff: { ...skill.buff!, label: skill.name } });
    this.postAction(actor, null);
  }

  /** 瞬步：传送 */
  useTeleportSkill(actorId: string, skillId: string, dest: TilePos) {
    const actor = this.unitById(actorId)!;
    const skill = getSkill(skillId);
    actor.mp -= skill.mp;
    actor.hasActed = true;
    actor.buffs.push({ stat: skill.buff!.stat, mult: skill.buff!.mult, turns: skill.buff!.turns + 1, label: skill.name });
    actor.pos = { ...dest };
    this.refreshUnitMap();
    this.emit({ type: 'move', unitId: actorId, path: [dest] });
    this.emit({ type: 'buff', actorId, targetId: actorId, buff: { ...skill.buff!, label: skill.name } });
    this.postAction(actor, null);
  }

  useItem(actorId: string, itemId: string, targetId: string) {
    const actor = this.unitById(actorId)!;
    const target = this.unitById(targetId)!;
    const item = getItem(itemId);
    const entry = this.inventory.find(e => e.id === itemId);
    if (!entry || entry.count <= 0) return;
    entry.count--;
    if (entry.count <= 0) this.inventory = this.inventory.filter(e => e.count > 0);
    actor.hasActed = true;

    if (item.effect.revive && !target.alive) {
      target.alive = true;
      target.hp = Math.round(target.stats.hp * item.effect.revive);
      this.emit({ type: 'heal', actorId, targetId, amount: target.hp });
    }
    if (item.effect.hp) {
      const before = target.hp;
      target.hp = Math.min(target.stats.hp, target.hp + item.effect.hp);
      if (target.hp > before) this.emit({ type: 'heal', actorId, targetId, amount: target.hp - before });
    }
    if (item.effect.mp) {
      target.mp = Math.min(target.stats.mp, target.mp + item.effect.mp);
    }
    this.postAction(actor, null);
  }

  wait(unitId: string) {
    const u = this.unitById(unitId)!;
    u.hasActed = true;
    u.hasMoved = true;
  }

  private postAction(actor: Unit, target: Unit | null) {
    // 死亡结算
    for (const u of [target, actor]) {
      if (u && u.hp <= 0 && u.alive) this.killUnit(u, actor);
    }
    // Boss 狂暴检查
    for (const u of this.aliveEnemies) {
      if (u.isBoss && !u.enraged && u.hp <= u.stats.hp * 0.5) {
        u.enraged = true;
        u.buffs.push({ stat: 'atk', mult: 1.3, turns: 99, label: '狂暴' });
        this.emit({ type: 'enrage', unitId: u.id });
      }
    }
    if (this.phase === 'battle' && actor.hasActed) {
      // 表现层动画完成后由 controller 调用 endUnitTurn
    }
  }

  private killUnit(u: Unit, killer: Unit | null) {
    u.alive = false;
    this.emit({ type: 'death', unitId: u.id });
    if (killer && u.faction === 'enemy') {
      this.gold += u.goldReward;
      killer.kills++;
    }
  }

  // ===== 经验与升级 =====
  private grantExp(unit: Unit, target: Unit | null, killed: boolean, dealtDamage: boolean, healExp = 0) {
    if (unit.faction !== 'player' || unit.level >= MAX_LEVEL) return;
    let exp = healExp;
    if (target && target.faction === 'enemy') {
      if (dealtDamage) exp += 8 + target.level * 2;
      if (killed) exp += target.expReward;
    }
    if (exp <= 0) return;
    unit.exp += exp;
    this.emit({ type: 'expGain', unitId: unit.id, amount: exp });
    while (unit.exp >= EXP_CURVE(unit.level) && unit.level < MAX_LEVEL) {
      unit.exp -= EXP_CURVE(unit.level);
      unit.level++;
      const gains = this.levelUpStats(unit);
      // 学习新技能
      const def = getCharacter(unit.defId);
      for (const sid of def.skills) {
        if (getSkill(sid).learnLevel === unit.level && !unit.skills.includes(sid)) {
          unit.skills.push(sid);
        }
      }
      this.emit({ type: 'levelUp', unitId: unit.id, newLevel: unit.level, gains });
    }
  }

  private levelUpStats(unit: Unit): Partial<Stats> {
    const def = getCharacter(unit.defId);
    const gains: Partial<Stats> = {};
    for (const k of Object.keys(def.growth) as Array<keyof Stats>) {
      const rate = def.growth[k]!;
      let gain = 0;
      // 期望值补偿：rate*2 舍入
      gain += Math.floor(rate) + (Math.random() < rate % 1 ? 1 : 0);
      if (gain > 0) {
        unit.stats[k] += gain;
        gains[k] = gain;
      }
    }
    if (gains.hp) unit.hp += gains.hp;
    if (gains.mp) unit.mp += gains.mp;
    return gains;
  }

  /** 章节结束后导出英雄等级 */
  exportHeroLevels(): Record<string, number> {
    const out: Record<string, number> = {};
    for (const u of this.units) {
      if (u.faction === 'player') out[u.defId] = u.level;
    }
    return out;
  }

  // ===== 敌方 AI =====
  planEnemyTurn(unitId: string): AIPlan {
    const u = this.unitById(unitId)!;
    const range = this.pf.computeMoveRange(u);
    const enemies = this.alivePlayers; // 玩方单位是 AI 的敌人
    let best: AIPlan = { kind: 'wait', moveTo: { ...u.pos }, path: null };

    // ---- 治疗型 AI ----
    if (u.aiRole === 'healer') {
      const allies = this.aliveEnemies.filter(a => a.hp < a.stats.hp * 0.55 && a.id !== u.id);
      if (u.aiRole === 'healer' && getSkill(u.skills[0])?.damageType === 'magical') {
        // 暗黑主教：优先攻击低血量玩家，残血则保持距离
      }
      // 有受伤队友时靠近并施放汲取（对敌）或贴近待命
    }

    let bestScore = -Infinity;

    for (const [k, node] of range) {
      if (node.cost === Infinity) continue;
      const pos = this.pf.parseKey(k);
      const saved = { ...u.pos };
      u.pos = pos;
      const terrain = this.terrainAt(pos);

      // 尝试每个可用攻击方式
      const options: Array<{ skillId?: string; range: number }> = [
        { range: this.basicAttackRange(u) },
        ...u.skills.filter(sid => this.canUseSkill(u, sid))
          .map(sid => ({ skillId: sid, range: getSkill(sid).range })),
      ];

      for (const opt of options) {
        const skill = opt.skillId ? getSkill(opt.skillId) : null;
        // 治疗技能：治疗受伤友军
        if (skill && (skill.damageType === 'heal' || (skill.damageType === 'buff' && skill.shape.kind === 'ally'))) {
          const allies = this.aliveEnemies.filter(a => dist(pos, a.pos) <= opt.range);
          for (const ally of allies) {
            const missing = ally.stats.hp - ally.hp;
            if (missing < 25) continue;
            const score = missing + (ally.isBoss ? 40 : 0);
            if (score > bestScore) {
              bestScore = score;
              const path = this.pf.buildPath(range, k);
              best = { kind: 'heal', moveTo: pos, path, targetId: ally.id, skillId: opt.skillId };
            }
          }
          continue;
        }

        for (const t of enemies) {
          const d = dist(pos, t.pos);
          if (d > opt.range || d === 0) continue;
          const fc = CombatResolver.forecast(u, t, terrain, skill ?? undefined);
          let score = Math.min(fc.damage, t.hp) * 1.0;
          if (fc.lethal) score += 60 + t.level * 5;
          if (fc.effective) score += 8;
          score -= (100 - fc.hit) * 0.3;
          // Boss 优先集火低血量
          if (t.hp <= t.stats.hp * 0.35) score += 15;
          // 脆弱单位偏好地形防御
          const ti = TERRAIN_INFO[terrain];
          score += ti.defBonus * 25 + ti.avoid * 0.3;
          // 远程单位保持最大射程的安全偏好
          if (u.aiRole === 'ranged' && d >= 2) score += 10;
          // Boss 靠近雷恩（主角威胁）
          if (u.isBoss && t.defId === 'ren') score += 12;

          if (score > bestScore) {
            bestScore = score;
            const path = this.pf.buildPath(range, k);
            best = { kind: skill ? 'skill' : 'attack', moveTo: pos, path, targetId: t.id, skillId: opt.skillId };
          }
        }
      }
      u.pos = saved;
    }

    // 无法攻击任何目标：向最近的玩家移动
    if (bestScore === -Infinity) {
      let nearest = enemies[0];
      let nd = Infinity;
      for (const t of enemies) {
        const d = dist(u.pos, t.pos);
        if (d < nd) { nd = d; nearest = t; }
      }
      if (nearest) {
        const step = this.pf.greedyStep(u.pos, nearest.pos, u);
        const path = this.pf.buildPath(range, this.pf.key(step));
        if (path && path.length > 1) {
          best = { kind: 'wait', moveTo: step, path };
        }
      }
    }
    return best;
  }

  /** 执行 AI 计划（表现层调用） */
  executeAIPlan(plan: AIPlan, unitId: string) {
    const u = this.unitById(unitId)!;
    if (plan.path && plan.path.length > 1) {
      this.moveUnit(unitId, plan.path);
    }
    if (plan.kind === 'attack' || plan.kind === 'skill') {
      this.attack(unitId, plan.targetId!, plan.skillId);
    } else if (plan.kind === 'heal') {
      const skill = getSkill(plan.skillId!);
      if (skill.damageType === 'heal') this.useHealSkill(unitId, plan.skillId!, plan.targetId!);
      else this.useBuffSkill(unitId, plan.skillId!);
    }
  }

  addItem(id: string, count: number) {
    const e = this.inventory.find(i => i.id === id);
    if (e) e.count += count;
    else this.inventory.push({ id, count });
  }
}

