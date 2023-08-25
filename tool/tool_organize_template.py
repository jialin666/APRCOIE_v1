# template指的是vt，具体来说是vt中的vt_schema和mapping_triple
from ..all_classes.class_virtual_tree import Virtual_Tree
from ..all_classes.class_node import Node
from ..all_classes.class_tree import Tree
from typing import List, Tuple, Any
from ..tool.tool_generateTriples_givenTemplate import generate_triples_given_vt
import V_I.tool.tool_processingPOB as PPOB
import V_I.tool.tool_postProcessing as TPP


def is_same(vt1: Virtual_Tree, vt2: Virtual_Tree) -> bool:
    # 判断vt1，vt2是否一样，是则返回True，否则返回False
    # vt schema: {1: [('.{3}  v%%%', -1, [0, 1])], 2: [('SBV nh%%%', 0, []), ('VOB ns%%%', 0, [])]}
    # 判断两个的vt schema，如果完全一致就是same
    if len(vt1.vt_schema) != len(vt2.vt_schema):  # 如果两个vt 的 vt schema层次都不一样，返回False
        return False
    for key in vt1.vt_schema.keys():
        if len(vt1.vt_schema[key]) != len(vt2.vt_schema[key]):  # 如果第key层的节点数不一样，返回False
            return False
        for i in range(len(vt1.vt_schema[key])):
            item1 = vt1.vt_schema[key][i]
            item2 = vt2.vt_schema[key][i]
            if item1[0] != item2[0]:
                return False
            if item1[1] != item2[1]:
                return False
            if item1[2] != item2[2]:
                return False
    # 还需要判断mapping_triple一致
    mapping_triple = {"arg1": [], "rel": [], "arg2": []}  # 指示triple中每个部分是第几层第几个词
    # mapping_triple["arg1"] = [(1, 2), (2, 1)]意思是要抽取的triple的arg1由两个词组成：
    if len(vt1.mapping_triple['arg1']) != len(vt2.mapping_triple['arg1']):
        return False
    if len(vt1.mapping_triple['rel']) != len(vt2.mapping_triple['rel']):
        return False
    if len(vt1.mapping_triple['arg2']) != len(vt2.mapping_triple['arg2']):
        return False
    return True


def _tripleName(vt, nodeID):
    if nodeID in vt.triple_in_num[0]:
        return 'arg1'
    elif nodeID in vt.triple_in_num[1]:
        return 'rel'
    elif nodeID in vt.triple_in_num[2]:
        return 'are2'
    else:
        return 'None'
# 判断VTreeA是否是VTreeB的子结构
def isSubstructure(VTreeA: Virtual_Tree, VTreeB: Virtual_Tree) -> bool:
    # 判断treeA是否是treeB的子结构(n叉树),传入前要保证ab必不为空
    #首先在BTreeB中找到所有和VTreeA中common parent相等的点，然后从这个点开始搜索
    # 在使用该函数前需要先判断这两个VT是否相等，如果相等则不需要再调用本函数
    # if len(VTreeA.core_nodes_id_list) >= len(VTreeB.core_nodes_id_list):
    #     return False
    if max(VTreeA.level_to_node_dict.keys()) - min(VTreeA.level_to_node_dict.keys()) > \
            max(VTreeB.level_to_node_dict.keys()) - min(VTreeB.level_to_node_dict.keys()):
        return False
    nodes_equal_to_VALevel1 = []
    for nodeID, node in VTreeB.nodes_dict.items():
        if _nodeIsEqual(VTreeA.nodes_dict[VTreeA.level_to_node_dict[1][0]], node, True):
            # 比较两个点各自的triple成分
            triNameA = _tripleName(VTreeA, VTreeA.level_to_node_dict[1][0])
            triNameB = _tripleName(VTreeB, nodeID)
            if triNameA == triNameB:
                nodes_equal_to_VALevel1.append(nodeID)
    if len(nodes_equal_to_VALevel1) == 0:
        return False
    is_sub = False  # 先假设不是子结构
    for nodeID in nodes_equal_to_VALevel1:
        result = _isSubstructure_VBNodes(VTreeA, VTreeB, nodeID)
        if result:
            is_sub = True
            break
    return is_sub

