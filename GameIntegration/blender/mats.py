import bpy, json
out = []
NAMES = ['Head_Geo','LeftArm_Geo','LeftLeg_Geo','RightArm_Geo','RightLeg_Geo','Torso_Geo',
         'Wakizashi_3P_R','Wakizashi_3P_L','Wakizashi_3P_Kunai',
         'Gukgung_3P_Bow','Gukgung_3P_String','Gukgung_3P_Arrow']
for n in NAMES:
    o = bpy.data.objects.get(n)
    if not o:
        continue
    slots = []
    for s in o.material_slots:
        m = s.material
        if not m:
            slots.append({"mat": None})
            continue
        base, img = None, None
        if m.use_nodes:
            for nd in m.node_tree.nodes:
                if nd.type == 'BSDF_PRINCIPLED':
                    inp = nd.inputs.get('Base Color')
                    if inp and not inp.is_linked:
                        base = [round(v, 3) for v in inp.default_value[:3]]
                    elif inp and inp.is_linked:
                        base = 'linked:' + inp.links[0].from_node.type
                if nd.type == 'TEX_IMAGE' and nd.image:
                    img = nd.image.name
        slots.append({"mat": m.name, "base": base, "image": img})
    out.append({"obj": n, "uv": [u.name for u in o.data.uv_layers], "slots": slots})
print("MAT_JSON " + json.dumps(out, ensure_ascii=False))
