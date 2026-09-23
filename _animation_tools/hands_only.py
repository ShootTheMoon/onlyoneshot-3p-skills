import bpy,json,math,os
from mathutils import Matrix,Quaternion
assert os.path.basename(bpy.data.filepath)=='Wakizashi_3P.blend'
arm=bpy.data.objects['Armature'];sc=bpy.context.scene
items=json.loads(bpy.data.texts['Wakizashi_Skill_Manifest.json'].as_string())
weapons=['Wakizashi_3P_L','Wakizashi_3P_R','Wakizashi_3P_Kunai']
snapshots={}
for item in items:
 for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 snapshots[item['name']]={}
 for f in range(1,item['end']+1):
  sc.frame_set(f)
  snapshots[item['name']][f]=({p.name:p.matrix.copy() for p in arm.pose.bones},{n:bpy.data.objects[n].matrix_world.copy() for n in weapons})
report={}
for item in items:
 for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 left=bpy.data.objects[weapons[0]];left.animation_data_create();a=bpy.data.actions.new('Wakizashi_'+item['name']+'_LeftSword');a.use_fake_user=True;left.animation_data.action=a;item['left_sword_action']=a.name
 last={};max_weapon_error=0;max_arm_error=0;max_angle_error=0
 for f,(bones,worlds) in snapshots[item['name']].items():
  sc.frame_set(f)
  for pre in ['Left','Right']:
   n=pre+'Hand';p=arm.pose.bones[n];m=bones[n];axis=(m.translation-bones[pre+'LowerArm'].translation).normalized()
   desired=Matrix.LocRotScale(m.translation,Quaternion(axis,math.pi)@m.to_quaternion(),m.to_scale())
   local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local;p.matrix_basis=local.inverted()@bones[p.parent.name].inverted()@desired;p.rotation_mode='QUATERNION'
   q=p.rotation_quaternion.copy()
   if n in last and q.dot(last[n])<0:q.negate();p.rotation_quaternion=q
   last[n]=q.copy()
   for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=n)
  bpy.context.view_layer.update()
  for n,m in worlds.items():
   o=bpy.data.objects[n];o.matrix_world=m;o.rotation_mode='QUATERNION';q=o.rotation_quaternion.copy()
   if n in last and q.dot(last[n])<0:q.negate();o.rotation_quaternion=q
   last[n]=q.copy()
   for dp in ['location','rotation_quaternion','scale']:o.keyframe_insert(dp,frame=f)
  bpy.context.view_layer.update()
  for n,m in worlds.items():max_weapon_error=max(max_weapon_error,max(abs(bpy.data.objects[n].matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4)))
  for pre in ['Left','Right']:
   for part in ['UpperArm','LowerArm']:
    n=pre+part;max_arm_error=max(max_arm_error,max(abs(arm.pose.bones[n].matrix[r][c]-bones[n][r][c]) for r in range(4) for c in range(4)))
   n=pre+'Hand';angle=math.degrees(bones[n].to_quaternion().rotation_difference(arm.pose.bones[n].matrix.to_quaternion()).angle);max_angle_error=max(max_angle_error,abs(angle-180))
 report[item['name']]={'max_weapon_matrix_error':max_weapon_error,'max_arm_matrix_error':max_arm_error,'max_hand_180_error_deg':max_angle_error}
 assert max_weapon_error<.001 and max_arm_error<.001 and max_angle_error<.01,report[item['name']]
text=json.dumps(items,indent=2);t=bpy.data.texts['Wakizashi_Skill_Manifest.json'];t.clear();t.write(text)
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\manifest.json','w').write(text)
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\hands_only_verification.json','w').write(json.dumps(report,indent=2))
i=next(i for i in items if i['name']=='Attack3')
for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[i[key]]
sc.frame_end=i['end'];sc.frame_set(25)
print('HANDS ONLY VERIFIED',report)
