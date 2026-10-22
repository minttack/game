@echo off
setlocal
REM Read-only by default. To actually launch the app after manual installation,
REM pass --run as an argument. The script NEVER installs an APK.
cd /d "%~dp0..\.."
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo Python 3.11+ required. No phone actions performed.
 pause
 exit /b 1
)
py -3 "%~dp0irl_android_device_smoke.py" --project-root "%CD%" %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" (
 echo IRL real-device smoke was NOT VERIFIED.
) else (
 echo IRL recorded an authorized phone check.
 echo This is NOT proof of working game controls, sustained FPS or release readiness.
)
echo Reports: IRL\Saved\IRL\android_device_smoke_*.json
pause
exit /b %EXIT_CODE%
