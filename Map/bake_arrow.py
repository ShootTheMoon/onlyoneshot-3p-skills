r"""국궁 3P 클립의 화살(Gukgung_3P_Arrow, WeaponRig 'Arrow' 본) 궤적을 모델 로컬 좌표(cm, 엔진 축)로 굽는다.
블렌더 (x,y,z) → 리그 모델 로컬 (−x, z, y)·100  (FBX 가 Y축 180° 돌아 들어오는 규칙, HANDOFF 함정 참고)
산출: Map/bones/arrow_track.lua  — SkillPreviewConfig.C.ArrowTrack 에 붙여 넣는다.
"""
import bpy
from mathutils import Vector
sc = bpy.context.scene
def setact(o, name):
    act = bpy.data.actions[name]; ad = o.animation_data or o.animation_data_create(); ad.action = act
    try: ad.action_slot = act.slots[0]
    except Exception: pass
arm = bpy.data.objects['Armature']; wr = bpy.data.objects['Gukgung_WeaponRig']
def conv(v): return (-v.x * 100, v.z * 100, v.y * 100)
out = ['-- bake_arrow.py 산출. 프레임별 {x,y,z, dx,dy,dz} (리그 모델 로컬 cm, 방향 = 화살 본 축). 30 fps.']
for body, weap, key in (('Gukgung_3P_DrawRelease', 'Gukgung_Weapon_DrawRelease', 'Gukgung_DrawRelease'), ('Gukgung_3P_HorizontalAttack', 'Gukgung_Weapon_HorizontalAttack', 'Gukgung_HorizontalAttack')):
    setact(arm, body); setact(wr, weap)
    act = bpy.data.actions[body]; s, e = int(act.frame_range[0]), int(act.frame_range[1])
    rows = []
    for f in range(s, e + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        m = wr.matrix_world @ wr.pose.bones['Arrow'].matrix
        p = conv(m.translation); d = conv(m.col[1].to_3d().normalized())  # 본 Y축 = 화살 방향
        rows.append('{%.1f,%.1f,%.1f,%.3f,%.3f,%.3f}' % (p + d))
    out.append('%s = { fps = 30, frames = {\n\t%s\n} },' % (key, ',\n\t'.join(rows)))
    print('[arrow]', key, s, e, 'first', rows[0], 'last', rows[-1])
open(r'C:\Users\29\Desktop\3y\Map\bones\arrow_track.lua', 'w', encoding='utf-8').write('\n'.join(out))
