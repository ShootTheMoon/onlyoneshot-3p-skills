import bpy, sys, json, os
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
outpath, cfg = argv[0], json.loads(argv[1])
# cfg = {"pose_action": str, "frame": int, "weapons": [[obj_name, export_name], ...]}

sc = bpy.context.scene
arm = bpy.data.objects['Armature']
GEO = ['Head_Geo', 'LeftArm_Geo', 'LeftLeg_Geo', 'RightArm_Geo', 'RightLeg_Geo', 'Torso_Geo']
geo = [bpy.data.objects[n] for n in GEO if n in bpy.data.objects]

# 1) 무기가 제대로 쥐어진 한 프레임으로 맞춘다.
arm.animation_data_create()
arm.animation_data.action = bpy.data.actions[cfg['pose_action']]
sc.frame_set(int(cfg['frame']))
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

def nearest_bone(points):
    """붙잡는 지점 기준으로 고른다. 칼 무게중심으로 재면 날 한가운데가 위팔에 더 가까워
    엉뚱한 본에 묶인다. 그래서 '메시에서 그 본에 가장 가까운 점' 으로 잰다."""
    best, best_d = None, None
    for pb in arm.pose.bones:
        head = arm.matrix_world @ pb.head
        tail = arm.matrix_world @ pb.tail
        seg = tail - head
        L2 = seg.dot(seg)
        near = None
        for p in points:
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, (p - head).dot(seg) / L2))
            d = (p - (head + seg * t)).length
            if near is None or d < near:
                near = d
        if best_d is None or near < best_d:
            best, best_d = pb, near
    return best, best_d

report = []
made = []
for obj_name, export_name in cfg['weapons']:
    src = bpy.data.objects.get(obj_name)
    if src is None:
        report.append({"object": obj_name, "status": "missing"})
        continue
    # 2) 그 프레임의 변형된 모양을 그대로 굳힌다 (활시위처럼 리그로 휜 것 포함).
    ev = src.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, depsgraph=dg)
    me.transform(src.matrix_world)          # 월드 좌표로 구움
    me.name = export_name  # 데이터블록 이름도 맞춘다. 안 그러면 임포트 때 Kunai.001 이 된다
    dup = bpy.data.objects.new(export_name, me)
    sc.collection.objects.link(dup)

    step = max(1, len(me.vertices) // 400)  # 400점만 훑어도 충분하다
    pts = [Vector(me.vertices[i].co) for i in range(0, len(me.vertices), step)]
    want = cfg.get('bones', {}).get(obj_name)
    if want and want in arm.pose.bones:
        pb, dist = arm.pose.bones[want], -1.0  # 손에 쥔 무기는 지정한 본이 맞다
    else:
        pb, dist = nearest_bone(pts)

    # 3) 레스트 자세에서의 위치로 옮겨놓고 그 본에 통째로 묶는다.
    pose_world = arm.matrix_world @ pb.matrix
    rest_world = arm.matrix_world @ pb.bone.matrix_local
    dup.matrix_world = rest_world @ pose_world.inverted()

    # 원본 무기가 쓰던 버텍스 그룹(WeaponRig 용)이 딸려온다. 합칠 때 이름이 충돌하므로 버린다.
    for vg in list(dup.vertex_groups):
        dup.vertex_groups.remove(vg)
    g = dup.vertex_groups.new(name=pb.name)
    g.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    mod = dup.modifiers.new('Rig', 'ARMATURE')
    mod.object = arm
    dup.parent = arm
    dup.matrix_parent_inverse = arm.matrix_world.inverted()
    made.append(dup)
    report.append({"object": obj_name, "as": export_name, "bone": pb.name,
                   "distance_cm": round(dist * 100, 1), "verts": len(me.vertices)})

# 4) 메시를 하나로 합친다. 오버데어 임포터는 파일당 메시 1개만 받는다.
#    버텍스 그룹은 이름 기준으로 합쳐지므로 스킨 웨이트는 그대로 살아남는다.
#    ★ 액션만 떼면 포즈 본은 마지막 자세를 그대로 들고 있는다. 그 상태로 내보내면
#    바인드 자세가 '무기 쥔 포즈' 로 굳어, 클립을 얹는 순간 포즈가 두 번 먹어 관절이 벌어진다.
#    그래서 포즈를 명시적으로 지우고 레스트로 되돌린다.
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix()
    pb.location = (0.0, 0.0, 0.0)
    pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    pb.rotation_euler = (0.0, 0.0, 0.0)
    pb.scale = (1.0, 1.0, 1.0)
sc.frame_set(1)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
target = geo[0]
for o in geo + made:
    o.select_set(True)
bpy.context.view_layer.objects.active = target
bpy.ops.object.join()
target.name = cfg.get('mesh_name', 'Preview3P')
target.data.name = target.name

# 5) 재질 색을 텍스처 한 장으로 굽는다.
#    오버데어는 메시 1개 = 재질 1개라, 합치는 순간 칼날/황동/천 구분이 전부 날아간다.
#    UV 를 새로 펴고 디퓨즈 색만 베이크하면 한 장으로 그 구분이 살아난다.
bake_info = None
if cfg.get('bake', True):
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
    sc.cycles.use_denoising = False
    sc.render.bake.use_pass_direct = False
    sc.render.bake.use_pass_indirect = False
    sc.render.bake.margin = 8
    bpy.ops.object.bake(type='DIFFUSE')

    png = os.path.splitext(outpath)[0] + '_BaseColor.png'
    img.filepath_raw = png
    img.file_format = 'PNG'
    img.save()

    # 구운 텍스처 한 장만 쓰는 재질로 갈아끼운다
    mat = bpy.data.materials.new(target.name + '_Mat')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])
    target.data.materials.clear()
    target.data.materials.append(mat)
    bake_info = {"image": png, "size": size}

bpy.ops.object.select_all(action='DESELECT')
for o in [arm, target]:
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(filepath=outpath, use_selection=True, object_types={'ARMATURE', 'MESH'},
    global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Z', axis_up='Y', bake_space_transform=False, add_leaf_bones=False,
    use_armature_deform_only=False, bake_anim=False,
    path_mode='COPY', embed_textures=True, use_custom_props=False)

print("RIG_JSON " + json.dumps({"file": outpath, "bytes": os.path.getsize(outpath),
                               "mesh": target.name, "bake": bake_info, "groups": sorted(g.name for g in target.vertex_groups),
                               "weapons": report}))
