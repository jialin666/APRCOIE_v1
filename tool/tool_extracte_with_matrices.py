from ..all_classes.class_tree import Tree
from typing import List
from ..all_classes.class_virtual_tree import Virtual_Tree
from ..tool.tool_generateTriples_givenTemplate import generate_triples_given_vt
from ..all_classes.class_template import Template
from time import perf_counter
import numpy as np
import V_I.tool.tool_postProcessing as TPP

# 以词性作为行和列，边为依存，产生矩阵
index_to_pos_tag = {
    0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"g", 6:"h",
    7:"i", 8:"j", 9:"k", 10:"m", 11:"n", 12:"nd", 13:"nh",
    14:"ni", 15:"nl", 16:"ns", 17:"nt", 18:"nz",
    19:"o", 20:"p", 21:"q", 22:"r", 23:"u", 24:"v",25:"wp",26:"ws",
    27:"x",28:"z"
}
pos_tag_to_index = {
    "a":0, "b":1, "c":2, "d":3, "e":4, "g":5, "h":6,
    "i":7, "j":8, "k":9, "m":10, "n":11, "nd":12, "nh":13,
    "ni":14, "nl":15, "ns":16, "nt":17, "nz":18,
    "o":19, "p":20, "q":21, "r":22, "u":23, "v":24, "wp":25, "ws":26,
    "x":27, "z":28
}
index_to_dep_tag = {
    0.001:"SBV", 0.007:"VOB", 0.049:"IOB", 0.343:"FOB", 2.401:"DBL", 16.807:"ATT", 117.649:"ADV",
    823:"CMP", 5764:"COO", 40353:"POB", 282475:"LAD", 1977326:"RAD", 13841287:"IS", 96889010:"HED",
    678223072:"WP"
}
dep_tag_to_index = {
    "SBV": 0.001, "VOB": 0.007, "IOB":0.049, "FOB": 0.343, "DBL": 2.401, "ATT": 16.807,
    "ADV": 117.649,
    "CMP": 823, "COO": 5764, "POB": 40353, "LAD": 282475, "RAD": 1977326, "IS": 13841287,
    "HED": 96889010, "WP":678223072
}

# 为待抽取的句子建立矩阵
# 矩阵大小等于词性类型数量，矩阵中的值表示两个词之间的依存值，如果一棵树中出现同种情况，则叠加值
def building_matrix_Tree(post_list, dep_list):
    # 给定词性和依存，就可以建立依存矩阵
    mat = np.zeros((len(pos_tag_to_index), len(pos_tag_to_index)))
    for i in range(len(post_list)):
        x_axis = pos_tag_to_index[post_list[dep_list[i][0]-1]]
        y_axis = pos_tag_to_index[post_list[dep_list[i][1]-1]]
        z_axis = dep_tag_to_index[dep_list[i][2]]
        mat[x_axis, y_axis] += z_axis
    return mat

# 为模板建立矩阵
def building_matrix_VTree(post_list, dep_list):
    # 这里的post_list和dep_list都是VT中的list，而不是完整的list
    # [[5, 6, 'SBV'], [6, 0, 'HED'], [7, 8, 'ATT'], [8, 6, 'VOB']]
    # ['nh', 'v', 'nz', 'n']
    noID_needToConsider = [s for s, e, d in dep_list]
    fake_index_to_real_index = {}
    for i in range(len(dep_list)):
        fake_index_to_real_index[dep_list[i][0]] = i

    mat = np.zeros((len(pos_tag_to_index), len(pos_tag_to_index)))
    for i in range(len(post_list)):
        if dep_list[i][1] not in noID_needToConsider:
            continue
        x_axis = pos_tag_to_index[post_list[i]]
        y_axis = pos_tag_to_index[post_list[fake_index_to_real_index[dep_list[i][1]]]]
        z_axis = dep_tag_to_index[dep_list[i][2]]
        mat[x_axis, y_axis] += z_axis
    return mat

