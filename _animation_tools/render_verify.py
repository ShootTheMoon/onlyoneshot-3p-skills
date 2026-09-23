import bpy,json,os
from mathutils import Vector
folder=r'C:\Users\29\Desktop\3y\Wakizashi_Skills';temp=r'C:\Users\29\Desktop\3y\_animation_tools\renders'
manifest=json.load(open(folder+'\\manifest.json'));sc=bpy.context.scene;expected={};names=['Wakizashi_3P_R','Wakizashi_3P_L','Wakizashi_3P_Kunai','LeftArm_Geo','RightArm_Geo','LeftLeg_Geo','RightLeg_Geo']
def bounds(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];res=[min(v[k] for v in vs) for k in range(3)]+[max(v[k] for v in vs) for k in range(3)];ev.to_mesh_clear();return res
camd=bpy.data.cameras.new('SkillsPreview');cam=bpy.data.objects.new('SkillsPreview',camd);sc.collection.objects.link(cam);cam.location=(2,-4,2.3);cam.rotation_euler=(Vector((0,-.15,1.0))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=2.65;sc.camera=cam
sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world=sc.world or bpy.data.worlds.new('World');sc.world.color=(.045,.055,.07);sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.fps=30
for item in manifest:
 for obj,key in [('Armature','action'),('Wakizashi_3P_R','sword_action'),('Wakizashi_3P_L','left_sword_action'),('Wakizashi_3P_Kunai','kunai_action')]:bpy.data.objects[obj].animation_data.action=bpy.data.actions[item[key]]
 fs=sorted(set([1,item['end']//2,item['end']]+[min(item['end'],round(t*30)+1) for _,t in item['events']]))
 expected[item['name']]={}
 for f in fs:
  sc.frame_set(f);expected[item['name']][f]={n:bounds(bpy.data.objects[n]) for n in names}
 out=os.path.join(temp,item['name']);os.makedirs(out,exist_ok=True);sc.frame_start=1;sc.frame_end=item['end'];sc.frame_step=2;sc.render.filepath=out+'\\frame_';bpy.ops.render.render(animation=True)
results={}
for item in manifest:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=os.path.join(folder,item['fbx']))
 start=min(a.frame_range[0] for a in bpy.data.actions);errors=[]
 for f,objects in expected[item['name']].items():
  bpy.context.scene.frame_set(round(start+f-1))
  for n,ex in objects.items():errors.extend(abs(x-y) for x,y in zip(bounds(bpy.data.objects[n]),ex))
 results[item['name']]={'max_error_m':max(errors),'pass':max(errors)<.002}
json.dump(results,open(os.path.join(folder,'verification.json'),'w'),indent=2);print('RESULTS',results)



