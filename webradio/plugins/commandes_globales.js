(function () {
    'use strict';

    function prevKey(played) {
        const list = Array.isArray(played) ? played : [];
        for (let i = list.length - 1; i >= 0; i--) {
            const it = list[i];
            if (it && !it.jingle && typeof it.key === 'string' && it.key) return it.key;
        }
        return null;
    }

    window.CreaZik.registerPlugin({
        id: 'commandes-globales',
        title: 'Commandes globales (tous les auditeurs)',
        prevKey,
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            ctx.body.className = 'global-ctl';
            ctx.body.innerHTML = '<p class="global-label">Radio pour tous les auditeurs</p>'
                + '<div class="global-btns">'
                + '<button type="button" class="btn-global" data-act="prev" aria-label="Précédent pour tous les auditeurs">&#9198; Précédent (tous)</button>'
                + '<button type="button" class="btn-global" data-act="next" aria-label="Suivant pour tous les auditeurs">Suivant (tous) &#9197;</button>'
                + '</div><span class="global-hint" role="status" aria-live="polite"></span>';
            const hint = ctx.body.querySelector('.global-hint');
            const btns = Array.from(ctx.body.querySelectorAll('.btn-global'));
            ctx.body.addEventListener('click', async ev => {
                const btn = ev.target.closest('.btn-global');
                if (!btn || btn.disabled) return;
                hint.textContent = '';
                let body;
                if (btn.dataset.act === 'prev') {
                    const key = prevKey(adm.live().played);
                    if (!key) {
                        hint.textContent = 'Aucun morceau précédent.';
                        return;
                    }
                    body = {action: 'now', key};
                } else {
                    body = {action: 'skip'};
                }
                btns.forEach(b => { b.disabled = true; });
                const ok = await adm.radioAction(body);
                hint.textContent = ok ? '' : 'Action refusée par le serveur.';
                setTimeout(() => btns.forEach(b => { b.disabled = false; }), 800);
            });
        }
    });
}());
