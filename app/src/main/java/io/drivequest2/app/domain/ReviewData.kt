package io.drivequest2.app.domain

enum class Restriction { UNKNOWN, RESTRICTED, PARKED, NON_AUTOMOTIVE }
enum class Turn(val label: String, val accuracy: Int, val monthlyAccuracy: Int) { LEFT("좌회전",88,85), RIGHT("우회전",91,89), UTURN("유턴",82,78), CURVE("커브",94,90) }
data class DriveEvent(val id: String, val turn: Turn, val hour: Int, val minute: Int, val accuracy: Int) {
    val time get() = "%02d:%02d".format(hour,minute)
    val minutes get() = hour*60+minute
}
data class Achievement(val title: String, val done: Int, val target: Int, val icon: Int) {
    val progress get() = (done.toFloat()/target).coerceIn(0f,1f)
}
/** Deliberately authored concept fixtures, not measured telemetry or an inferred driver score. */
data class DailyGrade(val day: Int, val score: Float)
object ReviewData {
    // 0=E, 1=D, 2=C, 3=B, 4=A, 4.3=A+. Fractions retain +/- grade detail without axis suffixes.
    val monthlyGrades = listOf(3.7f,2.2f,4.1f,2.8f,3.6f,2.0f,4.3f,3.1f,2.4f,4.0f,2.6f,3.8f,2.1f,4.2f,3.3f)
        .mapIndexed { index,score -> DailyGrade(index+1,score) }

    val events = listOf(
        DriveEvent("ev01",Turn.LEFT,8,5,87),
        DriveEvent("ev02",Turn.RIGHT,8,12,90),
        DriveEvent("ev03",Turn.LEFT,8,18,88),
        DriveEvent("ev04",Turn.RIGHT,8,24,89),
        DriveEvent("ev05",Turn.UTURN,8,31,81),
        DriveEvent("ev06",Turn.CURVE,8,38,93),
        DriveEvent("ev07",Turn.RIGHT,8,46,92),
        DriveEvent("ev08",Turn.LEFT,8,54,86),
        DriveEvent("ev09",Turn.RIGHT,12,4,94),
        DriveEvent("ev10",Turn.LEFT,12,13,90),
        DriveEvent("ev11",Turn.CURVE,12,25,95),
        DriveEvent("ev12",Turn.RIGHT,12,38,91),
        DriveEvent("ev13",Turn.LEFT,12,49,89),
        DriveEvent("ev14",Turn.CURVE,13,2,94),
        DriveEvent("ev15",Turn.RIGHT,13,16,88),
        DriveEvent("ev16",Turn.LEFT,13,27,87),
        DriveEvent("ev17",Turn.CURVE,18,4,95),
        DriveEvent("ev18",Turn.RIGHT,18,12,93),
        DriveEvent("ev19",Turn.LEFT,18,20,90),
        DriveEvent("ev20",Turn.UTURN,18,29,83),
        DriveEvent("ev21",Turn.RIGHT,18,37,91),
        DriveEvent("ev22",Turn.CURVE,18,44,93),
        DriveEvent("ev23",Turn.LEFT,18,51,87),
        DriveEvent("ev24",Turn.RIGHT,18,58,91)
    )
    val achievements = listOf(
        Achievement("신호 지키기 100회",36,100,0),Achievement("차로 변경 전 방향지시등 50회",32,50,1),
        Achievement("정지선 앞 멈추기 50회",28,50,2),Achievement("제한속도 지키기 30회",21,30,3),
        Achievement("부드러운 좌회전 30회",19,30,4),Achievement("부드러운 우회전 30회",24,30,5),
        Achievement("여유로운 유턴 20회",8,20,6),Achievement("안정적인 커브 30회",22,30,7),
        Achievement("보행자에게 양보 20회",12,20,8),Achievement("하루 주행 돌아보기 7회",4,7,9)
    )
    fun playbackAllowed(automotive: Boolean, restriction: Restriction, foreground: Boolean) =
        foreground && if(automotive) restriction==Restriction.PARKED else restriction==Restriction.NON_AUTOMOTIVE
}
