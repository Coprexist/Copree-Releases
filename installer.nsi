; Copree Launcher NSIS Installer Script
; =======================================
; Generates single .exe installer with:
; - Language selection at start
; - Custom installation directory
; - Desktop and Start Menu shortcuts
; - Uninstaller
; - Optional auto-start

; 中文串要求 Unicode 版安装器，否则 makensis 按 cp1252 解码，
; 桌面快捷方式会显示成「Copree å¯åŠ¨å™¨」。
Unicode true

!include "MUI2.nsh"

; --- Basic Information ---
Name "Copree Launcher"
OutFile "Copree-Installer.exe"
InstallDir "$LOCALAPPDATA\Copree"
InstallDirRegKey HKCU "Software\Copree" "InstallDir"
RequestExecutionLevel admin

; --- Version Info ---
; 版本由 CI 生成 source/version.nsh 注入（Tag 去掉 v 前缀），本地打包没有它就回落 0.0.0
!if /FileExists "version.nsh"
  !include "version.nsh"
!endif
!ifndef VER3
  !define VER3 "0.0.0"
!endif
!ifndef VER4
  !define VER4 "0.0.0.0"
!endif
VIProductVersion "${VER4}"
VIAddVersionKey "ProductName" "Copree Launcher"
VIAddVersionKey "CompanyName" "Copree"
VIAddVersionKey "FileVersion" "${VER3}"
VIAddVersionKey "FileDescription" "Copree Desktop Launcher Installer"

; --- Interface Settings ---
!define MUI_ICON "frontend\public\brand\coprexist-icon.ico"
!define MUI_UNICON "frontend\public\brand\coprexist-icon.ico"
!define MUI_ABORTWARNING

; --- Language Selection ---
; Show language selection dialog before welcome page
!define MUI_LANGDLL_ALLLANGUAGES

; --- Installation Pages ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; --- Uninstallation Pages ---
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; --- Languages ---
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; --- Language Dialog Settings ---
; Chinese texts
!define MUI_LANGDLL_WINDOWTITLE "选择安装语言"
!define MUI_LANGDLL_INFO "请选择安装过程中使用的语言："

!define MUI_WELCOMEPAGE_TITLE "欢迎安装 Copree 启动器"
!define MUI_WELCOMEPAGE_TEXT "本向导将引导您完成 Copree 启动器的安装。$\r$\n$\r$\nCopree 是一个本地 AI 社交网络，支持与多个 AI 角色进行对话。$\r$\n$\r$\n点击下一步继续。"
!define MUI_FINISHPAGE_RUN "$INSTDIR\Copree.exe"
!define MUI_FINISHPAGE_RUN_TEXT "启动 Copree"

; --- Installation Section ---
Section "Copree Launcher" SecMain
  SetOutPath "$INSTDIR"
  
  ; Copy all files
  File /r "dist\Copree\*.*"
  
  ; Write registry (install path)
  WriteRegStr HKCU "Software\Copree" "InstallDir" "$INSTDIR"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\Copree"
  CreateShortCut "$SMPROGRAMS\Copree\Copree 启动器.lnk" "$INSTDIR\Copree.exe" "" "$INSTDIR\Copree.exe" 0
  CreateShortCut "$SMPROGRAMS\Copree\卸载 Copree.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\Copree 启动器.lnk" "$INSTDIR\Copree.exe" "" "$INSTDIR\Copree.exe" 0
  
  ; Write uninstall information to registry
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "DisplayName" "Copree 启动器"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "DisplayVersion" "${VER3}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "Publisher" "Copree"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree" "NoRepair" 1

  ; 让资源管理器重读 shell 图标：升级安装后 exe 换了新图标，Explorer 仍按旧缓存画，
  ; 用户看到的就是"图标还是糊的"。这一下通知是标准做法，不用让用户手动清缓存。
  System::Call 'shell32::SHChangeNotify(i 0x08000000, i 0, i 0, i 0)'

SectionEnd

; --- Uninstallation Section ---
Section "Uninstall"
  ; Delete files
  RMDir /r "$INSTDIR"
  
  ; Delete shortcuts
  Delete "$DESKTOP\Copree 启动器.lnk"
  RMDir /r "$SMPROGRAMS\Copree"
  
  ; Delete registry keys
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Copree"
  DeleteRegKey HKCU "Software\Copree"
  
SectionEnd

; --- Language Selection Function ---
Function .onInit
  ; Show language selection dialog
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd
