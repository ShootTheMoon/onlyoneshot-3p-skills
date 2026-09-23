import bpy, sys, json, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
outpath, action_name, frame = argv[0], argv[1], int(argv[2])

sc = bpy.context.scene
arm = bpy.data.objects['Armature']
arm.animation_data_create()
arm.animation_data.action = bpy.data.actions[action_name]
sc.frame_set(frame)

KEEP = {'Head_Geo', 'LeftArm_Geo', 'LeftLeg_Geo', 'RightArm_Geo', 'RightLeg_Geo', 'Torso_Geo',
        'Wakizashi_3P_R', 'Wakizashi_3P_L', 'Wakizashi_3P_Kunai',
        'Gukgung_3P_Bow', 'Gukgung_3P_String', 'Gukgung_3P_Arrow'}
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = o.name not in KEEP

# 캐릭터 바운드를 재서 카메라를 앞에 놓는다
dg = bpy.context.evaluated_depsgraph_get()
lo = hi = None
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.hide_render:
        ev = o.evaluated_get(dg)
        for c in ev.bound_box:
            w = ev.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z))) if lo else w.copy()
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z))) if hi else w.copy()
mid = (lo + hi) * 0.5
span = max((hi - lo).x, (hi - lo).z)

cam_data = bpy.data.cameras.new('RefCam')
cam = bpy.data.objects.new('RefCam', cam_data)
sc.collection.objects.link(cam)
dist = span * 2.4
cam.location = mid + Vector((0, -dist, 0))
cam.rotation_euler = (math.radians(90), 0, 0)
sc.camera = cam

sc.render.engine = 'BLENDER_WORKBENCH'
sc.render.resolution_x, sc.render.resolution_y = 700, 900
sc.render.film_transparent = False
sc.render.filepath = outpath
bpy.ops.render.render(write_still=True)
print("REF_JSON " + json.dumps({"out": outpath, "frame": frame,
                               "bounds": [round(v, 3) for v in (hi - lo)]}))
