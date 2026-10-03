import type { ChapterDef, DialogueLine } from '../../core/types';

const narration = (text: string): DialogueLine => ({ speaker: '', name: '', text });

export const CHAPTERS: ChapterDef[] = [
  {
    id: 1,
    title: '序章 · 边境的烽火',
    subtitle: '苍风平原',
    mapId: 'map_plains',
    roster: ['ren', 'alice', 'roland'],
    introDialogue: [
      narration('星陨历 302 年，一颗暗星坠落大陆，黑雾自北方蔓延。'),
      narration('苍风平原，边境哨所 ——'),
      { speaker: 'por-ren', name: '雷恩', text: '……烽火台的方向，有黑雾在涌动。哥布林军队？它们从不曾如此大规模集结。' },
      { speaker: 'por-alice', name: '艾莉丝', text: '这股气息……是「星陨之瘴」。被侵蚀的魔物会变得狂暴。雷恩，小心！' },
      { speaker: 'por-roland', name: '罗兰', text: '呵，来得正好。我的弓弦已经绷了三天了。诸位 —— 列阵！' },
    ],
    victoryDialogue: [
      { speaker: 'por-roland', name: '罗兰', text: '碎兵游勇罢了。但这支军队的旗帜……我从未见过。' },
      { speaker: 'por-alice', name: '艾莉丝', text: '是「永夜军团」的徽记。传说中被星陨之瘴完全吞噬的骑士 —— 卡奥斯率领的军队。' },
      { speaker: 'por-ren', name: '雷恩', text: '卡奥斯……如果是他亲手放出的先遣队，那正主一定就在这片大陆的某处。追上去！' },
    ],
    reward: { gold: 120, items: [{ id: 'herb', count: 2 }, { id: 'mana_potion', count: 1 }] },
  },
  {
    id: 2,
    title: '第一章 · 迷雾森林',
    subtitle: '低语森林',
    mapId: 'map_forest',
    roster: ['ren', 'alice', 'roland', 'selena'],
    introDialogue: [
      narration('追击敌军残部，一行人深入低语森林。浓雾锁林，火光明灭。'),
      { speaker: 'por-selena', name: '赛琳娜', text: '站住！你们也是永夜军团的走狗吗？！圣光会制裁……呜……' },
      { speaker: 'por-ren', name: '雷恩', text: '等等！我们是来追击哥布林军队的边境卫队 —— 你受伤了。' },
      { speaker: 'por-selena', name: '赛琳娜', text: '……抱歉，我被围攻了整夜。教会的姐妹们都倒下了。请，借我一份力量！' },
      { speaker: 'por-alice', name: '艾莉丝', text: '又来了一批……雾里有兽人的吼声。赛琳娜，退到我们身后！' },
    ],
    victoryDialogue: [
      { speaker: 'por-selena', name: '赛琳娜', text: '感谢诸位……我是圣辉教的祭司赛琳娜。我此行是为调查星陨之瘴的源头。' },
      { speaker: 'por-selena', name: '赛琳娜', text: '黑雾的中心在北方的「永夜要塞」。堕落骑士卡奥斯被陨星之力彻底吞噬，正集结魔物大军。' },
      { speaker: 'por-ren', name: '雷恩', text: '那就去要塞。趁大军未成，斩断这个源头。所有人都……跟我来！' },
    ],
    reward: { gold: 200, items: [{ id: 'herb', count: 2 }, { id: 'fairy_tear', count: 1 }] },
  },
  {
    id: 3,
    title: '终章 · 永夜要塞',
    subtitle: '王座大厅',
    mapId: 'map_fortress',
    roster: ['ren', 'alice', 'roland', 'selena', 'kage'],
    introDialogue: [
      narration('穿越焦土，永夜要塞矗立眼前。黑暗如活物般在城墙上流淌。'),
      { speaker: 'por-kage', name: '影', text: '……想进要塞？跟紧我。城墙的暗门，我三年前就摸清了。' },
      { speaker: 'por-roland', name: '罗兰', text: '你是谁？刺客的气味可不太让人放心。' },
      { speaker: 'por-kage', name: '影', text: '影。卡奥斯灭了我的氏族。我来取他项上人头 —— 仅此而已。' },
      { speaker: 'por-ren', name: '雷恩', text: '够了。目标一致就是同伴。卡奥斯就在王座之上 —— 总攻，开始！' },
    ],
    victoryDialogue: [
      { speaker: 'por-chaos-knight', name: '卡奥斯', text: '呵……呵呵……星陨之力……岂会……随吾消散……' },
      narration('黑暗骑士的身体化作黑雾消散，一颗暗紫色的星核悬浮在王座之上。'),
      { speaker: 'por-selena', name: '赛琳娜', text: '这就是「星陨之核」……以圣光净化它 —— 愿逝者安息，愿大陆重获黎明。' },
      narration('晨光刺破永夜，照耀大陆。星陨幻世的传说，由五位勇士写下终章。'),
      { speaker: 'por-ren', name: '雷恩', text: '走吧，各位。回家的路还很长 —— 而且我请客。' },
      { speaker: 'por-roland', name: '罗兰', text: '哈哈，这可是你说的！' },
    ],
    reward: { gold: 500, items: [] },
  },
];

export function getChapter(id: number): ChapterDef {
  return CHAPTERS.find(c => c.id === id) ?? CHAPTERS[0];
}

export const TOTAL_CHAPTERS = CHAPTERS.length;