# def _isSubstructure_2(VTreeA: Virtual_Tree, VTreeB: Virtual_Tree) -> bool:
#     if max(VTreeA.level_to_node_dict.keys()) - min(VTreeA.level_to_node_dict.keys()) > \
#             max(VTreeB.level_to_node_dict.keys()) - min(VTreeB.level_to_node_dict.keys()):
#         return False
#     nodes_equal_to_VALevel1 = []  # 从vb中先找出和va第一层匹配的点，然后在vb中从这些点开始遍历
#     for nodeID, node in VTreeB.nodes_dict.items():
#         if _nodeIsEqual(VTreeA.nodes_dict[VTreeA.level_to_node_dict[1][0]], node, True):
#             nodes_equal_to_VALevel1.append(nodeID)
#     if len(nodes_equal_to_VALevel1) == 0:
#         return False
#     if max(VTreeA.level_to_node_dict.keys()) == 1:  # 如果VTA只有一层，则A是B子结构，返回True
#         return True
#     is_sub = False  # 先假设不是子结构
#     nodesMatchingSituationAllLevels = {1:{VTreeA.level_to_node_dict[1][0]:nodes_equal_to_VALevel1}}  # 记录所有层每个点的匹配情况 {1: {1:[3,4], 3:[5, 6]}, 2:{...}}
#     for nodeID in nodes_equal_to_VALevel1:
#         # 接下来va中从第二层、vb中从nodeID的下一层中同步进行遍历
#         currentLevelA = VTreeA.level_to_node_dict[2]
#         currentLevelA.sort()
#         parentA = VTreeA.level_to_node_dict[1]
#         currentLevelB = [key for key, value in VTreeB.parent_dict.items() if value == nodeID]
#         currentLevelB.sort()
#         parentB = [nodeID]
#         if currentLevelA  and currentLevelB:
#             if len(currentLevelA) > len(currentLevelB):  # 要判断A是否是B的子结构，所以如果某一层A中的点数比B中还多，那肯定不行
#                 continue
#             # 保证triple中的点保持一致即可
#             # 对于A中的点，在B中找到对应的点，如果有A中的点在B中找不到对应的点，则结束这个nodeID的搜索
#             for noIDA in currentLevelA:
#                 for noIDB in currentLevelB:







# 在isSubstructure的基础上判断两个是子结构的是否每个子结构的triple成分也一致

# 判断两个当前节点是否一致
def _nodeIsEqual(nodeInVA: Node, nodeInVB: Node, is_top_level: bool) -> bool:
    if is_top_level:
        return nodeInVA.node_level1_string == nodeInVB.node_level1_string
    else:
        return nodeInVA.node_mask_string == nodeInVB.node_mask_string

