package io.drivequest2.app

import android.app.Application
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.getValue
import io.drivequest2.app.data.*
import io.drivequest2.app.domain.*
import io.drivequest2.app.ui.ReviewApp
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class ReviewModel(app: Application): AndroidViewModel(app) {
    private val automotive=app.packageManager.hasSystemFeature(PackageManager.FEATURE_AUTOMOTIVE)
    private val monitor: DrivingRestrictionMonitor = if(!automotive) DesktopRestrictionMonitor() else try { CarRestrictionMonitor(app) } catch(_:LinkageError) { UnavailableRestrictionMonitor() }
    private val foreground=MutableStateFlow(false)
    val allowed=combine(monitor.restriction,foreground) { restriction,active -> ReviewData.playbackAllowed(automotive,restriction,active) }.stateIn(viewModelScope,SharingStarted.Eagerly,false)
    private var poll:Job?=null
    fun foreground(active:Boolean) {
        foreground.value=active;poll?.cancel()
        if(active) { monitor.start();poll=viewModelScope.launch { while(isActive) { monitor.refresh();delay(1000) } } }
        else monitor.stop()
    }
    override fun onCleared() { monitor.stop();super.onCleared() }
}
class MainActivity:ComponentActivity() {
    private val model:ReviewModel by viewModels()
    override fun onCreate(savedInstanceState:Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { val allowed by model.allowed.collectAsStateWithLifecycle();ReviewApp(allowed) }
    }
    override fun onResume() { super.onResume();model.foreground(true) }
    override fun onPause() { model.foreground(false);super.onPause() }
}
