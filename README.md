# ShareGPTQAExtractor-mnbvc


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [ShareGPTQAExtractor-mnbvc](#sharegptqaextractor-mnbvc)
  - [项目需求描述](#项目需求描述)
  - [使用方式](#使用方式)
    - [环境准备](#环境准备)
    - [运行方式](#运行方式)
    - [代码说明](#代码说明)
    - [原始文件示例（以\[Ejafa/GPT\_4\_with\_ShareGPT\]格式文件为例）](#原始文件示例以ejafagpt_4_with_sharegpt格式文件为例)
    - [结果示例](#结果示例)
  - [相关项目](#相关项目)

<!-- /code_chunk_output -->



## 项目需求描述

###原始数据集

- 本项目主要目的是从Trello上分享的ShareGPT语料链接中抽取中文/英文问答数据。一共5个语料：
1. [scryscan/multilingual-share](https://huggingface.co/datasets/cryscan/multilingual-share)
2. [anon8231489123/ShareGPT_Vicuna_unfiltered](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered)
3. [Ejafa/GPT_4_with_ShareGPT](https://huggingface.co/datasets/Ejafa/GPT_4_with_ShareGPT/tree/main)
4. [shareAI/ShareGPT-Chinese-English-90k](https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k/tree/main/sharegpt_jsonl)
5. baiduzhidao-train

###标准化需求说明

- 将不同格式的原始数据集，统一处理为标准格式的jsonl文件，每行对应一对问答，包含问答文本，以及同一会话下多轮问答的唯一标识和序号，详细格式附后。
- 对于每一个问答数据，其最高层次结构如下。
```json
{
    "id":"82b2834abe2ed41a26b6b06317114f8f",
    "问":"写一个超短小说",
    "答":"他们相遇，又别离。岁月如梭，情感却不减。",
    "来源":"ShareGPT",
    "元数据":{
        "create_time":"20230511 15:56:03",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段":"{\"会话\": 1, \"多轮序号\": 1, \"解析模型\": gpt4}"
    }
}
```
- jsonl文件中每一行的json基本KV说明

| KEY  | VALUE说明 |
| ------ | ---- |
|id   | 每一对问答的唯一标识，使用json串的md5作为唯一标识id |
|问   | 问的文本 |
|答   | 答的文本 |
|来源   | 固定为'ShareGPT' |
|元数据   | 包含创建时间、问题明细、回答明细、扩展字段 |

- 元数据中每一项的KV说明

| KEY  | VALUE说明 |
| ------ | ---- |
|create_time   | 问答创建时间，格式为`%Y%m%d %H:%M:%S` |
|问题明细   | 原始语料中问的来源，例如 "from": "human" |
|回答明细   | 原始语料中答的来源，例如 "from": "gpt" |
|扩展字段   | 包含会话的唯一标识和本条在会话中的序号，以及解析模型 |

- 扩展字段中每一项的KV说明

| KEY  | VALUE说明 |
| ------ | ---- |
|会话   | 会话的唯一标识，例如 "会话": "yOKd88p" |
|多轮序号   | 本条在会话中的序号，例如 "多轮序号": 1 |
|解析模型   | 用于标识原始语料的来源，例如 "解析模型": "gpt4" |
|其他。。等等   | 语料中问答相关的其他补充信息字段 |

- 注意：**如果有问没答，保持答为空。如果只有答案没有问，直接丢弃答。**

## 使用方式

### 环境准备

1. 下载本项目
```shell
git clone ShareGPTQAExtractor-mnbvc
```
2. 进入目录并安装依赖
```shell
cd ShareGPTQAExtractor-mnbvc
pip install -r requirements.txt
```

### 运行方式

通过以下命令将FILE文件转化并输出到以`ShareGPT`为开头的结果文件中。
```shell
python sharegpt_extract.py FILE -m MODEL
```

以上命令将输出时间戳结果文件例子`shareGPT_gpt4_2023-09-17-00-21-06.jsonl`。
模型和原始语料的对应关系如下：

| MODEL  | 对应原始语料 |
| ------ | ---- |
|multilang   | [scryscan/multilingual-share](https://huggingface.co/datasets/cryscan/multilingual-share) |
| vicuna   | [anon8231489123/ShareGPT_Vicuna_unfiltered](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered)         |
| gpt4   | [Ejafa/GPT_4_with_ShareGPT](https://huggingface.co/datasets/Ejafa/GPT_4_with_ShareGPT/tree/main)       |
| common_en/common_zh   | [shareAI/ShareGPT-Chinese-English-90k](https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k/tree/main/sharegpt_jsonl)      |
| baiduzhidao   |  shareGPT的中文问答       |

### 代码说明

- `sharegpt_extract.py` 入口程序
- `schema.py` 输出json模板

##文件示例

### 原始文件示例（以[Ejafa/GPT_4_with_ShareGPT]格式文件为例）

```json
  {
    "id": "yOKd88p",
    "conversations": [
      {
        "from": "human",
        "value": "Can you make me a Shakespearean script about a girl who has tummy troubles and can\u2019t fart not matter how hard she tries- so they think she is a witch"
      },
      {
        "from": "gpt",
        "value": "Sure, here's a Shakespearean script about a girl who c..."
      },
      {
        "from": "human",
        "value": "Can you change Mary\u2019s name to Katy"
      },
      {
        "from": "gpt",
        "value": "Certainly! Here's the revised script:\n\nAct I, Scene I\n\nEnter KATY,..."
      }
    ]
  }
```

### 结果示例

```json
{
    "id": "82b2834abe2ed41a26b6b06317114f8f",
    "问": "Can you make me a Shakespearean script about a girl who has tummy troubles and can\u2019t fart not matter how hard she tries- so they think she is a witch",
    "答": "Sure, here's a Shakespearean script about a girl who c...",
    "来源": "ShareGPT",
    "元数据": {
        "create_time": "20230517 10:41:58",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段": {
                    "会话": "yOKd88p",
                    "多轮序号": 1,
                    "解析模型": "gpt4"
                    }
    }
}
{
    "id": "82b2834abe2ed41a26bbbbbbbbbbbbbbbb",
    "问": "Can you change Mary\u2019s name to Katy",
    "答": "Certainly! Here's the revised script:\n\nAct I, Scene I\n\nEnter KATY,...",
    "来源": "ShareGPT",
    "元数据": {
        "create_time": "20230517 10:41:58",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段": {
                    "会话": "yOKd88p",
                    "多轮序号": 2,
                    "解析模型": "gpt4"
                    }
    }
},
```
###补充说明

**上面的格式方便查看，最终输出到文件仍然为jsonl的规范，如下：**
```json
{"id": "82b...", "问": "Can you make me a ...", "答": "Sure...", "来源": "ShareGPT", "元数据": {"create_time": "20230517 10:41:58",...}}
{"id": "82b...", "问": "Can you make me a ...", "答": "Sure...", "来源": "ShareGPT", "元数据": {"create_time": "20230517 10:41:58",...}}
```

## 相关项目

[MNBVC](https://github.com/esbatmop/MNBVC)
[WikiHowQAExtractor-mnbvc](https://github.com/wanicca/WikiHowQAExtractor-mnbvc)
