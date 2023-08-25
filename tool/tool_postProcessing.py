from typing import List

import V_I.tool.tool_extracte_with_matrices as MATRIX
from ..all_classes.class_tree import Tree
from  ..all_classes.class_virtual_tree import Virtual_Tree
import V_I.tool.tool as TOOL
import pandas as pd

MAXIMUMARGLENGTH = 7  # arg 最大词的长度，在有多个分支时，如果长度超过该值，则省略前面分支的内容

def isATT(tree: Tree, triple_in_number: List, isvt=False, vt:Virtual_Tree=None):  # triple_in_number从0开始
    # 对dep list进行遍历，
    # 1. 如果triple中的点之间只有ATT，就可以认定为ATT,
    # 2. 如果arg2是地名或者人名，除了ATT，可以包含vob
    # 3. arg1内部可以出现任何形式，但是与rel之间、rel与arg2直接，arg1与arg2之间只能是ATT
    # triple的common point必须是triple中的点
    all_nodes = [ind for i in range(3) for ind in triple_in_number[i]]
    core_nodes = [ind+1 for ind in all_nodes]
    common_nodex = TOOL.getCommonParent(tree, core_nodes)
    if common_nodex-1 not in triple_in_number[0] and common_nodex-1 not in triple_in_number[2]:
        return False
    if isvt:
        dep_list = vt.real_tree.dep_list
        pos_list = vt.real_tree.pos_list
    else:
        dep_list = tree.dep_list
        pos_list = tree.pos_list

    all_dep_is_att = True
    arg2_is_NE = False
    arg1_2_rel_is_att = True
    rel_2_arg2_is_att = True
    ar1_2_rel_2_arg2 = True  # 必须保证所有关系都是从arg1指向rel指向arg2
    # if tree.sentenceID == 5:
    #     print('yes')
    for son, par, dep in dep_list:

        if son-1 in all_nodes and par-1 in all_nodes:  #
            if son-1 in triple_in_number[1] or son-1 in triple_in_number[2]:
                if par-1 in triple_in_number[0]:
                    ar1_2_rel_2_arg2 =False
                    return False
            if son-1 in triple_in_number[2] and par-1 in triple_in_number[1]:
                ar1_2_rel_2_arg2 = False
                return False
            if dep != 'ATT':
                all_dep_is_att = False
            if son-1 in triple_in_number[2] and pos_list[son-1] in ['nh', 'ni', 'ns', 'nz']:
                arg2_is_NE = True
            if par-1 in triple_in_number[2] and pos_list[par-1] in ['nh', 'ni', 'ns', 'nz']:
                arg2_is_NE = True
            if son-1 in triple_in_number[0] and par-1 in triple_in_number[1]:
                if dep != 'ATT':
                    arg1_2_rel_is_att = False
            if son-1 in triple_in_number[1] and par-1 in triple_in_number[2]:
                if dep != 'ATT':
                    rel_2_arg2_is_att = False
    if all_dep_is_att:
        return True
    if arg1_2_rel_is_att and rel_2_arg2_is_att and arg2_is_NE:
        return True
    return False

def organize_att_triples(triples_in_number):
    # 得到att抽取的结果，然后进行组织，即最长的triple最为最终的结果
    return

def isSVOCOO(tree: Tree, triple_in_number: List, isvt=False, vt: Virtual_Tree=None):
    # 返回的svo coo triple中，rel可能长度为1， arg1和arg2长度都为1
    svo_coo_triples = []
    if isvt:
        svo_coo_base, svo_coo_full, svo_coo_triple = _isSVOCOO(tree, triple_in_number, isvt, vt)
    else:
        svo_coo_base, svo_coo_full, svo_coo_triple = _isSVOCOO(tree, triple_in_number)
    if svo_coo_full:
        for a1 in svo_coo_triple[0]:
            rel = svo_coo_triple[1]
            for a2 in svo_coo_triple[2]:
                svo_coo_triples.append([[a1], rel, [a2]])
    return svo_coo_base, svo_coo_full, svo_coo_triples

