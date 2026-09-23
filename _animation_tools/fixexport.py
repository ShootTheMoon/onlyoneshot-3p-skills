import bpy,json,os
from mathutils import Matrix
folder=r'C:\Users\29\Desktop\3y\Wakizashi_Skills';manifest=json.load(open(folder+'\\manifest.json'));sc=bpy.context.scene
names=['Wakizashi_3P_R','Wakizashi_3P_L','Wakizashi_3P_Kunai'];originals={n:bpy.data.objects[n] for n in names};samples={}
for item in manifest:
 for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 samples[item['name']]={}
 for f in range(1,item['end']+1):
  sc.frame_set(f);samples[item['name']][f]={n:o.matrix_world.copy() for n,o in originals.items()}
data=bpy.data.armatures.new('ExportWeaponSkeleton');rig=bpy.data.objects.new('Wakizashi_WeaponRig',data);sc.collection.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for n in names:
 b=data.edit_bones.new(n);b.head=(0,0,0);b.tail=(0,.1,0)
bpy.ops.object.mode_set(mode='OBJECT');copies=[]
for n,o in originals.items():
 o.name=n+'_SOURCE';dup=bpy.data.objects.new(n,o.data);sc.collection.objects.link(dup);dup.parent=rig;g=dup.vertex_groups.new(name=n);g.add(list(range(len(dup.data.vertices))),1,'REPLACE');mod=dup.modifiers.new('RigidWeaponSkin','ARMATURE');mod.object=rig;copies.append(dup)
rig.animation_data_create();actions=[]
for item in manifest:
 bpy.data.objects['Armature'].animation_data.action=bpy.data.actions[item['action']];a=bpy.data.actions.new('Export_'+item['name']);actions.append(a);rig.animation_data.action=a
 for f,worlds in samples[item['name']].items():
  for n,m in worlds.items():
   p=rig.pose.bones[n];p.matrix_basis=p.bone.matrix_local.inverted()@m;p.rotation_mode='QUATERNION'
   for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=n)
 sc.frame_start=1;sc.frame_end=item['end'];sc.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
 for o in list(bpy.data.collections['COL_Character'].objects)+[rig]+copies:o.select_set(True)
 bpy.context.view_layer.objects.active=bpy.data.objects['Armature']
 bpy.ops.export_scene.fbx(filepath=os.path.join(folder,item['fbx']),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Z',axis_up='Y',bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True,use_custom_props=False)
for o in copies+[rig]:bpy.data.objects.remove(o,do_unlink=True)
for a in actions:bpy.data.actions.remove(a)
for n,o in originals.items():o.name=n
item=next(i for i in manifest if i['name']=='Attack3')
for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
sc.frame_end=item['end'];sc.frame_set(25)
print('RIGID SKIN EXPORT FIX COMPLETE')



