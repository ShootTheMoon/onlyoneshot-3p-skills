import bpy, json
out={"armatures":[],"actions":[a.name for a in bpy.data.actions],"objects":[]}
for o in bpy.data.objects:
    out["objects"].append({"name":o.name,"type":o.type,"parent":o.parent.name if o.parent else None})
    if o.type=='ARMATURE':
        bones=[b.name for b in o.data.bones]
        out["armatures"].append({"obj":o.name,"data":o.data.name,"nbones":len(bones),"bones":bones[:70]})
print("INSPECT_JSON "+json.dumps(out,ensure_ascii=False))