def _isSVOCOO(tree: Tree, triple_in_number: List, isvt=False, vt: Virtual_Tree=None):
    # 判断是否是SVO-COO情况，或者判断一个vt是否是SVO-COO
    # SVO-COO的特征是：arg1在SVB中，但是SBV对应的谓语不在rel中，rel在谓语的coo中，或者coo的vob，或者coo的vob的vob
    # SBV的谓语必须有vob或者cmp，如果没有，则另外处理
    # 另外还要保证除了arg1中中有sbv外，rel不能再有sbv
    # triple_in_number从0开始计数
    svo_coo_base = False  # 是否具有基本的svo coo结构
    svo_coo_full = False  # 是否是确凿的svo coo结构
    points_in_triple_ = [ind for i in range(3) for ind in triple_in_number[i]]  # 从 0 开始
    svo_coo_triple = []
    global common_point  # 从0开始
    if isvt:  # 如果是需要判断vt是否是svo-coo结构，那么可以直接调用common point
        common_point = vt.common_parent_id -1  # vt.common_parent_id是从1开始的
    else:
        core_nodes = [ind +1 for i in range(3) for ind in triple_in_number[i]]
        common_point = TOOL.getCommonParent(tree, core_nodes)
        common_point = common_point - 1
    # 首先找到基本的SVO结构，即common_point有SBV和VOB/CMP
    sbv_of_commonPoint = [ind-1 for ind, par, dep in tree.dep_list if par-1 == common_point
                           and dep == "SBV"]  #
    vob_of_commonPoint = [ind-1 for ind, par, dep in tree.dep_list if par-1 == common_point
                           and dep == "VOB"]
    cmp_of_commonPoint = [ind - 1 for ind, par, dep in tree.dep_list if par - 1 == common_point
                           and dep == "CMP"]
    coo_of_commonPoint = [ind - 1 for ind, par, dep in tree.dep_list if par - 1 == common_point
                           and dep == "COO"]
    coo_of_sbv_of_commonPoint = [ind - 1 for ind, par, dep in tree.dep_list if par - 1 in sbv_of_commonPoint
                  and dep == "COO"]
    if not sbv_of_commonPoint:  # 如果没有sbv，则不构成sbv-coo
        return svo_coo_base, svo_coo_full, svo_coo_triple
    if not vob_of_commonPoint and not cmp_of_commonPoint:  # 如果vob和cmp同时没有，则不构成sbv-coo
        return svo_coo_base, svo_coo_full, svo_coo_triple
    if not coo_of_commonPoint and not coo_of_sbv_of_commonPoint:  # 如果sbv和common point都没有coo，则不构成sbv-coo
        return svo_coo_base, svo_coo_full, svo_coo_triple
    svo_coo_base = True  # 存在基本的svo coo结构
    # 走到这里，就说明存在sbv-coo结构，但是存在基本的sbv-coo结构并不就是sbv-coo，还有一个要求：
    # 即triple中各个部分所在的位置：arg1要么在common point的sbv中，要么在这个sbv的coo中
    # rel必须在common point的coo中，或者coo的vob中（如果coo的vob还有vob的话），
    # arg2必须在common point的coo的vob中或者coo的vob的vob中
    arg1_in_coo_of_sbv = False  # 如果arg1在sbv的coo中，则rel可以是common point，然后arg2在vob中
                            # 当然，此时rel也可以在common point的coo中
    # 先在sbv of common point或者coo of sbv of common point中把与arg1的交找出来
    intersection_of_sbv_of_commonPoint_with_arg1 = [ind for ind in sbv_of_commonPoint
                                     if ind in triple_in_number[0]]
    intersection_of_coo_of_sbv_of_commonPoint_with_arg1 = \
                    [ind for ind in coo_of_sbv_of_commonPoint if ind in triple_in_number[0]]
    if intersection_of_sbv_of_commonPoint_with_arg1:
        svo_coo_triple.append(intersection_of_sbv_of_commonPoint_with_arg1)
    elif intersection_of_coo_of_sbv_of_commonPoint_with_arg1:
        svo_coo_triple.append(intersection_of_coo_of_sbv_of_commonPoint_with_arg1)
        arg1_in_coo_of_sbv = True
    else:  # sbv或者sbv的coo中都没有arg1，因此不是sbv coo结构
        return svo_coo_base, svo_coo_full, svo_coo_triple  # True, False, []
    # 走到这里，arg1已经找到了，接下来处理rel和arg2
    # if tree.sentenceID == 7798:
    #     print('yes')
    intersection_of_coo_of_commonPoint_with_rel = [ind for ind in coo_of_commonPoint
                                                   if ind in triple_in_number[1]]
    intersection_of_vob_of_commonPoint_with_arg2 = [ind for ind in vob_of_commonPoint
                                                    if ind in triple_in_number[2]]
    vob_of_coo_of_commonPoint = [ind - 1 for ind, par, dep in tree.dep_list
                                 if par - 1 in coo_of_commonPoint and dep == "VOB"]
    vob_of_vob_of_coo_of_commonPoint = [ind - 1 for ind, par, dep in tree.dep_list
                                        if par - 1 in vob_of_coo_of_commonPoint and dep == "VOB"]
    intersection_of_vob_of_coo_of_commonPoint_with_rel = [ind for ind in vob_of_coo_of_commonPoint
                                                          if ind in triple_in_number[1]]
    intersection_of_vob_of_coo_of_commonPoint_with_arg2 = [ind for ind in vob_of_coo_of_commonPoint
                                                           if ind in triple_in_number[2]]
    intersection_of_vob_of_vob_of_coo_of_commonPoint_with_arg2 = \
        [ind for ind in vob_of_vob_of_coo_of_commonPoint if ind in triple_in_number[2]]

    # 因为common point中已经存在sbv，因此这时必须保证rel中的点不再有sbv，或者FOB
    if intersection_of_coo_of_commonPoint_with_rel:
        need_delete_index = [index-1 for _, index, dep, in tree.dep_list \
                         if index-1 in intersection_of_coo_of_commonPoint_with_rel and dep in ["SBV", "FOB"]]
        intersection_of_coo_of_commonPoint_with_rel = [index for index in intersection_of_coo_of_commonPoint_with_rel if
                                                   index not in need_delete_index]
    if intersection_of_vob_of_coo_of_commonPoint_with_rel:
        need_delete_index = [index-1 for _, index, dep, in tree.dep_list \
                         if index-1 in intersection_of_vob_of_coo_of_commonPoint_with_rel and dep in ["SBV", "FOB"]]
        intersection_of_vob_of_coo_of_commonPoint_with_rel = [index for index in intersection_of_vob_of_coo_of_commonPoint_with_rel if
                                                   index not in need_delete_index]
    # 1. 如果arg1_in_coo_of_sbv为True，则common point可能为rel，此时arg2在vob of common point中
    commonPoint_in_rel = True if common_point in triple_in_number[1] else False
    if arg1_in_coo_of_sbv and commonPoint_in_rel:
        if intersection_of_vob_of_commonPoint_with_arg2:
            svo_coo_triple.append([common_point])
            svo_coo_triple.append(intersection_of_vob_of_commonPoint_with_arg2)
            svo_coo_full = True
            return svo_coo_base, svo_coo_full, svo_coo_triple
    # 2. rel在coo of common point中
    if intersection_of_coo_of_commonPoint_with_rel:
        if intersection_of_vob_of_coo_of_commonPoint_with_arg2:
            svo_coo_triple.append(intersection_of_coo_of_commonPoint_with_rel)
            svo_coo_triple.append(intersection_of_vob_of_coo_of_commonPoint_with_arg2)
            svo_coo_full = True
            return svo_coo_base, svo_coo_full, svo_coo_triple
    # 3. coo of common point 与vob of coo of common point共同组成rel
    if intersection_of_coo_of_commonPoint_with_rel and \
                    intersection_of_vob_of_coo_of_commonPoint_with_rel:
        if intersection_of_vob_of_vob_of_coo_of_commonPoint_with_arg2:
            rel = intersection_of_coo_of_commonPoint_with_rel + \
                  intersection_of_vob_of_coo_of_commonPoint_with_rel
            svo_coo_triple.append(rel)
            svo_coo_triple.append(intersection_of_vob_of_vob_of_coo_of_commonPoint_with_arg2)
            svo_coo_full = True
            return svo_coo_base, svo_coo_full, svo_coo_triple

    return svo_coo_base, svo_coo_full, svo_coo_triple


