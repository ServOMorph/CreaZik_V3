(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'programmation',
        title: 'Programmation',
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            const esc = ctx.esc;
            const plName = ctx.plName;
            const openPlaylists = new Set();
            let library = [];
            let libraryLoaded = false;
            let visible = false;
            ctx.body.classList.add('prog-plugin');
            ctx.body.innerHTML = '<div class="prog-head"><span class="prog-sub">Agit sur la radio de tous les auditeurs.</span>'
                + '<button type="button" class="prog-act prog-foldall">Tout plier</button></div>'
                + '<details class="fold" open><summary class="prog-h">Vient de passer</summary><div class="prog-zone" data-zone="played"></div></details>'
                + '<details class="fold" open><summary class="prog-h">En cours</summary><div class="prog-zone" data-zone="now"></div></details>'
                + '<details class="fold" open><summary class="prog-h">À venir</summary><div class="prog-zone prog-scroll" data-zone="queue"></div></details>'
                + '<details class="fold" open><summary class="prog-h">Playlists et jingles</summary><div class="prog-zone prog-scroll" data-zone="library"></div></details>';
            const zone = name => ctx.body.querySelector('[data-zone="' + name + '"]');
            const foldBtn = ctx.body.querySelector('.prog-foldall');
            const folds = () => Array.from(ctx.body.querySelectorAll('details.fold'));
            const syncFold = () => { foldBtn.textContent = folds().some(d => d.open) ? 'Tout plier' : 'Tout déplier'; };

            function rowHtml(it, src, extra) {
                const isJ = !!it.jingle;
                const sub = (isJ ? 'Jingle' : plName(it.playlist_label)) + (it.duration ? ' - ' + adm.fmtTime(it.duration) : '');
                const badge = extra.explicit ? '<span class="prog-badge">Choisi</span>'
                    : (extra.auto && isJ ? '<span class="prog-badge">Jingle auto</span>' : '');
                const attrs = 'data-src="' + src + '" data-key="' + esc(it.key) + '"' + (extra.qi !== undefined ? ' data-qi="' + extra.qi + '"' : '');
                const removable = src === 'queue' && !(extra.auto && isJ);
                return '<div class="prog-item' + (isJ ? ' is-jingle' : '') + (extra.explicit ? ' is-explicit' : '') + (extra.cls || '') + '" ' + attrs + '>'
                    + '<button type="button" class="prog-main" data-act="next" ' + attrs + '>'
                    + '<span class="prog-title">' + esc(adm.trackTitle(it)) + '</span>'
                    + '<span class="prog-sub">' + esc(sub) + (extra.time ? ' - ' + esc(extra.time) : '') + '</span>' + badge + '</button>'
                    + '<button type="button" class="prog-act" data-act="now" ' + attrs + ' aria-label="Lire juste après" title="Lire juste après">&#9654;</button>'
                    + (removable ? '<button type="button" class="prog-act" data-act="remove" ' + attrs + ' aria-label="Retirer de la file" title="Retirer de la file">&times;</button>' : '')
                    + '</div>';
            }

            function render() {
                if (!visible || ctx.body.hidden) return;
                const live = adm.live() || {};
                const current = adm.current();
                const empty = txt => '<div class="prog-empty">' + txt + '</div>';
                const played = (live.played || []).slice(-8);
                zone('played').innerHTML = played.length
                    ? played.map(p => rowHtml(p, 'played', {time: adm.fmtClock(p.start), cls: ' is-played'})).join('')
                    : empty('Rien de joué avant ce morceau.');
                zone('now').innerHTML = current
                    ? '<div class="prog-item is-now' + (current.jingle ? ' is-jingle' : '') + '"><div class="prog-main">'
                        + '<span class="prog-title">' + esc(current.jingle ? 'Jingle - ' + adm.trackTitle(current) : adm.trackTitle(current)) + '</span>'
                        + '<span class="prog-sub">' + esc(current.jingle ? 'CréaZik IA WebRadio' : plName(current.playlist_label)) + '</span>'
                        + '<span class="prog-badge">En direct</span></div></div>'
                    : empty('Aucun morceau en cours.');
                const queue = live.queue || [];
                const upcoming = live.upcoming || [];
                const rows = [];
                for (let i = 0; i < Math.min(queue.length, upcoming.length); i++) {
                    rows.push(rowHtml(upcoming[i], 'queue', {qi: queue[i].index, explicit: queue[i].explicit, auto: queue[i].auto}));
                }
                zone('queue').innerHTML = rows.length ? rows.join('') : empty('File vide : aucun morceau disponible.');
                zone('library').innerHTML = library.length ? library.map(pl => {
                    const open = openPlaylists.has(pl.id);
                    const b = esc(pl.id);
                    return '<div class="prog-playlist' + (open ? ' open' : '') + '" data-playlist="' + b + '">'
                        + '<div class="prog-pl-head"><button type="button" class="prog-expand" data-act="toggle" data-playlist="' + b + '" aria-expanded="' + open + '">'
                        + '<span class="prog-pl-name">' + esc(plName(pl.label)) + '</span><span class="prog-pl-count">' + pl.tracks.length + '</span></button>'
                        + '<button type="button" class="prog-pl-act" data-act="pl-next" data-playlist="' + b + '">Ensuite</button>'
                        + '<button type="button" class="prog-pl-act" data-act="pl-now" data-playlist="' + b + '">Lire</button></div>'
                        + '<div class="prog-pl-tracks">' + (open ? pl.tracks.map(t => rowHtml(t, 'library', {})).join('') : '') + '</div></div>';
                }).join('') : empty(libraryLoaded ? 'Aucune playlist disponible.' : 'Chargement…');
            }

            async function loadLibrary() {
                const list = await ctx.getJSON('/api/radio/library', []);
                library = (Array.isArray(list) ? list : []).map(pl => ({
                    id: pl.id, label: pl.label,
                    tracks: pl.tracks.map(t => ({key: t.key, name: t.name, playlist_label: pl.label, duration: t.duration, jingle: pl.jingle}))
                }));
                libraryLoaded = true;
                render();
            }

            ctx.body.addEventListener('click', ev => {
                if (ev.target === foldBtn) {
                    const target = !folds().some(d => d.open);
                    folds().forEach(d => { d.open = target; });
                    syncFold();
                    return;
                }
                const btn = ev.target.closest('[data-act]');
                if (!btn) return;
                const act = btn.dataset.act;
                const playlistId = btn.dataset.playlist;
                if (act === 'toggle') {
                    if (openPlaylists.has(playlistId)) openPlaylists.delete(playlistId); else openPlaylists.add(playlistId);
                    render();
                    return;
                }
                if (act === 'pl-next') { adm.radioAction({action: 'playlist_next', id: playlistId}); return; }
                if (act === 'pl-now') { adm.radioAction({action: 'playlist_front', id: playlistId}); return; }
                if (btn.dataset.src === 'queue') {
                    const index = parseInt(btn.dataset.qi, 10);
                    if (act === 'remove') adm.radioAction({action: 'remove', index});
                    else adm.radioAction({action: 'move_front', index});
                    return;
                }
                adm.radioAction({action: act === 'now' ? 'front' : 'next', key: btn.dataset.key});
            });
            folds().forEach(d => d.addEventListener('toggle', syncFold));
            adm.onLive(render);
            adm.onTrack(render);
            this.show = () => {
                visible = true;
                if (!libraryLoaded) loadLibrary();
                render();
            };
        },
        open() {
            if (this.show) this.show();
        }
    });
}());
