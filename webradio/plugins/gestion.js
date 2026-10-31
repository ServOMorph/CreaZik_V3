(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'gestion',
        title: 'Gestion WebRadio',
        init(ctx) {
            if (!ctx.admin) return;
            ctx.body.innerHTML = '<p class="plugin-intro">Page de gestion complète (9 sections), chargée à l\'ouverture.</p>'
                + '<iframe class="admin-frame" title="Gestion WebRadio"></iframe>';
            const frame = ctx.body.querySelector('iframe');
            let ro = null;
            const fit = () => {
                const d = frame.contentDocument;
                if (d && d.body) frame.style.height = Math.max(200, Math.ceil(d.body.getBoundingClientRect().height)) + 'px';
            };
            frame.addEventListener('load', () => {
                const d = frame.contentDocument;
                if (ro) ro.disconnect();
                if (d && d.body && window.ResizeObserver) {
                    d.documentElement.style.overflow = 'hidden';
                    d.body.style.minHeight = '0';
                    ro = new ResizeObserver(fit);
                    ro.observe(d.body);
                }
                fit();
            });
            this.load = () => {
                if (!frame.getAttribute('src')) frame.src = '/radio.html';
            };
        },
        open() {
            if (this.load) this.load();
        }
    });
}());
