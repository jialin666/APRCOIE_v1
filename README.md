# APRCOIE_v1
## Introduction
**APRCOIE** means Auto Patterns Recognition for Chinese Open Information Extraction, which is a open information extraction model for Chinese text.\
APRCOIE achieved the best performance on the latest Open Information Extraction benchmark BenchIE [1]. \
This is the code and data of APRCOIE.
## Usage
### Training
The train.py file in the usage folder demonstrates how to conduct training. If you do not have additional annotated data, simply run train.py to complete the training process.\
You will get two model files in the data folder: model.obj, model_att.obj. \
If you have your own annotated data, you need to ensure that the data follows the format as shown below: words, dependency, POS, triples which represent annotation result in number.\ 
An example is provided below: words = ["美国", "有", "50", "个", "州"] \
dependency = [(1, 2, 'SBV'), (2, 0, 'HED'), (3, 4, 'ATT'), (4, 5, 'ATT'), (5, 2, 'VOB'), (6, 2, 'WP')] \
POS = ['ns', 'v', 'm', 'q', 'n', 'wp'], \
triples_in_number = [[[0], [1], [2, 3, 4]]] (represents the only triple: [[['美国'], ['有'], ['50', '个', '州']]]) \
Then these data organized as a dictionary as shown in the lien 20 in train.py.
### Predicting
> [1] K. Gashteovski, M. Yu, B. Kotnis, C. Lawrence, M. Niepert, G. Glavas, BenchIE: A framework for multi-faceted fact-based open information extraction evaluation, Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, ACL 2022, pp. 4472-4490.



