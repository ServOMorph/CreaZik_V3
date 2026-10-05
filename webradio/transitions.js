(function () {
  'use strict';

  var TYPES = ['dissolve', 'blur', 'radial', 'drift', 'veil'];

  function hash(str) {
    var x = 2166136261;
    for (var i = 0; i < str.length; i++) {
      x ^= str.charCodeAt(i);
      x = Math.imul(x, 16777619);
    }
    return x >>> 0;
  }

  function pick(seed) {
    return TYPES[hash(String(seed == null ? '' : seed)) % TYPES.length];
  }

  function smoother(x) {
    if (x <= 0) { return 0; }
    if (x >= 1) { return 1; }
    return x * x * x * (x * (x * 6 - 15) + 10);
  }

  function reduced() {
    try {
      return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) {
      return false;
    }
  }

  function create() {
    var A = null;
    var B = null;
    var C = null;
    var actx = null;
    var bctx = null;
    var cctx = null;
    var pw = 0;
    var ph = 0;
    var cw = 0;
    var ch = 0;
    var fromFn = null;
    var toFn = null;
    var type = 'dissolve';
    var dur = 5000;
    var startMs = -1;

    var eng = { active: false };

    function ensure(wPx, hPx) {
      if (!A) {
        A = document.createElement('canvas');
        B = document.createElement('canvas');
        C = document.createElement('canvas');
        actx = A.getContext('2d');
        bctx = B.getContext('2d');
        cctx = C.getContext('2d');
      }
      if (pw !== wPx || ph !== hPx) {
        A.width = wPx;
        A.height = hPx;
        B.width = wPx;
        B.height = hPx;
        pw = wPx;
        ph = hPx;
      }
      var sw = Math.max(8, Math.round(wPx / 10));
      var sh = Math.max(8, Math.round(hPx / 10));
      if (cw !== sw || ch !== sh) {
        C.width = sw;
        C.height = sh;
        cw = sw;
        ch = sh;
      }
    }

    eng.start = function (fromDraw, toDraw, t, durationMs) {
      fromFn = fromDraw;
      toFn = toDraw;
      type = reduced() ? 'dissolve' : (TYPES.indexOf(t) >= 0 ? t : 'dissolve');
      var d = Number(durationMs);
      if (!isFinite(d)) { d = 5000; }
      dur = Math.max(3000, Math.min(10000, d));
      startMs = -1;
      eng.active = true;
    };

    eng.render = function (ctx, w, h, nowMs) {
      if (!eng.active) { return; }
      if (startMs < 0) { startMs = nowMs; }
      var p = (nowMs - startMs) / dur;
      if (p >= 1) {
        eng.active = false;
        toFn(ctx, w, h);
        return;
      }
      var e = smoother(p);
      var sx = w > 0 && ctx.canvas && ctx.canvas.width ? ctx.canvas.width / w : 1;
      ensure(Math.max(1, Math.round(w * sx)), Math.max(1, Math.round(h * sx)));
      actx.setTransform(sx, 0, 0, sx, 0, 0);
      bctx.setTransform(sx, 0, 0, sx, 0, 0);
      fromFn(actx, w, h);
      toFn(bctx, w, h);

      var cx = w / 2;
      var cy = h / 2;

      if (type === 'dissolve') {
        ctx.globalAlpha = 1;
        ctx.drawImage(A, 0, 0, w, h);
        ctx.globalAlpha = e;
        ctx.drawImage(B, 0, 0, w, h);
        ctx.globalAlpha = 1;
        return;
      }

      if (type === 'blur') {
        ctx.globalAlpha = 1;
        ctx.drawImage(A, 0, 0, w, h);
        ctx.globalAlpha = e;
        ctx.drawImage(B, 0, 0, w, h);
        ctx.globalAlpha = 1;
        cctx.drawImage(ctx.canvas, 0, 0, cw, ch);
        ctx.globalAlpha = 0.6 * Math.sin(Math.PI * e);
        ctx.imageSmoothingEnabled = true;
        if (ctx.imageSmoothingQuality) { ctx.imageSmoothingQuality = 'high'; }
        ctx.drawImage(C, 0, 0, w, h);
        ctx.globalAlpha = 1;
        return;
      }

      if (type === 'radial') {
        var maxR = Math.sqrt(cx * cx + cy * cy);
        var R = Math.max(1, e * maxR * 2.2);
        var g = bctx.createRadialGradient(cx, cy, 0, cx, cy, R);
        g.addColorStop(0, 'rgba(0,0,0,1)');
        g.addColorStop(0.55, 'rgba(0,0,0,1)');
        g.addColorStop(1, 'rgba(0,0,0,0)');
        bctx.save();
        bctx.setTransform(sx, 0, 0, sx, 0, 0);
        bctx.globalCompositeOperation = 'destination-in';
        bctx.fillStyle = g;
        bctx.fillRect(0, 0, w, h);
        bctx.restore();
        ctx.globalAlpha = 1;
        ctx.drawImage(A, 0, 0, w, h);
        ctx.drawImage(B, 0, 0, w, h);
        return;
      }

      if (type === 'drift') {
        var sa = 1 + 0.06 * e;
        var sb = 1 + 0.06 * (1 - e);
        ctx.globalAlpha = 1;
        ctx.drawImage(A, cx - (w * sa) / 2 - e * w * 0.03, cy - (h * sa) / 2, w * sa, h * sa);
        ctx.globalAlpha = e;
        ctx.drawImage(B, cx - (w * sb) / 2 + (1 - e) * w * 0.03, cy - (h * sb) / 2, w * sb, h * sb);
        ctx.globalAlpha = 1;
        return;
      }

      var soft = 0.6;
      var pos = e * (1 + soft) * h;
      var lg = bctx.createLinearGradient(0, pos - soft * h, 0, pos);
      lg.addColorStop(0, 'rgba(0,0,0,1)');
      lg.addColorStop(1, 'rgba(0,0,0,0)');
      bctx.save();
      bctx.setTransform(sx, 0, 0, sx, 0, 0);
      bctx.globalCompositeOperation = 'destination-in';
      bctx.fillStyle = lg;
      bctx.fillRect(0, 0, w, h);
      bctx.restore();
      ctx.globalAlpha = 1;
      ctx.drawImage(A, 0, 0, w, h);
      ctx.drawImage(B, 0, 0, w, h);
    };

    return eng;
  }

  window.CreaTransitions = { types: TYPES.slice(), pick: pick, create: create };
})();
