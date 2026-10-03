import { GRID_COLS, GRID_ROWS, TERRAIN_INFO } from '../../core/constants';
import type { Terrain, TilePos, Unit } from '../../core/types';

/** 曼哈顿距离 */
export function dist(a: TilePos, b: TilePos): number {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

export interface ReachableTile {
  cost: number;
  from: TilePos | null;
}

/**
 * 基于代际 Dijkstra 的移动范围计算 + 路径重建。
 * 地形决定移动消耗，被占用格不可停留但可穿越友方单位（简化：友军可穿行，敌军阻挡）。
 */
export class PathFinding {
  private terrainGrid: Terrain[][] = [];
  private unitAt: Map<string, Unit> = new Map(); // "x,y" -> unit

  setTerrain(grid: Terrain[][]) {
    this.terrainGrid = grid;
  }

  setUnits(units: Unit[]) {
    this.unitAt.clear();
    for (const u of units) {
      if (u.alive) this.unitAt.set(this.key(u.pos), u);
    }
  }

  key(p: TilePos): string { return `${p.x},${p.y}`; }

  parseKey(k: string): TilePos {
    const [x, y] = k.split(',').map(Number);
    return { x, y };
  }

  inBounds(p: TilePos): boolean {
    return p.x >= 0 && p.x < GRID_COLS && p.y >= 0 && p.y < GRID_ROWS;
  }

  terrainAt(p: TilePos): Terrain {
    return this.terrainGrid[p.y]?.[p.x] ?? 'wall';
  }

  isWall(p: TilePos): boolean {
    return this.terrainAt(p) === 'wall';
  }

  /** 计算单位可到达的所有格子（含起点） */
  computeMoveRange(unit: Unit): Map<string, ReachableTile> {
    const result = new Map<string, ReachableTile>();
    const start = this.key(unit.pos);
    result.set(start, { cost: 0, from: null });

    // Dijkstra（小图用简单优先队列即可）
    const frontier: Array<{ pos: TilePos; cost: number }> = [{ pos: unit.pos, cost: 0 }];
    const mov = unit.stats.mov;

    while (frontier.length > 0) {
      frontier.sort((a, b) => a.cost - b.cost);
      const cur = frontier.shift()!;
      const curKey = this.key(cur.pos);

      for (const dir of [{ x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 }]) {
        const next = { x: cur.pos.x + dir.x, y: cur.pos.y + dir.y };
        if (!this.inBounds(next) || this.isWall(next)) continue;

        const t = TERRAIN_INFO[this.terrainAt(next)];
        if (t.cost === Infinity) continue;
        const nextCost = cur.cost + t.cost;
        if (nextCost > mov) continue;

        // 友军可穿行，敌军阻挡
        const occ = this.unitAt.get(this.key(next));
        if (occ && occ.faction !== unit.faction) continue;

        const nextKey = this.key(next);
        const prev = result.get(nextKey);
        if (!prev || nextCost < prev.cost) {
          result.set(nextKey, { cost: nextCost, from: cur.pos });
          frontier.push({ pos: next, cost: nextCost });
        }
      }
    }

    // 只有无人占用的格子可作为停留点
    for (const [k, v] of result) {
      const occ = this.unitAt.get(k);
      if (occ && occ.id !== unit.id) v.cost = Infinity; // 标记不可停留
    }
    return result;
  }

  /** 重建到目标格的路径 */
  buildPath(range: Map<string, ReachableTile>, targetKey: string): TilePos[] | null {
    if (!range.has(targetKey)) return null;
    const path: TilePos[] = [];
    let cur = targetKey;
    while (cur) {
      const node = range.get(cur)!;
      path.unshift(this.parseKey(cur));
      cur = node.from ? this.key(node.from) : '';
      if (!node.from) break;
    }
    return path;
  }

  /** 曼哈顿距离 */
  static dist(a: TilePos, b: TilePos): number {
    return dist(a, b);
  }

  /** 从 from 朝 to 走一步的贪心路径（AI 追击用） */
  greedyStep(from: TilePos, to: TilePos, mover: Unit): TilePos {
    const range = this.computeMoveRange(mover);
    let best: TilePos | null = null;
    let bestD = Infinity;
    for (const [k, v] of range) {
      if (v.cost === Infinity) continue; // 不可停留
      const p = this.parseKey(k);
      const d = PathFinding.dist(p, to);
      if (d < bestD) { bestD = d; best = p; }
    }
    return best ?? from;
  }
}
