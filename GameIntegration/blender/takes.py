import bpy, sys, json
path = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)
out = []
for a in bpy.data.actions:
    fr = a.frame_range
    out.append({"name": a.name, "end": round(fr[1], 2), "seconds": round((fr[1]-0)/30.0, 3)})
print("TAKES_JSON " + json.dumps(out, ensure_ascii=False))
