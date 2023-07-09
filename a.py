import json

# 读取文件
file_path_test = 'final_data_sample_230706test.json'  # 替换为实际文件路径
with open(file_path_test, 'r') as file:
    data = json.load(file)

# 取出第一个 JSON 字符串
first_json_string = data[0]

# 打印结果
print(json.dumps(first_json_string, indent=2))  # 格式化打印，可选

# 或者，如果你只想取出 JSON 字符串的内容而不需要格式化打印，可以使用以下代码：
# print(json.dumps(first_json_string['conversations'], indent=2))


# 读取文件
file_path_all = 'final_data.json'  # 替换为实际文件路径

def process_json_file(file_path, start_line):
    with open(file_path, 'r') as f:
        # 定位到指定行数
        for _ in range(start_line - 1):
            f.readline()
        
        buffer = ""
        for line_number, line in enumerate(f, start=start_line):
            buffer += line.strip()
            print("========1=======")
            print(line.strip())
            print("========2=======")
            print(f"Line {line_number}: {data}")  # 打印行号和数据
            break
            # buffer += line.strip()
            # try:
            #     data = json.loads(buffer)
            #     # 处理数据
            #     # 在这里可以对有效的 JSON 对象进行处理或分析
            #     buffer = ""  # 重置缓冲区
            # except json.JSONDecodeError:
            #     continue  # 无效的 JSON 对象，继续读取下一行

# 调用函数来处理 JSON 文件，从第2行开始读取
process_json_file(file_path_all, 2)