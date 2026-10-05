(function () {
    'use strict';

    const HOP_FALLBACK = 0.1;
    const NB_FREQ = 64;
    const NB_WAVE = 128;
    const PRELOAD_S = 25;
    const SLEW_PER_S = 4;
    const POLL_MS = 2000;
    const SILENT_WAV = '/silence.wav';

    const $ = id => document.getElementById(id);
    const canvas = $('vizCanvas');
    const ctx2d = canvas.getContext('2d');

    const slots = [$('audio'), new Audio(), new Audio()].map(el => {
        el.preload = 'auto';
        el.setAttribute('playsinline', '');
        return {el, key: null, item: null, gain: 0, seeded: false, usingMp3: true, lastSeek: 0, unlocking: false};
    });

    const supportsVolume = (function () {
        try {
            const a = new Audio();
            a.volume = 0.5;
            return a.volume === 0.5;
        } catch (e) {
            return false;
        }
    }());

    let audioCtx = null;
    const gainNodes = new Map();

    let live = {active: [], upcoming: [], played: [], queue: [], rev: -1};
    let clockOffset = 0;
    let haveClock = false;
    let listening = false;
    let current = null;
    let viz = null;
    let isAdmin = false;
    let viewAsUser = false;
    let comments = [];
    let featuredId = null;
    let votes = {tracks: {}, mine: {}};
    let library = [];
    let libraryLoaded = false;
    let lastTick = performance.now();
    const openPlaylists = new Set();
    const sm = {level: 0, bass: 0, mid: 0, treble: 0};
    const freq = new Uint8Array(NB_FREQ);
    const wave = new Uint8Array(NB_WAVE);
    const data = {freq, wave, level: 0, bass: 0, mid: 0, treble: 0, progress: 0, hue: 200, t: 0, playing: false, playlist: ''};
    let specs = {playlists: {}};
    let content = {jingle_messages: [], ads: []};
    const scenes = {};
    let sceneKey = null;
    let transEngine = null;

    try { viewAsUser = localStorage.getItem('viewAsUser') === '1'; } catch (e) {}

    function effectiveAdmin() {
        return isAdmin && !viewAsUser;
    }

    function esc(v) {
        return String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
    }

    function fmtTime(s) {
        if (!isFinite(s) || s < 0) return '0:00';
        const m = Math.floor(s / 60);
        const r = Math.floor(s % 60);
        return m + ':' + (r < 10 ? '0' : '') + r;
    }

    function fmtClock(sec) {
        const d = new Date(sec * 1000);
        return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    }

    function fmtDate(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        return isNaN(d) ? '' : d.toLocaleDateString('fr-FR', {day: 'numeric', month: 'long', year: 'numeric'});
    }

    async function getJSON(url, fallback) {
        try {
            const r = await fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now());
            if (r.ok) return await r.json();
        } catch (e) {}
        return fallback;
    }

    function serverNow() {
        return Date.now() / 1000 + clockOffset;
    }

    function webSrc(it) {
        return it.file.replace(/\.wav$/i, '.mp3') + '?v=' + encodeURIComponent(it.generated_at || '');
    }

    function wavSrc(it) {
        return it.file + '?v=' + encodeURIComponent(it.generated_at || '');
    }

    function ease(x) {
        return Math.sin(Math.max(0, Math.min(1, x)) * Math.PI / 2);
    }

    function gainAt(it, T) {
        let g = 1;
        if (it.fade_in > 0) g = Math.min(g, ease((T - it.start) / it.fade_in));
        if (it.fade_out > 0) g = Math.min(g, ease((it.end - T) / it.fade_out));
        return g;
    }

    function ensureGraph() {
        if (supportsVolume || audioCtx) return;
        try {
            const AC = window.AudioContext || window.webkitAudioContext;
            if (!AC) return;
            audioCtx = new AC();
            slots.forEach(s => {
                const src = audioCtx.createMediaElementSource(s.el);
                const g = audioCtx.createGain();
                src.connect(g);
                g.connect(audioCtx.destination);
                gainNodes.set(s.el, g);
            });
            if (navigator.audioSession) navigator.audioSession.type = 'playback';
        } catch (e) {
            audioCtx = null;
            gainNodes.clear();
        }
    }

    function setGain(el, g) {
        g = Math.max(0, Math.min(1, g));
        const node = gainNodes.get(el);
        if (node) {
            node.gain.value = g;
            if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
        } else if (supportsVolume) {
            el.volume = g;
        }
    }

    function loadSlot(s, it) {
        s.key = it.key;
        s.item = it;
        s.seeded = false;
        s.usingMp3 = true;
        s.gain = 0;
        setGain(s.el, 0);
        s.el.pause();
        s.el.src = webSrc(it);
        s.el.load();
    }

    function releaseSlot(s) {
        s.key = null;
        s.item = null;
        s.seeded = false;
        s.gain = 0;
        setGain(s.el, 0);
        s.el.pause();
        s.el.removeAttribute('src');
        s.el.load();
    }

    function onSlotError(s) {
        if (!s.key || !s.item || s.unlocking) return;
        if (s.usingMp3) {
            s.usingMp3 = false;
            s.seeded = false;
            s.el.src = wavSrc(s.item);
            s.el.load();
        }
    }

    function playSlot(s) {
        const p = s.el.play();
        if (p && p.catch) {
            p.catch(err => {
                if (err && err.name === 'NotAllowedError') onAutoplayBlocked();
            });
        }
    }

    function onAutoplayBlocked() {
        listening = false;
        setPlayLabel();
        const once = () => {
            document.removeEventListener('pointerdown', once);
            if (!listening) startListening();
        };
        document.addEventListener('pointerdown', once);
    }

    function setPlayLabel() {
        $('playBtn').textContent = listening ? '❚❚' : '▶';
        $('playBtn').setAttribute('aria-pressed', listening ? 'true' : 'false');
    }

    function unlockSlots() {
        slots.forEach(s => {
            if (s.key) return;
            s.unlocking = true;
            s.el.src = SILENT_WAV;
            const p = s.el.play();
            const done = () => {
                s.el.pause();
                s.el.removeAttribute('src');
                s.el.load();
                s.unlocking = false;
            };
            if (p && p.then) p.then(done, done); else done();
        });
    }

    function startListening() {
        ensureGraph();
        unlockSlots();
        listening = true;
        setPlayLabel();
        refreshLive();
    }

    function stopListening() {
        listening = false;
        slots.forEach(s => {
            if (!s.el.paused) s.el.pause();
        });
        setPlayLabel();
    }

    function toggle() {
        if (listening) stopListening(); else startListening();
    }

    async function refreshLive() {
        const t0 = performance.now();
        const sent = Date.now() / 1000;
        let st;
        try {
            const r = await fetch('/api/radio/state?t=' + Date.now());
            if (!r.ok) return;
            st = await r.json();
        } catch (e) {
            return;
        }
        const rtt = (performance.now() - t0) / 1000;
        const estimate = st.server_time - (sent + rtt / 2);
        clockOffset = haveClock ? clockOffset + (estimate - clockOffset) * 0.3 : estimate;
        haveClock = true;
        const changed = st.rev !== live.rev;
        live = st;
        if (changed || effectiveAdmin()) renderProgram();
    }

    function tick() {
        const now = performance.now();
        const dt = Math.min(0.5, (now - lastTick) / 1000);
        lastTick = now;
        if (!haveClock) return;
        const T = serverNow();
        const items = live.active.concat(live.upcoming);
        const audible = items.filter(it => it.start <= T && T < it.end);
        const wanted = audible.map(it => ({it, play: true}));
        items.filter(it => it.start > T && it.start - T < PRELOAD_S).forEach(it => wanted.push({it, play: false}));

        const used = new Set();
        wanted.forEach(w => {
            let s = slots.find(x => x.key === w.it.key && !used.has(x));
            if (!s) s = slots.find(x => !x.key && !x.unlocking && !used.has(x));
            if (!s) {
                s = slots.find(x => !used.has(x) && !x.unlocking && !wanted.some(y => y.it.key === x.key));
                if (s) releaseSlot(s);
            }
            if (!s) return;
            used.add(s);
            if (s.key !== w.it.key) loadSlot(s, w.it);
            s.item = w.it;
            driveSlot(s, w.play, T, dt);
        });
        slots.forEach(s => {
            if (!used.has(s) && s.key && !s.unlocking) releaseSlot(s);
        });
        updateDominant(audible, T);
    }

    function driveSlot(s, play, T, dt) {
        const it = s.item;
        let target = 0;
        if (play && listening) {
            target = gainAt(it, T);
            const desired = T - it.start;
            if (s.el.readyState >= 1) {
                const maxPos = (isFinite(s.el.duration) && s.el.duration > 1 ? s.el.duration : it.duration) - 0.3;
                if (!s.seeded) {
                    try { s.el.currentTime = Math.max(0, Math.min(desired, maxPos)); } catch (e) {}
                    s.seeded = true;
                } else if (Math.abs(s.el.currentTime - desired) > 1.0 && performance.now() - s.lastSeek > 3000) {
                    try { s.el.currentTime = Math.max(0, Math.min(desired, maxPos)); } catch (e) {}
                    s.lastSeek = performance.now();
                }
            }
            if (s.el.paused) playSlot(s);
        } else if (!s.el.paused) {
            s.el.pause();
        }
        const step = SLEW_PER_S * dt;
        s.gain += Math.max(-step, Math.min(step, target - s.gain));
        setGain(s.el, s.gain);
    }

    function updateDominant(audible, T) {
        let best = null;
        audible.forEach(it => {
            if (!best || it.start > best.start) best = it;
        });
        if (best && (!current || current.key !== best.key || current.start !== best.start)) {
            const changed = !current || current.key !== best.key;
            current = best;
            if (changed) showMeta(best);
        } else if (best) {
            current = best;
        }
        updateProgress(T);
    }

    function buildTicker(it) {
        const parts = [];
        if (it.jingle) {
            parts.push('Jingle généré par une IA tournant en local');
        } else {
            if (it.playlist_description) parts.push(it.playlist_description);
            parts.push('Morceau : ' + it.name);
            if (it.prompt) parts.push('Style demandé à l\'IA : ' + it.prompt);
            const date = fmtDate(it.generated_at);
            if (it.model || date) parts.push('Généré' + (date ? ' le ' + date : '') + (it.model ? ' avec ' + it.model : ''));
            parts.push('Création 100 % en local sur un ordinateur personnel');
        }
        parts.push('Contact : sereniatech33@gmail.com');
        parts.push('serenia-tech.fr');
        return parts.join('   |   ');
    }

    function setTicker(text) {
        const el = $('tickerText');
        const box = $('ticker');
        if (!el || !box || el.textContent === text) return;
        el.textContent = text;
        box.style.setProperty('--ticker-duration', Math.max(20, Math.round(text.length * 0.2)) + 's');
        el.style.animation = 'none';
        void el.offsetWidth;
        el.style.animation = '';
    }

    function hueFor(key) {
        let h = 0;
        for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) % 360;
        return h;
    }

    async function loadViz(it) {
        viz = null;
        const d = await getJSON('./' + it.file + '.viz.json', null);
        if (current && current.file === it.file && d && d.d && d.bands) viz = d;
    }

    function showMeta(it) {
        $('nowTitle').textContent = it.jingle ? 'Jingle' : it.name;
        $('nowSub').textContent = it.jingle ? 'CreaZik Radio' : it.playlist_label;
        setTicker(buildTicker(it));
        loadViz(it);
        applyMediaSession();
        updateThumbs();
        renderProgram();
        const area = $('comText');
        if (area) area.placeholder = it.jingle ? 'Ton commentaire sur la radio...' : 'Ton commentaire sur « ' + it.name + ' »...';
        featuredId = null;
        loadComments();
    }

    function applyMediaSession() {
        if (!('mediaSession' in navigator) || !current) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: current.jingle ? 'Jingle' : current.name,
            artist: current.jingle ? 'CreaZik Radio' : current.playlist_label,
            album: 'CreaZik Radio'
        });
        navigator.mediaSession.setActionHandler('play', startListening);
        navigator.mediaSession.setActionHandler('pause', stopListening);
        try {
            navigator.mediaSession.setActionHandler('nexttrack', effectiveAdmin() ? skip : null);
        } catch (e) {}
    }

    function updateProgress(T) {
        const fill = $('progressFill');
        const lab = $('timeLabel');
        if (!current) {
            if (fill) fill.style.width = '0%';
            if (lab) lab.textContent = '0:00 / 0:00';
            return;
        }
        const pos = Math.max(0, Math.min(current.duration, T - current.start));
        if (fill) fill.style.width = (pos / current.duration * 100) + '%';
        if (lab) lab.textContent = fmtTime(pos) + ' / ' + fmtTime(current.duration);
    }

    async function loadVotes() {
        votes = Object.assign({tracks: {}, mine: {}}, await getJSON('/api/votes', {tracks: {}, mine: {}}));
        updateThumbs();
    }

    function updateThumbs() {
        const box = $('thumbs');
        if (!box) return;
        const show = !!current && !current.jingle;
        box.hidden = !show;
        if (!show) return;
        const v = votes.tracks[current.key] || {up: 0, down: 0};
        const mine = votes.mine[current.key] || {up: 0, down: 0};
        const set = (id, text) => {
            const el = $(id);
            if (el) el.textContent = text;
        };
        set('thumbUpCount', v.up || 0);
        set('thumbDownCount', v.down || 0);
        [['thumbUp', 'up'], ['thumbDown', 'down']].forEach(([id, kind]) => {
            const b = $(id);
            if (!b) return;
            const on = (mine[kind] || 0) > 0;
            b.classList.toggle('active', on);
            b.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
    }

    const pendingVotes = {};
    let voteTimer = null;

    function sendVote(kind) {
        if (!current || current.jingle) return;
        const key = current.key;
        const entry = Object.assign({up: 0, down: 0}, votes.tracks[key]);
        entry[kind] += 1;
        votes.tracks[key] = entry;
        const mine = Object.assign({up: 0, down: 0}, votes.mine[key]);
        mine[kind] += 1;
        votes.mine[key] = mine;
        const bucket = pendingVotes[key] || (pendingVotes[key] = {up: 0, down: 0});
        bucket[kind] += 1;
        updateThumbs();
        if (!voteTimer) voteTimer = setTimeout(flushVotes, 400);
    }

    async function flushVotes() {
        voteTimer = null;
        const batch = Object.assign({}, pendingVotes);
        Object.keys(pendingVotes).forEach(k => delete pendingVotes[k]);
        for (const key of Object.keys(batch)) {
            for (const kind of ['up', 'down']) {
                const count = batch[key][kind];
                if (!count) continue;
                try {
                    const r = await fetch('/api/vote', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                        body: JSON.stringify({key, vote: kind, count})});
                    if (r.ok) {
                        const res = await r.json();
                        votes.tracks[key] = {up: res.up, down: res.down, score: res.score};
                        votes.mine[key] = res.mine;
                    }
                } catch (e) {}
            }
        }
        updateThumbs();
    }

    function interpolateBands(t) {
        const bands = viz.bands;
        const hop = viz.hop || HOP_FALLBACK;
        const total = Math.floor(viz.d.length / bands);
        const pos = Math.max(0, Math.min(total - 1, t / hop));
        const i0 = Math.floor(pos);
        const i1 = Math.min(total - 1, i0 + 1);
        const f = pos - i0;
        const row = new Array(bands);
        for (let b = 0; b < bands; b++) {
            row[b] = viz.d[i0 * bands + b] * (1 - f) + viz.d[i1 * bands + b] * f;
        }
        return row;
    }

    function syntheticBands(t) {
        const row = new Array(16);
        for (let b = 0; b < 16; b++) {
            const e = 0.5 + 0.5 * Math.sin(t * (0.9 + b * 0.13) + b * 1.7) * Math.sin(t * 0.37 + b);
            row[b] = 255 * (0.25 + 0.55 * e * (1 - b / 24));
        }
        return row;
    }

    function updateData(now) {
        const playing = listening && !!current;
        const T = serverNow();
        const t = current ? Math.max(0, T - current.start) : 0;
        const dur = current ? current.duration : 0;
        let row = null;
        if (playing) row = viz ? interpolateBands(t) : syntheticBands(t);
        const bands = row ? row.length : 16;
        for (let i = 0; i < NB_FREQ; i++) {
            let target = 0;
            if (row) {
                const p = i / (NB_FREQ - 1) * (bands - 1);
                const b0 = Math.floor(p);
                const b1 = Math.min(bands - 1, b0 + 1);
                target = row[b0] * (1 - (p - b0)) + row[b1] * (p - b0);
            }
            const prev = freq[i];
            freq[i] = target > prev ? prev + (target - prev) * 0.6 : prev + (target - prev) * 0.15;
        }
        let lv = 0, ba = 0, mi = 0, tr = 0;
        for (let i = 0; i < NB_FREQ; i++) {
            lv += freq[i];
            if (i < 6) ba += freq[i]; else if (i < 24) mi += freq[i]; else tr += freq[i];
        }
        sm.level += (lv / NB_FREQ / 255 - sm.level) * 0.3;
        sm.bass += (ba / 6 / 255 - sm.bass) * 0.35;
        sm.mid += (mi / 18 / 255 - sm.mid) * 0.3;
        sm.treble += (tr / 40 / 255 - sm.treble) * 0.3;
        for (let i = 0; i < NB_WAVE; i++) {
            const x = i / NB_WAVE;
            const v = Math.sin(x * 18 + now * 5.5) * 0.55 + Math.sin(x * 41 - now * 8.5) * 0.3 * sm.mid
                + Math.sin(x * 7 + now * 2.1) * 0.4 * sm.bass;
            wave[i] = Math.max(0, Math.min(255, 128 + 127 * v * Math.min(1, sm.level * 2.2)));
        }
        const progress = dur ? Math.min(1, t / dur) : 0;
        data.level = sm.level;
        data.bass = sm.bass;
        data.mid = sm.mid;
        data.treble = sm.treble;
        data.progress = progress;
        data.t = t;
        data.playing = playing;
        data.playlist = current ? current.playlist : '';
        const base = current ? hueFor(current.key || '') : 200;
        data.hue = (base + progress * 140 + sm.level * 50) % 360;
    }

    function resizeCanvas() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        if (!w || !h) return;
        if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
            canvas.width = Math.round(w * dpr);
            canvas.height = Math.round(h * dpr);
        }
        ctx2d.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function getScene(id) {
        if (!scenes[id]) {
            const spec = (specs.playlists || {})[id] || window.CreaScenes.autoSpec(id);
            scenes[id] = window.CreaScenes.create(id, spec);
        }
        return scenes[id];
    }

    function applyTheme(id) {
        const spec = (specs.playlists || {})[id] || (window.CreaScenes ? window.CreaScenes.autoSpec(id) : null);
        if (!spec) return;
        const root = document.documentElement.style;
        root.setProperty('--pl-h1', String(Math.round(spec.hue)));
        root.setProperty('--pl-h2', String(Math.round(spec.hue2)));
    }

    function transitionMs() {
        const s = live.ui && live.ui.visual_transition_s;
        return Math.max(3, Math.min(10, Number(s) || 5)) * 1000;
    }

    function drawOverlay(w, h, T, nowSec) {
        if (!window.CreaMotion || !current || !current.overlay) return;
        const ov = current.overlay;
        if (T < ov.start || T >= ov.end) return;
        const t = T - ov.start;
        const dur = ov.end - ov.start;
        const alpha = window.CreaMotion.envelope(t, dur, 0.8);
        if (alpha <= 0.001) return;
        ctx2d.save();
        ctx2d.globalAlpha = alpha;
        try {
            if (ov.type === 'jingle') {
                const list = content.jingle_messages.length ? content.jingle_messages : [{title: 'CreaZik Radio', lines: []}];
                const msg = list[ov.n % list.length];
                window.CreaMotion.jingle.draw(ctx2d, w, h, t, dur, msg, ov.n % window.CreaMotion.jingle.variants, data);
            } else if (content.ads.length) {
                const designs = window.CreaMotion.ads;
                designs[ov.n % designs.length].draw(ctx2d, w, h, t, dur, content.ads[ov.n % content.ads.length], data);
            }
        } finally {
            ctx2d.restore();
        }
    }

    function drawVisual(w, h, now) {
        if (!window.CreaScenes) {
            if (window.CreaVisuals) window.CreaVisuals.draw(1, ctx2d, w, h, data);
            return;
        }
        const nowSec = now / 1000;
        const wanted = current ? (current.jingle ? (sceneKey || 'jingles') : current.playlist) : (sceneKey || 'jingles');
        if (!transEngine && window.CreaTransitions) transEngine = window.CreaTransitions.create();
        if (sceneKey === null) {
            sceneKey = wanted;
            applyTheme(wanted);
        } else if (wanted !== sceneKey) {
            const from = sceneKey;
            sceneKey = wanted;
            applyTheme(wanted);
            if (transEngine) {
                const type = window.CreaTransitions.pick(from + '>' + wanted);
                transEngine.start((c, ww, hh) => getScene(from).draw(c, ww, hh, data, nowSec),
                                  (c, ww, hh) => getScene(wanted).draw(c, ww, hh, data, nowSec), type, transitionMs());
            }
        }
        if (transEngine && transEngine.active) {
            transEngine.render(ctx2d, w, h, now);
        } else {
            getScene(sceneKey).draw(ctx2d, w, h, data, nowSec);
        }
        drawOverlay(w, h, serverNow(), nowSec);
    }

    function frame(now) {
        requestAnimationFrame(frame);
        if (document.hidden) return;
        resizeCanvas();
        updateData(now / 1000);
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        if (w && h) drawVisual(w, h, now);
    }

    function rowHtml(it, src, extra) {
        const isJ = !!it.jingle;
        const sub = (isJ ? 'Jingle' : it.playlist_label) + (it.duration ? ' - ' + fmtTime(it.duration) : '');
        const badge = extra.explicit ? '<span class="prog-badge">Choisi</span>'
            : (extra.auto && isJ ? '<span class="prog-badge">Jingle auto</span>' : '');
        const attrs = `data-src="${src}" data-key="${esc(it.key)}"` + (extra.qi !== undefined ? ` data-qi="${extra.qi}"` : '');
        const removable = src === 'queue' && !(extra.auto && isJ);
        return `<div class="prog-item${isJ ? ' is-jingle' : ''}${extra.explicit ? ' is-explicit' : ''}${extra.cls || ''}" ${attrs}>
            <button type="button" class="prog-main" data-act="next" ${attrs}>
                <span class="prog-title">${esc(it.name)}</span>
                <span class="prog-sub">${esc(sub)}${extra.time ? ' - ' + esc(extra.time) : ''}</span>
                ${badge}
            </button>
            <button type="button" class="prog-act" data-act="now" ${attrs} aria-label="Lire maintenant" title="Lire maintenant">&#9654;</button>
            ${removable ? `<button type="button" class="prog-act" data-act="remove" ${attrs} aria-label="Retirer de la file" title="Retirer de la file">&times;</button>` : ''}
        </div>`;
    }

    function renderProgram() {
        const panel = $('progPanel');
        if (!panel || panel.hidden || !effectiveAdmin()) return;
        const setHtml = (id, html) => {
            const el = $(id);
            if (el) el.innerHTML = html;
        };
        const empty = txt => `<div class="prog-empty">${txt}</div>`;
        const played = (live.played || []).slice(-8);
        setHtml('progPlayed', played.length
            ? played.map(p => rowHtml(p, 'played', {time: fmtClock(p.start), cls: ' is-played'})).join('')
            : empty('Rien de joué avant ce morceau.'));
        setHtml('progNow', current
            ? `<div class="prog-item is-now${current.jingle ? ' is-jingle' : ''}"><div class="prog-main">
                   <span class="prog-title">${esc(current.jingle ? 'Jingle - ' + current.name : current.name)}</span>
                   <span class="prog-sub">${esc(current.jingle ? 'CreaZik Radio' : current.playlist_label)}</span>
                   <span class="prog-badge">En direct</span></div></div>`
            : empty('Aucun morceau en cours.'));
        const queue = live.queue || [];
        const upcoming = live.upcoming || [];
        const n = Math.min(queue.length, upcoming.length);
        const rows = [];
        for (let i = 0; i < n; i++) {
            rows.push(rowHtml(upcoming[i], 'queue', {qi: queue[i].index, explicit: queue[i].explicit, auto: queue[i].auto}));
        }
        setHtml('progQueue', rows.length ? rows.join('') : empty('File vide : aucun morceau disponible.'));
        setHtml('progLibrary', library.length ? library.map(pl => {
            const open = openPlaylists.has(pl.id);
            const b = esc(pl.id);
            return `<div class="prog-playlist${open ? ' open' : ''}" data-playlist="${b}">
                <div class="prog-pl-head">
                    <button type="button" class="prog-expand" data-act="toggle" data-playlist="${b}" aria-expanded="${open}">
                        <span class="prog-pl-name">${esc(pl.label)}</span>
                        <span class="prog-pl-count">${pl.tracks.length}</span>
                    </button>
                    <button type="button" class="prog-pl-act" data-act="pl-next" data-playlist="${b}">Ensuite</button>
                    <button type="button" class="prog-pl-act" data-act="pl-now" data-playlist="${b}">Lire</button>
                </div>
                <div class="prog-pl-tracks">${open ? pl.tracks.map(t => rowHtml(t, 'library', {})).join('') : ''}</div>
            </div>`;
        }).join('') : empty('Aucune playlist disponible.'));
    }

    async function loadLibrary() {
        const list = await getJSON('/api/radio/library', []);
        library = list.map(pl => ({
            id: pl.id, label: pl.label,
            tracks: pl.tracks.map(t => ({key: t.key, name: t.name, playlist_label: pl.label, duration: t.duration, jingle: pl.jingle}))
        }));
        libraryLoaded = true;
        renderProgram();
    }

    async function radioAction(body) {
        try {
            const r = await fetch('/api/radio/action', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                        body: JSON.stringify(body)});
            const st = await r.json().catch(() => null);
            if (st && st.active) {
                const T = Date.now() / 1000;
                clockOffset = st.server_time - T;
                live = st;
                renderProgram();
            }
        } catch (e) {}
    }

    function skip() {
        radioAction({action: 'skip'});
    }

    function onProgramClick(ev) {
        const btn = ev.target.closest('[data-act]');
        if (!btn || !effectiveAdmin()) return;
        const act = btn.dataset.act;
        const src = btn.dataset.src;
        const key = btn.dataset.key;
        const playlistId = btn.dataset.playlist;
        if (act === 'toggle') {
            if (openPlaylists.has(playlistId)) openPlaylists.delete(playlistId); else openPlaylists.add(playlistId);
            renderProgram();
            return;
        }
        if (act === 'pl-next') { radioAction({action: 'playlist_next', id: playlistId}); return; }
        if (act === 'pl-now') { radioAction({action: 'playlist_now', id: playlistId}); return; }
        if (src === 'queue') {
            const index = parseInt(btn.dataset.qi, 10);
            if (act === 'remove') radioAction({action: 'remove', index});
            else if (act === 'next') radioAction({action: 'move_front', index});
            else if (act === 'now') radioAction({action: 'play_index', index});
            return;
        }
        if (act === 'now') radioAction({action: 'now', key});
        else radioAction({action: 'next', key});
    }

    function initFolds() {
        let saved = {};
        try { saved = JSON.parse(localStorage.getItem('folds') || '{}'); } catch (e) {}
        document.querySelectorAll('details[data-fold]').forEach(d => {
            const k = d.dataset.fold;
            if (k in saved) d.open = !!saved[k];
            d.addEventListener('toggle', () => {
                saved[k] = d.open;
                try { localStorage.setItem('folds', JSON.stringify(saved)); } catch (e) {}
            });
        });
    }

    function applyMode() {
        const adm = effectiveAdmin();
        const setHidden = (id, hidden) => {
            const el = $(id);
            if (el) el.hidden = hidden;
        };
        setHidden('nextBtn', !adm);
        setHidden('adminBar', !adm);
        setHidden('progPanel', !adm);
        setHidden('viewAsBanner', !(isAdmin && viewAsUser));
        const icon = $('modeIcon');
        if (icon) {
            const mode = !isAdmin ? 'login' : (viewAsUser ? 'user' : 'admin');
            const label = {login: 'Connexion admin', admin: 'Voir comme auditeur', user: 'Revenir en mode admin'}[mode];
            icon.dataset.mode = mode;
            icon.setAttribute('aria-label', label);
            icon.title = label;
        }
        applyMediaSession();
        if (adm && !libraryLoaded) loadLibrary();
        renderProgram();
    }

    function setViewAsUser(v) {
        viewAsUser = v;
        try { localStorage.setItem('viewAsUser', v ? '1' : '0'); } catch (e) {}
        applyMode();
    }

    function onModeIcon() {
        if (!isAdmin) {
            try { sessionStorage.setItem('autoplayAdmin', '1'); } catch (e) {}
            location.href = '/login?next=/listen.html';
            return;
        }
        setViewAsUser(!viewAsUser);
        if (!viewAsUser && !listening) startListening();
    }

    function autoplayAfterLogin() {
        let flag = null;
        try {
            flag = sessionStorage.getItem('autoplayAdmin');
            sessionStorage.removeItem('autoplayAdmin');
        } catch (e) {}
        if (!flag || !isAdmin || viewAsUser) return;
        listening = true;
        setPlayLabel();
        onAutoplayBlockedCheck();
    }

    function onAutoplayBlockedCheck() {
        const probe = slots[0].el;
        const prevSrc = probe.getAttribute('src');
        if (prevSrc) return;
        const p = probe.play ? probe.play() : null;
        if (p && p.catch) p.catch(err => {
            if (err && err.name === 'NotAllowedError') onAutoplayBlocked();
        });
    }

    function showFeatured() {
        const text = $('featuredComment');
        const author = $('featuredAuthor');
        if (!text) return;
        if (!comments.length) {
            text.textContent = current && !current.jingle ? 'Aucun commentaire sur ce morceau pour le moment : sois le premier !' : 'Sois le premier à laisser un commentaire.';
            if (author) author.textContent = '';
            return;
        }
        let cands = comments.filter(c => c.id !== featuredId);
        if (!cands.length) cands = comments;
        const c = cands[Math.floor(Math.random() * cands.length)];
        featuredId = c.id;
        text.textContent = c.text;
        if (author) author.textContent = c.name;
    }

    function rotateFeatured() {
        const text = $('featuredComment');
        if (!text) return;
        const author = $('featuredAuthor');
        text.classList.add('fade-out');
        if (author) author.classList.add('fade-out');
        setTimeout(() => {
            showFeatured();
            text.classList.remove('fade-out');
            if (author) author.classList.remove('fade-out');
        }, 350);
    }

    let commentsKey = '';

    async function loadComments() {
        const key = current && !current.jingle ? current.key : '';
        commentsKey = key;
        const list = await getJSON('/api/comments' + (key ? '?key=' + encodeURIComponent(key) : ''), []);
        if (commentsKey !== key) return;
        comments = list;
        if (!featuredId || !comments.some(c => c.id === featuredId)) {
            featuredId = null;
            showFeatured();
        }
    }

    async function postComment(ev) {
        ev.preventDefault();
        const hint = $('comHint');
        const name = $('comName').value;
        const text = $('comText').value;
        hint.textContent = '';
        hint.classList.remove('error', 'ok');
        const track = current ? ((current.jingle ? 'Jingle' : current.name) + ' - ' + $('nowSub').textContent) : '';
        try {
            const r = await fetch('/api/comments', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                    body: JSON.stringify({name, text, track, key: current && !current.jingle ? current.key : ''})});
            if (r.ok) {
                $('comText').value = '';
                try { localStorage.setItem('comName', name); } catch (e) {}
                hint.classList.add('ok');
                hint.textContent = 'Merci pour ton commentaire !';
                loadComments();
            } else {
                const err = await r.json().catch(() => ({}));
                hint.classList.add('error');
                hint.textContent = err.error || 'Échec de l\'envoi';
            }
        } catch (e) {
            hint.classList.add('error');
            hint.textContent = 'Échec de l\'envoi';
        }
    }

    async function init() {
        const me = await getJSON('/api/me', {admin: false});
        isAdmin = !!me.admin;
        $('playBtn').addEventListener('click', toggle);
        $('nextBtn').addEventListener('click', skip);
        const mi = $('modeIcon');
        if (mi) mi.addEventListener('click', onModeIcon);
        const panel = $('progPanel');
        if (panel) panel.addEventListener('click', onProgramClick);
        const tu = $('thumbUp');
        const td = $('thumbDown');
        if (tu) tu.addEventListener('click', () => sendVote('up'));
        if (td) td.addEventListener('click', () => sendVote('down'));
        slots.forEach(s => s.el.addEventListener('error', () => onSlotError(s)));
        $('comForm').addEventListener('submit', postComment);
        specs = await getJSON('./scenes_spec.json', {playlists: {}});
        content = Object.assign({jingle_messages: [], ads: []}, await getJSON('./radio_content.json', {}));
        try { $('comName').value = localStorage.getItem('comName') || ''; } catch (e) {}
        initFolds();
        applyMode();
        setPlayLabel();
        setTicker('CreaZik Radio : musiques générées par intelligence artificielle, en local   |   Contact : sereniatech33@gmail.com   |   serenia-tech.fr');
        await refreshLive();
        await Promise.all([loadComments(), loadVotes()]);
        setInterval(rotateFeatured, 5000);
        setInterval(loadComments, 30000);
        setInterval(loadVotes, 30000);
        setInterval(refreshLive, POLL_MS);
        setInterval(tick, 100);
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) refreshLive();
        });
        requestAnimationFrame(frame);
        autoplayAfterLogin();
    }

    window.__radioDebug = () => ({current, T: serverNow(), live: {active: live.active, upcoming: live.upcoming.length}, content, sceneKey, listening, transActive: !!(transEngine && transEngine.active)});
    window.addEventListener('load', init);
}());
