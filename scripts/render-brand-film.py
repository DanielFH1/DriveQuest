#!/usr/bin/env python3
"""40s overview-to-detail cut, current UI only, licensed background music."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[1];S=R/'submission/output/screenshots';A=R/'artifacts/product-film';O=R/'submission/current';W=R/'.local/brand-film';W.mkdir(parents=True,exist_ok=True)
WIDTH,HEIGHT,FPS=1920,1080,30;BG=(248,248,250);INK='#1D1D1F';MUTED='#58585E'
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n,index=1)
def text(d,x,y,t,n=56,color=INK,b=False):d.multiline_text((x,y),t,font=font(n,b),fill=color,spacing=16)
plan=[
 dict(key='intro',duration=4,title='영상으로 나의 운전을\n교정할 수 있다면?'),
 dict(key='today-overview',duration=3,title='오늘의 주행',file='today.png',overview=True),
 dict(key='summary',duration=4,title='오늘의 주행 요약',body='잘한 점과 아쉬운 점을\n먼저 짚어봅니다.',file='today.png',crop=[40,149,1100,332]),
 dict(key='events',duration=4,title='영상으로 돌아보기',body='기억에 남은 순간을\n시간으로 찾아봅니다.',file='today.png',crop=[40,561,1000,853]),
 dict(key='playback',duration=6,title='주행 경로 비교',body='각 상황의 최적 경로를\n살펴봅니다.',video='left-clean.mp4'),
 dict(key='skills-overview',duration=3,title='내 주행실력',file='monthly.png',overview=True),
 dict(key='monthly',duration=4,title='이번 달 주행 기록',body='어떤 날이 좋았는지,\n한 달의 흐름을 봅니다.',file='monthly.png',crop=[40,156,855,496]),
 dict(key='accuracy',duration=4,title='주행타입별 월간 정확도',body='좌회전부터 커브까지,\n이번 달 정확도를 봅니다.',file='monthly.png',crop=[40,521,1642,655]),
 dict(key='missions',duration=4,title='도전과제',body='다음 운전에서 지킬\n작은 목표를 정합니다.',file='achievements.png',crop=[40,492,832,704]),
 dict(key='end',duration=4,title='DriveQuest')]
assert sum(s['duration'] for s in plan)==40
logo=Image.open(R/'submission/reference/hmg-logo.png').convert('RGBA');logo.thumbnail((240,110))
prepared={}
for s in plan:
 if 'file' in s:
  im=Image.open(S/s['file']).convert('RGB')
  if 'crop' in s:im=im.crop(s['crop'])
  prepared[s['key']]=im
play=W/'playback.rgb';subprocess.run(['ffmpeg','-v','error','-y','-ss','2','-i',str(A/'left-clean.mp4'),'-vf','crop=1532:862:927:253,scale=1320:742:flags=lanczos,fps=30','-t','8','-pix_fmt','rgb24','-f','rawvideo',str(play)],check=True)
stream=play.open('rb');silent=W/'silent.mp4'
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-map_metadata','-1',str(silent)],stdin=subprocess.PIPE)
def ease(t):return 1-(1-max(0,min(1,t)))**3
elapsed=0;timeline=[]
for s in plan:
 key=s['key'];dur=s['duration'];brand=key in ('intro','end');base=(13,43,34) if brand else BG
 for f in range(dur*FPS):
  t=f/FPS;progress=ease(t/.5);alpha=min(1,t/.2,(dur-t)/.18);im=Image.new('RGB',(WIDTH,HEIGHT),base);d=ImageDraw.Draw(im)
  if brand:
   im.paste(logo,(100,75),logo)
   note='주행 영상은 합성이며, 수치는 임의로 구성했습니다.'
   text(d,WIDTH-80-d.textlength(note,font=font(23)),72,note,23,'#C5D8CF')
   if key=='intro':
    text(d,105,260,'DriveQuest',36,'#C5D8CF',True)
    text(d,100,385,s['title'],84,'white',True)
   else:
    text(d,100,365,'DriveQuest',118,'white',True)
    text(d,106,540,'오늘의 주행을 돌아보다.',42,'#D0E4D8')
    text(d,106,815,'Music: “Dream Culture” — Kevin MacLeod (incompetech.com)',22,'#BCCFC5')
    text(d,106,850,'CC BY 4.0 · creativecommons.org/licenses/by/4.0/ · 발췌·음량 조정',21,'#BCCFC5')
   text(d,106,700,'로보티즈 삼형제',31,'#D0E4D8')
   text(d,106,965,'2026 현대자동차그룹 차량용 앱 개발 공모전',27,'#C5D8CF')
  else:
   text(d,100,72,s['title'],58,INK,True)
   overview=s.get('overview',False)
   if key=='playback':
    raw=stream.read(1320*742*3);assert len(raw)==1320*742*3
    comp=Image.frombytes('RGB',(1320,742),raw);tw,th=1320,742;tx,ty=520,225
    text(d,100,460,s['body'],31,MUTED)
   else:
    comp=prepared[key]
    ratio=min((1200 if overview else 1100)/comp.width,(864 if overview else 650)/comp.height)
    tw,th=round(comp.width*ratio),round(comp.height*ratio)
    tx=(WIDTH-tw)//2 if overview else 720+(1100-tw)//2
    ty=175 if overview else 560-th//2
    if not overview:
     text(d,100,448,s['body'],35,MUTED)
     # Quiet reference-style leader from explanation to the isolated component.
     d.line((100,574,570,574),fill='#D4D4D8',width=2)
   scale=.98+.02*progress;w,h=round(tw*scale),round(th*scale);x=tx+(tw-w)//2;y=ty+round(12*(1-progress))
   comp=comp.resize((w,h),Image.Resampling.LANCZOS)
   mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=18,fill=255)
   sh=Image.new('RGBA',(WIDTH,HEIGHT));ImageDraw.Draw(sh).rounded_rectangle((x,y+10,x+w,y+h+10),radius=18,fill=(0,0,0,20));sh=sh.filter(ImageFilter.GaussianBlur(16));im=Image.alpha_composite(im.convert('RGBA'),sh).convert('RGB');im.paste(comp,(x,y),mask)
  if alpha<1:im=Image.blend(Image.new('RGB',(WIDTH,HEIGHT),base),im,max(0,alpha))
  if f==min(60,dur*FPS-1):im.save(W/(key+'-review.png'))
  enc.stdin.write(im.tobytes())
 timeline.append({**s,'start':elapsed});elapsed+=dur;print(key,flush=True)
enc.stdin.close();assert enc.wait()==0;stream.close();play.unlink()
output=O/'DriveQuest-demo-40s-music.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-ss','8','-i',str(R/'.local/music/Dream-Culture.mp3'),'-map','0:v:0','-map','1:a:0','-af','atrim=duration=40,asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-2:LRA=7,afade=t=in:st=0:d=1.2,afade=t=out:st=37:d=3','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','40','-map_metadata','-1','-movflags','+faststart',str(output)],check=True)
(O/'DriveQuest-40s-story.json').write_text(json.dumps({'duration_seconds':40,'fps':30,'reference_times':['4:43','5:50','7:48','13:30'],'music':{'title':'Dream Culture','artist':'Kevin MacLeod','license':'CC BY 4.0','source':'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300046','edits':'40-second excerpt from 00:08; normalized to -23 LUFS; fade in/out'},'scenes':timeline},ensure_ascii=False,indent=2))
print('DONE 40 seconds with music',flush=True)