def isSVO(tree, triple_in_number):  # triple_in_number从0开始
    # 给定目标句子tree及其上的抽取结果，判断抽取结果是否是主谓宾结构，即subject-verb-object
    # 这里的SVO要求arg1对应S，rel对应V，arg2对应O，同时要求S和O与rel中同一个点连接
    # 统一以triple的形式返回，即[[1], [2], [3]]的形式返回结果
    arg1 = triple_in_number[0]
    rel = triple_in_number[1]
    arg2 = triple_in_number[2]
    # 得到rel所有点的子孙，如果这些子孙与arg1和arg2交集为空，则返回False
    relSChild = [ind-1 for ind, par, dep in tree.dep_list if par-1 in rel and dep == "SBV"]  # ind-1是因为dep_list下标从1开始
    relSChild = [ind for ind in relSChild if ind in arg1]
    relOChild = [ind-1 for ind, par, dep in tree.dep_list if par-1 in rel and dep == "VOB"]  # ind-1是因为dep_list下标从1开始
    relOChild = [ind for ind in relOChild if ind in arg2]
    if len(set(relSChild).intersection(set(arg1))) == 0:
        return None  # S不在arg1中
    if len(set(relOChild).intersection(set(arg2))) == 0:
        return None  # O不在arg2中
    # 走到这里就说明S, O都存在，现在需要判断S和O是否连接rel中的同一个点
    SVOTriples = []
    for indS in relSChild:
        # print(indS)
        par = tree.dep_list[indS][1]
        for indO in relOChild:
            if tree.dep_list[indO][1] == par:
                SVOTriples.append([[indS], [par-1], [indO]])
    if len(SVOTriples) == 1:  # 一个triple中只可能有一个svo triple
        return SVOTriples[0]
    return None

