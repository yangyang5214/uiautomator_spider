# -*- coding: UTF-8 -*-
import os


def main():
    with open('task.txt', 'r') as f:
        lines = f.readlines()

    for line in lines:
        print('*' * 30)
        print(line)
        print('*' * 30)
        os.system(line)


if __name__ == '__main__':
    main()
