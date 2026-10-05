(function () {
  'use strict';

  var TAU = Math.PI * 2;
  var FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
  var TEAL = '111,211,200';
  var BLUE = '91,159,216';
  var WHITE = '243,241,234';
  var SOFT = '208,226,226';
  var NAVY = '12,28,40';
  var PINK = '255,107,157';
  var RBLUE = '100,150,255';

  function clamp01(x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
  function sm(x) { x = clamp01(x); return x * x * x * (x * (x * 6 - 15) + 10); }
  function eo(x) { x = clamp01(x); var u = 1 - x; return 1 - u * u * u; }
  function rgba(c, a) { return 'rgba(' + c + ',' + clamp01(a).toFixed(3) + ')'; }

  function envelope(t, dur, fade) {
    var f = fade > 0 ? fade : 0.6;
    if (f * 2 > dur) { f = dur / 2; }
    return Math.min(sm(t / f), sm((dur - t) / f));
  }

  function setFont(ctx, wt, size) {
    ctx.font = wt + ' ' + size.toFixed(1) + 'px ' + FONT;
  }

  function wrapAt(ctx, text, maxW, size, wt) {
    setFont(ctx, wt, size);
    var words = String(text == null ? '' : text).split(/\s+/);
    var lines = [];
    var cur = '';
    var i;
    for (i = 0; i < words.length; i++) {
      if (!words[i]) { continue; }
      var test = cur ? cur + ' ' + words[i] : words[i];
      if (!cur || ctx.measureText(test).width <= maxW) {
        cur = test;
      } else {
        lines.push(cur);
        cur = words[i];
      }
    }
    if (cur) { lines.push(cur); }
    var tooWide = false;
    for (i = 0; i < lines.length; i++) {
      if (ctx.measureText(lines[i]).width > maxW) { tooWide = true; }
    }
    return { lines: lines, tooWide: tooWide };
  }

  var fcache = {};
  var fcount = 0;

  function fit(ctx, text, maxW, maxLines, base, min, wt) {
    var key = wt + '|' + (maxW | 0) + '|' + maxLines + '|' + (base | 0) + '|' + min + '|' + text;
    var hit = fcache[key];
    if (hit) { return hit; }
    if (fcount > 300) { fcache = {}; fcount = 0; }
    var res = null;
    for (var s = Math.floor(base); s >= min; s--) {
      var r = wrapAt(ctx, text, maxW, s, wt);
      if (r.lines.length <= maxLines && !r.tooWide) { res = { size: s, lines: r.lines }; break; }
    }
    if (!res) {
      var f = wrapAt(ctx, text, maxW, min, wt);
      res = { size: min, lines: f.lines };
    }
    fcache[key] = res;
    fcount++;
    return res;
  }

  var lc = { key: '', val: null };

  function layout(ctx, w, h, ad) {
    var head = ad.headline || '';
    var sub = ad.sub || '';
    var cta = ad.cta || '';
    var key = w + '|' + h + '|' + head + '|' + sub + '|' + cta;
    if (lc.key === key) { return lc.val; }
    var maxW = Math.min(w * 0.86, 640);
    var scale = 1;
    var H;
    var S;
    var cs;
    var hlh;
    var slh;
    var ctaH;
    var ctaW;
    var g1;
    var g2;
    var total;
    for (var it = 0; it < 6; it++) {
      H = fit(ctx, head, maxW, 3, Math.min(w * 0.1, 46) * scale, 16, '700');
      S = fit(ctx, sub, maxW, 3, Math.min(w * 0.048, 22) * scale, 12, '400');
      cs = Math.max(14, Math.min(w * 0.045, 19));
      hlh = H.size * 1.2;
      slh = S.size * 1.38;
      ctaH = cs * 2.5;
      setFont(ctx, '600', cs);
      ctaW = Math.min(maxW, ctx.measureText(cta).width + cs * 2.6);
      g1 = H.size * 0.55;
      g2 = cs * 1.1;
      total = H.lines.length * hlh + g1 + S.lines.length * slh + g2 + ctaH;
      if (total <= h * 0.9) { break; }
      scale *= 0.88;
    }
    var top = (h - total) / 2;
    var v = {
      maxW: maxW, H: H, S: S, hlh: hlh, slh: slh, cs: cs, ctaW: ctaW, ctaH: ctaH, total: total,
      top: top, hTop: top, hBot: top + H.lines.length * hlh,
      hy: top + hlh / 2,
      sy: top + H.lines.length * hlh + g1 + slh / 2,
      cy: top + total - ctaH / 2
    };
    lc.key = key;
    lc.val = v;
    return v;
  }

  function veil(ctx, w, h, E, k) {
    ctx.fillStyle = rgba(NAVY, k * E);
    ctx.fillRect(0, 0, w, h);
  }

  function rrPath(ctx, x, y, w, h, r) {
    if (r > h / 2) { r = h / 2; }
    if (r > w / 2) { r = w / 2; }
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arc(x + w - r, y + r, r, -Math.PI / 2, 0);
    ctx.lineTo(x + w, y + h - r);
    ctx.arc(x + w - r, y + h - r, r, 0, Math.PI / 2);
    ctx.lineTo(x + r, y + h);
    ctx.arc(x + r, y + h - r, r, Math.PI / 2, Math.PI);
    ctx.lineTo(x, y + r);
    ctx.arc(x + r, y + r, r, Math.PI, Math.PI * 1.5);
    ctx.closePath();
  }

  function drawLines(ctx, lines, x, y0, lh) {
    for (var i = 0; i < lines.length; i++) { ctx.fillText(lines[i], x, y0 + i * lh); }
  }

  function pill(ctx, L, cx, y, p, text, tm, E) {
    if (p <= 0) { return; }
    var sc = 0.85 + 0.15 * eo(p);
    var pw = L.ctaW * sc;
    var ph = L.ctaH * sc;
    ctx.save();
    ctx.globalAlpha = E * clamp01(p);
    rrPath(ctx, cx - pw / 2, y - ph / 2, pw, ph, ph / 2);
    ctx.fillStyle = rgba(TEAL, 0.2);
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = rgba(TEAL, 0.95);
    ctx.stroke();
    rrPath(ctx, cx - pw / 2 - 4, y - ph / 2 - 4, pw + 8, ph + 8, ph / 2 + 4);
    ctx.lineWidth = 1;
    ctx.strokeStyle = rgba(TEAL, 0.22 * (0.5 + 0.5 * Math.sin(tm * 3)));
    ctx.stroke();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    setFont(ctx, '600', L.cs * sc);
    ctx.fillStyle = rgba(WHITE, 1);
    ctx.fillText(text, cx, y + 1);
    ctx.restore();
  }

  function drawStatic(ctx, L, w, ad, E, ha, sa, ca, tm) {
    var cx = w / 2;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    setFont(ctx, '700', L.H.size);
    ctx.fillStyle = rgba(WHITE, E * ha);
    drawLines(ctx, L.H.lines, cx, L.hy, L.hlh);
    setFont(ctx, '400', L.S.size);
    ctx.fillStyle = rgba(SOFT, E * sa);
    drawLines(ctx, L.S.lines, cx, L.sy, L.slh);
    pill(ctx, L, cx, L.cy, ca, ad.cta || '', tm, E);
  }

  function adKinetic(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var cx = w / 2;
    var i;
    ctx.save();
    veil(ctx, w, h, E, 0.72);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var lp = sm((t - 0.1) / 0.9);
    ctx.fillStyle = rgba(TEAL, 0.9 * E);
    ctx.fillRect(cx - L.maxW * 0.15 * lp, L.hTop - 12, L.maxW * 0.3 * lp, 3);
    setFont(ctx, '700', L.H.size);
    var n = L.H.lines.length;
    for (i = 0; i < n; i++) {
      var p = eo((t - (0.3 + i * 0.35)) / 0.7);
      ctx.fillStyle = rgba(WHITE, E * p);
      ctx.fillText(L.H.lines[i], cx, L.hy + i * L.hlh + (1 - p) * 24);
    }
    var ts = 0.5 + n * 0.35;
    setFont(ctx, '400', L.S.size);
    for (i = 0; i < L.S.lines.length; i++) {
      var q = eo((t - ts - i * 0.2) / 0.7);
      ctx.fillStyle = rgba(SOFT, E * q);
      ctx.fillText(L.S.lines[i], cx, L.sy + i * L.slh + (1 - q) * 16);
    }
    pill(ctx, L, cx, L.cy, eo((t - (ts + 0.9 + L.S.lines.length * 0.2)) / 0.6), ad.cta || '', t, E);
    ctx.restore();
  }

  function adSplit(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    ctx.save();
    veil(ctx, w, h, E, 0.6);
    var open = sm((t - 0.4) / 1.4);
    drawStatic(ctx, L, w, ad, E, clamp01(open * 1.6 - 0.3), clamp01(open * 1.6 - 0.45), eo((t - 2.4) / 0.6), t);
    var ph = (h / 2) * (1 - open);
    if (ph > 0.5) {
      ctx.fillStyle = rgba('14,40,56', 0.97 * E);
      ctx.fillRect(0, 0, w, ph);
      ctx.fillRect(0, h - ph, w, ph);
      ctx.fillStyle = rgba(TEAL, 0.95 * E);
      ctx.fillRect(0, ph - 2, w, 2);
      ctx.fillRect(0, h - ph, w, 2);
    }
    var rp = sm((t - 1.6) / 0.9);
    if (rp > 0) {
      var ry = (L.hBot + L.sy - L.S.size * 0.6) / 2 - 2;
      ctx.fillStyle = rgba(TEAL, 0.8 * E);
      ctx.fillRect(w / 2 - L.maxW * 0.2 * rp, ry, L.maxW * 0.4 * rp, 2);
    }
    ctx.restore();
  }

  function adOrbits(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var cx = w / 2;
    var cy = h / 2;
    var i;
    var j;
    ctx.save();
    veil(ctx, w, h, E, 0.74);
    var appear = eo(t / 1.2);
    for (i = 0; i < 3; i++) {
      var rx = w * (0.4 - i * 0.07) * appear;
      var ry = rx * (0.3 + i * 0.05);
      var rot = -0.35 + i * 0.35;
      ctx.lineWidth = 1;
      ctx.strokeStyle = rgba(i === 1 ? BLUE : TEAL, 0.22 * E);
      ctx.beginPath();
      ctx.ellipse(cx, cy, rx, ry, rot, 0, TAU);
      ctx.stroke();
      var sp = (0.5 + i * 0.22) * (i === 1 ? -1 : 1);
      var cr = Math.cos(rot);
      var sr = Math.sin(rot);
      for (j = 0; j < 8; j++) {
        var a = t * sp - j * 0.09;
        var ex = Math.cos(a) * rx;
        var ey = Math.sin(a) * ry;
        var dx = cx + ex * cr - ey * sr;
        var dy = cy + ex * sr + ey * cr;
        var hid = Math.abs(dx - cx) < L.maxW / 2 + 8 && dy > L.top - 8 && dy < L.top + L.total + 8 ? 0.12 : 1;
        ctx.fillStyle = rgba(i === 1 ? BLUE : TEAL, E * (1 - j / 8) * 0.95 * hid);
        ctx.beginPath();
        ctx.arc(dx, dy, 4.5 - j * 0.45, 0, TAU);
        ctx.fill();
      }
    }
    var rg = ctx.createRadialGradient(cx, cy, 0, cx, cy, w * 0.4);
    rg.addColorStop(0, rgba(TEAL, 0.1 * E));
    rg.addColorStop(1, rgba(TEAL, 0));
    ctx.fillStyle = rg;
    ctx.fillRect(0, 0, w, h);
    drawStatic(ctx, L, w, ad, E, eo((t - 0.5) / 0.9), eo((t - 1.1) / 0.9), eo((t - 2) / 0.6), t);
    ctx.restore();
  }

  function adSweep(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var cx = w / 2;
    ctx.save();
    veil(ctx, w, h, E, 0.72);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var bx0 = cx - L.maxW / 2;
    var bw = L.maxW;
    var bc = bx0 - bw * 0.3 + ((t / 2.6) % 1) * bw * 1.6;
    var g = ctx.createLinearGradient(bc - bw * 0.25, 0, bc + bw * 0.25, 0);
    g.addColorStop(0, rgba(SOFT, 0.85));
    g.addColorStop(0.5, rgba('160,245,230', 1));
    g.addColorStop(1, rgba(SOFT, 0.85));
    var hp = eo((t - 0.3) / 0.9);
    ctx.globalAlpha = E * hp;
    setFont(ctx, '700', L.H.size);
    ctx.fillStyle = g;
    drawLines(ctx, L.H.lines, cx, L.hy + (1 - hp) * 10, L.hlh);
    ctx.globalAlpha = 1;
    var sp = eo((t - 1) / 0.9);
    setFont(ctx, '400', L.S.size);
    ctx.fillStyle = rgba(SOFT, E * sp);
    drawLines(ctx, L.S.lines, cx, L.sy, L.slh);
    var bandX = -w * 0.4 + ((t / 3.2) % 1) * w * 1.8;
    var dg = ctx.createLinearGradient(bandX - w * 0.12, 0, bandX + w * 0.12, h * 0.35);
    dg.addColorStop(0, rgba(TEAL, 0));
    dg.addColorStop(0.5, rgba(TEAL, 0.1 * E));
    dg.addColorStop(1, rgba(TEAL, 0));
    ctx.fillStyle = dg;
    ctx.fillRect(0, 0, w, h);
    pill(ctx, L, cx, L.cy, eo((t - 2.2) / 0.6), ad.cta || '', t, E);
    ctx.restore();
  }

  function adCards(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var pad = 12;
    var gap = 10;
    var c1 = L.H.lines.length * L.hlh + pad * 2;
    var c2 = L.S.lines.length * L.slh + pad * 2;
    var c3 = L.ctaH;
    var tot = c1 + c2 + c3 + gap * 2;
    var sc = Math.min(1, (h * 0.92) / tot);
    var cw = Math.min(L.maxW + 24, w * 0.94 / sc);
    ctx.save();
    veil(ctx, w, h, E, 0.68);
    ctx.translate(w / 2, h / 2);
    ctx.scale(sc, sc);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var y = -tot / 2;
    var hs = [c1, c2, c3];
    var fills = [rgba(WHITE, 0.96), rgba(TEAL, 0.95), rgba(BLUE, 0.95)];
    for (var i = 0; i < 3; i++) {
      var p = eo((t - 0.3 - i * 0.5) / 0.7);
      var dir = i % 2 ? 1 : -1;
      ctx.save();
      ctx.globalAlpha = E * clamp01(p * 1.4);
      ctx.translate((1 - p) * dir * w * 0.6, y + hs[i] / 2);
      ctx.rotate((1 - p) * dir * 0.08);
      ctx.shadowColor = 'rgba(0,0,0,0.35)';
      ctx.shadowBlur = 12;
      ctx.fillStyle = fills[i];
      rrPath(ctx, -cw / 2, -hs[i] / 2, cw, hs[i], 14);
      ctx.fill();
      ctx.shadowBlur = 0;
      if (i === 0) {
        setFont(ctx, '700', L.H.size);
        ctx.fillStyle = rgba('14,38,52', 1);
        drawLines(ctx, L.H.lines, 0, -hs[i] / 2 + pad + L.hlh / 2, L.hlh);
      } else if (i === 1) {
        setFont(ctx, '400', L.S.size);
        ctx.fillStyle = rgba('14,38,52', 1);
        drawLines(ctx, L.S.lines, 0, -hs[i] / 2 + pad + L.slh / 2, L.slh);
      } else {
        setFont(ctx, '700', L.cs);
        ctx.fillStyle = rgba(WHITE, 1);
        ctx.fillText(ad.cta || '', 0, 1);
      }
      ctx.restore();
      y += hs[i] + gap;
    }
    ctx.restore();
  }

  function adTypewriter(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var x0 = (w - L.maxW) / 2;
    var i;
    ctx.save();
    veil(ctx, w, h, E, 0.74);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = rgba(TEAL, 0.9 * E);
    ctx.fillRect(x0 - 12, L.hTop, 3, L.sy + L.S.lines.length * L.slh / 2 - L.hTop);
    var hLen = 0;
    for (i = 0; i < L.H.lines.length; i++) { hLen += L.H.lines[i].length; }
    var sLen = 0;
    for (i = 0; i < L.S.lines.length; i++) { sLen += L.S.lines[i].length; }
    var hn = Math.max(0, Math.floor((t - 0.4) * 24));
    var tS = 0.4 + hLen / 24 + 0.4;
    var sn = Math.max(0, Math.floor((t - tS) * 30));
    var tC = tS + sLen / 30 + 0.4;
    var caretX = x0;
    var caretY = L.hy;
    var caretH = L.H.size;
    var rem = hn;
    setFont(ctx, '700', L.H.size);
    ctx.fillStyle = rgba(WHITE, E);
    for (i = 0; i < L.H.lines.length; i++) {
      var part = L.H.lines[i].slice(0, Math.max(0, rem));
      if (part.length > 0 || rem > 0) {
        ctx.fillText(part, x0, L.hy + i * L.hlh);
        caretX = x0 + ctx.measureText(part).width;
        caretY = L.hy + i * L.hlh;
      }
      rem -= L.H.lines[i].length;
    }
    if (sn > 0 || t > tS) {
      rem = sn;
      setFont(ctx, '400', L.S.size);
      ctx.fillStyle = rgba(SOFT, E);
      for (i = 0; i < L.S.lines.length; i++) {
        var sp = L.S.lines[i].slice(0, Math.max(0, rem));
        if (sp.length > 0) {
          ctx.fillText(sp, x0, L.sy + i * L.slh);
          caretX = x0 + ctx.measureText(sp).width;
          caretY = L.sy + i * L.slh;
          caretH = L.S.size;
        }
        rem -= L.S.lines[i].length;
      }
    }
    if (Math.floor(t * 2.5) % 2 === 0 || t < tC) {
      ctx.fillStyle = rgba(TEAL, E);
      ctx.fillRect(caretX + 3, caretY - caretH * 0.55, 2, caretH * 1.1);
    }
    pill(ctx, L, w / 2, L.cy, eo((t - tC) / 0.5), ad.cta || '', t, E);
    ctx.restore();
  }

  function adSpotlight(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    ctx.save();
    veil(ctx, w, h, E, 0.86);
    var maxR = Math.sqrt(w * w + h * h) * 0.6;
    var grow = sm((t - 2.6) / 2.2);
    var R = w * 0.26 + (maxR - w * 0.26) * grow;
    var mx = w * (-0.2 + 0.7 * sm(t / 2.6)) + Math.sin(t * 1.3) * w * 0.05 * (1 - grow);
    var my = L.hy + (L.cy - L.hy) * (0.5 + 0.5 * Math.sin(t * 0.9)) * (1 - grow) + (h / 2 - L.hy) * grow;
    drawStatic(ctx, L, w, ad, E, 0.16, 0.16, 0.16, t);
    ctx.save();
    ctx.beginPath();
    ctx.arc(mx, my, R, 0, TAU);
    ctx.clip();
    drawStatic(ctx, L, w, ad, E, 1, 1, 1, t);
    ctx.restore();
    var g = ctx.createRadialGradient(mx, my, 0, mx, my, R);
    g.addColorStop(0, rgba(TEAL, 0.16 * E));
    g.addColorStop(1, rgba(TEAL, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  }

  function adRibbon(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var cx = w / 2;
    var i;
    ctx.save();
    veil(ctx, w, h, E, 0.66);
    var th = L.H.lines.length * L.hlh + 26;
    var cyc = (L.hTop + L.hBot) / 2;
    var xe = w * sm((t - 0.2) / 1.4);
    var step = 12;
    if (xe > 2) {
      ctx.beginPath();
      for (i = 0; i * step <= xe; i++) {
        var x = i * step;
        var y = cyc - th / 2 + Math.sin(x * 0.018 + t * 1.6) * 7;
        if (i === 0) { ctx.moveTo(x, y); } else { ctx.lineTo(x, y); }
      }
      for (i = Math.floor(xe / step); i >= 0; i--) {
        var xb = i * step;
        ctx.lineTo(xb, cyc + th / 2 + Math.sin(xb * 0.018 + t * 1.6 + 0.8) * 7);
      }
      ctx.closePath();
      var g = ctx.createLinearGradient(0, 0, w, 0);
      g.addColorStop(0, rgba(TEAL, 0.95 * E));
      g.addColorStop(1, rgba('140,225,200', 0.95 * E));
      ctx.fillStyle = g;
      ctx.fill();
    }
    var xe2 = w * sm((t - 0.6) / 1.4);
    if (xe2 > 2) {
      var yb = Math.max(10, cyc - th / 2 - 14);
      ctx.beginPath();
      for (i = 0; i * step <= xe2; i++) {
        var x2 = w - i * step;
        var y2 = yb + Math.sin(x2 * 0.02 - t * 1.4) * 6;
        if (i === 0) { ctx.moveTo(x2, y2); } else { ctx.lineTo(x2, y2); }
      }
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.strokeStyle = rgba(BLUE, 0.9 * E);
      ctx.stroke();
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var hp = eo((t - 1.3) / 0.7);
    setFont(ctx, '700', L.H.size);
    ctx.fillStyle = rgba('10,32,44', E * hp);
    drawLines(ctx, L.H.lines, cx, L.hy + (1 - hp) * 10, L.hlh);
    var sp = eo((t - 1.9) / 0.7);
    setFont(ctx, '400', L.S.size);
    ctx.fillStyle = rgba(WHITE, E * sp);
    drawLines(ctx, L.S.lines, cx, L.sy + 6, L.slh);
    pill(ctx, L, cx, L.cy + 6, eo((t - 2.6) / 0.6), ad.cta || '', t, E);
    ctx.restore();
  }

  function adGrid(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    ctx.save();
    veil(ctx, w, h, E, 0.6);
    drawStatic(ctx, L, w, ad, E, 1, 1, eo((t - 2.8) / 0.6), t);
    var cols = 8;
    var s = w / cols;
    var rows = Math.ceil(h / s);
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var rn = ((c * 7 + r * 13) % 17) / 17;
        var tr = 0.3 + rn * 1.6 + (c + r) * 0.04;
        var a = 1 - sm((t - tr) / 0.6);
        if (a > 0.01) {
          ctx.globalAlpha = E * a * 0.95;
          ctx.fillStyle = (c + r) % 2 ? 'rgb(24,64,84)' : 'rgb(40,110,122)';
          ctx.fillRect(c * s + 1, r * s + 1, s - 2, s - 2);
        }
      }
    }
    ctx.globalAlpha = E * sm((t - 2.2) / 1) * 0.18;
    ctx.fillStyle = rgba(TEAL, 1);
    for (var k = 1; k < cols; k++) { ctx.fillRect(k * s, 0, 1, h); }
    for (var q = 1; q < rows; q++) { ctx.fillRect(0, q * s, w, 1); }
    ctx.restore();
  }

  function adTicker(ctx, w, h, t, dur, ad) {
    var E = envelope(t, dur, 0.6);
    var L = layout(ctx, w, h, ad);
    var cx = w / 2;
    ctx.save();
    veil(ctx, w, h, E, 0.72);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    var n = L.H.lines.length;
    var hp = eo((t - 0.4) / 0.9);
    setFont(ctx, '700', L.H.size);
    ctx.fillStyle = rgba(WHITE, E * hp);
    drawLines(ctx, L.H.lines, cx, h * 0.34 - ((n - 1) * L.hlh) / 2 + (1 - hp) * 12, L.hlh);
    var bp = eo((t - 0.3) / 0.8);
    var bh = 40;
    var by = h * 0.72 + (1 - bp) * (h * 0.4);
    var g = ctx.createLinearGradient(0, 0, w, 0);
    g.addColorStop(0, rgba(TEAL, 0.95 * E));
    g.addColorStop(1, rgba(BLUE, 0.95 * E));
    ctx.fillStyle = g;
    ctx.fillRect(0, by, w, bh);
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, by, w, bh);
    ctx.clip();
    var seg = (ad.sub || '') + '     •     ' + (ad.cta || '') + '     •     ';
    setFont(ctx, '600', 16);
    var segW = Math.max(40, ctx.measureText(seg).width);
    var off = (t * 64) % segW;
    ctx.textAlign = 'left';
    ctx.fillStyle = rgba('10,32,44', E);
    for (var x = -off; x < w; x += segW) { ctx.fillText(seg, x, by + bh / 2 + 1); }
    ctx.restore();
    var tp = eo((t - 0.7) / 0.8);
    var ty = by - 14 - (1 - tp) * 10;
    ctx.textAlign = 'left';
    ctx.fillStyle = rgba(TEAL, E * tp * 0.85);
    ctx.fillRect(0, ty, w, 1);
    setFont(ctx, '600', 13);
    var seg2 = (ad.cta || '') + '     •     ';
    var seg2W = Math.max(40, ctx.measureText(seg2).width);
    var off2 = (t * 40) % seg2W;
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, by - 34, w, 18);
    ctx.clip();
    ctx.fillStyle = rgba(SOFT, E * tp * 0.7);
    for (var x2 = off2 - seg2W; x2 < w; x2 += seg2W) { ctx.fillText(seg2, x2, by - 24); }
    ctx.restore();
    ctx.restore();
  }

  var ads = [
    { id: 'kinetic', name: 'Typographie cinétique', draw: adKinetic },
    { id: 'split', name: 'Volets', draw: adSplit },
    { id: 'orbits', name: 'Orbites', draw: adOrbits },
    { id: 'sweep', name: 'Balayage de dégradé', draw: adSweep },
    { id: 'cards', name: 'Cartes empilées', draw: adCards },
    { id: 'typewriter', name: 'Machine à écrire', draw: adTypewriter },
    { id: 'spotlight', name: 'Projecteur', draw: adSpotlight },
    { id: 'ribbon', name: 'Ruban', draw: adRibbon },
    { id: 'grid', name: 'Grille qui se révèle', draw: adGrid },
    { id: 'ticker', name: 'Bandeau défilant', draw: adTicker }
  ];

  var jc = { key: '', val: null };

  function jlayout(ctx, w, h, msg) {
    var title = msg.title || '';
    var src = msg.lines || [];
    var key = w + '|' + h + '|' + title + '|' + src.join('~');
    if (jc.key === key) { return jc.val; }
    var maxW = Math.min(w * 0.86, 620);
    var scale = 1;
    var T;
    var sz;
    var groups;
    var lh;
    var titleH;
    var gap;
    var total;
    var i;
    for (var it = 0; it < 6; it++) {
      T = fit(ctx, title, maxW, 1, Math.min(w * 0.14, 58) * scale, 16, '800');
      sz = Math.min(w * 0.046, 20) * scale;
      var lines3 = src.slice(0, 3);
      for (i = 0; i < lines3.length; i++) {
        var f = fit(ctx, lines3[i], maxW, 2, sz, 12, '400');
        if (f.size < sz) { sz = f.size; }
      }
      groups = [];
      var cnt = 0;
      for (i = 0; i < lines3.length; i++) {
        var gl = wrapAt(ctx, lines3[i], maxW, sz, '400').lines;
        groups.push(gl);
        cnt += gl.length;
      }
      lh = sz * 1.4;
      titleH = T.size * 1.15;
      gap = T.size * 0.6;
      total = titleH + gap + cnt * lh + Math.max(0, groups.length - 1) * sz * 0.5;
      if (total <= h * 0.88) { break; }
      scale *= 0.88;
    }
    var top = (h - total) / 2;
    var v = { maxW: maxW, T: T, sz: sz, groups: groups, lh: lh, total: total, top: top, ty: top + titleH / 2, ly: top + titleH + gap, gp: sz * 0.5 };
    jc.key = key;
    jc.val = v;
    return v;
  }

  function jbase(ctx, w, h, E, cx, cy) {
    ctx.fillStyle = rgba('18,18,30', 0.64 * E);
    ctx.fillRect(0, 0, w, h);
    var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.55);
    g.addColorStop(0, rgba(PINK, 0.12 * E));
    g.addColorStop(1, rgba(PINK, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  }

  function jlinesEach(L, fn) {
    var y = L.ly + L.lh / 2;
    var idx = 0;
    for (var g = 0; g < L.groups.length; g++) {
      for (var i = 0; i < L.groups[g].length; i++) {
        fn(L.groups[g][i], y, g, idx);
        y += L.lh;
        idx++;
      }
      y += L.gp;
    }
  }

  function jingleDraw(ctx, w, h, t, dur, msg, variant, data) {
    var E = envelope(t, dur, 0.6);
    var L = jlayout(ctx, w, h, msg || {});
    var v = ((variant | 0) % 3 + 3) % 3;
    var cx = w / 2;
    var bass = data && data.bass ? data.bass : 0;
    var title = (msg && msg.title) || '';
    ctx.save();
    jbase(ctx, w, h, E, cx, L.ty);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (v === 0) {
      setFont(ctx, '800', L.T.size);
      var tw = ctx.measureText(title).width;
      var sx = cx - tw / 2;
      for (var i = 0; i < title.length; i++) {
        var p = eo((t - (0.15 + i * 0.07)) / 0.5);
        if (p <= 0) { continue; }
        var pre = ctx.measureText(title.slice(0, i)).width;
        var cw = ctx.measureText(title.charAt(i)).width;
        ctx.save();
        ctx.translate(sx + pre + cw / 2, L.ty - (1 - p) * 30);
        var s = 0.6 + 0.4 * p;
        ctx.scale(s, s);
        ctx.fillStyle = rgba(WHITE, E * p);
        ctx.fillText(title.charAt(i), 0, 0);
        ctx.restore();
      }
      var up = sm((t - 1) / 0.8);
      if (up > 0) {
        var ug = ctx.createLinearGradient(cx - tw / 2, 0, cx + tw / 2, 0);
        ug.addColorStop(0, rgba(PINK, E));
        ug.addColorStop(1, rgba(RBLUE, E));
        ctx.fillStyle = ug;
        ctx.fillRect(cx - (tw / 2) * up, L.ty + L.T.size * 0.62, tw * up, 3);
      }
      setFont(ctx, '400', L.sz);
      jlinesEach(L, function (line, y, g) {
        var q = eo((t - 1.4 - g * 0.5) / 0.7);
        ctx.fillStyle = rgba(SOFT, E * q);
        ctx.fillText(line, cx, y + (1 - q) * 14);
      });
    } else if (v === 1) {
      var maxR = Math.max(w, h) * 0.6;
      ctx.lineWidth = 2;
      for (var k = 0; k < 4; k++) {
        var ph = (t * 0.4 + k / 4) % 1;
        var rr = ph * maxR + L.T.size;
        ctx.strokeStyle = rgba(k % 2 ? RBLUE : PINK, E * (1 - ph) * 0.7 * eo(t / 0.8));
        ctx.beginPath();
        ctx.arc(cx, L.ty, rr, 0, TAU);
        ctx.stroke();
      }
      var tp = eo((t - 0.2) / 0.8);
      ctx.save();
      ctx.translate(cx, L.ty);
      var ps = 1 + bass * 0.05 + 0.03 * Math.sin(t * 2);
      ctx.scale(ps, ps);
      setFont(ctx, '800', L.T.size);
      ctx.fillStyle = rgba(WHITE, E * tp);
      ctx.fillText(title, 0, (1 - tp) * 10);
      ctx.restore();
      setFont(ctx, '400', L.sz);
      jlinesEach(L, function (line, y, g) {
        var q = eo((t - 1.2 - g * 0.5) / 0.7);
        ctx.fillStyle = rgba(SOFT, E * q);
        ctx.fillText(line, cx, y + (1 - q) * 10);
      });
    } else {
      setFont(ctx, '800', L.T.size);
      var tw2 = ctx.measureText(title).width;
      var rp = sm((t - 0.2) / 1);
      ctx.save();
      ctx.beginPath();
      ctx.rect(cx - (tw2 / 2 + 6) * rp, L.ty - L.T.size, (tw2 + 12) * rp, L.T.size * 2);
      ctx.clip();
      ctx.fillStyle = rgba(WHITE, E);
      ctx.fillText(title, cx, L.ty);
      ctx.restore();
      var lg = ctx.createLinearGradient(cx - L.maxW / 2, 0, cx + L.maxW / 2, 0);
      lg.addColorStop(0, rgba(PINK, E));
      lg.addColorStop(1, rgba(RBLUE, E));
      ctx.fillStyle = lg;
      var rw = (L.maxW / 2) * rp;
      ctx.fillRect(cx - rw, L.ty - L.T.size * 0.75, rw * 2, 2);
      ctx.fillRect(cx - rw, L.ty + L.T.size * 0.75, rw * 2, 2);
      ctx.textAlign = 'left';
      setFont(ctx, '400', L.sz);
      jlinesEach(L, function (line, y, g) {
        var lw = ctx.measureText(line).width;
        var wp = sm((t - 1.3 - g * 0.6) / 0.9);
        if (wp <= 0) { return; }
        ctx.save();
        ctx.beginPath();
        ctx.rect(cx - lw / 2 - 2, y - L.lh / 2, (lw + 4) * wp, L.lh);
        ctx.clip();
        ctx.fillStyle = rgba(SOFT, E);
        ctx.fillText(line, cx - lw / 2, y);
        ctx.restore();
      });
    }
    ctx.restore();
  }

  window.CreaMotion = {
    envelope: envelope,
    jingle: { variants: 3, draw: jingleDraw },
    ads: ads
  };
})();
