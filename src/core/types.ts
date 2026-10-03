// ===== 星陨幻世录 · 核心类型定义 =====

export type Faction = 'player' | 'enemy';
export type Element = 'fire' | 'ice' | 'thunder' | 'wind' | 'light' | 'dark' | 'none';
export type Terrain = 'plain' | 'road' | 'forest' | 'mountain' | 'wall';

export interface Stats {
  hp: number; mp: number;
  atk: number; def: number;
  mag: number; res: number;
  spd: number; mov: number; luk: number;
}

export type GrowthRates = Partial<Record<keyof Stats, number>>;

export type DamageType = 'physical' | 'magical' | 'heal' | 'buff';

export type SkillShape =
  | { kind: 'single' }
  | { kind: 'blast'; radius: 1 | 2 }
  | { kind: 'line'; length: number }
  | { kind: 'self' }
  | { kind: 'ally' };

export interface Skill {
  id: string;
  name: string;
  desc: string;
  mp: number;
  range: number;              // 施法距离（曼哈顿）
  shape: SkillShape;
  element: Element;
  damageType: DamageType;
  power: number;              // 倍率（0 = 非伤害）
  hits?: number;              // 多段攻击
  critBonus?: number;         // 暴击率加成
  buff?: { stat: 'atk' | 'def' | 'luk'; mult: number; turns: number };
  learnLevel: number;
  fx: 'slash' | 'fire' | 'ice' | 'thunder' | 'wind' | 'light' | 'dark' | 'heal' | 'buff';
  icon: string;               // emoji 图标
}

export interface CharacterDef {
  id: string;
  name: string;
  title: string;
  element: Element;
  cls: string;
  baseStats: Stats;
  growth: GrowthRates;
  skills: string[];           // 技能 id 列表（按 learnLevel 排序）
  spriteKey: string;
  portraitKey: string;
  color: number;              // 主题色
}

export interface EnemyDef {
  id: string;
  name: string;
  element: Element;
  aiRole: 'melee' | 'ranged' | 'healer' | 'boss';
  level: number;
  stats: Stats;
  skills: string[];
  expReward: number;
  goldReward: number;
  spriteKey: string;
  portraitKey: string;
  color: number;
  boss?: boolean;
}

export interface Buff {
  stat: 'atk' | 'def' | 'luk';
  mult: number;
  turns: number;
  label: string;
}

export interface Unit {
  id: string;
  defId: string;
  name: string;
  title?: string;
  faction: Faction;
  element: Element;
  cls: string;
  level: number;
  exp: number;
  stats: Stats;
  hp: number;
  mp: number;
  pos: TilePos;
  skills: string[];
  buffs: Buff[];
  alive: boolean;
  hasMoved: boolean;
  hasActed: boolean;
  aiRole?: EnemyDef['aiRole'];
  isBoss?: boolean;
  enraged?: boolean;
  expReward: number;
  goldReward: number;
  spriteKey: string;
  portraitKey: string;
  color: number;
  kills: number;
}

export interface TilePos { x: number; y: number; }

export interface MapDef {
  id: string;
  name: string;
  subtitle: string;
  cols: number;
  rows: number;
  bgKey: string;
  weather: 'pollen' | 'fireflies' | 'embers';
  // 行字符串: . 平原 r 道路 f 森林 m 山脉 # 墙/障碍
  // P 玩家出生点 E 敌人出生点 B Boss出生点（地形默认平原）
  grid: string[];
  enemies: Array<{ defId: string; at: string; ch?: string }>;  // at: "x,y" 或 "E" 索引; ch: 剧情名
}

export interface ForecastResult {
  damage: number;
  hit: number;
  crit: number;
  lethal: boolean;
  elementMult: number;
  effective: boolean;
  counter?: ForecastResult | null;
}

export type BattlePhase =
  | 'intro'
  | 'playerIdle'        // 等待玩家选择行动
  | 'moving'            // 播放移动动画
  | 'acting'            // 播放攻击/技能动画
  | 'enemyTurn'
  | 'victory'
  | 'defeat';

// ===== 战斗事件（模拟层 → 表现层）=====
export type BattleEvent =
  | { type: 'unitTurnStart'; unitId: string; round: number }
  | { type: 'roundStart'; round: number }
  | { type: 'move'; unitId: string; path: TilePos[] }
  | { type: 'attackStart'; attackerId: string; targetId: string; skillId?: string }
  | { type: 'hit'; attackerId: string; targetId: string; skillId?: string; damage: number; crit: boolean; lethal: boolean; element: Element; fx: Skill['fx']; effective: boolean }
  | { type: 'miss'; attackerId: string; targetId: string }
  | { type: 'heal'; actorId: string; targetId: string; amount: number }
  | { type: 'buff'; actorId: string; targetId: string; buff: Buff }
  | { type: 'death'; unitId: string }
  | { type: 'expGain'; unitId: string; amount: number }
  | { type: 'levelUp'; unitId: string; newLevel: number; gains: Partial<Stats> }
  | { type: 'turnEnd'; unitId: string }
  | { type: 'enrage'; unitId: string }
  | { type: 'victory'; round: number }
  | { type: 'defeat'; round: number };

export interface ItemDef {
  id: string;
  name: string;
  desc: string;
  icon: string;
  target: 'ally' | 'self';
  effect: { hp?: number; mp?: number; revive?: number };
}

export interface ChapterDef {
  id: number;
  title: string;
  subtitle: string;
  mapId: string;
  roster: string[];
  introDialogue: DialogueLine[];
  victoryDialogue: DialogueLine[];
  reward: { gold: number; items: Array<{ id: string; count: number }> };
}

export interface DialogueLine {
  speaker: string;      // 立绘 key 或 ''
  name: string;
  text: string;
}
