; pyemsi NSIS Installer Script
; Requires NSIS 3.x with MUI2
;
; Build:  makensis installer\pyemsi.nsi
; Source: expects a pre-built portable runtime in dist\pyemsi\

;---------------------------------------------------------------------------
; General
;---------------------------------------------------------------------------
!define APP_NAME        "pyemsi"
!define APP_VERSION     "0.1.3"
!define APP_PUBLISHER   "SSIL"
!define APP_URL         "https://github.com/EMSolution-SSIL/pyemsi"
!define APP_EXE         "pyemsi.exe"
!define UNINSTALL_KEY   "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Unicode true
Name "${APP_NAME} ${APP_VERSION}"
OutFile "..\dist\${APP_NAME}-${APP_VERSION}-setup.exe"
InstallDir "$LOCALAPPDATA\${APP_NAME}"
InstallDirRegKey HKCU "${UNINSTALL_KEY}" "InstallLocation"
RequestExecutionLevel user
SetCompressor /SOLID lzma

;---------------------------------------------------------------------------
; Modern UI 2
;---------------------------------------------------------------------------
!include "MUI2.nsh"
!include "FileFunc.nsh"

!define MUI_ICON   "..\pyemsi\resources\icons\Icon.ico"
!define MUI_UNICON "..\pyemsi\resources\icons\Icon.ico"

!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APP_NAME}"
!define MUI_FINISHPAGE_LINK "Open documentation"
!define MUI_FINISHPAGE_LINK_LOCATION "https://emsolution-ssil.github.io/pyemsi/"

; --- Installer pages ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; --- Uninstaller pages ---
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; --- Language ---
!insertmacro MUI_LANGUAGE "English"

;---------------------------------------------------------------------------
; Version metadata (shown in file properties)
;---------------------------------------------------------------------------
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName"     "${APP_NAME}"
VIAddVersionKey "ProductVersion"  "${APP_VERSION}"
VIAddVersionKey "CompanyName"     "${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "LegalCopyright"  "GPLv3+"
VIAddVersionKey "FileVersion"     "${APP_VERSION}.0"

;---------------------------------------------------------------------------
; Installer Section
;---------------------------------------------------------------------------
Section "${APP_NAME} (required)" SecCore
    SectionIn RO ; cannot be unchecked
    SetOutPath "$INSTDIR"

    ; Copy the entire portable runtime
    File /r "..\dist\pyemsi\*.*"

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; --- Add/Remove Programs entry ---
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "DisplayName"      "${APP_NAME} ${APP_VERSION}"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "DisplayVersion"    "${APP_VERSION}"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "Publisher"         "${APP_PUBLISHER}"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "URLInfoAbout"      "${APP_URL}"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "InstallLocation"   "$INSTDIR"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "UninstallString"   "$INSTDIR\uninstall.exe"
    WriteRegStr   HKCU "${UNINSTALL_KEY}" "DisplayIcon"       "$INSTDIR\${APP_EXE},0"
    WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoModify"          1
    WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoRepair"          1

    ; Estimate installed size (in KB) for Add/Remove Programs
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "${UNINSTALL_KEY}" "EstimatedSize" $0
SectionEnd

;---------------------------------------------------------------------------
; Optional Components
;---------------------------------------------------------------------------
Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
                   "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
SectionEnd

Section "Start Menu Shortcut" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
                    "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
    CreateShortCut  "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" \
                    "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
SectionEnd

Section 'Explorer "Open with pyemsi"' SecContextMenu
    WriteRegStr HKCU "Software\Classes\Directory\shell\${APP_NAME}" "" "Open with ${APP_NAME}"
    WriteRegStr HKCU "Software\Classes\Directory\shell\${APP_NAME}" "Icon" "$INSTDIR\${APP_EXE},0"
    WriteRegStr HKCU "Software\Classes\Directory\shell\${APP_NAME}\command" "" '"$INSTDIR\${APP_EXE}" "%1"'

    WriteRegStr HKCU "Software\Classes\Directory\Background\shell\${APP_NAME}" "" "Open with ${APP_NAME}"
    WriteRegStr HKCU "Software\Classes\Directory\Background\shell\${APP_NAME}" "Icon" "$INSTDIR\${APP_EXE},0"
    WriteRegStr HKCU "Software\Classes\Directory\Background\shell\${APP_NAME}\command" "" '"$INSTDIR\${APP_EXE}" "%V"'
SectionEnd

;---------------------------------------------------------------------------
; Component Descriptions
;---------------------------------------------------------------------------
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore}        "Install ${APP_NAME} application files (required)."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop}     "Create a shortcut on the Desktop."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu}   "Create a Start Menu program group."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecContextMenu}  "Add 'Open with ${APP_NAME}' to the folder right-click menu."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;---------------------------------------------------------------------------
; Uninstaller Section
;---------------------------------------------------------------------------
Section "Uninstall"
    ; --- Remove context menu entries ---
    DeleteRegKey HKCU "Software\Classes\Directory\shell\${APP_NAME}"
    DeleteRegKey HKCU "Software\Classes\Directory\Background\shell\${APP_NAME}"

    ; --- Remove Add/Remove Programs entry ---
    DeleteRegKey HKCU "${UNINSTALL_KEY}"

    ; --- Remove shortcuts ---
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"

    ; --- Remove installed files ---
    RMDir /r "$INSTDIR"
SectionEnd
