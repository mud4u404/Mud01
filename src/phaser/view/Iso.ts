import { TILE_H, TILE_RISE, TILE_W } from '../../core/constants';
import type { Terrain, TilePos } from '../../core/types';

// ===== 等距坐标转换 =====
export const GRID_ORIGIN_X = 864;   // 世界原点（tile 0,0 的菱形中心）
export const GRID_ORIGIN_Y = 120;
export const WORLD_W = 1760;
export const WORLD_H = 1000;

export function tileToWorld(p: TilePos): { x: number; y: number } {
  return {
    x: GRID_ORIGIN_X + (p.x - p.y) * (TILE_W / 2),
    y: GRID_ORIGIN_Y + (p.x + p.y) * (TILE_H / 2),
  };
}

export function worldToTile(wx: number, wy: number): TilePos {
  const fx = (wx - GRID_ORIGIN_X) / (TILE_W / 2);
  const fy = (wy - GRID_ORIGIN_Y) / (TILE_H / 2);
  return {
    x: Math.floor((fy + fx) / 2),
    y: Math.floor((fy - fx) / 2),
  };
}

/** 单位站立点（山顶单位抬高） */
export function unitStandPos(p: TilePos, terrain: Terrain): { x: number; y: number } {
  const w = tileToWorld(p);
  return { x: w.x, y: w.y - (terrain === 'mountain' ? TILE_RISE : 0) - 6 };
}

/** 菱形多边形顶点（以中心 cx,cy） */
export function diamondPoints(cx: number, cy: number, w = TILE_W, h = TILE_H): number[] {
  return [cx, cy - h / 2, cx + w / 2, cy, cx, cy + h / 2, cx - w / 2, cy];
}

/** 深度排序键 */
export function depthOf(p: TilePos): number {
  return (p.x + p.y) * 10;
}
