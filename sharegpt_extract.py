# -*- coding: utf-8 -*-
# 脚本设置使用utf-8编码

from datetime import datetime
import json
from enum import Enum
import schema
import hashlib
import logging

# 配置日志记录
logging.basicConfig(
    filename='shareGTP_log_file.log',  # 指定日志文件的名称
    level=logging.INFO,  # 指定日志级别（INFO、WARNING、ERROR、CRITICAL等）
    format='%(asctime)s [%(levelname)s]: %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 日期和时间格式
)

# 定义一个枚举类
class Json_str(Enum):
    JSON_START = "{"
    ID = '"id":'
    CONVERSATION_START = '"conversations":'
    CONVERSATION_ALL = '"conversations": []'
    CONVERSATION_END = ']'
    JSON_END = '},'
    JSON_END_END = '}'
    NONE = ''

# 读取文件
# file_path_all = 'final_data_sample_230706test.json'  # 替换为实际文件路径

# 获取每一段对话，输入到json中处理
def process_json_file_gpt4(file_path, write_file, start_line=1, model='gpt4'):
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
            # 如果json_len大于1000，就退出
            if json_len > 1000:
                print(f"Line {line_number}, json len > 1000, exit!")  # json检测失败
                break
            this_line = line.strip()
            # 最后的逻辑放到前面，避免重复判断
            if json_str_flag == Json_str.CONVERSATION_END.value or json_str_flag == Json_str.CONVERSATION_ALL.value:
                if this_line == Json_str.JSON_END.value or this_line == Json_str.JSON_END_END.value:
                    print(f"Line {line_number}, json end!")  # json解析开始
                    buffer += '}'
                    # 重置状态
                    json_str_flag = Json_str.NONE.value
                    json_len = 0
                    if process_json_gpt4(buffer, write_file, model):
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
                if this_line.startswith(Json_str.CONVERSATION_ALL.value):
                    print(f"Line {line_number}, conversations all detected!")
                    json_str_flag = Json_str.CONVERSATION_ALL.value
                    buffer += this_line
                elif this_line.startswith(Json_str.CONVERSATION_START.value):
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
            # 撒分支都没走进去
            print(f"json parse error!")  # json检测失败
            print(f"Line {line_number}, error!")  # json检测失败
            print(f"parse stage: {json_str_flag}, json str: {buffer}")

def process_json_gpt4(json_str, write_file=None, model='gpt4'):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        id = json_data['id']
        #用json_data的md5值作为id
        unique_id = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        question_detail = "\"from\": \"human\""
        answer_detail = "\"from\": \"gpt\""
        other_field = ''
        conversation = json_data['conversations']
        # 打印conversation的长度，并加上说明
        print(f"conversation length: {len(conversation)}")
        # 标识conversation中的对话数以及开始标记
        i = 1
        conversation_start = False
        question = ''
        # 循环处理conversation中的每一个json，如果json中的from不是human或gpt，就退出
        while len(conversation) > 0:
            if conversation[0]['from'] != 'human' and conversation[0]['from'] != 'gpt':
                unknown_q_or_a = conversation.pop(0)
                # 记录并继续
                logging.error(f"unknown conversation: {unknown_q_or_a}")
                continue
            q_or_a = conversation.pop(0)
            if q_or_a['from'] == 'gpt':
                # 如果是gpt，且前面没有human，就丢弃
                if conversation_start == False:
                    continue
                # 如果是gpt，且前面有human，就生成json
                else:
                    answer = q_or_a['value']
                    # 生成json
                    json_str = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, id, i, model, other_field).to_json()
                    write_file.write(json_str)
                    write_file.write('\n')
                    # 对话重置且问答序号加1
                    conversation_start = False
                    i += 1
                    continue
            # 如果是human，分两种情况。如果前面也是human，先将前面的human作为单独的问生成json，本次作为新一轮的问答；否则，就将human作为问暂存
            if q_or_a['from'] == 'human':
                if conversation_start == False:
                    question = q_or_a['value']
                    conversation_start = True
                    continue
                else:
                    # 生成json
                    json_str = schema.ShareGPTQASchema(unique_id, question, '', question_detail, answer_detail, id, i, model, other_field).to_json()
                    write_file.write(json_str)
                    write_file.write('\n')
                    question = q_or_a['value']
                    # 对话重置且问答序号加1
                    conversation_start = False
                    i += 1
                    continue
        # 如果最后一个是human，就生成json
        if conversation_start == True:
            # 生成json
            json_str = schema.ShareGPTQASchema(unique_id, question, '', id, i).to_json()
            write_file.write(json_str)
            write_file.write('\n')
