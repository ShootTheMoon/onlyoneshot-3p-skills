import bpy,json,os
from mathutils import Vector
root=r'C:\Users\29\Desktop\3y';work=root+r'\_animation_tools';sc=bpy.context.scene
exec(compile(open(work+r'\dynamic_body.py',encoding='utf-8-sig').read(),'dynamic_body.py','exec'))
items=[{'name':'BowVertical','action':'Gukgung_3P_DrawRelease','weapon_action':'Gukgung_Weapon_DrawRelease','end':91,'stem':'Gukgung_3P'}, {'name':'BowHorizontal','action':'Gukgung_3P_HorizontalAttack','weapon_action':'Gukgung_Weapon_HorizontalAttack','end':91,'stem':'Gukgung_3P_HorizontalAttack'}]
report=make_dynamic(items,bow=True);open(work+r'\bow_dynamic_verification.json','w').write(json.dumps(report,indent=2))
arm=bpy.data.objects['Armature'];rig=bpy.data.objects['Gukgung_WeaponRig']
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];rig.animation_data.action=bpy.data.actions[item['weapon_action']];sc.frame_start=1;sc.frame_end=91;sc.frame_set(1)
 for only in [False,True]:
  bpy.ops.object.select_all(action='DESELECT')
  objects=list(bpy.data.collections['COL_Weapon3P'].objects)+(list(bpy.data.collections['COL_Character'].objects) if not only else [])
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=rig if only else arm
  path=root+'\\'+item['stem']+('_WeaponsOnly.fbx' if only else '_For_OVDR.fbx')
  bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Z',axis_up='Y',bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True,use_custom_props=False)
 bpy.ops.object.select_all(action='DESELECT')
 for o in list(bpy.data.collections['COL_Weapon3P'].objects)+list(bpy.data.collections['COL_Character'].objects):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=root+'\\'+item['stem']+'.glb',export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
sc.frame_set(54);bpy.ops.wm.save_as_mainfile(filepath=root+r'\Gukgung_3P.blend')
def bounds(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];out=[min(v[k] for v in vs) for k in range(3)]+[max(v[k] for v in vs) for k in range(3)];ev.to_mesh_clear();return out
names=['Gukgung_3P_Bow','Gukgung_3P_Arrow','Gukgung_3P_String','LeftArm_Geo','RightArm_Geo','LeftLeg_Geo','RightLeg_Geo'];frames=[1,15,31,54,61,64,76,91];expected={}
camd=bpy.data.cameras.new('Preview');cam=bpy.data.objects.new('Preview',camd);sc.collection.objects.link(cam);cam.location=(2,-4,2.7);cam.rotation_euler=(Vector((0,-.1,.95))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=3.05;sc.camera=cam
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_cavity=True;sc.display.shading.background_type='WORLD';sc.world=sc.world or bpy.data.worlds.new('World');sc.world.color=(.045,.055,.07);sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.fps=30
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];rig.animation_data.action=bpy.data.actions[item['weapon_action']];expected[item['name']]={}
 for f in frames:
  sc.frame_set(f);expected[item['name']][f]={n:bounds(bpy.data.objects[n]) for n in names}
 out=work+'\\renders\\'+item['name'];os.makedirs(out,exist_ok=True);sc.render.filepath=out+'\\frame_';sc.frame_start=1;sc.frame_end=91;sc.frame_step=2;bpy.ops.render.render(animation=True)
results={}
for item in items:
 results[item['name']]={}
 for ext in ['fbx','glb']:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
  if ext=='fbx':bpy.ops.import_scene.fbx(filepath=root+'\\'+item['stem']+'_For_OVDR.fbx')
  else:bpy.ops.import_scene.gltf(filepath=root+'\\'+item['stem']+'.glb')
  start=min(a.frame_range[0] for a in bpy.data.actions);errors=[]
  for f,objs in expected[item['name']].items():
   bpy.context.scene.frame_set(round(start+f-1))
   for n,bb in objs.items():errors.extend(abs(x-y) for x,y in zip(bounds(bpy.data.objects[n]),bb))
  results[item['name']][ext]={'max_error_m':max(errors),'pass':max(errors)<.002}
open(work+r'\bow_export_verification.json','w').write(json.dumps(results,indent=2));print('BOW_RESULTS',results)
