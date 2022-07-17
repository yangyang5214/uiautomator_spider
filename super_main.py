# -*- coding: UTF-8 -*-
import sys
import os


def main(base_dir: str):
    with open(os.path.join(base_dir, 'task.txt'), 'r') as f:
        lines = f.readlines()

    for line in lines:
        print('*' * 30)
        line = f"cd {base_dir} && " + line
        print(line)
        print('*' * 30)
        os.system(line)


if __name__ == '__main__':
    base_dir = os.path.dirname(sys.argv[0])
    main(base_dir)
