; Basic setup
!define APPNAME "Flappy Bird"
!define COMPANYNAME "Your Company"
!define DESCRIPTION "A Flappy Bird clone"
!define VERSION "1.0"

; Include Modern UI
!include "MUI2.nsh"

; General
Name "${APPNAME}"
OutFile "FlappyBirdSetup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; Request application privileges
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    
    ; Copy the main executable
    File "dist\game\game.exe"
    
    ; Copy python313.dll to the same directory as the executable
    File "dist\game\_internal\python313.dll"
    
    ; Copy all required DLLs from _internal
    File "dist\game\_internal\*.dll"
    
    ; Create _internal directory and copy its contents
    SetOutPath "$INSTDIR\_internal"
    File /r "dist\game\_internal\*.*"
    
    ; Copy asset directories
    SetOutPath "$INSTDIR\img"
    File /r "dist\game\img\*.*"
    
    SetOutPath "$INSTDIR\sound"
    File /r "dist\game\sound\*.*"
    
    ; Reset working directory to installation root
    SetOutPath "$INSTDIR"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\game.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\game.exe"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Write registry keys for uninstall
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
SectionEnd

Section "Uninstall"
    ; Remove Start Menu shortcuts
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove files and directories
    Delete "$INSTDIR\game.exe"
    Delete "$INSTDIR\python313.dll"
    Delete "$INSTDIR\*.dll"
    RMDir /r "$INSTDIR\_internal"
    RMDir /r "$INSTDIR\img"
    RMDir /r "$INSTDIR\sound"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

; Function to verify installation
Function .onInstSuccess
    MessageBox MB_OK "Installation completed successfully. The game has been installed on your computer."
FunctionEnd

; Function to handle installation errors
Function .onInstFailed
    MessageBox MB_OK|MB_ICONSTOP "There was an error during installation. Please try again or contact support."
FunctionEnd 