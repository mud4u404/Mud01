// ===== Web Audio 合成音效 =====
// 轻量级程序化音效：不依赖任何音频文件。

type SfxName =
  | 'select' | 'confirm' | 'cancel' | 'move' | 'turn'
  | 'slash' | 'hit' | 'crit' | 'fire' | 'ice' | 'thunder' | 'wind' | 'light' | 'dark' | 'heal' | 'buff'
  | 'death' | 'levelup' | 'victory' | 'defeat' | 'boss';

class SfxEngine {
  private ctx: AudioContext | null = null;
  private master: GainNode | null = null;
  muted = false;

  private ensure(): AudioContext | null {
    if (this.ctx) return this.ctx;
    try {
      const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AC();
      this.master = this.ctx.createGain();
      this.master.gain.value = 0.32;
      this.master.connect(this.ctx.destination);
    } catch {
      return null;
    }
    return this.ctx;
  }

  resume() {
    const ctx = this.ensure();
    if (ctx && ctx.state === 'suspended') ctx.resume();
  }

  private tone(freq: number, dur: number, type: OscillatorType, vol: number, delay = 0, slideTo?: number) {
    const ctx = this.ensure();
    if (!ctx || !this.master || this.muted) return;
    const t0 = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t0);
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(Math.max(1, slideTo), t0 + dur);
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(vol, t0 + 0.012);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    osc.connect(g); g.connect(this.master);
    osc.start(t0); osc.stop(t0 + dur + 0.05);
  }

  private noise(dur: number, vol: number, delay = 0, lowpass = 3200, highpass = 0) {
    const ctx = this.ensure();
    if (!ctx || !this.master || this.muted) return;
    const t0 = ctx.currentTime + delay;
    const len = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource();
    src.buffer = buf;
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, t0);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    let node: AudioNode = src;
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass'; lp.frequency.value = lowpass;
    node.connect(lp); node = lp;
    if (highpass > 0) {
      const hp = ctx.createBiquadFilter();
      hp.type = 'highpass'; hp.frequency.value = highpass;
      node.connect(hp); node = hp;
    }
    node.connect(g); g.connect(this.master);
    src.start(t0);
  }

  play(name: SfxName) {
    if (this.muted) return;
    switch (name) {
      case 'select': this.tone(660, 0.06, 'square', 0.12); break;
      case 'confirm': this.tone(520, 0.07, 'square', 0.14); this.tone(780, 0.1, 'square', 0.12, 0.06); break;
      case 'cancel': this.tone(420, 0.09, 'square', 0.1, 0, 280); break;
      case 'move': this.noise(0.12, 0.1, 0, 900); break;
      case 'turn': this.tone(392, 0.12, 'triangle', 0.16); this.tone(523, 0.16, 'triangle', 0.14, 0.09); break;
      case 'slash': this.noise(0.16, 0.28, 0, 5200, 900); this.tone(290, 0.1, 'sawtooth', 0.1, 0, 120); break;
      case 'hit':
        this.noise(0.14, 0.3, 0, 1600);
        this.tone(160, 0.12, 'square', 0.16, 0, 70);
        break;
      case 'crit':
        this.noise(0.2, 0.34, 0, 7000, 1400);
        this.tone(220, 0.16, 'sawtooth', 0.2, 0, 60);
        this.tone(1320, 0.1, 'square', 0.1, 0.02);
        break;
      case 'fire':
        this.noise(0.5, 0.22, 0, 1100);
        this.tone(90, 0.4, 'sawtooth', 0.14, 0, 45);
        this.tone(320, 0.3, 'triangle', 0.1, 0.05, 130);
        break;
      case 'ice':
        this.tone(1560, 0.3, 'sine', 0.12, 0, 780);
        this.tone(2080, 0.25, 'sine', 0.09, 0.08, 1040);
        this.noise(0.3, 0.12, 0, 8000, 3000);
        break;
      case 'thunder':
        this.noise(0.5, 0.4, 0, 9000, 2000);
        this.tone(110, 0.35, 'sawtooth', 0.22, 0, 40);
        this.tone(1800, 0.12, 'square', 0.08, 0.03, 400);
        break;
      case 'wind':
        this.noise(0.6, 0.18, 0, 2400, 500);
        this.tone(640, 0.4, 'sine', 0.08, 0.05, 940);
        break;
      case 'light':
        this.tone(784, 0.35, 'sine', 0.12);
        this.tone(1046, 0.3, 'sine', 0.1, 0.1);
        this.tone(1568, 0.4, 'sine', 0.08, 0.2);
        break;
      case 'dark':
        this.tone(140, 0.5, 'sawtooth', 0.14, 0, 60);
        this.tone(92, 0.55, 'triangle', 0.12, 0.08, 42);
        this.noise(0.4, 0.1, 0, 700);
        break;
      case 'heal':
        this.tone(523, 0.18, 'sine', 0.12);
        this.tone(659, 0.18, 'sine', 0.11, 0.1);
        this.tone(784, 0.3, 'sine', 0.1, 0.2);
        break;
      case 'buff':
        this.tone(440, 0.14, 'triangle', 0.12);
        this.tone(554, 0.14, 'triangle', 0.11, 0.08);
        this.tone(659, 0.22, 'triangle', 0.1, 0.16);
        break;
      case 'death':
        this.tone(300, 0.4, 'sawtooth', 0.16, 0, 60);
        this.noise(0.35, 0.14, 0.05, 1200);
        break;
      case 'levelup':
        [523, 659, 784, 1046].forEach((f, i) => this.tone(f, 0.16, 'square', 0.11, i * 0.09));
        break;
      case 'victory':
        [523, 659, 784, 1046, 784, 1046].forEach((f, i) => this.tone(f, 0.22, 'triangle', 0.13, i * 0.14));
        break;
      case 'defeat':
        [392, 349, 311, 262].forEach((f, i) => this.tone(f, 0.4, 'triangle', 0.13, i * 0.25));
        break;
      case 'boss':
        this.tone(80, 0.8, 'sawtooth', 0.2, 0, 50);
        this.noise(0.7, 0.2, 0, 500);
        break;
    }
  }
}

export const Sfx = new SfxEngine();
