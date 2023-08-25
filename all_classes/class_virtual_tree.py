import numpy as np

class Virtual_Tree:
    """
    virtual tree主要作用是表示标注数据模板
    返回的树只包含core_nodes到common parent之间的路径
    返回的树中包含的点仅包括：core node到common parent之间路径的点
    virtual tree和具体的triple对应
    """
    def __init__(self, common_parent_id, core_nodes_id_list, real_tree, triple_in_num, vtID=None):
        self.common_parent_id = common_parent_id  # 这些id要从1开始
        self.core_nodes_id_list = core_nodes_id_list  # triple中的点才是core node
        self.real_tree = real_tree
        self.triple_in_num = triple_in_num  # 值从1开始
        self.vtID = vtID

        self.word_list, self.dep_list, self.pos_list, self.parent_dict, self.nodes_dict, self.virtual_tree_dict = \
                    self._construct_virtual_tree()  # 这里的点都是那些从core node到common parent之间（包括自己）所有的点
        self.node_to_level_dict, self.level_to_node_dict, self.mapping_triple = \
                            self.level_and_mapping()
        self.vt_schema = self.generate_vt_schema()
        self.geometry_string = self.generate_geometry_string()


    def _construct_virtual_tree(self):
        need_keep_nodes = self.get_nodes_needed_keep()  # 得到要保留的node，
        # 这些node指的是从triple node到common parent路径上的点
        vtNodesDict = {}
        for key in self.real_tree.nodes_dict.keys():  # 删除应该删除的node
            if key in need_keep_nodes and key != 0:
                vtNodesDict[key] = self.real_tree.nodes_dict[key]

        vtTreeDict = {}
        for key, value in self.real_tree.tree_dict.items():
            if key in need_keep_nodes and key != 0:
                temp_v = [i for i in value if i in need_keep_nodes]
                vtTreeDict[key] = temp_v

        vtWordList = [self.real_tree.word_list[i] for i in range(len(self.real_tree.word_list))
                                        if i+1 in need_keep_nodes]
        vtDepList = [self.real_tree.dep_list[i] for i in range(len(self.real_tree.dep_list))
                                        if i+1 in need_keep_nodes]
        parentDict = {}
        for s, e, dep in vtDepList:
            parentDict[s] = e
        vtPosList = [self.real_tree.pos_list[i] for i in range(len(self.real_tree.pos_list))
                                        if i+1 in need_keep_nodes]

        return vtWordList, vtDepList, vtPosList, parentDict, vtNodesDict, vtTreeDict

    def generate_geometry_string(self):
        # 每个vt都有唯一的一个表示其几何形状的字符串
        # 几何形状包括两个方面的内容：树形结构、依存关系
        # 最后的字符串包括：每个点由数字坐标和父节点坐标构成，然后按层遍历
        geometry_string_list = []  # 每个节点一个字符串，最后拼接起来就是总字符串
        for level in self.vt_schema.keys():
            if level == 1:
                if len(self.vt_schema[level]) == 1:
                    geometry_string_list.append("0-0-HHH-" + str(level) + "-0")  # 父节点坐标-依存-自己的坐标
                else:
                    print('vt_schema有错！')
            else:
                for index, item in enumerate(self.vt_schema[level]):
                    s = str(level-1) + "-" + str(item[1])  # 父节点位置
                    s = s + "-" + item[0][:3]  # 对父节点的依存
                    s =  s + "-" + str(level) + "-" + str(index)  # 自己的位置
                    geometry_string_list.append(s)
        s = "*".join(geometry_string_list)
        return s

    def get_nodes_needed_keep(self):
        need_keep = []  # 需要从real tree中保留的点，
        # 这些点指的是从core node到common parent路径上的点

        for node_id in self.core_nodes_id_list:  # 从每个core node往上进行遍历，直到common parent，
            # 路径上的点都需要keep
            currend_id = node_id
            flag = True
            while flag:
                need_keep.append(currend_id)
                if currend_id == self.common_parent_id:
                    break
                currend_id = self.real_tree.parents[currend_id]  # 沿着路径往上走
                if currend_id == self.common_parent_id:
                    need_keep.append(currend_id)
                    flag = False

        need_keep = list(set(need_keep))
        return need_keep

    def level_and_mapping(self):
        # 设置层次，标明每个层次排名第几的节点位于triple的什么位置
        current_level = 1
        node_to_level_dict = {}  # node作为key, level作为value
        level_to_node_dict = {}  # level作为key，node作为value
        flag = True
        nodes_in_current_level = [self.common_parent_id]
        while flag:
            _temp_next_nodes = []
            for node in nodes_in_current_level:
                node_to_level_dict[node] = current_level
                if current_level in level_to_node_dict.keys():
                    level_to_node_dict[current_level].append(node)
                else:
                    level_to_node_dict[current_level] = [node]
                if self.virtual_tree_dict[node]:
                    _temp_next_nodes.extend(self.virtual_tree_dict[node])
            nodes_in_current_level = _temp_next_nodes
            current_level += 1
            if not nodes_in_current_level:
                flag = False

        mapping_triple = {"arg1":[], "rel":[], "arg2":[]}  # 指示triple中每个部分是第几层第几个词
        # mapping_triple["arg1"] = [(1, 2), (2, 1)]意思是要抽取的triple的arg1由两个词组成：
        # 第一个是VT第一层的排名第二的词，第二个是VT中第二层排名第一的词
        # index = np.argsort(self.core_nodes_id_list)
        # rank = np.argsort(index)  # 抽取的词的排名
        # 接下来对每层进行遍历，排序，然后看core node排第几
        for level in level_to_node_dict.keys():
            level_to_node_dict[level].sort()
            index = np.argsort(level_to_node_dict[level])
            rank = np.argsort(index)
            for i in range(len(level_to_node_dict[level])):
                if level_to_node_dict[level][i] in self.triple_in_num[0]:
                    mapping_triple["arg1"].append((level, rank[i]))
                if level_to_node_dict[level][i] in self.triple_in_num[1]:
                    mapping_triple["rel"].append((level, rank[i]))
                if level_to_node_dict[level][i] in self.triple_in_num[2]:
                    mapping_triple["arg2"].append((level, rank[i]))

        return node_to_level_dict, level_to_node_dict, mapping_triple

    def generate_vt_schema(self):
        # vt schema结构与vt类似，主要作用是指示哪个点该填充什么样的点、其下一代应该如何
        # vt schema: {1: [('.{3}  v%%%', -1, [0, 1])], 2: [('SBV nh%%%', 0, []), ('VOB ns%%%', 0, [])]}
        # 说明VT有两层，第一层的list里面有一个tuple，每个tuple代表一个node，第二层的list有两个tuple，即两个node
        # tuple中第二个值表示父节点是上一层第几个点，第三个值表示子节点是下一层中哪些点
        VT_schema = {}  # 以VT中level为key，以list为value，list中的值为相应点的node mask string
        for level in self.level_to_node_dict.keys():
            if level == 1:
                _nID = self.level_to_node_dict[level][0]
                node_string = self.nodes_dict[_nID].node_level1_string
                parent_position = -1
                child_position_list = list(range(len(self.level_to_node_dict[2])))
                VT_schema[level] = [(node_string, parent_position, child_position_list)]
            else:
                VT_schema[level] = []
                for node_id in self.level_to_node_dict[level]:
                    node_string = self.nodes_dict[node_id].node_mask_string
                    parent_position = self.level_to_node_dict[level - 1].index(self.parent_dict[node_id])

                    child_position_list = []
                    if level + 1 in self.level_to_node_dict.keys():
                        for i in range(len(self.level_to_node_dict[level + 1])):
                            if self.parent_dict[self.level_to_node_dict[level + 1][i]] == node_id:
                                child_position_list.append(i)
                    VT_schema[level].append((node_string, parent_position, child_position_list))
        return VT_schema