def _isSubstructure_VBNodes(VTreeA: Virtual_Tree, VTreeB: Virtual_Tree, nodeID_from_VB: int):
    # 从VTreeB的nodeID_from_VB开始判断，VTreeA是否是其子结构
    # 已知VTreeA的common parent与nodeID_from_VB是一致的
    if len(VTreeA.level_to_node_dict[2]) == 0:  # 如果VTA只有一层，则A是B子结构，返回True
        return True
    # A树未到叶子节点，但是B树到了叶子节点，说明匹配失败
    if nodeID_from_VB in VTreeB.real_tree.leaf_nodes:
        return False
    level_matching_node_pair = {1:{VTreeA.level_to_node_dict[1][0]:[nodeID_from_VB]}}
    matchedNodesInB = {1:[nodeID_from_VB]}  # 记录B中每层匹配到的点，这些点是下层匹配到的点的父节点
    # level_matching_node_pair记录两个树每一次的匹配情况，比如下面1:{1:[1]}指第一层中，A的1和B的1匹配，记录B之所以用list是考虑其中多个点
    # 和A的点匹配，毕竟是从B中找A的子结构；
    # 要注意这里的level与A的level是一致的，而B的实际level需要加上起始点的level
    # {1：{1:[1]}, 2:{3：[5], 5:[6, 8]}, 3:{2:[3], 7:[4, 7]}}
    for level in range(2, max(VTreeA.level_to_node_dict.keys())+1):
        # 如果VB已经超出最底层了
        if VTreeB.node_to_level_dict[nodeID_from_VB]+level-1 > max(VTreeB.level_to_node_dict.keys()):
            return False
        # 按照A的层次从上到下进行遍历；因为要考虑到最后一层，所以要+1
        matching_node_pair = {}  # 形如{nodeA: [匹配的nodeB]}，记录当前层每个A点匹配的B点
        alreadyUsedNodeInBInCurrentLevel = []
        for nodeA in VTreeA.level_to_node_dict[level]:
            foundB = False
            nodeB_list = VTreeB.level_to_node_dict[VTreeB.node_to_level_dict[nodeID_from_VB]+level-1]
            if not nodeB_list:
                return False
            for nodeB in nodeB_list:
                if nodeB not in alreadyUsedNodeInBInCurrentLevel:
                    if _nodeIsEqual(VTreeA.nodes_dict[nodeA], VTreeB.nodes_dict[nodeB], False):
                        triNameA = _tripleName(VTreeA, nodeA)
                        triNameB = _tripleName(VTreeB, nodeB)
                        if triNameA == triNameB:  # 判断两个点是否是同样的triple成分
                            if VTreeB.parent_dict[nodeB] in matchedNodesInB[level-1]:
                                if level not in matchedNodesInB.keys():
                                    matchedNodesInB[level] = [nodeB]
                                else:
                                    matchedNodesInB[level].append(nodeB)
                                foundB = True
                                alreadyUsedNodeInBInCurrentLevel.append(nodeB)
                                if nodeA in matching_node_pair:
                                    matching_node_pair[nodeA].append(nodeB)
                                else:
                                        matching_node_pair[nodeA] = [nodeB]
            if not foundB:
                return False
        level_matching_node_pair[level] = matching_node_pair
    # 走到这里就说明对于A的所有层中的点，都在B中找到了与之对应的点
    # 接下来要判断父子结构是否一致
    # 由于第一层不考虑父节点，第二层的父节点都只有一个，因此如果VT A不超过2，则是子结构
    if max(VTreeA.level_to_node_dict.keys())  <= 2:
        return True
    # VT A层次超过2
    consist = True
    for level in range(3, max(VTreeA.level_to_node_dict.keys())+1):
        level_consist = True
        for key, value in level_matching_node_pair[level].items():
            item_consist = False
            for nodeB in value:
                if VTreeB.parent_dict[nodeB] in level_matching_node_pair[level-1][VTreeA.parent_dict[key]]:
                    item_consist = True
            if not item_consist:
                level_consist = False
        if not level_consist:
            consist = False
    if not consist:
        return False
    return True

