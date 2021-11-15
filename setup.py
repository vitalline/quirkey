from os import walk
from os.path import join
from pathlib import PurePath

from cx_Freeze import setup, Executable


def gen_data_files(include, exclude=()):
    data_files = []
    for directory in include:
        for path, dirs, files in walk(directory):
            for excluded in exclude:
                if PurePath(path).is_relative_to(excluded):
                    path = None
                    break
            if path is not None:
                data_files += [(join(path, file), join(path, file)) for file in files]
    return data_files


setup(
    name='quirkey',
    version='0.0.1',
    options={
        'build_exe': {
            'includes': ['win32com'],
            'include_files': gen_data_files(
                ['keyboards', 'quirks'],
                ['keyboards/__pycache__', 'quirks/__pycache__'],
            ),
        }
    },
    executables=[
        Executable('console.py'),
        Executable('keyboard.py', target_name='keyboard_debug'),
        Executable('keyboard.py', base='Win32GUI'),
    ],
)
