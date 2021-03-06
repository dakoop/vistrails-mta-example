import csv
from itertools import izip
try:
    import numpy
except ImportError:
    numpy = None

from vistrails.core.modules.vistrails_module import ModuleError
from ..common import TableObject, Table, InternalModuleError


def count_lines(fp):
    lines = 0
    for line in fp:
        lines += 1
    return lines


class CSVTable(TableObject):

    def __init__(self, csv_file, header_present, delimiter, 
                 skip_lines=0, dialect=None, use_sniffer=True):
        TableObject.__init__(self)
        self._rows = None

        self.header_present = header_present
        self.delimiter = delimiter
        self.filename = csv_file
        self.skip_lines = skip_lines
        self.dialect = dialect

        (self.columns, self.names, self.delimiter, 
         self.header_present, self.dialect) = \
            self.read_file(csv_file, delimiter, header_present, skip_lines,
                           dialect, use_sniffer)
        if self.header_present:
            self.skip_lines += 1

        self.column_cache = {}

    @staticmethod
    def read_file(filename, delimiter=None, header_present=True, 
                  skip_lines=0, dialect=None, use_sniffer=True):
        if delimiter is None and use_sniffer is False:
            raise InternalModuleError("Must set delimiter if not using sniffer")

        try:
            with open(filename, 'rb') as fp:
                if use_sniffer:                    
                    first_lines = ""
                    line = fp.readline()
                    for i in xrange(skip_lines):
                        if not line:
                            break
                        line = fp.readline()
                    for i in xrange(5):
                        if not line:
                            break
                        first_lines += line
                        line = fp.readline()
                    sniffer = csv.Sniffer()
                    fp.seek(0)
                    if delimiter is None:
                        dialect = sniffer.sniff(first_lines)
                        delimiter = dialect.delimiter
                        # cannot determine header without sniffing delimiter
                        if header_present is None:
                            header_present = sniffer.has_header(first_lines)

                for i in xrange(skip_lines):
                    if not line:
                        raise IntneralModuleError("skip_lines greater than "
                                                  "the number of lines in the "
                                                  "file")
                    line = fp.readline()

                if dialect is not None:
                    reader = csv.reader(fp, dialect=dialect)
                else:
                    reader = csv.reader(fp, delimiter=delimiter)
                result = reader.next()
                column_count = len(result)

                if header_present:
                    column_names = [name.strip() for name in result]
                else:
                    column_names = None
        except IOError:
            raise InternalModuleError("File does not exist")
            
        return column_count, column_names, delimiter, header_present, dialect

    def get_column(self, index, numeric=False):
        if (index, numeric) in self.column_cache:
            return self.column_cache[(index, numeric)]

        if numeric and numpy is not None:
            result = numpy.loadtxt(
                    self.filename,
                    dtype=numpy.float32,
                    delimiter=self.delimiter,
                    skiprows=self.skip_lines,
                    usecols=[index])
        else:
            with open(self.filename, 'rb') as fp:
                for i in xrange(self.skip_lines):
                    line = fp.readline()
                    if not line:
                        raise IntneralModuleError("skip_lines greater than "
                                                  "the number of lines in the "
                                                  "file")
                if self.dialect is not None:
                    reader = csv.reader(fp, dialect=self.dialect)
                else:
                    reader = csv.reader(fp, delimiter=self.delimiter)

                result = [row[index] for row in reader]
            if numeric:
                result = [float(e) for e in result]

        self.column_cache[(index, numeric)] = result
        return result

    @property
    def rows(self):
        if self._rows is not None:
            return self._rows
        with open(self.filename, 'rb') as fp:
            self._rows = count_lines(fp)
        self._rows -= self.skip_lines
        return self._rows


