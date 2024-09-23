import PyInstaller.__main__
    
PyInstaller.__main__.run([
        'check_balance.py',
        '--onefile',
        '--clean',
        '--noconsole'
    ])