def Result_Analysis(TMatrix, VTMatrix_list):
    # total_result的shape为 len_vtmatrix_list * 29 * 29
    # Tree matrix 减去VT matrix，
    # if 结果矩阵中出现负值
    #    则存在VT中存在但Tree中不存在的边，这个VT去掉
    # else：
    #    检查结果矩阵中值发生改变的位置：
    #      if 值发生改变的位置值不为0：
    #          如果此时为负值，则去掉这个VT
    #          如果剩下的值不能组合为dep index的加，则去掉这个VT
    #
    # 第一次筛选
    vt_matrixs = np.array(VTMatrix_list)
    # 先将TMatrix在第三维上复制 len(VTMatrix_list) 次，
    # 然后利用numpy的性质同时执行Tree matrix与每个vt matrix的减法
    total_result = [TMatrix] * len(VTMatrix_list) - vt_matrixs
    # 如果Tree matrix与 vt matrix相减的结果中，如果存在负值，则表示这个vt中存在Tree中没有的边，因此过滤掉这个vt
    filted_vt_index = []  # 存储保留的vt tree index
    for i in range(len(VTMatrix_list)):
        if np.sum(total_result[i] < 0) == 0:  # 看看有多少小于0的元素，只有小于零0的元素数量等于0的vt才保留
            filted_vt_index.append(i)

    # # 第二次筛选
    # # 我们假设两个点之间最大只有两个边，因此结果矩阵中vt不为0的位置上的值必须是dep的值
    # filted_matrix_index_1 = []
    # refer = np.array(list(index_to_dep_tag.keys()) + [0])
    # for index in filted_matrix_index:  # 对于第一次过滤剩下的VT，进行进一步过滤
    #     # 把VT那些不为0的值的坐标取出来，然后把total_result中相应位置的值取出来
    #     temp_result = total_result[index][VTMatrix_list[index] != 0]  # 此时temp_result是一个一维的向量
    #     # 如果这些位置的值仍然保持是dep的那些取值，则说明前面的减法是正常的
    #     if np.sum(np.isin(temp_result, refer, invert=True)) == 0:
    #         filted_matrix_index_1.append(index)
    # print(len(filted_matrix_index_1))
    return filted_vt_index

def base_extraction(tree: Tree, vt_list:List[Virtual_Tree]):
    # baseExtraction利用矩阵的方法进行抽取，并不判断是否是POB等类型的vt
    # 抽取结果进行了拉平处理
    start_time = perf_counter()
    tree_matrix = building_matrix_Tree(tree.pos_list, tree.dep_list)
    # 产生所有的模板矩阵
    vt_matrix_list = []
    for vt in vt_list:
        vt_matrix = building_matrix_VTree(vt.pos_list, vt.dep_list)
        vt_matrix_list.append(vt_matrix)

    start_time = perf_counter()
    # 通过矩阵运算去掉不符合模板
    filted_vt_index = Result_Analysis(tree_matrix, vt_matrix_list)
    # 这个filted_vt_index还不一定是具有抽取结果的vt
    end_time = perf_counter()
    t1 = end_time - start_time
    # print("base_extraction中矩阵运算执行时间为：", t1)
    # 这里的vt_list里面的vt并不一定就能产生triple，因为filted vt没有考虑词之间的顺序
    vt_list = [vt_list[index] for index in filted_vt_index]

    # 接下来产生真正的triple，并得到起作用的vt，并得到triple in number
    final_shot_vt = []
    final_triple_in_char = []  # 记录总的triples
    final_triple_in_number = []  # 这三个final长度一致
    for vt in vt_list:
        triples_in_char, triples_in_number = generate_triples_given_vt(tree, vt)
        if triples_in_char:
            for i, triple in enumerate(triples_in_number):  # 可能存在一个vt在一个tree中得到多个triple，
                # 所以进行了拉平处理
                final_shot_vt.append(vt)
                final_triple_in_char.append(triples_in_char[i])
                final_triple_in_number.append(triple)

    end_time = perf_counter()
    t2 = end_time - start_time
    # print("base_extraction总花费时间为：", t2)

    if len(final_shot_vt) > 0:
        return final_shot_vt, final_triple_in_number, final_triple_in_char  # 返回的triple in number
        # 从0开始
    else:
        return None, None, None

