/** Run pinned upstream JSON import logic with avatar output intercepted in memory.
 * Usage: node qa_json_import.cjs characters.js world-info.js node_modules
 * Sources: SillyTavern/SillyTavern@06bde939fb1e9c4c8d8641d810f0a916b5bce127
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const upstreamRequire = createRequire(path.resolve(process.argv[4], 'qa.cjs'));
const root = path.resolve(__dirname, '../..');
const target = path.join(root, 'assembly/card/dist/希灵帝国_最终.json');
const qaPath = path.join(root, 'assembly/card/dist/希灵帝国_装卡QA.json');
const source = fs.readFileSync(process.argv[2], 'utf8');
const worldSource = fs.readFileSync(process.argv[3], 'utf8');
function extract(text, name) {
    const match = text.match(new RegExp(`(?:async )?function ${name}\\(`));
    assert(match, name);
    const end = text.indexOf('\n}', match.index) + 2;
    assert(end > match.index);
    return text.slice(match.index, end);
}
const card = JSON.parse(fs.readFileSync(target, 'utf8'));
let imported;
const context = {
    fs: {
        readFileSync: (p, encoding) => { assert.equal(p, target); return fs.readFileSync(p, encoding); },
        unlinkSync: (p) => assert.equal(p, target),
    },
    console: { info() {}, warn: (...args) => { throw new Error(args.join(' ')); } },
    _: upstreamRequire('lodash'),
    sanitize: upstreamRequire('sanitize-filename'),
    importRisuSprites: () => assert.equal(card.data.extensions.risuai, undefined),
    humanizedDateTime: () => 'QA',
    getPngName: () => '希灵帝国',
    DEFAULT_AVATAR_PATH: 'intercepted-default-avatar',
    writeCharacterData: async (_avatar, metadata) => { imported = JSON.parse(metadata); return true; },
    newWorldInfoEntryTemplate: {},
    world_info_position: { before: 0, after: 1 },
    world_info_logic: { AND_ANY: 0 },
    extension_prompt_roles: { SYSTEM: 0 },
    DEFAULT_DEPTH: 4, DEFAULT_WEIGHT: 100,
};
vm.createContext(context);
vm.runInContext(['unsetPrivateFields', 'readFromV2', 'importFromJson'].map(n => extract(source, n)).join('\n') + '\n' + extract(worldSource, 'convertCharacterBook'), context);
(async () => {
    const result = await context.importFromJson(target, { request: { user: { directories: {} } } });
    assert.equal(result, '希灵帝国');
    assert.equal(imported.name, card.data.name);
    assert.deepEqual(imported.data.character_book, card.data.character_book);
    assert.equal(imported.spec, 'chara_card_v3');
    const converted = context.convertCharacterBook(imported.data.character_book);
    const entries = Object.values(converted.entries);
    assert.equal(entries.length, 335);
    for (const original of card.data.character_book.entries) {
        const actual = converted.entries[original.id];
        assert.equal(actual.content, original.content);
        assert.equal(actual.disable, !original.enabled);
        assert.equal(actual.constant, original.constant);
        assert.deepEqual(actual.key, original.keys);
        assert.equal(actual.position, original.extensions.position);
    }
    const blue10 = entries.find(e => e.comment === '蓝灯｜陈俊第一人称叙事视角');
    assert(blue10 && blue10.constant && !blue10.disable && !blue10.selective);
    assert.deepEqual(entries.filter(e => e.comment.startsWith('时间线｜') && !e.disable).map(e => e.comment), ['时间线｜第一卷（上）｜帝国苏醒与维迪斯']);
    const sourceEntries = card.data.character_book.entries;
    const triggered = sourceEntries.filter(e => /^(绿灯｜|角色｜|能力｜|地点｜)/.test(e.comment));
    assert.equal(triggered.length, 281);
    assert(triggered.every(e => e.extensions.prevent_recursion === true && e.extensions.exclude_recursion === true));
    const timelines = sourceEntries.filter(e => e.comment.startsWith('时间线｜'));
    assert.equal(timelines.length, 26);
    assert(timelines.every(e => (e.content.match(/<world_timeline>/g) || []).length === 1));
    assert(timelines.every(e => !e.content.includes('【第') && !e.content.includes('【制卡插入锚')));
    const report = JSON.parse(fs.readFileSync(qaPath, 'utf8'));
    report.sillytavern_import = {
        result: 'PASS', source_commit: '06bde939fb1e9c4c8d8641d810f0a916b5bce127',
        json_import_routine: true, embedded_world_conversion_entries: entries.length,
        content_and_enabled_flags_preserved: true,
        split_timeline_entries_preserved: true,
        triggered_double_recursion_preserved: true,
        method: 'Executed unmodified upstream importFromJson/readFromV2/unsetPrivateFields/convertCharacterBook bodies. Input is the final JSON. Avatar output is isolated in memory. Android UI test must still be performed after this rebuild.',
    };
    fs.writeFileSync(qaPath, JSON.stringify(report, null, 2) + '\n');
    console.log('SillyTavern JSON import and 335-entry conversion: PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
