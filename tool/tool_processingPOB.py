# template指的是vt，具体来说是vt中的vt_schema和mapping_triple
from ..all_classes.class_virtual_tree import Virtual_Tree
from ..all_classes.class_tree import Tree
import V_I.tool.tool_organize_template as OT

def is_samePOB(vt1: Virtual_Tree, vt2: Virtual_Tree) -> bool:
    if OT.is_same(vt1, vt2):  # 两个vt基本结构相同
        # 1. 判断两个vt是否都是需要处理的POB
        triple1 = []
        for i in range(3):
            temp = [ind-1 for ind in vt1.triple_in_num[i]]
            triple1.append(temp)
        ispob, POBPairs_vt1, POBPairs_dict_vt1 = is_POB(vt1.real_tree, triple1)
        if not ispob:
            return False
        triple2 = []
        for i in range(3):
            temp = [ind - 1 for ind in vt2.triple_in_num[i]]
            triple2.append(temp)
        ispob, POBPairs_vt2, POBPairs_dict_vt2= is_POB(vt2.real_tree, triple2)
        if not ispob:
            return False
        # 走到这里说明两者都是需要处理的POB结构，且他们结构一致
        # 接下来看看介词是否一致，包括文字是否一致、位置是否一致
        if len(POBPairs_vt1) != len(POBPairs_vt2):
            return False
        for key in POBPairs_dict_vt1.keys():
            if len(POBPairs_dict_vt1[key]) != len(POBPairs_dict_vt2[key]):
                return False
            if len(POBPairs_dict_vt1[key]) != 0:
                POBPairs_dict_vt1[key].sort()
                POBPairs_dict_vt2[key].sort()
                if POBPairs_dict_vt1[key] != POBPairs_dict_vt2[key]:
                    return False
    else: # 连基本结构都不同，自然就直接返回False
        return False
    return True

def findOutPOBPairs(tree: Tree, triple_in_number: List):
    # 找出所有的triple_in_number中的点参与的POB结构
    # 这里的pair指介词及其孩子构成的pair
    # triple_in_number 从0开始
    POBPairs = []  # [(1, 2)], 1为POB的parent，即介词，2为child，均从0开始
    # POBPairs_dict = {'arg1': [], 'rel': [], 'arg2': []}  #
    for i in range(3):
        for nod in triple_in_number[i]:
            if tree.dep_list[nod][2] == "POB":
                POBPairs.append((tree.dep_list[nod][1] - 1, nod))
                # if i == 0:
                #     POBPairs_dict['arg1'].append(tree.word_list[nod])
                # elif i == 1:
                #     POBPairs_dict['rel'].append(tree.word_list[nod])
                # else:
                #     POBPairs_dict['arg2'].append(tree.word_list[nod])
    return POBPairs #, POBPairs_dict

def allPartsInAPreposition(tree: Tree, triple_in_number: List, POBPair: tuple) -> bool:
    # 判断triple_in_number中所有点都在一个POB结构的child之下的情况，这种情况的特殊之处在于虽然属于POB，
    # 但是不需要按照POB来处理
    # 注意： triple_in_number 从0开始
    allNodesInTriple = []
    for i in range(3):  # 得到triple中所有的点
        for nod in triple_in_number[i]:
            allNodesInTriple.append(nod)

    # 看谁能够把allIsChild变为True
    pobP, pobC = POBPair
    if pobP not in allNodesInTriple:  # 介词不在triple中
        # 判断triple中每个都是否都是pobC的子节点
        allIsChild = True  # 先假设所有点都是介词pobP的子节点，看谁能把此推翻
        for node in allNodesInTriple:  # 从0开始
            # 找出node的所有祖先
            nodeIsChild = False  # 假设当前点不是pobP的子节点，看谁能推翻
            if node == pobC:
                nodeIsChild = True
            else:
                currentInd = node + 1
                while tree.parents[currentInd] != 0:
                    currentInd = tree.parents[currentInd]  # tree.parents中的点是从1开始的，0表示HED
                    if currentInd == pobC + 1:  # 当前点是pobP的子节点，推翻了刚才的nodeIsChild=False
                        nodeIsChild = True
                        break  # 跳出上面的while
            if nodeIsChild:  # 如果当前点是pobB的子节点，那就继续上面的for node循环，看下一个点是否是pobP子节点
                continue
            else:  # 找到了一个点不是pobP的child, 那么allIsChild被推翻，不用再考察其他点了，需要考察另外的POB对
                allIsChild = False
                break
        if allIsChild:  # 走到这一步说明allIsChild=True没有被推翻，因此可以返回True
            return True
    return False

