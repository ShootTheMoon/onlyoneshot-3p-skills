"""render_video.py 가 뽑아둔 PNG 시퀀스에 자막을 얹어 MP4 로 묶는다 (Blender 불필요).

실행:  python Map\assemble_video.py
왜 Blender VSE 가 아닌가: 이 PC 의 Steam Blender 빌드에는 FFMPEG 출력이 빠져 있다.
"""
import os, glob
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont

ROOT = r'C:\Users\29\Desktop\3y'
OUT = os.path.join(ROOT, 'Map', 'video')
FRAMES = os.path.join(OUT, 'frames')
MP4 = os.path.join(OUT, 'PreviewStage_AllSkills.mp4')
FPS = 30
W, H = 1280, 720
LABELS = [
    ('00_Wakizashi_3P_Idle', '와키자시', '대기'),
    ('01_Wakizashi_3P_Attack1', '와키자시', '일반공격 1타'),
    ('02_Wakizashi_3P_Attack2', '와키자시', '일반공격 2타'),
    ('03_Wakizashi_3P_Attack3', '와키자시', '일반공격 3타'),
    ('04_Wakizashi_3P_BlockIn', '와키자시', '막기 진입'),
    ('05_Wakizashi_3P_BlockHold', '와키자시', '막기 유지'),
    ('06_Wakizashi_3P_BlockOut', '와키자시', '막기 해제'),
    ('07_Wakizashi_3P_KunaiThrow', '와키자시', '쿠나이 투척'),
    ('08_Wakizashi_3P_Teleport', '와키자시', '순간이동'),
    ('09_Wakizashi_3P_Draw', '와키자시', '칼 재장착'),
    ('10_Wakizashi_3P_Ryunochi', '와키자시', '용의 이빨 (궁극기)'),
    ('11_Gukgung_3P_For_OVDR', '국궁', '세로 사격'),
    ('12_Gukgung_3P_HorizontalAttack_For_OVDR', '국궁', '가로 사격'),
]
HOLD = 15   # 클립 끝에서 마지막 포즈를 잡아두는 프레임 수 (0.5 s)
import json
SEG = os.path.join(OUT, 'segments.json')
if os.path.exists(SEG):
    LABELS = [(d['tag'], d['weapon'], d['label'] + ('  (0.5× 슬로우)' if d.get('slow') else ''), d['seconds']) for d in json.load(open(SEG, encoding='utf-8'))]
else:
    LABELS = [(t, w, l, None) for t, w, l in LABELS]
FONT = next(f for f in (r'C:\Windows\Fonts\malgunbd.ttf', r'C:\Windows\Fonts\malgun.ttf') if os.path.exists(f))
big, mid, small = ImageFont.truetype(FONT, 56), ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 34)

def label(img, text_main, text_sub):
    d = ImageDraw.Draw(img, 'RGBA')
    x, y = 36, H - 36
    w = max(d.textlength(text_main, font=small), d.textlength(text_sub, font=mid)) + 40
    d.rectangle((x - 20, y - 96, x + w, y + 6), fill=(0, 0, 0, 140))
    d.text((x, y - 90), text_main, font=small, fill=(255, 255, 255))
    d.text((x, y - 46), text_sub, font=mid, fill=(215, 215, 215))

writer = imageio.get_writer(MP4, fps=FPS, codec='libx264', quality=8, pixelformat='yuv420p', macro_block_size=8)
# 타이틀 카드 1.5 s
card = Image.new('RGB', (W, H), (13, 13, 15))
d = ImageDraw.Draw(card)
d.text((80, 280), '3인칭 스킬 애니메이션 미리보기', font=big, fill=(245, 245, 245))
d.text((82, 360), '와키자시 11 클립  ·  국궁 2 클립  ·  무대 PreviewStage', font=mid, fill=(170, 170, 170))
import numpy as np
for _ in range(int(FPS * 1.5)):
    writer.append_data(np.asarray(card))
total = 0
for i, (tag, weapon, name, seconds) in enumerate(LABELS):
    files = sorted(glob.glob(os.path.join(FRAMES, tag + '_*.png')))
    n = len(files)
    secs = seconds if seconds is not None else n / FPS
    for f in files + [files[-1]] * HOLD:
        img = Image.open(f).convert('RGB')
        label(img, f'{weapon}  ·  {name}', f'{i + 1:02d} / {len(LABELS)}     클립 {secs:.2f} s')
        writer.append_data(np.asarray(img))
    total += n + HOLD
    print(f'[video] {tag}: {n} frames')
writer.close()
print(f'[video] done: {MP4}  {total} frames = {total / FPS:.1f}s  {os.path.getsize(MP4) / 1e6:.1f} MB')
