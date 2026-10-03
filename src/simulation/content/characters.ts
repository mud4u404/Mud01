import type { CharacterDef } from '../../core/types';

// ===== 可操作角色数据 =====
export const CHARACTERS: Record<string, CharacterDef> = {
  ren: {
    id: 'ren',
    name: '雷恩',
    title: '炎之剑士',
    element: 'fire',
    cls: '剑士',
    baseStats: { hp: 44, mp: 22, atk: 12, def: 9, mag: 6, res: 6, spd: 8, mov: 5, luk: 6 },
    growth: { hp: 0.9, mp: 0.4, atk: 0.6, def: 0.45, mag: 0.2, res: 0.3, spd: 0.4, luk: 0.3 },
    skills: ['ren_blaze_slash', 'ren_sword_wave', 'ren_warcry', 'ren_inferno'],
    spriteKey: 'spr-ren',
    portraitKey: 'por-ren',
    color: 0xff6b35,
  },
  alice: {
    id: 'alice',
    name: '艾莉丝',
    title: '冰霜法师',
    element: 'ice',
    cls: '法师',
    baseStats: { hp: 32, mp: 44, atk: 5, def: 5, mag: 14, res: 11, spd: 7, mov: 4, luk: 7 },
    growth: { hp: 0.6, mp: 0.8, atk: 0.15, def: 0.25, mag: 0.65, res: 0.5, spd: 0.35, luk: 0.4 },
    skills: ['ali_ice_lance', 'ali_blizzard', 'ali_frost_armor', 'ali_absolute_zero'],
    spriteKey: 'spr-alice',
    portraitKey: 'por-alice',
    color: 0x5ec8f2,
  },
  roland: {
    id: 'roland',
    name: '罗兰',
    title: '疾风游侠',
    element: 'wind',
    cls: '游侠',
    baseStats: { hp: 36, mp: 24, atk: 11, def: 7, mag: 7, res: 8, spd: 11, mov: 5, luk: 10 },
    growth: { hp: 0.7, mp: 0.4, atk: 0.55, def: 0.3, mag: 0.25, res: 0.35, spd: 0.6, luk: 0.6 },
    skills: ['rol_pierce_arrow', 'rol_multi_arrow', 'rol_eagle_eye', 'rol_storm_volley'],
    spriteKey: 'spr-roland',
    portraitKey: 'por-roland',
    color: 0x7fe08c,
  },
  selena: {
    id: 'selena',
    name: '赛琳娜',
    title: '圣光祭司',
    element: 'light',
    cls: '祭司',
    baseStats: { hp: 34, mp: 46, atk: 4, def: 6, mag: 13, res: 13, spd: 6, mov: 4, luk: 9 },
    growth: { hp: 0.65, mp: 0.85, atk: 0.1, def: 0.3, mag: 0.6, res: 0.6, spd: 0.3, luk: 0.5 },
    skills: ['sel_heal', 'sel_holy_smite', 'sel_mass_heal', 'sel_divine_guard'],
    spriteKey: 'spr-selena',
    portraitKey: 'por-selena',
    color: 0xffe9a8,
  },
  kage: {
    id: 'kage',
    name: '影',
    title: '雷刃刺客',
    element: 'thunder',
    cls: '刺客',
    baseStats: { hp: 38, mp: 26, atk: 13, def: 6, mag: 8, res: 7, spd: 13, mov: 6, luk: 12 },
    growth: { hp: 0.75, mp: 0.4, atk: 0.65, def: 0.25, mag: 0.3, res: 0.3, spd: 0.7, luk: 0.7 },
    skills: ['kag_thunder_stab', 'kag_shadow_strike', 'kag_shadow_step', 'kag_thousand_thunder'],
    spriteKey: 'spr-kage',
    portraitKey: 'por-kage',
    color: 0xf7e05a,
  },
};

export function getCharacter(id: string): CharacterDef {
  return CHARACTERS[id];
}
