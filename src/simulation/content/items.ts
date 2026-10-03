import type { ItemDef } from '../../core/types';

export const ITEMS: Record<string, ItemDef> = {
  herb: {
    id: 'herb', name: '治愈药草', desc: '恢复 80 HP', icon: '🌿',
    target: 'ally', effect: { hp: 80 }
  },
  mana_potion: {
    id: 'mana_potion', name: '魔力药剂', desc: '恢复 50 MP', icon: '🔵',
    target: 'ally', effect: { mp: 50 }
  },
  fairy_tear: {
    id: 'fairy_tear', name: '精灵之泪', desc: '复苏倒下的同伴（50% HP）', icon: '💧',
    target: 'ally', effect: { revive: 0.5 }
  },
  elixir: {
    id: 'elixir', name: '星陨圣露', desc: '完全恢复 HP 与 MP', icon: '🌟',
    target: 'ally', effect: { hp: 999, mp: 999 }
  },
};

export function getItem(id: string): ItemDef {
  return ITEMS[id];
}
