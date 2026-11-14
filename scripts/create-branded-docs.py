from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import textwrap,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'submission/current';templates=ROOT/'submission/current/templates'
sections=[
('앱 한 줄 소개','주차 후 오늘의 회전 장면과 두 경로를 나란히 보며, 다음 운전에서 바꿀 한 가지를 찾는 주행 복습 앱입니다.'),
('기획 배경','집에 도착하고 나서야 아까 그 회전이 마음에 걸릴 때가 있습니다. 너무 크게 돌았는지, 어디서 방향을 틀었는지 기억만으로는 짚기 어렵습니다. 블랙박스를 처음부터 돌려보는 일도 번거롭습니다. DriveQuest는 하루의 운전을 마친 뒤, 커브와 회전 구간만 골라 차 안에서 짧게 돌아보는 경험을 제안합니다. 첫 대상은 좌·우회전과 유턴이 아직 익숙하지 않은 운전자입니다.'),
('앱 주요 기능 및 차량 특화 요소','오늘의 주행에서는 하루 요약, 회전별 횟수와 정확도, 시간순 영상 목록을 보여줍니다. 영상을 열면 초록 실선과 주황 점선으로 비교 경로와 주행 경로를 함께 볼 수 있습니다. 재생을 멈추거나 원하는 시점으로 이동해 차이를 살펴봅니다. 내 주행실력에서는 월간 성적 변화와 회전별 정확도, 운전 습관과 도전과제를 한곳에서 확인합니다.\n차량 화면에서는 운전 직후 기억이 남아 있을 때 같은 전방 시점으로 복습할 수 있습니다. AAOS의 주행 제한 상태를 확인하고, 제한되거나 확인되지 않으면 화면을 차단합니다. 현재는 합성 영상 24개와 고정 수치로 이 흐름을 구현했습니다. 전면 카메라 영상을 실제로 수집하거나 주행 정확도를 측정하는 기능은 아직 없습니다.'),
('주요 사용 시나리오','운전자가 하루 운행을 마치고 집 주차장에 주차합니다. 앱을 열어 오늘 주행 요약을 읽고, 마음에 걸렸던 회전을 시간순 목록에서 찾습니다. 영상에서는 각 상황의 최적 경로를 살펴봅니다. 현재의 ‘최적 경로’는 콘셉트용 비교 궤적이며 실도로 최적화 결과는 아닙니다. 이어 내 주행실력에서 한 달의 변화를 확인하고 다음 운전에서 신경 쓸 습관 하나를 정합니다. 현재 시연에서는 오전·점심·저녁의 좌회전 8개, 우회전 9개, 유턴 2개, 커브 5개를 볼 수 있습니다. 실제 운행 기록을 불러오는 과정은 향후 구현 범위입니다.'),
('개발 계획','현재 Kotlin·Compose 화면, MP4 재생, 월간 그래프, 도전과제 UI를 구현했고 Pleos Connect 2.1.0 / API 34 / 2560×1440에서 확인했습니다. Android Car API의 CarUxRestrictions를 사용하며 앱이 비활성화되면 재생을 멈춥니다. Vehicle SDK 2.3.2 의존성은 유지하지만, 이 버전의 점수와 영상은 차량 신호로 생성되지 않습니다.\n다음 단계는 사용자 동의를 받은 영상과 시각·차량 자세 데이터를 연결하는 것입니다. 공개 API와 권한으로 가능한 수집 범위를 먼저 확인하고, 차로 경계·차량 폭·교통 상황을 반영한 비교 경로를 검토하겠습니다. 정보가 부족하면 경로와 점수 제시를 보류합니다. 실제 앞유리 HUD 출력, 차량 제어, 페달 잠금은 현재 기능이 아닙니다.'),
('기대효과 및 발전 가능성','막연히 운전을 잘했는지 평가받기보다, 어떤 회전에서 무엇을 바꿀지 스스로 설명할 수 있게 하는 것이 목표입니다. 초기에는 회전이 어려운 운전자와 운전 교육기관을 대상으로 복습 흐름을 검토하려 합니다. 같은 영상에 대한 단순 재생과 두 경로 비교를 나눠, 차이를 이해하는지와 안내를 지나치게 믿지 않는지를 확인할 계획입니다. 이후 새로운 구간에서 판단이 달라지는지도 살펴보겠습니다. 실제 운전 실력이나 사고 위험이 개선됐다는 결과는 아직 없으며, 이용자 수·유지율 역시 측정 전입니다.'),
('참고자료','첨부 영상: DriveQuest-demo-40s-music.mp4\n추가 소개서: DriveQuest-제품소개.pdf\n검증 환경과 범위: DriveQuest-DEMO_GUIDE.txt\n소스·release APK 링크와 최종 commit hash는 공유 위치 및 제출 빌드 확정 후 기재해야 합니다. 현재 촬영 APK는 debug 검증본입니다.'),
('숏폼 링크','미제출')]
d=Document(ROOT/'submission/reference/contest-application-consent.docx')
for p in d.paragraphs:
 if p.text.startswith('참가 단위:'):p.text='참가 단위: □ 개인           ■ 팀'
 elif p.text.startswith('참가 부문:'):p.text='참가 부문: □ 대학(원)생    ■ 일반(스타트업 포함)'
 elif p.text.startswith('팀명(개인 참가'):p.text='팀명(개인 참가 시 성명): 로보티즈 삼형제'
 elif p.text.lstrip().startswith('앱명 / 프로젝트명:'):p.text='앱명 / 프로젝트명: DriveQuest'
 elif p.text.startswith('팀명(팀 참가 시)'):p.text='팀명(팀 참가 시): 로보티즈 삼형제'
