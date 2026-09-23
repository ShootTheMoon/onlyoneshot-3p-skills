r"""무대를 그룹별 FBX 여러 개로 내보낸다 (오버데어 30k tri/메시 제한, 데시메이트 없음).

실행:  blender -b Map\PreviewStage.blend -P Map\export_parts.py
산출:  OVDR_Import\parts\<group>_overdare.fbx (+ 1024 베이크 텍스처 내장), parts_manifest.json

각 그룹은 자기 바운딩박스 중심이 원점이 되게 옮겨서 내보낸다. 스튜디오가 피벗을 원점으로 잡든
바운딩박스 중심으로 잡든 결과가 같아지므로, 배치 = 무대 원점 + manifest 의 center 로 끝난다.
"""
import bpy, bmesh, os, json, time
from mathutils import Vector

ROOT = r'C:\Users\29\Desktop\3y'
OUT = os.path.join(ROOT, 'OVDR_Import', 'parts')
os.makedirs(OUT, exist_ok=True)
GROUPS = {
    'stage_ground': lambda n: n.startswith(('ENV_ground', 'ENV_plaza', 'ENV_stage_', 'ENV_step_', 'ENV_bush_')),
    'stage_fence':  lambda n: n.startswith(('ENV_fence_', 'ENV_wall_')),
    'stage_gate':   lambda n: n.startswith('ENV_gate_'),
    'stage_trees':  lambda n: n.startswith(('PRP_pine_', 'PRP_maple_', 'PRP_rock_')),
    'stage_props':  lambda n: n.startswith('PRP_') and not n.startswith(('PRP_pine_', 'PRP_maple_', 'PRP_rock_')),
}
TEX = 1024
sc = bpy.context.scene; vl = bpy.context.view_layer
vl.layer_collection.children['EXPORT'].exclude = False
src_all = [o for c in ('MAP', 'PROPS') for o in bpy.data.collections[c].objects if o.type == 'MESH']
dg = bpy.context.evaluated_depsgraph_get()
manifest = []
t0 = time.time()
for gname, pred in GROUPS.items():
    src = [o for o in src_all if pred(o.name)]
    bm = bmesh.new(); bm.loops.layers.uv.new('UVMap')
    mats = []
    for o in src:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
        me.transform(o.matrix_world)
        remap = []
        for m in me.materials:
            if m not in mats: mats.append(m)
            remap.append(mats.index(m))
        for p in me.polygons: p.material_index = remap[p.material_index] if remap else 0
        bm.from_mesh(me); bpy.data.meshes.remove(me)
    # recentre on the bounding-box centre, remember the offset
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    center = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    for v in bm.verts: v.co -= center
    me = bpy.data.meshes.new(gname); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    old = bpy.data.objects.get(gname)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    ob = bpy.data.objects.new(gname, me); bpy.data.collections['EXPORT'].objects.link(ob)
    for o in sc.objects: o.select_set(False)
    ob.select_set(True); vl.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.003)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new(gname + '_BaseColor', TEX, TEX)
    img.generated_color = (0.45, 0.43, 0.40, 1)
    for m in mats:
        nt = m.node_tree
        n = nt.nodes.get('BAKE_TARGET') or nt.nodes.new('ShaderNodeTexImage'); n.name = 'BAKE_TARGET'; n.image = img
        for x in nt.nodes: x.select = False
        n.select = True; nt.nodes.active = n
    prev = sc.render.engine
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.device = 'CPU'
    sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False; sc.render.bake.use_pass_color = True
    sc.render.bake.margin = 8; sc.render.bake.use_clear = False
    bpy.ops.object.bake(type='DIFFUSE')
    png = os.path.join(OUT, gname + '_BaseColor.png'); img.filepath_raw = png; img.file_format = 'PNG'; img.save()
    sc.render.engine = prev
    for m in mats:
        n = m.node_tree.nodes.get('BAKE_TARGET')
        if n: m.node_tree.nodes.remove(n)
    am = bpy.data.materials.new('M_' + gname); am.use_nodes = True
    nt = am.node_tree; tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(nt.nodes['Principled BSDF'].inputs['Base Color'], tex.outputs['Color']); nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85
    me.materials.clear(); me.materials.append(am)
    out = os.path.join(OUT, gname + '_overdare.fbx')
    bpy.ops.export_scene.fbx(filepath=out, use_selection=True, object_types={'MESH'}, global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', axis_forward='-Z', axis_up='Y', bake_space_transform=False, use_mesh_modifiers=True, bake_anim=False, path_mode='COPY', embed_textures=True, use_custom_props=False)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    size = [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]
    manifest.append({'group': gname, 'file': out, 'tris': tris, 'objects': len(src), 'center_m_blender': [round(c, 4) for c in center], 'size_m_blender': [round(s, 3) for s in size]})
    print(f'[parts] {gname}: {len(src)} objs, {tris} tris, center {tuple(round(c,2) for c in center)}  ({time.time()-t0:.0f}s)')
json.dump(manifest, open(os.path.join(OUT, 'parts_manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('[parts] done', [(m['group'], m['tris']) for m in manifest])
