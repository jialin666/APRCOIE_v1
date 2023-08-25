from ..all_classes.class_template import Template
from ..all_classes.class_tree import Tree
from typing import List
from ..all_classes.class_virtual_tree import Virtual_Tree


def generate_triples_given_vt(target_tree: Tree, vt: Virtual_Tree)->List:
    # 这个函数是对上面5个函数的一个综合运用：只需要给定目标句的tree，和代表模板的virtual tree，返回抽取到的所有triple
    template = Template(vt)
    filled_schema_list = _fill_vt_schema(target_tree, template.vt_schema)
    triples_in_char = []
    triples_in_number = []
    for filled_schema in filled_schema_list:
        if filled_schema:
            triple_in_char = _generate_triple_givenVTSchema(target_tree, filled_schema, template.mapping_triple)
            triples_in_char.append(triple_in_char)
            arg1_in_number = []
            arg2_in_number = []
            rel_in_number = []
            for tup in template.mapping_triple['arg1']:
                arg1_in_number.append(filled_schema[tup[0]-1][tup[1]]-1)
            for tup in template.mapping_triple['arg2']:
                arg2_in_number.append(filled_schema[tup[0]-1][tup[1]]-1)
            for tup in template.mapping_triple['rel']:
                rel_in_number.append(filled_schema[tup[0]-1][tup[1]]-1)
            arg1_in_number = list(set(arg1_in_number))
            arg1_in_number.sort()
            rel_in_number = list(set(rel_in_number))
            rel_in_number.sort()
            arg2_in_number = list(set(arg2_in_number))
            arg2_in_number.sort()
            triples_in_number.append([arg1_in_number, rel_in_number, arg2_in_number])
    return triples_in_char, triples_in_number  # 这里返回的triples in number是从0开始的

def _generate_triple_givenVTSchema(target_tree, filled_vt_schema, VT_mapping_triple):
    # 在给定filled vt schema的条件下生成最终的triple
    triple = {}
    for key, value in VT_mapping_triple.items():
        _value = []
        for level, index in value:
            _value.append(filled_vt_schema[level-1][index])
        _value.sort()
        _value = [target_tree.nodes_dict[id].word for id in _value]
        triple[key] = _value
    return triple

def _fill_vt_schema(target_tree, VT_schema):
    # vt schema: {1: [('.{3}  v%%%', -1, [0, 1])], 2: [('SBV nh%%%', 0, []), ('VOB ns%%%', 0, [])]}
    # 每一个filled schema形如[[7], [1, 9, 11], [5, 13]]，意思是树第一层是7，第二层1,9,11,第三层5，13，每层都按照VT排列
    # 每一个filled schema都对应一个triple，因此filled schema与triple是等价的，只需要
    filled_schema_list = []

    for level in target_tree.level_to_node_dict.keys():  # 对target tree按层遍历
        target_level_gap = max(target_tree.level_to_node_dict.keys()) - level  # 首先判断target tree中的层次与
        vt_level_gap = max(VT_schema.keys()) - min(VT_schema.keys())           # vt schema中的层次是否匹配
        if target_level_gap < vt_level_gap:  # 目标树中的层次已经不如VT中层次多，因此终止
            break
        # 如果层次没有问题，则遍历当前层次中的点
        for node_id in target_tree.level_to_node_dict[level]:
            # 考虑node_id作为common parent是否可行，下面if判断两个第一层的node的字符串表示是否匹配
            if target_tree.nodes_dict[node_id].node_level1_string != VT_schema[1][0][0]:
                continue
            # 走到这里说明node_id是可以作为common parent的
            _filled_vt_schema_list = _fill_vt_schema_by_nodeID(target_tree, VT_schema, node_id, level)
            if _filled_vt_schema_list:
                filled_schema_list.extend(_filled_vt_schema_list)
    return filled_schema_list

