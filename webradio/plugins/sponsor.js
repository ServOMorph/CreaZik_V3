(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'sponsor',
        title: 'Lien partenaire',
        init(ctx) {
            const sp = ctx.profile && ctx.profile.sponsor;
            if (!sp || !/^https:\/\//.test(String(sp.url || ''))) return;
            const p = document.createElement('p');
            p.className = 'human-text';
            if (sp.text) p.appendChild(document.createTextNode(sp.text + ' '));
            const a = document.createElement('a');
            a.href = sp.url;
            a.target = '_blank';
            a.rel = 'noopener';
            a.textContent = sp.link_text || sp.name;
            p.appendChild(a);
            p.appendChild(document.createTextNode('.'));
            ctx.body.appendChild(p);
        }
    });
}());
