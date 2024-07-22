import sys
import traceback
from typing import TextIO


class Tee(object):
    def __init__(self, file: TextIO | str):
        if isinstance(file, str):
            self.should_close = True
            self.file = open(file, "w")
        else:
            self.should_close = False  # The caller is responsible for closing the file
            self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def __enter__(self):
        sys.stdout = _StreamTee(self.file, self.stdout)
        sys.stderr = _StreamTee(self.file, self.stderr)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        if exc_type is not None:
            self.file.write(traceback.format_exc())
        if self.should_close:
            self.file.close()


class _StreamTee:
    """
    A class that duplicates writes to a file and a stream
    """

    def __init__(self, file: TextIO, stream):
        self.file = file
        self.stream = stream

    def write(self, data):
        self.file.write(data)
        self.stream.write(data)

    def flush(self):
        self.file.flush()
        self.stream.flush()
