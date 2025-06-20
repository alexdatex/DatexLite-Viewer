import PyInstaller.utils.win32.versioninfo as vi
import sys

build = int(sys.argv[1]) if len(sys.argv) > 1 else 0
version_tuple = (1, 0, build) 

# Задаём версию в одном месте (major, minor, patch, build)
version_tuple = (1, 0, 0, build)

# Форматируем версию для строковых полей
version_str = ".".join(map(str, version_tuple))


version_info = vi.VSVersionInfo(
    ffi=vi.FixedFileInfo(
        filevers=version_tuple,
        prodvers=version_tuple,
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        vi.StringFileInfo([vi.StringTable('041904B0', [  # Русский (0419)
            vi.StringStruct('CompanyName', 'БиоТехно'),
            vi.StringStruct('FileDescription', 'DatexLite'),
            vi.StringStruct('FileVersion', version_str),
            vi.StringStruct('ProductVersion', version_str),
            vi.StringStruct('InternalName', 'DatexLite'),
            vi.StringStruct('LegalCopyright', '© 2025 БиоТехно'),
            vi.StringStruct('OriginalFilename', 'DatexLite.exe'),
            vi.StringStruct('ProductName', 'DatexLite'),
        ])]),
        vi.VarFileInfo([vi.VarStruct('Translation', [1049, 1251])])  # 1049 = 0x0419
    ]
)

with open('version_info.txt', 'w', encoding='utf-8') as f:
    f.write(str(version_info))