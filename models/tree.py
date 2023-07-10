import pandas as pd

levels = ['children', 'g_children', 'gg_children']


class Tree:
    def __init__(self, name):
        self.tree_name = name.lower().replace(' ', '_')
        self.root = None
        self.paths = []

    def add_root(self, val):
        self.root = val

    def printTree(self, node):
        if len(node.children) == 0:
            print(node.name)
        else:
            print(node.name)
            for child in node.children.values():
                self.printTree(child)

    def Traverse(self, path):
        node = self.root
        skip = 0
        for p in path:
            if p != '':
                if skip > 0:
                    poss = getattr(node, levels[skip])
                    x = [val for key, val in poss.items() if p in key]
                    return x
                node = node.children[p]
            else:
                skip = skip + 1
        return [node]


class Node:
    def __init__(self, name, parent=None):
        self.name = name.lower().replace(' ', '_')
        self.parent = parent
        self.children = dict()
        self.g_children = dict()
        self.gg_children = dict()
        self.values = pd.DataFrame({'Id': pd.Series(dtype='str'),
                                    'Department__c': pd.Series(dtype='str'),
                                    'Category__c': pd.Series(dtype='str'),
                                    'Sub_Category__c': pd.Series(dtype='str'),
                                    'Type__c': pd.Series(dtype='str'),
                                    'Fee': pd.Series(dtype='int')})

    def add_node(self, node):
        # print(f"Adding {Node.name} to {self.name}")
        self.children[node.name] = node
        try:
            if self.parent is not None:
                # print(f"Adding {Node.name} to {self.parent.name} as grand child")
                self.parent.g_children[f"{self.name}_{node.name}"] = node
                if self.parent.parent is not None:
                    # print(f"Adding {Node.name} to {self.parent.parent.name} as great grand child")
                    self.parent.parent.gg_children[f"{self.parent.name}_{self.name}_{node.name}"] = node
        except Exception as e:
            print(f"Error adding extended family - {e}")

    def add_values(self, df):
        self.values = pd.concat([self.values, df[["Id", "Department__c", "Category__c", "Sub_Category__c", "Type__c", "Fee"]]])

    def list_family(self):
        print(f"Children: {[child for child in self.children]}")
        print(f"Grand Children: {[g_child for g_child in self.g_children]}")
        print(f"Great Grand Children: {[gg_child for gg_child in self.gg_children]}")
        # return [child for child in self.children]


def formatName(name):
    return name.lower().replace(' ', '_')


def printTree(tree):
    if len(tree.children) == 0:
        print(tree.name)
    else:
        print(tree.name)
        for child in tree.children:
            printTree(tree.children[child])


def getValues(node):
    tmp = pd.DataFrame()
    if len(node.children) == 0:
        return node.values
    else:
        for child in node.children:
            tmp = pd.concat([tmp, getValues(node.children[child])])
        return tmp


def filter_df(name, layer, df, filter_col, unique_col, g_parent=None, gg_parent=None):
    new_node = Node(name, layer)
    layer.add_node(new_node)
    filtered_df = df.loc[df[filter_col] == name]
    unique = filtered_df[unique_col].unique() if unique_col is not None else []
    unique.sort()
    return new_node, filtered_df, unique


def buildHierarchy(dataObject):
    hierarchy = dict()
    for department in dataObject.departments:
        department = department
        tree = Tree(department)
        tree.add_root(Node(department))
        department_level_df = dataObject.data_frame.loc[dataObject.data_frame['Department__c'] == department]
        categories = department_level_df.Category__c.unique()
        categories.sort()
        for category in categories:
            category_node, category_level_df, sub_categories = filter_df(category, tree.root, department_level_df,
                                                                         'Category__c', 'Sub_Category__c')
            for sub in sub_categories:
                sub_node, sub_level_df, types = filter_df(sub, category_node, category_level_df, 'Sub_Category__c',
                                                          'Type__c', tree.root)
                for fee_type in types:
                    type_node, type_level_df, _ = filter_df(fee_type, sub_node, sub_level_df, 'Type__c', None,
                                                            category_node, tree.root)
                    type_node.add_values(type_level_df)
        hierarchy[department] = tree
    return hierarchy
