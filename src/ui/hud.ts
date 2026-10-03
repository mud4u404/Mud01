// ===== DOM HUD：回合序列 / 指令菜单 / 单位信息 / 对话 / 结算 =====
import { ELEMENT_INFO, EXP_CURVE, TERRAIN_INFO } from '../core/constants';
import type {
  ChapterDef, DialogueLine, ForecastResult, ItemDef, Skill, Stats, Terrain, Unit,
} from '../core/types';
import { Sfx } from '../audio/Sfx';
import { getSkill } from '../simulation/content/skills';
import { getItem } from '../simulation/content/items';
import type { BattleSystem, InventoryEntry } from '../simulation/systems/BattleSystem';
import { CombatResolver } from '../simulation/systems/CombatResolver';

const DESIGN_W = 1600;
const DESIGN_H = 900;

function $id<T extends HTMLElement = HTMLElement>(id: string): T {
  return document.getElementById(id) as T;
}

function h(html: string): HTMLElement {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild as HTMLElement;
}

function portraitUrl(portraitKey: string): string {
  return `assets/portraits/${portraitKey.replace(/^por-/, '')}.png`;
}

/** 带立绘 + 加载失败回退的容器 */
function portraitBlock(portraitKey: string, element: keyof typeof ELEMENT_INFO, cls: string, alt = ''): HTMLElement {
  const box = h(`<div class="${cls}"><div class="ph">${ELEMENT_INFO[element].icon}</div></div>`);
  const img = document.createElement('img');
  img.src = portraitUrl(portraitKey);
  img.alt = alt;
  img.onerror = () => img.remove();
  img.onload = () => box.querySelector('.ph')?.remove();
  box.prepend(img);
  return box;
}

function unitPortrait(unit: Unit, cls: string): HTMLElement {
  return portraitBlock(unit.portraitKey, unit.element, cls, unit.name);
}

function elChip(unit: Unit, size = 26): string {
  const info = ELEMENT_INFO[unit.element];
  return `<span class="el-chip" style="width:${size}px;height:${size}px;color:${info.css};border-color:${info.css}55;background:${info.css}1c">${info.icon}</span>`;
}

function bar(cls: string, ratio: number): string {
  return `<div class="bar ${cls}"><div class="fill" style="width:${Math.max(0, Math.min(1, ratio)) * 100}%"></div></div>`;
}

const STAT_NAMES: Partial<Record<keyof Stats, string>> = {
  hp: '体力', mp: '魔力', atk: '攻击', def: '防御',
  mag: '法强', res: '魔抗', spd: '速度', mov: '移动', luk: '幸运',
};

export interface CommandMenuOpts {
  x: number; y: number;
  canAttack: boolean; canSkill: boolean; canItem: boolean; canUndo: boolean;
  onAttack: () => void;
  onSkill: () => void;
  onItem: () => void;
  onWait: () => void;
  onUndo: () => void;
}

export interface ResultScreenOpts {
  victory: boolean;
  isEnding: boolean;
  chapter: ChapterDef;
  round: number;
  gold: number;
  units: Unit[];
  onContinue: () => void;
}

class Hud {
  private shownUnitKey = '';
  private typingTimer: number | null = null;
  private dialogueLines: DialogueLine[] = [];
  private dialogueIdx = 0;
  private dialogueDone: (() => void) | null = null;
  private hintTimer = 0;

  // ===== 总控 =====
  hideAll() {
    for (const id of [
      'objective-chip', 'turn-order', 'unit-card', 'command-menu', 'skill-menu',
      'item-menu', 'forecast-panel', 'dialogue-box', 'turn-banner', 'chapter-banner',
      'levelup-banner', 'cutin-banner', 'result-screen', 'hint-bar',
    ]) {
      $id(id).classList.add('hidden');
    }
    this.shownUnitKey = '';
  }

  setMuteState() { /* 预留：全局静音状态同步 */ }

  toggleMute() {
    Sfx.muted = !Sfx.muted;
    this.showHint(Sfx.muted ? '🔇 音效已关闭（按 M 切换）' : '🔊 音效已开启');
  }

