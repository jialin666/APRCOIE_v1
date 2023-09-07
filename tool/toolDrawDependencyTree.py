import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# px = 1/plt.rcParams['figure.dpi']  # pixel in inches
XLIMIT = 15
YLIMIT = 15
ZERO_X = XLIMIT/2
ZERO_Y = YLIMIT/2
FigSize = (XLIMIT, YLIMIT)
NodeHeight = 0.8  # 节点高度
RowSpacing = 1 # 行之间的空白
ColumnSpacing = 0.5  # 列之间的空白
PaddingSize = 0.2  # 文字和边缘直接空白
FontSize = 20  # 单位为point，即1/72 inch
LineColor = 'r'
Arg1Color = 'mediumorchid'
RelColor = 'deeppink'
Arg2Color = 'darkolivegreen'


def computingXYLimit(tree):  # 根据树形结构计算图的大小
    _xLimit = 0
    maxLevel = max(tree.level_to_node_dict.keys())
    _yLimit = (maxLevel+1) * (NodeHeight + RowSpacing)
    for level in tree.level_to_node_dict.keys():
        levelWidth = 0
        for treeNodeID in tree.level_to_node_dict[level]:  # 先计算整层的宽度
                    # 分别是：文字的宽度，
            nodeWidth = len(tree.nodes_dict[treeNodeID].word) * (FontSize/72) + \
                        2 * PaddingSize + \
                        len(tree.nodes_dict[treeNodeID].pos) * (FontSize/72) + 4 * (FontSize/72)
            levelWidth += nodeWidth
            levelWidth += ColumnSpacing
        if levelWidth > _xLimit:
            _xLimit = levelWidth

    if _xLimit <= XLIMIT:
        xLimit = XLIMIT
    else:
        xLimit = _xLimit
    if _yLimit <= YLIMIT:
        yLimit = YLIMIT
    else:
        yLimit = _yLimit
    return xLimit, yLimit

def drawNode(ax, index, word, pos, xx, yy, tripleType=None):  #index, word, pos, x, y
    #  nodeWidth计算为：word文字的宽度，首尾两个padding的宽度，pos字符的宽度，两位index的宽度，两个空格
    # tripleType = "arg1", "rel", "arg2"
    # tripleType 主要是为了设置节点的颜色
    nodeWidth = len(word) * (FontSize/72) + 2 * PaddingSize +\
                len(pos) * (FontSize/72) + 2 * (FontSize/72) + 2 * (FontSize/72)

    if tripleType == 'arg1':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=Arg1Color, label='arg1')
    elif tripleType == 'rel':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=RelColor, label='rel')
    elif tripleType == 'arg2':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=Arg2Color, label='arg2')
    else:
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color="#9EFFA9", label='NoTriple')
    nodeContent = ""
    if len(str(index)) == 1:
        nodeContent = " " +  str(index) + " "  # 两位放Index，如果只有一位则补空格
    else:
        nodeContent = str(index) + " "
    nodeContent = nodeContent + word + " " + pos
    ax.text(xx+PaddingSize, yy+NodeHeight/3, nodeContent, size=FontSize)
    # ax.text(xx , yy , nodeContent, size=FontSize)
    ax.add_patch(rectangle)

def drawSchemalNode(ax, index, word, pos, xx, yy, tripleType):  #index, word, pos, x, y
    #  nodeWidth计算为：word文字的宽度，首尾两个padding的宽度，pos字符的宽度，两位index的宽度，两个空格
    # tripleType = "arg1", "rel", "arg2"
    # 画schema node时一定要有tripleType
    nodeWidth = len(word) * (FontSize/72) + 2 * PaddingSize +\
                len(pos) * (FontSize/72) + 2 * (FontSize/72) + 2 * (FontSize/72)

    if tripleType == 'arg1':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=Arg1Color, label='arg1')
    elif tripleType == 'rel':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=RelColor, label='rel')
    elif tripleType == 'arg2':
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color=Arg2Color, label='arg2')
    else:
        rectangle = mpatches.Rectangle(xy=(xx, yy), width=nodeWidth, height=NodeHeight, color="#9EFFA9", label='NoTriple')
    if tripleType in ['arg1', 'arg2', 'rel']:
        if len(str(index)) == 1:
            nodeContent = " " +  str(index) + " "  # 两位放Index，如果只有一位则补空格
        else:
            nodeContent = str(index) + " "
        nodeContent = nodeContent + '***' + " " + pos
    else:
        nodeContent = '...'
    ax.text(xx+PaddingSize, yy+NodeHeight/3, nodeContent, size=FontSize)
    # ax.text(xx , yy , nodeContent, size=FontSize)
    ax.add_patch(rectangle)

