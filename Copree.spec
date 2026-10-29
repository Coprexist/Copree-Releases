import sys

from PyInstaller.utils.hooks import collect_submodules
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 应用图标：Windows 用 .ico、macOS 用 .icns（都由 frontend/public/brand 下的主图派生，
# Linux 的 tar.gz 没有图标概念，交给默认）。
if sys.platform.startswith('win'):
    _APP_ICON = 'frontend/public/brand/coprexist-icon.ico'
elif sys.platform == 'darwin':
    _APP_ICON = 'frontend/public/brand/coprexist-icon.icns'
else:
    _APP_ICON = None

a = Analysis(
    ['run_packaged.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/app', 'app'),
        ('frontend/dist', 'frontend/dist'),
    ],

    hiddenimports=[
        'pydantic_settings',
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.aiosqlite',
        'aiosqlite',
        'greenlet',
        'fastapi.middleware.cors',
        'fastapi.staticfiles',
        'passlib.context',
        'passlib.hash.bcrypt',
        'passlib.hash.sha256_crypt',
        'jose',
        'jose.jwt',
        'jose.jws',
        'jose.jwe',
        'httpx',
        'PIL',
        'bcrypt',
        'python_multipart',
        'cryptography.fernet',
    ] + collect_submodules('passlib') + collect_submodules('jose'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'mypy',
        'hypothesis',
        'IPython',
        'trio',
        'uvloop',
        'winloop',
        'psycopg2',
        'psycopg',
        'asyncpg',
        'pymysql',
        'mysql',
        'oracledb',
        'cx_Oracle',
        'gunicorn',
        'watchfiles',
        'wsproto',
        'werkzeug',
        'python_socks',
        'yaml',
        'passlib.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 版本号由 CI 生成（build.yml 的 Launcher version 步骤）；本地打包没有就跳过，
# 启动器会回落到 config.py 里的 app_version。
import pathlib as _pathlib
if _pathlib.Path('version.txt').exists():
    # datas TOC 是三段 (dest, src, typecode)：写成两段会在 COLLECT 阶段
    # 报 "not enough values to unpack (expected 3, got 2)"。dest 就是包内路径。
    a.datas.append(('version.txt', 'version.txt', 'DATA'))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Copree',
    # 图标必须喂给 EXE：快捷方式、任务栏、资源管理器都读 exe 自带图标，
    # 漏掉这一行装完就是白底空白图标（v0.4.16 第二版踩过）。
    icon=_APP_ICON,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Copree',
)
