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
                    zip_handle.write(path, join(zip_path, relpath(root, directory), file))


setup(
    name='quirkey',
    version='0.2.0',
    options={
        'build_exe': {
            'build_exe': join('build', 'keyboard'),
            'excludes': ['numpy', 'scipy', 'test', 'unittest'],
            'includes': ['win32com'],
            'include_files': gen_data_files(
                ['effects', 'keyboards'],
                ['effects/glitch.py', 'effects/__pycache__', 'keyboards/__pycache__'],
            ) + ['config_default.ini', 'config_rb.ini', 'config_tiled.ini'],
        }
    },
    executables=[
        Executable('keyboard.py', target_name='keyboard_debug'),
        Executable('keyboard.py', base='Win32GUI'),
    ],
)

setup(
    name='quirkey_full',
    version='0.2.0',
    options={
        'build_exe': {
            'build_exe': join('build', 'keyboard_full'),
            'excludes': ['scipy', 'test', 'unittest'],
            'includes': ['glitch_this', 'win32com'],
            'include_files': gen_data_files(
                ['effects', 'keyboards'],
                ['effects/__pycache__', 'keyboards/__pycache__'],
            ) + ['config_default.ini', 'config_rb.ini', 'config_tiled.ini'],
        }
    },
    executables=[
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
zip_write(zip_file, '', ['build/keyboard'], [
    'build/keyboard/config_default.ini',
    'build/keyboard/config_rb.ini',
    'build/keyboard/config_tiled.ini',
    'build/keyboard/keyboards/rb.py',
    'build/keyboard/keyboards/assets/rb',
    'build/keyboard/keyboards/hs.py',
    'build/keyboard/keyboards/assets/hs',
    'build/keyboard/keyboards/tiles.py',
    'build/keyboard/keyboards/assets/tiles',
    'build/keyboard/effects/tiled.py',
    # 'build/keyboard/keyboard_debug.exe',
])
zip_file.write('build/keyboard/config_default.ini', 'config.ini')
zip_file.close()
filename = filename.replace('keyboard', 'keyboard_rb')
zip_file = ZipFile(filename, 'w', ZIP_DEFLATED)
zip_write(zip_file, '', ['build/keyboard'], [
    'build/keyboard/config_default.ini',
    'build/keyboard/config_rb.ini',
    'build/keyboard/config_tiled.ini',
    'build/keyboard/keyboards',
    'build/keyboard/effects',
    # 'build/keyboard/keyboard_debug.exe',
])
zip_write(zip_file, 'keyboards/assets/rb', ['build/keyboard/keyboards/assets/rb'], [])
zip_write(zip_file, 'keyboards/assets/util', ['build/keyboard/keyboards/assets/util'], [])
zip_file.write('build/keyboard/keyboards/rb.py', 'keyboards/rb.py')
zip_file.write('build/keyboard/config_rb.ini', 'config.ini')
zip_file.close()
filename = filename.replace('keyboard_rb', 'keyboard_tiled')
zip_file = ZipFile(filename, 'w', ZIP_DEFLATED)
zip_write(zip_file, '', ['build/keyboard'], [
    'build/keyboard/config_default.ini',
    'build/keyboard/config_rb.ini',
    'build/keyboard/config_tiled.ini',
    'build/keyboard/keyboards',
    'build/keyboard/effects',
    # 'build/keyboard/keyboard_debug.exe',
])
zip_write(zip_file, 'keyboards/assets/tiles', ['build/keyboard/keyboards/assets/tiles'], [])
zip_write(zip_file, 'keyboards/assets/util',
          ['build/keyboard/keyboards/assets/util'],
          ['build/keyboard/keyboards/assets/util/cursor.png'])
zip_file.write('build/keyboard/keyboards/assets/util/cell.png', 'keyboards/assets/util/cursor.png')
zip_file.write('build/keyboard/keyboards/tiles.py', 'keyboards/tiles.py')
zip_file.write('build/keyboard/effects/tiled.py', 'effects/tiled.py')
zip_file.write('build/keyboard/config_tiled.ini', 'config.ini')
zip_file.close()
filename = filename.replace('keyboard_tiled', 'keyboard_full')
zip_file = ZipFile(filename, 'w', ZIP_DEFLATED)
zip_write(zip_file, '', ['build/keyboard_full'], [
    'build/keyboard_full/config_default.ini',
    'build/keyboard_full/config_rb.ini',
    'build/keyboard_full/config_tiled.ini',
    'build/keyboard_full/keyboards/rb.py',
    'build/keyboard_full/keyboards/assets/rb',
    'build/keyboard_full/keyboards/hs.py',
    'build/keyboard_full/keyboards/assets/hs',
    'build/keyboard_full/keyboards/tiles.py',
    'build/keyboard_full/keyboards/assets/tiles',
    'build/keyboard_full/effects/tiled.py',
    # 'build/keyboard_full/keyboard_debug.exe',
])
zip_file.write('build/keyboard_full/config_default.ini', 'config.ini')
zip_file.close()