def drawNodes(ax, tree, triple=None, drwaSchema=False):
    # 计算每个节点的起始位置和宽度
    levelToEachNodeSize = {}
    maxLevel = max(tree.level_to_node_dict.keys())
    for level in tree.level_to_node_dict.keys():
        levelToEachNodeSize[level] = []  # 每个node size由三个值表示：起始点的x, y，宽度
        if level == 1:  # 第一层是根节点，只有一个节点，特殊处理
            if len(tree.level_to_node_dict[1]) != 1:
                print('Tree中出现错误！')
                return
            nodeWidth = 3 * (FontSize/72) + 2 * PaddingSize
            x = ZERO_X
            y = ZERO_Y + int(maxLevel/2) * (RowSpacing + NodeHeight)
            # ax.plot(x, y, 'bo')
            levelToEachNodeSize[level].append((x, y, nodeWidth))
        else:
            levelWidth = 0
            for treeNodeID in tree.level_to_node_dict[level]:  # 先计算整层的宽度
                        # 分别是：文字的宽度，
                nodeWidth = len(tree.nodes_dict[treeNodeID].word) * (FontSize/72) + \
                            2 * PaddingSize + \
                            len(tree.nodes_dict[treeNodeID].pos) * (FontSize/72) + 4 * (FontSize/72)
                levelWidth += nodeWidth
                levelWidth += ColumnSpacing
            levelWidth = levelWidth - ColumnSpacing  # 减去最后一个节点加上的column spacing
            # 在得到这一层的levelWidth之后就可以确定第一个节点的坐标了
            y = -(level - 1) * (RowSpacing + NodeHeight) + ZERO_Y + int(maxLevel/2) * (RowSpacing + NodeHeight)
            x = - levelWidth / 2 + ZERO_X
            # ax.plot(x, y, 'bo')
            for i in range(len(tree.level_to_node_dict[level])):
                treeNodeID = tree.level_to_node_dict[level][i]
                nodeWidth = len(tree.nodes_dict[treeNodeID].word) * (FontSize/72) + 2 * PaddingSize + \
                            len(tree.nodes_dict[treeNodeID].pos) * (FontSize/72) + 4 * (FontSize/72)
                levelToEachNodeSize[level].append((x, y, nodeWidth))
                x = x + nodeWidth
                x = x + ColumnSpacing

    for level in tree.level_to_node_dict.keys():
        for i in range(len(tree.level_to_node_dict[level])):
            # print(tree.sentenceID)
            # if tree.sentenceID == 1944:
            #     print(type(tree.sentenceID))
            treeNode = tree.nodes_dict[tree.level_to_node_dict[level][i]]

            tripleType = None
            if triple:
                # 问题在这里？

                if treeNode.id in triple[0]:
                    tripleType = 'arg1'
                elif treeNode.id in triple[1]:
                    tripleType = 'rel'
                elif treeNode.id in triple[2]:
                    tripleType = 'arg2'

            if not drwaSchema:
                drawNode(ax, treeNode.id, treeNode.word, treeNode.pos, levelToEachNodeSize[level][i][0],
                     levelToEachNodeSize[level][i][1], tripleType)
            else:
                drawSchemalNode(ax, treeNode.id, treeNode.word, treeNode.pos, levelToEachNodeSize[level][i][0],
                                levelToEachNodeSize[level][i][1], tripleType)
    return levelToEachNodeSize

