(function () {
    'use strict';

    const STORE = 'userSongs';
    const POLL_MS = 3000;
    const KEEP = 10;
    const MAX = 300;
    const STAGES = {lyrics: 'Étape 1 sur 3 : écriture des paroles…', music: 'Étape 2 sur 3 : composition de la musique…',
                    finalize: 'Étape 3 sur 3 : finalisation…'};

    function stateText(it) {
        const st = it.state || {};
        if (it.status === 'queued') {
            if (st.waiting_music) return 'En attente : la carte graphique est occupée par la radio, votre morceau suivra.';
            const ahead = st.ahead || 0;
            return ahead ? 'Dans la file : ' + ahead + ' demande' + (ahead > 1 ? 's' : '') + ' avant la vôtre.' : 'Démarrage imminent.';
        }
        if (it.status === 'running') return STAGES[st.stage] || 'Création en cours…';
        if (it.status === 'ready') {
            const t = st.title ? '« ' + st.title + ' » est prêt. ' : 'Votre morceau est prêt. ';
            return t + (st.scheduled ? 'Votre morceau passe juste après le morceau en cours.' : 'Il sera diffusé dès que possible.');
        }
        if (it.status === 'missing') return 'Demande introuvable.';
        return st.error || 'La création a échoué.';
    }

    window.CreaZik.registerPlugin({
        id: 'song',
        title: 'Créer un morceau',
        init(ctx) {
            const esc = ctx.esc;
            let items = [];
            let timer = null;
            ctx.body.innerHTML = '<p class="plugin-intro">Décrivez la musique que vous voulez entendre : l\'IA locale écrit des paroles en français et compose le morceau. Une fois prêt, il passe à l\'antenne pour tous les auditeurs, juste après le morceau en cours.</p>'
                + '<form class="plugin-form" autocomplete="off">'
                + '<label class="field"><span class="label">Votre description musicale</span>'
                + '<textarea name="prompt" maxlength="' + MAX + '" rows="3" required placeholder="Ex. : un funk joyeux avec une basse slap, une voix de femme, sur un départ en vacances"></textarea></label>'
                + '<span class="plugin-count" aria-hidden="true">0 / ' + MAX + '</span>'
                + '<button type="submit" class="btn-send">Créer le morceau</button>'
                + '<span class="hint" role="status" aria-live="polite"></span>'
                + '</form><ul class="img-list" aria-live="polite"></ul>';
            const form = ctx.body.querySelector('form');
            const area = form.querySelector('textarea');
            const count = form.querySelector('.plugin-count');
            const hint = form.querySelector('.hint');
            const btn = form.querySelector('button');
            const list = ctx.body.querySelector('.img-list');

            function save() {
                try { localStorage.setItem(STORE, JSON.stringify(items.slice(-KEEP))); } catch (e) {}
            }

            function render() {
                list.innerHTML = items.slice().reverse().map(it => {
                    const cls = it.status === 'ready' ? ' is-ready' : (it.status === 'error' || it.status === 'missing' ? ' is-error' : '');
                    return '<li class="img-item song-item' + cls + '"><span class="img-text"><span class="img-prompt">' + esc(it.prompt)
                        + '</span><span class="img-state">' + esc(stateText(it)) + '</span></span></li>';
                }).join('');
            }

            function busy() {
                return items.some(it => it.status === 'queued' || it.status === 'running');
            }

            function schedule() {
                if (timer || !busy()) return;
                timer = setTimeout(poll, POLL_MS);
            }

            async function poll() {
                timer = null;
                for (const it of items.filter(x => x.status === 'queued' || x.status === 'running')) {
                    let st = null;
                    try {
                        const r = await ctx.fetch('/api/songs/' + encodeURIComponent(it.id) + '?t=' + Date.now());
                        if (r.status === 404) st = {status: 'missing'};
                        else if (r.ok) st = await r.json();
                    } catch (e) {}
                    if (!st) continue;
                    it.status = st.status;
                    it.state = st;
                }
                save();
                render();
                schedule();
            }

            form.addEventListener('submit', async ev => {
                ev.preventDefault();
                const prompt = area.value.trim();
                hint.textContent = '';
                hint.classList.remove('error', 'ok');
                if (!prompt) return;
                btn.disabled = true;
                try {
                    const r = await ctx.postJSON('/api/songs', {prompt});
                    const d = await r.json().catch(() => ({}));
                    if (r.ok && d.id) {
                        items.push({id: d.id, prompt, status: d.status, state: d});
                        items = items.slice(-KEEP);
                        save();
                        render();
                        schedule();
                        area.value = '';
                        count.textContent = '0 / ' + MAX;
                        hint.classList.add('ok');
                        hint.textContent = 'Demande envoyée. La création prend plusieurs minutes.';
                    } else {
                        hint.classList.add('error');
                        hint.textContent = d.error || 'Échec de l\'envoi';
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
