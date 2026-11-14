import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}
android {
    namespace = "io.drivequest2.app"
    compileSdk = 35
    useLibrary("android.car", false)
    defaultConfig {
        applicationId = "io.drivequest2.app"
        minSdk = 28
        targetSdk = 35
        versionCode = 5
        versionName = "0.3.1-intersections"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    val signingFile = System.getenv("DRIVEQUEST_SIGNING_PROPERTIES")?.let { file(it) }
    if (signingFile != null) {
        require(signingFile.isFile) { "Signing properties file missing" }
        val releaseCredentials = Properties().apply { signingFile.inputStream().use { load(it) } }
        signingConfigs.create("submission") {
            storeFile = file(releaseCredentials.getProperty("storeFile"))
            storePassword = releaseCredentials.getProperty("storePassword")
            keyAlias = releaseCredentials.getProperty("keyAlias")
            keyPassword = releaseCredentials.getProperty("keyPassword")
        }
    }
    buildTypes {
        getByName("debug") {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        getByName("release") {
            isDebuggable = false
            isMinifyEnabled = false
            if (signingFile != null) signingConfig = signingConfigs.getByName("submission")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } }
}
dependencies {
    implementation(libs.vehicle.sdk)
    implementation(libs.kotlin.reflect)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
