"""Package the frozen generated book and approved cover; never rebuild lore."""
from pathlib import Path
import base64, copy, hashlib, json, struct, zlib
from collections import Counter
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT / 'assembly/worldbook/dist/希灵帝国_character_book.json'
COVER = ROOT / 'assembly/card/media/希灵帝国_正式封面.png'
OUT = ROOT / 'assembly/card/dist'

def chunks(raw):
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    p = 8
    while p < len(raw):
        n = struct.unpack('>I', raw[p:p+4])[0]
        kind, data = raw[p+4:p+8], raw[p+8:p+8+n]
        end = p + n + 12
        assert zlib.crc32(kind + data) & 0xffffffff == struct.unpack('>I', raw[end-4:end])[0]
        yield kind, data, raw[p:end]
        p = end
    assert p == len(raw)

def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    book = json.loads(BOOK.read_text())
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
        creator_notes='正式无MVU角色卡。完整嵌入318条世界书（304正文+14分区标记），默认仅第一卷时间线启用。切换剧情卷时仅启用当前卷。封面采用最终确认的《希灵帝国：混乱的全家福》，封装不更改图像像素。',
        system_prompt='',
        post_history_instructions='正文始终遵守蓝灯「陈俊第一人称叙事视角」。每次将当前叙事正文放入<story_scene>...</story_scene>，以供世界书场景触发；随后输出简短的<status>块，包含「当前时间:」「当前位置:」「当前卷:」，位置写当前实际地点的正式名称。以上为文本标签，不引入变量、脚本或MVU。遵守当前启用卷的知识与能力边界。',
        alternate_greetings=[], tags=['希灵帝国','世界角色卡','无MVU'],
        creator='多娜多娜', character_version='1.0.0',
        extensions={'talkativeness':0.5,'fav':False}, character_book=book,
        assets=[], nickname='', creator_notes_multilingual={}, source=[], group_only_greetings=[])
    card = {'spec':'chara_card_v3','spec_version':'3.0','data':data}
    target_json = OUT / '希灵帝国_最终.json'
    target_png = OUT / '希灵帝国_最终.png'
    target_json.write_text(json.dumps(card, ensure_ascii=False, indent=2)+'\n')
    v2 = copy.deepcopy(card)
    v2['spec'], v2['spec_version'] = 'chara_card_v2','2.0'
    raw = COVER.read_bytes()
    parts = []
    for kind, payload, full in chunks(raw):
        if kind == b'tEXt' and payload.split(b'\0',1)[0].lower() in (b'chara',b'ccv3'):
            continue
        if kind == b'IEND':
            for keyword, value in [(b'chara',v2),(b'ccv3',card)]:
                encoded = base64.b64encode(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode())
                parts.append(chunk(b'tEXt',keyword+b'\0'+encoded))
        parts.append(full)
    target_png.write_bytes(raw[:8]+b''.join(parts))
    decoded = {}
    for kind, payload, _ in chunks(target_png.read_bytes()):
        if kind == b'tEXt':
            key, value = payload.split(b'\0',1)
            if key in (b'chara',b'ccv3'):
                decoded[key.decode()] = json.loads(base64.b64decode(value))
    assert decoded['ccv3'] == json.loads(target_json.read_text())
    assert decoded['chara']['data'] == card['data']
    assert card['data']['character_book'] == json.loads(BOOK.read_text())
    assert [(k,d) for k,d,_ in chunks(raw) if k in (b'IHDR',b'IDAT',b'IEND')] == [(k,d) for k,d,_ in chunks(target_png.read_bytes()) if k in (b'IHDR',b'IDAT',b'IEND')]
    with Image.open(COVER) as a, Image.open(target_png) as b:
        a.load(); b.load()
        assert a.size == b.size and a.mode == b.mode and a.tobytes() == b.tobytes()
        dimensions = a.size
    report = {'result':'PASS','entries':318,'counts':dict(counts),'BLUE10':'constant=true / enabled=true / selective=false','timeline_enabled':[e['comment'] for e in timelines if e['enabled']],'mvu':False,'embedded_book_exact_equal':True,'json_png_v3_exact_equal':True,'v2_v3_data_exact_equal':True,'cover_pixels_identical':True,'cover_image_chunks_identical':True,'cover_dimensions':dimensions,'cover_sha256':hashlib.sha256(raw).hexdigest(),'worldbook_sha256':hashlib.sha256(BOOK.read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target_json,target_png)},'real_android_test':'NOT_RUN'}
    (OUT / '希灵帝国_装卡QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__':
    main()
