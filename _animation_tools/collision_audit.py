import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def mesh_tree(o,arm,kind=None):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];ids=None
 if kind=='blade':ids={v.index for v in o.data.vertices if v.co.y>.09}
 if kind=='arm':
  pre='Left' if o.name.startswith('Left') else 'Right';groups={o.vertex_groups[pre+s].index for s in ['LowerArm','Hand']};upper=o.vertex_groups[pre+'UpperArm'].index;shoulder=(arm.matrix_world@arm.pose.bones[pre+'UpperArm'].matrix).translation
  ids={v.index for v in o.data.vertices if any((g.group in groups and g.weight>.5) or (g.group==upper and g.weight>.5 and (vs[v.index]-shoulder).length>.075) for g in v.groups)}
 faces=[tuple(p.vertices) for p in me.polygons if ids is None or all(i in ids for i in p.vertices)]
 tree=BVHTree.FromPolygons(vs,faces,all_triangles=False);ev.to_mesh_clear();return tree
def audit(items,bow=False,half=False):
 arm=bpy.data.objects['Armature'];sc=bpy.context.scene;report={}
 for item in items:
  arm.animation_data.action=bpy.data.actions[item['action']]
  if bow:bpy.data.objects['Gukgung_WeaponRig'].animation_data.action=bpy.data.actions[item['weapon_action']]
  else:
   for obj,key in [('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
  hits=[];counts={};last={};maxrot=0
  moving=[('LeftArm_Geo','arm'),('RightArm_Geo','arm')]+([('Gukgung_3P_Bow',None),('Gukgung_3P_String',None),('Gukgung_3P_Arrow',None)] if bow else [('Wakizashi_3P_R','blade'),('Wakizashi_3P_L','blade'),('Wakizashi_3P_Kunai',None)])
  for tick in range(0,(item['end']-1)*(2 if half else 1)+1):
   f=1+tick/(2 if half else 1);sc.frame_set(int(f),subframe=f-int(f));body={n:mesh_tree(bpy.data.objects[n],arm) for n in ['Torso_Geo','Head_Geo','LeftLeg_Geo','RightLeg_Geo']}
   trees={}
   for n,kind in moving:
    o=bpy.data.objects[n]
    if max(o.scale)<.001:continue
    bt=mesh_tree(o,arm,kind);trees[n]=bt
    for other,t in body.items():
     if bt.overlap(t):
      key=n+' / '+other;counts[key]=counts.get(key,0)+1
      if len(hits)<30:hits.append([f,n,other])
   extra=[('LeftArm_Geo','RightArm_Geo')]
   if bow:extra += [('Gukgung_3P_Bow','RightArm_Geo')]
   else:extra += [('Wakizashi_3P_L','RightArm_Geo'),('Wakizashi_3P_R','LeftArm_Geo'),('Wakizashi_3P_L','Wakizashi_3P_R'),('Wakizashi_3P_Kunai','LeftArm_Geo')]
   for n,other in extra:
    if n in trees and other in trees and trees[n].overlap(trees[other]):
     key=n+' / '+other;counts[key]=counts.get(key,0)+1
     if len(hits)<30:hits.append([f,n,other])
   for pre in ['Left','Right']:
    q=arm.pose.bones[pre+'LowerArm'].matrix.to_quaternion()
    if pre in last:
     a=math.degrees(q.rotation_difference(last[pre]).angle);maxrot=max(maxrot,min(a,360-a))
    last[pre]=q.copy()
  report[item['name']]={'collision_count':sum(counts.values()),'pairs':counts,'first_collisions':hits,'max_forearm_delta_deg':maxrot,'sample_step_frames':.5 if half else 1}
 return report

