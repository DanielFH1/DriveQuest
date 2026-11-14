#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export JAVA_HOME="${DRIVEQUEST2_JDK:-$HOME/projects/DriveQuest/.local/jdk17}"
export ANDROID_HOME="${DRIVEQUEST2_SDK:-$HOME/projects/DriveQuest/.local/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME="${DRIVEQUEST2_GRADLE_CACHE:-$HOME/projects/DriveQuest/.local/gradle}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"
./gradlew "$@"