def delete_same_template(vt_list: List[Virtual_Tree]):
    print('开始时vt的数量', len(vt_list))
    # POB结构单独处理
    # ATT单独处理
    vt_of_att_list = []
    vt_of_pob_list = []
    vt_of_svo_list = []
    vt_of_svo_coo_list = []
    vt_of_no_no_no_no = []
    # 首先要删除完全一致的vt
    sameClusters = {}
    duplicatedVt = []  # 所有重复的vt
    duplicatedVTPair = []
    for i in range(len(vt_list) - 1):
        if i in duplicatedVt:
            continue
        for j in range(i + 1, len(vt_list)):
            sameVT = is_same(vt_list[i], vt_list[j])
            if sameVT:
                if i not in duplicatedVt:
                    duplicatedVt.append(i)
                if j not in duplicatedVt:
                    duplicatedVt.append(j)
                duplicatedVt = list(set(duplicatedVt))
                if i in sameClusters.keys():
                    sameClusters[i].append(j)
                else:
                    sameClusters[i] = [i, j]
                duplicatedVTPair.append((vt_list[i], vt_list[j]))
    vtListIndex = [i for i in range(len(vt_list)) if i not in duplicatedVt]
    vtListIndex.extend(list(sameClusters.keys()))  # vtListIndex是没有重复的vt在vt_list中的index
    _vt_list = [vt_list[i] for i in range(len(vt_list)) if i in vtListIndex]

    # 接下来找出所有的ATT
    _vt_of_att_list = []
    for i, vt in enumerate(_vt_list):
        arg1 = [ind-1 for ind in vt.triple_in_num[0]]
        rel = [ind-1 for ind in vt.triple_in_num[1]]
        arg2 = [ind-1 for ind in vt.triple_in_num[2]]
        temp_triple = [arg1, rel, arg2]
        if TPP.isATT(vt.real_tree, temp_triple):
            _vt_of_att_list.append(i)
    vt_of_att_list = [_vt_list[ind] for ind in _vt_of_att_list]
    _vt_list = [_vt_list[ind] for ind in range(len(_vt_list)) if ind not in _vt_of_att_list]

    # 接下来找出所有的POB vt
    _vt_of_pob_list = []
    _vt_of_pob_index = []
    for index in range(len(_vt_list)):
        vt = _vt_list[index]
        _triple = []
        arg1Num = [ind - 1 for ind in vt.triple_in_num[0]]
        _triple.append(arg1Num)
        relNum = [ind - 1 for ind in vt.triple_in_num[1]]
        _triple.append(relNum)
        arg2Num = [ind - 1 for ind in vt.triple_in_num[2]]
        _triple.append(arg2Num)
        ispob, POBPairs, POBPairs_dict = PPOB.is_POB(vt.real_tree, _triple)
        if ispob:
            _vt_of_pob_list.append(vt)
            _vt_of_pob_index.append(index)
    _vt_list = [_vt_list[ind] for ind in range(len(_vt_list)) if ind not in _vt_of_pob_index]
    usedVTIndex = []
    vt_of_pob_list_index = []
    for i in range(len( _vt_of_pob_list) - 1):
        if i not in usedVTIndex:
            vt_i = _vt_of_pob_list[i]
            vtSameWithI = [i]
            for j in range(i + 1, len( _vt_of_pob_list)):
                if j not in usedVTIndex:
                    vt_j =  _vt_of_pob_list[j]
                    if PPOB.is_samePOB(vt_i, vt_j):
                        vtSameWithI.append(j)
            vt_of_pob_list_index.append(i)
            usedVTIndex.extend(vtSameWithI)
    vt_of_pob_list = [ _vt_of_pob_list[i] for i in vt_of_pob_list_index]
    # print(len(newVTWithPOBList))
    # vt_list = [_vt_list[i] for i in range(len(_vt_list)) if i not in vtPOBIndex]
    # print('剩下的vt list长度为：', len(vt_list))

    # 接下来找svo
    vt_svo_list = []
    for i in range(len(_vt_list)):
        triple = []
        for j in range(3):
            triple.append([ind-1 for ind in _vt_list[i].triple_in_num[j]])
        if TPP.isSVO(_vt_list[i].real_tree, triple):
            vt_svo_list.append(i)
    vt_of_svo_list = [_vt_list[i] for i in vt_svo_list]
    _vt_list = [_vt_list[i] for i in range(len(_vt_list)) if i not in vt_svo_list]

    # 接下来找svocoo
    svo_coo_index = []
    for i, vt in enumerate(_vt_list):
        triple = vt.triple_in_num
        arg1Num = [ind - 1 for ind in triple[0]]
        relNum = [ind - 1 for ind in triple[1]]
        arg2Num = [ind - 1 for ind in triple[2]]
        triple1 = [arg1Num, relNum, arg2Num]
        svo_coo_base, svo_coo_full, triple_svo_coo = TPP.isSVOCOO(vt.real_tree, triple1, True, vt)
        if svo_coo_full:
            svo_coo_index.append(i)
    vt_of_svo_coo_list = [_vt_list[ind] for ind in range(len(_vt_list)) if ind in svo_coo_index]
    vt_of_no_no_no_no = [_vt_list[ind] for ind in range(len(_vt_list)) if ind not in svo_coo_index]

    print('最后各种类型的vt数量为， pob数量为%d， att数量为%d， svo数量为%d, svocoo数量为%d, 其他类型数量为%d' % \
          (len(vt_of_pob_list), len(vt_of_att_list), len(vt_of_svo_list), len(vt_of_svo_coo_list), len(vt_of_no_no_no_no)))
    # vt_list.extend(newVTWithPOBList)
    # print('去重后vt总的数量为：', len(vt_list))
    return vt_of_pob_list, vt_of_att_list, vt_of_svo_list, vt_of_svo_coo_list, vt_of_no_no_no_no

