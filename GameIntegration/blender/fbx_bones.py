import bpy, sys, json
path = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=path)
out={"objects":[],"armatures":[],"actions":[a.name for a in bpy.data.actions]}
for o in bpy.data.objects:
    out["objects"].append({"name":o.name,"type":o.type})
    if o.type=='ARMATURE':
        out["armatures"].append({"obj":o.name,"nbones":len(o.data.bones),"bones":[b.name for b in o.data.bones]})
print("FBX_JSON "+json.dumps(out))