def drawAllEdges(ax, levelToEachNodeSize, tree):
    for level in levelToEachNodeSize.keys():
        if level == 1:
            continue
        for i in range(len(levelToEachNodeSize[level])):
            currentNodeIndex = tree.level_to_node_dict[level][i]
            if level == 2:  # 该层所有点都指向根节点
                startPointX = levelToEachNodeSize[level-1][0][0] + levelToEachNodeSize[level-1][0][2]/2
                startPointY = levelToEachNodeSize[level-1][0][1]
                endPointX = levelToEachNodeSize[level][i][0] + levelToEachNodeSize[level][i][2]/2
                endPointY = levelToEachNodeSize[level][i][1] + NodeHeight
                text = tree.dep_list[currentNodeIndex-1][2]
                ax.plot([startPointX , endPointX], [startPointY, endPointY], LineColor, linewidth=4)
                ax.text((startPointX + endPointX)/2, (startPointY + endPointY)/2, text, size=FontSize)
                # if i < len(levelToEachNodeSize[level])/2:
                #     ax.text((startPointX + endPointX)/2, (startPointY + endPointY)/2-0.2, text, size=FontSize)
                #     # ax.text(endPointX + PaddingSize, endPointY + NodeHeight/3, text, size=FontSize)
                # else:
                #     ax.text((startPointX + endPointX) / 2, (startPointY + endPointY) / 2 - 0.2, text, size=FontSize)
                    # ax.text(endPointX - PaddingSize, endPointY + NodeHeight / 3, text, size=FontSize)
            else:  # 其他层就需要根据tree中提供的信息确定从哪个节点到哪个节点进行连边
                parentNodeIndex = tree.parents[currentNodeIndex]  # 找出父节点index
                if parentNodeIndex not in tree.level_to_node_dict[level-1]:
                    print('找不到父节点！')
                    return
                index = tree.level_to_node_dict[level-1].index(parentNodeIndex)
                startPointX = levelToEachNodeSize[level-1][index][0] + levelToEachNodeSize[level-1][index][2]/2
                startPointY = levelToEachNodeSize[level-1][index][1] # - NodeHeight
                endPointX = levelToEachNodeSize[level][i][0] + levelToEachNodeSize[level][i][2]/2
                endPointY = levelToEachNodeSize[level][i][1]  + NodeHeight
                ax.plot([startPointX, endPointX], [startPointY, endPointY], LineColor, linewidth=4)
                text = tree.dep_list[currentNodeIndex - 1][2]
                ax.text((startPointX + endPointX)/2, (startPointY + endPointY)/2, text, size=FontSize)

def drawDependencyTree(tree, triple=None, triple_index = -1, drawSchema = False, figSavePath="D:\\dependencyTreeGraphs\\"):
    # 给定一棵树，画出依存树，如果给定triple，则将triple中的点以不同颜色画出
    # triple_index是当前triple在标注语句中的triple序号，比如某标注句有3个triple，则序号为0,1,2，triple_index只涉及到图的文件名
    # 给定triple的话就会将triple中的点以不同颜色显示，不给定triple则所有点使用同样颜色
    # drawSchema为True则隐去每个节点的内容
    # if tree.sentenceID == 2:
    #     print('problem')
    # print("drawDependencyTree现在画树：", tree.sentenceID)
    xLimit, yLimit = computingXYLimit(tree)
    xLimit = int(xLimit) + 1
    yLimit = int(yLimit) + 3
    # print(xLimit, yLimit)
    fig, ax = plt.subplots(figsize=(xLimit, yLimit))
    plt.rc('axes', unicode_minus=False)
    plt.rcParams['font.sans-serif'] = ['simhei']
    # ax.set_xlim(0, XLIMIT)
    # ax.set_ylim(0, YLIMIT)
    levelToEachNodeSize = drawNodes(ax, tree, triple, drawSchema)
    drawAllEdges(ax, levelToEachNodeSize, tree)
    if triple:
        _handles, _labels = ax.get_legend_handles_labels()
        handles = []
        labels = []
        for i in range(len(_labels)):
            if _labels[i] not in labels:
                labels.append(_labels[i])
                handles.append(_handles[i])
            else:
                continue
        # print(tree1.sentenceID, type(tree2.sentenceID))

        arg1Index = labels.index('arg1')
        arg2Index = labels.index('arg2')
        relIndex = labels.index('rel')
        if 'NoTriple' in labels:
            noIndex = labels.index('NoTriple')
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
        else:
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]

        ax.legend(_handles, _labels)

    xmin, xmax, ymin, ymax = plt.axis()
    ax.text(xmin+0.5, ymax-0.2, tree.sentence, size=FontSize)
    # ax.legend()
    path = figSavePath  + str(tree.sentenceID)
    # print(path)
    if triple_index != -1:
        path = path + "-" + str(triple_index)
    path = path + ".jpg"
    # print(path)
    plt.savefig(path)
    plt.close()
    # plt.show()`