def sub_triple(triple_in_numberA, triple_in_numberB):
    for i in range(3):
        triple_in_numberA[i] = list(set(triple_in_numberA[i]))
        triple_in_numberA[i].sort()
        triple_in_numberB[i] = list(set(triple_in_numberB[i]))
        triple_in_numberB[i].sort()
    # 如果triple A是triple B的子triple，即A的arg1, rel, arg2均是B 的arg1, rel, arg2的子集，则返回True，
    # 否则False
    intersect_a_b_arg1 = [ind for ind in triple_in_numberA[0] if ind in triple_in_numberB[0]]
    intersect_a_b_arg1 = list(set(intersect_a_b_arg1))
    intersect_a_b_arg1.sort()
    if intersect_a_b_arg1 != triple_in_numberA[0]:
        return False
    intersect_a_b_rel = [ind for ind in triple_in_numberA[1] if ind in triple_in_numberB[1]]
    intersect_a_b_rel = list(set(intersect_a_b_rel))
    intersect_a_b_rel.sort()
    if intersect_a_b_rel != triple_in_numberA[1]:
        return False
    intersect_a_b_arg2 = [ind for ind in triple_in_numberA[2] if ind in triple_in_numberB[2]]
    intersect_a_b_arg2 = list(set(intersect_a_b_arg2))
    intersect_a_b_arg2.sort()
    if intersect_a_b_arg2 != triple_in_numberA[2]:
        return False
    return True

def att_extraction(tree: Tree, att_vt_list: List[Virtual_Tree]):
    # 利用att模板进行抽取，对结果进行组织，给出最终结果
    # 1. 利用矩阵方法进行基础抽取，找出基础结果，最终结果是在对基础结果进行组织的而来
    final_shot_vt, final_triple_in_number, final_triple_in_char = \
                                                            base_extraction(tree, att_vt_list)
    if not final_triple_in_number:
        return None, None, None
    # 2. 存在抽取结果，则进行子triple处理，即子triple不返回
    # 2.1 找出每个triple所包含的点，放在一个list中，这些list构成all_node_index_of_triple
    all_node_index_of_triple = []  # [[1, 2, 3], [6, 8, 9]], 其中[1, 2, 3]是某个triple所涉及的
    # 所有点的index
    for i, triple in enumerate(final_triple_in_number):  # base_extraction对结果已经进行了拉平处理
        temp = [ind for ii in range(3) for ind in triple[ii]]
        temp.sort()
        all_node_index_of_triple.append(temp)
    # 2.2 对final_shot_vt和final_triple_in_number按照all_node_index从长到短进行排序
    node_amount_sorted_index = [i[0] for i in sorted(enumerate([len(item)
                                        for item in all_node_index_of_triple]),
                                             key=lambda x:x[1], reverse=True)]
    # 最长的那个triple是final_triple_in_number[node_amount_sort[0]]
    # 2.3 按照node_amount_sorted_index中的顺序对抽取结果进行重排
    final_shot_vt = [final_shot_vt[node_amount_sorted_index[i]]
                     for i in range(len(node_amount_sorted_index))]
    final_triple_in_number = [final_triple_in_number[node_amount_sorted_index[i]]
                                for i in range(len(node_amount_sorted_index))]
    used_index = []
    sub_pair_dict = {}  # 记录哪些triple对构成子结构
    for i in range(len(final_triple_in_number)-1):
        if i in used_index:
            continue
        for j in range(i+1, len(final_triple_in_number)):
            if j in used_index:
                continue
            if sub_triple(final_triple_in_number[j], final_triple_in_number[i]):
                if i not in sub_pair_dict.keys():
                    sub_pair_dict[i] = [i, j]
                    used_index.extend([i, j])
                else:
                    sub_pair_dict[i].append(j)
                    used_index.append(j)
    final_index = list(sub_pair_dict.keys())
    temp = [ind for ind in range(len(final_triple_in_number)) if ind not in used_index]
    final_index.extend(temp)
    final_shot_vt = [final_shot_vt[ind] for ind in final_index]
    final_triple_in_number = [final_triple_in_number[ind] for ind in final_index]
    final_triple_in_char = []
    for triple in final_triple_in_number:
        arg1 = [tree.word_list[index] for index in triple[0]]
        rel = [tree.word_list[index] for index in triple[1]]
        arg2 = [tree.word_list[index] for index in triple[2]]
        final_triple_in_char.append([arg1, rel, arg2])

    return final_shot_vt, final_triple_in_number, final_triple_in_char

