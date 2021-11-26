import os
import sys

from keyboard.manager import KeyboardManager

sys.path.append(os.path.abspath(os.getcwd()))

if __name__ == '__main__':
    KeyboardManager().run()
