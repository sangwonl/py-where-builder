import re
import sys

from . import tree

if sys.version_info.major == 2:
    from .py2 import *
else:
    from .py3 import *


ESCAPE_REGEX = re.compile(r'[\0\n\r\032\'\"\\]')
ESCAPE_MAP = {
    '\0': '\\0', '\n': '\\n', '\r': '\\r', '\032': '\\Z',
    '\'': '\\\'', '"': '\\"', '\\': '\\\\'
}

def escape_string(value, mapping=None):
    return ('%s' % (ESCAPE_REGEX.sub(lambda match: ESCAPE_MAP.get(match.group(0)), value),))


class Q(object):
    def __init__(self, query_stmt, *args, **kwargs):
        self.translated_stmt = self._format(query_stmt, *args, **kwargs) 

    def clause(self):
        return self.translated_stmt

    def _format(self, query_stmt, *args, **kwargs):
        matches = re.findall(r':[_a-zA-Z\d]+', query_stmt)
        if kwargs:
            if not all([(':%s' % k) in matches for k in kwargs]):
                raise ValueError
            query_stmt = self._format_with_kwargs(query_stmt, matches, **kwargs)
        elif args:
            if len(args) != len(matches):
                raise ValueError
            query_stmt = self._format_with_args(query_stmt, matches, *args)
        return query_stmt

    def _value_by_type(self, val):
        if val is None:
            val = 'null'
        elif isinstance(val, STRING_TYPE):
            val = '\'%s\'' % escape_string(val)
        elif isinstance(val, NUMBER_TYPE):
            val = '%d' % val
        elif isinstance(val, float):
            val = '%f' % val
        else:
            raise ValueError
        return val

    def _format_with_args(self, query_stmt, matches, *args):
        for i in range(len(matches)):
            query_stmt = query_stmt.replace(matches[i], self._value_by_type(args[i])) 
        return query_stmt

    def _format_with_kwargs(self, query_stmt, matches, **kwargs):
        for m in matches:
            query_stmt = query_stmt.replace(m, self._value_by_type(kwargs.get(m[1:], '')))
        return query_stmt


class WhereNode(tree.TreeNode):
    def __init__(self, value, *args):
        super(WhereNode, self).__init__(value)
        for q in args:
            if isinstance(q, WhereNode):
                self.add(q)
            else:
                self.add(WhereNode(q))

    def clause(self):
        stack = []
        ops = ('and', 'or')
        for n in self.walk():
            op = n.value
            if op in ops:
                operands = []
                for s in reversed(stack):
                    if n.parent == s.parent:
                        break
                    pop = stack.pop()
                    if pop.value.clause() != '':
                        operands.append(pop)

                reversed_operands = []
                for o in reversed(operands):
                    reversed_operands.append('(%s)' % o.value.clause())
                    
                stmt = (' %s ' % op).join(reversed_operands)
                combined = WhereNode(Q(stmt))
                combined.parent = self
                stack.append(combined)
            else:
                stack.append(n)
        return stack.pop().value.clause()


class AND(WhereNode):
    def __init__(self, *args):
        super(AND, self).__init__('and', *args)


class OR(WhereNode):
    def __init__(self, *args):
        super(OR, self).__init__('or', *args)


def _conditional_clause(q):
    if q is None:
        return ''
    return q.clause()


class SWITCH(object):
    def __init__(self, switch, *args):
        cases_map = {}
        for (case, q) in args:
            cases_map[case] = q

        q = cases_map.get(switch)
        self.translated_stmt = _conditional_clause(q) if q else ''

    def clause(self):
        return self.translated_stmt


class IF(object):
    def __init__(self, condition, q):
        self.translated_stmt = _conditional_clause(q) if condition else ''

    def clause(self):
        return self.translated_stmt