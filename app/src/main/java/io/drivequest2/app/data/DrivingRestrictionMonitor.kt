package io.drivequest2.app.data

import android.car.Car
import android.car.VehiclePropertyIds
import android.car.drivingstate.CarUxRestrictionsManager
import android.car.hardware.CarPropertyValue
import android.car.hardware.property.CarPropertyManager
import android.content.ComponentName
import android.content.Context
import android.content.ServiceConnection
import android.os.IBinder
import android.os.SystemClock
import io.drivequest2.app.domain.Restriction
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlin.math.abs

interface DrivingRestrictionMonitor {
    val restriction: StateFlow<Restriction>
    fun start()
    fun refresh()
    fun speedKmh(): Double?
    fun stop()
}
class DesktopRestrictionMonitor : DrivingRestrictionMonitor {
    override val restriction = MutableStateFlow(Restriction.NON_AUTOMOTIVE)
    override fun start() {}
    override fun refresh() {}
    override fun speedKmh(): Double? = null
    override fun stop() {}
}
class UnavailableRestrictionMonitor : DrivingRestrictionMonitor {
    override val restriction = MutableStateFlow(Restriction.UNKNOWN)
    override fun start() {}
    override fun refresh() {}
    override fun speedKmh(): Double? = null
    override fun stop() {}
}
/** Only constructed on FEATURE_AUTOMOTIVE. Optional android.car library keeps phones usable. */
@Suppress("DEPRECATION")
class CarRestrictionMonitor(private val context: Context) : DrivingRestrictionMonitor {
    override val restriction = MutableStateFlow(Restriction.UNKNOWN)
    private var car: Car? = null
    private var ux: CarUxRestrictionsManager? = null
    @Volatile private var properties: CarPropertyManager? = null
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            try {
                ux = car?.getCarManager(Car.CAR_UX_RESTRICTION_SERVICE) as? CarUxRestrictionsManager
                properties = car?.getCarManager(Car.PROPERTY_SERVICE) as? CarPropertyManager
                ux?.registerListener { restriction.value = if (it.isRequiresDistractionOptimization || it.activeRestrictions != 0) Restriction.RESTRICTED else Restriction.PARKED }
                refresh()
            } catch (_: Exception) { restriction.value = Restriction.UNKNOWN }
        }
        override fun onServiceDisconnected(name: ComponentName?) {
            restriction.value = Restriction.UNKNOWN; ux = null; properties = null
        }
    }
    override fun start() {
        if (car != null) return
        restriction.value = Restriction.UNKNOWN
        try { car = Car.createCar(context, connection); car?.connect() }
        catch (_: Exception) { stop() }
    }
    override fun refresh() {
        restriction.value = try {
            val value = ux?.currentCarUxRestrictions
            when {
                value == null -> Restriction.UNKNOWN
                value.isRequiresDistractionOptimization || value.activeRestrictions != 0 -> Restriction.RESTRICTED
                else -> Restriction.PARKED
            }
        } catch (_: Exception) { Restriction.UNKNOWN }
    }
    override fun speedKmh(): Double? = try {
        val manager = properties
        if (manager == null || context.checkSelfPermission(Car.PERMISSION_SPEED) != android.content.pm.PackageManager.PERMISSION_GRANTED) null
        else {
            val p = manager.getProperty<Float>(VehiclePropertyIds.PERF_VEHICLE_SPEED, 0)
            val age = SystemClock.elapsedRealtimeNanos() - p.timestamp
            if (p.status != CarPropertyValue.STATUS_AVAILABLE || age !in 0..3_000_000_000L || !p.value.isFinite()) null
            else abs(p.value.toDouble()) * 3.6
        }
    } catch (_: Exception) { null }
    override fun stop() {
        restriction.value = Restriction.UNKNOWN
        runCatching { ux?.unregisterListener() }; ux = null; properties = null
        runCatching { car?.disconnect() }; car = null
    }
}
