// ===== 进度存档（localStorage）=====
const SAVE_KEY = 'afc-save-v1';

export interface SaveData {
  chapter: number;                 // 下一个待玩章节
  heroLevels: Record<string, number>;
  inventory: Array<{ id: string; count: number }>;
  gold: number;
}

export const SaveSystem = {
  load(): SaveData | null {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) return null;
      return JSON.parse(raw) as SaveData;
    } catch {
      return null;
    }
  },

  save(data: SaveData) {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(data)); } catch { /* ignore */ }
  },

  clear() {
    try { localStorage.removeItem(SAVE_KEY); } catch { /* ignore */ }
  },
};
