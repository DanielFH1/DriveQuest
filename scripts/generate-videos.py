#!/usr/bin/env python3
"""Authored concept footage, not recorded roads or measured optimal trajectories.
Road geometry, middle divider and right lane paths use one world coordinate frame.
Event catalogue is read from Kotlin so UI counts and video resources cannot drift.
"""
from pathlib import Path
import math,random,subprocess,re,argparse,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'app/src/main/res/raw';THUMBS=ROOT/'app/src/main/res/drawable'
RAW.mkdir(exist_ok=True);THUMBS.mkdir(exist_ok=True)
W,H=960,540;FPS=20;SECONDS=10;FOCAL=620;HORIZON=235
CATALOG=ROOT/'app/src/main/java/io/drivequest2/app/domain/ReviewData.kt'
EVENTS=[(id,kind.lower(),int(h),int(m)) for id,kind,h,m in re.findall(r'DriveEvent\("(ev\d+)",Turn\.(\w+),(\d+),(\d+),\d+\)',CATALOG.read_text())]
assert len(EVENTS)==24
assert {k:sum(e[1]==k for e in EVENTS) for k in ['left','right','uturn','curve']}=={'left':8,'right':9,'uturn':2,'curve':5}

def route(kind,seed):
    r=4.8 if kind=='uturn' else 7 if kind!='curve' else (44+seed%6)
    angle=math.pi if kind=='uturn' else math.pi/2 if kind!='curve' else math.pi/3
    sign=-1 if kind in ('left','uturn') else 1
    points=[(0.,i*.5) for i in range(70)]
    steps=math.ceil(r*angle/.5)
    points.extend((sign*r*(1-math.cos(angle*i/steps)),35+r*math.sin(angle*i/steps)) for i in range(steps+1))
    x,z=points[-1]
    points.extend((x+sign*math.sin(angle)*i*.5,z+math.cos(angle)*i*.5) for i in range(1,111))
    if kind=='uturn':points=[(x+4.8,z) for x,z in points]
    return points

