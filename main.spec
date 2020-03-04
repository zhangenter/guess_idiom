# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Kamin\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages', 'D:\\gitcode\\guess_idiom'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('bg.jpeg','D:\\gitcode\\guess_idiom\\bg.jpeg','DATA'),
          ('bg2.jpeg','D:\\gitcode\\guess_idiom\\bg2.jpeg','DATA'),
          ('cap1.png','D:\\gitcode\\guess_idiom\\cap1.png','DATA'),
          ('cap2.png','D:\\gitcode\\guess_idiom\\cap2.png','DATA'),
          ('tzg.jpg','D:\\gitcode\\guess_idiom\\tzg.jpg','DATA'),
          ('syht.otf','D:\\gitcode\\guess_idiom\\syht.otf','DATA'),
          ('english.txt','D:\\gitcode\\guess_idiom\\english.txt','DATA'),
          ('poetry.txt','D:\\gitcode\\guess_idiom\\poetry.txt','DATA'),
          ('words.txt','D:\\gitcode\\guess_idiom\\words.txt','DATA')],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
