#!/usr/bin/env python3
"""38-second component-focused cut. Crops only actual, current DriveQuest2 UI.
Reference inspected: Apple's WWDC26 Rev up your CarPlay app; no reference footage reused.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import subprocess,json,math,hashlib
R=Path(__file__).resolve().parents[1];S=R/'submission/output/screenshots';A=R/'artifacts/product-film';O=R/'submission/output';W=R/'.local/focus-film';W.mkdir(parents=True,exist_ok=True)
WIDTH,HEIGHT,FPS=1920,1080,30
BG=(248,248,250);INK='#1D1D1F';GREEN='#006241';MUTED='#747477'
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n,index=1)
def text(d,x,y,t,n=56,color=INK,b=False):d.multiline_text((x,y),t,font=font(n,b),fill=color,spacing=18)
def centered(d,y,t,n=76,color=INK,b=False):
 for line in t.split('\n'):
  text(d,(WIDTH-d.textlength(line,font=font(n,b)))/2,y,line,n,color,b);y+=n+20
# Crop coordinates are relative to the app viewport, not reconstructed UI.
plan=[
 dict(key='intro',duration=3,title='DriveQuest2'),
 dict(key='question',duration=4,title='영상으로 나의 운전을\n교정할 수 있다면?'),
 dict(key='summary',duration=4,title='오늘의 주행 요약',file='today.png',crop=[40,149,1100,332]),
 dict(key='events',duration=4,title='돌아보고 싶은 순간',file='today.png',crop=[40,561,1642,853]),
 dict(key='playback',duration=10,title='두 경로를 한눈에',video='left-clean.mp4',crop=[927,253,2459,1115]),
 dict(key='monthly',duration=5,title='한 달의 변화',file='monthly.png',crop=[40,156,1642,496]),
 dict(key='missions',duration=4,title='다음 운전의 작은 목표',file='achievements.png',crop=[40,492,1642,704]),
 dict(key='end',duration=4,title='DriveQuest2')]
assert sum(s['duration'] for s in plan)==38
logo=Image.open(R/'submission/reference/hmg-logo.png').convert('RGBA');logo.thumbnail((260,120))
prepared={}
for s in plan:
 if 'file' in s:
  im=Image.open(S/s['file']).convert('RGB').crop(s['crop']);im.save(W/(s['key']+'-component.png'));prepared[s['key']]=im
# Decode only the true playback viewport from current app capture.
play=W/'playback.rgb';subprocess.run(['ffmpeg','-v','error','-y','-ss','1.3','-i',str(A/'left-clean.mp4'),'-vf','crop=1532:862:927:253,scale=1440:810:flags=lanczos,fps=30,tpad=stop_mode=clone:stop_duration=2','-t','10','-pix_fmt','rgb24','-f','rawvideo',str(play)],check=True)
stream=play.open('rb')
output=O/'DriveQuest2-demo-38s.mp4';encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-map_metadata','-1','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
def ease(t):return 1-(1-max(0,min(1,t)))**3
elapsed=0;timeline=[]
for s in plan:
 key=s['key'];dur=s['duration'];is_brand=key in ('intro','end');basecolor=(13,43,34) if is_brand else BG
 for frame in range(dur*FPS):
  t=frame/FPS;intro=ease(t/.55);opacity=min(1,t/.22,(dur-t)/.18);canvas=Image.new('RGB',(WIDTH,HEIGHT),basecolor);d=ImageDraw.Draw(canvas)
  if is_brand:
   canvas.paste(logo,(104,80),logo)
   text(d,100,380,s['title'],118,'#FFFFFF',True)
   if key=='intro':text(d,106,550,'주차 후, 오늘의 운전을 돌아보다.',40,'#D0E4D8')
   else:text(d,106,554,'실제 앱 UI · 합성 주행 영상 · 고정 수치',29,'#D0E4D8')
   text(d,106,955,'2026 현대자동차그룹 차량용 앱 개발 공모전',28,'#C1D8CB')
  elif key=='question':
   centered(d,365+int(22*(1-intro)),s['title'],84,INK,True)
  else:
   text(d,100,74+int(12*(1-intro)),s['title'],58,INK,True)
   if key=='playback':
    raw=stream.read(1440*810*3)
    assert len(raw)==1440*810*3
    im=Image.frombytes('RGB',(1440,810),raw);target_w,target_h=1440,810;y=204
   else:
    im=prepared[key]
    scale=min(1640/im.width,650/im.height)
    target_w,target_h=round(im.width*scale),round(im.height*scale)
    y=round(550-target_h/2)
   # Gentle entrance, then a stable hold; no perpetual zoom while reading.
   scale=.97+.03*intro;w,h=round(target_w*scale),round(target_h*scale)
   im=im.resize((w,h),Image.Resampling.LANCZOS);x=(WIDTH-w)//2;y+=round(18*(1-intro))
   mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=20,fill=255)
   shadow=Image.new('RGBA',(WIDTH,HEIGHT),(0,0,0,0));sd=ImageDraw.Draw(shadow);sd.rounded_rectangle((x,y+12,x+w,y+h+12),radius=20,fill=(0,0,0,22));shadow=shadow.filter(ImageFilter.GaussianBlur(18));canvas=Image.alpha_composite(canvas.convert('RGBA'),shadow).convert('RGB')
   canvas.paste(im,(x,y),mask)
  # Fade toward the neutral stage at each boundary; keep the screenshot content intact.
  if opacity<1:canvas=Image.blend(Image.new('RGB',(WIDTH,HEIGHT),basecolor),canvas,max(0,opacity))
  if frame==min(60,dur*FPS-1):canvas.save(W/(key+'-review.png'))
  encoder.stdin.write(canvas.tobytes())
 timeline.append({**s,'start':elapsed});elapsed+=dur;print(key,'complete',flush=True)
encoder.stdin.close();assert encoder.wait()==0;stream.close();play.unlink()
(O/'DriveQuest2-38s-story.json').write_text(json.dumps({'duration_seconds':elapsed,'fps':30,'resolution':[WIDTH,HEIGHT],'audio':'none','reference':'https://www.youtube.com/watch?v=ykwG0I8UGjg','reference_usage':'Visual presentation study only; no reference footage/audio/assets incorporated','editing':'Isolated crops of current UI, single concise heading, short fade/rise entrance, full 10-second playback emphasis','scenes':timeline},ensure_ascii=False,indent=2))
print('DONE',elapsed,flush=True)
