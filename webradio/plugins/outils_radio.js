(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'outils-radio',
        title: 'Outils radio',
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            ctx.body.innerHTML = '<p class="plugin-intro">Découverte et Test changent la programmation pour tous les auditeurs.</p>'
                + '<div class="tools-row">'
                + '<button type="button" class="btn-next btn-discover" data-act="discover" aria-pressed="false">Découverte</button>'
                + '<button type="button" class="btn-next btn-discover" data-act="test" aria-pressed="false">Test</button>'
                + '</div><p class="prog-sub tools-note"></p>'
                + '<div class="tools-row">'
                + '<button type="button" class="btn-next btn-discover" data-act="unfold">Tout déplier</button>'
                + '<button type="button" class="btn-next btn-discover" data-act="fold">Tout plier</button>'
                + '</div>';
            const btn = act => ctx.body.querySelector('[data-act="' + act + '"]');
            const note = ctx.body.querySelector('.tools-note');

            function render() {
                const live = adm.live() || {};
                const disc = !!live.unrated_only;
                const test = !!live.test_loop;
                btn('discover').setAttribute('aria-pressed', String(disc));
                btn('discover').textContent = disc ? 'Désactiver découverte' : 'Découverte';
                btn('test').setAttribute('aria-pressed', String(test));
                btn('test').textContent = test ? 'Arrêter le test' : 'Test';
                note.textContent = [disc ? 'Découverte active : morceaux sans avis seulement.' : '',
                                    test ? 'Test actif : seule la playlist de test passe.' : ''].filter(Boolean).join(' ');
            }

            function foldAll(open) {
                const own = ctx.body.closest('.plugin');
                document.querySelectorAll('#pluginList .plugin-toggle').forEach(t => {
                    if ((t.getAttribute('aria-expanded') === 'true') !== open && t.closest('.plugin') !== own) t.click();
                });
            }

            ctx.body.addEventListener('click', ev => {
                const b = ev.target.closest('[data-act]');
                if (!b) return;
                const live = adm.live() || {};
                const act = b.dataset.act;
                if (act === 'discover') adm.radioAction({action: 'unrated', on: !live.unrated_only});
                else if (act === 'test') adm.radioAction({action: 'test_loop', on: !live.test_loop});
                else foldAll(act === 'unfold');
            });
            adm.onLive(render);
            render();
        }
    });
}());
