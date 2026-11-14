package io.drivequest2.app
import io.drivequest2.app.domain.*
import org.junit.Assert.*
import org.junit.Test
class ReviewDataTest {
    @Test fun historyIsChronologicalAndWithinRequestedTimeWindows() {
        val e=ReviewData.events
        assertEquals(24,e.size);assertEquals(e.size,e.map { it.id }.distinct().size)
        assertEquals(e.sortedBy { it.minutes },e)
        assertTrue(e.all { it.minutes in 480..540 || it.minutes in 720..810 || it.minutes in 1080..1140 })
        val expected=mapOf(Turn.LEFT to 8,Turn.RIGHT to 9,Turn.UTURN to 2,Turn.CURVE to 5)
        expected.forEach { (turn,count) -> assertEquals(count,e.count { it.turn==turn }) }
    }
    @Test fun missionProgressIsBoundedAndTenMissionsExist() {
        assertEquals(10,ReviewData.achievements.size)
        assertTrue(ReviewData.achievements.all { it.target>0 && it.done in 0..it.target && it.progress in 0f..1f })
    }
    @Test fun automotiveUnknownAndRestrictedAlwaysBlockPlayback() {
        Restriction.entries.forEach { state ->
            assertEquals(state==Restriction.PARKED,ReviewData.playbackAllowed(true,state,true))
            assertFalse(ReviewData.playbackAllowed(true,state,false))
        }
    }
    @Test fun backgroundAndUnknownNonAutomotiveCannotPlay() {
        assertTrue(ReviewData.playbackAllowed(false,Restriction.NON_AUTOMOTIVE,true))
        assertFalse(ReviewData.playbackAllowed(false,Restriction.NON_AUTOMOTIVE,false))
        assertFalse(ReviewData.playbackAllowed(false,Restriction.UNKNOWN,true))
    }
}
