#!/usr/bin/env python3
import subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=[str(R.parent/'DriveQuest/.local/android-sdk/platform-tools/adb'),'-s','emulator-5554'];o=R/'artifacts/product-film'
def cmd(*a):subprocess.run(b+list(a),check=True,stdout=subprocess.DEVNULL)
def tap(x,y):cmd('shell','input','tap',str(x),str(y));time.sleep(2)
def shot(n):
 with (o/(n+'.png')).open('wb') as f:subprocess.run(b+['exec-out','screencap','-p'],stdout=f,check=True)
def record(n,action=None):
 p=subprocess.Popen(b+['shell','screenrecord','--bit-rate','14000000','--time-limit','12','/sdcard/dq2-'+n+'.mp4']);time.sleep(1)
 if action:action()
 time.sleep(1);shot(n);p.wait();cmd('pull','/sdcard/dq2-'+n+'.mp4',str(o/(n+'.mp4')))
cmd('shell','am','force-stop','io.drivequest2.app.debug');cmd('shell','am','start','-n','io.drivequest2.app.debug/io.drivequest2.app.MainActivity');time.sleep(6)
shot('today-clean')
record('left-clean',lambda:tap(1170,720));tap(2415,288)
record('right-clean',lambda:tap(1170,870));tap(2415,288)
tap(1340,140);time.sleep(2);record('monthly-clean')
cmd('shell','input','swipe','1800','1160','1800','660','900');time.sleep(3);shot('achievements-clean')
print('final capture done',flush=True)
