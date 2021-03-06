#!/usr/bin/env python3
import argparse
import os
import pickle
import sys


class RetCode():
    OK, ERR, ARG, WARN = range(4)


class TodoError(Exception):
    pass


class TodoList(object):

    def __init__(self, todo_file=None):
        self.todo_list = []
        self.todo_file = None

        if todo_file and os.path.isfile(todo_file):
            self.load(todo_file)

    def load(self, todo_file):
        self.todo_file = todo_file
        try:
            with open(self.todo_file, 'r+b') as f:
                self.todo_list = pickle.load(f)
        except EOFError:
            # File is empty.
            pass

    def save(self):
        with open(self.todo_file, 'wb') as f:
            pickle.dump(self.todo_list, f)

    def show(self):
        found_categories = []

        if len(self.todo_list) == 0:
            print("The todo list is empty. Add items with the '-a' argument.")
            return

        first_found = False
        # Print all the uncategorized todos first
        for k,item in enumerate(self.todo_list):
            item_s = item.strip().split(':', 1)
            if len(item_s) == 1:
                print('{}{:>3} - {}' \
                      .format('' if first_found else '\n', k+1, item.strip()))
                first_found = True
            elif item_s[0].strip() not in found_categories:
                found_categories.append(item_s[0].strip())

        # Print all categorized todos
        for cat in found_categories:
            print('\n{}:\n'.format(cat))
            for k,item in enumerate(self.todo_list):
                item_s = item.split(':', 1)
                if len(item_s) == 2 and item_s[0] == cat:
                    print('{:>3} - {}'.format(k+1, item_s[1].strip()))

    def add(self, todo):
        self.todo_list.append(todo)

    def delete(self, index):
        try:
            item = self.todo_list[index]
            del self.todo_list[index]
            print('\nRemoved: {0}'.format(item))
        except IndexError:
            raise TodoError('Index {} is out of range.'.format(index + 1))

    def reword(self, index):
        try:
            print('\nOriginal: {0}'.format(self.todo_list[index]))
            reword = input('Reword:   ')
            self.todo_list[index] = reword
        except IndexError:
            raise TodoError('Index {} is out of range.'.format(index + 1))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Simple Todo Script'
    )

    parser.add_argument(
        '-a',
        dest='add',
        metavar='"todo item"',
        help='add a todo item'
    )

    parser.add_argument(
        '-d',
        dest='delete',
        metavar='#',
        type=int,
        help='delete a todo item at index #'
    )

    parser.add_argument(
        '-r',
        dest='reword',
        metavar='#',
        type=int,
        help='reword a todo item at index #'
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    todo_file = os.path.expanduser('~/.todo_list')

    todo_list = TodoList(todo_file)

    if args.add:
        todo_list.add(args.add)
    elif args.delete:
        todo_list.delete(args.delete - 1)
    elif args.reword:
        todo_list.reword(args.reword - 1)

    if args.add or args.delete or args.reword:
        todo_list.save()

    todo_list.show()

    return RetCode.OK


if __name__ == '__main__':
    try:
        retcode = main()
    except KeyboardInterrupt as e:
        retcode = RetCode.WARN
    except TodoError as e:
        retcode = RetCode.ARG
        print('ERROR: {}'.format(e))

    sys.exit(retcode)
