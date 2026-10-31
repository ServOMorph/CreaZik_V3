(function () {
    'use strict';

    const LIST_LEN = 50;

    window.CreaZik.registerPlugin({
        id: 'styles',
        title: 'Choisir mes styles',
        init(ctx) {
            let styles = [];
            const chosen = new Set();
            ctx.setVisible(false);
            ctx.body.innerHTML = '<div class="styles-list" data-role="list"></div>'
                + '<div class="controls"><button class="btn-next" data-role="play" type="button" disabled>Écouter ma sélection</button></div>';
            const box = ctx.body.querySelector('[data-role="list"]');
            const btn = ctx.body.querySelector('[data-role="play"]');

            function render() {
                ctx.setVisible(styles.length > 0);
                box.innerHTML = styles.map(s => '<button type="button" class="style-chip" data-id="' + ctx.esc(s.id) + '" aria-pressed="'
                    + chosen.has(s.id) + '">' + ctx.esc(ctx.plName(s.label)) + '</button>').join('');
                btn.disabled = !chosen.size;
            }

            function pool(ids) {
                const out = styles.filter(s => ids.has(s.id)).flatMap(s => s.tracks || []);
                for (let i = out.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [out[i], out[j]] = [out[j], out[i]];
                }
                return out.slice(0, LIST_LEN);
            }

            box.addEventListener('click', ev => {
                const chip = ev.target.closest('.style-chip');
                if (!chip) return;
                const id = chip.dataset.id;
                if (chosen.has(id)) chosen.delete(id); else chosen.add(id);
                render();
            });
            btn.addEventListener('click', () => {
                if (!chosen.size) return;
                const ids = new Set(chosen);
                ctx.playList(pool(ids), () => pool(ids));
            });
            ctx.getJSON('/api/radio/styles', []).then(list => {
                styles = Array.isArray(list) ? list : [];
                render();
            });
        }
    });
}());
