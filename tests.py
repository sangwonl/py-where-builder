#-*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

from wherebuilder import tree
from wherebuilder import qb


class TreeTestCase(unittest.TestCase):
    def tree_add(self):
        node = tree.TreeNode(3)
        node.add(tree.TreeNode(5))
        node.add(tree.TreeNode(6))
        self.assertEquals(node.value, 3)
        self.assertEquals(node.children[0], 5)
        self.assertEquals(node.children[0], 6)

        traversed = []
        for n in node.walk():
            traversed.append(n.value)

        self.assertEquals(traversed[0], 5)
        self.assertEquals(traversed[1], 6)
        self.assertEquals(traversed[2], 3)


class DumbQueryBuilderTestCase(unittest.TestCase):
    def test_q(self):
        q = qb.Q('a.first_name = :first and a.age >= :age', first='eddy', age=34)
        expected = "a.first_name = 'eddy' and a.age >= 34"
        self.assertEquals(q.clause(), expected)

        q = qb.Q('a.first_name = :first and a.age >= :age', 'eddy', 34)
        expected = "a.first_name = 'eddy' and a.age >= 34"
        self.assertEquals(q.clause(), expected)

    def test_similar_query_parameter(self):
        q = qb.AND(qb.Q('a.first_name = :first and a.last_name = :first2', first='eddy', first2='lee'))
        expected = u"(a.first_name = 'eddy') and (a.last_name = 'lee')"
        self.assertEquals(q.clause(), expected)

    def test_unicode_in_query(self):
        q = qb.AND(qb.Q('a.first_name = :first', u'상원'), qb.Q('a.last_name = :last', u'이'))
        expected = u"(a.first_name = '상원') and (a.last_name = '이')"
        self.assertEquals(q.clause(), expected)

    def test_and_or_builder(self):
        where = qb.OR(
            qb.Q('a.first_name = :first and a.last_name = :last', first='eddy', last='lee'),
            qb.AND(qb.Q('a.age >= 34'), qb.Q('a.allowed_push = :allowed_push', allowed_push=1))
        )
        expected = "(a.first_name = 'eddy' and a.last_name = 'lee') or ((a.age >= 34) and (a.allowed_push = 1))"
        self.assertEquals(where.clause(), expected)

    def test_and_or_with_emty_q(self):
        where = qb.OR(qb.IF(False, qb.Q('a.age <= 40')), qb.Q('a.age >= 34'))
        expected = '(a.age >= 34)'
        self.assertEquals(where.clause(), expected)

    def test_switch_builder(self):
        var = 'case1'
        where = qb.SWITCH(var,
            ('case1', qb.AND(qb.Q('a.age >= 34'), qb.Q('a.age < :age', age=50))),
            ('case2', qb.AND(qb.Q('a.age >= 50'), qb.Q('a.age < :age', age=60)))
        )
        expected = '(a.age >= 34) and (a.age < 50)'
        self.assertEquals(where.clause(), expected)

    def test_switch_undefined_case(self):
        var = 'case3'
        where = qb.SWITCH(var,
            ('case1', qb.AND(qb.Q('a.age >= 34'), qb.Q('a.age < :age', age=50))),
            ('case2', qb.AND(qb.Q('a.age >= 50'), qb.Q('a.age < :age', age=60)))
        )
        self.assertEquals(where.clause(), '')

    def test_if_builder(self):
        var = 30
        where = qb.IF(var > 40, qb.Q('a.age > 30'))
        self.assertEquals(where.clause(), '')

    def test_all_together(self):
        where = qb.OR(
            qb.Q('a.first_name = :first and a.last_name = :last', first='eddy', last='lee'),
            qb.AND(qb.Q('a.age >= 34'), qb.Q('a.allowed_push = :allowed_push', allowed_push=1)),
            qb.IF(True, qb.Q('a.age > 30')),
            qb.IF(True, qb.SWITCH('inner_case1',
                ('inner_case1', qb.Q('a.age >= 10')),
                ('inner_case2', qb.Q('a.age >= 15')))
            ),
            qb.SWITCH('case2',
                ('case1', qb.AND(qb.Q('a.age >= 34'), qb.Q('a.age < :age', age=50))),
                ('case2', qb.AND(qb.Q('a.age >= 50'), qb.Q('a.age < :age', age=60)))
            )
        )
        expected = "(a.first_name = 'eddy' and a.last_name = 'lee') or ((a.age >= 34) and (a.allowed_push = 1)) or " \
            + "(a.age > 30) or (a.age >= 10) or ((a.age >= 50) and (a.age < 60))"
        self.assertEquals(where.clause(), expected)