def render(event,preview=False):
    id,kind,hour,minute=event;number=int(id[2:]);rng=random.Random(number);path=route(kind,number);n=len(path)
    evening=hour>=18;noon=12<=hour<18
    intersection=kind in ('left','right')
    uturn=kind=='uturn'
    reference=0 if uturn else 2.4
    def normal(i):
        a=path[max(0,i-1)];b=path[min(n-1,i+1)];dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        return dz/length,-dx/length
    normals=[normal(i) for i in range(n)]
    def world(i,lateral=0,y=0):
        x,z=path[i];nx,nz=normals[i];return (x+nx*lateral,y,z+nz*lateral)
    def driven(i):return reference+.65*math.sin(math.pi*i/(n-1))**2*math.sin(i*.022+number*.25)
    # The divider is exactly halfway between both road edges for every cross section.
    for i in range(n):
        l=world(i,-5);r=world(i,5);c=world(i,0)
        assert abs((l[0]+r[0])/2-c[0])<1e-8 and abs((l[2]+r[2])/2-c[2])<1e-8
        assert reference-.7<=driven(i)<=reference+.7
    top=(44,59,84) if evening else (120,174,198) if noon else (137,174,183)
    bottom=(211,153,113) if evening else (223,234,226) if noon else (246,218,177)
    sky=Image.new('RGB',(W,H));d=ImageDraw.Draw(sky)
    for y in range(H):
        t=min(1,y/260);d.line((0,y,W,y),fill=tuple(int(a*(1-t)+b*t) for a,b in zip(top,bottom)))
    sun=(770 if evening else 180,205 if evening else 95 if noon else 155)
    d.ellipse((sun[0]-25,sun[1]-25,sun[0]+25,sun[1]+25),fill=(247,208,151) if evening else (255,241,202))
    d.polygon([(0,244),(100,212),(230,237),(380,215),(560,243),(720,219),(960,242),(960,H),(0,H)],fill=(72,89,79) if evening else (134,156,130))
    objects=[]
    for i in range(10,n-10,20):
        for side in [-1,1]:
            x,_,z=world(i,side*(15+rng.random()*3));height=4+rng.random()*3;width=3.5+rng.random()*2
            col=rng.choice([(200,190,170),(182,194,182),(205,178,151),(162,181,186)])
            objects.append(('house',x,z,height,width,col))
    for i in range(12,n-8,13):
        for side in [-1,1]:
            x,_,z=world(i,side*(8.7+rng.random()*1.1));objects.append(('tree',x,z,4+rng.random()*2,2.4+rng.random(),None))
    if uturn:
        objects=[]
        for z in range(-25,100,12):
            for side in (-1,1):
                objects.append(('house',side*19,z,5+rng.random()*2,4.5,(190,190,170)))
                objects.append(('tree',side*12,z+5,5,3,None))
        for z in range(-40,110,3):
            for side in (-1,1):objects.append(('straightRail',side*10.5,z,0,1,None))
        objects.append(('signal',10.6,47,5.8,1,(1,0)))
        objects.append(('signal',-10.6,28,5.8,1,(-1,0)))
    elif intersection:
        objects=[]
        for x in (-24,-15,15,24):
            for z in (10,23,60,74):
                objects.append(('house',x,z,5+rng.random()*2,4.5,(190,190,170)))
        for x in (-8,8):
            for z in (4,14,24,60,70,80):objects.append(('tree',x,z,5,3,None))
        for z in (34,50):
            for x in (-36,-24,-14,14,24,36):objects.append(('tree',x,z,5,3,None))
        # Signals on the far side of the intersection, facing each approach.
        for x,z,nx,nz in [(6.3,51,1,0),(-6.3,33,-1,0),(9,35.7,0,-1),(-9,48.3,0,1)]:
            objects.append(('signal',x,z,5.8,1,(nx,nz)))
        for z in list(range(2,27,3))+list(range(57,90,3)):
            for side in (-1,1):objects.append(('straightRail',side*5.8,z,0,1,None))
        for x in list(range(-50,-13,3))+list(range(14,55,3)):
            for side in (-1,1):objects.append(('straightRail',x,42+side*5.8,1,0,None))
    else:
        for i in (62,min(n-30,125),n-55):
            x,_,z=world(i,6.3);objects.append(('signal',x,z,5.8,1,normals[i]))
        for i in range(5,n-2,5):
            for side in (-1,1):
                x,_,z=world(i,side*5.8);objects.append(('rail',x,z,i,side,None))
    movie=RAW/f'{id}.mp4';proc=None
    if not preview:
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],stdin=subprocess.PIPE)
    frame_numbers=[10,60,115,180] if preview else range(FPS*SECONDS)
    for frame in frame_numbers:
        progress=frame/(FPS*SECONDS-1);at=30+progress*(n-115);idx=int(at);fraction=at-idx
        ca=world(idx,driven(idx));cb=world(idx+1,driven(idx+1));cx=ca[0]*(1-fraction)+cb[0]*fraction;cz=ca[2]*(1-fraction)+cb[2]*fraction
        na=normals[idx];nb=normals[idx+1];nx=na[0]*(1-fraction)+nb[0]*fraction;nz=na[1]*(1-fraction)+nb[1]*fraction;length=math.hypot(nx,nz);nx/=length;nz/=length;fx,fz=-nz,nx
        def depth(x,z):return (x-cx)*fx+(z-cz)*fz
        def project(x,y,z):
            dep=depth(x,z)
            if dep<1:return None
            return (W/2+FOCAL*((x-cx)*nx+(z-cz)*nz)/dep,HORIZON+FOCAL*(1.55-y)/dep)
        def poly(points,color):
            # Clip the ground plane against the camera, rather than dropping whole crossing arms.
            clipped=[]
            for a,b in zip(points,points[1:]+points[:1]):
                da,db=depth(a[0],a[2]),depth(b[0],b[2])
                if da>=1.01:clipped.append(a)
                if (da>=1.01)!=(db>=1.01):
                    t=(1.01-da)/(db-da);clipped.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
            if len(clipped)>=3:draw.polygon([project(*p) for p in clipped],fill=color)
        im=sky.copy();draw=ImageDraw.Draw(im)
        draw.rectangle((0,247,W,H),fill=(65,78,64) if evening else (141,155,123))
        if uturn:
            def rect(x1,z1,x2,z2,col):poly([(x1,0,z1),(x2,0,z1),(x2,0,z2),(x1,0,z2)],col)
            rect(-11,-100,11,180,(98,94,85) if evening else (135,130,116))
            rect(-9.6,-100,9.6,180,(53,61,67) if evening else (79,87,87))
            for side in (-1,1):rect(side*9.2-.06,-100,side*9.2+.06,180,(225,225,207))
            # Fixed straight carriageways; the centre opening permits a return into the opposite lane.
            for lo,hi in [(-100,31),(44,180)]:
                for x in (-.13,.13):rect(x-.04,lo,x+.04,hi,(239,218,151))
            for z in range(31,44,3):rect(-.10,z,.10,z+1.5,(239,218,151))
            # A road-direction arrow in each carriageway makes the reversal readable.
            for z in (5,20,55,75):
                for x,direction in [(4.8,1),(-4.8,-1)]:
                    rect(x-.12,z-1.5,x+.12,z+1.5,(225,225,207))
                    poly([(x-.65,0,z+direction),(x,0,z+direction*2),(x+.65,0,z+direction)],(225,225,207))
        elif intersection:
            def rect(x1,z1,x2,z2,col):poly([(x1,0,z1),(x2,0,z1),(x2,0,z2),(x1,0,z2)],col)
            road=(53,61,67) if evening else (79,87,87)
            walk=(98,94,85) if evening else (135,130,116)
            rect(-7,-100,7,180,walk);rect(-180,35,180,49,walk)
            rect(-5,-100,5,180,road);rect(-180,37,180,47,road)
            # Straight centre markings stop at the crossing: no curved-road boundaries through the junction.
            for z in range(-80,150,6):
                if not 27<z<56:rect(-.065,z,.065,z+3,(239,218,151))
            for x in range(-140,150,6):
                if not -14<x<12:rect(x,41.935,x+3,42.065,(239,218,151))
            for lo,hi in [(-100,30),(54,180)]:
                for side in (-1,1):rect(side*4.6-.05,lo,side*4.6+.05,hi,(225,225,207))
            for lo,hi in [(-180,-12),(12,180)]:
                for side in (-1,1):rect(lo,42+side*4.6-.05,hi,42+side*4.6+.05,(225,225,207))
            for t in range(-4,5,2):
                rect(t,31,t+1,34,(225,225,207));rect(t,50,t+1,53,(225,225,207))
                rect(-11,42+t,-8,43+t,(225,225,207));rect(8,42+t,11,43+t,(225,225,207))
            rect(.2,28,4.5,28.25,(225,225,207))
        else:
            for layer in range(3):
                for i in range(n-2,max(-1,idx-5),-1):
                    def strip(lo,hi,col):poly([world(i,lo),world(i+1,lo),world(i+1,hi),world(i,hi)],col)
                    if layer==0:strip(-7,7,(135,130,116) if not evening else (98,94,85))
                    elif layer==1:strip(-5,5,(79,87,87) if not evening else (53,61,67))
                    else:
                        strip(-4.65,-4.55,(215,215,197));strip(4.55,4.65,(215,215,197))
                        if i%14<7:strip(-.065,.065,(239,218,151))
        # Paint route annotations on the pavement before foreground road furniture.
        for is_actual,color in [(False,(72,218,157)),(True,(255,194,93))]:
            for i in range(min(n-2,idx+115),idx+3,-1):
                if is_actual and i%10>=6:continue
                p=project(*world(i,driven(i) if is_actual else reference,.055));q=project(*world(i+1,driven(i+1) if is_actual else reference,.055))
                if p and q:draw.line([p,q],fill=color,width=max(2,min(8,int(38/max(4,i-idx)))))
        for typ,x,z,h,w,col in sorted(objects,key=lambda o:depth(o[1],o[2]),reverse=True):
            dep=depth(x,z)
            if dep<2.5 or dep>170:continue
            p=project(x,0,z)
            if p is None or not -220<p[0]<W+220:continue
            unit=FOCAL/dep
            if typ=='straightRail':
                end=(x+3*h,z+3*w);rail=(131,148,145) if evening else (183,191,184)
                poly([(x,.78,z),(end[0],.78,end[1]),(end[0],1.03,end[1]),(x,1.03,z)],rail)
                a=project(x,0,z);b=project(x,1.08,z)
                if a and b:draw.line([a,b],fill=(101,116,111),width=max(1,int(.1*unit)))
            elif typ=='rail':
                i,side=int(h),int(w);j=min(n-1,i+5)
                rail=(183,191,184) if not evening else (131,148,145)
                poly([world(i,side*5.8,.78),world(j,side*5.8,.78),world(j,side*5.8,1.03),world(i,side*5.8,1.03)],rail)
                a=project(*world(i,side*5.8));b=project(*world(i,side*5.8,1.08))
                if a and b:draw.line([a,b],fill=(101,116,111),width=max(1,int(.1*unit)))
            elif typ=='house':
                roof=project(x,h,z);wide=w*unit;shade=tuple(int(c*(.58 if evening else .96)) for c in col)
                draw.rectangle((p[0]-wide/2,roof[1],p[0]+wide/2,p[1]),fill=shade)
                draw.polygon([(p[0],roof[1]),(p[0]+wide/2,roof[1]),(p[0]+wide/2,p[1]),(p[0],p[1])],fill=tuple(int(c*.88) for c in shade))
                draw.polygon([(p[0]-wide*.58,roof[1]),(p[0],roof[1]-wide*.25),(p[0]+wide*.58,roof[1])],fill=(83,93,82) if not evening else (51,57,63))
                for k in [-.24,.24]:
                    yc=roof[1]+(p[1]-roof[1])*.4;wc=max(1,wide*.15)
                    draw.rectangle((p[0]+k*wide-wc/2,yc,p[0]+k*wide+wc/2,yc+wc*1.3),fill=(241,204,134) if evening else (101,136,144))
            elif typ=='tree':
                crown=project(x,h*.72,z);top=project(x,h,z)
                draw.line([p,crown],fill=(103,86,64) if not evening else (67,60,49),width=max(2,int(unit*.23)))
                radius=w*unit/2;leaf=(70,114,80) if not evening else (39,77,63)
                draw.ellipse((crown[0]-radius,top[1],crown[0]+radius,crown[1]+radius*.55),fill=leaf)
                draw.ellipse((crown[0]-radius*.73,top[1]+radius*.13,crown[0]+radius*.25,crown[1]+radius*.25),fill=(88,133,87) if not evening else (50,91,70))
            else:
                pole=project(x,h,z);axisx,axisz=col
                arm=project(x-axisx*8,h,z-axisz*8)
                if pole:draw.line([p,pole],fill=(79,92,88),width=max(2,int(.13*unit)))
                if pole and arm:draw.line([pole,arm],fill=(79,92,88),width=max(2,int(.15*unit)))
                head=project(x-axisx*3.9,h-.45,z-axisz*3.9)
                hanger=project(x-axisx*3.9,h,z-axisz*3.9)
                if head and hanger:
                    draw.line([head,hanger],fill=(79,92,88),width=max(1,int(.08*unit)))
                    hw=1.8*unit;hh=.6*unit;hx,hy=head
                    draw.rounded_rectangle((hx-hw/2,hy-hh/2,hx+hw/2,hy+hh/2),radius=max(1,unit*.1),fill=(29,39,37))
                    for k,color in enumerate([(77,48,43),(78,69,42),(37,238,130)]):
                        lx=hx+(k-1)*.55*unit;r=.2*unit
                        draw.ellipse((lx-r,hy-r,lx+r,hy+r),fill=color)
        draw.polygon([(0,H),(0,H-27),(W*.18,H-45),(W*.5,H-52),(W*.82,H-45),(W,H-27),(W,H)],fill=(33,44,45))
        draw.line([(0,H-27),(W*.18,H-45),(W*.5,H-52),(W*.82,H-45),(W,H-27)],fill=(105,117,113),width=2)
        if preview:
            out=ROOT/'artifacts/road-review';out.mkdir(parents=True,exist_ok=True);im.save(out/f'{id}-{frame:03d}.png')
        else:
            if frame==60:im.save(THUMBS/f'{id}_thumb.jpg',quality=94)
            proc.stdin.write(im.tobytes())
    if proc:
        proc.stdin.close();assert proc.wait()==0
    print(id,kind,f'{hour:02d}:{minute:02d}','preview' if preview else 'rendered',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--ids',nargs='*');args=parser.parse_args()
    for event in EVENTS:
        if not args.ids or event[0] in args.ids:render(event,args.preview)