def vtIsFakePOB(tree: Tree, triple_in_number) -> (bool, List):
    # 判断triple_in_number是否是需要处理的POB结构
    # 这里的POB结构指的是需要特殊对待的POB结构，不包括allPartsInAPreposition函数为True的情况
    # triple_in_number从0开始
    # 1. 首先查看是否包括POB
    POBPairs = findOutPOBPairs(tree, triple_in_number)
    if len(POBPairs) == 0:
        return False, None

    # # 2. 查看是否是不需要处理的POB
    # if allPartsInAPreposition(tree, triple_in_number):
    #     return False, None

    return True, POBPairs


def is_POB(tree: Tree, triple_in_number) -> (bool, List, dict):
    # if tree.sentenceID == 33:
    #     print('yes')
    # 判断triple_in_number是否是需要处理的POB结构
    # 这里的POB结构指的是需要特殊对待的POB结构，不包括allPartsInAPreposition函数为True的情况
    # triple_in_number从0开始
    # 如果triple是POB，则返回True，POB对，POB位置
    # 1. 首先查看triple中是否包括POB
    POBPairs_1 = findOutPOBPairs(tree, triple_in_number)
    if len(POBPairs_1) == 0:
        return False, None, None

    # 2. 查看是否是不需要处理的POB
    POBPairs_2 = []
    for pair in POBPairs_1:
        if not allPartsInAPreposition(tree, triple_in_number, pair):
            POBPairs_2.append(pair)

    # 3. 查看是否是在成分内部的POB，这种情况下也是不需要处理的
    # POB在内部指POB对应的两个点及parent的父亲、child的孩子都在里面，这样的POB也不需要处理
    realPOBPairs = []
    for pair in POBPairs_2:  # 检查每个POB对，
        emptyIntersection = []
        for i in range(3):  # 与triple中的每个成分进行比对
            inter = [ind for ind in list(pair) if ind in triple_in_number[i]]  # 考察POB对与triple的第i个成分的交集
            if len(inter) == 1:  # 如果只有一个交点，则说明POB不在成分的内部
                realPOBPairs.append(pair)
                break
            elif len(inter) == 2:  # 如果POB都在内部，那么必须parent有父节点，且父节点不在内部，或者child有子节点，且子节点不在内部
                if tree.parents[pair[0]+1]-1 not in triple_in_number[i]:  # 如果POB中parent的父亲不在triple的第i个成分中
                    realPOBPairs.append(pair)   # 这样的POB也需要处理
                    break
                # elif tree.tree_dict[pair[1]+1]:  # 或者POB中child有孩子的话，
                #     inter2 = [ind-1 for ind in tree.tree_dict[pair[1]+1] if ind-1 in triple_in_number[i]]
                #     if len(inter2) == 0:
                #         realPOBPairs.append(pair)
                #         break
            elif len(inter) == 0:
                emptyIntersection.append(1)
        if sum(emptyIntersection) == 3:
            continue
    if len(realPOBPairs) == 0:
        return False, None, None

    # 还是在这里把那些POB介词及出现的位置找出来
    POBPairs_dict = {'arg1':[], 'rel':[], 'arg2':[]}  # 记录介词pobP在triple中的哪个部分，要注意：1.有可能介词不在triple中，此时看pobC在哪个部分
    # 2. 有可能pobP在一个成分中，pobC在另一个成分中，此时pobB当然算在其所在的成分中
    for pobP, pobC in realPOBPairs:
        position = -1
        for i in range(3):
            if pobP in triple_in_number[i]:
                position = i
        if position == -1:  # 说明介词pobP不在任何成分中，那就看pobC属于哪个成分
            for i in range(3):
                if pobC in triple_in_number[i]:
                    position = i
        if position == -1:  # 如果此时position仍然为-1，则说明这个POB结构不属于要处理的情况
            print('vtIsPOB中出现问题！！！')
            return False, None, None
        if position == 0:
            POBPairs_dict['arg1'].append(tree.word_list[pobP])
        elif position == 1:
            POBPairs_dict['rel'].append(tree.word_list[pobP])
        else :
            POBPairs_dict['arg2'].append(tree.word_list[pobP])

    return True, realPOBPairs, POBPairs_dict
