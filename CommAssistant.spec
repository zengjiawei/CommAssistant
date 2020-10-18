# -*- mode: python -*-

block_cipher = None


a = Analysis(['CommAssistant.py'],
             pathex=['C:\\Users\\ZJW\\Desktop\\My File\\Project\\Upper\\CommAssistant\\CommAssistant'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5.sip'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
a.datas.extend([('PyQt5/Qt/plugins/styles/qwindowsvistastyle.dll', 'src/styles/qwindowsvistastyle.dll', 'BINARY')])
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='CommAssistant',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
		  icon='C:/images/icon.ico' )
