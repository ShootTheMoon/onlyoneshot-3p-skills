import bpy,json,math,os
from mathutils import Matrix,Vector,Quaternion
arm=bpy.data.objects['Armature'];sc=bpy.context.scene;items=json.loads(bpy.data.texts['Wakizashi_Skill_Manifest.json'].as_string());path=r'C:\Users\29\Desktop\3y\_animation_tools\safe_arm_source.json'
bindings=[('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]
def serial(m):return [list(r) for r in m]
if not os.path.exists(path):
 arm.animation_data.action=None
 for p in arm.pose.bones:p.matrix_basis=Matrix(json.loads(arm['oda_tpose_basis_backup'])[p.name])
 bpy.context.view_layer.update();data={'ref':{p.name:serial(arm.matrix_world@p.matrix) for p in arm.pose.bones},'clips':{}}
 for item in items:
  for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
  data['clips'][item['name']]={}
  for f in range(1,item['end']+1):
   sc.frame_set(f);data['clips'][item['name']][str(f)]={'bones':{p.name:serial(arm.matrix_world@p.matrix) for p in arm.pose.bones},'weapons':{n:serial(bpy.data.objects[n].matrix_world) for n,_ in bindings[1:]}}
 json.dump(data,open(path,'w'))
data=json.load(open(path));ref={n:Matrix(m) for n,m in data['ref'].items()}
def frame(d,g):
 x=d.normalized();y=g-x*g.dot(x);y.normalize();return Matrix((x,y,x.cross(y))).transposed()
cfg={}
for pre,side,sign in [('Left','L',1),('Right','R',-1)]:
 h=ref[pre+'Hand'];palm=h.to_quaternion().inverted()@(Vector((sign*.730,-.004,1.071))-h.translation);thumb=h.to_quaternion().inverted()@Vector((0,-1,0));cfg[side]=(pre,sign,frame(palm,thumb),(ref[pre+'LowerArm'].translation-ref[pre+'UpperArm'].translation).length,(ref[pre+'Hand'].translation-ref[pre+'LowerArm'].translation).length)
for item in items:
 for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 last={};release_shift=Vector()
 for fs,entry in data['clips'][item['name']].items():
  f=int(fs);sc.frame_set(f);bones={n:Matrix(m) for n,m in entry['bones'].items()};desired=dict(bones);center=(bones['LeftUpperArm'].translation+bones['RightUpperArm'].translation)*.5
  for side,(pre,sign,hf,l1,l2) in cfg.items():
   old=bones[pre+'Hand'].translation-center;shoulder=bones[pre+'UpperArm'].translation
   x=sign*max(.24,min(.34,.23+.3*abs(old.x)));y=-.35;z=max(-.24,min(.06,old.z))
   if item['name'].startswith('Block'):x=sign*.18;y=-.36;z=-.06
   if item['name']=='Attack3':x=sign*max(.17,min(.31,.20+.25*abs(old.x)));y=-.37
   wrist=center+Vector((x,y,z));axis=wrist-shoulder;distance=axis.length
   if distance>l1+l2-.008:wrist=shoulder+axis.normalized()*(l1+l2-.008);axis=wrist-shoulder;distance=axis.length
   axis.normalize();pole=Vector((sign*.95,-.05,-.65));bend=pole-axis*pole.dot(axis);bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);elbow=shoulder+axis*along+bend*math.sqrt(max(0,l1*l1-along*along));guide=Vector((sign*.90,-.12,.75))
   for part,start,end,nextpart,angle in [('UpperArm',shoulder,elbow,'LowerArm',60),('LowerArm',elbow,wrist,'Hand',120)]:
    r=ref[pre+part];rd=ref[pre+nextpart].translation-r.translation;q=(frame(end-start,Quaternion((end-start).normalized(),math.radians(sign*angle))@guide)@frame(rd,Vector((0,1,0))).inverted()).to_quaternion()@r.to_quaternion();desired[pre+part]=Matrix.LocRotScale(start,q,bones[pre+part].to_scale())
   handguide=Quaternion((wrist-elbow).normalized(),math.radians(-sign*45))@guide;hq=(frame(wrist-elbow,handguide)@hf.inverted()).to_quaternion()
   if item['name']=='KunaiThrow' and side=='R':hq=bones[pre+'Hand'].to_quaternion()
   desired[pre+'Hand']=Matrix.LocRotScale(wrist,hq,bones[pre+'Hand'].to_scale())
  for pre in ['Left','Right']:
   for part in ['UpperArm','LowerArm','Hand']:
    p=arm.pose.bones[pre+part];local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local;p.matrix_basis=local.inverted()@desired[p.parent.name].inverted()@desired[p.name];p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
    if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
    last[p.name]=q.copy()
    for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
  bpy.context.view_layer.update()
  for n,m in entry['weapons'].items():
   pre='Left' if n=='Wakizashi_3P_L' else 'Right';original=Matrix(m);delta=desired[pre+'Hand']@bones[pre+'Hand'].inverted();target=delta@original
   if n=='Wakizashi_3P_Kunai' and item['name']=='KunaiThrow':
    if f==65:release_shift=target.translation-original.translation
    if f>=65:target=original.copy();target.translation+=release_shift
   o=bpy.data.objects[n];o.matrix_world=target;o.rotation_mode='QUATERNION';q=o.rotation_quaternion.copy()
   if n in last and q.dot(last[n])<0:q.negate();o.rotation_quaternion=q
   last[n]=q.copy()
   for dp in ['location','rotation_quaternion','scale']:o.keyframe_insert(dp,frame=f)
 print('SAFE PATH',item['name'])
item=next(i for i in items if i['name']=='Attack3')
for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
sc.frame_end=item['end'];sc.frame_set(25)
