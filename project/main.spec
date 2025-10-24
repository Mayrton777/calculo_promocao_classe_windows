# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Encontra o diretório do seu ambiente virtual (env)
SPEC_DIR = SPECPATH
SITE_PACKAGES_DIR = os.path.join(SPEC_DIR, 'env', 'Lib', 'site-packages')

# Lista de binários (DLLs)
pyogrio_libs_path = os.path.join(SITE_PACKAGES_DIR, 'pyogrio.libs')
shapely_libs_path = os.path.join(SITE_PACKAGES_DIR, 'shapely.libs')

# Lista de dados (arquivos de configuração do GDAL)
pyogrio_data_path = os.path.join(SITE_PACKAGES_DIR, 'pyogrio', 'gdal_data')

a = Analysis(
    ['main.py'],
    pathex=[],
    
    # Adiciona as DLLs do pyogrio E do shapely
    binaries=[
        (pyogrio_libs_path, 'pyogrio.libs'),
        (shapely_libs_path, 'shapely.libs')
    ],
    
    # Adiciona os dados e os dados do GDAL
    datas=[
        ('data', 'data'), 
        (pyogrio_data_path, 'pyogrio\\gdal_data')
    ],
    
    hiddenimports=['pyogrio', 'pyogrio._geometry', 'pyogrio._io', 'pyogrio._errors'],
    
    # Diz ao PyInstaller para executar o script de hook antes do main.py
    runtime_hooks=['runtime_hook.py'],
    
    hookspath=[],
    hooksconfig={},
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='promocao_classe',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='promocao_classe'
)