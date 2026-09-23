"""리그(몸+무기) + 클립 전부를 FBX 한 개로 내보낸다.

클립을 따로 임포트하면 파일마다 스켈레톤이 새로 생겨서 리그에 안 물린다.
한 파일에 담으면 전부 같은 스켈레톤을 쓴다.
"""
import bpy, sys, json, os
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
outpath, cfg = argv[0], json.loads(argv[1])

sc = bpy.context.scene
arm = bpy.data.objects['Armature']
GEO = ['Head_Geo', 'LeftArm_Geo', 'LeftLeg_Geo', 'RightArm_Geo', 'RightLeg_Geo', 'Torso_Geo']
geo = [bpy.data.objects[n] for n in GEO if n in bpy.data.objects]
# ODA Rig 인식용 (2026-09-18 임포트 창 경고 대응):
#  - 가중치 없는 끝본(Nub/001) 삭제 + 그 본의 F커브 제거 (F커브가 남으면 exporter 가 액션을 통째로 버린다)
#  - 아마추어 스케일 0.01 적용 + location F커브 ×100 (적용은 액션을 안 건드려서 직접 보정)
def channelbags(act):
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                yield cb
ren = cfg.get('rename_bones', {})
if ren:
    for b in arm.data.bones:
        if b.name in ren: b.name = ren[b.name]
    for act in bpy.data.actions:
        for cb in channelbags(act):
            for fc in cb.fcurves:
                for o, n in ren.items():
                    if ('pose.bones["%s"]' % o) in fc.data_path: fc.data_path = fc.data_path.replace('pose.bones["%s"]' % o, 'pose.bones["%s"]' % n)
# ODA NPC 스켈레톤과 동일하게: 본 추가/이동 (좌표는 아마추어 로컬 cm, Blender Z-up).
add = cfg.get('add_bones', []); move = cfg.get('move_bones', {})
if add or move:
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    for n, h in move.items():
        if n in eb:
            b = eb[n]; b.head = Vector(h); b.tail = Vector(h) + Vector((0, 0, 5))
    for spec in add:
        b = eb.new(spec['name']); b.head = Vector(spec['head']); b.tail = Vector(spec['head']) + Vector(spec.get('dir', (0, 0, 5)))
        b.parent = eb[spec['parent']]; b.use_deform = False
    bpy.ops.object.mode_set(mode='OBJECT')
drop = set(cfg.get('drop_bones', []))
if drop:
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in list(arm.data.edit_bones):
        if eb.name in drop: arm.data.edit_bones.remove(eb)
    bpy.ops.object.mode_set(mode='OBJECT')
    for act in bpy.data.actions:
        for cb in channelbags(act):
            for fc in list(cb.fcurves):
                if any(('pose.bones["%s"]' % b) in fc.data_path for b in drop): cb.fcurves.remove(fc)
# --- 1) 무기가 쥐어진 프레임에서 모양과 손 위치를 기록해둔다 ---
arm.animation_data_create()
arm.animation_data.action = bpy.data.actions[cfg['pose_action']]
sc.frame_set(int(cfg['frame']))
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

snaps = []
for obj_name, export_name in cfg['weapons']:
    src = bpy.data.objects.get(obj_name)
    if src is None:
        continue
    ev = src.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    me.transform(src.matrix_world)      # 월드 좌표로 구움
    me.name = export_name
    bone = cfg.get('bones', {}).get(obj_name)
    if bone not in arm.pose.bones:
        bone = 'RightHand'
    pb = arm.pose.bones[bone]
    snaps.append({"mesh": me, "name": export_name, "bone": bone,
                  "pose_world": (arm.matrix_world @ pb.matrix).copy()})

# --- 2) 포즈를 레스트로 완전히 되돌린다 ---
#     액션만 떼면 포즈 본이 마지막 자세를 들고 있어서 바인드가 그 자세로 굳는다.
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix()
bpy.context.view_layer.update()

