(function () {
    'use strict';

    const ORDER = ['slow', 'medium', 'high'];

    window.CreaZik.registerPlugin({
        id: 'dynamique',
        title: 'Dynamique du morceau (Slow / Medium / High)',
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            ctx.body.innerHTML = '<p class="plugin-intro">Votre avis remplace l\'énergie mesurée du morceau en cours dans la dynamique de la journée.</p>'
                + '<p class="dyn-track prog-sub"></p>'
                + '<div class="dyn"><div class="dyn-btns" role="group" aria-label="Dynamique du morceau">'
                + ORDER.map(l => '<button type="button" class="dyn-btn" data-level="' + l + '" aria-pressed="false">' + l.charAt(0).toUpperCase() + l.slice(1) + '</button>').join('')
                + '</div></div><span class="hint" role="status" aria-live="polite"></span>';
            const label = ctx.body.querySelector('.dyn-track');
            const hint = ctx.body.querySelector('.hint');
            const buttons = Array.from(ctx.body.querySelectorAll('.dyn-btn'));

            const dynamics = () => {
                const v = adm.votes();
                if (!v.dynamics) v.dynamics = {};
                return v.dynamics;
            };

            function render() {
                const cur = adm.current();
                const ok = !!cur && !cur.jingle;
                label.textContent = ok ? 'Morceau : ' + adm.trackTitle(cur) : 'Pas de morceau en cours (jingle ou attente).';
                const lvls = ok ? String(dynamics()[cur.key] || '').split('+') : [];
                buttons.forEach(b => {
                    const on = lvls.includes(b.dataset.level);
                    b.disabled = !ok;
                    b.classList.toggle('active', on);
                    b.setAttribute('aria-pressed', on ? 'true' : 'false');
                });
            }

            ctx.body.addEventListener('click', async ev => {
                const b = ev.target.closest('.dyn-btn');
                const cur = adm.current();
                if (!b || !cur || cur.jingle) return;
                const key = cur.key;
                const map = dynamics();
                const prev = map[key];
                const sel = prev ? prev.split('+') : [];
                const level = b.dataset.level;
                let nextSel;
                if (sel.includes(level)) nextSel = sel.filter(l => l !== level);
                else if (sel.length >= 2) nextSel = [level];
                else nextSel = sel.concat(level);
                nextSel.sort((x, y) => ORDER.indexOf(x) - ORDER.indexOf(y));
                const next = nextSel.length ? nextSel.join('+') : 'none';
                if (next === 'none') delete map[key]; else map[key] = next;
                hint.textContent = '';
                render();
                b.blur();
                try {
                    const r = await ctx.postJSON('/api/dynamics', {key, level: next});
                    if (!r.ok) throw new Error(r.status);
                } catch (e) {
                    if (prev) map[key] = prev; else delete map[key];
                    hint.textContent = 'Avis non enregistré.';
                    render();
                }
            });
            adm.onTrack(render);
            render();
        }
    });
}());
