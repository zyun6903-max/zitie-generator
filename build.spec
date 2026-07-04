# -*- mode: python ; coding: utf-8 -*-
# 字帖生成器 PyInstaller 打包配置（Windows）
# 使用：pyinstaller build.spec
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/vocab.db', 'data'),
        ('data/fonts/*.ttf', 'data/fonts'),
    ],
    hiddenimports=[
        'engine',
        'engine.stroke_renderer',
        'engine.char_block',
        'engine.grid_layout',
        'engine.pdf_generator',
        'ui',
        'ui.main_window',
        'svg.path',
        'svg.path.path',
        'pypinyin',
        'pypinyin.dicts',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PIL',
        'scipy',
        'numpy',
        'notebook',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebChannel',
        'PyQt6.QtMultimedia',
        'PyQt6.QtSensors',
        'PyQt6.QtBluetooth',
        'PyQt6.QtNfc',
        'PyQt6.QtPositioning',
        'PyQt6.QtLocation',
        'PyQt6.QtXml',
        'PyQt6.QtXmlPatterns',
        'PyQt6.QtHelp',
        'PyQt6.QtDesigner',
        'PyQt6.QtQuick',
        'PyQt6.QtQml',
        'PyQt6.QtTest',
        'PyQt6.QtSql',
        'PyQt6.QtNetwork',
        'PyQt6.QtQmlModels',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='字帖生成器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='字帖生成器',
)