  // ===== 目标 chip =====
  showObjective(chapter: ChapterDef) {
    const el = $id('objective-chip');
    const isBoss = chapter.mapId === 'map_fortress';
    el.innerHTML = `
      <div class="obj-ico">⚔️</div>
      <div>
        <div class="obj-title">${chapter.title}</div>
        <div class="obj-goal">作战目标：${isBoss ? '讨伐魔王 <b>堕落骑士·卡奥斯</b>' : '歼灭 <b>所有敌军</b>'} · ${chapter.subtitle}</div>
      </div>`;
    el.classList.remove('hidden');
  }

  // ===== 回合序列 =====
  renderTurnOrder(units: Unit[], activeId: string, round: number) {
    const el = $id('turn-order');
    const rows = units.map(u => `
      <div class="to-row ${u.faction} ${u.id === activeId ? 'active' : ''}">
        ${elChip(u)}
        <span class="nm">${u.isBoss ? '☠ ' : ''}${u.name}</span>
        <span class="sp">速${u.stats.spd}</span>
      </div>`).join('');
    el.innerHTML = `
      <div class="to-head"><span class="t">行动顺序</span><span class="r">回合 <b>${round}</b></span></div>
      ${rows}`;
    el.classList.remove('hidden');
  }

  // ===== 单位信息卡 =====
  showUnitCard(unit: Unit, terrain: Terrain) {
    const key = `${unit.id}:${unit.hp}:${unit.mp}:${unit.buffs.length}:${unit.level}`;
    if (key === this.shownUnitKey) return;
    this.shownUnitKey = key;

    const el = $id('unit-card');
    const info = ELEMENT_INFO[unit.element];
    const ti = TERRAIN_INFO[terrain];
    const hpRatio = unit.hp / unit.stats.hp;
    const hpCls = hpRatio > 0.55 ? '' : hpRatio > 0.28 ? 'mid' : 'low';

    const statGrid = (['atk', 'def', 'mag', 'res', 'spd', 'mov', 'luk'] as Array<keyof Stats>)
      .map(k => `<div class="st"><span>${STAT_NAMES[k]}</span><b>${unit.stats[k]}</b></div>`).join('');
    const expCell = unit.faction === 'player'
      ? `<div class="st"><span>经验</span><b>${unit.exp}/${EXP_CURVE(unit.level)}</b></div>`
      : `<div class="st"><span>强度</span><b>Lv.${unit.level}</b></div>`;

    const buffs = unit.buffs.map(b =>
      `<span class="buff-chip">${b.stat === 'atk' ? '⚔' : b.stat === 'def' ? '🛡' : '🎯'} ${b.label} · ${Math.min(b.turns, 99)}回合</span>`).join('');

    el.innerHTML = `
      <div class="uc-top">
        ${'' /* portrait injected */}
        <div style="flex:1;min-width:0">
          <div class="uc-name">${unit.name}${unit.isBoss ? ' <span style="color:#ff4d5e">☠</span>' : ''}</div>
          <div class="uc-title">${unit.title ?? unit.cls} · ${unit.cls}</div>
          <div class="uc-tags">
            <span class="tag lv">Lv.${unit.level}</span>
            <span class="tag el" style="color:${info.css};border-color:${info.css}66;background:${info.css}14">${info.icon} ${info.name}属性</span>
          </div>
        </div>
      </div>
      <div class="bars">
        <div class="bar-row"><span class="lbl">HP</span>${bar('hp ' + hpCls, hpRatio)}<span class="val">${unit.hp}/${unit.stats.hp}</span></div>
        ${unit.stats.mp > 0 ? `<div class="bar-row"><span class="lbl">MP</span>${bar('mp', unit.mp / unit.stats.mp)}<span class="val">${unit.mp}/${unit.stats.mp}</span></div>` : ''}
      </div>
      <div class="uc-stats">${statGrid}${expCell}</div>
      <div class="uc-terrain">⛰ <span class="tn">${ti.name}</span>${ti.defBonus ? ` · 防御+${Math.round(ti.defBonus * 100)}%` : ''}${ti.avoid ? ` · 回避+${ti.avoid}` : ''}</div>
      ${buffs ? `<div class="uc-buffs">${buffs}</div>` : ''}
    `;
    el.querySelector('.uc-top')!.prepend(unitPortrait(unit, 'uc-portrait'));
    el.classList.remove('hidden');
  }

  hideUnitCard() {
    $id('unit-card').classList.add('hidden');
    this.shownUnitKey = '';
  }