def get_vt_edgeSet(vt_dict):
    vt_edgeSet = []  # vt构成的边集, 形如[(2, 4), (1, 5)], (2, 4)表示vt_list中第2个vt是第4个vt的子结构
    for i in range(len(vt_dict) - 1):
        vta = vt_dict[i]
        for j in range(i + 1, len(vt_dict)):
            if i == 3 and j == 6:
                print('wenti')
            vtb = vt_dict[j]
            if len(vta.nodes_dict) > len(vtb.nodes_dict):
                b_isSub_of_a = isSubstructure(vtb, vta)
                if b_isSub_of_a:
                    vt_edgeSet.append((j, i))
            if len(vta.nodes_dict) < len(vtb.nodes_dict):
                a_isSub_of_b = isSubstructure(vta, vtb)
                if a_isSub_of_b:
                    vt_edgeSet.append((i, j))
    return vt_edgeSet

# def _organize_vtCluster(vt_edgeSet_in_same_cluster, vt_dict):
#     # 属于同一个cluster的vt edge组成的List
#     return

def _get_vt_clusters(vt_edgeSet):
    # 返回的cluster_list形如[[2, 3, 5, 10], [20, 21, 45, 50]]
    # edge_cluster_list形如[[(2, 3), (3, 5), (5, 10)], [(20, 21), (45, 20), (45, 50)]]

    cluster_list = []
    for s, e in vt_edgeSet:
        if len(cluster_list) == 0:  # 开始阶段
            cluster_list.append([s, e])
            continue
        need_fused_vt_index = []
        for i in range(len(cluster_list)):
            # 看看对于当前的s,e，能够把哪些cluster融合在一起
            if s in cluster_list[i] or e in cluster_list[i]:
                cluster_list[i].extend([s, e])
                need_fused_vt_index.append(i)
        if len(need_fused_vt_index) == 0:
            cluster_list.append([s, e])
            continue
        if len(need_fused_vt_index) == 1:
            continue
        if len(need_fused_vt_index) > 0:
            _cluster_list = [cluster_list[i] for i in range(len(cluster_list)) if i not in need_fused_vt_index]
            temp = []
            for i in need_fused_vt_index:
                temp.extend(cluster_list[i])
            _cluster_list.append(temp)
            cluster_list = _cluster_list
    cluster_list = [list(set(cluster)) for cluster in cluster_list]
    edge_cluster_list = [[] for i in range(len(cluster_list))]

    for s, e in vt_edgeSet:
        for i in range(len(cluster_list)):
            if s in cluster_list[i] and e in cluster_list[i]:
                edge_cluster_list[i].append((s, e))
    return cluster_list, edge_cluster_list

# 先对标注数据调用generate_all_template，得到所有的vt
# 然后调用delete_same_template删除相同template
# 然后再使用organize_template以vt cluster形式组织vt
def seperate_vtList(vt_list: List[Virtual_Tree]):# vt_list是最原始的vt list，没有去重，没有判断是否有子结构关系
    # 将所有的原始vt分成孤立的部分和构成图的部分
    # 返回的fingle_vt就是孤立的vt的index组成的list
    # 而cluster_list是由cluster组成的list，一个cluster就是连在一起的vt index组成的list，而edge_cluster_list是连在一起的边集组成list
    # 构成edge cluster
    vt_cluster_id_list = []  # [[2, 5, 10], [8, 50, 120]],表示2,5,10这几个vt被联系在一起

    vt_list = delete_same_template(vt_list)  # 先对vt去重
    vt_dict = {i: vt_list[i] for i in range(len(vt_list))}  # key作为vt的编号

    vt_edgeSet = get_vt_edgeSet(vt_dict)  # vt构成的边集, 形如[(2, 4), (1, 5)]

    # 找出哪些点是单独成树的
    all_nodes_in_vt_edgeSet = []  # 这些vt就不是单独成树了
    for s, e in vt_edgeSet:
        all_nodes_in_vt_edgeSet.extend([s, e])
    all_nodes_in_vt_edgeSet = list(set(all_nodes_in_vt_edgeSet))  # 去重
    # single_vt是那些单个vt组成的list，这些vt不与其他任何vt有子结构关系
    single_vt_index_list = [vt_index for vt_index in vt_dict.keys() if vt_index not in all_nodes_in_vt_edgeSet]
    cluster_list, edge_cluster_list = _get_vt_clusters(vt_edgeSet)
    return single_vt_index_list, cluster_list, edge_cluster_list, vt_dict

