from .class_node import Node
class Tree:
    """
    以字典来表示树：字典的 key 为 node id，value 为以 list 表示的直接子节点
    注意node id是从0开始，0节点为树根，不代表实体节点
    """
    def __init__(self, sentence, word_list, dep_list, pos_list, sentenceID = -1):
        self.sentenceID = sentenceID
        self.sentence = sentence
        self.word_list = word_list  # 记录树中所有的词，按照分词顺序
        self.dep_list = dep_list  # 记录树中所有的依存，按照分词顺序
        self.pos_list = pos_list  # 记录树中所有的词性，按照分词顺序
        self.leaf_nodes = []  # 记录树中所有的叶子节点

        # nodes_dict以字典来记录树中所有的节点，key为每个节点在word_list中的位置加1，0表示根节点，是一个虚拟节点
        self.nodes_dict = self._constructNodes(word_list, dep_list, pos_list)
        # tree_dict以字典来记录树，其中key与nodes_dict中的key相同，value为一个node id组成的list
        # 表示key节点的直接子节点；parents为一个dict，key为节点id，value为对应父节点id
        self.tree_dict, self.parents, self.HED_position = self._constructTree()

        # who_depend 记录哪些节点依存于当前节点，depend_who 记录当前节点依存哪个节点
        self.who_depend = {}
        for i in range(len(dep_list)):
            if dep_list[i][1] in self.who_depend.keys():
                self.who_depend[dep_list[i][1]].append(dep_list[i][0])
            else:
                self.who_depend[dep_list[i][1]] = [dep_list[i][0]]

        self.node_to_level_dict, self.level_to_node_dict = self._setLevels()
        self.full_tree_string, self.mask_tree_string = self.generate_tree_string(self.HED_position)


    def _constructNodes(self, word_list, dep_list, pos_list):
        di = {0: Node(0)}  # 以字典记录所有的点，其中key为点在原句中的位置，从1开始，如果
                 # dep_list中存在依存0节点，则建立一个0节点

        for i in range(len(word_list)):
            n = Node(dep_list[i][0], dep_list[i][2], pos_list[i], word_list[i])
            di[dep_list[i][0]] = n  # 以词在句子中的位置作为作为节点的编号，包括0节点
        return di

    def _constructTree(self):
        tree_dict = {}  # 以字典的形式表示树，key为父节点的id，
                 # value为list，存储key的所有直接子节点
        parents = {}  # parents记录每个点的父节点
        hed_position = -1
        for key in self.nodes_dict.keys():  # key = 0代表树根节点
            tree_dict[key] = []
            parents[key] = -1
        for s, e, d in self.dep_list:
            tree_dict[e].append(s)
            parents[s] = e
            if d == "HED":
                hed_position = s
        for key in tree_dict:
            if tree_dict[key]: # 直接儿子节点集非空
                tree_dict[key].sort()
            else:  # 直接儿子节点集为空，则是叶子节点
                self.leaf_nodes.append(key)
        return tree_dict, parents, hed_position

    def _setLevels(self):
        # 设置每个点的层次，设置每个层次有哪些点
        # Root 位于第 0 层
        node_to_level_dict = {}  # 每个点的层次
        level_to_node_dict = {}  # 每个层次有哪些点

        # 设置层次，标明每个层次排名第几的节点位于triple的什么位置
        current_level = 1
        node_to_level_dict = {}  # node作为key, level作为value
        level_to_node_dict = {}  # level作为key，node作为value
        flag = True
        nodes_in_current_level = [self.HED_position]
        while flag:
            _temp_next_nodes = []
            for node in nodes_in_current_level:
                node_to_level_dict[node] = current_level
                if current_level in level_to_node_dict.keys():
                    level_to_node_dict[current_level].append(node)
                else:
                    level_to_node_dict[current_level] = [node]
                if self.tree_dict[node]:
                    _temp_next_nodes.extend(self.tree_dict[node])
            nodes_in_current_level = _temp_next_nodes
            level_to_node_dict[current_level].sort()
            current_level += 1
            if not nodes_in_current_level:
                flag = False
        return node_to_level_dict, level_to_node_dict

    def generate_tree_string(self, node_id):
        s = self.nodes_dict[node_id].node_full_string
        s_mask = self.nodes_dict[node_id].node_mask_string
        if self.tree_dict[node_id]:  # 如果node_id包含子节点
            if len(self.tree_dict[node_id]) == 1:
                for id in self.tree_dict[node_id]:
                    _s, _s_mask = self.generate_tree_string(id)
                    s = s + "[" + _s + "]"
                    s_mask = s_mask + "!" + _s_mask + "#"
            else:
                s = s + "["
                s_mask = s_mask + "!"
                for id in self.tree_dict[node_id]:
                    _s, _s_mask = self.generate_tree_string(id)
                    s = s + "[" + _s + "]"
                    s_mask = s_mask + "!" + _s_mask + "#"
                s = s + "]"
                s_mask = s_mask + "#"
        return s, s_mask
