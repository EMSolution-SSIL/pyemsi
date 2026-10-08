@echo off
rem Start FreeCAD from this conda prefix with the environment conda activation would set.
for %%I in ("%~dp0..") do set "CONDA_PREFIX=%%~fI"
set "PATH=%CONDA_PREFIX%;%CONDA_PREFIX%\Library\mingw-w64\bin;%CONDA_PREFIX%\Library\usr\bin;%CONDA_PREFIX%\Library\bin;%CONDA_PREFIX%\Scripts;%CONDA_PREFIX%\bin;%PATH%"
for %%F in ("%CONDA_PREFIX%\etc\conda\activate.d\*.bat") do call "%%F"
set "QT_API=pyside6"
set "QTWEBENGINE_CHROMIUM_FLAGS=--no-sandbox"
start "" "%CONDA_PREFIX%\Library\bin\freecad.exe" %*