def drawComparisonGivenTwoTrees(tree1, tree2,triple1=None, triple2=None,
                        triple_index1 = -1, drawSchema1 = False,
                            triple_index2 = -1, drawSchema2 = False,
                                figSavePath="D:\\dependencyTreeGraphs\\subStructure\\"):
    # 给定两个Tree，将依存树画在一张图上方便对比，如果给定triple则将triple点以不同颜色画出
    print("drawComparisonGivenTwoTrees画两个对比树", tree1.sentenceID, tree2.sentenceID)

    xLimit1, yLimit1 = computingXYLimit(tree1)
    xLimit1 = int(xLimit1) + 1
    yLimit1 = int(yLimit1) + 3
    xLimit2, yLimit2 = computingXYLimit(tree2)
    xLimit2 = int(xLimit2) + 1
    yLimit2 = int(yLimit2) + 3
    xLimit = 2* max(xLimit1, xLimit2)
    yLimit = 2* max(yLimit1, yLimit2)
    # print(xLimit, yLimit)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(xLimit, yLimit))
    plt.rc('axes', unicode_minus=False)
    plt.rcParams['font.sans-serif'] = ['simhei']
    # ax.set_xlim(0, XLIMIT)
    # ax.set_ylim(0, YLIMIT)
    levelToEachNodeSize = drawNodes(ax1, tree1, triple1, drawSchema1)
    drawAllEdges(ax1, levelToEachNodeSize, tree1)
    if triple1:
        _handles, _labels = ax1.get_legend_handles_labels()
        handles = []
        labels = []
        for i in range(len(_labels)):
            if _labels[i] not in labels:
                labels.append(_labels[i])
                handles.append(_handles[i])
            else:
                continue
        # print(tree1.sentenceID, type(tree2.sentenceID))

        arg1Index = labels.index('arg1')
        arg2Index = labels.index('arg2')
        relIndex = labels.index('rel')
        if 'NoTriple' in labels:
            noIndex = labels.index('NoTriple')
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
        else:
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
    # print(_handles)
    # print(_labels)
    # print('************************************')
        ax1.legend(_handles, _labels)
    xmin1, xmax1 = ax1.get_xlim()
    ymin1, ymax1 = ax1.get_ylim()
    ax1.text(xmin1+0.5, ymax1-0.2, tree1.sentence, size=FontSize)


    levelToEachNodeSize = drawNodes(ax2, tree2, triple2, drawSchema2)
    drawAllEdges(ax2, levelToEachNodeSize, tree2)
    if triple2:
        _handles, _labels = ax2.get_legend_handles_labels()
        handles = []
        labels = []
        for i in range(len(_labels)):
            if _labels[i] not in labels:
                labels.append(_labels[i])
                handles.append(_handles[i])
            else:
                continue

        arg1Index = labels.index('arg1')
        arg2Index = labels.index('arg2')
        relIndex = labels.index('rel')
        if 'NoTriple' in labels:
            noIndex = labels.index('NoTriple')
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
        else:
            _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
            _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
        # print(_handles)
        # print(_labels)
        # print('************************************')
        ax2.legend(_handles, _labels)
    xmin2, xmax2 = ax2.get_xlim()
    ymin2, ymax2 = ax2.get_ylim()
    ax2.text(xmin2 + 0.5, ymax2 - 0.2, tree2.sentence, size=FontSize)

    # ax.legend()
    path = figSavePath  + str(tree1.sentenceID) + "-" + str(tree2.sentenceID)
    path = path + ".jpg"
    # print(path)
    plt.savefig(path)
    plt.close()

