(function () {
  'use strict';

  var TAU = Math.PI * 2;
  var PI = Math.PI;
  var MOTIFS = ['rings', 'bars', 'wave', 'particles', 'aurora', 'grid', 'spokes', 'bokeh', 'strings', 'stars', 'mosaic', 'smoke'];

  function col(h, s, l, a) {
    var hh = (((h % 360) + 360) % 360) | 0;
    var aa = a < 0 ? 0 : (a > 1 ? 1 : a);
    return 'hsla(' + hh + ',' + s + '%,' + l + '%,' + aa.toFixed(2) + ')';
  }

  function hash(str) {
    var x = 2166136261;
    for (var i = 0; i < str.length; i++) {
      x ^= str.charCodeAt(i);
      x = Math.imul(x, 16777619);
    }
    return x >>> 0;
  }

  function autoSpec(playlistId) {
    var id = String(playlistId == null ? '' : playlistId);
    var a = hash(id);
    var b = hash(id + '#2');
    var hue = (a >>> 4) % 360;
    return {
      motif: MOTIFS[a % MOTIFS.length],
      hue: hue,
      hue2: (hue + 70 + ((b >>> 3) % 160)) % 360,
      speed: 0.5 + ((b >>> 11) % 101) / 100,
      density: 0.4 + ((b >>> 19) % 51) / 100
    };
  }

  function roundBar(ctx, x, y, bw, bh) {
    var r = bw / 2;
    if (bh < bw) { r = bh / 2; }
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + bw - r, y);
    ctx.arc(x + bw - r, y + r, r, -PI / 2, 0);
    ctx.lineTo(x + bw, y + bh - r);
    ctx.arc(x + bw - r, y + bh - r, r, 0, PI / 2);
    ctx.lineTo(x + r, y + bh);
    ctx.arc(x + r, y + bh - r, r, PI / 2, PI);
    ctx.lineTo(x, y + r);
    ctx.arc(x + r, y + r, r, PI, PI * 1.5);
    ctx.closePath();
  }

  var builders = {};

  builders.rings = function (S) {
    var N = 12;
    var r = new Float32Array(N);
    var act = new Uint8Array(N);
    var timer = 0;
    var prev = 0;
    return function (ctx, w, h) {
      var cx = w / 2;
      var cy = h / 2;
      var m = Math.min(w, h);
      var maxR = Math.sqrt(cx * cx + cy * cy);
      timer -= S.dt;
      var strong = S.b > 0.5 && S.b > prev + 0.03 && S.calm < 0.5;
      prev = S.b;
      var interval = (1.9 - S.d * 1.2) / S.sp * (1 + S.calm);
      var i;
      if (timer <= 0 || (strong && timer < interval * 0.5)) {
        timer = interval;
        for (i = 0; i < N; i++) {
          if (!act[i]) { act[i] = 1; r[i] = m * 0.12; break; }
        }
      }
      var v = maxR * 0.22 * S.sp * (0.6 + S.e * 1.4) * S.dt;
      ctx.lineCap = 'round';
      for (i = 0; i < N; i++) {
        if (!act[i]) { continue; }
        r[i] += v;
        var k = r[i] / maxR;
        if (k >= 1) { act[i] = 0; continue; }
        var al = (1 - k) * (1 - k);
        ctx.lineWidth = 1.5 + (1 - k) * m * 0.03 * (0.5 + S.d);
        ctx.strokeStyle = col(S.mh(k), 80, 62, al * 0.9);
        ctx.beginPath();
        ctx.arc(cx, cy, r[i], 0, TAU);
        ctx.stroke();
      }
      var r0 = m * (0.09 + 0.04 * S.b + 0.01 * Math.sin(S.ph * 2));
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r0 * 2.4);
      g.addColorStop(0, col(S.h1, 85, 68, 0.95));
      g.addColorStop(0.45, col(S.mh(0.5), 85, 55, 0.55));
      g.addColorStop(1, col(S.h2, 85, 50, 0));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cx, cy, r0 * 2.4, 0, TAU);
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = col(S.h2, 85, 72, 0.8);
      ctx.beginPath();
      for (i = 0; i <= 64; i++) {
        var k2 = i % 64;
        var kk = k2 < 32 ? k2 : 63 - k2;
        var rr = r0 * 1.5 + S.fs[kk] * m * 0.12;
        var a = (i / 64) * TAU + S.ph * 0.3;
        var x = cx + Math.cos(a) * rr;
        var y = cy + Math.sin(a) * rr;
        if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
      }
      ctx.stroke();
    };
  };

  builders.bars = function (S) {
    return function (ctx, w, h) {
      var n = 14 + ((S.d * 26) | 0);
      var gap = Math.max(2, w * 0.008);
      var bw = (w - gap * (n + 1)) / n;
      var cy = h * 0.5;
      var maxH = h * 0.44;
      var g = ctx.createLinearGradient(0, cy - maxH, 0, cy + maxH);
      g.addColorStop(0, col(S.h2, 85, 66, 0.95));
      g.addColorStop(0.5, col(S.h1, 90, 62, 0.95));
      g.addColorStop(1, col(S.h2, 85, 66, 0.95));
      ctx.fillStyle = g;
      ctx.beginPath();
      for (var i = 0; i < n; i++) {
        var pos = (i / (n - 1)) * 44;
        var i0 = pos | 0;
        var f = pos - i0;
        var v = (S.fs[i0] * (1 - f) + S.fs[i0 + 1] * f) * (1 + (i / n) * 0.8);
        if (v > 1) { v = 1; }
        var bh = Math.max(bw * 0.5, v * maxH);
        roundBar(ctx, gap + i * (bw + gap), cy - bh, bw, bh * 2);
      }
      ctx.fill();
    };
  };

  builders.wave = function (S) {
    var ws = new Float32Array(128);
    return function (ctx, w, h) {
      var cy = h * 0.5;
      var n = 56;
      var i;
      var wv = S.data.wave;
      var c = S.calm;
      for (i = 0; i < 128; i++) {
        ws[i] += (((wv[i] - 128) / 128) * (1 - c) - ws[i]) * 0.35;
      }
      for (var L = 0; L < 3; L++) {
        var amp = h * (0.3 - L * 0.07) * (0.45 + S.e * 1.2);
        var px = 0;
        var py = cy;
        var hue = S.mh(L / 2);
        ctx.beginPath();
        for (i = 0; i <= n; i++) {
          var si = ((i / n) * 127) | 0;
          var env = Math.sin((PI * i) / n);
          var y = cy + (L - 1) * h * 0.08 + ws[si] * amp * (1.3 - L * 0.25) +
            Math.sin(i * 0.18 + S.ph * (1.2 + L * 0.5) + L * 2) * h * 0.035 * (0.6 + S.e) * env;
          var x = (i / n) * w;
          if (i === 0) { ctx.moveTo(x, y); } else { ctx.quadraticCurveTo(px, py, (px + x) / 2, (py + y) / 2); }
          px = x;
          py = y;
        }
        ctx.lineTo(px, py);
        ctx.lineWidth = 3 - L * 0.5;
        ctx.lineJoin = 'round';
        ctx.strokeStyle = col(hue, 88, 66, 0.95 - L * 0.15);
        ctx.stroke();
        ctx.lineTo(w, h);
        ctx.lineTo(0, h);
        ctx.closePath();
        var g = ctx.createLinearGradient(0, cy - amp, 0, h);
        g.addColorStop(0, col(hue, 85, 60, 0.3));
        g.addColorStop(1, col(hue, 85, 45, 0));
        ctx.fillStyle = g;
        ctx.fill();
      }
    };
  };

  builders.particles = function (S) {
    var MAXP = 120;
    var px = new Float32Array(MAXP);
    var py = new Float32Array(MAXP);
    var pvx = new Float32Array(MAXP);
    var pvy = new Float32Array(MAXP);
    var life = new Float32Array(MAXP);
    var size = new Float32Array(MAXP);
    var bucket = new Uint8Array(MAXP);
    var acc = 0;
    var prev = 0;
    var BK = 4;
    function spawn(w, h, strong) {
      for (var i = 0; i < MAXP; i++) {
        if (life[i] <= 0) {
          var a = Math.random() * TAU;
          var sp = (0.4 + Math.random() * 1.6) * (strong ? 1.6 : 0.7) * (0.6 + S.sp * 0.5);
          px[i] = w / 2 + (Math.random() - 0.5) * w * 0.3;
          py[i] = h * 0.65 + (Math.random() - 0.5) * h * 0.1;
          pvx[i] = Math.cos(a) * sp;
          pvy[i] = -Math.abs(Math.sin(a)) * sp * 1.4 - 0.3;
          life[i] = 1;
          size[i] = 1.5 + Math.random() * (2 + S.e * 4);
          bucket[i] = (Math.random() * BK) | 0;
          return;
        }
      }
    }
    return function (ctx, w, h) {
      var dt = S.dt;
      var cap = 40 + ((S.d * 80) | 0);
      var strong = S.b > 0.55 && S.b > prev + 0.04 && S.calm < 0.5;
      prev = S.b;
      acc += S.calm > 0.5 ? 1.2 * dt : (strong ? 6 : S.b * 70 * dt * 0.12 + S.e * 3 * dt + 2 * dt);
      var alive = 0;
      var i;
      for (i = 0; i < MAXP; i++) { if (life[i] > 0) { alive++; } }
      while (acc >= 1) {
        acc -= 1;
        if (alive < cap) { spawn(w, h, strong); alive++; }
      }
      var g = ctx.createRadialGradient(w / 2, h * 0.7, 0, w / 2, h * 0.7, h * 0.75);
      g.addColorStop(0, col(S.h1, 80, 50, 0.16 + S.e * 0.2));
      g.addColorStop(1, col(S.h2, 80, 40, 0));
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
      ctx.globalAlpha = 0.85;
      var b;
      for (b = 0; b < BK; b++) {
        ctx.fillStyle = col(S.mh(b / (BK - 1)), 90, 68, 1);
        ctx.beginPath();
        for (i = 0; i < MAXP; i++) {
          if (life[i] > 0 && bucket[i] === b) {
            var r = size[i] * (0.4 + life[i] * 0.6);
            ctx.moveTo(px[i] + r, py[i]);
            ctx.arc(px[i], py[i], r, 0, TAU);
          }
        }
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      var k = dt * 60;
      for (i = 0; i < MAXP; i++) {
        if (life[i] > 0) {
          px[i] += pvx[i] * k;
          py[i] += pvy[i] * k;
          pvy[i] += 0.004 * k;
          pvx[i] *= 0.998;
          life[i] -= dt * (0.28 + S.t * 0.3);
          if (py[i] < -10 || px[i] < -10 || px[i] > w + 10) { life[i] = 0; }
        }
      }
    };
  };

  builders.aurora = function (S) {
    return function (ctx, w, h) {
      var nb = 3 + ((S.d * 2.99) | 0);
      var i;
      ctx.globalCompositeOperation = 'lighter';
      for (i = 0; i < nb; i++) {
        var ph = i * 1.7;
        var x = w * (0.5 + 0.38 * Math.sin(S.ph * (0.2 + i * 0.05) + ph));
        var y = h * (0.5 + 0.3 * Math.cos(S.ph * (0.16 + i * 0.04) + ph * 1.3));
        var r = Math.max(w, h) * (0.32 + 0.1 * Math.sin(S.ph * 0.3 + ph)) * (0.8 + S.e * 0.7);
        var g = ctx.createRadialGradient(x, y, 0, x, y, r);
        var hh = S.mh((i % 3) / 2);
        g.addColorStop(0, col(hh, 90, 52, 0.28 + S.e * 0.3));
        g.addColorStop(1, col(hh, 90, 52, 0));
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
      }
      var steps = 18;
      for (var L = 0; L < 3; L++) {
        var base = h * (0.25 + 0.12 * L);
        var hc = S.mh(L / 2);
        ctx.beginPath();
        for (i = 0; i <= steps; i++) {
          var xx = (i / steps) * w;
          var yy = base + Math.sin(xx * 0.012 + S.ph * (0.5 + L * 0.2) + L * 2) * h * 0.1 * (0.7 + S.m) +
            Math.sin(xx * 0.027 - S.ph * 0.7 + L) * h * 0.04;
          if (i === 0) { ctx.moveTo(xx, yy); } else { ctx.lineTo(xx, yy); }
        }
        ctx.lineTo(w, h * 0.95);
        ctx.lineTo(0, h * 0.95);
        ctx.closePath();
        var cg = ctx.createLinearGradient(0, h * 0.1, 0, h * 0.95);
        cg.addColorStop(0, col(hc, 85, 62, 0.14 + S.e * 0.22));
        cg.addColorStop(1, col(hc, 85, 55, 0));
        ctx.fillStyle = cg;
        ctx.fill();
      }
      ctx.globalCompositeOperation = 'source-over';
    };
  };

  builders.grid = function (S) {
    return function (ctx, w, h) {
      var hz = h * 0.45;
      var cx = w / 2;
      var m = Math.min(w, h);
      var i;
      var R = m * 0.3 * (1 + 0.06 * S.b);
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, w, hz);
      ctx.clip();
      var sg = ctx.createLinearGradient(0, hz - R * 1.6, 0, hz);
      sg.addColorStop(0, col(S.h2, 90, 62, 0.95));
      sg.addColorStop(1, col(S.h1, 90, 58, 0.95));
      ctx.fillStyle = sg;
      ctx.beginPath();
      ctx.arc(cx, hz - R * 0.45, R, 0, TAU);
      ctx.fill();
      ctx.fillStyle = col(S.h1, 35, 6, 1);
      ctx.beginPath();
      var nb = 20;
      var bw = w / nb;
      for (i = 0; i < nb; i++) {
        var kk = i < nb / 2 ? i : nb - 1 - i;
        var v = S.fs[(kk * 3) | 0] * (0.6 + S.d * 0.8);
        if (v > 1) { v = 1; }
        var bh = hz * (0.04 + v * 0.38);
        ctx.rect(i * bw + 1, hz - bh, bw - 2, bh);
      }
      ctx.fill();
      ctx.restore();
      var gl = ctx.createLinearGradient(0, hz - 4, 0, hz + h * 0.25);
      gl.addColorStop(0, col(S.h2, 90, 60, 0.35 + S.b * 0.3));
      gl.addColorStop(1, col(S.h2, 90, 60, 0));
      ctx.fillStyle = gl;
      ctx.fillRect(0, hz - 4, w, h * 0.25 + 4);
      var lw = 1 + S.b * 1.5 * (1 - S.calm);
      ctx.lineWidth = lw;
      ctx.strokeStyle = col(S.h1, 90, 65, 0.75);
      ctx.beginPath();
      var nv = 9 + ((S.d * 8) | 0);
      for (i = 0; i <= nv; i++) {
        var xb = cx + (i / nv - 0.5) * w * 3;
        ctx.moveTo(cx + (i / nv - 0.5) * w * 0.05, hz);
        ctx.lineTo(xb, h);
      }
      var nh = 12;
      var off = (S.ph * 0.35) % 1;
      for (i = 0; i < nh; i++) {
        var z = (i + off) / nh;
        var y = hz + (h - hz) * z * z;
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
      }
      ctx.stroke();
    };
  };

  builders.spokes = function (S) {
    function layer(ctx, cx, cy, r0, maxLen, n, rot, S2, hue, alpha, boost) {
      ctx.fillStyle = col(hue, 88, 60, alpha);
      ctx.beginPath();
      var da = (PI / n) * 0.6;
      var half = n >> 1;
      for (var i = 0; i < n; i++) {
        var j = i < half ? i : n - 1 - i;
        var v = S2.fs[((j / half) * 44) | 0] * boost;
        if (v > 1) { v = 1; }
        var len = r0 * 0.15 + v * maxLen;
        var a = rot + (i / n) * TAU;
        ctx.moveTo(cx + Math.cos(a - da) * r0, cy + Math.sin(a - da) * r0);
        ctx.lineTo(cx + Math.cos(a) * (r0 + len), cy + Math.sin(a) * (r0 + len));
        ctx.lineTo(cx + Math.cos(a + da) * r0, cy + Math.sin(a + da) * r0);
        ctx.closePath();
      }
      ctx.fill();
    }
    return function (ctx, w, h) {
      var cx = w / 2;
      var cy = h / 2;
      var m = Math.min(w, h);
      var n = 20 + ((S.d * 28) | 0);
      var r0 = m * (0.13 + 0.03 * S.b);
      layer(ctx, cx, cy, r0, m * 0.34, n, S.ph * 0.35, S, S.h1, 0.9, 1.4);
      layer(ctx, cx, cy, r0, m * 0.2, n >> 1, -S.ph * 0.5 + 0.3, S, S.h2, 0.75, 1.2);
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r0);
      g.addColorStop(0, col(S.h2, 90, 78, 1));
      g.addColorStop(1, col(S.h1, 90, 50, 0.95));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cx, cy, r0, 0, TAU);
      ctx.fill();
    };
  };

  builders.bokeh = function (S) {
    var N = 36;
    var bx = new Float32Array(N);
    var by = new Float32Array(N);
    var br = new Float32Array(N);
    var bv = new Float32Array(N);
    var bp = new Float32Array(N);
    var bk = new Uint8Array(N);
    var ready = false;
    function init(w, h) {
      for (var i = 0; i < N; i++) {
        bx[i] = Math.random() * w;
        by[i] = Math.random() * h;
        br[i] = Math.min(w, h) * (0.04 + Math.random() * 0.1);
        bv[i] = 0.2 + Math.random() * 0.8;
        bp[i] = Math.random() * TAU;
        bk[i] = (Math.random() * 3) | 0;
      }
      ready = true;
    }
    return function (ctx, w, h) {
      if (!ready) { init(w, h); }
      var cnt = 14 + ((S.d * 22) | 0);
      var i;
      var vy = h * 0.05 * S.sp * (0.5 + S.e) * S.dt;
      for (i = 0; i < N; i++) {
        by[i] -= vy * bv[i];
        bx[i] += Math.sin(S.ph * 0.4 + bp[i]) * 6 * S.dt;
        if (by[i] < -br[i] * 2) {
          by[i] = h + br[i] * 2;
          bx[i] = Math.random() * w;
        }
      }
      var bg = ctx.createLinearGradient(0, 0, 0, h);
      bg.addColorStop(0, col(S.h1, 40, 10, 0.6));
      bg.addColorStop(1, col(S.h2, 40, 12, 0.6));
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);
      var pulse = 1 + S.b * 0.25;
      for (var b = 0; b < 3; b++) {
        var hh = S.mh(b / 2);
        ctx.beginPath();
        for (i = 0; i < cnt; i++) {
          if (bk[i] === b) {
            var r = br[i] * pulse * (1 + 0.1 * Math.sin(S.ph + bp[i]));
            ctx.moveTo(bx[i] + r, by[i]);
            ctx.arc(bx[i], by[i], r, 0, TAU);
          }
        }
        ctx.fillStyle = col(hh, 80, 62, 0.1 + S.e * 0.2);
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = col(hh, 85, 75, 0.3 + S.e * 0.2);
        ctx.stroke();
      }
    };
  };

  builders.strings = function (S) {
    return function (ctx, w, h) {
      var n = 7 + ((S.d * 7) | 0);
      var seg = 24;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      for (var i = 0; i < n; i++) {
        var yb = h * (0.12 + 0.76 * (i / (n - 1)));
        var v = S.fs[((i / (n - 1)) * 40) | 0];
        var amp = h * 0.06 * (0.2 + v * 1.8);
        var k1 = 2 + (i % 3);
        ctx.beginPath();
        var px = 0;
        var py = yb;
        for (var j = 0; j <= seg; j++) {
          var f = j / seg;
          var env = Math.sin(PI * f);
          var y = yb + amp * env * Math.sin(f * TAU * k1 / 2 + S.ph * 3 + i) +
            amp * 0.4 * env * Math.sin(f * TAU * 1.5 - S.ph * 5 + i * 2);
          var x = f * w;
          if (j === 0) { ctx.moveTo(x, y); } else { ctx.quadraticCurveTo(px, py, (px + x) / 2, (py + y) / 2); }
          px = x;
          py = y;
        }
        ctx.lineTo(px, py);
        var hue = S.mh(i / (n - 1));
        ctx.lineWidth = 5 + v * 5;
        ctx.strokeStyle = col(hue, 85, 60, 0.16);
        ctx.stroke();
        ctx.lineWidth = 1.2 + v * 2;
        ctx.strokeStyle = col(hue, 85, 72, 0.9);
        ctx.stroke();
      }
    };
  };

  builders.stars = function (S) {
    var N = 120;
    var sx = new Float32Array(N);
    var sy = new Float32Array(N);
    var sz = new Float32Array(N);
    var ready = false;
    function reset(i, far) {
      sx[i] = (Math.random() - 0.5) * 2;
      sy[i] = (Math.random() - 0.5) * 2;
      sz[i] = far ? 1 : Math.random();
    }
    return function (ctx, w, h) {
      var i;
      if (!ready) { for (i = 0; i < N; i++) { reset(i, false); } ready = true; }
      var cx = w / 2;
      var cy = h / 2;
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.6);
      g.addColorStop(0, col(S.h2, 80, 45, 0.18 + S.b * 0.2 * (1 - S.calm)));
      g.addColorStop(1, col(S.h1, 80, 35, 0));
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
      var cnt = 50 + ((S.d * 70) | 0);
      var v = 0.12 * S.sp * (0.4 + S.e * 1.6) * (1 - 0.7 * S.calm) * S.dt + 0.01 * S.dt;
      var sc = Math.max(cx, cy);
      ctx.lineCap = 'round';
      for (var b = 0; b < 2; b++) {
        ctx.beginPath();
        for (i = b; i < cnt; i += 2) {
          var z0 = sz[i];
          var z1 = z0 + v * 4;
          if (z1 > 1) { z1 = 1; }
          var x0 = cx + (sx[i] / z0) * sc * 0.25;
          var y0 = cy + (sy[i] / z0) * sc * 0.25;
          var x1 = cx + (sx[i] / z1) * sc * 0.25;
          var y1 = cy + (sy[i] / z1) * sc * 0.25;
          ctx.moveTo(x1, y1);
          ctx.lineTo(x0, y0);
        }
        ctx.lineWidth = 1.6;
        ctx.strokeStyle = col(S.mh(b), 70, 80, 0.85);
        ctx.stroke();
      }
      for (i = 0; i < cnt; i++) {
        sz[i] -= v;
        if (sz[i] < 0.03) { reset(i, true); continue; }
        var px = cx + (sx[i] / sz[i]) * sc * 0.25;
        var py = cy + (sy[i] / sz[i]) * sc * 0.25;
        if (px < -20 || px > w + 20 || py < -20 || py > h + 20) { reset(i, true); }
      }
    };
  };

  builders.mosaic = function (S) {
    var cells = new Float32Array(600);
    return function (ctx, w, h) {
      var cols = 5 + ((S.d * 6) | 0);
      var s = w / cols;
      var rows = Math.ceil(h / s);
      if (cols * rows > 600) { rows = (600 / cols) | 0; }
      var BK = 5;
      var c;
      var r;
      for (r = 0; r < rows; r++) {
        for (c = 0; c < cols; c++) {
          var idx = r * cols + c;
          var wv = 0.5 + 0.5 * Math.sin((c + r) * 0.7 - S.ph * 2);
          var tv = S.fs[((c * 5 + r * 3) % 44)] * (0.5 + S.e) + wv * 0.25;
          if (tv > 1) { tv = 1; }
          cells[idx] += (tv - cells[idx]) * 0.25;
        }
      }
      var ox = (w - cols * s) / 2;
      var oy = (h - rows * s) / 2;
      for (var b = 0; b < BK; b++) {
        ctx.fillStyle = col(S.mh(b / (BK - 1)), 80, 62, 1);
        for (r = 0; r < rows; r++) {
          for (c = 0; c < cols; c++) {
            var bi = (((c + r) * BK) / (cols + rows)) | 0;
            if (bi !== b) { continue; }
            var v = cells[r * cols + c];
            var sz = s * (0.55 + 0.4 * v);
            ctx.globalAlpha = 0.08 + v * 0.8;
            ctx.fillRect(ox + c * s + (s - sz) / 2, oy + r * s + (s - sz) / 2, sz, sz);
          }
        }
      }
      ctx.globalAlpha = 1;
    };
  };

  builders.smoke = function (S) {
    return function (ctx, w, h) {
      var n = 5 + ((S.d * 4) | 0);
      var m = Math.max(w, h);
      for (var i = 0; i < n; i++) {
        var ph = i * 2.1;
        var x = w * (0.5 + 0.45 * Math.sin(S.ph * (0.1 + i * 0.023) + ph));
        var y = h * (0.5 + 0.4 * Math.sin(S.ph * (0.08 + i * 0.019) * 1.3 + ph * 1.7));
        var r = m * (0.35 + 0.12 * Math.sin(S.ph * 0.2 + ph)) * (0.85 + S.e * 0.5);
        var hh = S.mh((i % 2) ? 1 : 0) + Math.sin(S.ph * 0.1 + i) * 8;
        var g = ctx.createRadialGradient(x, y, 0, x, y, r);
        g.addColorStop(0, col(hh, 40, 58, 0.16 + S.e * 0.14));
        g.addColorStop(0.6, col(hh, 35, 45, 0.07));
        g.addColorStop(1, col(hh, 35, 40, 0));
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
      }
      var vg = ctx.createLinearGradient(0, 0, 0, h);
      vg.addColorStop(0, col(S.h1, 40, 6, 0.5));
      vg.addColorStop(0.5, col(S.h1, 40, 6, 0));
      vg.addColorStop(1, col(S.h2, 40, 6, 0.5));
      ctx.fillStyle = vg;
      ctx.fillRect(0, 0, w, h);
    };
  };

  function create(playlistId, spec) {
    var auto = autoSpec(playlistId);
    var sp = {};
    var s = spec || {};
    sp.motif = MOTIFS.indexOf(s.motif) >= 0 ? s.motif : auto.motif;
    sp.hue = typeof s.hue === 'number' ? s.hue : auto.hue;
    sp.hue2 = typeof s.hue2 === 'number' ? s.hue2 : auto.hue2;
    sp.speed = typeof s.speed === 'number' && s.speed > 0 ? s.speed : auto.speed;
    sp.density = typeof s.density === 'number' ? Math.max(0, Math.min(1, s.density)) : auto.density;

    var S = {
      ph: 0, e: 0.1, b: 0.08, m: 0.08, t: 0.08, calm: 1, dt: 0.016,
      h1: sp.hue, h2: sp.hue2, dh: 0, sp: sp.speed, d: sp.density,
      fs: new Float32Array(64), data: null,
      mh: function (f) { return this.h1 + this.dh * f; }
    };
    var fn = builders[sp.motif](S);
    var last = -1;

    function draw(ctx, w, h, data, nowSec) {
      var now = typeof nowSec === 'number' ? nowSec : performance.now() / 1000;
      var dt = last < 0 ? 0.016 : Math.min(0.1, Math.max(0, now - last));
      last = now;
      S.dt = dt;
      S.data = data;
      var target = data.playing ? 0 : 1;
      S.calm += (target - S.calm) * Math.min(1, dt * 3);
      var c = S.calm;
      S.ph += dt * S.sp * (1 - 0.6 * c);
      var up = Math.min(1, dt * 18);
      var dn = Math.min(1, dt * 6);
      var ph = S.ph;
      var t;
      t = data.level * (1 - c) + (0.1 + 0.05 * Math.sin(ph * 0.7)) * c;
      S.e += (t - S.e) * (t > S.e ? up : dn);
      t = data.bass * (1 - c) + (0.08 + 0.04 * Math.sin(ph * 0.9)) * c;
      S.b += (t - S.b) * (t > S.b ? up : dn);
      t = data.mid * (1 - c) + (0.08 + 0.04 * Math.sin(ph * 0.8 + 1)) * c;
      S.m += (t - S.m) * (t > S.m ? up : dn);
      t = data.treble * (1 - c) + (0.08 + 0.04 * Math.sin(ph * 1.1 + 2)) * c;
      S.t += (t - S.t) * (t > S.t ? up : dn);
      var freq = data.freq;
      for (var i = 0; i < 64; i++) {
        t = (freq[i] / 255) * (1 - c) + (0.06 + 0.04 * Math.sin(ph * 1.2 + i * 0.35)) * c;
        S.fs[i] += (t - S.fs[i]) * (t > S.fs[i] ? up : dn);
      }
      var drift = (data.progress * 2 - 1) * 15;
      S.h1 = sp.hue + drift;
      var d2 = ((((sp.hue2 - sp.hue) % 360) + 540) % 360) - 180;
      S.dh = d2 - 2 * drift;
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      ctx.fillStyle = col(S.h1, 35, 6, 1);
      ctx.fillRect(0, 0, w, h);
      fn(ctx, w, h);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
    }

    return { spec: sp, draw: draw };
  }

  window.CreaScenes = { motifs: MOTIFS.slice(), autoSpec: autoSpec, create: create };
})();
