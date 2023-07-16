# ShareGPTQAExtractor-mnbvc

## 项目描述

- 本项目主要目的是从Trello上分享的ShareGPT语料链接中抽取中文/英文问答数据。一共3个语料：
1. https://huggingface.co/datasets/cryscan/multilingual-share
2. https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered
3. https://huggingface.co/datasets/Ejafa/GPT_4_with_ShareGPT/tree/main
- 处理结果为jsonl文件，每行对应一对问答，包含问答文本，以及同一会话下多轮问答的唯一标识和序号，详细格式附后。

## 环境

1. 下载本项目
```
git clone ShareGPTQAExtractor-mnbvc
```
2. 进入目录并安装依赖
```
cd ShareGPTQAExtractor-mnbvc
pip install -r requirements.txt
```

## 用法

通过以下命令将FILE文件转化并输出到以`ShareGPT`为名称的结果文件中。
```shell
python sharegpt_extract.py FILE
```

以上命令将输出时间戳结果文件例子`shareGPT_2023-07-17-00-30-43.jsonl`。

## 注意

1. 

## 代码说明

- `sharegpt_extract.py` 入口程序
- `sharegpt_parser.py` ShareGPT解析器


## 输出jsonl文件格式

1. 每个jsonl文件，其大小略大于500MB。每行是一条问答数据，对应ShareGPT一个会话（即**conversations**，下同）中的一个问答。
2. 对于每一个问答数据，其最高层次结构如下。
```json
{
    "id":123456,
    "问":"写一个超短小说",
    "答":"他们相遇，又别离。岁月如梭，情感却不减。",
    "来源":"ShareGPT",
    "元数据":{
        "create_time":"20230511 15:56:03",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段":""
    }
}
```
3. 在ShareGPT语料中，`"扩展字段"`一共两个字段，会话的唯一标识和本条在会话中的序号，示例如下：
```json
    {
    "会话": "yOKd88p",
    "多轮序号": 1
    }
```


## 原始文件示例

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

## 结果示例

```json
{
    "id": 0,
    "问": "Can you make me a Shakespearean script about a girl who has tummy troubles and can\u2019t fart not matter how hard she tries- so they think she is a witch",
    "答": "Sure, here's a Shakespearean script about a girl who c...",
    "来源": "ShareGPT",
    "元数据": {
        "create_time": "20230517 10:41:58",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段": {
                    "会话": "yOKd88p",
                    "多轮序号": 1
                    }
    }
}
{
    "id": 1,
    "问": "Can you change Mary\u2019s name to Katy",
    "答": "Certainly! Here's the revised script:\n\nAct I, Scene I\n\nEnter KATY,...",
    "来源": "ShareGPT",
    "元数据": {
        "create_time": "20230517 10:41:58",
        "问题明细":"\"from\": \"human\"",
        "回答明细":"\"from\": \"gpt\"",
        "扩展字段": {
                    "会话": "yOKd88p",
                    "多轮序号": 2
                    }
    }
},
```

**补充说明：上面的格式方便查看，最终输出到文件仍然为jsonl的规范，如下：**
```json
{"id": 0, "问": "Can you make me a ...", "答": "Sure...", "来源": "ShareGPT", "元数据": {"create_time": "20230517 10:41:58",...}}
{"id": 0, "问": "Can you make me a ...", "答": "Sure...", "来源": "ShareGPT", "元数据": {"create_time": "20230517 10:41:58",...}}
```

## 相关项目

[MNBVC](https://github.com/esbatmop/MNBVC)
[WikiHowQAExtractor-mnbvc](https://github.com/wanicca/WikiHowQAExtractor-mnbvc)
