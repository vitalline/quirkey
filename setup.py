from datetime import datetime
from os import walk
from os.path import join, relpath, isfile
from pathlib import PurePath
from zipfile import ZipFile, ZIP_DEFLATED

from cx_Freeze import setup, Executable


def gen_data_files(include, exclude=()):
    data_files = []
    for directory in include:
        for root, dirs, files in walk(directory):
            for file in files:
                path = PurePath(join(root, file))
                for excluded in exclude:
                    if path.is_relative_to(excluded):
                        path = None
                        break
                if path is not None:
                    data_files += [(path, path)]
    return data_files


def zip_write(zip_handle, zip_path, include, exclude=()):
    for directory in include:
        for root, dirs, files in walk(directory):
            for file in files:
                path = PurePath(join(root, file))
                for excluded in exclude:
                    if path.is_relative_to(excluded):
                        path = None
                        break
                if path is not None:
                    zip_handle.write(path, relpath(path, join(zip_path, directory)))


setup(
    name='quirkey',
    version='0.1.0',
    options={
        'build_exe': {
            'includes': ['win32com'],
            'include_files': gen_data_files(
                ['keyboards', 'quirks'],
                ['keyboards/__pycache__', 'quirks/__pycache__'],
            ) + ['config.ini'],
        }
    },
    executables=[
        Executable('console.py'),
        Executable('keyboard.py', target_name='keyboard_debug'),
        Executable('keyboard.py', base='Win32GUI'),
    ],
)

timestamp = datetime.now().strftime('%Y%m%d')
version = 1
filename = 'release/keyboard.win-amd64-3.9-{}v{}.zip'
while isfile(filename.format(timestamp, version)):
    version += 1
filename = filename.format(timestamp, version)
zip_file = ZipFile(filename, 'w', ZIP_DEFLATED)
zip_write(zip_file, '', ['build/exe.win-amd64-3.9'], [
    'build/exe.win-amd64-3.9/quirks',
    'build/exe.win-amd64-3.9/console.exe',
    # 'build/exe.win-amd64-3.9/keyboard_debug.exe',
])
zip_file.close()
