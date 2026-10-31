(function () {
    'use strict';

    window.CreaZik.registerPlugin({
        id: 'tests',
        title: 'Tests',
        init(ctx) {
            const adm = ctx.admin;
            if (!adm) return;
            const esc = ctx.esc;
            const $ = id => document.getElementById(id);
            ctx.body.innerHTML = '<div id="testsList" class="prog-zone prog-scroll"></div>';
            const box = ctx.body.querySelector('#testsList');
            const testAudio = new Audio();
            let testing = false;

            function stopTest() {
                testing = false;
                testAudio.pause();
                renderTests();
            }

            let testsItems = [];
            let testsCur = '';

            const TEST_ICONS = {
                up: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 11v10H3V11z"/><path d="M7 11l4-8a2.5 2.5 0 0 1 2.5 2.8L13 9h6.2a2 2 0 0 1 2 2.3l-1.3 8a2 2 0 0 1-2 1.7H7"/></svg>',
                down: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 13V3h4v10z"/><path d="M17 13l-4 8a2.5 2.5 0 0 1-2.5-2.8L11 15H4.8a2 2 0 0 1-2-2.3l1.3-8A2 2 0 0 1 6.100 3H17"/></svg>',
                note: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
                del: '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/></svg>'
            };

            function testSeekMax() {
                const d = testAudio.duration;
                if (isFinite(d) && d > 0) return d;
                const it = testsItems.find(x => x.file === testsCur);
                return it && it.duration ? Number(it.duration) : 0;
            }

            function updateTestSeek() {
                const range = $('testSeek');
                const label = $('testTime');
                if (!range || !label) return;
                const d = testSeekMax();
                if (!range.matches(':active')) range.value = d ? Math.round(testAudio.currentTime / d * 1000) : 0;
                label.textContent = adm.fmtTime(testAudio.currentTime) + ' / ' + adm.fmtTime(d);
            }

            let testsFolder = '';
            let testsEditing = '';
            const testsOpen = new Set();
            let testsDraft = '';

            function testsFolders() {
                const map = new Map();
                testsItems.forEach(it => {
                    const id = it.folder || 'divers';
                    let f = map.get(id);
                    if (!f) { f = {id, label: it.folder_label || 'Divers', items: [], fresh: 0, todo: 0, last: ''}; map.set(id, f); }
                    f.items.push(it);
                    if (it.planned) f.todo++; else if (!it.played) f.fresh++;
                    if (String(it.generated_at || '') > f.last) f.last = String(it.generated_at || '');
                });
                return Array.from(map.values()).sort((x, y) => (y.fresh > 0) - (x.fresh > 0) || y.last.localeCompare(x.last));
            }

            function renderTests() {
                if (!box) return;
                if (!testsItems.length) {
                    box.innerHTML = '<div class="prog-empty">Aucune version de test.</div>';
                    return;
                }
                const folders = testsFolders();
                const open = folders.find(f => f.id === testsFolder);
                if (!open) {
                    testsFolder = '';
                    box.innerHTML = folders.map(f => `<div class="prog-item test-folder${f.fresh ? ' is-new' : ''}">
                        <button type="button" class="prog-main" data-act="open" data-folder="${esc(f.id)}">
                            <span class="prog-title">&#128193; ${esc(f.label)}</span>
                            <span class="prog-sub">${f.items.length} version${f.items.length > 1 ? 's' : ''}${f.todo ? ' · ' + f.todo + ' &agrave; faire' : ''}</span>
                            ${f.fresh ? `<span class="prog-badge">${f.fresh} jamais &eacute;cout&eacute;${f.fresh > 1 ? 's' : ''}</span>` : ''}
                        </button>
                    </div>`).join('');
                    return;
                }
                const head = `<div class="prog-item test-folder-head">
                    <button type="button" class="prog-main" data-act="back">
                        <span class="prog-title">&#8592; Dossiers</span>
                        <span class="prog-sub">${esc(open.label)}${open.fresh ? ' · ' + open.fresh + ' jamais &eacute;cout&eacute;' + (open.fresh > 1 ? 's' : '') : ''}</span>
                    </button>
                </div><div class="test-foldall"><button type="button" class="prog-act test-save" data-act="foldall" data-folder="${esc(open.id)}">Tout d&eacute;plier</button><button type="button" class="prog-act test-save" data-act="unfoldall" data-folder="${esc(open.id)}">Tout replier</button></div>`;
                box.innerHTML = head + open.items.map(it => {
                    const cur = it.file === testsCur;
                    const f = esc(it.file);
                    const planned = !!it.planned;
                    const act = (a, label, icon, short) => `<button type="button" class="prog-act test-act" data-act="${a}" data-file="${f}" aria-label="${label}" title="${label}"${a === 'up' || a === 'down' ? ` aria-pressed="${it.vote === a}"` : ''}>${icon}<span class="test-act-l">${short || label}</span></button>`;
                    const generated = it.generated_at ? new Date(it.generated_at).toLocaleString('fr-FR') : '';
                    const provenance = [it.model, generated].filter(Boolean).join(' · ');
                    const quality = it.technical_status === 'pass_needs_listening' ? 'Contrôle technique réussi — écoute requise' : it.technical_status === 'invalid' ? 'Contrôle technique invalide' : '';
                    const title = esc(String(it.name).replace(/_/g, ' '));
                    const isOpen = testsOpen.has(it.file) || testsEditing === it.file;
                    const badge = planned ? '<span class="prog-badge">&Agrave; faire</span>' : it.played ? '' : '<span class="prog-badge">Jamais &eacute;cout&eacute;</span>';
                    const headInner = `<span class="prog-title">${planned ? '&#128221; ' : cur && testing ? '&#9646;&#9646; ' : '&#9654; '}${title}</span>${badge}`;
                    const main = planned
                        ? `<button type="button" class="prog-main test-main" data-act="fold" data-file="${f}" aria-expanded="${isOpen}">${headInner}</button>`
                        : `<button type="button" class="prog-main test-main" data-act="play" data-file="${f}">${headInner}</button>`;
                    const fold = `<button type="button" class="prog-act test-fold" data-act="fold" data-file="${f}" aria-expanded="${isOpen}" aria-label="${isOpen ? 'Replier' : 'D&eacute;plier'}" title="${isOpen ? 'Replier' : 'D&eacute;plier'}">${isOpen ? '&#9650;' : '&#9660;'}</button>`;
                    const actions = planned
                        ? act('comment', 'Commentaire', TEST_ICONS.note, 'R&eacute;pondre') + act('delete', 'Supprimer ce test', TEST_ICONS.del, 'Supprimer')
                        : act('up', "J'aime", TEST_ICONS.up, "J'aime") + act('down', "Je n'aime pas", TEST_ICONS.down, 'Pas aim&eacute;') + act('comment', 'Commentaire', TEST_ICONS.note, 'Commentaire') + act('delete', 'Supprimer cette version', TEST_ICONS.del, 'Supprimer');
                    const details = isOpen ? `<div class="test-details">
                            ${provenance ? `<span class="prog-sub">${esc(provenance)}</span>` : ''}
                            ${quality ? `<span class="prog-sub">${esc(quality)}</span>` : ''}
                            ${it.description ? `<span class="test-desc">${esc(it.description)}</span>` : ''}
                            ${it.prompt ? `<span class="prog-sub test-prompt"><b>Caption :</b> ${esc(it.prompt)}</span>` : ''}
                            ${it.comment && testsEditing !== it.file ? `<div class="test-comment">${esc(it.comment)}</div>` : ''}
                            ${testsEditing === it.file ? `<div class="test-edit"><textarea id="testNote" maxlength="2000" rows="3" placeholder="${planned ? 'Votre réponse sur ce test' : 'Votre avis sur ce morceau'}">${esc(testsDraft)}</textarea><button type="button" class="prog-act test-save" data-act="save" data-file="${f}">Enregistrer</button><button type="button" class="prog-act test-save" data-act="cancel" data-file="${f}">Annuler</button></div>` : ''}
                        </div>
                        <div class="test-actions">${actions}</div>` : '';
                    return `<div class="prog-item test-item${cur ? ' is-now' : ''}${planned ? ' is-planned' : it.played ? '' : ' is-new'}">
                        <div class="test-head">${main}${fold}</div>
                        ${cur ? '<div class="test-seek"><input id="testSeek" type="range" min="0" max="1000" step="1" value="0" aria-label="Position dans le morceau"><span id="testTime" class="time">0:00 / 0:00</span></div>' : ''}
                        ${details}
                    </div>`;
                }).join('');
                updateTestSeek();
            }

            async function loadTests() {
                const d = await ctx.getJSON('/api/tests', null);
                if (!d || !Array.isArray(d.items)) return;
                const num = f => parseInt((f.split('/').pop().match(/^(\d+)/) || [0, 0])[1], 10);
                testsItems = d.items.slice().sort((a, b) => String(b.generated_at || '').localeCompare(String(a.generated_at || '')) || num(b.file) - num(a.file));
                renderTests();
            }

            async function testsPost(path, body) {
                try {
                    const r = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
                    return r.ok;
                } catch (e) {
                    return false;
                }
            }

            function markTestPlayed(file) {
                const it = testsItems.find(x => x.file === file);
                if (!it || it.played) return;
                it.played = true;
                testsPost('/api/tests/played', {file});
            }

            async function playTestFile(item) {
                if (adm.isListening()) adm.stopListening();
                if (testsCur !== item.file) {
                    testAudio.src = '/' + item.file + '?v=' + encodeURIComponent(item.generated_at || '');
                    testsCur = item.file;
                }
                try {
                    await testAudio.play();
                    testing = true;
                    markTestPlayed(item.file);
                } catch (e) {
                    testing = false;
                }
                renderTests();
            }

            async function onTestsClick(ev) {
                const btn = ev.target.closest('button[data-act]');
                if (!btn) return;
                if (btn.dataset.act === 'open' || btn.dataset.act === 'back') {
                    testsFolder = btn.dataset.act === 'open' ? btn.dataset.folder : '';
                    renderTests();
                    return;
                }
                if (btn.dataset.act === 'foldall' || btn.dataset.act === 'unfoldall') {
                    const fo = testsFolders().find(x => x.id === btn.dataset.folder);
                    if (fo) fo.items.forEach(x => { if (btn.dataset.act === 'foldall') testsOpen.add(x.file); else testsOpen.delete(x.file); });
                    renderTests();
                    return;
                }
                const item = testsItems.find(x => x.file === btn.dataset.file);
                if (!item) return;
                const act = btn.dataset.act;
                if (act === 'fold') {
                    if (testsOpen.has(item.file)) testsOpen.delete(item.file); else testsOpen.add(item.file);
                    renderTests();
                    return;
                }
                if (act === 'play') {
                    if (testsCur === item.file && testing) stopTest(); else playTestFile(item);
                } else if (act === 'up' || act === 'down') {
                    const vote = item.vote === act ? 'none' : act;
                    if (await testsPost('/api/tests/vote', {file: item.file, vote})) {
                        item.vote = vote === 'none' ? '' : vote;
                        renderTests();
                    }
                } else if (act === 'comment') {
                    testsOpen.add(item.file);
                    testsEditing = testsEditing === item.file ? '' : item.file;
                    testsDraft = item.comment || '';
                    renderTests();
                    const ta = $('testNote');
                    if (ta) ta.focus();
                } else if (act === 'cancel') {
                    testsEditing = '';
                    renderTests();
                } else if (act === 'save') {
                    const ta = $('testNote');
                    const text = ta ? ta.value.trim() : '';
                    if (await testsPost('/api/tests/comment', {file: item.file, text})) {
                        item.comment = text;
                        testsEditing = '';
                        renderTests();
                    }
                } else if (act === 'delete') {
                    if (!confirm('Supprimer définitivement cette version de test ?')) return;
                    if (await testsPost('/api/tests/delete', {file: item.file})) {
                        if (testsCur === item.file) {
                            testing = false;
                            testAudio.pause();
                            testAudio.removeAttribute('src');
                            testsCur = '';
                        }
                        await loadTests();
                    }
                }
            }

            testAudio.addEventListener('ended', stopTest);
            testAudio.addEventListener('timeupdate', updateTestSeek);
            testAudio.addEventListener('loadedmetadata', updateTestSeek);
            box.addEventListener('click', onTestsClick);
            box.addEventListener('input', ev => {
                if (ev.target.id !== 'testSeek') return;
                const d = testSeekMax();
                if (d) testAudio.currentTime = Number(ev.target.value) / 1000 * d;
            });
            adm.onListen(() => { if (testing) stopTest(); });
            box.innerHTML = '<div class="prog-empty">Chargement…</div>';
            this.load = loadTests;
        },
        open() {
            if (this.load) this.load();
        }
    });
}());
