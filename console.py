import os
import sys
import pyperclip
from importlib import import_module, util

sys.path.append(os.path.abspath(os.getcwd()))


def console():
    while True:
        quirk = input('Enter quirk name: ').strip()
        if quirk == '':
            break
        if util.find_spec(f'quirks.{quirk}') is None:
            continue
        module = import_module(f'quirks.{quirk}')
        while True:
            if hasattr(module, 'multiline'):
                message = ''
                print('Enter message. End with one empty line.')
                while True:
                    line = input()
                    if line.strip() == '':
                        message = message[:-1]
                        break
                    message += line + '\n'
            else:
                message = input('Enter message: ')
            if message.strip() == '':
                break
            message = module.quirk(message)
            if not (hasattr(module, 'copy_output') and module.copy_output is False):
                pyperclip.copy(message)
            if not (hasattr(module, 'print_output') and module.print_output is False):
                print(message, end='\n')


if __name__ == '__main__':
    console()
