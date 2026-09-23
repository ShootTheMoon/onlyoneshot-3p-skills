import bpy,math,json
from mathutils import Vector,Matrix,Quaternion
def smooth(u):
 u=max(0,min(1,u));return u*u*(3-2*u)
def step(u,a,b,c,d):
 if u<a:return 0,0
 if u<b:
  t=(u-a)/(b-a);return smooth(t),math.sin(math.pi*t)**2
 if u<c:return 1,0
 if u<d:
  t=(u-c)/(d-c);return 1-smooth(t),math.sin(math.pi*t)**2
 return 0,0
def make_dynamic(items,bow=False):
 arm=bpy.data.objects['Armature'];sc=bpy.context.scene;all_snap={};wep=bpy.data.objects.get('Gukgung_WeaponRig') if bow else None;report={}
 for item in items:
  arm.animation_data.action=bpy.data.actions[item['action']]
  if bow:wep.animation_data.action=bpy.data.actions[item['weapon_action']]
  all_snap[item['name']]={}
  for f in range(1,item['end']+1):
   sc.frame_set(f);all_snap[item['name']][f]=({p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones},{p.name:(wep.matrix_world@p.matrix).copy() for p in wep.pose.bones} if bow else {})
 for item in items:
  arm.animation_data.action=bpy.data.actions[item['action']]
  if bow:wep.animation_data.action=bpy.data.actions[item['weapon_action']]
  last={};heights=[];reach=[]
  for f,(bones,weaponbones) in all_snap[item['name']].items():
   sc.frame_set(f);u=(f-1)/(item['end']-1);t=(f-1)/30;name=item['name'];weight=lift=0;lead='Right' if name=='Attack2' else 'Left';sign=-1 if lead=='Right' else 1
   if bow:weight,lift=step(u,.03,.24,.76,1);drop=.045*weight;forward=.045*weight;yaw=math.radians(6)*weight
   elif name=='Idle':drop=.004*(1-math.cos(2*math.pi*u));forward=0;yaw=0
   elif name.startswith('Block'):
    weight=1 if name=='BlockHold' else smooth(u if name=='BlockIn' else 1-u);drop=.055*weight;forward=.015*weight;yaw=0
   elif name.startswith('Attack'):
    weight,lift=step(u,.04,.30,.58,.96);impact=math.sin(math.pi*smooth((u-.24)/.42));drop=.055*weight;forward=.075*weight;yaw=math.radians(sign*12)*math.sin(2*math.pi*u)*weight
   elif name=='KunaiThrow':weight,lift=step(u,.53,.79,.89,1);drop=.035*weight;forward=.065*weight;yaw=math.radians(-11)*math.sin(math.pi*smooth((u-.50)/.50))
   elif name=='Ryunochi':
    weight,lift=step(u,.10,.32,.88,1);drop=.05*weight;forward=.025*weight;yaw=math.radians(7)*math.sin(2*math.pi*u)
    if 2.50<t<2.93:drop=0;lift=0
    if 2.93<=t<3.4:drop+=.07*math.sin(math.pi*(t-2.93)/.47)**2
   else:weight,lift=step(u,.08,.30,.70,1);drop=.04*weight;forward=.045*weight;yaw=math.radians(6)*math.sin(2*math.pi*u)
   pelvis=bones['LowerTorso'].translation;shift=Vector((sign*.02*weight,-forward,-drop));delta=Matrix.Translation(pelvis+shift)@Matrix.Rotation(yaw,4,'Z')@Matrix.Translation(-pelvis)
   desired={n:(delta@m if n!='Root' else m.copy()) for n,m in bones.items()};heights.append(drop)
   for pre,sgn in [('Left',1),('Right',-1)]:
    hip=desired[pre+'UpperLeg'].translation;k0=bones[pre+'LowerLeg'].translation;a0=bones[pre+'Foot'].translation;h0=bones[pre+'UpperLeg'].translation
    amount=(.12 if bow else .065)*weight if pre==lead else .025*weight
    ankle=a0+Vector((sgn*.025*weight,-amount,.045*lift if pre==lead else .01*lift))
    if name.startswith('Block'):ankle=a0+Vector((sgn*.02*weight,0,0))
    l1=(k0-h0).length;l2=(a0-k0).length;axis=ankle-hip;distance=axis.length
    if distance>l1+l2-.001:
     # Keep the planted foot and solve the hip-height limit through a tiny reach clamp.
     ankle=hip+axis.normalized()*(l1+l2-.001);axis=ankle-hip;distance=axis.length
    reach.append(max(0,distance-l1-l2));axis.normalize();bend=Vector((sgn*.20,-1,0));bend-=axis*bend.dot(axis);bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);knee=hip+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
    for part,start,end,oldstart,oldend in [('UpperLeg',hip,knee,h0,k0),('LowerLeg',knee,ankle,k0,a0)]:
     n=pre+part;m=bones[n];q=(oldend-oldstart).rotation_difference(end-start)@m.to_quaternion();desired[n]=Matrix.LocRotScale(start,q,m.to_scale())
    foot=bones[pre+'Foot'];desired[pre+'Foot']=Matrix.LocRotScale(ankle,Quaternion((0,0,1),math.radians(sgn*5)*weight)@foot.to_quaternion(),foot.to_scale())
    nub=pre+'Foot_Nub'
    if nub in desired:desired[nub]=desired[pre+'Foot']@foot.inverted()@bones[nub]
   for p in arm.pose.bones:
    b=p.bone;local=b.parent.matrix_local.inverted()@b.matrix_local if b.parent else b.matrix_local
    posed=desired[p.parent.name].inverted()@desired[p.name] if p.parent else arm.matrix_world.inverted()@desired[p.name]
    p.matrix_basis=local.inverted()@posed;p.rotation_mode='QUATERNION';q=p.rotation_quaternion.copy()
    if p.name in last and q.dot(last[p.name])<0:q.negate();p.rotation_quaternion=q
    last[p.name]=q.copy()
    for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
   if bow:
    for p in wep.pose.bones:
     world=weaponbones[p.name] if p.name=='Arrow' and f>=64 else delta@weaponbones[p.name]
     p.matrix=wep.matrix_world.inverted()@world;p.rotation_mode='QUATERNION'
     for dp in ['location','rotation_quaternion','scale']:p.keyframe_insert(dp,frame=f,group=p.name)
   bpy.context.view_layer.update()
  report[item['name']]={'max_added_pelvis_lowering_m':max(heights),'max_overreach_m':max(reach)}
 return report
