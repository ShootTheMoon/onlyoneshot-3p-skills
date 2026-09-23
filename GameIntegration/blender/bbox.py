import bpy, sys, json
from mathutils import Vector
path = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)
lo = hi = None
meshes = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    o.data.calc_loop_triangles()
    meshes.append({"name": o.name, "tris": len(o.data.loop_triangles), "groups": len(o.vertex_groups)})
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        lo = Vector((min(lo.x,w.x),min(lo.y,w.y),min(lo.z,w.z))) if lo else w.copy()
        hi = Vector((max(hi.x,w.x),max(hi.y,w.y),max(hi.z,w.z))) if hi else w.copy()
arms = [{"name": o.name, "bones": len(o.data.bones)} for o in bpy.data.objects if o.type=='ARMATURE']
size = (hi - lo) if lo else Vector()
print("BBOX_JSON " + json.dumps({"meshes": meshes, "armatures": arms, "actions": len(bpy.data.actions),
                                "size": [round(v,4) for v in size]}))