def _isSingletonArg(tree, SVOTriple):  # SVOTriple: [0, 1, 2]
    # 给定SVOTriple，判断argument是否是无分支的，两个argument只要有一个即返回True，否则False
    arg1 = SVOTriple[0]
    arg2 = SVOTriple[2]
    arg1Singleton = True
    arg2Singleton = True
    currentIndexes = [arg1]
    while currentIndexes:
        if len(currentIndexes) > 1:
            arg1Singleton = False
            break
        if currentIndexes[0] + 1 in tree.who_depend.keys():
            temp = currentIndexes[0]
            # 在考虑是否为单支时，将符号和COO都剔除后再来看是否单支
            currentIndexes = [index-1 for index in tree.who_depend[temp+1]
                                        if tree.dep_list[index-1][2] not in ['COO', 'WP']]
        else:
            currentIndexes = None
    currentIndexes = [arg2]
    while currentIndexes:
        if len(currentIndexes) > 1:
            arg2Singleton = False
            break
        if currentIndexes[0]+1 in tree.who_depend.keys():
            temp = currentIndexes[0]
            currentIndexes = [index-1 for index in tree.who_depend[temp + 1]
                                if tree.dep_list[index-1][2] not in ['COO', 'WP']]
        else:
            currentIndexes = None
    return arg1Singleton, arg2Singleton

