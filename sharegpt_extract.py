# -*- coding: utf-8 -*-
# 脚本设置使用utf-8编码

from datetime import datetime
import json
from enum import Enum
import schema
import hashlib
import logging
import re

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
    LANG = '"lang":'
    TEXT = '"text":'
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
            logging.debug(f"Line {line_number}: {line}")
            # 如果json_len大于1000，就退出
            if json_len > 1000:
                logging.error(f"Line {line_number}, json len > 1000, exit!")  # json检测失败
                break
            this_line = line.strip()
            # 最后的逻辑放到前面，避免重复判断
            if json_str_flag == Json_str.CONVERSATION_END.value or json_str_flag == Json_str.CONVERSATION_ALL.value:
                if this_line == Json_str.JSON_END.value or this_line == Json_str.JSON_END_END.value:
                    logging.debug(f"Line {line_number}, json end!")  # json解析开始
                    buffer += '}'
                    # 重置状态
                    json_str_flag = Json_str.NONE.value
                    json_len = 0
                    if process_json_gpt4(buffer, write_file, model):
                        buffer = ''
                        json_len += 1
                        continue
                    else:
                        logging.error(f"Line {line_number}, error!")  # json检测失败
                        logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                        break
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.NONE.value:
                if this_line == "[":
                    logging.debug(f"Line {line_number}, start of text!")  # json检测文件开始
                    continue
                elif this_line == "]":
                    logging.debug(f"Line {line_number}, end of text!")  # json检测还没开始就到末尾了
                    break 
                elif this_line != "{":
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    break
                elif this_line == Json_str.JSON_START.value:
                    logging.debug(f"Line {line_number}, start parsing json!")  # json解析开始
                    json_str_flag = Json_str.JSON_START.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.JSON_START.value:
                if this_line.startswith(Json_str.ID.value):
                    logging.debug(f"Line {line_number}, id detected!")  # json解析开始
                    json_str_flag = Json_str.ID.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.ID.value:
                if this_line.startswith(Json_str.CONVERSATION_ALL.value):
                    logging.debug(f"Line {line_number}, conversations all detected!")
                    json_str_flag = Json_str.CONVERSATION_ALL.value
                    buffer += this_line
                elif this_line.startswith(Json_str.CONVERSATION_START.value):
                    logging.debug(f"Line {line_number}, conversations detected!")  # json解析开始
                    json_str_flag = Json_str.CONVERSATION_START.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.CONVERSATION_START.value:
                if this_line == Json_str.CONVERSATION_END.value:
                    logging.debug(f"Line {line_number}, conversations end!")  
                    json_str_flag = Json_str.CONVERSATION_END.value
                    buffer += this_line
                    continue
                else:
                    logging.debug(f"Line {line_number}, conversations parsing!")
                    # TODO：检测下buffer长度，以免数据异常
                    buffer += this_line
                    continue
            # 撒分支都没走进去
            logging.error(f"json parse error!")  # json检测失败
            logging.error(f"Line {line_number}, error!")  # json检测失败
            logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")

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
        logging.debug(f"conversation length: {len(conversation)}")
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
            json_str = schema.ShareGPTQASchema(unique_id, question, '', question_detail, answer_detail, id, i, model, other_field).to_json()
            write_file.write(json_str)
            write_file.write('\n')
        return True
    except json.JSONDecodeError:
        logging.error("JSONDecodeError")
        return False

# 获取每一段对话，输入到json中处理
def process_json_file_multilang(file_path, write_file, start_line=1, model='multilang'):
    with open(file_path, 'r', encoding='utf-8') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        buffer = ""
        json_len = 0
        json_str_flag = Json_str.NONE.value # 检测到json串时修改为对应状态，检测完成修改回NONE
        for line_number, line in enumerate(f, start=start_line):
            # 打印迭代信息
            logging.debug(f"Line {line_number}: {line}")
            # 如果json_len大于1000，就退出
            if json_len > 1000:
                logging.error(f"Line {line_number}, json len > 1000, exit!")  # json检测失败
                break
            this_line = line.strip()
            # 最后的逻辑放到前面，避免重复判断
            if json_str_flag == Json_str.TEXT.value:
                if this_line == Json_str.JSON_END.value or this_line == Json_str.JSON_END_END.value:
                    logging.debug(f"Line {line_number}, json end!")  # json解析开始
                    buffer += '}'
                    # 重置状态
                    json_str_flag = Json_str.NONE.value
                    json_len = 0
                    if process_json_multilang(buffer, write_file, model):
                        buffer = ''
                        json_len += 1
                        continue
                    else:
                        logging.error(f"Line {line_number}, error!")  # json检测失败
                        logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                        break
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.NONE.value:
                if this_line == "[":
                    logging.debug(f"Line {line_number}, start of text!")  # json检测文件开始
                    continue
                elif this_line == "]":
                    logging.debug(f"Line {line_number}, end of text!")  # json检测还没开始就到末尾了
                    break 
                elif this_line != "{":
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    break
                elif this_line == Json_str.JSON_START.value:
                    logging.debug(f"Line {line_number}, start parsing json!")  # json解析开始
                    json_str_flag = Json_str.JSON_START.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.JSON_START.value:
                if this_line.startswith(Json_str.ID.value):
                    logging.debug(f"Line {line_number}, id detected!")  # json解析开始
                    json_str_flag = Json_str.ID.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.ID.value:
                if this_line.startswith(Json_str.LANG.value):
                    logging.debug(f"Line {line_number}, lang detected!")
                    json_str_flag = Json_str.LANG.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            if json_str_flag == Json_str.LANG.value:
                if this_line.startswith(Json_str.TEXT.value):
                    logging.debug(f"Line {line_number}, text detected!")  
                    json_str_flag = Json_str.TEXT.value
                    buffer += this_line
                    continue
                else:
                    logging.error(f"Line {line_number}, error!")  # json检测失败
                    logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")
                    break
            # 撒分支都没走进去
            logging.error(f"json parse error!")  # json检测失败
            logging.error(f"Line {line_number}, error!")  # json检测失败
            logging.error(f"parse stage: {json_str_flag}, json str: {buffer}")


