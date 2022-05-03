# Author: Arturs Laizans
# Package for displaying and saving verbose log
'''
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging


class Log:

    # For initialization, class Log takes 3 arguments: path, logic, file_mode.
    # path:
    #  - False - don't do logging. It won't save anything to file and won't print anything to stdout.
    #  - True - will print verbose output to stdout.
    #  - string - will save the verbose output to file named as this string.
    # logic:
    #  - 'OR' - if the path is a string, only saves verbose to file;
    #  - 'AND' - if the path is string, prints verbose output to stdout and saves to file.
    # file_mode:
    #  - 'a' - appends log to existing file
    #  - 'w' - creates a new file for logging, if a file with such name already exists, it will be overwritten.

    def __init__(self, path, logic, file_mode):

        # If logging to file is needed, configure it
        if path is not True and type(path) == str:
            logging.basicConfig(filename=path, filemode=file_mode,
                                format='%(asctime)s - %(message)s', level=logging.DEBUG)

        # Define different log actions that can be used
        def nothing(message):
            pass

        def to_file(message):
            logging.debug(message)

        def to_stdout(message):
            print(message)

        def both(message):
            print(message)
            logging.debug(message)

        # Set appropriate action depending on path and logic values
        if not path:
            self.func = nothing

        elif path is True:
            self.func = to_stdout

        elif path is not True and type(path) == str and logic == 'OR':
            self.func = to_file

        elif path is not True and type(path) == str and logic == 'AND':
            self.func = both
        else:
            self.func = to_stdout

    def __call__(self, message):
        self.func(message)