def findSemanticParts4SingletonArg_SVO(tree, argIndex):
    # 已知triple是SVO结构，且argIndex是S或者O，且这个arg是单支的
    # 返回完整的arg index list
    # 在单支的情况下，只要依存不是coo或者wp，就把这些归入arg中
    argCandidate = [argIndex]  # 定义一个待考察点集合，先将argIndex放入其中，从0开始计数的
    arg = []
    while argCandidate:  # 只要仍然存在待考察点，就继续考察
        currentInd = argCandidate.pop(0)
        arg.append(currentInd)
        if currentInd + 1 in tree.who_depend.keys():
            currentIndexes = [index - 1 for index in tree.who_depend[currentInd + 1]
                              if tree.dep_list[index - 1][2] not in ['COO', 'WP']]  #
            argCandidate.extend(currentIndexes)
    arg.sort()
    return arg

def findSemanticParts4MultipleBranchArg_SVO(tree, argIndex, avoidIndex):  # argIndex从0开始计数的
    # 给定tree，已知是SVO结构，给定SVO结构中的arg点的index，即argIndex(从0开始计数)
    # 已知argIndex具有多分支
    # 由此找出语义相同部分，返回整个完整的arg的index
    # 如果判断某个COO分支需要分开，则剔除该分支

    argCandidate = [argIndex]  # 定义一个待考察点集合，先将argIndex放入其中，从0开始计数的
    arg = []
    while argCandidate:  # 只要仍然存在待考察点，就继续考察
        currentInd = argCandidate.pop(0)
        if avoidIndex:
            if currentInd not in avoidIndex:
                arg.append(currentInd)
        else:
            arg.append(currentInd)
        if currentInd + 1 in tree.who_depend.keys():  # 待考察点有孩子
            for index in tree.who_depend[currentInd + 1]: # 注意这里index是从1开始的
                if tree.dep_list[index - 1][2] == 'COO':
                    if cooNeedToFusion(tree, tree.dep_list[index - 1][1]-1, tree.dep_list[index - 1][0]-1):
                        argCandidate.append(index-1)
                else:
                    if tree.word_list[index-1] not in [',', '，']:
                        argCandidate.append(index - 1)
    arg.sort()
    return arg

def findSemanticParts4MultipleBranchArg(tree, argIndexList, avoidIndex):  # argIndex从0开始计数的， 是一个list
    # 给定tree
    # 已知argIndex具有多分支
    # 由此找出语义相同部分，返回整个完整的arg的index
    # 如果判断某个COO分支需要分开，则剔除该分支
    # avoidIndex是需要避开的点组成的list，值从0开始
    argCandidate = argIndexList  # 定义一个待考察点集合，先将argIndex放入其中，从0开始计数的
    arg = []
    while argCandidate:  # 只要仍然存在待考察点，就继续考察
        currentInd = argCandidate.pop(0)
        if avoidIndex:
            if currentInd not in avoidIndex:
                arg.append(currentInd)
        else:
            arg.append(currentInd)
        if currentInd + 1 in tree.who_depend.keys():  # 待考察点有孩子
            for index in tree.who_depend[currentInd + 1]: # 注意这里index是从1开始的
                if tree.dep_list[index - 1][2] == 'COO':
                    if cooNeedToFusion(tree, tree.dep_list[index - 1][1]-1, tree.dep_list[index - 1][0]-1):
                        argCandidate.append(index-1)
                else:
                    if tree.word_list[index-1] not in [',', '，']:
                        argCandidate.append(index - 1)
    arg.sort()
    return arg

