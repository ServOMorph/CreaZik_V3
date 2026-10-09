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
        if (testing) stopTest();
        if (listening) stopListening(); else startListening();
    }

    const testAudio = new Audio();
    let testing = false;

    function setTestLabel(text) {
        const b = $('testBtn');
        b.textContent = text || (testing ? 'Arrêter' : 'Test');
        b.setAttribute('aria-pressed', testing ? 'true' : 'false');
    }

    function stopTest() {
        testing = false;
        testAudio.pause();
        setTestLabel();
        renderTests();
    }

    let testsItems = [];
    let testsCur = '';

    const TEST_ICONS = {
        up: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 11v10H3V11z"/><path d="M7 11l4-8a2.5 2.5 0 0 1 2.5 2.8L13 9h6.2a2 2 0 0 1 2 2.3l-1.3 8a2 2 0 0 1-2 1.7H7"/></svg>',
        down: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 13V3h4v10z"/><path d="M17 13l-4 8a2.5 2.5 0 0 1-2.5-2.8L11 15H4.8a2 2 0 0 1-2-2.3l1.3-8A2 2 0 0 1 6.100 3H17"/></svg>',
        del: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/></svg>'
    };

    function testSeekMax() {
        const d = testAudio.duration;
        if (isFinite(d) && d > 0) return d;
        const it = testsItems.find(x => x.file === testsCur);
        return it && it.duration ? Number(it.duration) : 0;
    }

    function updateTestSeek() {
        const range = $('testSeek');
        const label = $('testTime');
        if (!range || !label) return;
        const d = testSeekMax();
        if (!range.matches(':active')) range.value = d ? Math.round(testAudio.currentTime / d * 1000) : 0;
        label.textContent = fmtTime(testAudio.currentTime) + ' / ' + fmtTime(d);
    }

    function renderTests() {
        const box = $('testsList');
        const panel = $('testsPanel');
        if (!box || !panel || panel.hidden) return;
        if (!testsItems.length) {
            box.innerHTML = '<div class="prog-empty">Aucune version de test.</div>';
            return;
        }
        box.innerHTML = testsItems.map(it => {
            const cur = it.file === testsCur;
            const f = esc(it.file);
            const act = (a, label, icon) => `<button type="button" class="prog-act test-act" data-act="${a}" data-file="${f}" aria-label="${label}" title="${label}"${a === 'up' || a === 'down' ? ` aria-pressed="${it.vote === a}"` : ''}>${icon}</button>`;
            const generated = it.generated_at ? new Date(it.generated_at).toLocaleString('fr-FR') : '';
            const provenance = [it.model, generated].filter(Boolean).join(' · ');
            const quality = it.technical_status === 'pass_needs_listening' ? 'Controle technique reussi - ecoute requise' : it.technical_status === 'invalid' ? 'Controle technique invalide' : '';
            return `<div class="prog-item test-item${cur ? ' is-now' : ''}${it.played ? '' : ' is-new'}">
                <button type="button" class="prog-main" data-act="play" data-file="${f}">
                    <span class="prog-title">${cur && testing ? '&#9646;&#9646; ' : '&#9654; '}${esc(String(it.name).replace(/_/g, ' '))}</span>
                    ${provenance ? `<span class="prog-sub">${esc(provenance)}</span>` : ''}
                    ${quality ? `<span class="prog-sub">${esc(quality)}</span>` : ''}
                    <span class="prog-sub">${esc(it.prompt)}</span>
                    ${it.played ? '' : '<span class="prog-badge">Jamais &eacute;cout&eacute;</span>'}
                </button>
                ${act('up', "J'aime", TEST_ICONS.up)}${act('down', "Je n'aime pas", TEST_ICONS.down)}${act('delete', 'Supprimer cette version', TEST_ICONS.del)}
                ${cur ? '<div class="test-seek"><input id="testSeek" type="range" min="0" max="1000" step="1" value="0" aria-label="Position dans le morceau"><span id="testTime" class="time">0:00 / 0:00</span></div>' : ''}
            </div>`;
        }).join('');
        updateTestSeek();
    }

    async function loadTests() {
        const d = await getJSON('/api/tests', null);
        if (!d || !Array.isArray(d.items)) return;
        const num = f => parseInt((f.split('/').pop().match(/^(\d+)/) || [0, 0])[1], 10);
        testsItems = d.items.slice().sort((a, b) => String(b.generated_at || '').localeCompare(String(a.generated_at || '')) || num(b.file) - num(a.file));
        renderTests();
    }

    async function testsPost(path, body) {
        try {
            const r = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
            return r.ok;
        } catch (e) {
            return false;
        }
    }

    function markTestPlayed(file) {
        const it = testsItems.find(x => x.file === file);
        if (!it || it.played) return;
        it.played = true;
        testsPost('/api/tests/played', {file});
    }

    async function playTestFile(item) {
        if (listening) stopListening();
        if (testsCur !== item.file) {
            testAudio.src = '/' + item.file + '?v=' + encodeURIComponent(item.generated_at || '');
            testsCur = item.file;
        }
        try {
            await testAudio.play();
            testing = true;
            markTestPlayed(item.file);
        } catch (e) {
            testing = false;
        }
        setTestLabel();
        renderTests();
    }

    async function onTestsClick(ev) {
        const btn = ev.target.closest('button[data-act]');
        if (!btn) return;
        const item = testsItems.find(x => x.file === btn.dataset.file);
        if (!item) return;
        const act = btn.dataset.act;
        if (act === 'play') {
            if (testsCur === item.file && testing) stopTest(); else playTestFile(item);
        } else if (act === 'up' || act === 'down') {
            const vote = item.vote === act ? 'none' : act;
            if (await testsPost('/api/tests/vote', {file: item.file, vote})) {
                item.vote = vote === 'none' ? '' : vote;
                renderTests();
            }
        } else if (act === 'delete') {
            if (!confirm('Supprimer définitivement cette version de test ?')) return;
            if (await testsPost('/api/tests/delete', {file: item.file})) {
                if (testsCur === item.file) {
                    testing = false;
                    testAudio.pause();
                    testAudio.removeAttribute('src');
                    testsCur = '';
                    setTestLabel();
                }
                await loadTests();
            }
        }
    }

    async function toggleTest() {
        if (testing) { stopTest(); return; }
        const b = $('testBtn');
        b.disabled = true;
        try {
            const d = await getJSON('/api/tests', null);
            if (!d || !Array.isArray(d.items)) throw new Error('tests indisponibles');
            testsItems = d.items.slice().sort((a, b) => String(a.generated_at || '').localeCompare(String(b.generated_at || '')));
            const g = testsItems[testsItems.length - 1];
            if (!g) throw new Error('aucun test');
            if (listening) stopListening();
            const mp3 = g.file;
            testAudio.src = '/' + mp3 + '?v=' + encodeURIComponent(g.generated_at || '');
            testsCur = mp3;
            await testAudio.play();
            testing = true;
            markTestPlayed(mp3);
            setTestLabel();
            renderTests();
        } catch (e) {
            testing = false;
            setTestLabel('Indisponible');
            setTimeout(() => setTestLabel(), 2000);
        }
        b.disabled = false;
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
        updateDiscover();
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
        showTrackCover(it);
        $('nowTitle').textContent = it.jingle ? 'Jingle' : trackTitle(it);
        $('nowSub').textContent = it.jingle ? 'CréaZik IA WebRadio' : plName(it.playlist_label);
        setTicker(buildTicker(it));
        loadViz(it);
        applyMediaSession();
        updateThumbs();
        renderProgram();
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
            navigator.mediaSession.setActionHandler('nexttrack', skip);
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
        const dbx = $('dynBox');
        if (dbx) dbx.hidden = !show;
        if (!show) return;
        const v = votes.tracks[current.key] || {up: 0, down: 0};
        const mine = votes.mine[current.key] || {up: 0, down: 0};
        const set = (id, text) => {
            const el = $(id);
            if (el) el.textContent = text;
        };
        set('thumbUpCount', v.up || 0);
        set('thumbDownCount', v.down || 0);
        const db = $('dynBox');
        if (db) {
            db.hidden = false;
            const lvls = String((votes.dynamics || {})[current.key] || '').split('+');
            db.querySelectorAll('.dyn-btn').forEach(b => {
                const on = lvls.includes(b.dataset.level);
                b.classList.toggle('active', on);
                b.setAttribute('aria-pressed', on ? 'true' : 'false');
            });
        }
        const rb = $('thumbReset');
        if (rb) rb.disabled = !((mine.up || 0) + (mine.down || 0));
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
        votes.neutral = (votes.neutral || []).filter(k => k !== key);
        const bucket = pendingVotes[key] || (pendingVotes[key] = {up: 0, down: 0});
        bucket[kind] += 1;
        updateThumbs();
        if (!voteTimer) voteTimer = setTimeout(flushVotes, 400);
    }

    async function setDynamics(level) {
        if (!current || current.jingle) return;
        const key = current.key;
        const prev = (votes.dynamics || {})[key];
        const order = ['slow', 'medium', 'high'];
        const sel = prev ? prev.split('+') : [];
        let nextSel;
        if (sel.includes(level)) nextSel = sel.filter(l => l !== level);
        else if (sel.length >= 2) nextSel = [level];
        else nextSel = sel.concat(level);
        nextSel.sort((a, b) => order.indexOf(a) - order.indexOf(b));
        const next = nextSel.length ? nextSel.join('+') : 'none';
        votes.dynamics = Object.assign({}, votes.dynamics);
        if (next === 'none') delete votes.dynamics[key]; else votes.dynamics[key] = next;
        updateThumbs();
        try {
            const r = await fetch('/api/dynamics', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                    body: JSON.stringify({key, level: next})});
            if (!r.ok) throw new Error(r.status);
        } catch (e) {
            if (prev) votes.dynamics[key] = prev; else delete votes.dynamics[key];
            updateThumbs();
        }
    }

    async function resetThumbs() {
        if (!current || current.jingle) return;
        const key = current.key;
        delete pendingVotes[key];
        try {
            const r = await fetch('/api/vote/reset', {method: 'POST', headers: {'Content-Type': 'application/json'},
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
        data.key = current ? (current.key || '') : '';
        const base = current ? hueFor(current.key || '') : 200;
        data.hue = (base + progress * 140 + sm.level * 50) % 360;
    }

    function initHumanBanner() {
        const img = $('humanBanner');
        const fb = $('humanFallback');
        if (!img || !fb) return;
        const fail = () => {
            img.hidden = true;
            fb.hidden = false;
        };
        img.addEventListener('error', fail);
        if (img.complete && img.naturalWidth === 0) fail();
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
            panelAdsList = [serenia, travel, radio].filter(g => g.length);
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
        const adOn = kind === 'ad';
        if (adOn && !adWasOn) {
            adN += 1;
            adStart = t;
            setAdLink(panelAdAt(adN));
        }
        if (!adOn && adWasOn) adOffAt = t;
        adWasOn = adOn;
        const coverOn = kind === 'cover' && coverOk;
        setLayer(coverBlack, coverOn);
        const coverShown = coverOn && x > PHASE_FX_MS / 1000 && x < pd - PHASE_FX_MS / 1000;
        trackCover.classList.toggle('show', coverShown);
        if (coverShown) fitCoverTitle();
        coverLabel.classList.toggle('show', coverShown);
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

    function rowHtml(it, src, extra) {
        const isJ = !!it.jingle;
        const sub = (isJ ? 'Jingle' : plName(it.playlist_label)) + (it.duration ? ' - ' + fmtTime(it.duration) : '');
        const badge = extra.explicit ? '<span class="prog-badge">Choisi</span>'
            : (extra.auto && isJ ? '<span class="prog-badge">Jingle auto</span>' : '');
        const attrs = `data-src="${src}" data-key="${esc(it.key)}"` + (extra.qi !== undefined ? ` data-qi="${extra.qi}"` : '');
        const removable = src === 'queue' && !(extra.auto && isJ);
        return `<div class="prog-item${isJ ? ' is-jingle' : ''}${extra.explicit ? ' is-explicit' : ''}${extra.cls || ''}" ${attrs}>
            <button type="button" class="prog-main" data-act="next" ${attrs}>
                <span class="prog-title">${esc(trackTitle(it))}</span>
                <span class="prog-sub">${esc(sub)}${extra.time ? ' - ' + esc(extra.time) : ''}</span>
                ${badge}
            </button>
            <button type="button" class="prog-act" data-act="now" ${attrs} aria-label="Lire juste après" title="Lire juste après">&#9654;</button>
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
                   <span class="prog-title">${esc(current.jingle ? 'Jingle - ' + trackTitle(current) : trackTitle(current))}</span>
                   <span class="prog-sub">${esc(current.jingle ? 'CréaZik IA WebRadio' : plName(current.playlist_label))}</span>
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
                        <span class="prog-pl-name">${esc(plName(pl.label))}</span>
                        <span class="prog-pl-count">${pl.tracks.length}</span>
                    </button>
                    <button type="button" class="prog-pl-act" data-act="pl-next" data-playlist="${b}">Ensuite</button>
                    <button type="button" class="prog-pl-act" data-act="pl-now" data-playlist="${b}">Lire</button>
                </div>
                <div class="prog-pl-tracks">${open ? pl.tracks.map(t => rowHtml(t, 'library', {})).join('') : ''}</div>
            </div>`;
        }).join('') : empty('Aucune playlist disponible.'));
    }

    function plName(label) {
        return String(label || '').replace(/^playlist\s+/i, '');
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
                updateDiscover();
                renderProgram();
            }
        } catch (e) {}
    }

    function updateDiscover() {
        const b = $('discoverBtn');
        if (!b) return;
        b.hidden = !isAdmin;
        const on = !!live.unrated_only;
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        b.textContent = on ? 'Désactiver découverte' : 'Découverte';
    }

    function toggleDiscover() {
        radioAction({action: 'unrated', on: !live.unrated_only});
    }

    async function skip() {
        if (effectiveAdmin()) {
            radioAction({action: 'skip'});
            return;
        }
        try {
            await fetch('/api/skip', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
            const r = await fetch('/api/radio/state?t=' + Date.now());
            const st = await r.json().catch(() => null);
            if (st && st.active) {
                clockOffset = st.server_time - Date.now() / 1000;
                live = st;
            }
        } catch (e) {}
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
        if (act === 'pl-now') { radioAction({action: 'playlist_front', id: playlistId}); return; }
        if (src === 'queue') {
            const index = parseInt(btn.dataset.qi, 10);
            if (act === 'remove') radioAction({action: 'remove', index});
            else if (act === 'next' || act === 'now') radioAction({action: 'move_front', index});
            return;
        }
        if (act === 'now') radioAction({action: 'front', key});
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
        setHidden('nextBtn', false);
        setHidden('adminBar', true);
        updateDiscover();
        syncAdminEmbed();
        setHidden('progPanel', !adm);
        setHidden('testsPanel', !isAdmin);
        if (isAdmin) loadTests();
        setHidden('humanRadio', true);
        updateThumbs();
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

    function syncAdminEmbed() {
        const box = $('adminEmbed');
        const frame = $('adminFrame');
        if (!box || !frame || frame.getAttribute('src')) return;
        box.hidden = false;
        let ro = null;
        const fit = () => {
            const d = frame.contentDocument;
            if (d && d.body) frame.style.height = Math.ceil(d.body.getBoundingClientRect().height) + 'px';
        };
        frame.addEventListener('load', async () => {
            const d = frame.contentDocument;
            if (ro) ro.disconnect();
            if (d && d.body && window.ResizeObserver) {
                d.documentElement.style.overflow = 'hidden';
                d.body.style.minHeight = '0';
                ro = new ResizeObserver(fit);
                ro.observe(d.body);
            }
            fit();
            const me = await getJSON('/api/me', {admin: false});
            if (!!me.admin !== isAdmin) {
                isAdmin = !!me.admin;
                applyMode();
            }
        });
        frame.src = '/radio.html';
    }

    async function init() {
        const me = await getJSON('/api/me', {admin: false});
        isAdmin = !!me.admin;
        $('playBtn').addEventListener('click', toggle);
        $('nextBtn').addEventListener('click', skip);
        $('testBtn').addEventListener('click', toggleTest);
        $('discoverBtn').addEventListener('click', toggleDiscover);
        window.addEventListener('resize', () => fitCoverTitle(true));
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => fitCoverTitle(true));
        testAudio.addEventListener('ended', stopTest);
        testAudio.addEventListener('timeupdate', updateTestSeek);
        testAudio.addEventListener('loadedmetadata', updateTestSeek);
        const tl = $('testsList');
        if (tl) {
            tl.addEventListener('click', onTestsClick);
            tl.addEventListener('input', ev => {
                if (ev.target.id !== 'testSeek') return;
                const d = testSeekMax();
                if (d) testAudio.currentTime = Number(ev.target.value) / 1000 * d;
            });
        }
        const mi = $('modeIcon');
        if (mi) mi.addEventListener('click', onModeIcon);
        const panel = $('progPanel');
        if (panel) panel.addEventListener('click', onProgramClick);
        const tu = $('thumbUp');
        const td = $('thumbDown');
        if (tu) tu.addEventListener('click', () => sendVote('up'));
        if (td) td.addEventListener('click', () => sendVote('down'));
        document.querySelectorAll('.dyn-btn').forEach(b => b.addEventListener('click', () => { setDynamics(b.dataset.level); b.blur(); }));
        const tr = $('thumbReset');
        if (tr) tr.addEventListener('click', resetThumbs);
        slots.forEach(s => s.el.addEventListener('error', () => onSlotError(s)));
        const cf = $('comForm');
        if (cf) cf.addEventListener('submit', postComment);
        specs = await getJSON('./scenes_spec.json', {playlists: {}});
        content = Object.assign({jingle_messages: [], ads: []}, await getJSON('./radio_content.json', {}));
        initFolds();
        initHumanBanner();
        applyMode();
        setPlayLabel();
        setTicker('CréaZik IA WebRadio : musiques générées par intelligence artificielle, en local   |   Contact : sereniatech33@gmail.com   |   serenia-tech.fr');
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
    window.__fitCoverTitle = fitCoverTitle;
    window.addEventListener('load', init);
}());