def process_json_multilang(json_str, write_file=None, model='multilang'):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        id = json_data['id']
        #用json_data的md5值作为id
        unique_id = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        question_detail = "<|user|>"
        answer_detail = "<|bot|>"
        other_field = ", \"lang\": \""+ json_data['lang'] +"\""
        conversation = json_data['text']
        logging.debug(f"conversation: {json_data['text']}")
        # 如果conversation以"\n<|bot|>:"开头，则去掉
        if conversation.startswith("\n<|bot|>:"):
            logging.error(f"conversation start with \"\n<|bot|>:\", remove it!")
            logging.error(f"conversation: {json_data['text']}")
        elif conversation.startswith("\n<|user|>:"):
            # 标识conversation中的对话数
            i = 1
            # 定义正则表达式匹配首轮对话
            pattern = r'\n<\|user\|>: (.*?)\n\n<\|bot\|>: (.*?)\n\n'
            # 使用正则表达式查找匹配项
            match_once = re.search(pattern, conversation, re.DOTALL)
            if match_once == None:
                # 定义正则表达式匹配首轮对话
                pattern = r'\n<\|user\|>: (.*?)\n\n$'
                # 使用正则表达式查找匹配项
                match_once = re.search(pattern, conversation, re.DOTALL)
                if match_once == None:
                    logging.error(f"conversation match error!")
                    logging.error(f"conversation: {json_data['text']}")
                    return False
                else:
                    question = match_once.group(1)
                    answer = ''
                    # 生成json
                    json_str = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, id, i, model, other_field).to_json()
                    write_file.write(json_str)
                    write_file.write('\n')
                    # 问答序号加1
                    i += 1
            else:
                question = match_once.group(1)
                answer = match_once.group(2)
                # 生成json
                json_str = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, id, i, model, other_field).to_json()
                write_file.write(json_str)
                write_file.write('\n')
                # 问答序号加1
                i += 1
            # 定义正则表达式匹配后续对话
            pattern = r'\n\n<\|user\|>: (.*?)\n\n<\|bot\|>: (.*?)\n\n'
            # 使用正则表达式查找匹配项
            matches = re.findall(pattern, conversation, re.DOTALL)
            # 打印匹配项
            for match in matches:
                # 如果刚开始匹配，报错
                if i == 1:
                    logging.error(f"conversation match error!")
                    logging.error(f"conversation: {json_data['text']}")
                    return False
                question = match[0]
                answer = match[1]
                # 生成json
                json_str = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, id, i, model, other_field).to_json()
                write_file.write(json_str)
                write_file.write('\n')
                # 问答序号加1
                i += 1
        else:
            logging.error(f"conversation string error!")
            logging.error(f"conversation: {json_data['text']}")
            return False
        return True
    except json.JSONDecodeError:
        logging.error("JSONDecodeError")
        return False


# 获取每一段对话，输入到json中处理
def process_json_file_common(file_path, write_file, start_line=1, model='common_en'):
    with open(file_path, 'r', encoding='utf-8') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        for line_number, line in enumerate(f, start=start_line):
            # 打印迭代信息
            logging.debug(f"Line {line_number}: {line}")
            this_line = line.strip()
            if process_json_common(this_line, write_file, model):
                this_line = ''
                continue
            else:
                logging.error("common json parse error!")
                logging.error(f"Line {line_number}, error!")  # json检测失败
                logging.error(f"json str: {this_line}")
                break


