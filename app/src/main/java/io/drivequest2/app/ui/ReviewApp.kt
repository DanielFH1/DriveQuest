package io.drivequest2.app.ui

import android.net.Uri
import android.graphics.Paint
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.platform.LocalDensity
import android.widget.VideoView
import androidx.activity.compose.BackHandler
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.compose.foundation.*
import androidx.compose.ui.input.nestedscroll.NestedScrollConnection
import androidx.compose.ui.input.nestedscroll.NestedScrollSource
import androidx.compose.ui.input.nestedscroll.nestedScroll
import androidx.compose.ui.unit.Velocity
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.*
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlinx.coroutines.delay
import io.drivequest2.app.domain.*

private val Beige=Color(0xFFF5F1E8)
private val Green=Color(0xFF006241)
private val Ink=Color(0xFF202720)
private val TimeColor=Color(0xFF99876B)
private val Track=Color(0xFFE9E6DC)
private val White=Color.White
private fun Turn.color()=when(this) { Turn.LEFT->Color(0xFFE89750);Turn.RIGHT->Color(0xFF75B5D5);Turn.UTURN->Color(0xFF922BEE);Turn.CURVE->Color(0xFF80BA28) }

@Composable fun ReviewApp(allowed:Boolean) {
    var entered by rememberSaveable { mutableStateOf(false) }
    var tab by rememberSaveable { mutableIntStateOf(0) }
    var selected by remember { mutableStateOf<DriveEvent?>(null) }
    LaunchedEffect(allowed) { if(!allowed)selected=null }
    MaterialTheme(colorScheme=lightColorScheme(primary=Green,background=Beige,surface=White,onSurface=Ink)) {
        Box(Modifier.fillMaxSize().background(Beige)) {
            if(!allowed) {
                Text("주차 후 확인해 주세요",Modifier.align(Alignment.Center),color=Green,fontSize=30.sp)
            } else if(!entered) {
                Greeting(Modifier.align(Alignment.Center)) { entered=true;tab=0 }
            } else {
                Column(Modifier.fillMaxSize().padding(horizontal=40.dp)) {
                    Row(Modifier.fillMaxWidth().height(98.dp),verticalAlignment=Alignment.CenterVertically) {
                        Text("DriveQuest",color=Green,fontSize=26.sp,fontWeight=FontWeight.SemiBold)
                        Spacer(Modifier.width(65.dp))
                        listOf("오늘의 주행","내 주행실력").forEachIndexed { index,title ->
                            Column(Modifier.width(165.dp).fillMaxHeight().clickable { tab=index;selected=null },horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center) {
                                Spacer(Modifier.height(12.dp))
                                Text(title,color=if(tab==index)Green else TimeColor,fontSize=21.sp,fontWeight=if(tab==index)FontWeight.Bold else FontWeight.Normal)
                                Spacer(Modifier.height(17.dp))
                                Box(Modifier.width(50.dp).height(3.dp).background(if(tab==index)Green else Color.Transparent,RoundedCornerShape(2.dp)))
                            }
                        }
                    }
                    if(tab==0) DailyPage { selected=it } else SkillsPage()
                }
                if(selected!=null) EventPlayer(selected!!,onClose={selected=null})
                BackHandler { if(selected!=null)selected=null else entered=false }
            }
        }
    }
}
@Composable private fun Greeting(modifier:Modifier,onFinished:()->Unit) {
    val opacity=remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        opacity.animateTo(1f,tween(1100,easing=FastOutSlowInEasing))
        delay(1100)
        opacity.animateTo(0f,tween(600))
        onFinished()
    }
    Text("오늘의 주행을 함께 확인해볼까요?",
        modifier.graphicsLayer { alpha=opacity.value;translationY=(1f-opacity.value)*20.dp.toPx() },
        style=TextStyle(brush=Brush.verticalGradient(listOf(Green,Color(0xFF5F9F7E))),fontSize=42.sp,fontWeight=FontWeight.Bold))
}
private fun Modifier.reveal(progress:Float,delay:Float)=graphicsLayer {
    val fraction=((progress-delay)/.4f).coerceIn(0f,1f)
    alpha=fraction;translationY=(1f-fraction)*16.dp.toPx()
}
@Composable private fun Bullet(text:String,modifier:Modifier=Modifier,color:Color=TimeColor) {
    Row(modifier,horizontalArrangement=Arrangement.spacedBy(10.dp)) {
        Text("•",color=Green,fontSize=18.sp)
        Text(text,color=color,fontSize=17.sp,lineHeight=26.sp)
    }
}
@Composable private fun DailySummary() {
    Column(verticalArrangement=Arrangement.spacedBy(13.dp)) {
        Text("오늘 주행 요약",color=Green,fontSize=23.sp,fontWeight=FontWeight.SemiBold)
        Column(Modifier.fillMaxWidth().background(White,RoundedCornerShape(20.dp)).padding(horizontal=28.dp,vertical=22.dp),verticalArrangement=Arrangement.spacedBy(13.dp)) {
            Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(28.dp)) {
                Text("A-",color=Green,fontSize=57.sp,fontWeight=FontWeight.Medium)
                Text("대체로 괜찮은 운행이었습니다",color=Ink,fontSize=25.sp,fontWeight=FontWeight.Medium)
            }
            Column(verticalArrangement=Arrangement.spacedBy(5.dp)) {
                Bullet("우회전이 특히 향상되었습니다")
                Bullet("유턴 시 더 작게 돌 필요가 있습니다")
            }
        }
    }
}
@Composable private fun MonthlyReview() {
    Column(verticalArrangement=Arrangement.spacedBy(15.dp)) {
        Text("이번달 주행 기록",color=Green,fontSize=25.sp,fontWeight=FontWeight.SemiBold)
        Row(Modifier.fillMaxWidth().background(White,RoundedCornerShape(20.dp)).padding(24.dp),horizontalArrangement=Arrangement.spacedBy(35.dp),verticalAlignment=Alignment.CenterVertically) {
            GradeChart(Modifier.weight(1.1f).height(292.dp))
            Column(Modifier.weight(1f),verticalArrangement=Arrangement.spacedBy(15.dp)) {
                Bullet("안전 운행하는 드라이버",color=Green)
                Bullet("지난달에 비해 우회전 실력이 향상되었습니다")
                Bullet("정지선 침범은 주의가 필요해보입니다")
                Bullet("유턴 시 더 작게 도는 습관이 필요합니다")
                Bullet("야간 운행 시 정확도가 평균 사용자보다 8% 높습니다")
            }
        }
    }
}
@Composable private fun GradeChart(modifier:Modifier) {
    val density=LocalDensity.current
    val labelSize=with(density) { 15.sp.toPx() }
    Canvas(modifier.semantics { contentDescription="이번달 주행 기록, 11월 1일부터 15일까지 일별 15개 점, C부터 A+ 사이 변동" }) {
        val left=35.dp.toPx();val right=size.width-24.dp.toPx();val top=12.dp.toPx();val bottom=size.height-36.dp.toPx()
        val paint=Paint(Paint.ANTI_ALIAS_FLAG).apply { color=TimeColor.toArgb();textSize=labelSize }
        val values=ReviewData.monthlyGrades
        fun x(day:Int)=left+(right-left)*(day-1)/(values.last().day-1)
        fun y(score:Float)=bottom-(bottom-top)*score/4.5f
        listOf("E","D","C","B","A").forEachIndexed { index,label ->
            val at=y(index.toFloat())
            drawLine(Track,Offset(left,at),Offset(right,at),1.dp.toPx())
            drawContext.canvas.nativeCanvas.drawText(label,0f,at+labelSize*.35f,paint)
        }
        for(day in 1..values.last().day step 7) {
            val label="11/$day"
            drawContext.canvas.nativeCanvas.drawText(label,x(day)-paint.measureText(label)/2,size.height-3.dp.toPx(),paint)
        }
        val line=Path().apply { values.forEachIndexed { index,grade -> if(index==0)moveTo(x(grade.day),y(grade.score)) else lineTo(x(grade.day),y(grade.score)) } }
        val area=Path().apply { addPath(line);lineTo(x(values.last().day),bottom);lineTo(left,bottom);close() }
        drawPath(area,Brush.verticalGradient(listOf(Green.copy(alpha=.13f),Green.copy(alpha=.01f)),top,bottom))
        drawPath(line,Green,style=Stroke(2.5.dp.toPx(),cap=StrokeCap.Round))
        values.forEach { grade ->
            val point=Offset(x(grade.day),y(grade.score))
            drawCircle(White,5.dp.toPx(),point);drawCircle(Green,3.4.dp.toPx(),point)
        }
    }
}
@Composable private fun SummaryCards(accuracy:Boolean) {
    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(18.dp)) {
        Turn.entries.forEach { turn ->
            Column(Modifier.weight(1f).background(White,RoundedCornerShape(20.dp)).padding(24.dp),verticalArrangement=Arrangement.spacedBy(13.dp)) {
                Text(turn.label,color=turn.color(),fontSize=21.sp,fontWeight=FontWeight.SemiBold)
                Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.Bottom) {
                    Text(if(accuracy)turn.monthlyAccuracy.toString() else ReviewData.events.count { it.turn==turn }.toString(),fontSize=40.sp,color=Ink,fontWeight=FontWeight.Medium)
                    Text(if(accuracy)" %" else " 회",Modifier.padding(bottom=7.dp),fontSize=17.sp,color=TimeColor)
                    if(!accuracy) {
                        Spacer(Modifier.weight(1f))
                        Column(horizontalAlignment=Alignment.End,verticalArrangement=Arrangement.spacedBy(4.dp)) {
                            Text("정확도",color=TimeColor,fontSize=13.sp)
                            Text("${turn.accuracy}%",color=TimeColor,fontSize=24.sp,fontWeight=FontWeight.Normal)
                        }
                    }
                }
            }
        }
    }
}
@Composable private fun DailyPage(onOpen:(DriveEvent)->Unit) {
    val context=LocalContext.current
    val slowerScroll=remember { object:NestedScrollConnection {
        override fun onPreScroll(available:Offset,source:NestedScrollSource):Offset =
            if(source==NestedScrollSource.Drag) Offset(0f,available.y*.96f) else Offset.Zero
        override suspend fun onPreFling(available:Velocity):Velocity = Velocity(0f,available.y*.99f)
    } }
    val appearance=remember { Animatable(0f) }
    LaunchedEffect(Unit) { appearance.animateTo(1f,tween(1450,easing=FastOutSlowInEasing)) }
    Column(Modifier.fillMaxSize()) {
        Spacer(Modifier.height(10.dp))
        Box(Modifier.reveal(appearance.value,0f)) { DailySummary() }
        Spacer(Modifier.height(22.dp))
        Box(Modifier.reveal(appearance.value,.18f)) { SummaryCards(false) }
        Spacer(Modifier.height(22.dp))
        Text("영상으로 돌아보기",Modifier.reveal(appearance.value,.3f),color=Green,fontSize=23.sp,fontWeight=FontWeight.SemiBold)
        Spacer(Modifier.height(14.dp))
        LazyColumn(Modifier.fillMaxSize().nestedScroll(slowerScroll).testTag("daily-list"),verticalArrangement=Arrangement.spacedBy(12.dp),contentPadding=PaddingValues(bottom=28.dp)) {
            items(ReviewData.events,key={it.id}) { event ->
                Row(Modifier.fillMaxWidth().reveal(appearance.value,.35f+(ReviewData.events.indexOf(event).coerceAtMost(4)*.06f)).clip(RoundedCornerShape(18.dp)).background(White.copy(alpha=.72f)).clickable { onOpen(event) }.padding(12.dp),verticalAlignment=Alignment.CenterVertically) {
                    Box(Modifier.width(210.dp).height(116.dp).clip(RoundedCornerShape(12.dp))) {
                        val id=remember(event.id) { context.resources.getIdentifier(event.id+"_thumb","drawable",context.packageName) }
                        if(id!=0)Image(painterResource(id),"${event.turn.label} ${event.time} 영상",Modifier.fillMaxSize(),contentScale=ContentScale.Crop)
                        Box(Modifier.align(Alignment.Center).size(36.dp).background(Color.Black.copy(alpha=.24f),RoundedCornerShape(30.dp)),contentAlignment=Alignment.Center) { Text("▶",color=White,fontSize=16.sp) }
                    }
                    Column(Modifier.padding(start=25.dp).weight(1f),verticalArrangement=Arrangement.spacedBy(10.dp)) {
                        Text(event.turn.label,color=Ink,fontSize=23.sp,fontWeight=FontWeight.Medium)
                        Text(event.time,color=TimeColor,fontSize=19.sp)
                    }
                    Text("${event.accuracy}%",Modifier.padding(horizontal=24.dp),color=Color(0xFFB1A48F),fontSize=27.sp,fontWeight=FontWeight.Normal)
                }
            }
        }
    }
}
@Composable private fun SkillsPage() {
    val appearance=remember { Animatable(0f) }
    LaunchedEffect(Unit) { appearance.animateTo(1f,tween(1450,easing=FastOutSlowInEasing)) }
    LazyColumn(Modifier.fillMaxSize().testTag("skills-list"),contentPadding=PaddingValues(top=13.dp,bottom=32.dp),verticalArrangement=Arrangement.spacedBy(25.dp)) {
        item { Box(Modifier.reveal(appearance.value,0f)) { MonthlyReview() } }
        item { Box(Modifier.reveal(appearance.value,.16f)) { SummaryCards(true) } }
        item {
            Row(Modifier.fillMaxWidth().reveal(appearance.value,.3f),horizontalArrangement=Arrangement.spacedBy(18.dp)) {
                listOf(Triple("과속",2,3),Triple("신호 준수",36,0),Triple("횡단보도 정지선 침범",3,10)).forEach { (label,count,icon) ->
                    Row(Modifier.weight(1f).background(White,RoundedCornerShape(18.dp)).padding(23.dp),verticalAlignment=Alignment.CenterVertically) {
                        MissionIcon(icon,Modifier.size(36.dp));Spacer(Modifier.width(18.dp))
                        Column(verticalArrangement=Arrangement.spacedBy(6.dp)) { Text(label,color=TimeColor,fontSize=17.sp);Text("${count}회",color=Ink,fontSize=28.sp,fontWeight=FontWeight.Medium) }
                    }
                }
            }
        }
        item { Text("도전과제",Modifier.reveal(appearance.value,.4f),fontSize=25.sp,color=Green,fontWeight=FontWeight.SemiBold) }
        items(ReviewData.achievements.chunked(4)) { row ->
            Row(Modifier.fillMaxWidth().reveal(appearance.value,.45f+ReviewData.achievements.indexOf(row.first())/4*.07f),horizontalArrangement=Arrangement.spacedBy(18.dp)) {
                row.forEach { achievement ->
                    Column(Modifier.weight(1f).height(212.dp).background(White,RoundedCornerShape(18.dp)).padding(22.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                        MissionIcon(achievement.icon,Modifier.size(35.dp))
                        Text(achievement.title,color=Ink,fontSize=17.sp,lineHeight=25.sp,modifier=Modifier.weight(1f))
                        LinearProgressIndicator(progress={achievement.progress},color=Green,trackColor=Track,modifier=Modifier.fillMaxWidth().height(5.dp).clip(RoundedCornerShape(5.dp)))
                        Text("${achievement.done} / ${achievement.target}",color=TimeColor,fontSize=14.sp)
                    }
                }
                repeat(4-row.size) { Spacer(Modifier.weight(1f)) }
            }
        }
    }
}
@Composable private fun MissionIcon(kind:Int,modifier:Modifier) {
    Canvas(modifier) {
        val s=size.width/40f;val stroke=Stroke(2.2f*s,cap=StrokeCap.Round)
        fun line(x:Float,y:Float,a:Float,b:Float)=drawLine(Green,Offset(x*s,y*s),Offset(a*s,b*s),strokeWidth=2.2f*s,cap=StrokeCap.Round)
        fun path(vararg points:Pair<Float,Float>) { val p=Path();points.forEachIndexed { i,v -> if(i==0)p.moveTo(v.first*s,v.second*s) else p.lineTo(v.first*s,v.second*s) };drawPath(p,Green,style=stroke) }
        when(kind) {
            0 -> { drawRoundRect(Green,Offset(11*s,2*s),Size(18*s,29*s),cornerRadius=androidx.compose.ui.geometry.CornerRadius(5*s),style=stroke);repeat(3){drawCircle(Green,2.1f*s,Offset(20*s,(9+8*it)*s))};line(20f,31f,20f,39f) }
            1 -> { path(7f to 13f,18f to 4f,18f to 10f,31f to 10f,31f to 16f,18f to 16f,18f to 22f,7f to 13f);line(8f,30f,14f,30f);line(21f,30f,27f,30f);line(34f,30f,38f,30f) }
            2 -> { line(3f,13f,37f,13f);repeat(4){val a=5f+it*9;line(a,21f,a,37f)};line(12f,4f,28f,4f) }
            10 -> {
                // Front (right) half of a side-view car, cropped at the body midpoint.
                path(8f to 9f,17f to 9f,25f to 18f,35f to 20f,37f to 24f,37f to 29f,32f to 29f)
                path(8f to 29f,22f to 29f)
                path(11f to 12f,16f to 12f,21f to 18f,11f to 18f)
                line(34f,23f,37f,23f)
                drawCircle(Green,4.5f*s,Offset(27*s,29*s),style=stroke)
                line(17f,33f,20f,33f)
            }
            3 -> { drawArc(Green,180f,180f,false,Offset(3*s,8*s),Size(34*s,34*s),style=stroke);line(20f,25f,29f,14f);line(5f,33f,35f,33f) }
            4,5 -> { val sign=if(kind==4)1f else -1f;val xx: (Float) -> Float = { v -> 20f+sign*(v-20f) };val p=Path().apply { moveTo(xx(28f)*s,36*s);lineTo(xx(28f)*s,19*s);quadraticBezierTo(xx(28f)*s,9*s,xx(17f)*s,9*s);lineTo(xx(7f)*s,9*s) };drawPath(p,Green,style=stroke);path(xx(14f) to 3f,xx(7f) to 9f,xx(14f) to 15f) }
            6 -> { val p=Path().apply { moveTo(30*s,35*s);lineTo(30*s,14*s);cubicTo(30*s,0f,10*s,0f,10*s,14*s);lineTo(10*s,26*s) };drawPath(p,Green,style=stroke);path(4f to 20f,10f to 27f,16f to 20f) }
            7 -> { val p=Path().apply {moveTo(8*s,38*s);cubicTo(8*s,18*s,32*s,24*s,32*s,4*s)};drawPath(p,Green,style=stroke);path(25f to 10f,32f to 3f,38f to 10f) }
            8 -> { drawCircle(Green,3*s,Offset(23*s,5*s),style=stroke);path(10f to 19f,19f to 13f,26f to 22f,34f to 22f);path(20f to 14f,17f to 26f,8f to 37f);path(17f to 26f,25f to 29f,28f to 38f) }
            else -> { drawRoundRect(Green,Offset(3*s,5*s),Size(34*s,29*s),cornerRadius=androidx.compose.ui.geometry.CornerRadius(5*s),style=stroke);path(16f to 12f,27f to 20f,16f to 28f,16f to 12f) }
        }
    }
}
@Composable private fun EventPlayer(event:DriveEvent,onClose:()->Unit) {
    val context=LocalContext.current
    var video by remember { mutableStateOf<VideoView?>(null) }
    var playing by remember { mutableStateOf(false) }
    var position by remember { mutableIntStateOf(0) }
    var duration by remember { mutableIntStateOf(8000) }
    var error by remember { mutableStateOf(false) }
    val lifecycle=LocalLifecycleOwner.current.lifecycle
    DisposableEffect(lifecycle) {
        val observer=LifecycleEventObserver { _,event ->
            if(event==Lifecycle.Event.ON_PAUSE || event==Lifecycle.Event.ON_STOP) { video?.pause();playing=false }
        }
        lifecycle.addObserver(observer)
        onDispose { lifecycle.removeObserver(observer);video?.stopPlayback() }
    }
    LaunchedEffect(video) { while(true) { video?.let { position=it.currentPosition };delay(100) } }
    Dialog(onDismissRequest=onClose,properties=DialogProperties(usePlatformDefaultWidth=false)) {
        Column(Modifier.fillMaxWidth(.94f).clip(RoundedCornerShape(24.dp)).background(Beige).padding(24.dp),verticalArrangement=Arrangement.spacedBy(14.dp)) {
            Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically) {
                Text(event.turn.label,color=event.turn.color(),fontSize=25.sp,fontWeight=FontWeight.SemiBold);Spacer(Modifier.width(16.dp));Text(event.time,color=TimeColor,fontSize=20.sp)

            }
            Box(Modifier.fillMaxWidth().aspectRatio(16f/9f).clip(RoundedCornerShape(14.dp)).background(Color(0xFF273B35)),contentAlignment=Alignment.Center) {
                AndroidView(factory={ ctx -> VideoView(ctx).apply {
                    video=this
                    setOnPreparedListener { player -> duration=player.duration;player.isLooping=false;start();playing=true }
                    setOnCompletionListener { playing=false;position=duration }
                    setOnErrorListener { _,_,_ -> error=true;playing=false;true }
                    val id=context.resources.getIdentifier(event.id,"raw",context.packageName)
                    setVideoURI(Uri.parse("android.resource://${context.packageName}/$id"))
                } },modifier=Modifier.fillMaxSize())
                if(error)Text("영상을 열 수 없습니다",color=White)
                Column(Modifier.align(Alignment.TopEnd).padding(12.dp),horizontalAlignment=Alignment.End,verticalArrangement=Arrangement.spacedBy(6.dp)) {
                    Box(Modifier.size(48.dp).clickable(onClick=onClose).semantics { contentDescription="영상 닫기" },contentAlignment=Alignment.Center) {
                        Box(Modifier.size(32.dp).background(Color.Black,RoundedCornerShape(4.dp)),contentAlignment=Alignment.Center) {
                            Text("×",color=White,fontSize=26.sp,fontWeight=FontWeight.Medium)
                        }
                    }
                    Column(Modifier.background(Color.Black.copy(alpha=.78f),RoundedCornerShape(6.dp)).padding(horizontal=12.dp,vertical=8.dp),verticalArrangement=Arrangement.spacedBy(6.dp)) {
                        Row(verticalAlignment=Alignment.CenterVertically) {
                            Canvas(Modifier.width(30.dp).height(12.dp)) { drawLine(Color(0xFF5EF5AE),Offset(0f,size.height/2),Offset(size.width,size.height/2),strokeWidth=3.dp.toPx()) }
                            Spacer(Modifier.width(8.dp));Text("최적 경로",color=White,fontSize=15.sp)
                        }
                        Row(verticalAlignment=Alignment.CenterVertically) {
                            Canvas(Modifier.width(30.dp).height(12.dp)) { for(i in 0..2)drawLine(Color(0xFFFFC56D),Offset(size.width*i/3,size.height/2),Offset(size.width*(i+.65f)/3,size.height/2),strokeWidth=3.dp.toPx()) }
                            Spacer(Modifier.width(8.dp));Text("주행 경로",color=White,fontSize=15.sp)
                        }
                    }
                }
            }
            Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(18.dp)) {
                Button(onClick={ video?.let { if(playing)it.pause() else { if(position>=duration-100)it.seekTo(0);it.start() };playing=!playing } },enabled=!error,modifier=Modifier.width(120.dp).height(52.dp)) { Text(if(playing)"일시정지" else "재생",fontSize=17.sp) }
                TextButton(onClick={video?.seekTo(0);position=0}) { Text("처음으로",fontSize=16.sp) }
                Slider(value=position.toFloat().coerceIn(0f,duration.toFloat()),onValueChange={position=it.toInt();video?.seekTo(position)},valueRange=0f..duration.toFloat().coerceAtLeast(1f),modifier=Modifier.weight(1f).semantics { contentDescription="영상 재생 위치" })
                Text("0:%02d / 0:%02d".format(position/1000,duration/1000),color=TimeColor,fontSize=16.sp)
            }
        }
    }
}