def _fill_vt_schema_by_nodeID(target_tree, VT_schema, node_id, node_level):
    # 以node_id作为common parent，按照VT_schema，看看target_tree是否可以得到一个filled_vt_schema
    # 调用该函数时以判断node_id是可以作为common parent的
    # 每一个filled schema形如[[7], [1, 9, 11], [5, 13]]，意思是树第一层是7，第二层1,9,11,第三层5，13，每层都按照VT排列
    # 每一个filled schema都对应一个triple，因此filled schema与triple是等价的
    filled_schema_list = [[[node_id]]]  # 可能会产生多个filled schema
    for vt_level in VT_schema.keys():  # 顺着vt的层次进行遍历，如果在target tree中从node level开始每层都能找到匹配，则整体找到匹配
        current_target_level = node_level + vt_level - 1
        if vt_level == 1:
            continue  # 第一层已经处理了，所以直接跳过
        # 下面的node是node对象，而不是node id，是target tree中所有的current_target_level层中的点
        nodes_in_current_level_of_targetTree = [target_tree.nodes_dict[id] for id in
                                                target_tree.level_to_node_dict[current_target_level]]

        if len(nodes_in_current_level_of_targetTree) == 0:
            return None
        else:
            result = _find_all_permutation_of_level(nodes_in_current_level_of_targetTree, VT_schema[vt_level])
            if result == None or len(result) == 0:
                return None
            # result形如[[3, 13], [3, 15], [5, 13], [5, 15]]，即表示这一层中有4种搭配符合VT_schema的vt_level中的情况
            # 但是要注意的是没有验证result中点父节点是否符合条件
            # 接下来对于result中的每个项，验证父节点是否匹配，如果父节点匹配，这这一项可以放入filled_vt_schema
            _filled_schema_list = []  # 记录合格的result item
            exist_ok = False  # 只要上面result中存在一个合理的结果，exist_ok就变为True，表明target tree的当前层是合格的
            for filled_schema in filled_schema_list:
                node_list_in_last_level = filled_schema[-1]
                for item in result:
                    ok = True  # 指示item是否是合格的，一开始假定合格
                    for index in range(len(item)):
                        if target_tree.parents[item[index]] != node_list_in_last_level[VT_schema[vt_level][index][1]]:
                            ok = False
                    if ok:
                        _filled_schema = filled_schema.copy()
                        _filled_schema.append(item)
                        _filled_schema_list.append(_filled_schema)
                        exist_ok = True
            if exist_ok:
                filled_schema_list = _filled_schema_list
            else:
                return None
    return filled_schema_list

def _find_all_permutation_of_level(nodes_of_the_level_of_targetTree, VT_schema_level):
    # 考察target tree中某层节点有多少种VT_schema的一层中的组合
    # 这里的level大于1
    # nodes_of_the_level_of_targetTree是target tree中这一层的node对象组成的list
    all_permutation = []
    vt_string_list = [item[0] for item in VT_schema_level]
    target_node_string_list = [node.node_mask_string for node in nodes_of_the_level_of_targetTree]
    result = []  # 里面的元素是list，每个list代表一个target level中的可能组合，lisi中的元素是真正的node id
    for i, ithMaskString_of_vt_schema_in_currentLevel in enumerate(vt_string_list):
        #对vt_string_list进行遍历，从前往后，看target_node有多少与当前vt node匹配
        # 下面的matching_...是一个list，里面记录target level里有多少个点与vt schema的level层的第i个点匹配
        matching_nodeIndex_with__ith_vtString = \
                _find_all_matching_of_node(target_node_string_list, ithMaskString_of_vt_schema_in_currentLevel)
        if len(matching_nodeIndex_with__ith_vtString) == 0:
            return None
        if i == 0:  # result还是空的
            for it in matching_nodeIndex_with__ith_vtString:
                result.append([nodes_of_the_level_of_targetTree[it].id])
        else:
            _result = []
            for ii in range(len(result)):
                for it in matching_nodeIndex_with__ith_vtString:
                    if nodes_of_the_level_of_targetTree[it].id > result[ii][-1]:
                        temp_i = result[ii].copy()
                        temp_i.append(nodes_of_the_level_of_targetTree[it].id)
                        _result.append(temp_i)
            result = _result
                        # result[ii].append(nodes_of_the_level_of_targetTree[it].id)
    # 要注意这里的result并没有考虑父节点和子节点结构关系，需要调用函数考虑
    return result

def _find_all_matching_of_node(target_node_string_list, vt_string):
    result = []
    for i, t_string in enumerate(target_node_string_list):
        if t_string == vt_string:
            result.append(i)
    return result
