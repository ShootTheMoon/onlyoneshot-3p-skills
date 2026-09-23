r"""13개 클립의 본 로컬 변환(pose matrix_basis, 레스트 대비 오프셋)을 30fps 로 구워 Lua 테이블로 낸다.
실행: blender -b -P Map\bake_bones.py     산출: Map\bones\<clip>.lua, bones\SkillPreviewBones.lua(전체)
엔진 Bone.Transform 이 로블록스식(레스트 기준 로컬 오프셋)이라는 가정. 축은 블렌더 본 로컬 그대로 → 안 맞으면 여기서 변환.
"""
import bpy, os, json, math
ROOT = r'C:\Users\29\Desktop\3y'; OUT = os.path.join(ROOT, 'Map', 'bones'); os.makedirs(OUT, exist_ok=True)
W = os.path.join(ROOT, 'Wakizashi_Skills')
CLIPS = {
 'Wakizashi_Idle': W+r'\Wakizashi_3P_Idle.fbx', 'Wakizashi_Attack1': W+r'\Wakizashi_3P_Attack1.fbx', 'Wakizashi_Attack2': W+r'\Wakizashi_3P_Attack2.fbx',
 'Wakizashi_Attack3': W+r'\Wakizashi_3P_Attack3.fbx', 'Wakizashi_BlockIn': W+r'\Wakizashi_3P_BlockIn.fbx', 'Wakizashi_BlockHold': W+r'\Wakizashi_3P_BlockHold.fbx',
 'Wakizashi_BlockOut': W+r'\Wakizashi_3P_BlockOut.fbx', 'Wakizashi_KunaiThrow': W+r'\Wakizashi_3P_KunaiThrow.fbx', 'Wakizashi_Teleport': W+r'\Wakizashi_3P_Teleport.fbx',
 'Wakizashi_Draw': W+r'\Wakizashi_3P_Draw.fbx', 'Wakizashi_Ryunochi': W+r'\Wakizashi_3P_Ryunochi.fbx',
 'Gukgung_DrawRelease': ROOT+r'\Gukgung_3P_For_OVDR.fbx', 'Gukgung_HorizontalAttack': ROOT+r'\Gukgung_3P_HorizontalAttack_For_OVDR.fbx',
}
BONES = ['Root','LowerTorso','UpperTorso01','UpperTorso02','RightUpperArm','RightLowerArm','RightHand','LeftUpperArm','LeftLowerArm','LeftHand','Head','LeftUpperLeg','LeftLowerLeg','LeftFoot','RightUpperLeg','RightLowerLeg','RightFoot']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = 30
def f3(v): return '%.3f' % v
out = ['-- bake_bones.py 산출물. Bone.Transform 용 본 로컬 오프셋 (cm, 쿼터니언 x y z w). 30 fps.', 'return {']
for key, path in CLIPS.items():
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    act = arm.animation_data.action; s, e = int(act.frame_range[0]), int(act.frame_range[1])
    names = {b.name: b for b in arm.pose.bones}
    present = [b for b in BONES if b in names]
    lines = ['\t%s = { fps = 30, bones = {%s}, frames = {' % (key, ','.join('"%s"' % b for b in present))]
    for f in range(s, e + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        row = []
        for b in present:
            m = names[b].matrix_basis; t = m.to_translation() * 100; q = m.to_quaternion()
            row.append('{%s,%s,%s,%s,%s,%s,%s}' % (f3(t.x), f3(t.y), f3(t.z), f3(q.x), f3(q.y), f3(q.z), f3(q.w)))
        lines.append('\t\t{' + ','.join(row) + '},')
    lines.append('\t}},')
    out += lines
    print('[bones]', key, len(present), 'bones', e - s + 1, 'frames', 'missing:', [b for b in BONES if b not in names])
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
out.append('}')
open(os.path.join(OUT, 'SkillPreviewBones.lua'), 'w', encoding='utf-8').write('\n'.join(out))
print('[bones] done', os.path.getsize(os.path.join(OUT, 'SkillPreviewBones.lua')))
