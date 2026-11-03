"""Assemble JSON only from the frozen generated worldbook; never rebuild lore."""
from pathlib import Path
import hashlib, json
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / 'assembly/worldbook/dist/希灵帝国_character_book.json'
OUT = ROOT / 'assembly/card/dist'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    book = json.loads(BOOK.read_text(encoding='utf-8'))
    entries = book['entries']
    counts = Counter(e['comment'].split('｜')[0] for e in entries)
    assert len(entries) == 318
    for kind, count in [('蓝灯',10),('绿灯',59),('角色',84),('能力',84),('时间线',13),('地点',54)]:
        assert counts[kind] == count, (kind, counts[kind])
    blue = [e for e in entries if e['comment'].startswith('蓝灯｜')]
    assert all(e['constant'] and e['enabled'] and not e['selective'] for e in blue)
    assert sum(e['comment'] == '蓝灯｜陈俊第一人称叙事视角' for e in blue) == 1
    timelines = [e for e in entries if e['comment'].startswith('时间线｜')]
    assert [e['comment'] for e in timelines if e['enabled']] == ['时间线｜第一卷｜帝国苏醒与维迪斯']
    data = dict(
        name='希灵帝国',
        description='<角色卡运行说明>\n这是《希灵帝国》的世界角色卡。人物、能力、设定、地点及剧情进程以嵌入世界书为依据。正文叙述者固定为陈俊，以第一人称“我”展开，只叙述当前可知的信息。{{user}}的身份与行动遵循玩家设定和实际输入，不擅自替玩家决定。\n</角色卡运行说明>',
        personality='',
        scenario='默认从第一卷《帝国苏醒与维迪斯》起步。遵循当前启用卷的事件顺序与知识边界，后期人物、能力和真相不得提前倒灌。',
        first_mes='<story_scene>\n灰色的废墟又一次出现在梦里。\n\n我抬起头，望向那片陌生的天空。三颗巨大的天体悬在那里，熟悉得让我心里发毛——这个梦，我已经不是第一次做了。\n\n等我睁开眼，眼前又成了熟悉的房间。\n\n我盯着天花板缓了半天，才慢慢坐起来。今天是周一。要是再不起来，等着我的恐怕就不是什么神秘梦境，而是迟到。\n</story_scene>\n<status>\n当前时间: 2010年11月22日\n当前位置: K市·陈俊家\n当前卷: 第一卷｜帝国苏醒与维迪斯\n</status>',
        mes_example='',
        creator_notes='正式无MVU角色卡。完整嵌入318条世界书（304正文+14分区标记），默认仅第一卷时间线启用。切换剧情卷时仅启用当前卷。本次仅交付JSON；用户可自行配合正式封面制作PNG。',
        system_prompt='',
        post_history_instructions='正文始终遵守蓝灯「陈俊第一人称叙事视角」。每次将当前叙事正文放入<story_scene>...</story_scene>，以供世界书场景触发；随后输出简短的<status>块，包含「当前时间:」「当前位置:」「当前卷:」，位置写当前实际地点的正式名称。以上为文本标签，不引入变量、脚本或MVU。遵守当前启用卷的知识与能力边界。',
        alternate_greetings=[], tags=['希灵帝国','世界角色卡','无MVU'],
        creator='多娜多娜', character_version='1.0.0',
        extensions={'talkativeness':0.5,'fav':False}, character_book=book,
        assets=[], nickname='', creator_notes_multilingual={}, source=[], group_only_greetings=[])
    card = {'spec':'chara_card_v3','spec_version':'3.0','data':data}
    target_json = OUT / '希灵帝国_最终.json'
    target_json.write_text(json.dumps(card, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    parsed = json.loads(target_json.read_text(encoding='utf-8'))
    assert parsed == card
    assert parsed['spec'] == 'chara_card_v3' and parsed['spec_version'] == '3.0'
    required_strings = ('name', 'description', 'personality', 'scenario', 'first_mes',
                        'mes_example', 'creator_notes', 'system_prompt',
                        'post_history_instructions', 'creator', 'character_version')
    assert all(isinstance(parsed['data'][key], str) for key in required_strings)
    for key in ('tags', 'alternate_greetings', 'group_only_greetings', 'source'):
        assert isinstance(data[key], list) and all(isinstance(v, str) for v in data[key])
    assert isinstance(data['extensions'], dict)
    assert data['assets'] == []
    assert set(data['extensions']) == {'talkativeness', 'fav'}
    assert parsed['data']['character_book'] == json.loads(BOOK.read_text(encoding='utf-8'))
    assert len({e['id'] for e in entries}) == len(entries)
    for entry in entries:
        assert isinstance(entry['content'], str)
        assert isinstance(entry['keys'], list) and all(isinstance(k, str) for k in entry['keys'])
        assert isinstance(entry['enabled'], bool)
        assert isinstance(entry['insertion_order'], (int, float))
        assert isinstance(entry['extensions'], dict)
    report = {
        'result': 'PASS', 'delivery_format': 'JSON_ONLY',
        'json_parse': 'PASS', 'character_card_v3_structure': 'PASS',
        'entries': len(entries), 'counts': dict(counts),
        'formal_entries': sum(counts[k] for k in ('蓝灯', '绿灯', '角色', '能力', '时间线', '地点')),
        'section_markers': sum(v for k, v in counts.items() if k.startswith('【')),
        'BLUE10': 'constant=true / enabled=true / selective=false',
        'timeline_enabled': [e['comment'] for e in timelines if e['enabled']],
        'mvu': False, 'embedded_book_exact_equal': True,
        'worldbook_sha256': hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        'files': {target_json.name: hashlib.sha256(target_json.read_bytes()).hexdigest()},
        'real_android_test': 'NOT_RUN',
    }
    (OUT / '希灵帝国_装卡QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__':
    main()
