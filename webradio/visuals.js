(function () {
  'use strict';

  var TAU = Math.PI * 2;
  var calm = 1;
  var lastT = -1;

  function hsla(h, s, l, a) {
    return 'hsla(' + (((h % 360) + 360) % 360).toFixed(0) + ',' + s + '%,' + l + '%,' + a.toFixed(3) + ')';
  }

  function breath(t, speed, phase) {
    return 0.5 + 0.5 * Math.sin(t * speed + (phase || 0));
  }

  function step(data) {
    var target = data.playing ? 0 : 1;
    calm += (target - calm) * 0.06;
  }

  function lvl(data, idle) {
    return data.level * (1 - calm) + idle * calm;
  }

  function roundBar(ctx, x, y, bw, bh) {
    var r = bw / 2;
    if (bh < bw) { r = bh / 2; }
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + bw - r, y);
    ctx.arc(x + bw - r, y + r, r, -Math.PI / 2, 0);
    ctx.lineTo(x + bw, y + bh - r);
    ctx.arc(x + bw - r, y + bh - r, r, 0, Math.PI / 2);
    ctx.lineTo(x + r, y + bh);
    ctx.arc(x + r, y + bh - r, r, Math.PI / 2, Math.PI);
    ctx.lineTo(x, y + r);
    ctx.arc(x + r, y + r, r, Math.PI, Math.PI * 1.5);
    ctx.closePath();
  }

  function spectrum(ctx, w, h, d) {
    var n = 24 + Math.floor(d.progress * 24);
    var gap = Math.max(2, w * 0.008);
    var bw = (w - gap * (n + 1)) / n;
    var base = h * 0.92;
    var maxH = h * 0.8;
    var grad = ctx.createLinearGradient(0, base - maxH, 0, base);
    grad.addColorStop(0, hsla(d.hue + 40, 90, 68, 1));
    grad.addColorStop(1, hsla(d.hue, 90, 60, 0.85));
    ctx.fillStyle = grad;
    ctx.beginPath();
    for (var i = 0; i < n; i++) {
      var pos = (i / (n - 1)) * 63;
      var i0 = pos | 0;
      var i1 = i0 < 63 ? i0 + 1 : 63;
      var f = pos - i0;
      var v = (d.freq[i0] * (1 - f) + d.freq[i1] * f) / 255;
      var idle = 0.07 + 0.05 * Math.sin(d.t * 1.4 + i * 0.45);
      var amp = v * (1 - calm) + idle * calm;
      var bh = Math.max(bw, amp * maxH);
      roundBar(ctx, gap + i * (bw + gap), base - bh, bw, bh);
    }
    ctx.fill();
    ctx.globalAlpha = 0.18;
    ctx.fillRect(0, base + h * 0.02, w * d.progress, 2);
    ctx.globalAlpha = 1;
  }

  function wave(ctx, w, h, d) {
    var cy = h / 2;
    var n = 64;
    var layers = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    for (var L = 0; L < layers; L++) {
      var amp = h * (0.34 - L * 0.07) * (0.35 + d.level * 1.1);
      var idleAmp = h * (0.05 + L * 0.015) * (0.6 + 0.4 * breath(d.t, 1.1, L));
      ctx.beginPath();
      var px = 0;
      var py = cy;
      for (var i = 0; i <= n; i++) {
        var si = Math.min(127, (i * 2) | 0);
        var s = (d.wave[si] - 128) / 128;
        var env = Math.sin((i / n) * Math.PI);
        var idleY = Math.sin(i * 0.22 + d.t * (1 + L * 0.4) + L * 1.7) * idleAmp * env;
        var y = cy + (s * amp * (1 - calm) + idleY * calm) * (1 - L * 0.12) + Math.sin(i * 0.15 + d.t * 0.8 + L) * h * 0.02 * env;
        var x = (i / n) * w;
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.quadraticCurveTo(px, py, (px + x) / 2, (py + y) / 2);
        }
        px = x;
        py = y;
      }
      ctx.lineTo(px, py);
      ctx.lineWidth = 4 - L;
      ctx.strokeStyle = hsla(d.hue + L * 45, 90, 62 + L * 4, 0.95 - L * 0.22);
      ctx.shadowColor = hsla(d.hue + L * 45, 90, 60, 0.7);
      ctx.shadowBlur = 8 + d.level * 14;
      ctx.stroke();
    }
    ctx.shadowBlur = 0;
  }

  function circle(ctx, w, h, d) {
    var cx = w / 2;
    var cy = h / 2;
    var m = Math.min(w, h);
    var pulse = lvl(d, 0.05 + 0.04 * breath(d.t, 1.3));
    var r0 = m * (0.16 + 0.05 * d.progress) * (1 + d.bass * 0.3 * (1 - calm) + 0.05 * calm * breath(d.t, 1.3));
    var maxLen = m * 0.3;
    var rot = d.t * 0.15 + d.progress * TAU;
    var n = 64;
    ctx.lineCap = 'round';
    ctx.lineWidth = Math.max(2, (TAU * r0) / n * 0.55);
    ctx.strokeStyle = hsla(d.hue + 30, 90, 66, 0.95);
    ctx.beginPath();
    for (var i = 0; i < n; i++) {
      var k = i < 32 ? i : 63 - i;
      var v = d.freq[k * 2 > 63 ? 63 : k * 2] / 255;
      var idle = 0.06 + 0.04 * Math.sin(d.t * 1.5 + i * 0.4);
      var len = (v * (1 - calm) + idle * calm) * maxLen + 2;
      var a = rot + (i / n) * TAU;
      var ca = Math.cos(a);
      var sa = Math.sin(a);
      ctx.moveTo(cx + ca * (r0 + 6), cy + sa * (r0 + 6));
      ctx.lineTo(cx + ca * (r0 + 6 + len), cy + sa * (r0 + 6 + len));
    }
    ctx.stroke();
    var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r0);
    g.addColorStop(0, hsla(d.hue + 60, 95, 75, 0.95));
    g.addColorStop(0.6, hsla(d.hue, 90, 60, 0.9));
    g.addColorStop(1, hsla(d.hue - 20, 90, 45, 0.85));
    ctx.fillStyle = g;
    ctx.shadowColor = hsla(d.hue, 90, 60, 0.8);
    ctx.shadowBlur = 10 + pulse * 40;
    ctx.beginPath();
    ctx.arc(cx, cy, r0, 0, TAU);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.lineWidth = 2;
    ctx.strokeStyle = hsla(d.hue + 90, 80, 75, 0.5);
    ctx.beginPath();
    ctx.arc(cx, cy, r0 + 6 + maxLen + 6, -Math.PI / 2, -Math.PI / 2 + TAU * d.progress);
    ctx.stroke();
  }

  var MAXP = 120;
  var px = new Float32Array(MAXP);
  var py = new Float32Array(MAXP);
  var pvx = new Float32Array(MAXP);
  var pvy = new Float32Array(MAXP);
  var plife = new Float32Array(MAXP);
  var psize = new Float32Array(MAXP);
  var pbucket = new Uint8Array(MAXP);
  var spawnAcc = 0;
  var prevBass = 0;
  var BUCKETS = 4;

  function spawn(w, h, d, strong) {
    for (var i = 0; i < MAXP; i++) {
      if (plife[i] <= 0) {
        var a = Math.random() * TAU;
        var sp = (0.4 + Math.random() * 1.6) * (strong ? 1.6 : 0.7);
        px[i] = w / 2 + (Math.random() - 0.5) * w * 0.25;
        py[i] = h * 0.62 + (Math.random() - 0.5) * h * 0.1;
        pvx[i] = Math.cos(a) * sp;
        pvy[i] = -Math.abs(Math.sin(a)) * sp * 1.4 - 0.3;
        plife[i] = 1;
        psize[i] = 1.5 + Math.random() * (2 + d.level * 4);
        pbucket[i] = (Math.random() * BUCKETS) | 0;
        return;
      }
    }
  }

  function particles(ctx, w, h, d) {
    var dt = lastT >= 0 && d.t > lastT ? Math.min(0.05, d.t - lastT) : 0.016;
    var cap = 40 + Math.floor(d.progress * 80);
    var strong = d.bass > 0.55 && d.bass > prevBass + 0.04;
    prevBass = d.bass;
    var rate = d.playing ? (strong ? 6 : d.bass * 10 * dt * 60 * 0.12 + d.level * 3 * dt) : 1.2 * dt;
    spawnAcc += rate;
    var alive = 0;
    for (var i = 0; i < MAXP; i++) { if (plife[i] > 0) { alive++; } }
    while (spawnAcc >= 1) {
      spawnAcc -= 1;
      if (alive < cap) { spawn(w, h, d, strong); alive++; }
    }
    var k = dt * 60;
    var g = ctx.createRadialGradient(w / 2, h * 0.7, 0, w / 2, h * 0.7, h * 0.7);
    g.addColorStop(0, hsla(d.hue, 80, 50, 0.18 + d.level * 0.2 * (1 - calm)));
    g.addColorStop(1, hsla(d.hue, 80, 50, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    for (var b = 0; b < BUCKETS; b++) {
      ctx.fillStyle = hsla(d.hue + b * 40, 90, 68, 1);
      ctx.beginPath();
      for (var j = 0; j < MAXP; j++) {
        if (plife[j] > 0 && pbucket[j] === b) {
          var l = plife[j];
          var r = psize[j] * (0.4 + l * 0.6);
          ctx.moveTo(px[j] + r, py[j]);
          ctx.arc(px[j], py[j], r, 0, TAU);
        }
      }
      ctx.globalAlpha = 0.85;
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    for (var m = 0; m < MAXP; m++) {
      if (plife[m] > 0) {
        px[m] += pvx[m] * k;
        py[m] += pvy[m] * k;
        pvy[m] += 0.004 * k;
        pvx[m] *= 0.998;
        plife[m] -= dt * (0.28 + d.treble * 0.3);
        if (py[m] < -10 || px[m] < -10 || px[m] > w + 10) { plife[m] = 0; }
      }
    }
  }

  function aurora(ctx, w, h, d) {
    var count = 3 + Math.floor(d.progress * 2.99);
    var energy = lvl(d, 0.12 + 0.06 * breath(d.t, 0.9));
    ctx.globalCompositeOperation = 'lighter';
    for (var i = 0; i < count; i++) {
      var ph = i * 1.7;
      var x = w * (0.5 + 0.38 * Math.sin(d.t * (0.17 + i * 0.05) + ph));
      var y = h * (0.5 + 0.3 * Math.cos(d.t * (0.13 + i * 0.04) + ph * 1.3));
      var r = Math.max(w, h) * (0.32 + 0.1 * Math.sin(d.t * 0.3 + ph)) * (0.8 + energy * 0.7);
      var g = ctx.createRadialGradient(x, y, 0, x, y, r);
      var hh = d.hue + i * 38;
      g.addColorStop(0, hsla(hh, 90, 55, 0.35 + energy * 0.35));
      g.addColorStop(1, hsla(hh, 90, 55, 0));
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
    }
    ctx.globalCompositeOperation = 'source-over';
    var bandY = h * (0.35 + 0.1 * Math.sin(d.t * 0.4));
    var bg = ctx.createLinearGradient(0, bandY - h * 0.25, 0, bandY + h * 0.25);
    bg.addColorStop(0, hsla(d.hue + 120, 90, 70, 0));
    bg.addColorStop(0.5, hsla(d.hue + 120, 90, 70, 0.08 + d.treble * 0.14 * (1 - calm)));
    bg.addColorStop(1, hsla(d.hue + 120, 90, 70, 0));
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);
  }

  var styles = [
    { id: 1, name: 'Spectre' },
    { id: 2, name: 'Onde' },
    { id: 3, name: 'Cercle' },
    { id: 4, name: 'Particules' },
    { id: 5, name: 'Aurore' }
  ];

  function draw(styleId, ctx, w, h, data) {
    ctx.clearRect(0, 0, w, h);
    step(data);
    switch (styleId) {
      case 2: wave(ctx, w, h, data); break;
      case 3: circle(ctx, w, h, data); break;
      case 4: particles(ctx, w, h, data); break;
      case 5: aurora(ctx, w, h, data); break;
      default: spectrum(ctx, w, h, data);
    }
    lastT = data.t;
  }

  window.CreaVisuals = { styles: styles, draw: draw };
})();
