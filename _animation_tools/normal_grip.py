import bpy,json,math
from mathutils import Matrix,Vector,Quaternion
arm=bpy.data.objects['Armature'];sc=bpy.context.scene
items=json.loads(bpy.data.texts['Wakizashi_Skill_Manifest.json'].as_string())
bindings=[('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]
arm.animation_data.action=None
for p in arm.pose.bones:p.matrix_basis=Matrix(json.loads(arm['oda_tpose_basis_backup'])[p.name])
bpy.context.view_layer.update();ref={p.name:arm.matrix_world@p.matrix for p in arm.pose.bones}
def frame(d,g):
 x=d.normalized();y=g-x*g.dot(x)
 if y.length<.01:y=Vector((0,-1,0))-x*x.dot(Vector((0,-1,0)))
 y.normalize();return Matrix((x,y,x.cross(y))).transposed()
cfg={}
for pre,side,sign in [('Left','L',1),('Right','R',-1)]:
 h=ref[pre+'Hand'];hq=h.to_quaternion();grip=Vector((sign*.730,-.004,1.071));palm=hq.inverted()@(grip-h.translation);thumb=hq.inverted()@Vector((0,-1,0))
 # Blade exits the thumb side of the modeled closed fist.
 swordrest=Matrix.LocRotScale(grip,Matrix.Diagonal(Vector((-1,-1,1))).to_quaternion(),Vector((1,1,1)))
 hr=Matrix.LocRotScale(h.translation,hq,Vector((1,1,1)))
 cfg[side]=(pre,palm,thumb,frame(palm,thumb),hr.inverted()@swordrest)
snapshots={}
for item in items:
 for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 snapshots[item['name']]={}
 for f in range(1,item['end']+1):
  sc.frame_set(f);snapshots[item['name']][f]=({p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones},{side:bpy.data.objects['Wakizashi_3P_'+side].matrix_world.copy() for side in ['L','R']})
report={}
for item in items:
 for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 for side,key in [('L','left_sword_action'),('R','sword_action')]:
  o=bpy.data.objects['Wakizashi_3P_'+side];a=bpy.data.actions.new('Wakizashi_'+item['name']+'_'+side+'_NormalGrip');a.use_fake_user=True;o.animation_data.action=a;item[key]=a.name
 last={};dots=[];griperrors=[]
 for f,(bones,swords) in snapshots[item['name']].items():
  sc.frame_set(f);desired={n:m.copy() for n,m in bones.items()};targets={}
  for side,(pre,palm,thumb,hframe,attach) in cfg.items():
   wrist=bones[pre+'Hand'].translation;elbow=bones[pre+'LowerArm'].translation;shoulder=bones[pre+'UpperArm'].translation
   direction=(wrist-elbow).normalized();blade=(swords[side].to_3x3()@Vector((0,1,0))).normalized()
   guide=blade-direction*blade.dot(direction)
   if guide.length<.05:guide=Vector((1 if side=='L' else -1,-.2,.7))
   pf=frame(direction,guide);handq=(pf@hframe.inverted()).to_quaternion()
   desired[pre+'Hand']=Matrix.LocRotScale(wrist,handq,bones[pre+'Hand'].to_scale())
   for part,start,end,nextpart,weight in [('LowerArm',elbow,wrist,'Hand',1.0),('UpperArm',shoulder,elbow,'LowerArm',.35)]:
    n=pre+part;r=ref[n];rd=ref[pre+nextpart].translation-r.translation
    q=(frame(end-start,guide)@frame(rd,Vector((0,-1,0))).inverted()).to_quaternion()@r.to_quaternion()
    old=bones[n].to_quaternion()
    if old.dot(q)<0:q.negate()
    desired[n]=Matrix.LocRotScale(start,old.slerp(q,weight),bones[n].to_scale())
   handrigid=Matrix.LocRotScale(wrist,handq,Vector((1,1,1)));target=handrigid@attach
   target=Matrix.LocRotScale(target.translation,target.to_quaternion(),swords[side].to_scale());targets[side]=target
  for pre in ['Left','Right']:
   for part in ['UpperArm','LowerArm','Hand']:
    p=arm.pose.bones[pre+part];local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local
    p.matrix_basis=local.inverted()@desired[p.parent.name].inverted()@desired[p.name];p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
    if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
    last[p.name]=q.copy()
    for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
  bpy.context.view_layer.update()
  for side,target in targets.items():
   o=bpy.data.objects['Wakizashi_3P_'+side];o.matrix_world=target;o.rotation_mode='QUATERNION';q=o.rotation_quaternion.copy()
   if o.name in last and q.dot(last[o.name])<0:q.negate();o.rotation_quaternion=q
   last[o.name]=q.copy()
   for dp in ['location','rotation_quaternion','scale']:o.keyframe_insert(dp,frame=f)
  bpy.context.view_layer.update()
  for side,(pre,palm,thumb,hframe,attach) in cfg.items():
   h=arm.matrix_world@arm.pose.bones[pre+'Hand'].matrix;o=bpy.data.objects['Wakizashi_3P_'+side]
   if max(o.scale)>.01:
    dots.append((h.to_quaternion()@thumb).normalized().dot((o.matrix_world.to_3x3()@Vector((0,1,0))).normalized()))
    griperrors.append((o.matrix_world.translation-(h.translation+h.to_quaternion()@palm)).length)
 report[item['name']]={'min_thumb_blade_dot':min(dots or [1]),'max_grip_center_error_m':max(griperrors or [0])}
 assert min(dots or [1])>.99 and max(griperrors or [0])<.001,report[item['name']]
text=json.dumps(items,indent=2);t=bpy.data.texts['Wakizashi_Skill_Manifest.json'];t.clear();t.write(text)
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\manifest.json','w').write(text)
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\normal_grip_verification.json','w').write(json.dumps(report,indent=2))
item=next(i for i in items if i['name']=='Idle')
for obj,key in bindings:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
sc.frame_end=item['end'];sc.frame_set(1)
print(report)
