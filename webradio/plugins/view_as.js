(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'view-as',
        title: 'Voir comme un profil',
        init(ctx) {
            const s = ctx.session || {};
            if (s.role !== 'admin') return;
            const esc = ctx.esc;
            const current = s.view_as || '';
            const options = [{id: '', label: 'Admin (tous les plugins)'}].concat(s.profiles || []);
            ctx.body.className = 'view-as';
            ctx.body.innerHTML = '<label class="view-as-field"><span class="view-as-label">Voir comme</span>'
                + '<select class="view-as-select" aria-label="Voir la page comme le profil">'
                + options.map(p => '<option value="' + esc(p.id) + '"' + (p.id === current ? ' selected' : '') + '>' + esc(p.label) + '</option>').join('')
                + '</select></label>'
                + '<span class="view-as-hint" role="status" aria-live="polite"></span>';
            const select = ctx.body.querySelector('select');
            const hint = ctx.body.querySelector('.view-as-hint');
            select.addEventListener('change', async () => {
                select.disabled = true;
                hint.textContent = '';
                try {
                    const r = await ctx.postJSON('/api/session/view-as', {profile: select.value});
                    if (r.ok) {
                        location.reload();
                        return;
                    }
                    hint.textContent = 'Changement refusé (' + r.status + ')';
                } catch (e) {
                    hint.textContent = 'Changement impossible';
                }
                select.value = current;
                select.disabled = false;
            });
        }
    });
}());
