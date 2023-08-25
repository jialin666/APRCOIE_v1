import json
from V_I.tool.tool import get_Core_and_AdditionNodes, getCommonParent
from V_I.all_classes.class_virtual_tree import Virtual_Tree
from V_I.tool.tool import _check_ltpResult
from V_I.all_classes.class_tree import Tree
import V_I.tool.tool_organize_template as TOT
import time
import pickle

annotated_data_regular_path = "..\\data\\data_regular.json"  # annotated data except attribute
annotated_data_att_path = "..\\data\\data_att.json"  # annotated attribute data

model_path = "..\\data\\model.obj"
model_att_path = "..\\data\\model_att.obj"

# reading annotated data
with open(annotated_data_regular_path, 'r', encoding='utf-8') as f:
    _data = json.load(f)

data = {}
for item in _data:
    new_item = {}
    id = item['id']
    print(id)
    sentence = item['sentence']
    postags = item['postag'].split(',')
    deps = json.loads(item['dep'])
    words = json.loads(item['words'])
    new_item['words-with-index'] = json.loads(item['words-with-index'])
    # triples_number = json.loads(item['triples-number'])  # 要注意这里是从0开始计数
    _triples_number = json.loads(item['triples-number'])  # 要注意这里是从0开始计数
    triples_char = []
    triples_number = []
    for triple in _triples_number:
        arg1 = "".join([words[index] for index in triple[0]])
        rel = "".join([words[index] for index in triple[1]])
        arg2 = "".join([words[index] for index in triple[2]])
        triples_number.append(triple)
        triples_char.append([arg1, rel, arg2])
    data[id] = [sentence, postags, deps, words, triples_number, triples_char]

# 读取训练数据生成所有的VT
vt_list = []  # 保存每个vt，这里的id同上面的id
vtCounter = 0

for id in data.keys():
    if _check_ltpResult(data[id][2]):  # check dependency
        tree = Tree(data[id][0], data[id][3], data[id][2], data[id][1], id)  # 句子，词，依存，词性
        for i, triple in enumerate(data[id][4]):  # triple-in-number
            arg1Num = [ind+1 for ind in triple[0]]
            relNum = [ind+1 for ind in triple[1]]
            arg2Num = [ind+1 for ind in triple[2]]
            _triple = [arg1Num, relNum, arg2Num]
            core_nodes = get_Core_and_AdditionNodes(tree, _triple)
            # 下面得到core nodes的共同父亲，这样从该节点往下查找子结构
            commonParent = getCommonParent(tree, core_nodes)
            vtID = str(tree.sentenceID) + "-" + str(i)
            # vt中的triple in number从1开始，标注数据中的从0开始
            virTree = Virtual_Tree(commonParent, core_nodes, tree, _triple, vtID=vtID)
            vt_list.append(virTree)
            vtCounter +=1

_, _, vt_of_svo_list, vt_of_svo_coo_list, _ \
                            = TOT.delete_same_template(vt_list)
vt_afte_deduplication = {"vt_of_pob_list": [],
                         "vt_of_att_list": [],
                         "vt_of_svo_list": vt_of_svo_list,
                         "vt_of_svo_coo_list": vt_of_svo_coo_list,
                         "vt_of_no_no_no_no": []}
with open(model_path, 'wb') as f:
    pickle.dump(vt_afte_deduplication, f)


# reading annotated att data
with open(annotated_data_att_path, 'r', encoding='utf-8') as f:
    _data = json.load(f)

data = {}
for item in _data:
    # new_item = {}
    id = item['id']
    print(id)
    sentence = item['sentence']
    postags = item['postag'].split(',')
    deps = json.loads(item['dep'])
    words = json.loads(item['words'])
    # new_item['words-with-index'] = json.loads(item['words-with-index'])
    # triples_number = json.loads(item['triples-number'])  # 要注意这里是从0开始计数
    _triples_number = json.loads(item['triples-number'])  # 要注意这里是从0开始计数
    triples_char = []
    triples_number = []
    for triple in _triples_number:
        arg1 = "".join([words[index] for index in triple[0]])
        rel = "".join([words[index] for index in triple[1]])
        arg2 = "".join([words[index] for index in triple[2]])
        triples_number.append(triple)
        triples_char.append([arg1, rel, arg2])
    data[id] = [sentence, postags, deps, words, triples_number, triples_char]

print("训练和测试数据语句个数为：", len(data))  # 10000, 5930

# 读取训练数据生成所有的VT
vt_list = []  # 保存每个vt，这里的id同上面的id
vtCounter = 0

for id in data.keys():
    if _check_ltpResult(data[id][2]):  # check dependency
        tree = Tree(data[id][0], data[id][3], data[id][2], data[id][1], id)  # 句子，词，依存，词性
        for i, triple in enumerate(data[id][4]):  # triple-in-number
            arg1Num = [ind+1 for ind in triple[0]]
            relNum = [ind+1 for ind in triple[1]]
            arg2Num = [ind+1 for ind in triple[2]]
            _triple = [arg1Num, relNum, arg2Num]
            core_nodes = get_Core_and_AdditionNodes(tree, _triple)
            # 下面得到core nodes的共同父亲，这样从该节点往下查找子结构
            commonParent = getCommonParent(tree, core_nodes)
            vtID = str(tree.sentenceID) + "-" + str(i)
            # vt中的triple in number从1开始，标注数据中的从0开始
            virTree = Virtual_Tree(commonParent, core_nodes, tree, _triple, vtID=vtID)
            vt_list.append(virTree)
            vtCounter +=1

print("去重前vt数量：", len(vt_list))
st = time.time()
_, vt_of_att_list, _, _, _ \
                            = TOT.delete_same_template(vt_list)
vt_afte_deduplication = {"vt_of_pob_list": [],
                         "vt_of_att_list": vt_of_att_list,
                         "vt_of_svo_list": [],
                         "vt_of_svo_coo_list": [],
                         "vt_of_no_no_no_no": []}
with open(model_att_path, 'wb') as f:
    pickle.dump(vt_afte_deduplication, f)
et = time.time()
elapsedTime = et - st
print('模板去除耗时：', elapsedTime)

# # 读取vt******************

