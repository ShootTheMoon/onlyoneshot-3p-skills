import bpy,json,math
from mathutils import Matrix,Vector,Quaternion
arm=bpy.data.objects['Armature'];sc=bpy.context.scene;items=json.loads(bpy.data.texts['Wakizashi_Skill_Manifest.json'].as_string());item=next(i for i in items if i['name']=='KunaiThrow')
arm.animation_data.action=None
for p in arm.pose.bones:p.matrix_basis=Matrix(json.loads(arm['oda_tpose_basis_backup'])[p.name])
bpy.context.view_layer.update();ref={p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones}
def frame(d,g):
 x=d.normalized();y=(g-x*g.dot(x)).normalized();return Matrix((x,y,x.cross(y))).transposed()
h=ref['RightHand'];palm=h.to_quaternion().inverted()@(Vector((-.730,-.004,1.071))-h.translation);thumb=h.to_quaternion().inverted()@Vector((0,-1,0));hf=frame(palm,thumb)
restknife=Matrix.Diagonal(Vector((-1,-1,1))).to_quaternion();knife_local=h.to_quaternion().inverted()@restknife
for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
snap={}
for f in range(1,item['end']+1):
 sc.frame_set(f);snap[f]={p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones}
keys=[(0,(-.24,-.28,1.02)),(.45,(-.25,-.22,.99)),(1.35,(-.27,-.10,1.29)),(1.90,(-.27,-.13,1.29)),(2.02,(-.23,-.30,1.26)),(64/30,(-.18,-.43,1.18)),(2.30,(-.15,-.42,1.05)),(2.50,(-.23,-.31,1.04))]
def target(t):
 for (ta,pa),(tb,pb) in zip(keys,keys[1:]):
  if t<=tb:
   u=max(0,min(1,(t-ta)/(tb-ta)));u=u*u*(3-2*u);return Vector(pa).lerp(Vector(pb),u)
 return Vector(keys[-1][1])
last={};grips={};knife_rot={}
for f,bones in snap.items():
 sc.frame_set(f);t=(f-1)/30;shoulder=bones['RightUpperArm'].translation;shift=shoulder-ref['RightUpperArm'].translation;wrist=target(t)+shift
 l1=(ref['RightLowerArm'].translation-ref['RightUpperArm'].translation).length;l2=(ref['RightHand'].translation-ref['RightLowerArm'].translation).length
 axis=wrist-shoulder;distance=axis.length
 if distance>l1+l2-.008:wrist=shoulder+axis.normalized()*(l1+l2-.008);axis=wrist-shoulder;distance=axis.length
 axis.normalize();pole=Vector((-.75,.10,.65));bend=pole-axis*pole.dot(axis);bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);elbow=shoulder+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
 blade=Vector((0,-1,0));palmdir=wrist-elbow;palmdir-=blade*palmdir.dot(blade)
 if palmdir.length<.03:palmdir=Vector((-.3,0,-1))
 handq=(frame(palmdir,blade)@hf.inverted()).to_quaternion();desired=dict(bones)
 for part,start,end,nextpart in [('UpperArm',shoulder,elbow,'LowerArm'),('LowerArm',elbow,wrist,'Hand')]:
  n='Right'+part;r=ref[n];rd=ref['Right'+nextpart].translation-r.translation;q=(frame(end-start,blade)@frame(rd,Vector((0,-1,0))).inverted()).to_quaternion()@r.to_quaternion();desired[n]=Matrix.LocRotScale(start,q,r.to_scale())
 desired['RightHand']=Matrix.LocRotScale(wrist,handq,h.to_scale())
 for part in ['UpperArm','LowerArm','Hand']:
  p=arm.pose.bones['Right'+part];local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local;p.matrix_basis=local.inverted()@desired[p.parent.name].inverted()@desired[p.name];p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
  if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
  last[p.name]=q.copy()
  for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
 grips[f]=wrist+handq@palm;knife_rot[f]=handq@knife_local
kunai=bpy.data.objects['Wakizashi_3P_Kunai'];action=bpy.data.actions.new('Wakizashi_KunaiThrow_CorrectedRelease');action.use_fake_user=True;kunai.animation_data.action=action;item['kunai_action']=action.name
release_f=65;release_q=knife_rot[release_f];release_origin=grips[release_f]-release_q@Vector((0,.035,0));errors=[];worlds={};lastq=None
for f in range(1,item['end']+1):
 sc.frame_set(f);q=knife_rot[f];origin=grips[f]-q@Vector((0,.035,0))
 if f>=release_f:
  dt=(f-release_f)/30;q=release_q;origin=release_origin+Vector((0,-6*dt,-dt*dt))
 visible=(f-1)/30>=.45;kunai.matrix_world=Matrix.LocRotScale(origin,q,Vector((1,1,1)) if visible else Vector((.000001,)*3));kunai.rotation_mode='QUATERNION';kq=kunai.rotation_quaternion.copy()
 if lastq and kq.dot(lastq)<0:kq.negate();kunai.rotation_quaternion=kq
 lastq=kq.copy()
 for dp in ['location','rotation_quaternion','scale']:kunai.keyframe_insert(dp,frame=f)
 bpy.context.view_layer.update();worlds[f]=kunai.matrix_world.copy()
 if visible and f<=release_f:errors.append((kunai.matrix_world@Vector((0,.035,0))-grips[f]).length)
item['events']=[[n,(release_f-1)/30 if n=='throw' else t] for n,t in item['events']]
text=json.dumps(items,indent=2);t=bpy.data.texts['Wakizashi_Skill_Manifest.json'];t.clear();t.write(text);open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\manifest.json','w').write(text)
report={'release_frame':release_f,'release_time_s':(release_f-1)/30,'max_held_grip_error_m':max(errors),'first_flight_step_m':(worlds[66].translation-worlds[65].translation).length,'flight_tip_direction':list((worlds[66].to_3x3()@Vector((0,1,0))).normalized())}
assert max(errors)<.001;assert (worlds[66].translation-worlds[65].translation).y<-.19
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\kunai_verification.json','w').write(json.dumps(report,indent=2));sc.frame_end=76;sc.frame_set(64);print(report)
