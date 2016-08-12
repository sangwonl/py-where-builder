import tree
import re


class Q(object):
    def __init__(self, query_stmt, *args, **kwargs):
        self.translated_stmt = self._format(query_stmt, *args, **kwargs) 

    def clause(self):
        return self.translated_stmt

    def _format(self, query_stmt, *args, **kwargs):
        matches = re.findall(r':[_a-zA-Z\d]+', query_stmt)
        if kwargs:
            if not all([(':%s' % k) in matches for k in kwargs]):
                print kwargs
                raise ValueError
            query_stmt = self._format_with_kwargs(query_stmt, matches, **kwargs)
        elif args:
            if len(args) != len(matches):
                raise ValueError
            query_stmt = self._format_with_args(query_stmt, matches, *args)
        return query_stmt

    def _value_by_type(self, val):
        if type(val) in (basestring, str, unicode):
            val = '\'%s\'' % val
        elif type(val) in (int, long):
            val = '%d' % val
        elif type(val) in (float):
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
            elif isinstance(q, Q):
                self.add(WhereNode(q))

    def clause(self):
        full_stmt = ''
        stack = []
        for n in self.walk():
            if isinstance(n.value, Q):
                stmt = n.value.clause()
                stack.append(stmt)
            elif n.value in ('and', 'or'):
                op_right = stack.pop()
                op_left = stack.pop()
                stmt = '(%s) %s (%s)' % (op_left, n.value, op_right)
                stack.append(stmt)
        return stack.pop()


class AND(WhereNode):
    def __init__(self, *args):
        super(AND, self).__init__('and', *args)


class OR(WhereNode):
    def __init__(self, *args):
        super(OR, self).__init__('or', *args)


def _conditional_clause(q):
    if q is None:
        return ''

    if q and (isinstance(q, Q) or isinstance(q, WhereNode)):
        return q.clause()

    return q


class SWITCH(object):
    def __init__(self, switch, *args):
        self.switch = switch
        self.cases_map = {}
        for (case, q) in args:
            self.cases_map[case] = q

    def clause(self):
        q = self.cases_map[self.switch]
        return _conditional_clause(q)

class IF(object):
    def __init__(self, condition, q):
        self.condition = condition
        self.q = q

    def clause(self):
        return _conditional_clause(self.q) if self.condition else ''
