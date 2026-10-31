(function () {
    'use strict';

    const LABEL = {run: 'En cours', wait: 'En attente', done: 'Fait', ko: 'Bloqué'};
    const STORE = 'suiviOpen';

    window.CreaZik.registerPlugin({
        id: 'suivi',
        title: 'Suivi du travail',
        init(ctx) {
            if (!ctx.admin) return;
            const esc = ctx.esc;
            let saved = {};
            try { saved = JSON.parse(localStorage.getItem(STORE) || '{}') || {}; } catch (e) { saved = {}; }
            let last = '';
            let timer = null;
            ctx.body.innerHTML = '<p class="suivi-maj prog-sub">Chargement…</p>'
                + '<div class="tools-row"><button type="button" class="btn-next btn-discover" data-act="open">Tout déplier</button>'
                + '<button type="button" class="btn-next btn-discover" data-act="close">Tout replier</button></div>'
                + '<div class="suivi-root"></div>';
            const maj = ctx.body.querySelector('.suivi-maj');
            const root = ctx.body.querySelector('.suivi-root');
            const isOpen = s => (s.nom in saved ? saved[s.nom] : s.nom !== "Fait aujourd'hui");
            const remember = () => {
                root.querySelectorAll('details.suivi-sec').forEach(d => { saved[d.dataset.nom] = d.open; });
                try { localStorage.setItem(STORE, JSON.stringify(saved)); } catch (e) {}
            };

            function render(data) {
                root.innerHTML = (data.sections || []).map(s => {
                    const items = Array.isArray(s.items) ? s.items : [];
                    return '<details class="fold suivi-sec" data-nom="' + esc(s.nom) + '"' + (isOpen(s) ? ' open' : '') + '>'
                        + '<summary class="prog-h">' + esc(s.nom) + ' <span class="suivi-n">' + items.length + '</span></summary><div class="prog-zone">'
                        + (items.length ? items.map(it => '<div class="suivi-item" data-statut="' + esc(it.statut) + '">'
                            + '<div class="suivi-top"><span class="suivi-titre">' + esc(it.titre) + '</span><span class="suivi-badge">' + esc(LABEL[it.statut] || it.statut) + '</span></div>'
                            + '<div class="prog-sub">' + esc(it.qui) + '</div>'
                            + ((it.detail || []).length ? '<ul class="suivi-detail">' + it.detail.map(d => '<li>' + esc(d) + '</li>').join('') + '</ul>' : '')
                            + '</div>').join('') : '<p class="prog-empty">Rien</p>')
                        + '</div></details>';
                }).join('');
                root.querySelectorAll('details.suivi-sec').forEach(d => d.addEventListener('toggle', remember));
            }

            async function load() {
                if (ctx.body.hidden || document.hidden) return;
                try {
                    const r = await ctx.fetch('/api/suivi?t=' + Date.now(), {cache: 'no-store'});
                    if (!r.ok) throw new Error(r.status);
                    const data = await r.json();
                    const sig = JSON.stringify(data);
                    if (sig !== last) {
                        last = sig;
                        render(data);
                    }
                    maj.textContent = 'Mis à jour le ' + (data.maj || '?') + ' · en direct';
                } catch (e) {
                    maj.textContent = 'Serveur injoignable, nouvel essai dans 10 s';
                }
            }

            ctx.body.addEventListener('click', ev => {
                const b = ev.target.closest('[data-act]');
                if (!b) return;
                root.querySelectorAll('details.suivi-sec').forEach(d => { d.open = b.dataset.act === 'open'; });
            });
            this.start = () => {
                load();
                if (!timer) timer = setInterval(load, 10000);
            };
        },
        open() {
            if (this.start) this.start();
        }
    });
}());