for i,(_,body) in enumerate(sections):
 cell=d.tables[i+1].cell(0,0);cell.text=body
 for p in cell.paragraphs:
  for run in p.runs:
   run.font.name='Noto Sans CJK KR';run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Sans CJK KR');run.font.size=Pt(10)
d.core_properties.author='';d.core_properties.last_modified_by='';d.core_properties.title='DriveQuest 공모전 접수양식'
d.save(templates/'DriveQuest-접수양식_본인정보서명필요.docx')
# Separate editable project narrative; no participant information.
b=Document();b.core_properties.author='';b.core_properties.last_modified_by='';b.add_heading('DriveQuest',0);b.add_paragraph('오늘의 운전을, 내일의 감각으로.')
for title,body in sections[:6]:b.add_heading(title,1);b.add_paragraph(body)
b.add_page_break();b.add_heading('최신 앱 화면',1)
for key,label in [('welcome-clean','첫 인사'),('today-clean','오늘의 주행'),('left-clean','경로 비교 재생'),('monthly-clean','월간 기록')]:
 from PIL import Image
 from docx.shared import Inches
 src=ROOT/'artifacts/product-film'/f'{key}.png'
 if src.exists():
  crop=ROOT/'artifacts/product-film'/f'{key}-doc.png';Image.open(src).crop((853,90,2533,1300)).save(crop)
  b.add_paragraph(label);b.add_picture(str(crop),width=Inches(5.7))
