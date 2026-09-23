import bpy, sys, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
path, out = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)
sc = bpy.context.scene
lo = hi = None
for o in bpy.data.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x,w.x),min(lo.y,w.y),min(lo.z,w.z))) if lo else w.copy()
            hi = Vector((max(hi.x,w.x),max(hi.y,w.y),max(hi.z,w.z))) if hi else w.copy()
mid = (lo+hi)*0.5
span = max((hi-lo).x, (hi-lo).z)
cam_data = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cam_data)
sc.collection.objects.link(cam)
cam.location = mid + Vector((0, -span*2.2, 0))
cam.rotation_euler = (math.radians(90), 0, 0)
sc.camera = cam
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x, sc.render.resolution_y = 700, 900
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("FR_JSON " + json.dumps({"bounds":[round(v,3) for v in (hi-lo)]}))
