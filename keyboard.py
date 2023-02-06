import os
import sys

sys.path.append(os.path.abspath(os.getcwd()))

if __name__ == '__main__':
    from keyboard import manager
    manager.run()