def generate_triples_given_vt_cluster(target_tree: Tree, edge_cluster, vt_dict):
    # 给定一个cluster进行抽取，注意这里的cluster只是vt index
    # level_to_nodes, nodes_to_level, childs, parents = construct_vt_graph(edge_cluster)
    # print(edge_cluster[0], '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    all_tree = construct_vt_graph(edge_cluster)  # parents, childs, level_to_nodes, nodes_to_level


    final_result = []
    worked_noIndex = []
    # for vt_index in level_to_nodes[1]:
    for vt_index in all_tree.keys():
        # vt_index是树的根，all_tree中每个元素都是一个tree
        # _depth_first_search_of_vtTree(target_tree, level_to_nodes, childs, parents, vt_dict)
        triples, real_noIndex = _depth_first_search_of_vtTree(target_tree, all_tree[vt_index][2],
                                                              all_tree[vt_index][1],
                                                              all_tree[vt_index][0],
                                                              vt_dict)
        if triples:
            final_result.extend(triples)
            worked_noIndex.extend(real_noIndex)
    return final_result, worked_noIndex
    # childs指示每个vt有哪些孩子，parents指示每个vt有哪些父亲，都是字典，value都是list
    # 关键是针对一个图，如何制定抽取规则
    # 抽取规则：按层进行遍历，对于当前层中的点，如果不能抽取，则记录其不能抽取，。。。
    # 记录哪些能被抽取，在最后阶段选取真正的抽取结果

from ..all_classes.class_template import Template
def _depth_first_search_of_vtTree(target_tree: Tree, level_to_nodes, childs, parents, vt_dict):
    # 从vt_index点开始，进行深度优先遍历，确定抽取结果
    # 只有其下层没有抽取结果且其有抽取结果时，返回当前点
    # level_to_nodes, childs, parents共同定义一棵VT树，注意是VT树，不是图
    # 函数返回所有的triple及对其作用的vt index
    extracted_result = {}  # 以字典记录每个点（vt）的抽取结果，如果有抽取结果，则
    level_to_nodeIndex_who_can_obtain_triples = {}  # level:[], 以字典的形式记录每层能抽取结果的vt
    for level in level_to_nodes.keys():  # 按层遍历，当然，可能不到最底层就中止了遍历
        level_to_nodeIndex_who_can_obtain_triples[level] = []  # 只记录每层有抽取结果的点
        can_going_next_level = False  # 如果当前层中所有点都没有抽取结果，则为False，这样就直接中止上面的for
        for no_index in level_to_nodes[level]:
            if level == 1:
                triples = generate_triples_given_vt(target_tree, vt_dict[no_index])
            else:
                can_going = False  # 记录no_index是否需要考虑进行抽取，即：只要其父亲中有一个有抽取结果，则需要考虑对no_index抽取
                for _n_index in parents[no_index]:
                    if extracted_result[_n_index]:  # 只要有一个父亲有结果，就设置can_going为True
                        can_going = True
                        break
                if can_going:
                    triples = generate_triples_given_vt(target_tree, vt_dict[no_index])
            if triples:
                extracted_result[no_index] = triples
                level_to_nodeIndex_who_can_obtain_triples[level].append(no_index)
                can_going_next_level = True
            else:
                extracted_result[no_index] = None
        if not can_going_next_level:
            break

    # 接下来考察level_to_nodeIndex_who_can_obtain_triples，那些叶子节点就是要抽取的结果
    real_noIndex = []
    for level in level_to_nodeIndex_who_can_obtain_triples.keys():
        if level == max(level_to_nodeIndex_who_can_obtain_triples.keys()):  # 最底层的点肯定要作为最终结果输出
            real_noIndex.extend(level_to_nodeIndex_who_can_obtain_triples[level])
            continue
        # 对于非底层的点，只要其没有叶子节点在level_to_nodeIndex_who_can_obtain_triples中，则将其放入real_noIndex
        for no_index in level_to_nodeIndex_who_can_obtain_triples[level]:
            if no_index not in childs.keys():  # no_index没有子节点
                real_noIndex.append(no_index)
                continue
            intersection = [_no_index for _no_index in level_to_nodeIndex_who_can_obtain_triples[level+1]
                            if _no_index in childs[no_index]]
            if len(intersection) == 0:
                real_noIndex.append(no_index)

    final_triples = []
    for no_index in real_noIndex:
        final_triples.extend(extracted_result[no_index])
    return final_triples, real_noIndex

