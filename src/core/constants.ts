import type { Element, Terrain } from './types';

// ===== 等距网格常量 =====
export const TILE_W = 128;
export const TILE_H = 64;
export const GRID_COLS = 16;
export const GRID_ROWS = 11;
export const TILE_RISE = 46;      // 山体抬升高度
export const UNIT_SPRITE_H = 132; // 战场单位显示高度

export const CANVAS_W = 1600;
export const CANVAS_H = 900;

// ===== 元素相克：对立互克 1.3x =====
export const ELEMENT_OPPOSITES: Record<Element, Element> = {
  fire: 'ice', ice: 'fire',
  thunder: 'wind', wind: 'thunder',
  light: 'dark', dark: 'light',
  none: 'none',
};
export const ELEMENT_ADVANTAGE = 1.3;

export const ELEMENT_INFO: Record<Element, { name: string; icon: string; color: number; css: string }> = {
  fire:    { name: '炎', icon: '🔥', color: 0xff6b35, css: '#ff6b35' },
  ice:     { name: '冰', icon: '❄️', color: 0x5ec8f2, css: '#5ec8f2' },
  thunder: { name: '雷', icon: '⚡', color: 0xf7e05a, css: '#f7e05a' },
  wind:    { name: '风', icon: '🌪️', color: 0x7fe08c, css: '#7fe08c' },
  light:   { name: '光', icon: '✨', color: 0xffe9a8, css: '#ffe9a8' },
  dark:    { name: '暗', icon: '🌑', color: 0xb07ae0, css: '#b07ae0' },
  none:    { name: '无', icon: '⬦', color: 0xaaaaaa, css: '#aaaaaa' },
};

// ===== 地形属性 =====
export const TERRAIN_INFO: Record<Terrain, { name: string; cost: number; defBonus: number; avoid: number; tint: number }> = {
  plain:    { name: '平原', cost: 1, defBonus: 0, avoid: 0, tint: 0x8fbf6a },
  road:     { name: '道路', cost: 1, defBonus: 0, avoid: 0, tint: 0xc9b48a },
  forest:   { name: '森林', cost: 2, defBonus: 0.15, avoid: 15, tint: 0x4f8f52 },
  mountain: { name: '山地', cost: 3, defBonus: 0.3, avoid: 10, tint: 0x9a8f82 },
  wall:     { name: '屏障', cost: Infinity, defBonus: 0, avoid: 0, tint: 0x6a6a72 },
};

// ===== 战斗公式常量 =====
export const BASE_HIT = 96;
export const BASE_CRIT = 5;
export const CRIT_MULT = 1.5;
export const COUNTER_POWER = 0.75;
export const VARIANCE = 0.1;      // ±10%
export const EXP_CURVE = (lv: number) => 40 + (lv - 1) * 45;
export const MAX_LEVEL = 20;
