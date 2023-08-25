from .class_virtual_tree import Virtual_Tree

class Template:
    # template是VT中的两个属性
    # # vt schema: {1: [('.{3}  v%%%', -1, [0, 1])], 2: [('SBV nh%%%', 0, []), ('VOB ns%%%', 0, [])]}
    # 说明VT有两层，第一层的list里面有一个tuple，即一个node，第二次的list有两个tuple，即两个node
    # tuple中第二个值表示父节点是上一层第几个点，第三个值表示子节点是下一层中哪些点
    # mapping_triple = {"arg1": [], "rel": [], "arg2": []}  # 指示triple中每个部分是第几次第几个词
    # mapping_triple["arg1"] = [(1, 2], (2, 1)]意思是要抽取的triple的arg1由两个词组成：
    # 第一个是VT第一层的排名第二的词，第二个是VT中第二层排名第一的词
    def __init__(self, vt: Virtual_Tree):
        self.vt_schema = vt.vt_schema
        self.mapping_triple = vt.mapping_triple
        self.num_of_level = len(vt.vt_schema)
        self.pos_feature = list(set(vt.pos_list))
        self.dep_feature = list(set([item[2] for item in vt.dep_list]))