import type { InventoryEntry } from '../simulation/systems/BattleSystem';

// ===== 跨场景游戏进度 =====
export interface GameStateShape {
  chapter: number;
  heroLevels: Record<string, number>;
  inventory: InventoryEntry[];
  gold: number;
}

export const GameState: GameStateShape = {
  chapter: 1,
  heroLevels: {},
  inventory: [
    { id: 'herb', count: 3 },
    { id: 'mana_potion', count: 2 },
  ],
  gold: 0,
};

export function resetGameState() {
  GameState.chapter = 1;
  GameState.heroLevels = {};
  GameState.inventory = [{ id: 'herb', count: 3 }, { id: 'mana_potion', count: 2 }];
  GameState.gold = 0;
}