b.save(out/'DriveQuest-제품소개.docx')
(templates/'접수메일_초안.txt').write_text('''수신: appdevchallenge@hyundai-partners.com
참조: [팀원 전원 이메일]
제목: [차량용 앱 개발 공모전] 로보티즈 삼형제_[대표자명]

안녕하세요. 일반 부문 팀 참가로 DriveQuest를 제출합니다.
DriveQuest는 하루 운행을 마친 뒤 주차 상태에서 회전 장면과 경로를 돌아보는 앱입니다.

첨부: 본인정보·동의·서명을 완성한 공식 접수양식, DriveQuest-demo-40s-music.mp4, DriveQuest-제품소개.pdf
개발 산출물: [소스와 서명된 release APK를 담은 실제 공유 링크]
최종 commit hash: [저장소를 사용할 경우 실제 최종 커밋]
APK 위치: [실제 release APK 경로]

현재 소개 영상은 Pleos 에뮬레이터에서 실행한 프로토타입 화면입니다. 영상과 수치는 콘셉트 데이터이며 실제 주행 수집·분석 결과는 아닙니다.
검토 부탁드립니다. 감사합니다.

※ 대괄호를 완성하고, 첨부·공유하지 않을 항목은 지운 뒤 발송하세요. 이 파일은 발송되지 않았습니다.
''')
(out/'제출자료_읽어주세요.txt').write_text('''DriveQuest 새 제작본 · DriveQuest1 원본 보존

1. DriveQuest-demo-40s-music.mp4: 설명 카드와 실제 에뮬레이터 화면으로 구성한 공개 시연 영상. 배경음악 포함, 참가자 실명 없음.
2. DriveQuest-제품소개.pdf / .docx: 추가 소개서. 공식 접수양식을 대신하지 않음.
3. templates/DriveQuest-접수양식_본인정보서명필요.docx: 공식 원본의 항목·순서를 유지한 기획 내용 작성본.
4. templates/접수메일_초안.txt: 사용자가 완성해 보낼 메일.
5. DriveQuest-DEMO_GUIDE.txt: 시연 순서와 구현 범위.

보내기 전
[ ] 대표자·팀원 정보, 역할, 인원, 날짜를 본인이 작성
[ ] 참가자 전원 동의 여부와 본인 서명·서명일 작성
[ ] DOCX를 Word/LibreOffice에서 열어 페이지 나눔과 빈칸 확인
[ ] 소스와 실행 가능한 서명된 release APK 준비: 현재 앱 검증본은 debug이며 이 묶음에 제출 APK는 포함하지 않음
[ ] 공개 링크와 APK 경로 확정; GitHub 방식이면 최종 commit hash도 기재
[ ] 공유 자료에 실명·연락처·비밀키가 없는지 확인
[ ] 팀원 전원 CC, 첨부파일 확인 후 직접 이메일 발송

공식 재확인일: 2026-11-14. 마감: 2026-11-15 23:59 KST.
필수: 공식 접수양식 및 참가자별 동의·서명. 영상·소스/APK·추가 소개서는 선택 자료.
commit hash 하나만으로는 접수가 완료되지 않습니다.
근거: https://appdevchallenge.auto-hmg.io/guide/submission
추가 안내: https://appdevchallenge.auto-hmg.io/notice/c0a1a000-2026-4923-8000-000000000007
''')
(out/'DriveQuest-DEMO_GUIDE.txt').write_text('''DriveQuest 시연 가이드

목적: 집에 주차한 뒤 그날의 회전 장면을 짧게 돌아보는 경험을 설명한다.
영상은 40초 편집이며 공식 시간 제한을 뜻하지 않는다.

1. 질문: 영상으로 나의 운전을 교정할 수 있다면?
2. 오늘의 주행: 요약과 회전별 횟수, 시간순 목록을 보여준다.
3. 경로 비교: 재생 장면에서 각 상황의 최적 경로를 살펴보는 흐름을 설명한다.
4. 월간 기록: 전체 탭을 보여준 뒤 그래프와 주행타입별 월간 정확도를 각각 설명한다.
5. 도전과제: 돌아보기의 반복 동기를 보여준다.
6. 범위: 실제 앱 UI, 합성 영상·고정 수치. 실주행 수집과 경로 분석은 다음 단계다.

Pleos Connect 2.1.0 / API 34 / 2560×1440. 영상에서는 앱 영역을 확대한다.
현재 촬영은 io.drivequest2.app.debug 검증본이다. 앱 내부 영상은 직접 제작한 합성 장면이다.
실차 HUD·카메라·라이다 연동, 운전 실력 개선 효과, 차량 잠금을 시연했다고 설명하지 않는다.
화면의 ‘최적 경로’는 고정 비교 궤적이며 실제 최적화 결과가 아니다.
발표자 질문 대응: 경로 선정 근거·카메라 접근·개인정보 보관은 제품화 전 검증할 항목이다.
''')
# Four designed, selectable-text PDF pages.
pdfmetrics.registerFont(TTFont('KR',str(ROOT/'.local/media-assets/NanumGothic.ttf')))
c=canvas.Canvas(str(out/'DriveQuest-제품소개.pdf'),pagesize=(595.28,841.89));c.setTitle('DriveQuest 제품 소개');c.setAuthor('')
W,H=595.28,841.89
pages=[('오늘의 운전을,\n내일의 감각으로.',[(sections[0][0],sections[0][1]),(sections[1][0],sections[1][1])],'today-clean'),('기억에 남은 회전.\n화면으로 다시.',[(sections[2][0],sections[2][1]),(sections[3][0],sections[3][1])],'left-clean'),('한 번의 점수보다,\n쌓여가는 변화.',[(sections[5][0],sections[5][1])],'monthly-clean'),('지금 보여드리는 것.\n다음에 검증할 것.',[(sections[4][0],sections[4][1]),('제작·검증','Pleos Connect 에뮬레이터에서 실행한 화면입니다. 단위 테스트 4개, UI 테스트 3개, lint 및 debug 빌드를 확인했습니다. 영상과 점수는 고정 콘셉트 데이터입니다. 실제 주행 분석과 학습 효과는 검증 전입니다. 이 문서는 공식 접수양식에 덧붙이는 소개 자료입니다.')],None)]
for n,(title,parts,shot) in enumerate(pages):
 c.setFillColor(HexColor('#F5F1E8'));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor('#006241'));c.setFont('KR',12);c.drawString(42,H-43,'DriveQuest  /  PRODUCT NOTE')
 y=H-100;c.setFillColor(HexColor('#18372C'));c.setFont('KR',28)
 for line in title.split('\n'):c.drawString(42,y,line);y-=39
 y-=22
 for heading,body in parts:
  c.setFillColor(HexColor('#006241'));c.setFont('KR',13);c.drawString(42,y,heading);y-=23
  c.setFillColor(HexColor('#35413A'));c.setFont('KR',10.5)
  for para in body.split('\n'):
   line=''
   for ch in para:
    if pdfmetrics.stringWidth(line+ch,'KR',10.5)>510:
     c.drawString(42,y,line);y-=17;line=ch
    else:line+=ch
   if line:c.drawString(42,y,line);y-=17
   y-=7
  y-=14
 if shot and (ROOT/'artifacts/product-film'/f'{shot}.png').exists():
  from PIL import Image
  im=Image.open(ROOT/'artifacts/product-film'/f'{shot}.png').crop((853,90,2533,1300));tmp=ROOT/'artifacts/product-film'/f'{shot}-crop.png';im.save(tmp)
  height=min(280,y-75);width=height*1680/1210
  c.drawImage(str(tmp),(W-width)/2,y-height,width,height)
 c.setFillColor(HexColor('#8E8D82'));c.setFont('KR',9);c.drawString(42,30,'2026 현대자동차그룹 차량용 앱 개발 공모전 · 출품작 소개');c.drawRightString(W-42,30,f'{n+1:02d} / 04');c.showPage()
c.save()
print('documents created')