def drawComparisonGivenTwoVTs(vt1, vt2, drawSchema1 = False, drawSchema2 = False,
                       figSavePath="D:\\dependencyTreeGraphs\\subStructure\\"):
    # 这个函数和drawComparisonGivenTwoTrees实质上是一样的，只是给定两个VT，然后从VT中把tree和triple取出来
    print('drawComparisonGivenTwoVTs画两个vt', vt1.vtID, vt2.vtID)
    xLimit1, yLimit1 = computingXYLimit(vt1.real_tree)
    xLimit1 = int(xLimit1) + 1
    yLimit1 = int(yLimit1) + 3
    xLimit2, yLimit2 = computingXYLimit(vt2.real_tree)
    xLimit2 = int(xLimit2) + 1
    yLimit2 = int(yLimit2) + 3
    xLimit = 2* max(xLimit1, xLimit2)
    yLimit = 2* max(yLimit1, yLimit2)
    # print(xLimit, yLimit)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(xLimit, yLimit))
    plt.rc('axes', unicode_minus=False)
    plt.rcParams['font.sans-serif'] = ['simhei']
    # ax.set_xlim(0, XLIMIT)
    # ax.set_ylim(0, YLIMIT)
    levelToEachNodeSize = drawNodes(ax1, vt1.real_tree, vt1.triple_in_num, drawSchema1)
    drawAllEdges(ax1, levelToEachNodeSize, vt1.real_tree)
    _handles, _labels = ax1.get_legend_handles_labels()
    handles = []
    labels = []
    for i in range(len(_labels)):
        if _labels[i] not in labels:
            labels.append(_labels[i])
            handles.append(_handles[i])
        else:
            continue
    arg1Index = labels.index('arg1')
    arg2Index = labels.index('arg2')
    relIndex = labels.index('rel')
    if 'NoTriple' in labels:
        noIndex = labels.index('NoTriple')
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
    else:
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
    # print(_handles)
    # print(_labels)
    # print('************************************')
    ax1.legend(_handles, _labels)
    xmin1, xmax1 = ax1.get_xlim()
    ymin1, ymax1 = ax1.get_ylim()
    ax1.text(xmin1+0.5, ymax1-0.2, vt1.real_tree.sentence, size=FontSize)

    levelToEachNodeSize = drawNodes(ax2, vt2.real_tree, vt2.triple_in_num, drawSchema2)
    drawAllEdges(ax2, levelToEachNodeSize, vt2.real_tree)
    _handles, _labels = ax2.get_legend_handles_labels()
    handles = []
    labels = []
    for i in range(len(_labels)):
        if _labels[i] not in labels:
            labels.append(_labels[i])
            handles.append(_handles[i])
        else:
            continue
    arg1Index = labels.index('arg1')
    arg2Index = labels.index('arg2')
    relIndex = labels.index('rel')
    if 'NoTriple' in labels:
        noIndex = labels.index('NoTriple')
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
    else:
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
    # print(_handles)
    # print(_labels)
    # print('************************************')
    ax2.legend(_handles, _labels)
    xmin2, xmax2 = ax2.get_xlim()
    ymin2, ymax2 = ax2.get_ylim()
    ax2.text(xmin2 + 0.5, ymax2 - 0.2, vt2.real_tree.sentence, size=FontSize)

    # ax.legend()
    path = figSavePath  + str(vt1.vtID) + "-" + str(vt2.vtID)
    path = path + ".jpg"
    # print(path)
    plt.savefig(path)
    plt.close()

