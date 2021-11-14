from os import walk
from os.path import join

from cx_Freeze import setup, Executable


def gen_data_files(source_dirs):
    data_files = []
    for source_dir in source_dirs:
        for path, dirs, files in walk(source_dir):
            data_files += [(join(path, file), join(path, file)) for file in files]
    return data_files


setup(
    name='quirkey',
    version='0.0.1',
    options={"build_exe": {
        'includes': ['win32com'],
        'include_files': gen_data_files(['keyboards', 'quirks'])}},
    executables=[
        Executable("console.py"),
        Executable("keyboard.py", base="Win32GUI"),
    ]
)