def cooNeedToFusion(tree, cooParentNodeIndex, cooChildNodeIndex):
    # 由于大部分的COO都是需要分割的，只有少数几种情况下COO是融合的，所以建立这个返回判断是否是需要融合
    # cooParentNodeIndex和cooChildNodeIndex之间有COO的依存关系，从0开始
    # 如果需要融合，则返回True，否则返回False
    needToFusion = False
    # 1.1 cooParentNodeIndex和cooChildNodeIndex两个word紧挨，cooChildNodeIndex没有孩子，则融合
    if abs(cooParentNodeIndex - cooChildNodeIndex) == 1 and len(tree.tree_dict[cooChildNodeIndex + 1]) == 0:
        return True
    # 1.2 cooParentNodeIndex和cooChildNodeIndex两个word之间间隔了一个-符号，且cooChildNodeIndex再无其他关联，则融合
    if len(tree.tree_dict[cooChildNodeIndex + 1]) == 1 and tree.word_list[
        tree.tree_dict[cooChildNodeIndex + 1][0] - 1] == "-":
        return True
    # # 1.3 COO中cooChildNodeIndex及其所有孩子在一个()中，融合，返回True
    # 首先得到孩子及其所有下标
    cooBlockIndex = []
    needToCheckIndex = [cooChildNodeIndex + 1]
    while needToCheckIndex:
        currentPointIndex = needToCheckIndex.pop()
        cooBlockIndex.append(currentPointIndex)
        if currentPointIndex in tree.tree_dict.keys() and len(tree.tree_dict[currentPointIndex]) > 0:
            needToCheckIndex.extend(tree.tree_dict[currentPointIndex])
    cooBlockIndex.sort()
    if tree.word_list[cooBlockIndex[0] - 1] in ["（", "(", "《", '"', '“']:
        if tree.word_list[cooBlockIndex[-1] - 1] in ["）", ")", "》", '"', '”']:
            # cooBlockIndex.append(cooParentNodeIndex + 1)
            # temp = [index - 1 for index in cooBlockIndex]
            # cooResult = [temp]
            return True
    # 1.4 cooParentNodeIndex和cooChildNodeIndex两个word紧挨，parent没有vob，child有或者没有vob，返回True
    if abs(cooParentNodeIndex - cooChildNodeIndex) == 1: # coo中两个词紧挨
        # 找出parent和child所有的孩子类型
        parentDeps = [tree.dep_list[ind-1][2] for ind in tree.tree_dict[cooParentNodeIndex+1]]
        parentDeps = list(set(parentDeps))
        if 'VOB' not in parentDeps:
            return True
    return False  # 默认情况下cooParentNodeIndex, cooChildNodeIndex是要分开的

def find_semantic_parts_general_version(tree, triple_in_number):
    # 给定一棵树tree及其上的抽取结果triple_in_number，返回语义补全的triple_in_number
    # triple_in_number都是从0开始

    # 1. 先对arg1和arg2进行补全
    # 注意到每个点只可能有一个父亲
    new_args = []
    for i in [0, 2]:  # arg1和arg2
        argCandidate = triple_in_number[i]  # 定义一个待考察点集合，先将argIndex放入其中，从0开始计数的
        arg = []
        avoid_node_list = []
        if i == 0:
            avoid_node_list.extend(triple_in_number[2])
            avoid_node_list.extend(triple_in_number[1])
        else:
            avoid_node_list.extend(triple_in_number[0])
            avoid_node_list.extend(triple_in_number[1])
        while argCandidate:  # 只要仍然存在待考察点，就继续考察
            currentInd = argCandidate.pop(0)
            if currentInd not in avoid_node_list:
                arg.append(currentInd)
            if currentInd + 1 in tree.tree_dict.keys():  # 待考察点有孩子
                for index in tree.tree_dict[currentInd + 1]:  # 注意这里index是从1开始的
                    if tree.dep_list[index - 1][2] == 'COO':
                        if cooNeedToFusion(tree, tree.dep_list[index - 1][1] - 1, tree.dep_list[index - 1][0] - 1):
                            argCandidate.append(index - 1)
                    else:
                        if tree.word_list[index - 1] not in [',', '，']:
                            argCandidate.append(index - 1)
        arg.sort()
        new_args.append(arg)
    # 2. 对rel进行补全
    rel = findSemanticParts4Rel_SVO(tree, triple_in_number)
    return [new_args[0], rel, new_args[1]]


