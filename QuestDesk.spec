# -*- mode: python ; coding: utf-8 -*-
import os
import sys

added_files = [
    ('assets', 'assets'),
    ('data', 'data'),
    ('config', 'config'),
]

a = Analysis(
    ['main.py'],
    pathex=['d:\\PythonProject\\QuestDesk'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas', 'unittest', 'email', 'http', 'xml'],
    noarchive=False,
)

# 排除系统 PATH (如 Anaconda) 误引用的过时旧版 ICU 动态库，彻底解决 Qt6 找不到指定程序的错误
a.binaries = [
    x for x in a.binaries
    if not any(bad in os.path.basename(x[0]).lower() for bad in ['icudt', 'icuuc', 'icuin'])
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QuestDesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='QuestDesk',
)
