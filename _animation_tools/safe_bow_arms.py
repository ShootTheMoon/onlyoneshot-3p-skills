import bpy,json,math
from mathutils import Matrix,Vector,Quaternion
arm=bpy.data.objects['Armature'];rig=bpy.data.objects['Gukgung_WeaponRig'];sc=bpy.context.scene
items=[{'name':'BowVertical','action':'Gukgung_3P_DrawRelease','weapon_action':'Gukgung_Weapon_DrawRelease','end':91},{'name':'BowHorizontal','action':'Gukgung_3P_HorizontalAttack','weapon_action':'Gukgung_Weapon_HorizontalAttack','end':91}]
all_snap={}
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];rig.animation_data.action=bpy.data.actions[item['weapon_action']];all_snap[item['name']]={}
 for f in range(1,92):
  sc.frame_set(f);all_snap[item['name']][f]=({p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones},{p.name:(rig.matrix_world@p.matrix).copy() for p in rig.pose.bones})
shift=Vector((-.17,-.14,-.020));overreach=[]
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];rig.animation_data.action=bpy.data.actions[item['weapon_action']];last={}
 for f,(bones,weapons) in all_snap[item['name']].items():
  sc.frame_set(f);desired=dict(bones)
  pivot=weapons['Grip'].translation;rot=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-40 if item['name']=='BowHorizontal' else 0),4,'X')@Matrix.Translation(-pivot)
  handtargets={pre:(rot@bones[pre+'Hand']).translation for pre in ['Left','Right']}
  shift=Vector((-.14,-.17,-.025))
  for iteration in range(50):
   for pre in ['Left','Right']:
    sh=bones[pre+'UpperArm'].translation;el=bones[pre+'LowerArm'].translation;wr=bones[pre+'Hand'].translation;limit=(el-sh).length+(wr-el).length-.006;v=handtargets[pre]+shift-sh
    if v.length>limit:shift=sh-handtargets[pre]+v.normalized()*limit
  for pre,sign in [('Left',1),('Right',-1)]:
   sh=bones[pre+'UpperArm'].translation;el=bones[pre+'LowerArm'].translation;wr=bones[pre+'Hand'].translation;wrist=handtargets[pre]+shift;l1=(el-sh).length;l2=(wr-el).length;axis=wrist-sh;distance=axis.length;overreach.append(max(0,distance-l1-l2));axis.normalize()
   if distance>=l1+l2:raise RuntimeError(('unreachable',item['name'],f,pre,distance,l1+l2))
   pole=Vector((sign*.9,-.1,-.55));bend=pole-axis*pole.dot(axis);bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);elbow=sh+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
   for part,start,end,oldstart,oldend in [('UpperArm',sh,elbow,sh,el),('LowerArm',elbow,wrist,el,wr)]:
    m=bones[pre+part];q=(oldend-oldstart).rotation_difference(end-start)@m.to_quaternion();desired[pre+part]=Matrix.LocRotScale(start,q,m.to_scale())
   desired[pre+'Hand']=rot@bones[pre+'Hand'];desired[pre+'Hand'].translation=wrist
   for part in ['UpperArm','LowerArm','Hand']:
    p=arm.pose.bones[pre+part];local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local;p.matrix_basis=local.inverted()@desired[p.parent.name].inverted()@desired[p.name];p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
    if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
    last[p.name]=q.copy()
    for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
  for p in rig.pose.bones:
   m=rot@weapons[p.name];m.translation+=shift;p.matrix=rig.matrix_world.inverted()@m;p.rotation_mode='QUATERNION'
   for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
exec(compile(open(r'C:\Users\29\Desktop\3y\_animation_tools\collision_audit.py',encoding='utf-8-sig').read(),'collision_audit.py','exec'))
r=audit(items,bow=True);open(r'C:\Users\29\Desktop\3y\_animation_tools\bow_collision_fixed.json','w').write(json.dumps(r,indent=2));print('BOW_FIXED',{n:v['pairs'] for n,v in r.items()})
if all(v['collision_count']==0 for v in r.values()):bpy.ops.wm.save_as_mainfile(filepath=r'C:\Users\29\Desktop\3y\Gukgung_3P.blend')





