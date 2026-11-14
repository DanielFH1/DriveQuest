package io.drivequest2.app
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import io.drivequest2.app.ui.ReviewApp
import org.junit.Rule
import org.junit.Test
class ReviewUiTest {
    @get:Rule val compose=createComposeRule()
    @Test fun greetingTabsAndAchievementListAreReachable() {
        compose.setContent { ReviewApp(true) }
        compose.onNodeWithText("오늘의 주행을 함께 확인해볼까요?").assertIsDisplayed()
        compose.mainClock.advanceTimeBy(5000)
        compose.waitForIdle()
        compose.onNodeWithText("오늘 주행 요약").assertIsDisplayed()
        compose.onNodeWithText("A-").assertIsDisplayed()
        compose.onNodeWithText("확인하기").assertDoesNotExist()
        compose.onNodeWithText("08:12").assertIsDisplayed()
        compose.onNodeWithText("내 주행실력").performClick()
        compose.onNodeWithText("이번달 주행 기록").assertIsDisplayed()
        compose.onNodeWithContentDescription("이번달 주행 기록, 11월 1일부터 15일까지 일별 15개 점, C부터 A+ 사이 변동").assertIsDisplayed()
        compose.onNodeWithTag("skills-list").performScrollToNode(hasText("하루 주행 돌아보기 7회"))
        compose.onNodeWithText("하루 주행 돌아보기 7회").assertIsDisplayed()
    }
    @Test fun all24VideosAreReachableAndPlayerCloses() {
        compose.setContent { ReviewApp(true) }
        compose.mainClock.advanceTimeBy(5000)
        val context=androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().targetContext
        for(event in io.drivequest2.app.domain.ReviewData.events) {
            compose.onNodeWithTag("daily-list").performScrollToNode(hasText(event.time))
            compose.onNodeWithText(event.time).assertIsDisplayed()
            val id=context.resources.getIdentifier(event.id,"raw",context.packageName)
            org.junit.Assert.assertTrue(id!=0)
            context.resources.openRawResourceFd(id).use { fd ->
                val reader=android.media.MediaMetadataRetriever()
                try {
                    reader.setDataSource(fd.fileDescriptor,fd.startOffset,fd.length)
                    org.junit.Assert.assertEquals("10000",reader.extractMetadata(android.media.MediaMetadataRetriever.METADATA_KEY_DURATION))
                } finally { reader.release() }
            }
        }
        compose.onNodeWithText("18:58").performClick()
        compose.onNodeWithText("최적 경로").assertIsDisplayed()
        compose.onNodeWithText("주행 경로").assertIsDisplayed()
        compose.onNodeWithContentDescription("영상 닫기").performClick()
        compose.onNodeWithText("최적 경로").assertDoesNotExist()
        compose.onNodeWithText("18:58").assertIsDisplayed()
    }
    @Test fun changingRestrictionRemovesVideoAndBlocksInteraction() {
        val allowed=mutableStateOf(true)
        compose.setContent { ReviewApp(allowed.value) }
        compose.mainClock.advanceTimeBy(5000)
        compose.waitForIdle()
        compose.onNodeWithText("08:12").performClick()
        compose.onNodeWithText("최적 경로").assertIsDisplayed()
        compose.runOnIdle { allowed.value=false }
        compose.onNodeWithText("주차 후 확인해 주세요").assertIsDisplayed()
        compose.onNodeWithContentDescription("영상 닫기").assertDoesNotExist()
        compose.onNodeWithText("오늘의 주행").assertDoesNotExist()
    }
}
