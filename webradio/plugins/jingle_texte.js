(function () {
    'use strict';

    const MAX = 300;
    const POLL_MS = 3000;
    const STORE = 'adminJingles';
    const KEEP = 8;
    const ENGINES = [
        {id: 'kokoro', label: 'Rapide (Kokoro, environ 1 minute)'},
        {id: 'chatterbox', label: 'Voix CréaZik (Chatterbox, environ 5 minutes)'}
    ];

    function stateText(it) {
        if (it.status === 'queued') return it.ahead ? 'En file : ' + it.ahead + ' jingle' + (it.ahead > 1 ? 's' : '') + ' avant celui-ci.' : 'Démarrage imminent.';
        if (it.status === 'running') return 'Synthèse en cours (' + (it.engine === 'chatterbox' ? 'environ 5 minutes' : 'environ 1 minute') + ')…';
        if (it.status === 'ready') {
            if (it.dry_run) return 'Essai sans synthèse : rien n\'est diffusé.';
            const d = it.duration_s ? ' (' + Number(it.duration_s).toFixed(1) + ' s, synthèse ' + Math.round(it.elapsed_s || 0) + ' s)' : '';
            return (it.broadcast ? 'Programmé juste après le morceau en cours' : 'Prêt, non diffusé') + d + '.';
        }
        if (it.status === 'missing') return 'Demande introuvable (serveur relancé ?).';
        return it.error || 'La synthèse a échoué.';
    }

    window.CreaZik.registerPlugin({
        id: 'jingle-texte',
        title: 'Texte vers jingle urgent',
        init(ctx) {
            if (!ctx.admin) return;
            const esc = ctx.esc;
            let items = [];
            let timer = null;
            ctx.body.innerHTML = '<p class="plugin-intro">Le texte devient un jingle parlé diffusé pour tous, juste après le morceau en cours (catégorie Annonces, hors rotation).</p>'
                + '<form class="plugin-form" autocomplete="off">'
                + '<label class="field"><span class="label">Texte du jingle</span>'
                + '<textarea name="text" maxlength="' + MAX + '" rows="3" required placeholder="Ex. : Bienvenue sur CréaZik IA WebRadio, la radio créée par une IA locale."></textarea></label>'
                + '<span class="plugin-count" aria-hidden="true">0 / ' + MAX + '</span>'
                + '<fieldset class="jt-engines"><legend class="label">Voix</legend>'
                + ENGINES.map((e, i) => '<label class="jt-engine"><input type="radio" name="engine" value="' + e.id + '"' + (i === 0 ? ' checked' : '') + '> ' + esc(e.label) + '</label>').join('')
                + '</fieldset>'
                + '<button type="submit" class="btn-send">Diffuser ce jingle</button>'
                + '<span class="hint" role="status" aria-live="polite"></span>'
                + '</form><ul class="img-list jt-list" aria-live="polite"></ul>';
            const form = ctx.body.querySelector('form');
            const area = form.querySelector('textarea');
            const count = form.querySelector('.plugin-count');
            const hint = form.querySelector('.hint');
            const btn = form.querySelector('button[type="submit"]');
            const list = ctx.body.querySelector('.jt-list');

            const busy = () => items.some(it => it.status === 'queued' || it.status === 'running');
            const save = () => {
                try { localStorage.setItem(STORE, JSON.stringify(items.slice(-KEEP))); } catch (e) {}
            };

            function render() {
                list.innerHTML = items.slice().reverse().map(it => {
                    const cls = it.status === 'ready' ? ' is-ready' : (it.status === 'error' || it.status === 'missing' ? ' is-error' : '');
                    return '<li class="img-item' + cls + '"><span class="img-text"><span class="img-prompt">' + esc(it.text) + '</span>'
                        + '<span class="img-state">' + esc((it.engine_label || it.engine) + ' · ' + stateText(it)) + '</span></span></li>';
                }).join('');
            }

            function schedule() {
                if (timer || !busy()) return;
                timer = setTimeout(poll, POLL_MS);
            }

            async function poll() {
                timer = null;
                for (const it of items.filter(x => x.status === 'queued' || x.status === 'running')) {
                    try {
                        const r = await ctx.fetch('/api/admin/jingle/' + encodeURIComponent(it.id) + '?t=' + Date.now());
                        if (r.status === 404) Object.assign(it, {status: 'missing'});
                        else if (r.ok) Object.assign(it, await r.json());
                    } catch (e) {}
                }
                save();
                render();
                schedule();
            }

            form.addEventListener('submit', async ev => {
                ev.preventDefault();
                const text = area.value.trim();
                const engine = (form.querySelector('input[name="engine"]:checked') || {}).value || 'kokoro';
                hint.textContent = '';
                hint.classList.remove('error', 'ok');
                if (!text) return;
                btn.disabled = true;
                try {
                    const r = await ctx.postJSON('/api/admin/jingle', {text, engine});
                    const d = await r.json().catch(() => ({}));
                    if (r.ok && d.id) {
                        items.push(d);
                        items = items.slice(-KEEP);
                        save();
                        render();
                        schedule();
                        area.value = '';
                        count.textContent = '0 / ' + MAX;
                        hint.classList.add('ok');
                        hint.textContent = 'Demande envoyée : le jingle sera programmé juste après le morceau en cours.';
                    } else {
                        hint.classList.add('error');
                        hint.textContent = d.error || 'Échec de l\'envoi (' + r.status + ')';
                    }
                } catch (e) {
                    hint.classList.add('error');
                    hint.textContent = 'Échec de l\'envoi';
                }
                btn.disabled = false;
            });
            area.addEventListener('input', () => { count.textContent = area.value.length + ' / ' + MAX; });

            try { items = JSON.parse(localStorage.getItem(STORE) || '[]').filter(x => x && /^[0-9a-f]{32}$/.test(x.id)); } catch (e) { items = []; }
            render();
            schedule();
        }
    });
}());