class CSVFile(Table):
    _input_ports = [
            ('file', '(org.vistrails.vistrails.basic:File)'),
            ('delimiter', '(org.vistrails.vistrails.basic:String)',
             {'optional': True}),
            ('header_present', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"}),
            ('sniff_header', '(org.vistrails.vistrails.basic:Boolean)',
             {'optional': True, 'defaults': "['True']"}),
            ('skip_lines', '(org.vistrails.vistrails.basic:Integer)',
             {'optional': True, 'defaults': "['0']"}),
            ('dialect', '(org.vistrails.vistrails.basic:String)',
             {'optional': True})]
    _output_ports = [
            ('column_count', '(org.vistrails.vistrails.basic:Integer)'),
            ('column_names', '(org.vistrails.vistrails.basic:List)'),
            ('value', '(org.vistrails.vistrails.tabledata:read|CSVFile)')]

    def compute(self):
        csv_file = self.getInputFromPort('file').name
        header_present = self.getInputFromPort('header_present')
        delimiter = self.forceGetInputFromPort('delimiter', None)
        skip_lines = self.getInputFromPort('skip_lines')
        dialect = self.forceGetInputFromPort('dialect', None)
        sniff_header = self.getInputFromPort('sniff_header')

        try:
            table = CSVTable(csv_file, header_present, delimiter, skip_lines,
                             dialect, sniff_header)
        except InternalModuleError, e:
            e.raise_module_error(self)

        self.setResult('column_count', table.columns)
        self.setResult('column_names', table.names)
        self.setResult('value', table)


_modules = [CSVFile]


###############################################################################

from StringIO import StringIO
import unittest
from vistrails.tests.utils import execute, intercept_result
from ..identifiers import identifier
from ..common import ExtractColumn


class CSVTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls._test_dir = os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'test_files')

    def test_csv_numeric(self):
        """Uses CSVFile and ExtractColumn to load a numeric array.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            with intercept_result(CSVFile, 'column_count') as columns:
                self.assertFalse(execute([
                        ('read|CSVFile', identifier, [
                            ('file', [('File', self._test_dir + '/test.csv')]),
                        ]),
                        ('ExtractColumn', identifier, [
                            ('column_index', [('Integer', '1')]),
                            ('column_name', [('String', 'col 2')]),
                            ('numeric', [('Boolean', 'True')]),
                        ]),
                        ('PythonSource', 'org.vistrails.vistrails.basic', [
                            ('source', [('String', '')]),
                        ]),
                    ],
                    [
                        (0, 'value', 1, 'table'),
                        (1, 'value', 2, 'l'),
                    ],
                    add_port_specs=[
                        (2, 'input', 'l',
                         'org.vistrails.vistrails.basic:List'),
                    ]))
                # Here we use a PythonSource just to check that a numpy array
                # can be passed on a List port
        self.assertEqual(columns, [3])
        self.assertEqual(len(results), 1)
        self.assertEqual(list(results[0]), [2.0, 3.0, 14.5])

    def test_csv_mismatch(self):
        """Uses CSVFile and ExtractColumn with mismatching columns.
        """
        self.assertTrue(execute([
                ('read|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, [
                    ('column_index', [('Integer', '0')]), # index is wrong
                    ('column_name', [('String', 'col 2')]),
                ]),
            ],
            [
                (0, 'value', 1, 'table'),
            ]))

    def test_csv_missing(self):
        """Uses CSVFile and ExtractColumn with a nonexisting column.
        """
        self.assertTrue(execute([
                ('read|CSVFile', identifier, [
                    ('file', [('File', self._test_dir + '/test.csv')]),
                ]),
                ('ExtractColumn', identifier, [
                    ('column_name', [('String', 'col not here')]),
                ]),
            ],
            [
                (0, 'value', 1, 'table'),
            ]))

    def test_csv_nonnumeric(self):
        """Uses CSVFile and ExtractColumn to load strings.
        """
        with intercept_result(ExtractColumn, 'value') as results:
            self.assertFalse(execute([
                    ('read|CSVFile', identifier, [
                        ('file', [('File', self._test_dir + '/test.csv')]),
                        ('header_present', [('Boolean', 'False')]),
                    ]),
                    ('ExtractColumn', identifier, [
                        ('column_index', [('Integer', '2')]),
                        ('numeric', [('Boolean', 'False')]),
                    ]),
                ],
                [
                    (0, 'value', 1, 'table'),
                ]))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0],
                         ['col moutarde', '4', 'not a number', '7'])


class TestCountlines(unittest.TestCase):
    def test_countlines(self):
        # Simple
        fp = StringIO("first\nsecond")
        self.assertEqual(count_lines(fp), 2)

        # With newline at EOF
        fp = StringIO("first\nsecond\n")
        self.assertEqual(count_lines(fp), 2)

        # Empty
        fp = StringIO("")
        self.assertEqual(count_lines(fp), 0)

        # Single newline
        fp = StringIO("\n")
        self.assertEqual(count_lines(fp), 1)