def processingPOB(tree, vt, triple_in_number):  # triple_in_number从0开始
    # newTriple_in_number = _processingPOB(tree, vt, triple_in_number)
    # if newTriple_in_number:  # 是POB
        # 进行常规补全操作
    argIndexList = triple_in_number[0]
    avoidIndex = [ind for i in [1, 2] for ind in triple_in_number[i]]
    arg1 = findSemanticParts4MultipleBranchArg(tree, argIndexList, avoidIndex=avoidIndex)
    argIndexList = triple_in_number[2]
    avoidIndex = [ind for i in [0, 1] for ind in triple_in_number[i]]
    arg2 = findSemanticParts4MultipleBranchArg(tree, argIndexList, avoidIndex=avoidIndex)
    rel = findSemanticParts4Rel_SVO(tree, triple_in_number)
    return [arg1, rel, arg2]  # 返回的triple从0开始


def _processingPOB(tree, vt, triple_in_number):
    # vt在tree上有triple_in_number的抽取结果，triple_in_number从0开始
    # 已知triple_in_number中含有POB，现在进行处理
    # 处理方案：1. POB要考虑介词文字；2. 进行正常补齐
    # 首先判断是否是所有triple点都在介词之下且介词不在triple中，如果是这样就直接进行补齐即可
    # allNodesInTriple = [ind for i in range(3) for ind in triple_in_number[i]]  # 从0开始
    POBPairs_InTree = []  # [(1, 2)], 1为POB的parent，即介词，2为child，均从0开始
    POBPairs_dict_InTree = {'arg1':[], 'rel':[], 'arg2':[]}
    allNodesInTriple_InTree = []
    for i in range(3):
        for nod in triple_in_number[i]:
            allNodesInTriple_InTree.append(nod)
            if tree.dep_list[nod][2] == "POB":
                POBPairs_InTree.append((tree.dep_list[nod][1]-1, nod))
                if i == 0:
                    POBPairs_dict_InTree['arg1'].append(tree.word_list[nod])
                elif i == 1:
                    POBPairs_dict_InTree['rel'].append(tree.word_list[nod])
                else:
                    POBPairs_dict_InTree['arg2'].append(tree.word_list[nod])
    if len(POBPairs_InTree) == 0:  # 不是POB结构
        return None  # 不返回任何结果

    # 接下来判断是否triple中所有点都是某个介词的子节点且该介词不在triple中
    # 如果符合这一情况，则无需处理，直接返回triple_in_number
    # 看谁能够把allIsChild变为True
    for pobP, pobC in POBPairs_InTree:
        if pobP not in allNodesInTriple_InTree: # 介词不在triple中
            # 判断triple中每个都是否都是pobP的子节点
            allIsChild = True
            for node in allNodesInTriple_InTree:  # 从0开始
                # 找出node的所有祖先
                nodeIsChild = False
                currentInd = node + 1
                while currentInd != 0:
                    currentInd = tree.parents[currentInd]
                    if currentInd == pobP+1:
                        nodeIsChild = True
                        break
                if nodeIsChild:
                    continue
                else:  # 找到了一个点不是pobP的child,
                    allIsChild = False
                    break
            if allIsChild:
                return triple_in_number  # 还需要补齐操作

    # 如果没有上面的情况，则接下来判断triple_in_number是否与vt中的介词是同一个词
    # 即考虑介词文字是否一致
    # 方法是：按照arg1, arg2, rel分别来找出tree和vt中的POB，比较是否是同样介词
    POBPairs_dict_InVT = {'arg1': [], 'rel': [], 'arg2': []}
    for i in range(3):
        for nod in vt.triple_in_num[i]:  # 注意这个值从1开始
            if vt.real_tree.dep_list[nod-1][2] == "POB":
                if i == 0:
                    POBPairs_dict_InTree['arg1'].append(vt.real_tree.word_list[nod-1])
                elif i == 1:
                    POBPairs_dict_InTree['rel'].append(vt.real_tree.word_list[nod-1])
                else:
                    POBPairs_dict_InTree['arg2'].append(vt.real_tree.word_list[nod-1])

    isSame = True
    for name in ['arg1', 'rel', 'arg2']:
        POBPairs_dict_InTree[name].sort()
        POBPairs_dict_InVT[name].sort()
        if POBPairs_dict_InTree[name] != POBPairs_dict_InVT[name]:
            isSame = False
            break
    if isSame:
        return triple_in_number
    else:
        return None