  // ===== 指令菜单 =====
  openCommandMenu(opts: CommandMenuOpts) {
    const el = $id('command-menu');
    el.innerHTML = `
      <button class="cmd-btn accent" data-a="attack" ${opts.canAttack ? '' : 'disabled'}><span class="ci">⚔️</span>攻击</button>
      <button class="cmd-btn" data-a="skill" ${opts.canSkill ? '' : 'disabled'}><span class="ci">✦</span>技能</button>
      <button class="cmd-btn" data-a="item" ${opts.canItem ? '' : 'disabled'}><span class="ci">🧪</span>道具</button>
      <button class="cmd-btn" data-a="undo" ${opts.canUndo ? '' : 'disabled'}><span class="ci">↩️</span>撤销</button>
      <button class="cmd-btn" data-a="wait"><span class="ci">⏳</span>待机</button>`;

    const x = Math.max(14, Math.min(opts.x - 60, DESIGN_W - 158));
    const y = Math.max(76, Math.min(opts.y - 80, DESIGN_H - 320));
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;

    el.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', ev => {
        ev.stopPropagation();
        const a = (btn as HTMLElement).dataset.a;
        if (a === 'attack') { Sfx.play('confirm'); opts.onAttack(); }
        else if (a === 'skill') { Sfx.play('confirm'); opts.onSkill(); }
        else if (a === 'item') { Sfx.play('confirm'); opts.onItem(); }
        else if (a === 'undo') { Sfx.play('cancel'); opts.onUndo(); }
        else if (a === 'wait') { Sfx.play('select'); opts.onWait(); }
      });
    });
    el.classList.remove('hidden');
  }

  // ===== 技能菜单 =====
  openSkillMenu(unit: Unit, system: BattleSystem, onPick: (sid: string) => void, onCancel: () => void) {
    const el = $id('skill-menu');
    const rows = unit.skills.map(sid => {
      const sk = getSkill(sid);
      const ok = system.canUseSkill(unit, sid);
      const mp = sk.mp > 0 ? `<span class="si-mp ${ok ? '' : 'no'}">MP ${sk.mp}</span>` : '';
      const kindText = sk.damageType === 'heal' ? '治疗' : sk.damageType === 'buff' ? '辅助' : `${sk.power.toFixed(1)}倍`;
      return `
        <div class="skill-item ${ok ? '' : 'off'}" data-sid="${sid}">
          <div class="si-ico">${sk.icon}</div>
          <div class="si-body">
            <div class="si-name">${sk.name} ${mp}</div>
            <div class="si-desc">${sk.desc}</div>
          </div>
          <div class="si-meta">射程 ${sk.range} · ${kindText}</div>
        </div>`;
    }).join('');

    el.innerHTML = `
      <div class="menu-title-row">
        <div class="mt">${unit.name} 的技能</div>
        <button class="menu-back">返回 (ESC)</button>
      </div>
      <div class="skill-list">${rows || '<div style="padding:20px;text-align:center;color:var(--ink-dim)">尚未习得任何技能</div>'}</div>`;

    el.querySelectorAll('.skill-item').forEach(item => {
      item.addEventListener('click', () => {
        if (item.classList.contains('off')) { Sfx.play('cancel'); return; }
        Sfx.play('confirm');
        onPick((item as HTMLElement).dataset.sid!);
      });
    });
    el.querySelector('.menu-back')!.addEventListener('click', () => { Sfx.play('cancel'); onCancel(); });
    el.classList.remove('hidden');
  }

  // ===== 物品菜单 =====
  openItemMenu(inventory: InventoryEntry[], onPick: (iid: string) => void, onCancel: () => void) {
    const el = $id('item-menu');
    const rows = inventory.map(e => {
      const it = getItem(e.id);
      if (!it) return '';
      return `
        <div class="skill-item" data-iid="${it.id}">
          <div class="si-ico">${it.icon}</div>
          <div class="si-body">
            <div class="si-name">${it.name}</div>
            <div class="si-desc">${it.desc}</div>
          </div>
          <div class="si-count">×${e.count}</div>
        </div>`;
    }).join('');

    el.innerHTML = `
      <div class="menu-title-row">
        <div class="mt">行囊</div>
        <button class="menu-back">返回 (ESC)</button>
      </div>
      <div class="skill-list">${rows || '<div style="padding:20px;text-align:center;color:var(--ink-dim)">行囊空空如也</div>'}</div>`;

    el.querySelectorAll('.skill-item').forEach(item => {
      item.addEventListener('click', () => {
        Sfx.play('confirm');
        onPick((item as HTMLElement).dataset.iid!);
      });
    });
    el.querySelector('.menu-back')!.addEventListener('click', () => { Sfx.play('cancel'); onCancel(); });
    el.classList.remove('hidden');
  }

  closeMenus() {
    for (const id of ['command-menu', 'skill-menu', 'item-menu', 'forecast-panel']) {
      $id(id).classList.add('hidden');
    }
  }

  // ===== 战斗预测 =====
  showForecast(
    actor: Unit, target: Unit, skill: Skill | undefined,
    data: number | ForecastResult,
    onOk: () => void, onCancel: () => void,
  ) {
    const el = $id('forecast-panel');
    const isHeal = typeof data === 'number';
    const fc = isHeal ? null : data as ForecastResult;
    const dmg = isHeal ? (data as number) : fc!.damage;

    const title = skill ? `技能 · ${skill.name}` : '普通攻击';
    const midStats = isHeal
      ? `<div class="fc-stat dmg"><span>治疗量</span><b style="color:var(--green)">+${dmg}</b></div>
         <div class="fc-stat hit"><span>命中</span><b>100%</b></div>`
      : `<div class="fc-stat dmg"><span>预期伤害</span><b>${dmg}</b></div>
         <div class="fc-stat hit"><span>命中率</span><b>${fc!.hit}%</b></div>
         <div class="fc-stat crit"><span>会心率</span><b>${fc!.crit}%</b></div>`;
    const badges = isHeal
      ? `<span class="fbadge heal">恢复</span>`
      : `${fc!.lethal ? '<span class="fbadge lethal">致命一击</span>' : ''}${fc!.effective ? '<span class="fbadge eff">属性克制 ▲</span>' : ''}`;

    el.innerHTML = `
      <div class="fc-head">
        <span class="fc-title" style="color:${skill ? ELEMENT_INFO[skill.element].css : '#e8eaf2'}">${title}</span>
      </div>
      <div class="fc-body">
        <div class="fc-side atk">
          ${''}
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#9fd0ff">${actor.name}</div>
            <div class="fi-sub">Lv.${actor.level} · ${actor.cls}</div>
          </div>
        </div>
        <div class="fc-mid">${midStats}<div class="fc-badges">${badges}</div></div>
        <div class="fc-side def">
          ${''}
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#ff9da6">${target.name}</div>
            <div class="fi-sub">HP ${target.hp}/${target.stats.hp}${isHeal ? ` → <b style="color:var(--green)">${Math.min(target.stats.hp, target.hp + dmg)}</b>` : ''}</div>
          </div>
        </div>
      </div>
      <div class="fc-actions">
        <button class="btn primary">${isHeal ? '施放' : '执行'}</button>
        <button class="btn">取消</button>
      </div>`;

    el.querySelector('.fc-side.atk')!.prepend(unitPortrait(actor, 'fp'));
    el.querySelector('.fc-side.def')!.prepend(unitPortrait(target, 'fp'));

    el.querySelectorAll('.fc-actions .btn').forEach((b, i) => {
      b.addEventListener('click', ev => {
        ev.stopPropagation();
        if (i === 0) { Sfx.play('confirm'); onOk(); }
        else { Sfx.play('cancel'); onCancel(); }
      });
    });
    el.classList.remove('hidden');
  }

  hideForecast() {
    $id('forecast-panel').classList.add('hidden');
  }

  /** 自身增益技能确认 */
  showSkillConfirm(unit: Unit, skill: Skill, onOk: () => void, onCancel: () => void) {
    const buff = skill.buff!;
    const statName = buff.stat === 'atk' ? '攻击' : buff.stat === 'def' ? '防御' : '幸运';
    const el = $id('forecast-panel');
    el.innerHTML = `
      <div class="fc-head"><span class="fc-title" style="color:${ELEMENT_INFO[skill.element].css}">技能 · ${skill.name}</span></div>
      <div class="fc-body">
        <div class="fc-side atk">
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#9fd0ff">${unit.name}</div>
            <div class="fi-sub">Lv.${unit.level} · ${unit.cls}</div>
          </div>
        </div>
        <div class="fc-mid">
          <div class="fc-stat hit"><span>消耗 MP</span><b>${skill.mp}</b></div>
          <div class="fc-stat crit"><span>${statName}</span><b>+${Math.round((buff.mult - 1) * 100)}%</b></div>
          <div class="fc-stat"><span>持续</span><b>${buff.turns} 回合</b></div>
          <div class="fc-badges"><span class="fbadge heal">自身强化</span></div>
        </div>
        <div class="fc-side def">
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#ffe9a8">${skill.icon} ${skill.name}</div>
            <div class="fi-sub">${skill.desc}</div>
          </div>
        </div>
      </div>
      <div class="fc-actions">
        <button class="btn primary">施放</button>
        <button class="btn">取消</button>
      </div>`;
    el.querySelector('.fc-side.atk')!.prepend(unitPortrait(unit, 'fp'));
    el.querySelectorAll('.fc-actions .btn').forEach((b, i) => {
      b.addEventListener('click', ev => {
        ev.stopPropagation();
        if (i === 0) { Sfx.play('confirm'); onOk(); }
        else { Sfx.play('cancel'); onCancel(); }
      });
    });
    el.classList.remove('hidden');
  }

  /** 范围技能确认（波及预览） */
  showBlastConfirm(actor: Unit, skill: Skill, affected: Unit[], system: BattleSystem, onOk: () => void, onCancel: () => void) {
    const el = $id('forecast-panel');
    const chips = affected.map(t => {
      const { dmg } = CombatResolver.expectedDamage(actor, t, system.terrainAt(t.pos), skill);
      return `<span class="fc-target-chip">${t.name}<i>-${dmg}</i>${dmg >= t.hp ? ' ☠' : ''}</span>`;
    }).join('');

    el.innerHTML = `
      <div class="fc-head"><span class="fc-title" style="color:${ELEMENT_INFO[skill.element].css}">范围技能 · ${skill.name}</span></div>
      <div class="fc-targets">${chips || '<span class="fc-target-chip">该区域没有目标</span>'}</div>
      <div class="fc-actions">
        <button class="btn primary">释放</button>
        <button class="btn">取消</button>
      </div>`;
    el.querySelectorAll('.fc-actions .btn').forEach((b, i) => {
      b.addEventListener('click', ev => {
        ev.stopPropagation();
        if (i === 0) { Sfx.play('confirm'); onOk(); }
        else { Sfx.play('cancel'); onCancel(); }
      });
    });
    el.classList.remove('hidden');
  }

  /** 道具确认 */
  showItemConfirm(actor: Unit, target: Unit, item: ItemDef, onOk: () => void, onCancel: () => void) {
    const el = $id('forecast-panel');
    const eff: string[] = [];
    if (item.effect.hp) eff.push(`HP +${item.effect.hp}`);
    if (item.effect.mp) eff.push(`MP +${item.effect.mp}`);
    if (item.effect.revive) eff.push('复苏倒下的同伴');
    const hpAfter = item.effect.hp
      ? Math.min(target.stats.hp, target.hp + item.effect.hp)
      : target.hp;

    el.innerHTML = `
      <div class="fc-head"><span class="fc-title" style="color:#9fd0ff">道具 · ${item.name}</span></div>
      <div class="fc-body">
        <div class="fc-side atk">
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#9fd0ff">${actor.name}</div>
            <div class="fi-sub">使用者</div>
          </div>
        </div>
        <div class="fc-mid">
          <div class="fc-stat dmg"><span>效果</span><b style="color:var(--green)">${eff.join(' / ')}</b></div>
          <div class="fc-stat"><span>目标 HP</span><b>${target.hp} → ${hpAfter}</b></div>
        </div>
        <div class="fc-side def">
          <div style="flex:1;min-width:0">
            <div class="fi-name" style="color:#ff9da6">${target.name}</div>
            <div class="fi-sub">HP ${target.hp}/${target.stats.hp}</div>
          </div>
        </div>
      </div>
      <div class="fc-actions">
        <button class="btn primary">使用</button>
        <button class="btn">取消</button>
      </div>`;
    el.querySelector('.fc-side.atk')!.prepend(unitPortrait(actor, 'fp'));
    el.querySelector('.fc-side.def')!.prepend(unitPortrait(target, 'fp'));
    el.querySelectorAll('.fc-actions .btn').forEach((b, i) => {
      b.addEventListener('click', ev => {
        ev.stopPropagation();
        if (i === 0) { Sfx.play('confirm'); onOk(); }
        else { Sfx.play('cancel'); onCancel(); }
      });
    });
    el.classList.remove('hidden');
  }

  // ===== 对话 =====
  showDialogue(lines: DialogueLine[], onDone: () => void) {
    this.dialogueLines = lines;
    this.dialogueIdx = 0;
    this.dialogueDone = onDone;
    $id('dialogue-box').classList.remove('hidden');
    this.showLine();
  }

  private showLine() {
    const line = this.dialogueLines[this.dialogueIdx];
    if (!line) { this.endDialogue(); return; }
    const box = $id('dialogue-box');
    const hasPortrait = !!line.speaker;

    box.innerHTML = `
      <div class="db-inner">
        ${hasPortrait ? '' : ''}
        <div class="db-right">
          ${line.name ? `<div class="db-name">${line.name}</div>` : ''}
          <div class="db-text ${hasPortrait ? '' : 'narr'}"></div>
          <div class="db-next">▼ 点击继续</div>
        </div>
      </div>`;
    if (hasPortrait) {
      box.querySelector('.db-inner')!.prepend(portraitBlock(line.speaker, 'none', 'db-portrait', line.name));
    }

    const textEl = box.querySelector('.db-text') as HTMLElement;
    if (hasPortrait) {
      textEl.style.color = 'var(--ink)';
    } else {
      textEl.style.color = '#b8c2d8';
      textEl.style.fontStyle = 'italic';
      textEl.style.paddingTop = '26px';
    }

    // 打字机
    if (this.typingTimer) { clearInterval(this.typingTimer); this.typingTimer = null; }
    let i = 0;
    this.typingTimer = window.setInterval(() => {
      i += 2;
      textEl.textContent = line.text.slice(0, i);
      if (i >= line.text.length) {
        if (this.typingTimer) clearInterval(this.typingTimer);
        this.typingTimer = null;
      }
    }, 34);
  }

  /** 对话是否正在展示 */
  isDialogueActive(): boolean {
    return !$id('dialogue-box').classList.contains('hidden');
  }

  advanceDialogue() {
    const box = $id('dialogue-box');
    if (box.classList.contains('hidden')) return;
    const line = this.dialogueLines[this.dialogueIdx];
    if (!line) return;
    const textEl = box.querySelector('.db-text') as HTMLElement | null;
    if (!textEl) return;
    if (this.typingTimer) {
      // 快进当前句
      clearInterval(this.typingTimer);
      this.typingTimer = null;
      textEl.textContent = line.text;
      return;
    }
    if (textEl.textContent !== line.text) return;
    this.dialogueIdx++;
    Sfx.play('select');
    this.showLine();
  }

  private endDialogue() {
    $id('dialogue-box').classList.add('hidden');
    const cb = this.dialogueDone;
    this.dialogueDone = null;
    cb?.();
  }

  // ===== 横幅 =====
  showTurnBanner(text: string, color: string): Promise<void> {
    return new Promise(resolve => {
      const el = $id('turn-banner');
      el.innerHTML = `<div class="tb-band"></div><div class="tb-text" style="color:${color}">${text}</div>`;
      el.classList.remove('hidden');
      window.setTimeout(() => {
        el.classList.add('hidden');
        resolve();
      }, 1150);
    });
  }

  showChapterBanner(chapter: ChapterDef): Promise<void> {
    return new Promise(resolve => {
      const el = $id('chapter-banner');
      el.innerHTML = `
        <div class="cb-no">— CHAPTER ${String(chapter.id).padStart(2, '0')} —</div>
        <div class="cb-title">${chapter.title}</div>
        <div class="cb-sep"><span class="line"></span><span class="dia">◆</span><span class="line"></span></div>
        <div class="cb-sub">${chapter.subtitle}</div>`;
      el.classList.remove('hidden');
      window.setTimeout(() => {
        el.classList.add('hidden');
        resolve();
      }, 2500);
    });
  }

  showLevelUp(unit: Unit, gains: Partial<Stats>) {
    const el = $id('levelup-banner');
    const chips = (Object.keys(gains) as Array<keyof Stats>)
      .map(k => `<span class="lu-g">${STAT_NAMES[k] ?? k} +${gains[k]}</span>`).join('');
    el.innerHTML = `<div class="lu-title">⬆ ${unit.name} 提升至 Lv.${unit.level}</div><div class="lu-gains">${chips}</div>`;
    el.classList.remove('hidden');
    window.setTimeout(() => el.classList.add('hidden'), 2400);
  }

  showCutIn(unit: Unit, skill: Skill): Promise<void> {
    return new Promise(resolve => {
      const el = $id('cutin-banner');
      const color = ELEMENT_INFO[skill.element].css;
      el.innerHTML = `
        <div class="cut-streak" style="color:${color}">
          <div class="cut-portrait"></div>
          <div class="cut-text">
            <div class="cut-who">${unit.name} · ${unit.title ?? unit.cls}</div>
            <div class="cut-skill">${skill.name}</div>
            <div class="cut-line"></div>
          </div>
        </div>`;
      el.querySelector('.cut-portrait')!.append(unitPortrait(unit, 'cut-inner'));
      el.classList.remove('hidden');
      window.setTimeout(() => {
        el.classList.add('hidden');
        resolve();
      }, 950);
    });
  }

  // ===== 提示条 =====
  showHint(text: string) {
    const el = $id('hint-bar');
    window.clearTimeout(this.hintTimer);
    if (!text) { el.classList.add('hidden'); return; }
    el.textContent = text;
    el.classList.remove('hidden');
    // 常驻提示不自动消失；短暂提示（音效开关）2.4s 后隐藏
    if (text.startsWith('🔊') || text.startsWith('🔇')) {
      this.hintTimer = window.setTimeout(() => el.classList.add('hidden'), 2400);
    }
  }

  // ===== 结算 =====
  showResultScreen(opts: ResultScreenOpts) {
    const el = $id('result-screen');
    const kills = opts.units.reduce((s, u) => s + u.kills, 0);
    const alive = opts.units.filter(u => u.alive).length;

    const roster = opts.units.map(u => `
      <div class="rs-unit ${u.alive ? '' : 'dead'}">
        <div class="rup"></div>
        <div class="rn">${u.name}</div>
        <div class="rl">Lv.${u.level}</div>
        <div class="rk">击破 <b>${u.kills}</b></div>
      </div>`).join('');

    el.innerHTML = `
      <div class="rs-title" style="color:${opts.victory ? 'var(--gold-bright)' : '#8a93a8'}">${opts.victory ? '胜  利' : '败  北'}</div>
      <div class="rs-sub">${opts.chapter.title} · ${opts.chapter.subtitle}</div>
      <div class="rs-stats">
        <div class="rs-stat"><div class="v">${opts.round}</div><div class="k">经过回合</div></div>
        <div class="rs-stat"><div class="v">${kills}</div><div class="k">歼灭数</div></div>
        <div class="rs-stat"><div class="v">${alive}/${opts.units.length}</div><div class="k">存活</div></div>
        <div class="rs-stat"><div class="v">+${opts.gold}</div><div class="k">金币</div></div>
      </div>
      <div class="rs-roster">${roster}</div>
      <button class="btn primary big">
        ${opts.victory ? (opts.isEnding ? '完结 · 返回标题' : '进军下一章') : '重整旗鼓 · 再战'}
      </button>`;

    el.querySelectorAll('.rs-unit').forEach((node, i) => {
      node.querySelector('.rup')!.append(unitPortrait(opts.units[i], 'rs-img'));
    });

    el.querySelector('button')!.addEventListener('click', () => {
      Sfx.play('confirm');
      el.classList.add('hidden');
      opts.onContinue();
    });
    el.classList.remove('hidden');
  }
}

// 对话框点击 / 空格 / 回车 → 推进
document.addEventListener('DOMContentLoaded', () => {
  $id('dialogue-box').addEventListener('click', () => hud.advanceDialogue());
  window.addEventListener('keydown', (e) => {
    if (e.code !== 'Space' && e.code !== 'Enter') return;
    const box = $id('dialogue-box');
    if (box.classList.contains('hidden')) return;
    e.preventDefault();
    hud.advanceDialogue();
  });
});

export const hud = new Hud();
