# -*- coding: utf-8 -*-
# 脚本设置使用utf-8编码

from datetime import datetime
import json
from enum import Enum
import schema
import re

# 定义一个枚举类
class Json_str(Enum):
    JSON_START = "{"
    ID = '"id":'
    CONVERSATION_START = '"conversations":'
    CONVERSATION_END = ']'
    JSON_END = '},'
    JSON_END_END = '}'
    NONE = ''

# 读取文件
# file_path_all = 'final_data_sample_230706test.json'  # 替换为实际文件路径

# 获取每一段对话，输入到json中处理
def process_json_file(file_path, write_file, start_line=1):
    with open(file_path, 'r', encoding='utf-8') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        buffer = ""
        json_len = 0
        json_str_flag = Json_str.NONE.value # 检测到json串时修改为对应状态，检测完成修改回NONE
        for line_number, line in enumerate(f, start=start_line):
            # 打印迭代信息
            # print(f"Line {line_number}: {line}")
            # 如果json_len大于10，就退出
            if json_len > 10:
                break
            this_line = line.strip()
            if json_str_flag == Json_str.NONE.value:
                if this_line == "[":
                    print(f"Line {line_number}, start of text!")  # json检测文件开始
                    continue
                elif this_line == "]":
                    print(f"Line {line_number}, end of text!")  # json检测还没开始就到末尾了
                    break 
                elif this_line != "{":
                    print(f"Line {line_number}, error!")  # json检测失败
                    break
                elif this_line == Json_str.JSON_START.value:
                    print(f"Line {line_number}, start parsing json!")  # json解析开始
                    json_str_flag = Json_str.JSON_START.value
                    buffer += this_line
                    continue
                else:
                    print(f"Line {line_number}, error!")  # json检测失败
                    print(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.JSON_START.value:
                if this_line.startswith(Json_str.ID.value):
                    print(f"Line {line_number}, id detected!")  # json解析开始
                    json_str_flag = Json_str.ID.value
                    buffer += this_line
                    continue
                else:
                    print(f"Line {line_number}, error!")  # json检测失败
                    print(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.ID.value:
                if this_line.startswith(Json_str.CONVERSATION_START.value):
                    print(f"Line {line_number}, conversations detected!")  # json解析开始
                    json_str_flag = Json_str.CONVERSATION_START.value
                    buffer += this_line
                    continue
                else:
                    print(f"Line {line_number}, error!")  # json检测失败
                    print(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.CONVERSATION_START.value:
                if this_line == Json_str.CONVERSATION_END.value:
                    print(f"Line {line_number}, conversations end!")  
                    json_str_flag = Json_str.CONVERSATION_END.value
                    buffer += this_line
                    continue
                else:
                    print(f"Line {line_number}, conversations parsing!")
                    # TODO：检测下buffer长度，以免数据异常
                    buffer += this_line
                    continue
            if json_str_flag == Json_str.CONVERSATION_END.value:
                if this_line == Json_str.JSON_END.value or this_line == Json_str.JSON_END_END.value:
                    print(f"Line {line_number}, json end!")  # json解析开始
                    json_str_flag = Json_str.NONE.value
                    buffer += '}'
                    if process_json(buffer, write_file):
                        buffer = ''
                        json_len += 1
                        continue
                    else:
                        print(f"Line {line_number}, error!")  # json检测失败
                        print(f"parse stage: {json_str_flag}, json str: {buffer}")
                        break
                else:
                    print(f"Line {line_number}, error!")  # json检测失败
                    print(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            # 撒分支都没走进去
            print(f"Line {line_number}, error!")  # json检测失败
            print(f"parse stage: {json_str_flag}, json str: {buffer}")

def process_json(json_str, write_file=None):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        id = json_data['id']
        conversation = json_data['conversations']
        # 打印conversation的长度，并加上说明
        print(f"conversation length: {len(conversation)}")
        # 判断conversation的长度是否为偶数，如果是奇数，就退出
        if(len(conversation) % 2 != 0):
            return False
        for i in range(int(len(conversation)/2)):
            # 如果是第一个元素，就是问题
            if(conversation[i*2]['from'] != 'human'):
                return False
            # 如果是第二个元素，就是答案
            if(conversation[i*2+1]['from'] != 'gpt'):
                return False
            # 如果是第一个元素，就是问题
            question = conversation[i*2]['value']
            # 如果是第二个元素，就是答案
            answer = conversation[i*2+1]['value']
            lang = 'not_en_or_zh'
            # 确认是否英文或中文，可能带有标点符号
            if re.match(r'^[a-zA-Z0-9\.\,\?\!\s]+$', question) is not None:
                lang = 'en'
            elif re.match(r'^[\u4e00-\u9fa5\.\,\?\!\s]+$', question) is not None:
                lang = 'zh'
            # 生成json
            json_str = schema.ShareGPTQASchema(id, question, answer, id, i+1, lang).to_json()
            write_file.write(json_str)
            write_file.write('\n')
        return True
    except json.JSONDecodeError:
        print("JSONDecodeError")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse shareGPT into QA data.")
    parser.add_argument("source_files",type=str, default="final_data_sample_230706test.json", help="文件名")
    parser.add_argument("-o","--output",type=str, default="shareGPT",help="output file name (without extension)")
    parser.add_argument("-l","--start_line",type=int,default=1,help="read start line")
    args = parser.parse_args()
    with open(f'{args.output}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.jsonl', 'w', encoding='utf-8') as of:
        # 调用函数来处理 JSON 文件，默认从第1行开始读取
        process_json_file(args.source_files, of, args.start_line)