def svo_extraction(tree: Tree, svo_vt_list: List[Virtual_Tree]):
    # 1. 利用矩阵方法进行抽取
    final_shot_vt, final_triple_in_number, final_triple_in_char = base_extraction(tree, svo_vt_list)
    if not final_triple_in_number:
        return None, None, None
    # 2. 判断抽取结果是否是svo，这是因为可能有多个svo triple，这种情况不算Svo
    svo_index = []
    for i, triple in enumerate(final_triple_in_number):
        svo_triple = TPP.isSVO(tree, triple)
        if svo_triple:
            svo_index.append(i)
    final_shot_vt = [final_shot_vt[ind] for ind in svo_index]
    final_triple_in_number = [final_triple_in_number[ind] for ind in svo_index]
    final_triple_in_char = [final_triple_in_char[ind] for ind in svo_index]

    # 2. 有抽取结果，则抽取svo triple，然后对svo triple进行补全，然后返回结果
    used_index = []
    index_2_svoTriple = {}
    same_svo_dict = {}  # 记录哪些triple具有相同的svo


    if len(final_triple_in_number) == 1:
        svo_triple = TPP.isSVO(tree, final_triple_in_number[0])
        final_triple_in_number = [TPP.find_semantic_parts_general_version(tree, svo_triple)]
        final_triple_in_char = []
        for triple in final_triple_in_number:
            arg1_char = [tree.word_list[ind] for ind in triple[0]]
            rel_char = [tree.word_list[ind] for ind in triple[1]]
            arg2_char = [tree.word_list[ind] for ind in triple[2]]
            final_triple_in_char.append([arg1_char, rel_char, arg2_char])
        return final_shot_vt, final_triple_in_number, final_triple_in_char

    for i in range(len(final_triple_in_number) - 1):
        if i in used_index:
            continue
        svo_triple_i = TPP.isSVO(tree, final_triple_in_number[i])
        if not svo_triple_i:
            continue
        if i not in index_2_svoTriple.keys():
            index_2_svoTriple[i] = svo_triple_i
        svo_triple_i_string = "-".join([str(ind[0]) for ind in svo_triple_i])
        for j in range(i + 1, len(final_triple_in_number)):
            if j in used_index:
                continue
            svo_triple_j = TPP.isSVO(tree, final_triple_in_number[j])
            if not svo_triple_j:
                continue
            if j not in index_2_svoTriple:
                index_2_svoTriple[j] = svo_triple_j
            svo_triple_j_string = "-".join([str(ind[0]) for ind in svo_triple_j])
            if svo_triple_i_string == svo_triple_j_string:
                if i not in same_svo_dict.keys():
                    same_svo_dict[i] = [i, j]
                    used_index.extend([i, j])
                else:
                    same_svo_dict[i].append(j)
                    used_index.append(j)
    final_index = list(same_svo_dict.keys())
    temp = [ind for ind in range(len(final_triple_in_number)) if ind not in used_index]
    final_index.extend(temp)
    final_shot_vt = [final_shot_vt[ind] for ind in final_index]
    final_triple_in_number = [TPP.find_semantic_parts_general_version(tree, index_2_svoTriple[ind])
                                        for ind in final_index]
    final_triple_in_char = []
    for triple in final_triple_in_number:
        arg1_char = [tree.word_list[ind] for ind in triple[0]]
        rel_char = [tree.word_list[ind] for ind in triple[1]]
        arg2_char = [tree.word_list[ind] for ind in triple[2]]
        final_triple_in_char.append([arg1_char, rel_char, arg2_char])
    return final_shot_vt, final_triple_in_number, final_triple_in_char