def findSemanticParts4Rel_SVO(tree: Tree, triple_in_number):
    # 对于是SVO结构的抽取结果中的rel部分寻找语义相同句子成分
    # 对于抽取到的rel中的每个词进行遍历，如果该词符合规则就进行补全
    # triple_in_number 从0开始
    # print(triple_in_number)
    # if tree.sentenceID == 717:
    #     print('yes')
    rules = [  # 0表示当前词的位置，-1表示当前词前一个位置的，1表示当前词后一个位置
                        {'dep':[(0, -1, 'ADV')], 'pos':{-1: 'd'},  'words': {-1: '将'}},
                        {'dep': [(0, -2, 'ADV')], 'pos': {-2: 'd'}, 'words': {-2: '被迫'}},
                        {'dep': [(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '被迫'}},
                        {'dep':[(0, -1, 'ADV')], 'pos':{-1: 'd'},  'words': {-1: '只'}},
                        {'dep': [(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '免'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '曾'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'v'}, 'words': {-1: '有望'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'v'}, 'words': {-1: '未能'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '没有'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '不'}},
                        {'dep': [(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '绝不'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '必须'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '从未'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'r'}, 'words': {-1: '*'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '不能'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '没'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '非'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '休'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '莫'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '不是'}},
                        {'dep':[(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '勿'}},
                        {'dep': [(0, -1, 'ADV')], 'pos': {-1: 'd'}, 'words': {-1: '没能'}},
        {'dep': [(0, -1, 'ADV')], 'pos': {-1: 'v'}, 'words': {-1: '需要'}},
        {'dep': [(0, -1, 'ADV'), (-1, -2, 'ADV')], 'pos': {-1: 'v', -2: 'd'}, 'words': {-1: '需要', -2: '不'}},
                        {'dep': [(0, -1, 'ADV'), (0, -2, 'ADV')], 'pos': {-1: 'v', -2: 'd'}, 'words': {-1: '去', -2: '不'}},
                        {'dep':[(2, 0, 'CMP'), (1, 2, 'ADV')], 'pos': {1: 'd', 2: 'v'}, 'words': {1: '不', 2: '了'}},
                        {'dep': [(-2, -1, 'ADV'), (-1, 0, 'ADV')], 'pos': {-2: 'd', -1: 'v'}, 'words': {-2: '不', -1: '能'}},
                      ]
    allWordIndexBeenUsed = []
    relWordIndex = triple_in_number[1]
    newRelWordIndex = relWordIndex.copy()
    for i in range(3):
        allWordIndexBeenUsed.extend(triple_in_number[i])
    for wordIndex in relWordIndex:  # triple中都是从0开始计数
        # 对每个word进行遍历，查看是否符合rule
        ruleGot = False
        for rule in rules:
            # 首先检查words是否符合
            tempIndex = []
            for key, value in rule['words'].items():
                if wordIndex+key > len(tree.word_list)-1:
                    continue
                if tree.word_list[wordIndex+key] == value and wordIndex+key not in allWordIndexBeenUsed:
                    tempIndex.append(wordIndex+key)
                else:
                    tempIndex = []
                    break
            # 暂时只考虑词匹配就可以，dep和pos暂不考虑
            if tempIndex:
                newRelWordIndex.extend(tempIndex)
                ruleGot = True
                break
        if ruleGot:  # 原rule中只要有一个词匹配到了，就终止
            break
    newRelWordIndex = list(set(newRelWordIndex))
    newRelWordIndex.sort()
    return newRelWordIndex







