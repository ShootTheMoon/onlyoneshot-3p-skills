import bpy,json
print('BOW_INFO',json.dumps({'objects':[(o.name,o.type,o.parent.name if o.parent else None,o.parent_bone,o.animation_data.action.name if o.animation_data and o.animation_data.action else None) for o in bpy.data.objects],'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions],'collections':[c.name for c in bpy.data.collections],'fps':bpy.context.scene.render.fps}))
for o in bpy.data.objects:
 if o.type=='ARMATURE':print('RIG',o.name,list(o.scale),[p.name for p in o.pose.bones])
