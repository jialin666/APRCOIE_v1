# APRCOIE_v1
## Introduction
**APRCOIE** means Auto Patterns Recognition for Chinese Open Information Extraction, which is a open information extraction model for Chinese text.  

APRCOIE achieves the best performance on the latest Open Information Extraction benchmark BenchIE [1].  

This repository contains the code and annatated dataset of APRCOIE model. <br>
## Usage
### Training  

The train.py file in the usage folder demonstrates how to conduct training. If you do not have additional annotated data, simply run train.py to complete the training process.<br>

You will get two model files in the data folder: model.obj, model_att.obj. <br>

If you have your own annotated data, it's important to ensure that the data adheres to the following format: : words, dependency, POS, triples which represent annotation result in number. <br>

An example is provided below: <br>
&emsp; sentence: 美国有50个州。<br>
&emsp; words = ["美国", "有", "50", "个", "州", "。"] <br>
&emsp; dependency = [(1, 2, 'SBV'), (2, 0, 'HED'), (3, 4, 'ATT'), (4, 5, 'ATT'), (5, 2, 'VOB'), (6, 2, 'WP')] <br>
&emsp; POS = ['ns', 'v', 'm', 'q', 'n', 'wp'], \
&emsp; triples_in_number = [[[0], [1], [2, 3, 4]]] (represents the only triple: [[['美国'], ['有'], ['50', '个', '州']]]) <br>
Then these data organized as a dictionary as shown in the line 20 in train.py.  

### Predicting
The file predict.py in usage folder shows how to extract triples. For a target sentence, it firstly conducts word segmentation, POS tagging, dependency parsing. We adopt LTP 4 [2] as the natural language processing tool here. Then it constructs an instance of class Tree, named test_tree, of the target sentence, loads the model, and passes all of these to extraction_regular and extraction_att functions of MATRIX module. 
## Contact
Jialin Hua (华佳林), nhma0004@gmail.com
## References
> [1] K. Gashteovski, M. Yu, B. Kotnis, C. Lawrence, M. Niepert, G. Glavas, BenchIE: A framework for multi-faceted fact-based open information extraction evaluation, Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, ACL 2022, pp. 4472-4490. <br>
> [2] W. Che, Y. Feng, L. Qin, T. Liu, N-LTP: An Open-source Neural Language Technology Platform for Chinese, Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing: System Demonstrations, EMNLP 2021, pp. 42-49.



