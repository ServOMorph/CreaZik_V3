(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'pochettes',
        title: 'Pochettes',
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            const esc = ctx.esc;
            let coversData = null;
            let coversBusy = false;
            let timer = null;
            ctx.body.innerHTML = '<div class="prog-zone cov-box"><div class="prog-empty">Chargement…</div></div>';
            const box = ctx.body.querySelector('.cov-box');

            function coversTodo() {
                const items = (coversData && coversData.items) || [];
                return items.map((x, i) => ({x, i})).filter(o => o.x.status === 'pending')
                    .sort((a, b) => a.x.redo_count - b.x.redo_count || a.i - b.i).map(o => o.x);
            }

            function renderCovers() {
                if (!coversData) return;
                const c = coversData.counts || {};
                const todo = coversTodo();
                const stats = '<div class="cov-stats"><span>À relire : <b>' + todo.length + '</b></span><span>Validées : <b>' + (c.validated || 0)
                    + '</b></span><span>À régénérer : <b>' + (c.redo || 0) + '</b></span><span>Abandonnées : <b>' + (c.abandoned || 0) + '</b></span></div>';
                const cur = todo[0];
                if (!cur) {
                    box.innerHTML = stats + '<p class="cov-empty">' + (c.redo ? 'Toutes les pochettes restantes attendent leur régénération.' : 'Aucune pochette à relire.') + '</p>';
                    return;
                }
                const again = cur.redo_count ? ' · refaite ' + cur.redo_count + '/' + cur.max_redo + ' fois' : '';
                box.innerHTML = stats + '<figure class="cov-fig"><img class="cov-img" src="' + esc(cur.url) + '" alt="Pochette de ' + esc(cur.title) + '">'
                    + '<figcaption><strong>' + esc(cur.title) + '</strong><span>' + esc(cur.playlist_label) + again + '</span></figcaption></figure>'
                    + '<div class="cov-actions"><button type="button" class="cov-btn cov-ok" data-verdict="validated" data-key="' + esc(cur.key) + '">Valider</button>'
                    + '<button type="button" class="cov-btn cov-redo" data-verdict="redo" data-key="' + esc(cur.key) + '">À refaire</button></div>';
                if (todo[1]) new Image().src = todo[1].url;
            }

            async function loadCovers() {
                if (coversBusy) return;
                const d = await ctx.getJSON('/api/covers/review', null);
                if (!d || !Array.isArray(d.items)) {
                    if (!coversData) box.innerHTML = '<div class="prog-empty">Pochettes indisponibles.</div>';
                    return;
                }
                coversData = d;
                renderCovers();
            }

            async function coversVerdict(key, verdict) {
                coversBusy = true;
                try {
                    const r = await ctx.postJSON('/api/covers/verdict', {key, verdict});
                    if (r.ok) {
                        const res = await r.json();
                        const it = coversData.items.find(x => x.key === key);
                        if (it && res.status) {
                            const c = coversData.counts;
                            c[it.status] = Math.max(0, (c[it.status] || 0) - 1);
                            it.status = res.status;
                            c[res.status] = (c[res.status] || 0) + 1;
                        }
                    }
                } catch (e) {
                } finally {
                    coversBusy = false;
                }
                renderCovers();
            }

            box.addEventListener('click', ev => {
                const btn = ev.target.closest('button[data-verdict]');
                if (!btn || coversBusy) return;
                coversVerdict(btn.dataset.key, btn.dataset.verdict);
            });
            this.start = () => {
                loadCovers();
                if (!timer) timer = setInterval(() => { if (!ctx.body.hidden && !coversBusy && !document.hidden) loadCovers(); }, 20000);
            };
        },
        open() {
            if (this.start) this.start();
        }
    });
}());
