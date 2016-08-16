class TreeNode(object):
    def __init__(self, value=None):
        self.value = value
        self.parent = None
        self.children = []

    def add(self, node):
        node.parent = self
        self.children.append(node)

    def walk(self):
        # walk pre-order traversal
        for child in self.children:
            for n in child.walk():
                yield n
        yield self
