from pathlib import Path
import json, shutil, zipfile
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
tmp=Path(r'C:\Users\29\Desktop\3y\_animation_tools\renders')
out=Path(r'C:\Users\29\Desktop\3y\Wakizashi_Skills')
items=json.loads((out/'manifest.json').read_text())
font=ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf',24)
with imageio.get_writer(str(out/'Wakizashi_AllSkills_Preview.mp4'),fps=15,codec='libx264',quality=8,macro_block_size=16) as total:
 for item in items:
  name=item['name']
  with imageio.get_writer(str(out/(name+'_Preview.mp4')),fps=15,codec='libx264',quality=8,macro_block_size=16) as clip:
   for p in sorted((tmp/name).glob('frame_*.png')):
    im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,640,45),fill='black');d.text((14,7),name+' | 손만 180도 회전',font=font,fill='white');a=np.asarray(im);clip.append_data(a);total.append_data(a)
readme=out/'README.md'
s=readme.read_text(encoding='utf-8').split('복원:')[0]
readme.write_text(s+'\n최초 완성본에서 손만 손목 축 기준 180도 회전. 윗팔과 팔뚝 변화 없음, 무기 위치와 방향 유지. 칼 약 45cm. 11개 클립 전 프레임 수치 검증: hands_only_verification.json. 왼칼 companion 액션 left_sword_action을 포함해 manifest에 따라 액션을 함께 전환하세요.\n',encoding='utf-8')
with zipfile.ZipFile(out.parent/'Wakizashi_Skills_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.iterdir()):
  if p.is_file():z.write(p,'Wakizashi_Skills/'+p.name)
print('RESTORED PACKAGE',len(items),'clips')

