import json
from datetime import datetime

class ShareGPTQASchema:

    def __init__(self, id, question, answer, session, round_number, format_type):
        self.source = "ShareGPT"
        self.create_time = datetime.now().strftime("%Y%m%d %H:%M:%S")
        self.question_detail = "\"from\": \"human\""
        self.answer_detail = "\"from\": \"gpt\""
        self.format_type = format_type
        # 扩展字段
        self.extended_field = "{\"会话\": " + session + ", \"多轮序号\": " + str(round_number) + "}"
        self.session = session
        self.round_number = round_number

    # 公共方法来设置问答信息
    def set_qa(self, id, question, answer, session, round_number, format_type):
        self.id = id
        self.question = question
        self.answer = answer
    
    # 根据不同模型格式来设置通用字段
    def set_extended_field(self, session, round_number, format_type):
        format_type

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


json_str = ShareGPTQASchema(0, "Can you make me a Shakespearean script about a girl who has tummy troubles and can't fart not matter how hard she tries- so they think she is a witch",
                "Sure, here's a Shakespearean script about a girl who c...", "ShareGPT", 1).to_json()
# print(json_str)
