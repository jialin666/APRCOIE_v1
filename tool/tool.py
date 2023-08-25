import numpy as np
import xlrd

def is_Chinese(w):
    # 判断当前字符是否是中文
    if w > u'\u4e00' and w < u'\u9fff':
        return True
    else:
        return False

def string_is_Chinese(s):
    for c in s:
        if not is_Chinese(c):
            return False
    return True


# 注意： 给定的triple计数要从1开始
def get_Core_and_AdditionNodes(tree, triple):  # 要求triple是（）形式的三元组
    # core node指 triple 中出现的 node
    # addtional node 指与 core node 有依存关系的 node
    core_nodes = [i for l in triple for i in l if str(i).isdigit()]  # triple中的点才是core node
    return core_nodes #, additional_nodes

def getCommonParent(tree, core_nodes):
    # 返回所有core node的共同父节点， node的下标0表示HED，因此实际node从1开始

    if tree.HED_position in core_nodes:
        # 如果HED node在core node中，则其即为共同父节点
        return tree.HED_position
    # 下面的情况处理 HED不在 core node中
    path2Hed = {}  # 记录每个core node到hed之间经过的所有的点，包括首尾
    for no in core_nodes:  # 所有的core node都是HED的子节点
        current_node = no
        path2Hed[no] = []
        flag = True
        while flag:
            path2Hed[no].append(current_node)
            current_node = tree.parents[current_node]
            if current_node == 0:
                flag = False

    result = list(set(path2Hed[core_nodes[0]]).intersection(*path2Hed.values()))
    if len(result) == 1:
        return result[0]
    else:  # 找出层次最高的点返回
        levels =[tree.node_to_level_dict[re] for re in result]
        index_max = np.argmax(levels)
        return result[index_max]

def get_wl_dl_pl(sentence, ltp_tool):
    segment, hidden = ltp_tool.seg([sentence])
    pos = ltp_tool.pos(hidden)
    ner = ltp_tool.ner(hidden)
    dep = ltp_tool.dep(hidden)
    word_list = segment[0]
    pos_list = pos[0]
    ner_list = ner[0]
    dep_list = dep[0]
    return word_list, dep_list, pos_list

def get_w_p_d_with_ltplist(sentence, ltp_list):
    global hidden, segment
    for ltp_tool in ltp_list:
        while True:
            try:
                segment, hidden = ltp_tool.seg([sentence])
            except Exception:
                continue
            else:
                break
        pos = ltp_tool.pos(hidden)
        ner = ltp_tool.ner(hidden)
        dep = ltp_tool.dep(hidden)
        word_list = segment[0]
        pos_list = pos[0]
        ner_list = ner[0]
        dep_list = dep[0]
        result = _check_ltpResult(dep_list)
        if result:
            return word_list, pos_list, dep_list
    return None, None, None

def _check_ltpResult(dep_list)->bool:
    # 检查dep_list是否有问题，没有问题返回True，有问题返回False
    # 问题包括：有环，无HED，多个HED,不在一棵树上
    # 检查有无HED或者多个HED
    dep_mark_list = [m for s, e, m in dep_list]
    if dep_mark_list.count('HED') != 1:
        # print('多个HED或者没有HED')
        return False
    # 检查是否有环
    for i in range(len(dep_list)-1):
        for j in range(i+1, len(dep_list)):
            if dep_list[i][0] == dep_list[j][1] and dep_list[i][1] == dep_list[j][0]:
                # print('有环')
                return False
    # 检查是否在一棵树上
    all_elements = []
    for s, e, mark in dep_list:
        index_list = []
        for i in range(len(all_elements)):
            if s in all_elements[i] or e in all_elements[i]:
                all_elements[i].extend([s, e])
                index_list.append(i)
        if len(index_list) == 0:
            all_elements.append([s, e])
        else:
            _temp = []
            for index in index_list:
                _temp.extend(all_elements[index])
            _all_elements = [all_elements[index] for index in range(len(all_elements)) if index not in index_list]
            all_elements = _all_elements
            all_elements.append(_temp)
    if len(all_elements) > 1:
        # print('多个树')
        return False
    # print('没有问题')
    return True

def read_excel(path='.\\data\\note_mission.xls'):
    data = xlrd.open_workbook(path)

    fr_book = data.sheet_by_name('FengRui')
    yyh_book = data.sheet_by_name('YanYuhui')

    sen_list = []
    triples_in_num_list = []

    # 原句列表
    fr_sen_list = []
    # 数字关系三元组
    fr_triples_annotated = []

    for rowx in range(1, 62):
        # print('rowx:',rowx)
        note_data = fr_book.row_values(rowx, start_colx=0, end_colx=None)
        # print(note_data)
        fr_sen_list.append(note_data[0])
        # 对标注关系进行整合
        entity1s = str(note_data[2]).split('/')
        relation_phrases = str(note_data[3]).split('/')
        entity2s = str(note_data[4]).split('/')

        relation_triple_list = []
        for i in range(len(entity1s)):
            relation_triple = []
            relation_triple.append(entity1s[i].split(','))
            relation_triple.append(relation_phrases[i].split(','))
            relation_triple.append(entity2s[i].split(','))

            relation_triple_list.append(relation_triple)

        fr_triples_annotated.append(relation_triple_list)

    # 原句列表
    yyh_sen_list = []
    # 数字关系三元组
    yyh_triples_annotated = []

    for rowx in range(1, 61):
        print('rowx:', rowx)
        note_data = yyh_book.row_values(rowx, start_colx=0, end_colx=None)
        # print(note_data)

        yyh_sen_list.append(note_data[0])
        # 对标注关系进行整合
        entity1s = note_data[2].split('/')
        relation_phrases = note_data[3].split('/')
        entity2s = note_data[4].split('/')

        relation_triple_list = []
        for i in range(len(entity1s)):
            relation_triple = []
            relation_triple.append(entity1s[i].split(','))
            relation_triple.append(relation_phrases[i].split(','))
            relation_triple.append(entity2s[i].split(','))

            relation_triple_list.append(relation_triple)

        yyh_triples_annotated.append(relation_triple_list)

    sen_list.extend(fr_sen_list)
    sen_list.extend(yyh_sen_list)

    triples_in_num_list.extend(fr_triples_annotated)
    triples_in_num_list.extend(yyh_triples_annotated)
    return sen_list, triples_in_num_list





