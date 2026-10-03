import type { Skill } from '../../core/types';

// ===== 技能数据表 =====
export const SKILLS: Record<string, Skill> = {
  // ---- 雷恩 · 炎之剑士 ----
  ren_blaze_slash: {
    id: 'ren_blaze_slash', name: '烈焰斩', desc: '缠绕烈焰的斩击，造成炎属性物理伤害。',
    mp: 6, range: 1, shape: { kind: 'single' }, element: 'fire', damageType: 'physical',
    power: 1.6, learnLevel: 1, fx: 'fire', icon: '🔥'
  },
  ren_sword_wave: {
    id: 'ren_sword_wave', name: '剑气纵横', desc: '释放贯穿剑气，穿透直线上所有敌人。',
    mp: 10, range: 3, shape: { kind: 'line', length: 3 }, element: 'none', damageType: 'physical',
    power: 1.15, learnLevel: 3, fx: 'slash', icon: '🗡️'
  },
  ren_warcry: {
    id: 'ren_warcry', name: '战意沸腾', desc: '燃烧斗志，攻击力提升35%，持续3回合。',
    mp: 8, range: 0, shape: { kind: 'self' }, element: 'none', damageType: 'buff',
    power: 0, learnLevel: 5, fx: 'buff', icon: '💪',
    buff: { stat: 'atk', mult: 1.35, turns: 3 }
  },
  ren_inferno: {
    id: 'ren_inferno', name: '炎狱斩', desc: '召唤地狱之火的终极一斩。',
    mp: 16, range: 1, shape: { kind: 'single' }, element: 'fire', damageType: 'physical',
    power: 2.2, learnLevel: 7, fx: 'fire', icon: '🌋'
  },

  // ---- 艾莉丝 · 冰霜法师 ----
  ali_ice_lance: {
    id: 'ali_ice_lance', name: '冰锥术', desc: '凝聚锋利冰锥刺穿敌人。',
    mp: 8, range: 2, shape: { kind: 'single' }, element: 'ice', damageType: 'magical',
    power: 1.7, learnLevel: 1, fx: 'ice', icon: '❄️'
  },
  ali_blizzard: {
    id: 'ali_blizzard', name: '暴风雪', desc: '召唤暴风雪，席卷范围内所有敌人。',
    mp: 16, range: 3, shape: { kind: 'blast', radius: 1 }, element: 'ice', damageType: 'magical',
    power: 1.15, learnLevel: 3, fx: 'ice', icon: '🌨️'
  },
  ali_frost_armor: {
    id: 'ali_frost_armor', name: '冰霜护甲', desc: '为友军披上寒冰铠甲，防御提升40%。',
    mp: 10, range: 2, shape: { kind: 'ally' }, element: 'ice', damageType: 'buff',
    power: 0, learnLevel: 5, fx: 'buff', icon: '🛡️',
    buff: { stat: 'def', mult: 1.4, turns: 3 }
  },
  ali_absolute_zero: {
    id: 'ali_absolute_zero', name: '绝对零度', desc: '冻结万物的极寒之力。',
    mp: 24, range: 2, shape: { kind: 'single' }, element: 'ice', damageType: 'magical',
    power: 2.4, learnLevel: 7, fx: 'ice', icon: '🧊'
  },

  // ---- 罗兰 · 疾风游侠 ----
  rol_pierce_arrow: {
    id: 'rol_pierce_arrow', name: '贯穿箭', desc: '射出贯穿之箭，命中直线上所有敌人。',
    mp: 6, range: 4, shape: { kind: 'line', length: 4 }, element: 'none', damageType: 'physical',
    power: 1.3, learnLevel: 1, fx: 'wind', icon: '🏹'
  },
  rol_multi_arrow: {
    id: 'rol_multi_arrow', name: '多重箭', desc: '同时射出多支箭矢，覆盖一片区域。',
    mp: 12, range: 3, shape: { kind: 'blast', radius: 1 }, element: 'none', damageType: 'physical',
    power: 0.95, learnLevel: 3, fx: 'wind', icon: '🎯'
  },
  rol_eagle_eye: {
    id: 'rol_eagle_eye', name: '鹰之眼', desc: '锐利如鹰，幸运（暴击）提升，持续3回合。',
    mp: 8, range: 0, shape: { kind: 'self' }, element: 'none', damageType: 'buff',
    power: 0, learnLevel: 5, fx: 'buff', icon: '👁️',
    buff: { stat: 'luk', mult: 2.0, turns: 3 }
  },
  rol_storm_volley: {
    id: 'rol_storm_volley', name: '疾风连射', desc: '如疾风般的连续射击，造成2次伤害。',
    mp: 18, range: 3, shape: { kind: 'single' }, element: 'wind', damageType: 'physical',
    power: 1.0, hits: 2, learnLevel: 7, fx: 'wind', icon: '🌀'
  },

  // ---- 赛琳娜 · 圣光祭司 ----
  sel_heal: {
    id: 'sel_heal', name: '治愈之光', desc: '以圣光治疗友军。',
    mp: 8, range: 2, shape: { kind: 'ally' }, element: 'light', damageType: 'heal',
    power: 1.2, learnLevel: 1, fx: 'heal', icon: '💚'
  },
  sel_holy_smite: {
    id: 'sel_holy_smite', name: '圣光冲击', desc: '以圣光审判敌人。',
    mp: 10, range: 2, shape: { kind: 'single' }, element: 'light', damageType: 'magical',
    power: 1.5, learnLevel: 3, fx: 'light', icon: '⚡'
  },
  sel_mass_heal: {
    id: 'sel_mass_heal', name: '群体治愈', desc: '治愈范围内所有友军。',
    mp: 20, range: 2, shape: { kind: 'blast', radius: 1 }, element: 'light', damageType: 'heal',
    power: 1.0, learnLevel: 5, fx: 'heal', icon: '🌿'
  },
  sel_divine_guard: {
    id: 'sel_divine_guard', name: '神圣庇护', desc: '大幅治疗并附加守护祝福。',
    mp: 18, range: 2, shape: { kind: 'ally' }, element: 'light', damageType: 'heal',
    power: 1.8, learnLevel: 7, fx: 'heal', icon: '🕊️',
    buff: { stat: 'def', mult: 1.25, turns: 2 }
  },

  // ---- 影 · 雷刃刺客 ----
  kag_thunder_stab: {
    id: 'kag_thunder_stab', name: '雷光刺', desc: '附雷一击，暴击率大幅提升。',
    mp: 6, range: 1, shape: { kind: 'single' }, element: 'thunder', damageType: 'physical',
    power: 1.5, critBonus: 30, learnLevel: 1, fx: 'thunder', icon: '⚡'
  },
  kag_shadow_strike: {
    id: 'kag_shadow_strike', name: '影袭', desc: '自暗影中发动无法防范的奇袭。',
    mp: 10, range: 1, shape: { kind: 'single' }, element: 'none', damageType: 'physical',
    power: 1.75, learnLevel: 3, fx: 'slash', icon: '🌑'
  },
  kag_shadow_step: {
    id: 'kag_shadow_step', name: '瞬步', desc: '化作影子瞬间移动。',
    mp: 8, range: 4, shape: { kind: 'self' }, element: 'none', damageType: 'buff',
    power: 0, learnLevel: 5, fx: 'dark', icon: '💨',
    buff: { stat: 'atk', mult: 1.2, turns: 1 }
  },
  kag_thousand_thunder: {
    id: 'kag_thousand_thunder', name: '千雷闪', desc: '以雷霆之速发动3连击。',
    mp: 20, range: 1, shape: { kind: 'single' }, element: 'thunder', damageType: 'physical',
    power: 0.95, hits: 3, learnLevel: 7, fx: 'thunder', icon: '🌩️'
  },

  // ---- 敌方技能 ----
  enemy_dark_bolt: {
    id: 'enemy_dark_bolt', name: '暗影箭', desc: '发射黑暗法球。',
    mp: 0, range: 2, shape: { kind: 'single' }, element: 'dark', damageType: 'magical',
    power: 1.4, learnLevel: 1, fx: 'dark', icon: '🌑'
  },
  enemy_drain: {
    id: 'enemy_drain', name: '汲取', desc: '汲取生命之力治疗自身。',
    mp: 0, range: 2, shape: { kind: 'single' }, element: 'dark', damageType: 'magical',
    power: 1.1, learnLevel: 1, fx: 'dark', icon: '🩸'
  },
  boss_dark_wave: {
    id: 'boss_dark_wave', name: '黑暗波动', desc: '释放黑暗冲击波，攻击周围敌人。',
    mp: 10, range: 3, shape: { kind: 'blast', radius: 1 }, element: 'dark', damageType: 'magical',
    power: 1.3, learnLevel: 1, fx: 'dark', icon: '💥'
  },
  boss_dread_slash: {
    id: 'boss_dread_slash', name: '恐惧斩', desc: '灌注黑暗之力的恐怖斩击。',
    mp: 6, range: 1, shape: { kind: 'single' }, element: 'dark', damageType: 'physical',
    power: 1.6, learnLevel: 1, fx: 'dark', icon: '⚔️'
  },
};

export function getSkill(id: string): Skill {
  return SKILLS[id];
}
