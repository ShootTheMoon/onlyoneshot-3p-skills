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
    im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,640,45),fill='black');d.text((14,7),name+' | 정방향 그립',font=font,fill='white');a=np.asarray(im);clip.append_data(a);total.append_data(a)
readme=out/'README.md'
s=readme.read_text(encoding='utf-8').split('최초 완성본에서')[0]
readme.write_text(s+'\n정방향 그립 수정: 칼날이 양손 엄지 쪽으로 나오도록 손·팔뚝 자세를 맞추고 손잡이를 쥔 공간에 배치했습니다. 상완 회전도 일부 분산했습니다. 칼 길이 약 45cm. 전 프레임 엄지/칼날 방향 및 그립 중심 검사 결과는 normal_grip_verification.json. FBX 재임포트 검증은 verification.json.\n',encoding='utf-8')
with zipfile.ZipFile(out.parent/'Wakizashi_Skills_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(out.iterdir()):
  if p.is_file():z.write(p,'Wakizashi_Skills/'+p.name)
print('RESTORED PACKAGE',len(items),'clips')