def drawComparisonGivenTreeVT(tree, vt, tree_triple_in_num, drawSchema1 = False, drawSchema2 = False, triple_index=0,
                       figSavePath="D:\\dependencyTreeGraphs\\subStructure\\"):
    # 这个函数和drawComparisonGivenTwoTrees实质上是一样的，只是给定两个VT，然后从VT中把tree和triple取出来
    print('drawComparisonGivenTreeVT画Tree和VT', tree.sentenceID, vt.vtID, triple_index)
    xLimit1, yLimit1 = computingXYLimit(tree)
    xLimit1 = int(xLimit1) + 1
    yLimit1 = int(yLimit1) + 3
    xLimit2, yLimit2 = computingXYLimit(vt.real_tree)
    xLimit2 = int(xLimit2) + 1
    yLimit2 = int(yLimit2) + 3
    xLimit = 2* max(xLimit1, xLimit2)
    yLimit = 2* max(yLimit1, yLimit2)
    # print(xLimit, yLimit)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(xLimit, yLimit))
    plt.rc('axes', unicode_minus=False)
    plt.rcParams['font.sans-serif'] = ['simhei']
    # ax.set_xlim(0, XLIMIT)
    # ax.set_ylim(0, YLIMIT)
    levelToEachNodeSize = drawNodes(ax1, tree, tree_triple_in_num, drawSchema1)
    drawAllEdges(ax1, levelToEachNodeSize, tree)
    _handles, _labels = ax1.get_legend_handles_labels()
    handles = []
    labels = []
    for i in range(len(_labels)):
        if _labels[i] not in labels:
            labels.append(_labels[i])
            handles.append(_handles[i])
        else:
            continue
    arg1Index = labels.index('arg1')
    arg2Index = labels.index('arg2')
    relIndex = labels.index('rel')
    if 'NoTriple' in labels:
        noIndex = labels.index('NoTriple')
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
    else:
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
    # print(_handles)
    # print(_labels)
    # print('************************************')
    ax1.legend(_handles, _labels)
    xmin1, xmax1 = ax1.get_xlim()
    ymin1, ymax1 = ax1.get_ylim()
    ax1.text(xmin1+0.5, ymax1-0.2, tree.sentence, size=FontSize)

    levelToEachNodeSize = drawNodes(ax2, vt.real_tree, vt.triple_in_num, drawSchema2)
    drawAllEdges(ax2, levelToEachNodeSize, vt.real_tree)
    _handles, _labels = ax2.get_legend_handles_labels()
    handles = []
    labels = []
    for i in range(len(_labels)):
        if _labels[i] not in labels:
            labels.append(_labels[i])
            handles.append(_handles[i])
        else:
            continue
    arg1Index = labels.index('arg1')
    arg2Index = labels.index('arg2')
    relIndex = labels.index('rel')
    if 'NoTriple' in labels:
        noIndex = labels.index('NoTriple')
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index], handles[noIndex]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index], labels[noIndex]]
    else:
        _handles = [handles[arg1Index], handles[relIndex], handles[arg2Index]]
        _labels = [labels[arg1Index], labels[relIndex], labels[arg2Index]]
    # print(_handles)
    # print(_labels)
    # print('************************************')
    ax2.legend(_handles, _labels)
    xmin2, xmax2 = ax2.get_xlim()
    ymin2, ymax2 = ax2.get_ylim()
    ax2.text(xmin2 + 0.5, ymax2 - 0.2, vt.real_tree.sentence, size=FontSize)

    # ax.legend()
    path = figSavePath  + str(tree.sentenceID) + "-" + str(vt.vtID) + "-" + str(triple_index)
    path = path + ".jpg"
    # print(path)
    plt.savefig(path)
    plt.close()
