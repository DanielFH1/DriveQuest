#!/usr/bin/env python3
"""DriveQuest2 editorial product film. Real app captures; no UI compositing to invent functions."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json
R=Path(__file__).resolve().parents[1];C=R/'artifacts/product-film';W=R/'.local/film-render';W.mkdir(parents=True,exist_ok=True)
OUT=R/'submission/output';BG='#F5F3EE';INK='#162D24';GREEN='#006241';MUTED='#747B71'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n,index=1)
def txt(d,x,y,t,n=40,col=INK,b=False):d.multiline_text((x,y),t,font=font(n,b),fill=col,spacing=18)
def center(d,y,t,n=80,col=INK,b=False):
 for line in t.split('\n'):
  width=d.textlength(line,font=font(n,b));txt(d,(1920-width)/2,y,line,n,col,b);y+=n+23
plan=[
 ('intro',8,'DriveQuest2','오늘의 운전을, 내일의 감각으로.',None),
 ('question',9,'영상으로 나의 운전을\n교정할 수 있다면?','운전이 끝난 뒤, 돌아볼 시간이 시작됩니다.',None),
 ('welcome',7,'주차를 마치고,\n나를 위한 시간.','오늘의 주행을\n함께 확인해볼까요?','welcome-clean.mp4'),
 ('today',12,'하루의 운전.\n한눈에.','요약을 읽고,\n마음에 걸린 회전을 찾습니다.','today-clean.png'),
 ('find',7,'기억에 남은 회전부터.','좌회전 · 우회전 · 유턴 · 커브',None),
 ('library',9,'그때의 순간을\n다시 선택.','시간순으로 정리된\n24개의 회전 장면.','today-clean.png'),
 ('compare',8,'두 경로를,\n같은 장면에서.','어디에서 달라졌는지 천천히 살펴봅니다.',None),
 ('left',11,'지나온 선과,\n비교할 선.','초록 실선은 비교 경로.\n주황 점선은 주행 경로.','left-clean.mp4'),
 ('right',11,'한 번 더.\n이번에는 천천히.','멈추고, 되돌리고,\n차이가 생긴 지점을 봅니다.','right-clean.mp4'),
 ('change',8,'오늘의 한 장면이,\n한 달의 흐름으로.','한 번의 점수보다, 반복되는 습관을 봅니다.',None),
 ('monthly',12,'변화를\n읽는 시간.','회전별 정확도와\n월간 기록을 함께 확인합니다.','monthly-clean.mp4'),
 ('habit',7,'다음 운전에서\n바꿀 한 가지.','작은 실천이 이어지도록.',None),
 ('achievements',11,'돌아보는 습관을\n계속할 이유.','신호, 정지선, 방향지시등.\n도전과제로 다시 떠올립니다.','achievements-clean.png'),
 ('scope',12,'현재는 화면으로.\n다음은 실제 기록으로.','Pleos에서 실행한 프로토타입입니다.\n영상과 수치는 콘셉트 데이터이며, 실주행 수집·분석은 다음 단계입니다.',None),
 ('end',9,'DriveQuest2','오늘의 운전을, 내일의 감각으로.',None)]
segments=[];timeline=[];elapsed=0
logo=Image.open(R/'submission/reference/hmg-logo.png').convert('RGBA');logo.thumbnail((280,140))
for idx,(key,dur,title,body,src) in enumerate(plan):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 if key in ('intro','end'):
  im=Image.new('RGB',(1920,1080),'#102D26');d=ImageDraw.Draw(im)
  im.paste(logo,(92,68),logo);txt(d,92,230,'2026 현대자동차그룹 차량용 앱 개발 공모전',30,'#BCD2C5')
  txt(d,86,392,title,124,'#FFFFFF',True);txt(d,96,579,body,46,'#C8E4D4')
  txt(d,96,940,'출품작 소개  /  주차 후 주행 복습',26,'#BCD2C5')
 elif src:
  txt(d,80,78,'DriveQuest2',28,GREEN,True)
  txt(d,80,256,title,55,INK,True);txt(d,83,490,body,29,MUTED)
  txt(d,83,858,'Pleos Connect\n실제 앱 화면 · 합성 주행 영상',22,MUTED)
  # Device viewport kept intact, with generous whitespace and no ornamental UI.
  d.rounded_rectangle((596,76,1836,978),radius=22,fill='#E0E3DB')
 else:
  txt(d,90,72,'DriveQuest2',26,GREEN,True)
  center(d,320,title,78,INK,True);center(d,650,body,32,MUTED)
  d.rounded_rectangle((914,875,1006,880),radius=2,fill=GREEN)
 txt(d,1790,1018,f'{idx+1:02d}',20,'#8C978D')
 bg=W/f'{idx:02d}.png';im.save(bg);video=W/f'{idx:02d}.mp4'
 cmd=['ffmpeg','-v','error','-y','-loop','1','-framerate','30','-i',str(bg)]
 fade=f'fade=t=in:st=0:d=0.45:color={BG},fade=t=out:st={dur-.4}:d=0.4:color={BG}'
 if src:
  source=C/src
  cmd+=(['-loop','1','-framerate','30'] if source.suffix=='.png' else [])+['-i',str(source)]
  # Recorded screen dimensions 2560x1440; crop only system chrome.
  filt=f'[1:v]crop=1680:1210:853:90,scale=1200:864:flags=lanczos,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=15[app];[0:v][app]overlay=616:94:shortest=1,{fade},format=yuv420p[v]'
  cmd+=['-filter_complex',filt,'-map','[v]']
 else:cmd+=['-vf',fade+',format=yuv420p']
 cmd+=['-t',str(dur),'-an','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-r','30','-map_metadata','-1',str(video)]
 subprocess.run(cmd,check=True);segments.append(video);timeline.append(dict(start=elapsed,duration=dur,scene=key,title=title,caption=body,source=src));elapsed+=dur;print(key,flush=True)
f=W/'concat.txt';f.write_text(''.join("file '"+str(p)+"'\n" for p in segments))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(f),'-c','copy','-map_metadata','-1','-movflags','+faststart',str(OUT/'DriveQuest2-demo.mp4')],check=True)
(OUT/'DriveQuest2-video-story.json').write_text(json.dumps({'duration':elapsed,'resolution':'1920x1080','fps':30,'audio':'none','privacy':'No participant identities','scenes':timeline},ensure_ascii=False,indent=2))
# Copy-ready subtitle transcript for reviewers and later voiceover.
(OUT/'DriveQuest2-영상대본.txt').write_text('\n\n'.join(f"{s['start']//60:02d}:{s['start']%60:02d}  {s['title']}\n{s['caption']}" for s in timeline))
print('DONE',elapsed,flush=True)
