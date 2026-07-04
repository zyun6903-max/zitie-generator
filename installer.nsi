; 字帖生成器 NSIS 安装脚本
; 使用 NSIS 3.0+ (https://nsis.sourceforge.io/)

Unicode true
Name "字帖生成器"
OutFile "dist\字帖生成器_安装包.exe"
RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\字帖生成器"

; 页面
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "安装" SecMain
    SetOutPath "$INSTDIR"

    ; 复制主程序和相关文件
    File /r "dist\字帖生成器\*.*"

    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\字帖生成器"
    CreateShortCut "$SMPROGRAMS\字帖生成器\字帖生成器.lnk" "$INSTDIR\字帖生成器.exe"
    CreateShortCut "$SMPROGRAMS\字帖生成器\卸载字帖生成器.lnk" "$INSTDIR\uninstall.exe"

    ; 桌面快捷方式
    CreateShortCut "$DESKTOP\字帖生成器.lnk" "$INSTDIR\字帖生成器.exe"

    ; 卸载信息注册
    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\字帖生成器" \
        "DisplayName" "字帖生成器"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\字帖生成器" \
        "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\字帖生成器" \
        "DisplayIcon" "$INSTDIR\字帖生成器.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\字帖生成器" \
        "Publisher" "字帖生成器"
SectionEnd

Section "Uninstall"
    ; 删除文件
    RMDir /r "$INSTDIR"

    ; 删除快捷方式
    RMDir /r "$SMPROGRAMS\字帖生成器"
    Delete "$DESKTOP\字帖生成器.lnk"

    ; 删除注册表
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\字帖生成器"
SectionEnd
