@echo off
setlocal
REM IRL is one project. Double-click inside IRL\Tools\Visual only after cloning
REM the full original Unreal 5.8 IRL repository/graphics feature branch.
cd /d "%~dp0..\.."
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo Python launcher not found. Install Python 3.11+ with numpy/Pillow.
 pause
 exit /b 1
)
py -3 "%~dp0irl_native_forest_runner.py" --project-root "%CD%" --mode build-and-audit %*
set "IRL_EXIT=%ERRORLEVEL%"
if "%IRL_EXIT%" NEQ "0" (
 echo.
 echo IRL Unreal verification DID NOT PASS. See IRL\Saved\IRL for logs and evidence.
) else (
 echo.
 echo IRL Editor physics review eligible. NOT a playable Android release.
)
pause
exit /b %IRL_EXIT%