# '''
#     如果有问没答，保持答为空。如果只有答案没有问，直接丢弃答。
#     注释之前的处理方式
#         # 判断conversation的长度是否为偶数，如果是奇数，就退出
#         if(len(conversation) % 2 != 0):
#             return False
#         for i in range(int(len(conversation)/2)):
#             # 如果是第一个元素，就是问题
#             if(conversation[i*2]['from'] != 'human'):
#                 return False
#             # 如果是第二个元素，就是答案
#             if(conversation[i*2+1]['from'] != 'gpt'):
#                 return False
#             # 如果是第一个元素，就是问题
#             question = conversation[i*2]['value']
#             # 如果是第二个元素，就是答案
#             answer = conversation[i*2+1]['value']
#             # lang = 'not_en_or_zh'
#             # # 确认是否英文或中文，可能带有标点符号
#             # if re.match(r'^[a-zA-Z0-9\.\,\?\!\s]+$', question) is not None:
#             #     lang = 'en'
#             # elif re.match(r'^[\u4e00-\u9fa5\.\,\?\!\s]+$', question) is not None:
#             #     lang = 'zh'
#             # 生成json
#             json_str = schema.ShareGPTQASchema(unique_id, question, answer, id, i+1).to_json()
#             write_file.write(json_str)
#             write_file.write('\n')
# '''
        return True
    except json.JSONDecodeError:
        print("JSONDecodeError")
        return False

# 获取每一段对话，输入到json中处理
def process_json_file_multilang(file_path, write_file, start_line=1):
    with open(file_path, 'r', encoding='utf-8') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        for line_number, line in enumerate(f, start=start_line):
            # 打印迭代信息
            # print(f"Line {line_number}: {line}")
            this_line = line.strip()
            if process_json_multilang(this_line, write_file):
                this_line = ''
                continue
            else:
                print(f"Line {line_number}, error!")  # json检测失败
                print(f"json str: {this_line}")

def process_json_multilang(json_str, write_file=None):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        print(json_data)
        # id = json_data['id']
        # #用json_data的md5值作为id
        # unique_id = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        # conversation = json_data['conversations']
        # # 打印conversation的长度，并加上说明
        # print(f"conversation length: {len(conversation)}")
        # # 标识conversation中的对话数以及开始标记
        # i = 1
        # conversation_start = False
        # question = ''
        # # 循环处理conversation中的每一个json，如果json中的from不是human或gpt，就退出
        # while len(conversation) > 0:
        #     if conversation[0]['from'] != 'human' and conversation[0]['from'] != 'gpt':
        #         unknown_q_or_a = conversation.pop(0)
        #         # 记录并继续
        #         logging.error(f"unknown conversation: {unknown_q_or_a}")
        #         continue
        #     q_or_a = conversation.pop(0)
        #     if q_or_a['from'] == 'gpt':
        #         # 如果是gpt，且前面没有human，就丢弃
        #         if conversation_start == False:
        #             continue
        #         # 如果是gpt，且前面有human，就生成json
        #         else:
        #             answer = q_or_a['value']
        #             # 生成json
        #             json_str = schema.ShareGPTQASchema(unique_id, question, answer, id, i).to_json()
        #             write_file.write(json_str)
        #             write_file.write('\n')
        #             # 对话重置且问答序号加1
        #             conversation_start = False
        #             i += 1
        #             continue
        #     # 如果是human，分两种情况。如果前面也是human，先将前面的human作为单独的问生成json，本次作为新一轮的问答；否则，就将human作为问暂存
        #     if q_or_a['from'] == 'human':
        #         if conversation_start == False:
        #             question = q_or_a['value']
        #             conversation_start = True
        #             continue
        #         else:
        #             # 生成json
        #             json_str = schema.ShareGPTQASchema(unique_id, question, '', id, i).to_json()
        #             write_file.write(json_str)
        #             write_file.write('\n')
        #             question = q_or_a['value']
        #             # 对话重置且问答序号加1
        #             conversation_start = False
        #             i += 1
        #             continue
        # # 如果最后一个是human，就生成json
        # if conversation_start == True:
        #     # 生成json
        #     json_str = schema.ShareGPTQASchema(unique_id, question, '', id, i).to_json()
        #     write_file.write(json_str)
        #     write_file.write('\n')
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
    # model：
    #   gpt4：https://huggingface.co/datasets/Ejafa/GPT_4_with_ShareGPT/tree/main
    #   common：https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k/tree/main/sharegpt_jsonl
    #   multilang：https://huggingface.co/datasets/cryscan/multilingual-share/tree/main
    #   vicuna：https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/tree/main
    parser.add_argument("-m","--model",type=str,default='gpt4',help="multi model parse")
    args = parser.parse_args()
    with open(f'{args.output}_{args.model}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.jsonl', 'w', encoding='utf-8') as of:
        if args.model == 'vicuna' or args.model == 'gpt4':
            # 调用函数来处理 JSON 文件，默认从第1行开始读取
            process_json_file_gpt4(args.source_files, of, args.start_line, args.model)
        elif args.model == 'multilang':
            # 调用函数来处理 JSON 文件，默认从第1行开始读取
            process_json_file_multilang(args.source_files, of, args.start_line)
        elif args.model == 'common':
            # 调用函数来处理 JSON 文件，默认从第1行开始读取
            process_json_file_common(args.source_files, of, args.start_line)
            # TODO：添加不同类型格式的方法适配 230914