# --- 3) 레스트 상태에서 무기를 손 본에 묶는다 ---
report = []
made = []
for s in snaps:
    dup = bpy.data.objects.new(s["name"], s["mesh"])
    sc.collection.objects.link(dup)
    rest_world = arm.matrix_world @ arm.pose.bones[s["bone"]].bone.matrix_local
    dup.matrix_world = rest_world @ s["pose_world"].inverted()
    for vg in list(dup.vertex_groups):
        dup.vertex_groups.remove(vg)
    g = dup.vertex_groups.new(name=s["bone"])
    g.add(list(range(len(s["mesh"].vertices))), 1.0, 'REPLACE')
    mod = dup.modifiers.new('Rig', 'ARMATURE')
    mod.object = arm
    dup.parent = arm
    dup.matrix_parent_inverse = arm.matrix_world.inverted()
    made.append(dup)
    report.append({"as": s["name"], "bone": s["bone"], "verts": len(s["mesh"].vertices)})

# --- 4) 메시 하나로 합친다 (임포터가 파일당 메시 1개만 받는다) ---
bpy.ops.object.select_all(action='DESELECT')
target = geo[0]
for o in geo + made:
    o.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.object.join()
target.name = cfg['mesh_name']
target.data.name = target.name

# --- 5) 재질 색을 텍스처 한 장으로 굽는다 (메시 1개 = 재질 1개라서) ---
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.005)
bpy.ops.object.mode_set(mode='OBJECT')

size = int(cfg.get('bake_size', 1024))
img = bpy.data.images.new(target.name + '_BaseColor', width=size, height=size)
for slot in target.material_slots:
    m = slot.material
    if not m:
        continue
    m.use_nodes = True
    node = m.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = img
    node.select = True
    m.node_tree.nodes.active = node
sc.render.engine = 'CYCLES'
sc.cycles.samples = 1
sc.render.bake.use_pass_direct = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.margin = 8
bpy.ops.object.bake(type='DIFFUSE')
png = os.path.splitext(outpath)[0] + '_BaseColor.png'
img.filepath_raw = png
img.file_format = 'PNG'
img.save()
mat = bpy.data.materials.new(target.name + '_Mat')
mat.use_nodes = True
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = img
mat.node_tree.links.new(mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'], tex.outputs['Color'])
target.data.materials.clear()
target.data.materials.append(mat)

# --- 6) 내보낼 클립만 남기고 나머지 액션은 전부 버린다 ---
#     use_all_actions 는 남아있는 액션을 전부 테이크로 굽는다. 무기용 오브젝트 액션까지
#     섞이면 쓰레기 테이크가 잔뜩 생긴다.
keep = set(cfg['clips'])
dropped = 0
for a in list(bpy.data.actions):
    if a.name not in keep:
        bpy.data.actions.remove(a)
        dropped += 1
left = sorted(a.name for a in bpy.data.actions)

if cfg.get('apply_scale'):
    # 아마추어 스케일(0.01)을 적용하고, 메시 정점을 아마추어 공간(m)으로 직접 다시 구워 넣는다.
    # (ops 로 자식까지 적용하면 parent_inverse 에 0.01 이 남아 FBX 에서 메시가 100배 커진다 — 2026-09-18)
    k = arm.scale.x
    W = target.matrix_world.copy()
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    target.data.transform(arm.matrix_world.inverted() @ W)
    target.matrix_parent_inverse = Matrix(); target.matrix_basis = Matrix()
    for act in bpy.data.actions:
        for cb in channelbags(act):
            for fc in cb.fcurves:
                if fc.data_path.endswith('.location'):
                    for kp in fc.keyframe_points:
                        kp.co[1] *= k; kp.handle_left[1] *= k; kp.handle_right[1] *= k
    bpy.context.view_layer.update()

bpy.ops.object.select_all(action='DESELECT')
for o in [arm, target]:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=outpath, use_selection=True, object_types={'ARMATURE', 'MESH'},
    global_scale=cfg.get('global_scale', 1), apply_unit_scale=True, apply_scale_options=cfg.get('scale_opt', 'FBX_SCALE_ALL'),
    axis_forward=cfg.get('axis_forward', '-Z'), axis_up=cfg.get('axis_up', 'Y'), bake_space_transform=cfg.get('bake_space', False), add_leaf_bones=False,
    use_armature_deform_only=False,
    bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0,
    path_mode='COPY', embed_textures=True, use_custom_props=False)

print("BUNDLE_JSON " + json.dumps({"file": outpath, "bytes": os.path.getsize(outpath),
                                  "mesh": target.name, "texture": png,
                                  "actions_kept": left, "actions_dropped": dropped,
                                  "weapons": report}))
