from pathlib import Path
import json,zipfile,shutil
import imageio.v2 as imageio
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(r'C:\Users\29\Desktop\3y');work=root/'_animation_tools';frames=work/'renders';out=root/'Wakizashi_Skills'
items=json.loads((out/'manifest.json').read_text())
font=ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf',23)
labels={'Idle':'검 대기','Attack1':'검 일반공격 1타','Attack2':'검 일반공격 2타','Attack3':'검 일반공격 3타','BlockIn':'검 막기 진입','BlockHold':'검 막기 유지','BlockOut':'검 막기 해제','KunaiThrow':'쿠나이 투척 수정','Teleport':'순간이동','Draw':'칼 재장착','Ryunochi':'용의 이빨','BowVertical':'국궁 세로 사격','BowHorizontal':'국궁 가로 사격'}
def writer(p):return imageio.get_writer(str(p),fps=15,codec='libx264',quality=8,macro_block_size=16)
with writer(root/'Combat_AllSkills_Preview.mp4') as total,writer(out/'Wakizashi_AllSkills_Preview.mp4') as sword:
 for item in items+[{'name':'BowVertical'},{'name':'BowHorizontal'}]:
  n=item['name'];bow=n.startswith('Bow');dest=(root/('Gukgung_3P_Preview.mp4' if n=='BowVertical' else 'Gukgung_3P_HorizontalAttack_Preview.mp4')) if bow else out/(n+'_Preview.mp4')
  with writer(dest) as clip:
   for p in sorted((frames/n).glob('frame_*.png')):
    im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,640,44),fill='black');d.text((12,6),labels[n]+' | 하체 동작 보강',fill='white',font=font);a=np.asarray(im);clip.append_data(a);total.append_data(a)
    if not bow:sword.append_data(a)
readme=out/'README.md';s=readme.read_text(encoding='utf-8').split('정방향 그립 수정:')[0].split('칼 확대 · 다리 모션 수정:')[0]
readme.write_text(s+'\n최신 수정: 쿠나이 그립 및 투척 팔 동작을 재구성. 65프레임(2.133초)에 손에서 분리해 전방으로 비행합니다. 검 동작에 골반 낮춤·전진·회전과 디딤, 궁극기에 착지 압축 동작을 추가했습니다. 칼 길이 약 56.3cm 유지. 다리 및 투척 수치 검증은 dynamic_body_verification.json, kunai_verification.json. 11개 FBX 재임포트 검증은 verification.json. 관통 검사는 별도 collision_report.json을 참조하세요.\n',encoding='utf-8')
(root/'Combat_Skill_List.md').write_text('검: 대기, 일반공격 1·2·3타, 막기 진입·유지·해제, 쿠나이 투척, 순간이동, 칼 재장착, 용의 이빨 (11개). 별도 칼 돌리기는 Blender에 보관.\n국궁: 세로 사격, 가로 사격 (2개). 국궁의 1인칭 Intro는 별도 3인칭 클립이 아닙니다.\n국궁 세로·가로 사격에는 앞발 디딤, 무릎 굽힘, 골반 이동 및 자세 회복을 추가했습니다.\n데미지·실제 순간이동·투사체 판정·용 이펙트는 게임 코드 연결이 필요합니다.\n',encoding='utf-8')
with zipfile.ZipFile(root/'Wakizashi_Skills_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():
  if p.is_file():z.write(p,'Wakizashi_Skills/'+p.name)
with zipfile.ZipFile(root/'Combat_Animations_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():
  if p.is_file():z.write(p,'Wakizashi_Skills/'+p.name)
 for p in root.glob('Gukgung_3P*'):
  if p.is_file() and p.suffix in ['.fbx','.glb','.mp4','.blend']:z.write(p,'Gukgung/'+p.name)
 for n in ['Wakizashi_3P.blend','Combat_Skill_List.md','Combat_AllSkills_Preview.mp4']:z.write(root/n,n)
 for n in ['bow_dynamic_verification.json','bow_export_verification.json']:z.write(work/n,'Gukgung/'+n)
print('PACKAGED SWORD 11 + BOW 2')
