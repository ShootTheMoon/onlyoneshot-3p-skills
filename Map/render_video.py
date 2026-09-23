r"""무대 위에서 3인칭 스킬 클립 13개를 차례로 렌더해 MP4 한 편으로 묶는다.

실행:  blender -b Map\PreviewStage.blend -P Map\render_video.py
산출:  Map\video\PreviewStage_AllSkills.mp4  (+ frames\ 아래 PNG 시퀀스)
"""
import bpy, os, math, glob, time
from mathutils import Vector

ROOT = r'C:\Users\29\Desktop\3y'
OUT = os.path.join(ROOT, 'Map', 'video')
FRAMES = os.path.join(OUT, 'frames')
os.makedirs(FRAMES, exist_ok=True)
W = os.path.join(ROOT, 'Wakizashi_Skills')
CLIPS = [  # (file, 무기, 라벨)
    (W + r'\Wakizashi_3P_Idle.fbx',       '와키자시', '대기'),
    (W + r'\Wakizashi_3P_Attack1.fbx',    '와키자시', '일반공격 1타'),
    (W + r'\Wakizashi_3P_Attack2.fbx',    '와키자시', '일반공격 2타'),
    (W + r'\Wakizashi_3P_Attack3.fbx',    '와키자시', '일반공격 3타'),
    (W + r'\Wakizashi_3P_BlockIn.fbx',    '와키자시', '막기 진입'),
    (W + r'\Wakizashi_3P_BlockHold.fbx',  '와키자시', '막기 유지'),
    (W + r'\Wakizashi_3P_BlockOut.fbx',   '와키자시', '막기 해제'),
    (W + r'\Wakizashi_3P_KunaiThrow.fbx', '와키자시', '쿠나이 투척'),
    (W + r'\Wakizashi_3P_Teleport.fbx',   '와키자시', '순간이동'),
    (W + r'\Wakizashi_3P_Draw.fbx',       '와키자시', '칼 재장착'),
    (W + r'\Wakizashi_3P_Ryunochi.fbx',   '와키자시', '용의 이빨 (궁극기)'),
    (ROOT + r'\Gukgung_3P_For_OVDR.fbx',                  '국궁', '세로 사격'),
    (ROOT + r'\Gukgung_3P_HorizontalAttack_For_OVDR.fbx', '국궁', '가로 사격'),
]
FPS = 30
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.render.resolution_percentage = 100
sc.render.engine = 'BLENDER_EEVEE'
sc.eevee.taa_render_samples = 16
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGB'
bpy.data.collections['HERO_REF'].hide_render = True
cam = bpy.data.objects['CAM_preview']
cam.animation_data_clear()
sc.camera = cam

CAM_START_DEG = -12     # 클립 시작 각도 (0 = 정면, 음수 = 캐릭터 오른쪽 앞)
CAM_DEG_PER_SEC = 6     # 카메라 각속도. 짧은 클립은 거의 안 움직인다
SLOW_UNDER_SEC = 1.0    # 이보다 짧은 클립은 0.5배 슬로우로 렌더

def orbit(f, s, e, seconds):
    t = 0 if e == s else (f - s) / (e - s)
    a1 = min(18, CAM_START_DEG + CAM_DEG_PER_SEC * seconds)
    a = math.radians(-90 + CAM_START_DEG + (a1 - CAM_START_DEG) * t)
    return (4.8 * math.cos(a), 4.8 * math.sin(a), 1.6)

segments = []
t0 = time.time()
for idx, (path, weapon, label) in enumerate(CLIPS):
    before = set(bpy.data.objects); acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    acts = [a for a in bpy.data.actions if a not in acts_before]
    rng = [a.frame_range for a in acts]
    s = int(min(r[0] for r in rng)); e = int(max(r[1] for r in rng))
    seconds = (e - s + 1) / FPS
    slow = seconds < SLOW_UNDER_SEC
    sc.render.frame_map_old, sc.render.frame_map_new = 100, (200 if slow else 100)
    sc.frame_start, sc.frame_end = (s * 2, e * 2) if slow else (s, e)
    cam.animation_data_clear()
    for f, (x, y, z) in ((s, orbit(s, s, e, seconds)), (e, orbit(e, s, e, seconds))):
        cam.location = (x, y, z); cam.keyframe_insert('location', frame=f)
    tag = f'{idx:02d}_{os.path.splitext(os.path.basename(path))[0]}'
    for old in glob.glob(os.path.join(FRAMES, tag + '_*.png')): os.remove(old)
    sc.render.filepath = os.path.join(FRAMES, tag + '_')
    bpy.ops.render.render(animation=True)
    files = sorted(glob.glob(os.path.join(FRAMES, tag + '_*.png')))
    segments.append({'tag': tag, 'weapon': weapon, 'label': label, 'seconds': seconds, 'slow': slow, 'frames': len(files)})
    print(f'[video] {tag}: {len(files)} frames  ({time.time()-t0:.0f}s elapsed)')
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    for a in acts: bpy.data.actions.remove(a)
import json
json.dump(segments, open(os.path.join(OUT, 'segments.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- MP4 조립은 assemble_video.py (일반 파이썬) 가 맡는다. 이 Blender 빌드엔 FFMPEG 출력이 없다.
import subprocess, sys
subprocess.run(['python', os.path.join(ROOT, 'Map', 'assemble_video.py')], check=True)
