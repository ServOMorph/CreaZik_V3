(function () {
    'use strict';

    const STORE = 'userImages';
    const POLL_MS = 3000;
    const KEEP = 10;
    const JINGLE = '/jingles/systeme/image_prete.mp3';
    const MAX = 300;

    function stateText(it) {
        const st = it.state || {};
        if (it.status === 'queued') {
            if (st.waiting_music) return 'En attente : la radio compose un morceau, votre image suivra.';
            const ahead = st.ahead || 0;
            return ahead ? 'Dans la file : ' + ahead + ' demande' + (ahead > 1 ? 's' : '') + ' avant la vôtre.' : 'Démarrage imminent.';
        }
        if (it.status === 'running') return 'Création en cours…';
        if (it.status === 'ready') return 'Prête : affichée pendant le morceau.';
        if (it.status === 'missing') return 'Demande introuvable.';
        return st.error || 'La création a échoué.';
    }

    window.CreaZik.registerPlugin({
        id: 'image',
        title: 'Créer une image',
        init(ctx) {
            const esc = ctx.esc;
            let items = [];
            let timer = null;
            let pending = null;
            ctx.body.innerHTML = '<p class="plugin-intro">Décrivez une image : l\'IA locale la dessine pour vous seul. Une fois prête, elle s\'affiche pendant le morceau en cours.</p>'
                + '<form class="plugin-form" autocomplete="off">'
                + '<label class="field"><span class="label">Votre description</span>'
                + '<textarea name="prompt" maxlength="' + MAX + '" rows="3" required placeholder="Ex. : un phare sous une pluie d\'étoiles, style aquarelle"></textarea></label>'
                + '<span class="plugin-count" aria-hidden="true">0 / ' + MAX + '</span>'
                + '<button type="submit" class="btn-send">Créer l\'image</button>'
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
                    const thumb = it.status === 'ready' ? '<img class="img-thumb" alt="" src="/user_images/' + esc(it.id) + '.png">' : '<span class="img-thumb" aria-hidden="true"></span>';
                    return '<li class="img-item' + cls + '">' + thumb + '<span class="img-text"><span class="img-prompt">' + esc(it.prompt)
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

            function onReady(src) {
                const pre = new Image();
                const go = () => {
                    pending = src;
                    if (ctx.notifyBusy()) return;
                    ctx.playNotify(JINGLE, () => {
                        const s = pending;
                        pending = null;
                        if (s) ctx.showImage(s);
                    });
                };
                pre.onload = go;
                pre.onerror = go;
                pre.src = src;
            }

            async function poll() {
                timer = null;
                for (const it of items.filter(x => x.status === 'queued' || x.status === 'running')) {
                    let st = null;
                    try {
                        const r = await ctx.fetch('/api/images/' + encodeURIComponent(it.id) + '?t=' + Date.now());
                        if (r.status === 404) st = {status: 'missing'};
                        else if (r.ok) st = await r.json();
                    } catch (e) {}
                    if (!st) continue;
                    it.status = st.status;
                    it.state = st;
                    if (st.status === 'ready') onReady(st.image || '/user_images/' + it.id + '.png');
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
                ctx.unlockAudio();
                btn.disabled = true;
                try {
                    const r = await ctx.postJSON('/api/images', {prompt});
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
                        hint.textContent = 'Demande envoyée.';
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
