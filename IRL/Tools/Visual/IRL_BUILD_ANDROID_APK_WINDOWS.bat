@echo off
setlocal
REM IRL Android-first build; must run from complete minttack/game IRL source on Windows.
cd /d "%~dp0..\.."
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo Python 3 launcher required. Install Python 3.11+.
 pause
 exit /b 1
)
py -3 "%~dp0irl_android_apk_runner.py" --project-root "%CD%" %*
set "RC=%ERRORLEVEL%"
if NOT "%RC%"=="0" (
 echo IRL Android APK NOT VERIFIED. Read IRL\Saved\IRL\android_apk_build_*.json.
) else (
 echo IRL Android runner passed its requested gate.
 echo Development APK proof does not mean it was tested on a phone.
)
pause
exit /b %RC%