def process_json_common(json_str, write_file=None, model='common_en'):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        id = json_data['conversation_id']
        #用json_data的md5值作为id
        unique_id = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        question_detail = "\"human\""
        answer_detail = "\"assistant\""
        other_field = ", \"category\": \""+ json_data['category'] +"\""
        conversation = json_data['conversation']
        # 打印conversation的长度，并加上说明
        logging.debug(f"conversation length: {len(conversation)}")
        # 标识conversation中的对话数以及开始标记
        i = 1
        question = ''
        # 循环处理conversation中的每一个json，json在conversation中序号+1就是该轮对话的序号
        while len(conversation) > 0:
            # 判断conversation中的human是否为null或者是空字符串
            if conversation[0]['human'] == None or conversation[0]['human'] == '':
                unknown_q_or_a = conversation.pop(0)
                # 记录并继续
                logging.error(f"unknown conversation: {unknown_q_or_a}")
                continue
            q_or_a = conversation.pop(0)
            question = q_or_a['human']
            # 如果assistant不是null或者是空字符串，就生成json
            if q_or_a['assistant'] != None and q_or_a['assistant'] != '':
                answer = q_or_a['assistant']
            else:
                answer = ''
            # 生成json
            json_str = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, id, i, model, other_field).to_json()
            write_file.write(json_str)
            write_file.write('\n')
            # 问答序号加1
            i += 1
        return True
    except json.JSONDecodeError:
        logging.error("JSONDecodeError")
        return False

# 获取每一段对话，输入到json中处理
def process_json_file_baiduzhidao(file_path, write_file, start_line=1, model='common_en', cur_time='', max_size=500 * 1024 * 1024, output='shareGPT'):
    # 文件序号
    file_number = 1
    write_file = open(f'{args.output}_{args.model}_{cur_time}_{file_number:02}.jsonl', 'w', encoding='utf-8')
    with open(file_path, 'r', encoding='utf-8') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        for line_number, line in enumerate(f, start=start_line):
            # 打印迭代信息
            logging.debug(f"Line {line_number}: {line}")
            this_line = line.strip()
            if process_json_baiduzhidao(this_line, write_file, model):
                this_line = ''
            else:
                logging.error("common json parse error!")
                logging.error(f"Line {line_number}, error!")  # json检测失败
                logging.error(f"json str: {this_line}")
                break
            # 如果文件超过500M，就关闭文件，新建文件
            if write_file.tell() > max_size:
                write_file.close()
                file_number += 1
                write_file = open(f'{args.output}_{args.model}_{cur_time}_{file_number:02}.jsonl', 'w', encoding='utf-8')

def process_json_baiduzhidao(json_str, write_file=None, model='common_en'):
    # Check if str is a valid JSON
    try:
        json_data = json.loads(json_str)
        #用json_data的md5值作为id
        unique_id = hashlib.md5(json_str.encode('utf-8')).hexdigest()
        question_detail = "\"input\""
        answer_detail = "\"output\""
        question = json_data['input']
        answer = json_data['output']
        json_schema = schema.ShareGPTQASchema(unique_id, question, answer, question_detail, answer_detail, '', 1, model, '')
        # 生成json
        json_str = json_schema.to_json()
        write_file.write(json_str)
        write_file.write('\n')
        return True
    except json.JSONDecodeError:
        logging.error("JSONDecodeError")
        return False
    except KeyError:
        logging.error("KeyError")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse shareGPT into QA data.")
    parser.add_argument("source_files",type=str, default="final_data_sample_230706test.json", help="文件名")
    parser.add_argument("-o","--output",type=str, default="shareGPT",help="output file name (without extension)")
    parser.add_argument("-l","--start_line",type=int,default=1,help="read start line")
    parser.add_argument("-s","--max_size",type=int,default=500 * 1024 * 1024,help="max chunk size")
    # model：
    #   gpt4：https://huggingface.co/datasets/Ejafa/GPT_4_with_ShareGPT/tree/main
    #   common：https://huggingface.co/datasets/shareAI/ShareGPT-Chinese-English-90k/tree/main/sharegpt_jsonl
    #   multilang：https://huggingface.co/datasets/cryscan/multilingual-share/tree/main
    #   vicuna：https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/tree/main
    #   baiduzhidao：baiduzhidao-train.jsonl
    parser.add_argument("-m","--model",type=str,default='gpt4',help="multi model parse")
    args = parser.parse_args()
    # 当前时间
    cur_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    of = open(f'{args.output}_{args.model}_{cur_time}.jsonl', 'w', encoding='utf-8')
    if args.model == 'vicuna' or args.model == 'gpt4':
        # 调用函数来处理 JSON 文件，默认从第1行开始读取
        process_json_file_gpt4(args.source_files, of, args.start_line, args.model)
    elif args.model == 'multilang':
        logging.info(f"model: {args.model}")
        # 调用函数来处理 JSON 文件，默认从第1行开始读取
        process_json_file_multilang(args.source_files, of, args.start_line)
    elif args.model == 'common_en' or args.model == 'common_zh':
        logging.info(f"model: {args.model}")
        # 调用函数来处理 JSON 文件，默认从第1行开始读取
        process_json_file_common(args.source_files, of, args.start_line, args.model)
    elif args.model == 'baiduzhidao':
        logging.info(f"model: {args.model}")
        # 调用函数来处理 JSON 文件，默认从第1行开始读取
        process_json_file_baiduzhidao(args.source_files, of, args.start_line, args.model, cur_time, args.max_size, args.output)
    else:
        logging.error(f"model: {args.model} not support!")
    of.close()