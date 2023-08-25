# 把所有的vt归为几个类型：连续ATT, SVO, POB, SVO-COO
from ltp import LTP
import pickle
from V_I.all_classes.class_tree import Tree
from V_I.tool.tool import _check_ltpResult
import V_I.tool.tool_extracte_with_matrices as MATRIX

model_path = "..\\data\\model.obj"
model_att_path = "..\\data\\model_att.obj"

# 读取vt
with open(model_path, 'rb') as f:
    all_vt = pickle.load(f)
vt_of_svo_list = all_vt['vt_of_svo_list']  # 读取svo模板
vt_of_svo_coo_list = all_vt['vt_of_svo_coo_list']  # 读取svocoo模板
with open(model_att_path, 'rb') as f:
    all_vt = pickle.load(f)
vt_of_att_list = all_vt['vt_of_att_list']  # 读取att模板

# 对输入的语句进行抽取
ltp = LTP("LTP/base", local_files_only=True) #force_download=True)

sentence = "在关口镇镇长张三的陪同下，浠水县胡河乡乡长李四考察农业高科技，浠水县县长陈顶过陪同。"
result = ltp.pipeline([sentence], tasks=['cws', 'pos', 'dep', 'sdp'])
word_list = result.cws[0]
pos_list = result.pos[0]
dep_list = [(i+1, result.dep[0]['head'][i], result.dep[0]['label'][i]) for i in range(len(result.dep[0]['head']))]

if _check_ltpResult(dep_list):  # check dependency
    test_tree = Tree(sentence, word_list, dep_list, pos_list, 0)  # 句子，词，依存，词性

    result = MATRIX.extraction_regular(test_tree, vt_of_svo_list, vt_of_svo_coo_list, vt_of_att_list)
    for triple in result:
        print(triple)


    # just extract att
    result = MATRIX.extraction_regular(test_tree, [], [], vt_of_att_list)
    for triple in result:
        print(triple)




