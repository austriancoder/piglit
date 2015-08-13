# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# This permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHOR(S) BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

""" Module for results generation """

from __future__ import print_function, absolute_import

from framework import status, exceptions

__all__ = [
    'TestrunResult',
    'TestResult',
]


class Subtests(dict):
    def __setitem__(self, name, value):
        super(Subtests, self).__setitem__(name, status.status_lookup(value))

    def to_json(self):
        res = dict(self)
        res['__type__'] = 'Subtests'
        return res

    @classmethod
    def from_dict(cls, dict_):
        res = cls(dict_)

        if '__type__' in res:
            del res['__type__']

        return res


class StringDescriptor(object):  # pylint: disable=too-few-public-methods
    """A Shared data descriptor class for TestResult.

    This provides a property that can be passed a str or unicode, but always
    returns a unicode object.

    """
    def __init__(self, name, default=unicode()):
        assert isinstance(default, unicode)
        self.__name = name
        self.__default = default

    def __get__(self, instance, cls):
        return getattr(instance, self.__name, self.__default)

    def __set__(self, instance, value):
        if isinstance(value, str):
            setattr(instance, self.__name, value.decode('utf-8', 'replace'))
        elif isinstance(value, unicode):
            setattr(instance, self.__name, value)
        else:
            raise TypeError('{} attribute must be a str or unicode instance, '
                            'but was {}.'.format(self.__name, type(value)))

    def __delete__(self, instance):
        raise NotImplementedError


class TestResult(object):
    """An object represting the result of a single test."""
    __slots__ = ['returncode', '_err', '_out', 'time', 'command', 'traceback',
                 'environment', 'subtests', 'dmesg', '__result', 'images']
    err = StringDescriptor('_err')
    out = StringDescriptor('_out')

    def __init__(self, result=None):
        self.returncode = None
        self.time = float()
        self.command = str()
        self.environment = str()
        self.subtests = Subtests()
        self.dmesg = str()
        self.images = None
        self.traceback = None
        if result:
            self.result = result
        else:
            self.__result = status.NOTRUN

    @property
    def result(self):
        """Return the result of the test.

        If there are subtests return the "worst" value of those subtests. If
        there are not return the stored value of the test.

        """
        if self.subtests:
            return max(self.subtests.itervalues())
        return self.__result

    @result.setter
    def result(self, new):
        try:
            self.__result = status.status_lookup(new)
        except exceptions.PiglitInternalError as e:
            raise exceptions.PiglitFatalError(str(e))

    def to_json(self):
        """Return the TestResult as a json serializable object."""
        obj = {
            '__type__': 'TestResult',
            'returncode': self.returncode,
            'err': self.err,
            'out': self.out,
            'time': self.time,
            'environment': self.environment,
            'subtests': self.subtests,
            'result': self.result,
        }
        return obj

    @classmethod
    def from_dict(cls, dict_):
        """Load an already generated result in dictionary form.

        This is used as an alternate constructor which converts an existing
        dictionary into a TestResult object. It converts a key 'result' into a
        status.Status object

        """
        # pylint will say that assining to inst.out or inst.err is a non-slot
        # because self.err and self.out are descriptors, methods that act like
        # variables. Just silence pylint
        # pylint: disable=assigning-non-slot
        inst = cls()

        # TODO: There's probably a more clever way to do this
        for each in ['returncode', 'time', 'command',
                     'environment', 'result', 'dmesg']:
            if each in dict_:
                setattr(inst, each, dict_[each])

        if 'subtests' in dict_:
            for name, value in dict_['subtests'].iteritems():
                inst.subtests[name] = value

        # out and err must be set manually to avoid replacing the setter
        if 'out' in dict_:
            inst.out = dict_['out']

        if 'err' in dict_:
            inst.err = dict_['err']

        return inst

    def update(self, dict_):
        """Update the results and subtests fields from a piglit test.

        Native piglit tests output their data as valid json, and piglit uses
        the json module to parse this data. This method consumes that raw
        dictionary data and updates itself.

        """
        if 'result' in dict_:
            self.result = dict_['result']
        elif 'subtest' in dict_:
            self.subtests.update(dict_['subtest'])


class TestrunResult(object):
    def __init__(self):
        self.name = None
        self.uname = None
        self.options = None
        self.glxinfo = None
        self.wglinfo = None
        self.lspci = None
        self.time_elapsed = None
        self.tests = {}
