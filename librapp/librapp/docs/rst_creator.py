'''
Usage Note:
    1. Use this script to create source/*.rst files
    2. After running this script, run:
       $ make html

Usage option 1:
    $ cd funedapp/docs
    $ python rst_creator.py

Usage option 2:
    $ python manage.py shell
    >>> from funedapp.docs.rst_creator import create_rst
    >>> create_rst()
'''

import django
import os
import sys


# path to BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# funedapp settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "funedapp.settings")
django.setup()

# do this after settings
from funedapp.urls import router

class Formatter(object):
    def format_title(self, title='', level=1):
        if level == 1:
            level_char = '='
        elif level == 2:
            level_char = '-'
        xtitle = '{0}\n{1}'.format(title, len(title)*level_char)
        return xtitle

    def get_toc_tree(self):
        return '.. toctree::'

    def add_indent(self, lines=None, n=1):
        indent = n*' '
        xlines = ['{0}{1}'.format(indent, _) for _ in lines]
        return xlines

    def add_newline(self, lines=None, n=1):
        newline = n*'\n'
        xlines = ['{0}{1}'.format(_, newline) for _ in lines]
        return xlines


class RstCreator(object):
    rf = Formatter()

    def __init__(self):
        self.registry = self._get_router_registry()
        self.dest_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source')

    def _get_router_registry(self):
        registry = list(router.registry)
        return registry

    # create_from_registry
    def create_rst(self):
        self._create_index_files()
        self._create_endpoint_docs()

    def _create_index_files(self):
        filename = 'index.rst'

        title = self.rf.format_title(title='funed API EndPoints')
        toc_tree = self.rf.get_toc_tree()
        header = [title, toc_tree]

        body = [_[0].replace(os.sep, '.') for _ in self.registry]
        body = self.rf.add_indent(lines=body)

        lines = header+body
        lines = self.rf.add_newline(lines=lines)
        self._write_file(filename=filename, content=lines)

    def _create_endpoint_docs(self):
        methods = ['list', 'retrieve', 'create', 'update', 'destroy']
        for entry in self.registry:
            lines = []
            module, klz, base_name = entry
            filebase = module.replace(os.sep, '.')
            filename = '{0}.rst'.format(filebase)
            title = self.rf.format_title(title=module)
            classdocs = [title, klz.__doc__]
            lines.extend(classdocs)
            for method in methods:
                if hasattr(klz, method):
                    title = self.rf.format_title(title=method, level=2)
                    methoddocs = [title, getattr(klz, method).__doc__]
                    lines.extend(methoddocs)
            lines = self.rf.add_newline(lines=lines)
            self._write_file(filename=filename, content=lines)

    def _write_file(self, filename='', content=None):
        filename = os.path.join(self.dest_dir, filename)
        with open(filename, 'w') as wf:
            wf.writelines(content)

def create_rst():
    rc = RstCreator()
    rc.create_rst()
    print 'Done Creating *.rst files. You can find them at dir: ./source\n'


if __name__ == '__main__':
    create_rst()
