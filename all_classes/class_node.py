class Node:
    """
    node表示依存树种的一个节点，记录内容包括：
    dep：其对父节点的依存符号
    pos：词性
    position：词在原句中的位置，从1开始
    word: 词本身
    node_string: 该节点构成的字符串
    node_string_schema: 该节点构成的字符串中的word用掩码代替后的字符串
    """
    def __init__(self, position, dep=None, pos=None, word=None):
        self.id = position  # 从0开始，0是根节点，1是真正的节点
        self.position = position  # 如果值为 0 则表示是根节点
        if position != 0:
            self.dep = dep
            self.pos = pos
            self.word = word
        else:
            self.dep = None
            self.pos = None
            self.word = None
        self.node_full_string, self.node_mask_string, self.node_template_string, self.node_level1_string = \
            self.construct_nodeStr(dep, pos, position, word)

    def construct_nodeStr(self, dep, pos, position, word):
        # 如果是在处理标注数据，则主要是为了产生模板，因而需要加（），否则不需要加
        if position == 0:  # 如果是Root节点，则返回长度为0字符串
            return "", "", "", ""
        # if len(str(position)) == 2:
        #     node_full_string = str(position)  # result是完整的节点字符串，包括依存、词性、词
        #     node_mask_string = str(position)
        # else:
        #     node_full_string = " " + str(position)
        #     node_mask_string = " " + str(position)
        if len(dep) == 3:
            node_full_string = dep  #node_full_string + dep
            node_mask_string = dep  #node_mask_string +
        else:
            node_full_string = " " + dep  # node_full_string +
            node_mask_string = " " + dep  # node_mask_string +
        if len(pos) == 1:
            node_full_string = node_full_string + "  " + pos
            node_mask_string = node_mask_string + "  " + pos
        elif len(pos) == 2:
            node_full_string = node_full_string + " " + pos
            node_mask_string = node_mask_string + " " + pos
        elif len(pos) == 3:
            node_full_string = node_full_string + pos
            node_mask_string = node_mask_string + pos
        node_full_string += word
        node_mask_string += "%%%"
        node_template_string = node_mask_string
        node_template_string = "(" + node_template_string + ")"
        node_level1_string = ".{3}" + node_mask_string[3:]

        return node_full_string, node_mask_string, node_template_string, node_level1_string