def construct_vt_graph(edge_cluster):
    end_list = []
    start_list = []
    for e, s in edge_cluster:  # 要注意e是s的子结构，边都是从下指向上的
        end_list.append(e)
        start_list.append(s)

    nodes_in_top = [noID for noID in end_list if noID not in start_list]  # 只有end没有start的点就是最上层的点
    nodes_in_top = list(set(nodes_in_top))  # nodes in top并不一定就是第一层的点，之所以top指的是其没有父节点
    nodes_in_top.sort()

    # 基于每个top node建立树，然后看看他们在哪一层可以合并成一个图
    all_tree = {}

    for noIndex in nodes_in_top:
        level = 1
        nodes_in_current_level = [noIndex]
        flag = True
        level_to_nodes = {}
        nodes_to_level = {}
        while flag:
            level_to_nodes[level] = nodes_in_current_level
            for nIndex in nodes_in_current_level:
                nodes_to_level[nIndex] = level
            nodes_in_next_level = []
            for e, s in edge_cluster:
                if e in level_to_nodes[level]:
                    nodes_in_next_level.append(s)
            nodes_in_next_level = list(set(nodes_in_next_level))
            _nodes_position_need_delete_in_next_level = []
            for i in range(len(nodes_in_next_level) - 1):
                for j in range(i + 1, len(nodes_in_next_level)):
                    if (nodes_in_next_level[i], nodes_in_next_level[j]) in edge_cluster:
                        _nodes_position_need_delete_in_next_level.append(j)
                    if (nodes_in_next_level[j], nodes_in_next_level[i]) in edge_cluster:
                        _nodes_position_need_delete_in_next_level.append(i)
            _nodes_position_need_delete_in_next_level = list(set(_nodes_position_need_delete_in_next_level))
            nodes_in_next_level = [nodes_in_next_level[i] for i in range(len(nodes_in_next_level))
                                   if i not in _nodes_position_need_delete_in_next_level]
            nodes_in_next_level = list(set(nodes_in_next_level))
            nodes_in_current_level = nodes_in_next_level
            if len(nodes_in_current_level) == 0:
                flag = False
            else:
                level += 1

        childs = {}
        parents = {}
        for level in level_to_nodes.keys():
            if level - 1 in level_to_nodes.keys():  # 考虑父节点
                for noID in level_to_nodes[level]:
                    for e, s in edge_cluster:
                        if s == noID and e in level_to_nodes[level - 1]:
                            if s in parents.keys():
                                parents[s].append(e)
                            else:
                                parents[s] = [e]

            if level + 1 in level_to_nodes.keys():  # 考虑子节点
                for noID in level_to_nodes[level]:
                    for e, s in edge_cluster:
                        if e == noID and s in level_to_nodes[level + 1]:
                            if e in childs.keys():
                                childs[e].append(s)
                            else:
                                childs[e] = [s]
        for key in childs.keys():
            childs[key].sort()
        for key in parents.keys():
            parents[key].sort()
        all_tree[noIndex] = [parents, childs, level_to_nodes, nodes_to_level]

    return all_tree

def main_generate_triples(vt_list: List[Virtual_Tree], target_tree:Tree):
    final_triples = []

    single_vt_index_list, cluster_list, edge_cluster_list, vt_dict = seperate_vtList(vt_list)
    for vt_index in single_vt_index_list:
        triples = generate_triples_given_vt(target_tree, vt_dict[vt_index])
        if triples:
            final_triples.extend(triples)

    for edge_cluster in edge_cluster_list:
        triples = generate_triples_given_vt_cluster(target_tree, edge_cluster, vt_dict)
        if triples:
            final_triples.extend(triples)

    return final_triples




