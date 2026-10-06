(function () {
  'use strict';

  var PI = Math.PI;
  var TAU = Math.PI * 2;

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function easeOutBack(x) {
    var c1 = 1.70158;
    var c3 = c1 + 1;
    return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
  }
  function hsl(h, s, l, a) {
    return 'hsla(' + (((h % 360) + 360) % 360) + ',' + s + '%,' + l + '%,' + (a === undefined ? 1 : a) + ')';
  }
  function foldBpm(bpm) {
    var b = Number(bpm) || 120;
    while (b < 80) { b *= 2; }
    while (b > 170) { b /= 2; }
    return b;
  }
  function pos(v) { return v > 0 ? v : 0; }

  var STYLES = [
    { id: 'disco', arms: 'point', legs: 'step', hop: 1.0, lean: 0.10, eyes: 'happy', bg: 'ball', hue: 310 },
    { id: 'rock', arms: 'strum', legs: 'wide', hop: 0.5, lean: 0.05, nod: 0.3, prop: 'guitar', bg: 'spot', hue: 8 },
    { id: 'hiphop', arms: 'cross', legs: 'bounce', hop: 0.6, lean: 0.15, glasses: true, hat: 'cap', bg: 'spot', hue: 45 },
    { id: 'electro', arms: 'robot', legs: 'step', hop: 0.8, glasses: true, bg: 'lasers', hue: 190 },
    { id: 'classique', arms: 'conduct', legs: 'none', hop: 0.08, lean: 0.06, prop: 'baton', hat: 'bow', bg: 'candles', hue: 40 },
    { id: 'jazz', arms: 'sway', legs: 'slow', hop: 0.3, lean: 0.14, prop: 'trumpet', hat: 'fedora', eyes: 'closed', bg: 'spot', hue: 260 },
    { id: 'folk', arms: 'strum', legs: 'tap', hop: 0.3, lean: 0.05, prop: 'guitar', hat: 'cowboy', bg: 'stars', hue: 95 },
    { id: 'latin', arms: 'shake', legs: 'slow', hop: 0.7, lean: 0.18, prop: 'maracas', eyes: 'happy', bg: 'ball', hue: 20 },
    { id: 'reggae', arms: 'sway', legs: 'tap', hop: 0.25, lean: 0.2, hat: 'rasta', eyes: 'half', bg: 'stars', hue: 130 },
    { id: 'metal', arms: 'devil', legs: 'wide', hop: 0.4, nod: 0.5, hat: 'horns', bg: 'fire', hue: 355 },
    { id: 'chill', arms: 'wave', legs: 'none', hop: 0, float: 1, lean: 0.05, eyes: 'closed', bg: 'stars', hue: 220 },
    { id: 'choir', arms: 'pray', legs: 'none', hop: 0.05, eyes: 'closed', hat: 'halo', bg: 'candles', singing: true, hue: 50 },
    { id: 'epic', arms: 'wide', legs: 'none', hop: 0.2, lean: 0.04, cape: true, bg: 'beams', hue: 210 },
    { id: 'synthwave', arms: 'alt', legs: 'step', hop: 0.5, glasses: true, bg: 'grid', hue: 300 },
    { id: 'lofi', arms: 'ear', legs: 'none', hop: 0.1, nod: 0.4, eyes: 'half', bg: 'moon', hue: 250 },
    { id: 'celtic', arms: 'jig', legs: 'jig', hop: 0.9, lean: 0.03, hat: 'cap', bg: 'stars', hue: 150 },
    { id: 'afro', arms: 'drum', legs: 'step', hop: 0.6, prop: 'drum', eyes: 'happy', bg: 'ball', hue: 30 },
    { id: 'punk', arms: 'fist', legs: 'pogo', hop: 1.4, nod: 0.2, hat: 'mohawk', bg: 'lasers', hue: 330 },
    { id: 'valse', arms: 'twirl', legs: 'step', hop: 0.3, lean: 0.12, path: true, eyes: 'happy', bg: 'candles', hue: 340 },
    { id: 'pop', arms: 'alt', legs: 'step', hop: 0.8, lean: 0.12, bg: 'beams', hue: 200 }
  ];

  var IDX = {};
  STYLES.forEach(function (s, i) { IDX[s.id] = i; });

  var RULES = [
    ['metal', /metal|hard-rock/],
    ['punk', /punk|indie|madness/],
    ['reggae', /reggae|dub|ska/],
    ['rock', /rock|hallyday|progressif/],
    ['hiphop', /rap|hip-hop|hip hop/],
    ['electro', /drum-and-bass|house|trance|hard-tech|\btech\b|electro-atmos|electro-spatiale|francais_tests-electro/],
    ['epic', /vangelis|epique|cinema/],
    ['synthwave', /jeux-video|futuriste|electro-pop|synthes/],
    ['choir', /gregorien|chorale|acappella|a cappella|gospel|mongol/],
    ['classique', /classique|piano|harpe|inde-classique|chine|japon/],
    ['jazz', /jazz|blues|saxophone|tango|soul|motown/],
    ['disco', /disco|groove|jackson|funk/],
    ['latin', /salsa|latin|bachata|merengue|bresil|mariachi|flamenco|caraibes/],
    ['afro', /percussion|tribal|afrobeats|maghreb|gamelan|bollywood|polynesie/],
    ['celtic', /celtique|medieval|renaissance|tri-yann|klezmer|balkans|nordique/],
    ['valse', /valse|musette|annees-50|lapointe/],
    ['folk', /folk|guitare|dylan|country|bluegrass|tiersen|goldman|perso/],
    ['chill', /ambient|chill/],
    ['lofi', /poesie|instrumental|lofi/]
  ];

  var pickCache = {};

  function pick(track) {
    var tr = track || {};
    var key = (tr.playlist || '') + '|' + (tr.energy === null || tr.energy === undefined ? '' : Math.round(tr.energy * 4));
    if (pickCache[key] !== undefined) { return pickCache[key]; }
    var text = ((tr.playlist || '') + ' ' + (tr.playlist_label || '')).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    var res = IDX.pop;
    var found = false;
    for (var i = 0; i < RULES.length; i++) {
      if (RULES[i][1].test(text)) { res = IDX[RULES[i][0]]; found = true; break; }
    }
    if (!found && typeof tr.energy === 'number') {
      if (tr.energy > 0.75) { res = IDX.electro; } else if (tr.energy < 0.25) { res = IDX.chill; }
    }
    pickCache[key] = res;
    return res;
  }

  function arms(kind, p, t, k) {
    var s = Math.sin(PI * p);
    switch (kind) {
      case 'point': {
        var side = Math.floor(p / 2) % 2;
        var up = 2.45 + 0.3 * Math.sin(TAU * p);
        return side ? [0.55, up] : [up, 0.55];
      }
      case 'strum': return [1.25, 0.9 + 0.35 * Math.sin(TAU * p * 2)];
      case 'cross': return [-0.7 + 0.25 * Math.sin(TAU * p), -0.7 - 0.25 * Math.sin(TAU * p)];
      case 'robot': {
        var table = [[1.57, 0.5], [2.4, 1.57], [0.5, 2.4], [1.57, 1.57]];
        return table[Math.floor(p * 2) % 4];
      }
      case 'conduct': return [0.9 + 0.3 * Math.sin(PI * p / 2 + 1), 1.6 + 0.8 * s];
      case 'sway': return [1.2 + 0.5 * Math.sin(PI * p / 2), 1.2 - 0.5 * Math.sin(PI * p / 2)];
      case 'shake': return [1.7 + 0.25 * Math.sin(TAU * p * 4), 1.7 - 0.25 * Math.sin(TAU * p * 4)];
      case 'devil': return [2.5 + 0.2 * Math.sin(TAU * p), 2.5 - 0.2 * Math.sin(TAU * p)];
      case 'wave': return [1.8 + 0.7 * Math.sin(t * 1.2), 1.8 + 0.7 * Math.sin(t * 1.2 + PI)];
      case 'pray': return [-1.25, -1.25];
      case 'wide': return [2.2 + 0.5 * Math.sin(PI * p / 2), 2.2 + 0.5 * Math.sin(PI * p / 2)];
      case 'ear': return [2.5, 0.7 + 0.3 * s];
      case 'jig': return [0.25 + 0.1 * Math.sin(TAU * p * 2), 0.25 - 0.1 * Math.sin(TAU * p * 2)];
      case 'drum': return [0.9 + 0.7 * pos(Math.sin(TAU * p)), 0.9 + 0.7 * pos(-Math.sin(TAU * p))];
      case 'fist': return [2.8 + 0.4 * Math.sin(TAU * p), 2.8 - 0.4 * Math.sin(TAU * p)];
      case 'twirl': return [1.55 + 0.2 * Math.sin(PI * p), 1.55 - 0.2 * Math.sin(PI * p)];
      default: return [2.0 + 0.9 * s, 2.0 - 0.9 * s];
    }
  }

  function legs(kind, p, k) {
    var s = Math.sin(PI * p);
    switch (kind) {
      case 'step': return [pos(s) * 0.3, pos(-s) * 0.3];
      case 'slow': return [pos(Math.sin(PI * p / 2)) * 0.2, pos(-Math.sin(PI * p / 2)) * 0.2];
      case 'wide': return [0.1 * k, 0.1 * k];
      case 'bounce': return [0.12 * k, 0.12 * k];
      case 'tap': return [0.15 * pos(Math.sin(TAU * p)), 0];
      case 'jig': return [0.35 * pos(Math.sin(TAU * p * 2)), 0.35 * pos(-Math.sin(TAU * p * 2))];
      case 'pogo': return [0.4 * Math.abs(s), 0.4 * Math.abs(s)];
      default: return [0, 0];
    }
  }

  function bgGradient(ctx, w, h, hue) {
    var g = ctx.createLinearGradient(0, 0, w, h);
    g.addColorStop(0, hsl(hue + 250, 60, 15));
    g.addColorStop(1, hsl(hue + 310, 70, 9));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);
  }

  function drawBg(ctx, w, h, t, kind, hue, tr, bass) {
    var s = Math.min(w, h);
    var i;
    var g;
    if (kind === 'ball') {
      ctx.fillStyle = 'rgba(255,255,255,0.15)';
      ctx.fillRect(w / 2 - 0.5, 0, 1, h * 0.12);
      g = ctx.createRadialGradient(w / 2 - s * 0.03, h * 0.14, 0, w / 2, h * 0.16, s * 0.11);
      g.addColorStop(0, 'rgba(255,255,255,0.95)');
      g.addColorStop(1, hsl(hue, 30, 55, 0.9));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(w / 2, h * 0.16, s * 0.1, 0, TAU);
      ctx.fill();
      for (i = 0; i < 14; i++) {
        var a = t * 0.8 + i * (TAU / 14);
        var r = s * (0.25 + 0.2 * ((i * 37) % 10) / 10);
        ctx.fillStyle = hsl(hue + i * 25, 90, 70, 0.5 * (0.5 + 0.5 * Math.sin(t * 3 + i)));
        ctx.beginPath();
        ctx.arc(w / 2 + Math.cos(a) * r * 1.3, h * 0.45 + Math.sin(a) * r * 0.8, s * 0.018, 0, TAU);
        ctx.fill();
      }
    } else if (kind === 'lasers') {
      ctx.lineWidth = 1.5;
      for (i = 0; i < 7; i++) {
        var ang = Math.sin(t * (0.8 + i * 0.13) + i) * 0.7;
        ctx.strokeStyle = hsl(hue + i * 22, 100, 65, 0.45);
        ctx.beginPath();
        ctx.moveTo(i % 2 ? w : 0, 0);
        ctx.lineTo(w / 2 + Math.tan(ang) * h, h);
        ctx.stroke();
      }
    } else if (kind === 'fire') {
      for (i = 0; i < 12; i++) {
        var fh = s * (0.18 + 0.14 * Math.abs(Math.sin(t * 7 + i * 1.9)) + 0.1 * bass);
        var fx = (i + 0.5) * (w / 12);
        ctx.fillStyle = hsl(10 + (i % 3) * 14, 100, 52, 0.75);
        ctx.beginPath();
        ctx.moveTo(fx - w / 24, h);
        ctx.quadraticCurveTo(fx + Math.sin(t * 5 + i) * 4, h - fh * 0.6, fx, h - fh);
        ctx.quadraticCurveTo(fx + w / 24, h - fh * 0.5, fx + w / 24, h);
        ctx.fill();
      }
    } else if (kind === 'stars') {
      for (i = 0; i < 22; i++) {
        var sx = ((i * 53) % 100) / 100 * w;
        var sy = ((i * 29) % 70) / 100 * h;
        ctx.fillStyle = 'rgba(255,255,255,' + (0.25 + 0.6 * Math.abs(Math.sin(t * 1.5 + i))) + ')';
        ctx.fillRect(sx, sy, 1.8, 1.8);
      }
    } else if (kind === 'grid') {
      g = ctx.createLinearGradient(0, h * 0.25, 0, h * 0.62);
      g.addColorStop(0, hsl(hue + 20, 100, 62, 0.95));
      g.addColorStop(1, hsl(hue - 60, 100, 55, 0.95));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(w / 2, h * 0.62, s * 0.3, PI, 0);
      ctx.fill();
      ctx.strokeStyle = hsl(hue + 40, 100, 65, 0.6);
      ctx.lineWidth = 1;
      for (i = -6; i <= 6; i++) {
        ctx.beginPath();
        ctx.moveTo(w / 2 + i * w * 0.02, h * 0.62);
        ctx.lineTo(w / 2 + i * w * 0.2, h);
        ctx.stroke();
      }
      for (i = 0; i < 6; i++) {
        var gy = h * 0.62 + Math.pow(((i + (t * 0.8) % 1) / 6), 2) * h * 0.38;
        ctx.beginPath();
        ctx.moveTo(0, gy);
        ctx.lineTo(w, gy);
        ctx.stroke();
      }
    } else if (kind === 'candles') {
      for (i = 0; i < 4; i++) {
        var cx = w * (0.12 + i * 0.25);
        var fl = 0.7 + 0.3 * Math.sin(t * 9 + i * 2);
        var rg = ctx.createRadialGradient(cx, h * 0.74, 0, cx, h * 0.74, s * 0.25);
        rg.addColorStop(0, 'rgba(255,200,90,' + 0.35 * fl + ')');
        rg.addColorStop(1, 'rgba(255,200,90,0)');
        ctx.fillStyle = rg;
        ctx.fillRect(cx - s * 0.25, h * 0.74 - s * 0.25, s * 0.5, s * 0.5);
        ctx.fillStyle = '#f4e9d0';
        ctx.fillRect(cx - 2, h * 0.78, 4, h * 0.14);
        ctx.fillStyle = 'rgba(255,190,70,' + fl + ')';
        ctx.beginPath();
        ctx.ellipse(cx, h * 0.76, 2.5, 5 * fl, 0, 0, TAU);
        ctx.fill();
      }
    } else if (kind === 'moon') {
      ctx.fillStyle = 'rgba(255,245,200,0.92)';
      ctx.beginPath();
      ctx.arc(w * 0.76, h * 0.22, s * 0.12, 0, TAU);
      ctx.fill();
      ctx.fillStyle = hsl(hue + 250, 60, 14);
      ctx.beginPath();
      ctx.arc(w * 0.8, h * 0.19, s * 0.1, 0, TAU);
      ctx.fill();
      drawBg(ctx, w, h, t, 'stars', hue, tr, bass);
    } else if (kind === 'spot') {
      g = ctx.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, 'rgba(255,255,255,0.22)');
      g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.moveTo(w * 0.42, 0);
      ctx.lineTo(w * 0.58, 0);
      ctx.lineTo(w * 0.9, h);
      ctx.lineTo(w * 0.1, h);
      ctx.closePath();
      ctx.fill();
    } else {
      for (i = 0; i < 3; i++) {
        var ang2 = Math.sin(t * 0.7 + i * 2.1) * 0.5;
        ctx.save();
        ctx.translate(w * (0.2 + i * 0.3), -h * 0.1);
        ctx.rotate(ang2);
        var bg = ctx.createLinearGradient(0, 0, 0, h * 1.2);
        bg.addColorStop(0, hsl(hue + i * 70, 90, 65, 0.05 + tr * 0.22));
        bg.addColorStop(1, hsl(hue + i * 70, 90, 65, 0));
        ctx.fillStyle = bg;
        ctx.beginPath();
        ctx.moveTo(-4, 0);
        ctx.lineTo(4, 0);
        ctx.lineTo(w * 0.28, h * 1.2);
        ctx.lineTo(-w * 0.28, h * 1.2);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }
    }
    var fg = ctx.createRadialGradient(w / 2, h * 0.92, 0, w / 2, h * 0.92, w * 0.6);
    fg.addColorStop(0, hsl(hue + 20, 90, 60, 0.3));
    fg.addColorStop(1, hsl(hue + 20, 90, 60, 0));
    ctx.fillStyle = fg;
    ctx.fillRect(0, h * 0.5, w, h * 0.5);
  }

  function drawEqualizer(ctx, w, h, t, d, hue) {
    var n = 9;
    var bw = w / (n * 1.6);
    var gap = bw * 0.6;
    var x0 = (w - (n * bw + (n - 1) * gap)) / 2;
    for (var i = 0; i < n; i++) {
      var band = i < 3 ? d.bass : i < 6 ? d.mid : d.treble;
      var v = 0.12 + 0.55 * band + 0.18 * Math.abs(Math.sin(t * (2 + i * 0.7) + i));
      var bh = h * 0.15 * clamp01(v);
      ctx.fillStyle = hsl(hue + i * 14, 85, 62, 0.75);
      ctx.fillRect(x0 + i * (bw + gap), h - bh, bw, bh);
    }
  }

  function drawNotes(ctx, w, h, t, s, hue) {
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (var k = 0; k < 6; k++) {
      var life = (t * 0.22 + k / 6) % 1;
      var x = w * 0.5 + Math.sin(k * 2.1 + t * 0.9) * s * 0.42;
      var y = h * 0.95 - life * h * 0.9;
      ctx.globalAlpha = Math.sin(life * PI) * 0.85;
      ctx.fillStyle = hsl(hue + k * 40, 90, 72);
      ctx.font = '700 ' + Math.round(s * (0.07 + 0.03 * (k % 2))) + 'px system-ui, sans-serif';
      ctx.fillText(k % 2 ? '♫' : '♪', x, y);
    }
    ctx.restore();
  }

  function limb(ctx, x1, y1, x2, y2, width, color) {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  function ell(ctx, x, y, rx, ry, rot) {
    ctx.beginPath();
    ctx.ellipse(x, y, Math.max(0.01, rx), Math.max(0.01, ry), rot || 0, 0, TAU);
  }

  function drawHat(ctx, hat, u, hue, t, kick) {
    var y = -u * 0.88;
    var i;
    if (hat === 'cap') {
      ctx.fillStyle = hsl(hue + 180, 80, 50);
      ctx.beginPath();
      ctx.arc(0, y + u * 0.1, u * 0.78, PI, TAU);
      ctx.fill();
      ctx.fillRect(-u * 0.1, y + u * 0.02, u * 1.0, u * 0.12);
    } else if (hat === 'cowboy' || hat === 'fedora') {
      ctx.fillStyle = hat === 'cowboy' ? '#8a5a2b' : '#2b2b3a';
      ell(ctx, 0, y + u * 0.12, u * (hat === 'cowboy' ? 1.15 : 1.0), u * 0.2);
      ctx.fill();
      ctx.beginPath();
      ctx.rect(-u * 0.5, y - u * 0.4, u, u * 0.5);
      ctx.fill();
      ctx.fillStyle = hat === 'cowboy' ? '#d9b36a' : '#d94a6a';
      ctx.fillRect(-u * 0.5, y - u * 0.05, u, u * 0.1);
    } else if (hat === 'rasta') {
      var cols = ['#2fb344', '#f4d03f', '#e04848'];
      for (i = 0; i < 3; i++) {
        ctx.fillStyle = cols[i];
        ctx.beginPath();
        ctx.arc(0, y + u * 0.2, u * (0.88 - i * 0.2), PI, TAU);
        ctx.fill();
      }
    } else if (hat === 'horns') {
      ctx.fillStyle = '#e8e8f0';
      [-1, 1].forEach(function (sd) {
        ctx.beginPath();
        ctx.moveTo(sd * u * 0.45, y + u * 0.2);
        ctx.quadraticCurveTo(sd * u * 0.95, y - u * 0.1, sd * u * 0.7, y - u * 0.55);
        ctx.quadraticCurveTo(sd * u * 0.6, y - u * 0.1, sd * u * 0.2, y + u * 0.2);
        ctx.fill();
      });
    } else if (hat === 'halo') {
      ctx.strokeStyle = 'rgba(255,230,120,' + (0.7 + 0.3 * Math.sin(t * 3)) + ')';
      ctx.lineWidth = u * 0.1;
      ell(ctx, 0, y - u * 0.25, u * 0.55, u * 0.15);
      ctx.stroke();
    } else if (hat === 'mohawk') {
      ctx.fillStyle = hsl(hue + 60, 100, 60);
      for (i = -2; i <= 2; i++) {
        ctx.beginPath();
        ctx.moveTo(i * u * 0.16 - u * 0.09, y + u * 0.15);
        ctx.lineTo(i * u * 0.16, y - u * (0.55 - Math.abs(i) * 0.07) - u * 0.1 * kick);
        ctx.lineTo(i * u * 0.16 + u * 0.09, y + u * 0.15);
        ctx.fill();
      }
    } else if (hat === 'bow') {
      ctx.fillStyle = '#d94a6a';
      ctx.beginPath();
      ctx.moveTo(0, u * 0.82);
      ctx.lineTo(-u * 0.3, u * 0.68);
      ctx.lineTo(-u * 0.3, u * 0.96);
      ctx.closePath();
      ctx.moveTo(0, u * 0.82);
      ctx.lineTo(u * 0.3, u * 0.68);
      ctx.lineTo(u * 0.3, u * 0.96);
      ctx.closePath();
      ctx.fill();
    }
  }

  function drawProp(ctx, prop, u, hue, p, t, k, hands) {
    var hl = hands[0];
    var hr = hands[1];
    if (prop === 'guitar') {
      ctx.save();
      ctx.translate(u * 0.1, u * 0.55);
      ctx.rotate(-0.45);
      ctx.fillStyle = '#b5651d';
      ell(ctx, 0, 0, u * 0.5, u * 0.34);
      ctx.fill();
      ctx.fillStyle = '#2b1a0c';
      ell(ctx, 0, 0, u * 0.12, u * 0.12);
      ctx.fill();
      ctx.strokeStyle = '#5b3a1a';
      ctx.lineWidth = u * 0.1;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(-u * 0.4, 0);
      ctx.lineTo(-u * 1.3, 0);
      ctx.stroke();
      ctx.restore();
    } else if (prop === 'maracas') {
      [hl, hr].forEach(function (h2, i) {
        ctx.fillStyle = hsl(hue + i * 90, 90, 60);
        ell(ctx, h2[0], h2[1] - u * 0.18, u * 0.14, u * 0.2);
        ctx.fill();
      });
    } else if (prop === 'trumpet') {
      ctx.strokeStyle = '#e8c14a';
      ctx.lineWidth = u * 0.1;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(u * 0.12, u * 0.33);
      ctx.lineTo(u * 1.0, u * 0.2);
      ctx.stroke();
      ctx.fillStyle = '#e8c14a';
      ctx.beginPath();
      ctx.moveTo(u * 1.0, u * 0.2);
      ctx.lineTo(u * 1.3, u * 0.02);
      ctx.lineTo(u * 1.3, u * 0.42);
      ctx.closePath();
      ctx.fill();
    } else if (prop === 'baton') {
      ctx.strokeStyle = '#f4f4f4';
      ctx.lineWidth = u * 0.05;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(hr[0], hr[1]);
      ctx.lineTo(hr[0] + hr[2] * u * 0.55, hr[1] + hr[3] * u * 0.55);
      ctx.stroke();
    } else if (prop === 'drum') {
      var sc = 1 + 0.08 * k;
      ctx.fillStyle = hsl(hue + 20, 80, 45);
      ell(ctx, 0, u * 0.82, u * 0.55 * sc, u * 0.3 * sc);
      ctx.fill();
      ctx.strokeStyle = '#f4e3b0';
      ctx.lineWidth = u * 0.05;
      ctx.stroke();
    }
  }

  function drawCharacter(ctx, w, h, t, d, bpm, s, st, hue) {
    var u = s * 0.25;
    var phase = t * foldBpm(bpm) / 60;
    var frac = phase - Math.floor(phase);
    var kick = Math.min(1, Math.pow(1 - frac, 3) * 0.5 + d.bass * 0.7);
    var hopBase = Math.abs(Math.sin(PI * phase)) * u * 0.32 * (0.5 + 0.5 * Math.min(1, d.level * 1.6 + 0.3));
    var hop = hopBase * st.hop;
    var floaty = st.float ? Math.sin(t * 1.5) * u * 0.14 - u * 0.1 : 0;
    var lean = (st.lean || 0) * Math.sin(PI * phase) + (st.nod || 0) * 0.35 * Math.sin(TAU * phase + 0.4) * (0.5 + kick * 0.5);
    var pop = easeOutBack(clamp01(t / 0.6));
    var squash = 1 + 0.07 * kick;
    var cx = w / 2 + (st.path ? Math.sin(t * 1.6) * s * 0.18 : 0);
    var baseY = h * 0.55;
    var cy = baseY - hop - floaty;
    var skin = hsl(hue + 150, 85, 62);
    var dark = hsl(hue + 200, 70, 38);
    var armsA = arms(st.arms, phase, t, kick);
    var legsL = legs(st.legs, phase, kick);
    var spread = st.legs === 'wide' ? 0.62 : 0.38;
    var i;

    ctx.fillStyle = 'rgba(0,0,0,0.3)';
    ell(ctx, cx, baseY + u * 1.15, u * (1.0 - Math.min(0.5, (hop + Math.abs(floaty)) / (u * 1.4))), u * 0.16);
    ctx.fill();

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(lean);
    ctx.scale(pop * (2 - squash), pop * squash);

    if (st.cape) {
      ctx.fillStyle = hsl(hue + 330, 80, 40, 0.9);
      ctx.beginPath();
      ctx.moveTo(-u * 0.7, -u * 0.2);
      ctx.quadraticCurveTo(-u * (1.5 + 0.2 * Math.sin(t * 4)), u * 0.6, -u * (1.2 + 0.3 * Math.sin(t * 5 + 1)), u * 1.3);
      ctx.lineTo(u * (1.2 + 0.3 * Math.sin(t * 5)), u * 1.3);
      ctx.quadraticCurveTo(u * (1.5 + 0.2 * Math.sin(t * 4 + 2)), u * 0.6, u * 0.7, -u * 0.2);
      ctx.closePath();
      ctx.fill();
    }

    var handsXY = [];
    var armLen = u * 0.8;
    [-1, 1].forEach(function (side, idx) {
      var a = armsA[idx];
      var dx = side * Math.sin(a);
      var dy = Math.cos(a);
      var sx = side * u * 0.75;
      var sy = u * 0.05;
      var hx = sx + dx * armLen;
      var hy = sy + dy * armLen;
      limb(ctx, sx, sy, hx, hy, u * 0.22, dark);
      handsXY.push([hx, hy, dx, dy]);
    });
    ctx.fillStyle = hsl(hue + 150, 85, 78);
    handsXY.forEach(function (hnd) { ell(ctx, hnd[0], hnd[1], u * 0.17, u * 0.17); ctx.fill(); });

    var fl = [u * (1.1 - legsL[0]), u * (1.1 - legsL[1])];
    limb(ctx, -u * 0.38, u * 0.8, -u * spread * 1.15, fl[0], u * 0.22, dark);
    limb(ctx, u * 0.38, u * 0.8, u * spread * 1.15, fl[1], u * 0.22, dark);

    var body = ctx.createLinearGradient(0, -u, 0, u);
    body.addColorStop(0, hsl(hue + 150, 85, 66));
    body.addColorStop(1, hsl(hue + 200, 80, 52));
    ctx.fillStyle = body;
    ell(ctx, 0, 0, u * 0.95, u * 0.95);
    ctx.fill();
    ctx.fillStyle = hsl(hue + 150, 85, 82, 0.35);
    ell(ctx, -u * 0.25, -u * 0.5, u * 0.4, u * 0.22, -0.5);
    ctx.fill();

    ctx.strokeStyle = '#f4f7ff';
    ctx.lineWidth = u * 0.16;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(0, -u * 0.05, u * 1.0, PI * 1.06, PI * 1.94);
    ctx.stroke();
    ctx.fillStyle = hsl(hue, 90, 55 + kick * 12);
    var cup = u * 0.34;
    ctx.fillRect(-u * 1.12, -u * 0.35, cup, u * 0.7);
    ctx.fillRect(u * 1.12 - cup, -u * 0.35, cup, u * 0.7);

    var blink = (t % 3.2) > 3.05 ? 0.1 : 1;
    var look = Math.sin(t * 1.3) * u * 0.06;
    for (i = -1; i <= 1; i += 2) {
      if (st.eyes === 'closed' || st.eyes === 'happy') {
        ctx.strokeStyle = '#1a2233';
        ctx.lineWidth = u * 0.09;
        ctx.beginPath();
        ctx.arc(i * u * 0.36, -u * 0.1, u * 0.17, st.eyes === 'happy' ? PI : 0, st.eyes === 'happy' ? TAU : PI);
        ctx.stroke();
      } else {
        var lid = st.eyes === 'half' ? 0.5 : 1;
        ctx.fillStyle = '#ffffff';
        ell(ctx, i * u * 0.36, -u * 0.15, u * 0.2, u * 0.24 * blink * lid);
        ctx.fill();
        ctx.fillStyle = '#1a2233';
        ell(ctx, i * u * 0.36 + look, -u * 0.13, u * 0.1, u * 0.14 * blink * lid);
        ctx.fill();
      }
      ctx.fillStyle = hsl(hue + 340, 90, 70, 0.55);
      ell(ctx, i * u * 0.6, u * 0.18, u * 0.12, u * 0.12);
      ctx.fill();
    }
    if (st.glasses) {
      ctx.fillStyle = 'rgba(10,10,20,0.92)';
      ctx.fillRect(-u * 0.62, -u * 0.32, u * 0.55, u * 0.3);
      ctx.fillRect(u * 0.07, -u * 0.32, u * 0.55, u * 0.3);
      ctx.fillRect(-u * 0.1, -u * 0.25, u * 0.2, u * 0.06);
      ctx.fillStyle = hsl(hue, 100, 80, 0.5);
      ctx.fillRect(-u * 0.55, -u * 0.29, u * 0.2, u * 0.06);
      ctx.fillRect(u * 0.14, -u * 0.29, u * 0.2, u * 0.06);
    }
    var open = (st.singing ? 0.14 : 0.06) + 0.3 * Math.min(1, d.level * 1.5 + 0.15 * kick);
    ctx.fillStyle = '#3a1020';
    ell(ctx, 0, u * 0.3, u * 0.22, u * open);
    ctx.fill();
    ctx.fillStyle = hsl(hue + 340, 85, 68);
    ell(ctx, 0, u * (0.3 + open * 0.55), u * 0.13, u * open * 0.4);
    ctx.fill();

    if (st.hat) { drawHat(ctx, st.hat, u, hue, t, kick); }
    if (st.prop) { drawProp(ctx, st.prop, u, hue, phase, t, kick, handsXY); }
    ctx.restore();
  }

  function draw(ctx, w, h, t, dur, d, bpm, hue, track) {
    var s = Math.min(w, h);
    var data = d || {};
    var st = STYLES[pick(track)];
    var audio = {
      bass: data.playing ? (data.bass || 0) : 0.15 + 0.15 * Math.abs(Math.sin(t * 4)),
      mid: data.playing ? (data.mid || 0) : 0.15,
      treble: data.playing ? (data.treble || 0) : 0.15,
      level: data.playing ? (data.level || 0) : 0.2
    };
    var hh = st.hue + ((hue || 0) % 24);
    ctx.save();
    bgGradient(ctx, w, h, hh);
    drawBg(ctx, w, h, t, st.bg, hh, audio.treble, audio.bass);
    drawNotes(ctx, w, h, t, s, hh);
    drawEqualizer(ctx, w, h, t, audio, hh);
    drawCharacter(ctx, w, h, t, audio, bpm, s, st, hh);
    ctx.restore();
  }

  window.CreaMascot = { draw: draw, pick: pick, styles: STYLES, duration: 5 };
})();
