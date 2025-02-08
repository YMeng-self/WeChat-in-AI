"""
使用方法

导入全部参数
from config import *

导入指定参数 DEEPSEEK_API_URL
from config import DEEPSEEK_API_URL
"""

### AI 参数配置 ###

# 硅基流动
# API
DEEPSEEK_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
# Token
DEEPSEEK_API_KEY = 'sk-'

# 模型
MODEL = 'deepseek-ai/DeepSeek-V3'
# MODEL = 'deepseek-ai/DeepSeek-R1'
# MODEL = 'Pro/deepseek-ai/DeepSeek-R1'
# MODEL = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B'
# MODEL = 'deepseek-ai/DeepSeek-R1-Distill-Llama-8B'
# MODEL = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B'
# MODEL = 'Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B'


# 提示词
# prompt 提示词
# 获取程序根目录
import os 

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# 读取 prompt.md 文件内容
with open(os.path.join(ROOT_DIR, 'prompt.md'), 'r', encoding='utf-8') as file:
    PROMPT_CONTENT = file.read()


# 是否以流的形式返回结果。
# 如果设置为True，模型会逐步生成文本并实时返回；
# 如果为False，则等待整个文本生成完毕后再一次性返回。
STREAM = False

# 生成文本的最大长度（以token为单位）。一个token通常对应一个单词或标点符号。
MAX_TOKEN = 2000

# 停止生成的条件。当模型生成到指定的字符串时，会停止生成。
# 在这个例子中，"null"是一个占位符，表示没有特定的停止条件。
STOP = ["null"]

# 控制生成文本的随机性。较高的值（接近1）会使输出更加随机和多样化，较低的值（接近0）会使输出更加确定和保守。
TEMPERATURE = 1.3

# 核采样方法中的参数，用于控制生成文本的多样性。它指定了选择下一个词的概率分布的累积概率阈值。
# 例如，top_p=0.7意味着只考虑累计概率达到70%的词。
TOP_P = 0.7
# 另一种控制生成文本多样性的方法。它指定了在生成下一个词时，只考虑前k个最可能的词。在这个例子中，k=50。
TOP_K = 50
# 频率惩罚系数。用于减少生成文本中重复出现的词。较高的值会增加对重复词的惩罚，使生成的文本更多样化。
FREQUENCY_PENALTY = 0.5
# 生成文本的数量。在这个例子中，n=1表示只生成一个文本。
N = 1

### 微信的参数配置 ###

# 监听消息列表
PERSON_LISTEN_LIST = ['Y1010']
GROUP_LISTEN_LIST = ['']



### 日志参数配置 ###

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)