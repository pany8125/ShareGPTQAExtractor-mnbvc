import json
from datetime import datetime

class ShareGPTQASchema:

    def __init__(self, id, question, answer, question_detail, answer_detail, session, round_number, model, other_field):
        self.id = id
        self.question = question
        self.answer = answer
        self.source = "ShareGPT"
        self.create_time = datetime.now().strftime("%Y%m%d %H:%M:%S")
        self.question_detail = question_detail 
        self.answer_detail = answer_detail 
        # 扩展字段
        self.extended_field = "{\"会话\": " + session + ", \"多轮序号\": " + str(round_number) + ", \"解析模型\": " + model + other_field + "}"

    def to_json(self):
        data = {
            "id": self.id,
            "问": self.question,
            "答": self.answer,
            "来源": self.source,
            "元数据": {
                "create_time": self.create_time,
                "问题明细": self.question_detail,
                "回答明细": self.answer_detail,
                "扩展字段": self.extended_field
            }
        }
        # jsonl的库处理下
        # 扩展字段直接json dump
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


# json_str = ShareGPTQASchema(0, "Can you make me a Shakespearean script about a girl who has tummy troubles and can't fart not matter how hard she tries- so they think she is a witch",
#                 "Sure, here's a Shakespearean script about a girl who c...", "ShareGPT", 1).to_json()
# print(json_str)
unique_id = 0
question = 'aaa'
i = 5
question_detail = "\"from\": \"human\""
answer_detail = "\"from\": \"gpt\""
id = 'aaa'
model = 'gpt4'
gpt4_json = ShareGPTQASchema(unique_id, question, '', question_detail, answer_detail, id, i, model, '')
gpt4_json.source = 'xxx'
# print(gpt4_json.to_json()) 