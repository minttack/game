@echo off
setlocal
REM IRL: after an actual IRL Development APK runs on your authorized Android.
REM Read-only ADB logcat summary. Never installs, launches or clears phone logs.
cd /d "%~dp0..\.."
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo Python 3.11 or newer required. No device changes performed.
 pause
 exit /b 1
)
py -3 "%~dp0irl_mobile_evidence_report.py" --adb --project-root "%CD%" %*
set "IRL_CODE=%ERRORLEVEL%"
if not "%IRL_CODE%"=="0" (
 echo IRL frame and touch evidence NOT ESTABLISHED. Read console diagnostic.
 echo Your Unreal-built IRL APK may not be running or logcat may not contain 20+ seconds of tagged samples.
) else (
 echo IRL source-reported Android frame and input summary saved in Saved\IRL.
 echo GPU speed, player locomotion and Android thermal behavior are NOT verified by this command.
)
pause
exit /b %IRL_CODE%