def svo_coo_extraction(tree: Tree, svo_coo_vt_list: List[Virtual_Tree]):
    _final_shot_vt, _final_triple_in_number, _final_triple_in_char = \
                                        base_extraction(tree, svo_coo_vt_list)
    if not _final_triple_in_number:
        return None, None, None
    final_shot_vt = []
    final_triple_in_number = []
    final_triple_in_char = []

    # 先得到每一个triple的svo coo triple
    shot_vt_list = []
    svocoo_triple_list = []
    for i, triple in enumerate(_final_triple_in_number):
        svo_coo_base, svo_coo_full, svo_coo_triples = TPP.isSVOCOO(tree, triple)
        if not svo_coo_full:
            return None, None, None
        for svocoo_triple in svo_coo_triples:
            shot_vt_list.append(_final_shot_vt[i])
            svocoo_triple_list.append(svocoo_triple)

    final_shot_vt_list = []
    final_svocoo_triple_list = []
    # 如果只有一个svo coo triple，那就直接补全返回结果
    if len(svocoo_triple_list) == 1:
        final_shot_vt_list.append(shot_vt_list[0])
        final_svocoo_triple_list = svocoo_triple_list
    else:
        # 有多个svo coo triple，这时候就需要排除重复值了
        used_triple_string = []
        for i in range(len(shot_vt_list)):
            triple_string = "-".join([str(ind) for ii in range(2)
                                        for ind in svocoo_triple_list[i][ii]])
            if triple_string not in used_triple_string:
                final_shot_vt_list.append(shot_vt_list[i])
                final_svocoo_triple_list.append(svocoo_triple_list[i])

    final_triple_in_number = []
    final_triple_in_char = []
    # 接下来对svo coo triple进行补全
    for svo_coo_triple in final_svocoo_triple_list:
        if len(svo_coo_triple[1]) == 1:
            final_triple_in_number.append(TPP.find_semantic_parts_general_version(tree, svo_coo_triple))
        else:
            tempTriple = TPP.find_semantic_parts_general_version(tree, [svo_coo_triple[0],
                                                                        svo_coo_triple[1][0],
                                                                        svo_coo_triple[2]])
            rel = tempTriple[1]
            for ii in range(1, len(svo_coo_triple[1])):
                rel.extend(TPP.findSemanticParts4Rel_SVO(tree, [svo_coo_triple[0],
                                                                svo_coo_triple[1][ii],
                                                                svo_coo_triple[2]]))
            final_triple_in_number.append([tempTriple[0], rel, tempTriple[2]])
        for i in range(len(final_triple_in_number)):
            final_shot_vt.append(_final_shot_vt[0])
            arg1 = [tree.word_list[ind] for ind in final_triple_in_number[i][0]]
            rel = [tree.word_list[ind] for ind in final_triple_in_number[i][1]]
            arg2 = [tree.word_list[ind] for ind in final_triple_in_number[i][2]]
            final_triple_in_char.append([arg1, rel, arg2])
        return final_shot_vt_list, final_triple_in_number, final_triple_in_char


def no_no_extraction(tree: Tree, vt_list: List[Virtual_Tree]):
    return

def extraction_regular(tree:Tree, vt_list_svo:List[Virtual_Tree],
                                    vt_list_svocoo:List[Virtual_Tree],
                                        vt_list_att:List[Virtual_Tree]):

    _, _, final_triple_in_char_svo = svo_extraction(tree, vt_list_svo)
    _, _, final_triple_in_char_svocoo = svo_coo_extraction(tree, vt_list_svocoo)
    _, _, final_triple_in_char_att =att_extraction(tree, vt_list_att)
    result = []
    if final_triple_in_char_svo:
        result.extend(final_triple_in_char_svo)
    if final_triple_in_char_svocoo:
        result.extend(final_triple_in_char_svocoo)
    if final_triple_in_char_att:
        result.extend(final_triple_in_char_att)
    return result









