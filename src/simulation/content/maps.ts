import type { MapDef } from '../../core/types';

// ===== 战场地图数据 =====
// 图例: . 平原  r 道路  f 森林  m 山脉  # 屏障
//       P 玩方出生位  E 敌方出生位  B Boss位（出生位地形为平原）

export const MAPS: Record<string, MapDef> = {
  map_plains: {
    id: 'map_plains',
    name: '苍风平原 · 边境哨所',
    subtitle: '第一战',
    cols: 16,
    rows: 11,
    bgKey: 'bg-plains',
    weather: 'pollen',
    grid: [
      '..........rr..E.',
      '.........rr...E.',
      '..f.....rr....E.',
      '..f....rr.......',
      '......rr......f.',
      '.....rr.......f.',
      '....rr..........',
      '..P.rr..........',
      '..Prr.........m.',
      '.PP..........m..',
      '.P..........mm..',
    ],
    enemies: [
      { defId: 'goblin', at: '14,0' },
      { defId: 'goblin', at: '14,1' },
      { defId: 'skeleton', at: '13,0' },
      { defId: 'goblin', at: '14,2' },
      { defId: 'goblin', at: '11,5' },
    ],
  },

  map_forest: {
    id: 'map_forest',
    name: '低语迷雾森林',
    subtitle: '伏击',
    cols: 16,
    rows: 11,
    bgKey: 'bg-forest',
    weather: 'fireflies',
    grid: [
      '..ff...ff....E..',
      '.fff...ff...fE..',
      '.fff......f.fE..',
      '..f....ff....f..',
      '...E...ff....f..',
      '..fff.........m.',
      '..ff.........mm.',
      '..........ff.m..',
      'P.......fff.....',
      'P.P.....fff.....',
      '........ff......',
    ],
    enemies: [
      { defId: 'orc', at: '3,4' },
      { defId: 'goblin', at: '12,2' },
      { defId: 'skeleton', at: '13,1' },
      { defId: 'skeleton', at: '14,1' },
      { defId: 'orc', at: '14,2' },
      { defId: 'cultist', at: '12,0' },
      { defId: 'cultist', at: '13,3' },
      { defId: 'dark_priest', at: '14,0' },
    ],
  },

  map_fortress: {
    id: 'map_fortress',
    name: '永夜要塞 · 王座大厅',
    subtitle: '决战',
    cols: 16,
    rows: 11,
    bgKey: 'bg-fortress',
    weather: 'embers',
    grid: [
      '#####.####.#####',
      '#..............#',
      '#..B......E...m#',
      '#...m......f...#',
      '#....##..##....#',
      '.....#....#....E',
      'P.P..#....#....E',
      'P.P...........E.',
      'P.....ff.....E..',
      'P....m..m..fE...',
      '................',
    ],
    enemies: [
      { defId: 'chaos_knight', at: '3,2' },
      { defId: 'dark_priest', at: '12,1' },
      { defId: 'gargoyle', at: '5,2' },
      { defId: 'gargoyle', at: '11,2' },
      { defId: 'cultist', at: '12,5' },
      { defId: 'cultist', at: '15,6' },
      { defId: 'orc', at: '15,7' },
      { defId: 'orc', at: '13,8' },
      { defId: 'skeleton', at: '12,9' },
      { defId: 'skeleton', at: '14,9' },
    ],
  },
};

export function getMap(id: string): MapDef {
  return MAPS[id];
}
