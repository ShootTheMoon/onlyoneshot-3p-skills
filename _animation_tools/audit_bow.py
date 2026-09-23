import bpy,json
exec(compile(open(r'C:\Users\29\Desktop\3y\_animation_tools\collision_audit.py',encoding='utf-8-sig').read(),'collision_audit.py','exec'))
items=[{'name':'BowVertical','action':'Gukgung_3P_DrawRelease','weapon_action':'Gukgung_Weapon_DrawRelease','end':91},{'name':'BowHorizontal','action':'Gukgung_3P_HorizontalAttack','weapon_action':'Gukgung_Weapon_HorizontalAttack','end':91}]
r=audit(items,bow=True);open(r'C:\Users\29\Desktop\3y\_animation_tools\bow_collision_initial.json','w').write(json.dumps(r,indent=2));print('BOW_AUDIT',r)
