import os
from contextlib import contextmanager


@contextmanager
def input_file(filename, mode='r'):
    f = open(os.path.join(os.path.dirname(__file__), '..', 'test_files', filename), mode)
    yield f
    f.close()


VALID_FILES = ['test.doc',
               'test.docx',
               'test.pdf',
               'test.xls',
               'test.xlsx',
               'Lenna.png',
               'random_data']
