#%%
from wikihow_parser import Article
import json,traceback,csv,time
from tqdm.auto import tqdm
#%%

#scheme
ID = "编号"
Q = "问"
A = "答"
ANSWER = "回答"
META = "元数据"
A_SUM = "简要回答"
# PREV = "前承"
# NEXT = "后续"
A_STRUCT = "结构"
METHOD = "方法"
STEP = "步骤"
NUMBER = "编号"
TIPS = "小提示"
WARN = "注意事项"
TITLE = "标题"
DESC = "描述"


def process_page(page):
    article = Article(page)
    title = article.title
    answer_sum = article.intro
    answer_struct = {}
    answer = ""
    answer_struct[METHOD] = []
    for method in article.methods:
        method_title = method.title.partition(':')[-1] if (':') in method.title else method.title
        method_title = method_title.strip()
        answer += f"{method.number}. {method_title}\n"
        method_struct = {NUMBER:method.number,TITLE:method_title,STEP:[]}
        for step in method.steps:
            answer += f"{method.number}-{step.number}. {step.title}\n" if len(method.steps) > 1 else f"{step.title}\n"
            description = step.description.replace('\n\n','\n').replace('\t',"")
            answer += f"{description}\n"
            method_struct[STEP].append({NUMBER:step.number,TITLE:step.title.strip(), DESC:description.strip()})
        answer_struct[METHOD].append(method_struct)
    if article.tips and article.tips['tips']:
        answer+=article.tips['title'].strip()+'\n'
        for tip in article.tips['tips']:
            answer+=tip.replace("\t","").strip() + '\n'
        method_struct[TIPS] = [tip.replace("\t","").strip()+"\n" for tip in article.tips['tips']]
    if article.warnings and article.warnings['warnings']:
        answer+=article.warnings['title'].strip()+'\n'
        for warn in article.warnings['warnings']:
            answer+=warn.replace("\t","").strip() + '\n'
        method_struct[WARN] = [warn.replace("\t","").strip() + '\n' for warn in article.warnings['warnings']]
    # result = {Q:title,A:[{A:answer,A_SUM:answer_sum,A_STRUCT:answer_struct}],}
    #  问答语料组的格式：{"文件名":"xxx.txt","目录":"20230199","分类":"数学题","内容":[{"Q":"1加1等于几","A":"等于2"},{"Q":"2减1等于几","A":"1"}]}
    result = {Q:title,A:answer,META:{"create_time":time.strftime('%Y%m%d %H:%M:%S'),"回答明细":{ANSWER:answer,A_SUM:answer_sum,A_STRUCT:answer_struct}}}
    return result
# %%
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse wikihow page into QA data.")
    parser.add_argument("source_files",type=str, nargs="*",help="source html files",default=[])
    parser.add_argument("-c","--csv",type=str,default=None,help="Crawled CSV files")
    parser.add_argument("-o","--output",type=str,default="wikihow",help="output file name (without extension)")
    parser.add_argument("-m","--max_size",type=int,default=500 * 1024 * 1024,help="max chunk size")
    args = parser.parse_args()
    chunk_counter = 0
    of = open(f"{args.output}.{chunk_counter}.jsonl",'w')

    for filepath in tqdm(args.source_files):
        with open(filepath) as f:
            try:
                result = {"id":i}
                result.update(process_page(d['html']))
            except Exception as e:
                traceback.print_exc()
                print("Failed to process", filepath)
                continue
            print(json.dumps(result,ensure_ascii=False),file=of)
            if of.tell() > args.max_size:
                of.close()
                chunk_counter+=1
                of = open(f"{args.output}.{chunk_counter}.jsonl",'w')
    if args.csv:
        csv.field_size_limit(100000000)
        with open(args.csv,'r',newline="") as f:
            reader = csv.DictReader(f)
            for i,d in enumerate(tqdm(reader)):
                try:
                    result = {"id":i}
                    result.update(process_page(d['html']))
                except Exception as e:
                    traceback.print_exc()
                    print("Failed to process csv index",i,d["_id"])
                    continue        
                print(json.dumps(result,ensure_ascii=False),file=of)
                if of.tell() > args.max_size:
                    of.close()
                    chunk_counter+=1
                    of = open(f"{args.output}.{chunk_counter}.jsonl",'w')
    print("Done")