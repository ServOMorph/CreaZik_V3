(function () {
    'use strict';

    const HOP_FALLBACK = 0.1;
    const NB_FREQ = 64;
    const NB_WAVE = 128;
    const PRELOAD_S = 25;
    const SLEW_PER_S = 4;
    const POLL_MS = 2000;
    const SILENT_WAV = '/silence.wav';
    const USER_HEADERS = Object.freeze({'X-Creazik-Ui': 'user'});
    let UI_HEADERS = USER_HEADERS;
    let adminSession = false;
    const pluginDefs = {};
    const hooks = {live: [], track: [], listen: []};
    let session = null;
    let profile = null;

    function emit(name, ...args) {
        hooks[name].forEach(fn => {
            try { fn(...args); } catch (e) {}
        });
    }

    window.CreaZik = Object.freeze({
        registerPlugin(def) {
            if (def && typeof def.id === 'string' && typeof def.init === 'function' && !pluginDefs[def.id]) pluginDefs[def.id] = def;
        }
    });

    const $ = id => document.getElementById(id);
    const canvas = $('vizCanvas');
    const ctx2d = canvas.getContext('2d');
    const trackCover = $('trackCover');
    const coverLabel = $('coverLabel');
    const coverTitle = $('coverTitle');
    const coverDate = $('coverDate');

    const slots = [$('audio'), new Audio(), new Audio()].map(el => {
        el.preload = 'auto';
        el.setAttribute('playsinline', '');
        return {el, key: null, item: null, gain: 0, seeded: false, usingMp3: true, lastSeek: 0, unlocking: false};
    });

    const supportsVolume = (function () {
        const ios = /iPad|iPhone|iPod/.test(navigator.userAgent)
            || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        if (ios) return false;
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
    const notifyAudio = new Audio();
    notifyAudio.preload = 'auto';
    notifyAudio.setAttribute('playsinline', '');
    const NOTIFY_DUCK = 0.25;
    const NOTIFY_RISE_MS = 1500;
    let notifyBusy = false;
    let notifyEndAt = -1e9;
    let notifyFinish = null;

    let live = {active: [], upcoming: [], played: [], queue: [], rev: -1};
    let clockOffset = 0;
    let haveClock = false;
    let listening = false;
    let current = null;
    let viz = null;
    let comments = [];
    let featuredId = null;
    let votes = {tracks: {}, mine: {}};
    let lastTick = performance.now();
    const sm = {level: 0, bass: 0, mid: 0, treble: 0};
    const freq = new Uint8Array(NB_FREQ);
    const wave = new Uint8Array(NB_WAVE);
    const data = {freq, wave, level: 0, bass: 0, mid: 0, treble: 0, progress: 0, hue: 200, t: 0, playing: false, playlist: ''};
    let specs = {playlists: {}};
    let content = {jingle_messages: [], ads: []};
    const scenes = {};
    let sceneKey = null;
    let transEngine = null;

    function esc(v) {
        return String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
    }

    function trackTitle(it) {
        return String(it && it.name || '').replace(/^\d+\s*-\s*/, '');
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
            const r = await fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), {headers: UI_HEADERS});
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

    const JINGLE_GAIN = 0.8;

    function ease(x) {
        return Math.sin(Math.max(0, Math.min(1, x)) * Math.PI / 2);
    }

    function gainAt(it, T) {
        let g = 1;
        if (it.fade_in > 0) g = Math.min(g, ease((T - it.start) / it.fade_in));
        if (it.fade_out > 0) g = Math.min(g, ease((it.end - T) / it.fade_out));
        if (it.duck) {
            const d = it.duck;
            if (T < d.until) g = Math.min(g, d.level * ease((T - it.start) / Math.max(0.5, d.until - it.start)));
            else g = Math.min(g, d.level + (1 - d.level) * ease((T - d.until) / Math.max(0.5, d.rise)));
        }
        if (it.jingle) g *= jingleGain();
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
            const ns = audioCtx.createMediaElementSource(notifyAudio);
            const ng = audioCtx.createGain();
            ns.connect(ng);
            ng.connect(audioCtx.destination);
            gainNodes.set(notifyAudio, ng);
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

    function duckFactor() {
        if (notifyBusy) return NOTIFY_DUCK;
        const x = (performance.now() - notifyEndAt) / NOTIFY_RISE_MS;
        return x >= 1 ? 1 : NOTIFY_DUCK + (1 - NOTIFY_DUCK) * ease(x);
    }

    function unlockNotify() {
        if (notifyBusy) return;
        notifyAudio.src = SILENT_WAV;
        const p = notifyAudio.play();
        const done = () => { if (!notifyBusy) notifyAudio.pause(); };
        if (p && p.then) p.then(done, done); else done();
    }

    function playNotify(src, after) {
        let finished = false;
        let timer = null;
        const end = () => {
            if (finished) return;
            finished = true;
            clearTimeout(timer);
            notifyFinish = null;
            notifyBusy = false;
            notifyEndAt = performance.now();
            notifyAudio.onended = notifyAudio.onerror = null;
            after();
        };
        notifyBusy = true;
        notifyFinish = end;
        notifyAudio.onended = end;
        notifyAudio.onerror = end;
        notifyAudio.src = src;
        setGain(notifyAudio, jingleGain());
        const p = notifyAudio.play();
        if (p && p.catch) p.catch(end);
        timer = setTimeout(end, 10000);
    }

    function startListening() {
        syncPersonalClock(serverNow());
        ensureGraph();
        unlockSlots();
        unlockNotify();
        listening = true;
        setPlayLabel();
        refreshLive();
        emit('listen');
    }

    function stopListening() {
        syncPersonalClock(serverNow());
        listening = false;
        slots.forEach(s => {
            if (!s.el.paused) s.el.pause();
        });
        notifyAudio.pause();
        notifyAudio.onended = notifyAudio.onerror = null;
        notifyAudio.removeAttribute('src');
        notifyAudio.load();
        if (notifyFinish) notifyFinish();
        notifyBusy = false;
        notifyEndAt = -1e9;
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
        emit('live', changed);
    }

    function tick() {
        const now = performance.now();
        const dt = Math.min(0.5, (now - lastTick) / 1000);
        lastTick = now;
        if (!haveClock) return;
        const T = serverNow();
        syncPersonalClock(T);
        if (personal && listening) {
            const ps = slots.find(x => x.key === personal.item.key && x.seeded);
            if (T >= personal.item.end || (ps && ps.el.ended)) {
                if (personal.pending != null) playPersonal(personal.pending); else advancePersonal();
            }
        }
        const items = personal ? [personal.item] : liveItems();
        const audible = items.filter(it => it.start <= T && T < it.end);
        const wanted = audible.map(it => ({it, play: true}));
        items.filter(it => it.start > T && it.start - T < PRELOAD_S).forEach(it => wanted.push({it, play: false}));
        if (personal) {
            const nx = personal.list[personal.pending != null ? personal.pending : personal.idx + 1];
            if (nx && nx.key !== personal.item.key) wanted.push({it: nx, play: false});
        }

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

    let personal = null;

    function jingleFilterOn() {
        return !!profile && Array.isArray(profile.jingle_categories);
    }

    function jingleAllowed(it) {
        if (!it || !it.jingle || !jingleFilterOn()) return true;
        return it.category === 'annonces' || it.urgent_at != null || profile.jingle_categories.includes(it.category);
    }

    const duckDrop = new Map();
    const liveView = new WeakMap();

    function liveItems() {
        const all = live.active.concat(live.upcoming);
        if (!jingleFilterOn()) return all;
        return all.filter(jingleAllowed).map(it => {
            if (it.jingle || !it.duck) return it;
            let view = liveView.get(it);
            if (view) return view;
            const id = it.key + '@' + it.start;
            let drop = duckDrop.get(id);
            if (drop === undefined) {
                const jg = all.find(x => x.jingle && Math.abs(x.end - it.duck.until) < 0.05);
                if (jg) {
                    drop = !jingleAllowed(jg);
                    duckDrop.set(id, drop);
                    if (duckDrop.size > 50) duckDrop.delete(duckDrop.keys().next().value);
                }
            }
            view = drop ? Object.assign({}, it, {duck: null}) : it;
            liveView.set(it, view);
            return view;
        });
    }

    function syncPersonalClock(T) {
        if (!personal || !personal.item) return;
        if (!listening) {
            const elapsed = T - personal.clock;
            personal.item.start += elapsed;
            personal.item.end += elapsed;
        }
        personal.clock = T;
    }

    function liveSong(T) {
        let best = null;
        live.active.forEach(it => {
            if (!it.jingle && it.start <= T && (!best || it.start > best.start)) best = it;
        });
        return best;
    }

    function navList(T) {
        const nav = live.nav || {played: [], next: []};
        const list = [];
        const seen = new Set();
        const id = it => it.uid != null ? 'u' + it.uid : it.key + '@' + it.start;
        const push = it => {
            if (!it || it.jingle || seen.has(id(it))) return;
            seen.add(id(it));
            list.push(it);
        };
        (nav.played || []).forEach(push);
        const before = list.length;
        const cur = liveSong(T);
        push(cur);
        (nav.next || []).forEach(push);
        const idx = cur ? list.findIndex(x => id(x) === id(cur)) : before - 0.5;
        return {list, idx};
    }

    function resetSlots() {
        slots.forEach(s => {
            if (s.key && !s.unlocking) releaseSlot(s);
        });
    }

    function prepareSlots(key) {
        slots.forEach(s => {
            if (s.unlocking || !s.key) return;
            if (s.key === key) {
                s.seeded = false;
                s.lastSeek = 0;
                try { s.el.currentTime = 0; } catch (e) {}
            } else {
                releaseSlot(s);
            }
        });
        current = null;
        updateNavUi();
    }

    function playPersonal(i) {
        const src = personal.list[i];
        const T = serverNow();
        personal.idx = i;
        personal.pending = null;
        personal.sinceJingle = (personal.sinceJingle || 0) + 1;
        personal.item = Object.assign({}, src, {
            start: T, end: T + src.duration, fade_in: 0, fade_out: 1.5, duck: null, overlay: null, explicit: false
        });
        personal.clock = T;
        prepareSlots(src.key);
    }

    const URGENT_STORE = 'urgentHeard';
    const urgentHeard = new Set();
    let lastHeardAnnouncement = null;
    try { JSON.parse(localStorage.getItem(URGENT_STORE) || '[]').forEach(x => urgentHeard.add(x)); } catch (e) {}

    function urgentId(u) {
        return u.key + '@' + u.urgent_at;
    }

    function markUrgentHeard(item) {
        const occurrence = item.urgent_at != null ? item : ((live.nav && live.nav.urgent) || [])
            .filter(u => u.key === item.key && !urgentHeard.has(urgentId(u)))
            .sort((a, b) => a.urgent_at - b.urgent_at)[0];
        if (!occurrence) return;
        urgentHeard.add(urgentId(occurrence));
        try { localStorage.setItem(URGENT_STORE, JSON.stringify([...urgentHeard].slice(-50))); } catch (e) {}
    }

    function nextUrgent() {
        return ((live.nav && live.nav.urgent) || []).find(u => !urgentHeard.has(urgentId(u))) || null;
    }

    function playJingleThen(i, jg) {
        const T = serverNow();
        if (jg.follow && jg.follow.key && jg.follow.duration) {
            i = Math.min(Math.max(0, i), personal.list.length);
            personal.list.splice(i, 0, Object.assign({}, jg.follow, {uid: 'u' + jg.urgent_at + '-' + i}));
        }
        personal.pending = i;
        personal.sinceJingle = 0;
        personal.item = Object.assign({}, jg, {
            start: T, end: T + jg.duration, fade_in: 0, fade_out: 0, duck: null, overlay: null, explicit: false, jingle: true,
            urgent: !!jg.urgent_at
        });
        personal.clock = T;
        if (jg.urgent_at != null) markUrgentHeard(jg);
        prepareSlots(jg.key);
    }

    function goTo(i, regular) {
        const urgent = nextUrgent();
        if (urgent) {
            playJingleThen(i, urgent);
            return;
        }
        const every = Number((live.ui || {}).jingle_every) || 0;
        const js = ((live.nav && live.nav.jingles) || []).filter(jingleAllowed);
        if (regular !== false && every > 0 && js.length && (personal.sinceJingle || 0) >= every) {
            playJingleThen(i, js[(personal.jseq || 0) % js.length]);
            personal.jseq = (personal.jseq || 0) + 1;
        } else {
            playPersonal(i);
        }
    }

    function advancePersonal() {
        if (personal.idx + 1 >= personal.list.length) {
            const keys = new Set(personal.list.slice(-PLAYED_KEEP).map(x => x.key));
            let more;
            if (personal.refill) {
                more = (personal.refill() || []).filter(t => t && t.key && !keys.has(t.key));
            } else {
                more = ((live.nav && live.nav.next) || []).filter(t => !keys.has(t.key));
            }
            if (!more.length) {
                goLive();
                return;
            }
            const base = personal.list.length;
            more.forEach((t, j) => personal.list.push(Object.assign({}, t, {uid: 'p' + (base + j)})));
        }
        goTo(personal.idx + 1);
    }

    function goLive() {
        personal = null;
        resetSlots();
        current = null;
        updateNavUi();
    }

    const NAV_COOLDOWN_MS = 600;
    const PLAYED_KEEP = 4;
    let navLockUntil = 0;

    function lockNavButtons() {
        navLockUntil = performance.now() + NAV_COOLDOWN_MS;
        ['userPrevBtn', 'userNextBtn'].forEach(id => {
            const b = $(id);
            if (b) b.disabled = true;
        });
        setTimeout(() => {
            ['userPrevBtn', 'userNextBtn'].forEach(id => {
                const b = $(id);
                if (b) b.disabled = false;
            });
        }, NAV_COOLDOWN_MS);
    }

    function navigate(dir) {
        if (!haveClock || performance.now() < navLockUntil) return;
        if (personal && personal.item && personal.item.urgent) return;
        lockNavButtons();
        if (!personal) {
            const nav = navList(serverNow());
            if (!nav.list.length) return;
            personal = {list: nav.list, idx: nav.idx, item: null, sinceJingle: 1};
        }
        if (personal.pending != null) {
            playPersonal(dir > 0 ? personal.pending : Math.max(0, personal.pending - 1));
        } else {
            const target = Math.round(personal.idx + dir * (Number.isInteger(personal.idx) ? 1 : 0.5));
            if (target >= personal.list.length) {
                personal.idx = personal.list.length - 1;
                advancePersonal();
            } else if (dir > 0) {
                goTo(target);
            } else {
                goTo(Math.max(0, target), false);
            }
        }
        if (!listening) startListening();
    }

    function updateNavUi() {
        const lb = $('userLiveBtn');
        if (lb) lb.hidden = !personal;
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
            if (s.el.paused && !s.el.ended) playSlot(s);
        } else if (!s.el.paused) {
            s.el.pause();
        }
        const step = SLEW_PER_S * dt;
        s.gain += Math.max(-step, Math.min(step, target - s.gain));
        setGain(s.el, s.gain * duckFactor());
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
        if (best && best.category === 'annonces' && listening) {
            const slot = slots.find(s => s.item === best && s.seeded && !s.el.paused && !s.el.ended && s.el.readyState >= 2);
            const occurrence = best.key + '@' + best.start + '@' + best.urgent_at;
            if (slot && occurrence !== lastHeardAnnouncement) {
                markUrgentHeard(best);
                lastHeardAnnouncement = occurrence;
            }
        }
        updateProgress(T);
    }

    function buildTicker(it) {
        const parts = [];
        if (it.jingle) {
            parts.push('Jingle généré par une IA tournant en local');
        } else {
            if (it.playlist_description) parts.push(it.playlist_description);
            parts.push('Morceau : ' + trackTitle(it));
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
        userImageOnTrack(it);
        showTrackCover(it);
        $('nowTitle').textContent = it.jingle ? 'Jingle' : trackTitle(it);
        $('nowSub').textContent = it.jingle ? 'CréaZik IA WebRadio' : plName(it.playlist_label);
        setTicker(buildTicker(it));
        loadViz(it);
        applyMediaSession();
        updateThumbs();
        emit('track', Object.assign({}, it));
        const area = $('comText');
        if (area) area.placeholder = it.jingle ? 'Ton commentaire sur la radio...' : 'Ton commentaire sur « ' + trackTitle(it) + ' »...';
        featuredId = null;
        loadComments();
    }

    function setCaption(it, show) {
        const box = $('vizCaption');
        if (!box) return;
        const on = it && !it.jingle;
        box.hidden = !on;
        if (on) startCaptionTyping(trackTitle(it), plName(it.playlist_label));
        else stopCaptionTyping();
    }

    let capTimer = null;
    let capKey = '';

    function stopCaptionTyping() {
        clearTimeout(capTimer);
        capTimer = null;
        capKey = '';
    }

    function startCaptionTyping(title, desc) {
        const key = title + ' ' + desc;
        if (key === capKey && capTimer) return;
        stopCaptionTyping();
        capKey = key;
        const els = [$('capTitle'), $('capStyle')];
        els[0].textContent = title;
        els[1].textContent = desc;
        let idx = 0;
        const render = (prev) => els.forEach((e, i) => {
            e.classList.toggle('cap-active', i === idx);
            e.classList.toggle('cap-out', i === prev);
        });
        render(-1);
        const tick = () => {
            const prev = idx;
            idx = 1 - idx;
            render(prev);
            capTimer = setTimeout(tick, 3500);
        };
        capTimer = setTimeout(tick, 3500);
    }

    let coverFitKey = '';

    function coverBox(w, h) {
        const areaTop = h * 0.05;
        const areaH = h * 0.9;
        const ratio = trackCover.naturalWidth && trackCover.naturalHeight ? trackCover.naturalWidth / trackCover.naturalHeight : 1;
        let cw = w;
        let ch = w / ratio;
        if (ch > areaH) {
            ch = areaH;
            cw = ch * ratio;
        }
        return {left: (w - cw) / 2, top: areaTop + (areaH - ch) / 2, width: cw, height: ch};
    }

    function fitCoverTitle(force) {
        const wrap = coverLabel.parentElement;
        const w = wrap.clientWidth;
        const h = wrap.clientHeight;
        const key = (coverTitle.dataset.full || coverTitle.textContent) + '|' + w + '|' + h + '|' + trackCover.naturalWidth + 'x' + trackCover.naturalHeight;
        if (!force && key === coverFitKey) return;
        coverFitKey = key;
        if (!coverTitle.textContent || !w || !h) return;
        const box = coverBox(w, h);
        const s = coverLabel.style;
        s.left = box.left + 'px';
        s.top = box.top + 'px';
        s.width = box.width + 'px';
        s.height = box.height + 'px';
        coverDate.style.fontSize = Math.max(8, Math.min(11, box.width * 0.06)) + 'px';
        const maxTitle = box.height * 0.45;
        const full = coverTitle.dataset.full || coverTitle.textContent;
        const base = Math.min(21.6, box.width * 0.13);
        const layout = (parts, nowrap) => {
            const nodes = [];
            parts.forEach((p, i) => {
                if (i) nodes.push(document.createElement('br'));
                nodes.push(document.createTextNode(p));
            });
            coverTitle.replaceChildren(...nodes);
            coverTitle.style.whiteSpace = nowrap ? 'nowrap' : 'normal';
        };
        const fits = () => coverTitle.scrollWidth <= coverTitle.clientWidth + 0.5
            && coverTitle.offsetHeight <= maxTitle;
        const shrink = (min) => {
            for (let size = base; size >= min; size -= 0.5) {
                coverTitle.style.fontSize = size + 'px';
                if (fits()) return true;
            }
            return false;
        };
        layout([full], true);
        if (shrink(9)) return;
        const dash = full.indexOf(' - ');
        if (dash > 0) {
            layout([full.slice(0, dash), full.slice(dash + 3)], true);
            if (shrink(9)) return;
        }
        layout([full], false);
        coverTitle.style.overflowWrap = '';
        if (shrink(7)) return;
        coverTitle.style.overflowWrap = 'anywhere';
        if (!shrink(7)) coverTitle.style.fontSize = '7px';
    }

    function showTrackCover(it) {
        coverOk = false;
        trackCover.hidden = true;
        trackCover.removeAttribute('src');
        coverTitle.textContent = it && !it.jingle ? trackTitle(it) : '';
        coverTitle.dataset.full = coverTitle.textContent;
        coverDate.textContent = it && !it.jingle ? fmtDate(it.generated_at) : '';
        fitCoverTitle();
        if (it && !it.jingle) phaseT0 = null;
        setCaption(it, true);
        if (!it || it.jingle || !it.file) return;
        const match = it.file.match(/^(playlists\/[\w-]+\/outputs\/.+)\.(?:wav|mp3|flac|ogg)$/i);
        if (!match) return;
        trackCover.onload = () => {
            if (current === it) {
                coverOk = true;
                trackCover.hidden = false;
                setCaption(it, false);
                fitCoverTitle(true);
            }
        };
        trackCover.onerror = () => { coverOk = false; setCaption(it, true); };
        trackCover.src = './' + match[1] + '.cover.png?v=' + encodeURIComponent(it.generated_at || '');
    }

    function applyMediaSession() {
        if (!('mediaSession' in navigator) || !current) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: current.jingle ? 'Jingle' : trackTitle(current),
            artist: current.jingle ? 'CréaZik IA WebRadio' : plName(current.playlist_label),
            album: 'CréaZik IA WebRadio'
        });
        navigator.mediaSession.setActionHandler('play', startListening);
        navigator.mediaSession.setActionHandler('pause', stopListening);
        try {
            navigator.mediaSession.setActionHandler('nexttrack', () => navigate(1));
            navigator.mediaSession.setActionHandler('previoustrack', () => navigate(-1));
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
        const rb = $('thumbReset');
        if (rb) {
            rb.hidden = !adminSession;
            rb.disabled = !((mine.up || 0) + (mine.down || 0));
        }
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

    let voteBusy = false;

    async function sendVoteSingle(kind) {
        if (voteBusy) return;
        voteBusy = true;
        const key = current.key;
        const other = kind === 'up' ? 'down' : 'up';
        const mine = Object.assign({up: 0, down: 0}, votes.mine[key]);
        const apply = res => {
            votes.tracks[key] = {up: res.up, down: res.down, score: res.score};
            votes.mine[key] = res.mine;
        };
        const post = async (url, body) => {
            const r = await fetch(url, {method: 'POST', headers: Object.assign({'Content-Type': 'application/json'}, UI_HEADERS), body: JSON.stringify(body)});
            if (!r.ok) throw new Error(r.status);
            apply(await r.json());
        };
        try {
            if (mine[kind] > 0 || mine[other] > 0) await post('/api/vote/reset', {key});
            if (!(mine[kind] > 0)) await post('/api/vote', {key, vote: kind, count: 1});
        } catch (e) {}
        voteBusy = false;
        updateThumbs();
    }

    function sendVote(kind) {
        if (!current || current.jingle) return;
        if (!adminSession) {
            sendVoteSingle(kind);
            return;
        }
        const key = current.key;
        const entry = Object.assign({up: 0, down: 0}, votes.tracks[key]);
        entry[kind] += 1;
        votes.tracks[key] = entry;
        const mine = Object.assign({up: 0, down: 0}, votes.mine[key]);
        mine[kind] += 1;
        votes.mine[key] = mine;
        votes.neutral = (votes.neutral || []).filter(k => k !== key);
        const bucket = pendingVotes[key] || (pendingVotes[key] = {up: 0, down: 0});
        bucket[kind] += 1;
        updateThumbs();
        if (!voteTimer) voteTimer = setTimeout(flushVotes, 400);
    }

    async function resetThumbs() {
        if (!current || current.jingle || !adminSession) return;
        const key = current.key;
        delete pendingVotes[key];
        try {
            const r = await fetch('/api/vote/reset', {method: 'POST', headers: Object.assign({'Content-Type': 'application/json'}, UI_HEADERS),
                                                      body: JSON.stringify({key})});
            if (!r.ok) throw new Error(r.status);
            const res = await r.json();
            votes.tracks[key] = {up: res.up, down: res.down, score: res.score};
            votes.mine[key] = res.mine;
        } catch (e) {}
        updateThumbs();
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
                    const r = await fetch('/api/vote', {method: 'POST', headers: Object.assign({'Content-Type': 'application/json'}, UI_HEADERS),
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
        data.key = current ? (current.key || '') : '';
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

    function jingleGain() {
        const v = live.ui && live.ui.jingle_volume;
        return typeof v === 'number' ? Math.max(0, Math.min(1, v)) : JINGLE_GAIN;
    }

    function transitionMs() {
        const s = live.ui && live.ui.visual_transition_s;
        return Math.max(3, Math.min(10, Number(s) || 5)) * 1000;
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
    }

    const AD_SLOT_S = 9;
    const MASCOT_S = 5;
    const PHASE_S = 5;
    const COVER_PHASE_S = 7;
    const AD_PHASE_S = 9;
    const PHASES = [{kind: 'cover', d: COVER_PHASE_S}, {kind: 'viz', d: PHASE_S}, {kind: 'ad', d: AD_PHASE_S}, {kind: 'viz', d: PHASE_S}];
    const CYCLE_S = PHASES.reduce((a, p) => a + p.d, 0);
    const adPanelEl = $('adPanel');
    const coverBlack = $('coverBlack');
    let coverOk = false;
    let phaseT0 = null;
    let adN = -1;
    let adStart = 0;
    let adWasOn = false;
    let adOffAt = -10;
    const phaseShine = $('phaseShine');
    const PHASE_FX_MS = 1000;
    const reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    const PHASE_FX = reduceMotion ? [{k: [{opacity: 0}, {opacity: 1}], e: 'linear'}] : [
        {k: [{clipPath: 'circle(0% at 50% 50%)'}, {clipPath: 'circle(75% at 50% 50%)'}], e: 'cubic-bezier(0.65, 0, 0.35, 1)'},
        {k: [{clipPath: 'polygon(0 0, 0 0, 0 0)'}, {clipPath: 'polygon(0 0, 250% 0, 0 250%)'}], e: 'cubic-bezier(0.65, 0, 0.35, 1)'},
        {k: [{transform: 'scale(1.4)', filter: 'blur(14px)', opacity: 0}, {transform: 'scale(1)', filter: 'blur(0)', opacity: 1}], e: 'cubic-bezier(0.22, 1, 0.36, 1)'},
        {k: [{clipPath: 'inset(50% 0 50% 0)'}, {clipPath: 'inset(0 0 0 0)'}], e: 'cubic-bezier(0.65, 0, 0.35, 1)'},
        {k: [{transform: 'perspective(700px) rotateY(-90deg)', opacity: 0}, {transform: 'perspective(700px) rotateY(0deg)', opacity: 1}], e: 'cubic-bezier(0.22, 1, 0.36, 1)'},
        {k: [{transform: 'rotate(-14deg) scale(0.5)', filter: 'blur(6px)', opacity: 0}, {transform: 'rotate(0deg) scale(1)', filter: 'blur(0)', opacity: 1}], e: 'cubic-bezier(0.34, 1.4, 0.64, 1)'},
        {k: [{clipPath: 'inset(0 100% 0 0)'}, {clipPath: 'inset(0 0 0 0)'}], e: 'cubic-bezier(0.65, 0, 0.35, 1)'},
        {k: [{clipPath: 'inset(0 0 100% 0)', transform: 'translateY(-12%)'}, {clipPath: 'inset(0 0 0 0)', transform: 'translateY(0)'}], e: 'cubic-bezier(0.22, 1, 0.36, 1)'}
    ];
    let phaseFxN = 0;

    function setLayer(el, on) {
        if (!el || !!el._on === on) return;
        el._on = on;
        const fx = PHASE_FX[phaseFxN++ % PHASE_FX.length];
        if (el._anim) el._anim.cancel();
        const anim = el.animate(fx.k, {duration: PHASE_FX_MS, easing: fx.e, fill: 'both', direction: on ? 'normal' : 'reverse'});
        el._anim = anim;
        if (on) el.style.visibility = 'visible';
        anim.onfinish = () => {
            if (!on) el.style.visibility = 'hidden';
            anim.cancel();
            if (el._anim === anim) el._anim = null;
        };
        if (phaseShine && !reduceMotion) {
            phaseShine.animate([
                {transform: 'translateX(-130%)', opacity: 0},
                {opacity: 1, offset: 0.35},
                {transform: 'translateX(130%)', opacity: 0}
            ], {duration: PHASE_FX_MS, easing: 'ease-in-out'});
        }
    }
    const AD_TR_S = 1.1;
    const adCanvas = $('adCanvas');
    const adCtx = adCanvas ? adCanvas.getContext('2d') : null;
    const adState = {i: 0, start: null};

    let panelAdsSrc = null;
    let panelAdsList = [];

    function panelAds() {
        if (panelAdsSrc !== content) {
            panelAdsSrc = content;
            const site = content.site && content.site.url ? 'https://' + String(content.site.url).replace(/^https?:\/\//, '') + '/' : '';
            const ts = content.traveling_sound || {};
            const serenia = (content.ads || []).map(a => Object.assign({}, a, {kind: 'serenia', url: site, label: 'Publicité : découvrir SéréniaTech (serenia-tech.fr)'}));
            const radio = (content.jingle_messages || []).map(m => ({
                headline: (m.lines && m.lines[0]) || m.title || '',
                sub: (m.lines && m.lines.slice(1).join(' - ')) || '',
                cta: m.title || 'CréaZik IA WebRadio',
                radio: true,
                kind: 'radio'
            }));
            const travel = (ts.ads || []).map(a => Object.assign({}, a, {kind: 'ts', url: ts.url || '', label: 'Écouter Traveling Sound Web Radio'}));
            const messages = (content.messages || []).map(m => Object.assign({}, m, {radio: true, kind: 'radio'}));
            const groups = profile && Array.isArray(profile.ad_groups) ? profile.ad_groups : null;
            const allow = g => !groups || groups.includes(g);
            panelAdsList = [[serenia, 'serenia'], [travel, 'traveling_sound'], [radio, 'radio'], [messages, 'messages']]
                .filter(([g, id]) => g.length && allow(id)).map(([g]) => g);
        }
        return panelAdsList;
    }

    function panelAdAt(n) {
        const groups = panelAds();
        if (!groups.length) return null;
        const g = groups[n % groups.length];
        return g[Math.floor(n / groups.length) % g.length];
    }

    function adItemDur(i) { return i % 2 === 0 ? AD_SLOT_S : MASCOT_S; }

    function easeInOut(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }

    function drawAdBackground(w, h, t, local, n, mode) {
        let hue = (200 + n * 47 + local * 5) % 360;
        let h2 = (hue + 60) % 360;
        if (mode === 'ts') {
            const g = adCtx.createLinearGradient(0, 0, w, h);
            g.addColorStop(0, '#0a0707');
            g.addColorStop(1, '#221517');
            adCtx.fillStyle = g;
            adCtx.fillRect(0, 0, w, h);
            for (let k = 0; k < 2; k++) {
                const a = t * (0.25 + k * 0.13) + k * 2.1;
                const cx = w * (0.5 + 0.35 * Math.cos(a));
                const cy = h * (0.5 + 0.35 * Math.sin(a * 1.2));
                const rg = adCtx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.55);
                const c = k ? 'hsla(30,70%,45%,' : 'hsla(123,34%,40%,';
                rg.addColorStop(0, c + '0.22)');
                rg.addColorStop(1, c + '0)');
                adCtx.fillStyle = rg;
                adCtx.fillRect(0, 0, w, h);
            }
            return;
        }
        if (mode === 'radio') {
            const g = adCtx.createLinearGradient(0, 0, w, h);
            g.addColorStop(0, '#11111d');
            g.addColorStop(1, '#0b0b14');
            adCtx.fillStyle = g;
            adCtx.fillRect(0, 0, w, h);
            for (let k = 0; k < 2; k++) {
                const a = t * (0.25 + k * 0.13) + k * 2.1;
                const cx = w * (0.5 + 0.35 * Math.cos(a));
                const cy = h * (0.5 + 0.35 * Math.sin(a * 1.2));
                const rg = adCtx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.55);
                const c = k ? 'hsla(200,88%,66%,' : 'hsla(330,92%,68%,';
                rg.addColorStop(0, c + '0.20)');
                rg.addColorStop(1, c + '0)');
                adCtx.fillStyle = rg;
                adCtx.fillRect(0, 0, w, h);
            }
            return;
        }
        const g = adCtx.createLinearGradient(0, 0, w, h);
        g.addColorStop(0, `hsl(${hue} 55% 14%)`);
        g.addColorStop(1, `hsl(${h2} 60% 8%)`);
        adCtx.fillStyle = g;
        adCtx.fillRect(0, 0, w, h);
        for (let k = 0; k < 2; k++) {
            const a = t * (0.25 + k * 0.13) + k * 2.1;
            const cx = w * (0.5 + 0.35 * Math.cos(a));
            const cy = h * (0.5 + 0.35 * Math.sin(a * 1.2));
            const r = Math.max(w, h) * 0.55;
            const rg = adCtx.createRadialGradient(cx, cy, 0, cx, cy, r);
            rg.addColorStop(0, `hsla(${(hue + 40 * k) % 360} 80% 55% / 0.28)`);
            rg.addColorStop(1, `hsla(${(hue + 40 * k) % 360} 80% 55% / 0)`);
            adCtx.fillStyle = rg;
            adCtx.fillRect(0, 0, w, h);
        }
    }

    function drawAdItem(i, w, h, t, local) {
        const designs = window.CreaMotion.ads;
        const n = Math.floor(i / 2);
        adCtx.save();
        try {
            if (i % 2 === 1 && window.CreaMascot) {
                const bpm = current && current.bpm ? current.bpm : 120;
                window.CreaMascot.draw(adCtx, w, h, local, MASCOT_S, data, bpm, (200 + n * 47) % 360, current);
            } else {
                const adItem = panelAdAt(n);
                drawAdBackground(w, h, t, local, n, adItem && (adItem.radio ? 'radio' : (adItem.kind === 'ts' ? 'ts' : null)));
                designs[n % designs.length].draw(adCtx, w, h, local, AD_SLOT_S, adItem, data);
            }
        } finally {
            adCtx.restore();
        }
    }

    function revealPath(style, w, h, e) {
        adCtx.beginPath();
        if (style === 0) {
            adCtx.arc(w / 2, h / 2, e * Math.hypot(w, h) * 0.53, 0, Math.PI * 2);
        } else if (style === 1) {
            const E = e * (w + h);
            adCtx.moveTo(0, 0);
            adCtx.lineTo(E, 0);
            adCtx.lineTo(0, E);
            adCtx.closePath();
        } else {
            const bands = 6;
            for (let k = 0; k < bands; k++) {
                const bh = h / bands;
                adCtx.rect(0, k * bh + bh * (1 - e) / 2, w, bh * e);
            }
        }
    }

    function drawRevealAccent(style, w, h, e, p, hue, t) {
        if (style === 2) return;
        adCtx.save();
        adCtx.globalAlpha = Math.sin(Math.PI * Math.min(1, p));
        adCtx.strokeStyle = `hsl(${hue} 95% 75%)`;
        adCtx.shadowColor = `hsl(${hue} 95% 65%)`;
        adCtx.shadowBlur = 14;
        adCtx.lineWidth = 3;
        adCtx.beginPath();
        let cx = 0;
        let cy = 0;
        if (style === 0) {
            const r = e * Math.hypot(w, h) * 0.53;
            adCtx.arc(w / 2, h / 2, r, 0, Math.PI * 2);
        } else {
            const E = e * (w + h);
            adCtx.moveTo(E, 0);
            adCtx.lineTo(0, E);
        }
        adCtx.stroke();
        adCtx.shadowBlur = 0;
        adCtx.fillStyle = `hsl(${(hue + 40) % 360} 95% 85%)`;
        for (let k = 0; k < 12; k++) {
            const u = (k + 0.5) / 12;
            if (style === 0) {
                const a = u * Math.PI * 2 + t * 0.8;
                const r = e * Math.hypot(w, h) * 0.53;
                cx = w / 2 + Math.cos(a) * r;
                cy = h / 2 + Math.sin(a) * r;
            } else {
                const E = e * (w + h);
                cx = E * (1 - u);
                cy = E * u;
            }
            const sz = (1.2 + 1.6 * Math.abs(Math.sin(t * 6 + k * 1.7))) * (w / 150);
            adCtx.fillRect(cx - sz / 2, cy - sz / 2, sz, sz);
        }
        adCtx.restore();
    }

    function drawAdPhase(w, h, t, local) {
        const designs = window.CreaMotion.ads;
        const n = Math.max(0, adN);
        const item = panelAdAt(n);
        adCtx.save();
        try {
            drawAdBackground(w, h, t, local, n, item && (item.radio ? 'radio' : (item.kind === 'ts' ? 'ts' : null)));
            designs[n % designs.length].draw(adCtx, w, h, local, AD_PHASE_S, item, data);
        } finally {
            adCtx.restore();
        }
    }

    function drawAds(t, adOn) {
        if (!adCtx || !window.CreaMotion || !window.CreaMotion.ads || !panelAds().length) return;
        if (!adOn && t - adOffAt > 1.1) return;
        const w = adCanvas.clientWidth;
        const h = adCanvas.clientHeight;
        if (!w || !h) return;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        if (adCanvas.width !== Math.round(w * dpr) || adCanvas.height !== Math.round(h * dpr)) {
            adCanvas.width = Math.round(w * dpr);
            adCanvas.height = Math.round(h * dpr);
        }
        adCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
        drawAdPhase(w, h, t, t - adStart);
    }

    function setAdLink(item) {
        if (!adPanelEl) return;
        const url = item && item.url;
        if (url) {
            adPanelEl.setAttribute('href', url);
            adPanelEl.setAttribute('aria-label', item.label || 'Publicité');
            adPanelEl.removeAttribute('tabindex');
            adPanelEl.dataset.link = '1';
        } else {
            adPanelEl.removeAttribute('href');
            adPanelEl.removeAttribute('aria-label');
            adPanelEl.setAttribute('tabindex', '-1');
            adPanelEl.dataset.link = '0';
        }
    }

    function updatePhase(t) {
        if (phaseT0 === null) phaseT0 = t;
        let x = (t - phaseT0) % CYCLE_S;
        let kind = 'viz';
        let pd = 0;
        for (const p of PHASES) {
            if (x < p.d) { kind = p.kind; pd = p.d; break; }
            x -= p.d;
        }
        const userOn = userImageOn();
        const adOn = kind === 'ad' && !userOn;
        if (adOn && !adWasOn) {
            adN += 1;
            adStart = t;
            setAdLink(panelAdAt(adN));
        }
        if (!adOn && adWasOn) adOffAt = t;
        adWasOn = adOn;
        const coverOn = kind === 'cover' && coverOk && !userOn;
        setLayer(coverBlack, coverOn || userOn);
        const coverShown = coverOn && x > PHASE_FX_MS / 1000 && x < pd - PHASE_FX_MS / 1000;
        trackCover.classList.toggle('show', coverShown);
        if (coverShown) fitCoverTitle();
        coverLabel.classList.toggle('show', coverShown);
        if (userImageEl) userImageEl.classList.toggle('show', userOn);
        setLayer(adPanelEl, adOn);
        return adOn;
    }

    function frame(now) {
        requestAnimationFrame(frame);
        if (document.hidden) return;
        const adOn = updatePhase(now / 1000);
        drawAds(now / 1000, adOn);
        resizeCanvas();
        updateData(now / 1000);
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        if (w && h) drawVisual(w, h, now);
    }

    function plName(label) {
        return String(label || '').replace(/^playlist\s+/i, '');
    }

    function playList(list, refill) {
        if (!haveClock || !Array.isArray(list) || !list.length) return false;
        personal = {list: list.map((t, i) => Object.assign({}, t, {uid: 's' + i})), idx: 0, item: null,
                    refill: typeof refill === 'function' ? refill : null, sinceJingle: 1};
        goTo(0, false);
        if (!listening) startListening();
        return true;
    }

    const userImageEl = $('userImage');
    let userImg = null;

    function showUserImage(src) {
        if (!userImageEl) return;
        const cur = current && !current.jingle ? current : null;
        userImg = {src, key: cur ? cur.key : null};
        userImageEl.src = src;
        userImageEl.hidden = false;
    }

    function clearUserImage() {
        userImg = null;
        if (!userImageEl) return;
        userImageEl.classList.remove('show');
        userImageEl.hidden = true;
        userImageEl.removeAttribute('src');
    }

    function userImageOnTrack(it) {
        if (!userImg || !it) return;
        if (userImg.key === null) {
            if (!it.jingle) userImg.key = it.key;
        } else if (it.key !== userImg.key) {
            clearUserImage();
        }
    }

    function userImageOn() {
        return !!(userImg && userImg.key && current && current.key === userImg.key);
    }

    function pluginNotify(src, after) {
        const done = typeof after === 'function' ? after : () => {};
        if (!listening) {
            done();
            return;
        }
        playNotify(src, done);
    }

    function unlockAudio() {
        ensureGraph();
        unlockNotify();
    }

    function uiFetch(url, opts) {
        const o = Object.assign({}, opts || {});
        o.headers = Object.assign({}, UI_HEADERS, o.headers || {});
        return fetch(url, o);
    }

    function adminApi() {
        return Object.freeze({
            live: () => live,
            current: () => (current ? Object.assign({}, current) : null),
            votes: () => votes,
            radioAction,
            stopListening,
            isListening: () => listening,
            onLive: fn => { if (typeof fn === 'function') hooks.live.push(fn); },
            onTrack: fn => { if (typeof fn === 'function') hooks.track.push(fn); },
            onListen: fn => { if (typeof fn === 'function') hooks.listen.push(fn); },
            trackTitle,
            fmtTime,
            fmtClock
        });
    }

    function pluginCtx(entry, body, card) {
        return Object.freeze({
            id: entry.id,
            title: entry.title,
            body,
            session: session ? JSON.parse(JSON.stringify(session)) : null,
            profile: profile ? JSON.parse(JSON.stringify(profile)) : null,
            esc,
            plName,
            getJSON,
            fetch: uiFetch,
            postJSON: (url, data) => uiFetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}),
            state: () => ({listening, haveClock, current: current ? Object.assign({}, current) : null}),
            playList,
            unlockAudio,
            playNotify: pluginNotify,
            notifyBusy: () => notifyBusy,
            showImage: showUserImage,
            setVisible: v => { if (card) card.hidden = !v; },
            admin: adminSession && entry.scope === 'admin' ? adminApi() : null
        });
    }

    function loadAsset(tag, attrs) {
        return new Promise(resolve => {
            const el = document.createElement(tag);
            Object.keys(attrs).forEach(k => el.setAttribute(k, attrs[k]));
            el.onload = () => resolve(true);
            el.onerror = () => resolve(false);
            (tag === 'script' ? document.body : document.head).appendChild(el);
        });
    }

    function pluginCard(entry) {
        const list = $('pluginList');
        if (!list) return null;
        const card = document.createElement('article');
        card.className = 'plugin' + (entry.scope === 'admin' ? ' plugin-admin' : '');
        card.dataset.plugin = entry.id;
        const bodyId = 'plugin-' + entry.id + '-body';
        card.innerHTML = '<h3 class="plugin-h"><button class="plugin-toggle" type="button" aria-expanded="false" aria-controls="' + esc(bodyId) + '">'
            + '<span class="plugin-name">' + esc(entry.title) + '</span><span class="plugin-chev" aria-hidden="true"></span></button></h3>'
            + '<div id="' + esc(bodyId) + '" class="plugin-body" hidden></div>';
        list.appendChild(card);
        return card;
    }

    function mountPlugin(entry) {
        const def = pluginDefs[entry.id];
        if (!def) return false;
        const slot = entry.slot || 'card';
        let card = null;
        let body;
        if (slot === 'card') {
            card = pluginCard(entry);
            if (!card) return false;
            body = card.querySelector('.plugin-body');
        } else {
            const host = document.querySelector('[data-plugin-slot="' + slot + '"]');
            if (!host) return false;
            body = document.createElement('div');
            body.dataset.plugin = entry.id;
            host.appendChild(body);
        }
        const ctx = pluginCtx(entry, body, card);
        try {
            def.init(ctx);
        } catch (e) {
            if (card) card.remove(); else body.remove();
            return false;
        }
        if (card) {
            const btn = card.querySelector('.plugin-toggle');
            const remember = entry.scope === 'admin';
            let opened = false;
            const setOpen = open => {
                btn.setAttribute('aria-expanded', String(open));
                body.hidden = !open;
                if (remember) {
                    cardsOpen[entry.id] = open;
                    try { localStorage.setItem(CARDS_STORE, JSON.stringify(cardsOpen)); } catch (e) {}
                }
                if (open && !opened) {
                    opened = true;
                    if (typeof def.open === 'function') def.open(ctx);
                }
            };
            btn.addEventListener('click', () => setOpen(btn.getAttribute('aria-expanded') !== 'true'));
            if (remember && cardsOpen[entry.id]) setOpen(true);
        }
        return slot === 'card';
    }

    const CARDS_STORE = 'adminCardsOpen';
    let cardsOpen = {};
    try { cardsOpen = JSON.parse(localStorage.getItem(CARDS_STORE) || '{}') || {}; } catch (e) { cardsOpen = {}; }

    async function mountPlugins() {
        const entries = (session && Array.isArray(session.plugins) ? session.plugins : [])
            .filter(e => e && /^[a-z0-9][a-z0-9-]*$/.test(e.id) && /^[\w-]+\.js$/.test(e.file || '')
                && (e.scope !== 'admin' || adminSession));
        const sheets = new Set();
        entries.forEach(e => { if (e.css && /^[\w-]+\.css$/.test(e.css)) sheets.add(e.css); });
        await Promise.all(Array.from(sheets).map(css => loadAsset('link', {rel: 'stylesheet', href: '/plugins/' + css})));
        const scripts = new Set(entries.map(e => e.file));
        await Promise.all(Array.from(scripts).map(f => loadAsset('script', {src: '/plugins/' + f})));
        let cards = 0;
        entries.forEach(e => { if (mountPlugin(e)) cards += 1; });
        const section = $('plugins');
        if (section) section.hidden = !cards;
    }

    async function loadSession() {
        session = await getJSON('/api/session', {role: 'anon', user: null, profile: null, plugins: [], view_as: null});
        profile = session && session.profile ? session.profile : null;
        adminSession = !!session && session.role === 'admin';
        UI_HEADERS = adminSession ? {} : USER_HEADERS;
        panelAdsSrc = null;
        const logged = session && (session.role === 'admin' || session.role === 'user');
        const icon = $('sessionIcon');
        if (icon) {
            const label = logged ? 'Déconnexion' + (session.user ? ' (' + session.user + ')' : '') : 'Connexion';
            icon.setAttribute('href', logged ? '/logout' : '/login');
            icon.dataset.mode = logged ? (session.role === 'admin' ? 'admin' : 'user') : 'login';
            icon.setAttribute('aria-label', label);
            icon.title = label;
        }
        const text = $('sessionText');
        if (text) {
            text.setAttribute('href', logged ? '/logout' : '/login');
            text.textContent = logged ? 'Déconnexion' + (session.user ? ' (' + session.user + ')' : '') : 'Connexion';
        }
    }

    async function radioAction(body) {
        try {
            const r = await fetch('/api/radio/action', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                        body: JSON.stringify(body)});
            const st = await r.json().catch(() => null);
            if (st && st.active) {
                clockOffset = st.server_time - Date.now() / 1000;
                live = st;
                emit('live', true);
            }
            return r.ok;
        } catch (e) {
            return false;
        }
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
        const track = current ? ((current.jingle ? 'Jingle' : trackTitle(current)) + ' - ' + $('nowSub').textContent) : '';
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
        const on = (id, fn) => { const el = $(id); if (el) el.addEventListener('click', fn); };
        on('playBtn', toggle);
        on('userPrevBtn', () => navigate(-1));
        on('userNextBtn', () => navigate(1));
        on('userLiveBtn', goLive);
        on('thumbUp', () => sendVote('up'));
        on('thumbDown', () => sendVote('down'));
        on('thumbReset', resetThumbs);
        window.addEventListener('resize', () => fitCoverTitle(true));
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => fitCoverTitle(true));
        slots.forEach(s => s.el.addEventListener('error', () => onSlotError(s)));
        const cf = $('comForm');
        if (cf) cf.addEventListener('submit', postComment);
        await loadSession();
        specs = await getJSON('./scenes_spec.json', {playlists: {}});
        content = Object.assign({jingle_messages: [], ads: []}, await getJSON('./radio_content.json', {}));
        setPlayLabel();
        setTicker('CréaZik IA WebRadio : musiques générées par intelligence artificielle, en local   |   Contact : sereniatech33@gmail.com   |   serenia-tech.fr');
        await refreshLive();
        mountPlugins();
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
    }

    window.__radioDebug = () => ({current, T: serverNow(), live: {active: live.active, upcoming: live.upcoming.length}, content, sceneKey, listening, transActive: !!(transEngine && transEngine.active),
                                  profile: profile && profile.id, view: liveItems().map(it => ({key: it.key, jingle: !!it.jingle, category: it.category, duck: !!it.duck})),
                                  ads: panelAds().map(g => g[0] && (g[0].kind + ':' + g[0].headline))});
    window.__fitCoverTitle = fitCoverTitle;
    window.addEventListener('load', init);
}());
