# DriveQuest2
- 기존 ../DriveQuest와 ../pleos-sample-vehicle-app을 수정하지 않는다.
- Kotlin 2.0.0 / AGP 8.8.2 / Gradle 8.10.2 / JDK17 / API35 / minSdk28 / Vehicle2.3.2 유지.
- domain: Android 비의존 기획 데이터·정책, data: 실제 안전 제한 모니터, ui: Compose와 VideoView.
- 현재 주행 데이터·점수·영상은 콘셉트용 고정 데이터다. 실데이터 공급자와 섞거나 실제 측정으로 보고하지 않는다.
- 사용자가 요청한 간결한 UI를 유지한다. 데이터 출처와 검증 한계는 README에 기록한다.
- AAOS unknown/restricted 차단, Activity 비활성화 시 즉시 영상 정지. 모의 데이터로 안전 제한 우회 금지.
- PRIVATE/CONTROL 권한, 실제 HUD·교통신호 판정·최적 경로 구현 주장 금지.
- 검증: scripts/build.sh assembleDebug testDebugUnitTest lintDebug. 연결 기기에서 connectedDebugAndroidTest.
- 기존 SDK/AVD·앱 데이터 보존. 비밀키나 개인정보를 프로젝트에 복사하지 않는다.
