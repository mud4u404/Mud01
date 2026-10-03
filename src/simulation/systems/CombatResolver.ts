import { BASE_CRIT, BASE_HIT, CRIT_MULT, ELEMENT_ADVANTAGE, ELEMENT_OPPOSITES, TERRAIN_INFO, VARIANCE } from '../../core/constants';
import type { Element, ForecastResult, Skill, Terrain, Unit } from '../../core/types';

export interface DamageResult {
  damage: number;
  crit: boolean;
  hit: boolean;
  elementMult: number;
  effective: boolean;
}

export class CombatResolver {
  /** 地形防御加成后的有效防御 */
  static effDef(unit: Unit, terrain: Terrain): number {
    const info = TERRAIN_INFO[terrain];
    return unit.stats.def * (1 + info.defBonus) * CombatResolver.buffMult(unit, 'def');
  }

  static effRes(unit: Unit): number {
    return unit.stats.res * CombatResolver.buffMult(unit, 'def');
  }

  static effAtk(unit: Unit): number {
    return unit.stats.atk * CombatResolver.buffMult(unit, 'atk');
  }

  static effMag(unit: Unit): number {
    return unit.stats.mag * CombatResolver.buffMult(unit, 'atk');
  }

  static effLuk(unit: Unit): number {
    return unit.stats.luk * CombatResolver.buffMult(unit, 'luk');
  }

  static buffMult(unit: Unit, stat: 'atk' | 'def' | 'luk'): number {
    let m = 1;
    for (const b of unit.buffs) if (b.stat === stat) m *= b.mult;
    return m;
  }

  static elementMultiplier(attackElement: Element, targetElement: Element): number {
    if (attackElement === 'none' || targetElement === 'none') return 1;
    if (ELEMENT_OPPOSITES[attackElement] === targetElement) return ELEMENT_ADVANTAGE;
    return 1;
  }

  /** 命中率计算 */
  static hitChance(attacker: Unit, target: Unit, terrain: Terrain): number {
    const avoid = TERRAIN_INFO[terrain].avoid;
    const spdDiff = attacker.stats.spd - target.stats.spd;
    return Math.max(55, Math.min(100, BASE_HIT + spdDiff * 2 - avoid));
  }

  /** 暴击率计算 */
  static critChance(attacker: Unit, skill?: Skill): number {
    let crit = BASE_CRIT + CombatResolver.effLuk(attacker) * 0.5;
    if (skill?.critBonus) crit += skill.critBonus;
    return Math.max(0, Math.min(80, crit));
  }

  /** 期望伤害（不含随机浮动，用于预测与 AI） */
  static expectedDamage(attacker: Unit, target: Unit, terrain: Terrain, skill?: Skill): { dmg: number; elementMult: number; effective: boolean } {
    const isMagic = skill ? skill.damageType === 'magical' : false;
    const power = skill ? skill.power : 1;
    let atkVal: number, defVal: number;
    if (isMagic) {
      atkVal = CombatResolver.effMag(attacker) * power;
      defVal = CombatResolver.effRes(target) * 0.6;
    } else {
      atkVal = CombatResolver.effAtk(attacker) * power;
      defVal = CombatResolver.effDef(target, terrain) * 0.6;
    }
    const em = skill ? CombatResolver.elementMultiplier(skill.element, target.element)
      : CombatResolver.elementMultiplier(attacker.element, target.element);
    const raw = Math.max(1, (atkVal - defVal) * em);
    return { dmg: Math.round(raw), elementMult: em, effective: em > 1 };
  }

  /** 实际伤害结算（含随机） */
  static rollDamage(attacker: Unit, target: Unit, terrain: Terrain, skill?: Skill): DamageResult {
    const { dmg, elementMult, effective } = CombatResolver.expectedDamage(attacker, target, terrain, skill);
    const variance = 1 - VARIANCE + Math.random() * VARIANCE * 2;
    const crit = Math.random() * 100 < CombatResolver.critChance(attacker, skill);
    const hit = Math.random() * 100 < CombatResolver.hitChance(attacker, target, terrain);
    if (!hit) return { damage: 0, crit: false, hit: false, elementMult, effective };
    let damage = dmg * variance;
    if (crit) damage *= CRIT_MULT;
    return { damage: Math.max(1, Math.round(damage)), crit, hit: true, elementMult, effective };
  }

  /** 治疗量 */
  static healAmount(actor: Unit, skill: Skill): number {
    return Math.round(CombatResolver.effMag(actor) * skill.power + 20);
  }

  /** 战斗预测（UI 展示 + AI 评估） */
  static forecast(attacker: Unit, target: Unit, terrain: Terrain, skill?: Skill): ForecastResult {
    const { dmg, elementMult, effective } = CombatResolver.expectedDamage(attacker, target, terrain, skill);
    return {
      damage: dmg,
      hit: CombatResolver.hitChance(attacker, target, terrain),
      crit: Math.round(CombatResolver.critChance(attacker, skill)),
      lethal: dmg >= target.hp,
      elementMult,
      effective,
    };

  }
}
