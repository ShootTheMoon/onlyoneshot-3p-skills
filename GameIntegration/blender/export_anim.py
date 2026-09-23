import bpy, os, sys, json
argv = sys.argv[sys.argv.index("--")+1:]
outdir, pairs = argv[0], json.loads(argv[1])   # pairs: [[action, outname], ...]
os.makedirs(outdir, exist_ok=True)
sc = bpy.context.scene
arm = bpy.data.objects['Armature']
arm.animation_data_create()
res = []
for action_name, out in pairs:
    act = bpy.data.actions[action_name]
    arm.animation_data.action = act
    start, end = act.frame_range
    sc.frame_start, sc.frame_end = 1, int(round(end))
    sc.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    path = os.path.join(outdir, out + '.fbx')
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'ARMATURE'},
        global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Z', axis_up='Y', bake_space_transform=False, add_leaf_bones=False,
        use_armature_deform_only=False, bake_anim=True, bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0, path_mode='COPY', embed_textures=False, use_custom_props=False)
    res.append({"action": action_name, "file": path, "frames": int(round(end)),
                "seconds": round(int(round(end))/sc.render.fps, 4),
                "bytes": os.path.getsize(path)})
print("EXPORT_JSON " + json.dumps(res))
