import bpy,json,math,os
from mathutils import Vector,Matrix,Quaternion
assert os.path.basename(bpy.data.filepath)=='Wakizashi_3P.blend'
arm=bpy.data.objects['Armature'];sc=bpy.context.scene
items=json.loads(bpy.data.texts['Wakizashi_Skill_Manifest.json'].as_string())
for side in ['L','R']:
 o=bpy.data.objects['Wakizashi_3P_'+side]
 if not o.get('skills_enlarged_125'):
  for v in o.data.vertices:v.co*=1.25
  o.data.update();o['skills_enlarged_125']=True
def smooth(v):
 v=max(0,min(1,v));return v*v*(3-2*v)
def step(u,a,b,c,d):
 if u<a:return 0,0
 if u<b:
  q=(u-a)/(b-a);return smooth(q),math.sin(math.pi*q)**2
 if u<c:return 1,0
 if u<d:
  q=(u-c)/(d-c);return 1-smooth(q),math.sin(math.pi*q)**2
 return 0,0
snapshots={}
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];snapshots[item['name']]={}
 for f in range(1,item['end']+1):
  sc.frame_set(f);snapshots[item['name']][f]={p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones}
report={}
for item in items:
 arm.animation_data.action=bpy.data.actions[item['action']];last={};distances=[];reacherrors=[]
 for f,bones in snapshots[item['name']].items():
  sc.frame_set(f);u=(f-1)/max(1,item['end']-1);name=item['name'];desired={n:m.copy() for n,m in bones.items()}
  for pre,sign in [('Left',1),('Right',-1)]:
   hip=bones[pre+'UpperLeg'].translation;knee0=bones[pre+'LowerLeg'].translation;ankle0=bones[pre+'Foot'].translation
   weight=lift=0;forward=lateral=yaw=0
   if name.startswith('Attack'):
    lead=('Right' if name=='Attack2' else 'Left')
    if pre==lead:weight,lift=step(u,.05,.28,.69,.94);forward=.09;lateral=.025;yaw=8
    else:weight,lift=step(u,.30,.48,.79,1);forward=.035;lateral=.018;yaw=4
   elif name.startswith('Block'):
    weight=1 if name=='BlockHold' else smooth(u if name=='BlockIn' else 1-u)
    lateral=.028;forward=.015 if pre=='Left' else -.015;yaw=5
   elif name in ['KunaiThrow','Draw']:
    weight,lift=step(u,.12,.33,.73,.98);forward=.07 if pre=='Left' else -.018;lateral=.015;yaw=5
   elif name=='Teleport':
    weight,lift=step(u,.02,.30,.70,1);forward=.055 if pre=='Left' else -.035;lateral=.025;yaw=5
   elif name=='Ryunochi':
    weight,lift=step(u,.1,.35,.8,1);forward=.06 if pre=='Left' else -.025;lateral=.035;yaw=7
    if 2.54<(f-1)/30<2.92:lift=0
   ankle=ankle0+Vector((sign*lateral*weight,-forward*weight,.04*lift))
   l1=(knee0-hip).length;l2=(ankle0-knee0).length;axis=ankle-hip;distance=axis.length
   if distance>l1+l2-.001:
    # Reduce the extra step rather than stretching the skeleton.
    for k in range(12):
     ankle=ankle.lerp(ankle0,.3);axis=ankle-hip;distance=axis.length
     if distance<l1+l2-.001:break
   reacherrors.append(max(0,distance-l1-l2));axis.normalize()
   bend=knee0-hip; bend-=axis*bend.dot(axis)
   if bend.length<.001:bend=Vector((sign*.15,-1,0));bend-=axis*bend.dot(axis)
   bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);height=math.sqrt(max(0,l1*l1-along*along));knee=hip+axis*along+bend*height
   for part,start,end,oldend in [('UpperLeg',hip,knee,knee0),('LowerLeg',knee,ankle,ankle0)]:
    n=pre+part;m=bones[n];oldstart=hip if part=='UpperLeg' else knee0
    q=(oldend-oldstart).rotation_difference(end-start)@m.to_quaternion();desired[n]=Matrix.LocRotScale(start,q,m.to_scale())
   foot=bones[pre+'Foot'];q=Quaternion((0,0,1),math.radians(sign*yaw*weight))@foot.to_quaternion();desired[pre+'Foot']=Matrix.LocRotScale(ankle,q,foot.to_scale())
   distances.append((ankle-ankle0).length)
   for part in ['UpperLeg','LowerLeg','Foot']:
    p=arm.pose.bones[pre+part];local=p.bone.parent.matrix_local.inverted()@p.bone.matrix_local
    p.matrix_basis=local.inverted()@desired[p.parent.name].inverted()@desired[p.name];p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
    if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
    last[p.name]=q.copy()
    for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
 report[item['name']]={'max_added_foot_movement_m':max(distances),'max_leg_overreach_m':max(reacherrors)}
 assert max(reacherrors)<.001
open(r'C:\Users\29\Desktop\3y\Wakizashi_Skills\leg_motion_verification.json','w').write(json.dumps(report,indent=2))
i=next(i for i in items if i['name']=='Attack1')
for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[i[key]]
sc.frame_end=i['end'];sc.frame_set(17)
print(report)
