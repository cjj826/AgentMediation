from preliminary import Back
import json
from tqdm import *
from chat import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# ---------- step 1
# output_path = "./data/case_back.json"
# output_lock = Lock()

# datas = open("./data/data_resource.json", "r").readlines()
# results = []

# def process_single(data):
#     data = json.loads(data)
#     back = Back(config={
#         "default": False,
#         "case_content": data['content']['基本案情'],
#         "content": data['content']['基本案情'] + data['content']['处理方式方法'],
#         "model_name": "deepseek-v3-0324",
#         # "model_name": "glm-4-flash",
#         "temperature": 0.7,
#         "max_tokens": 1024})

#     return {
#         "id": data['filename'],
#         "basic_back": data['content']['基本案情'],
#         "players": back.players,
#         "player_number": len(back.players),
#         "fact": back.facts
#     }


# # 多线程处理
# with ThreadPoolExecutor(max_workers=1) as executor:
#     futures = [executor.submit(process_single, data) for data in datas]
#     with open(output_path, "w") as f_out:
#         for future in tqdm(as_completed(futures), total=len(futures)):
#             try:
#                 result = future.result()
#                 # 写文件加锁
#                 with output_lock:
#                     json.dump({
#                         "basic_back": result["basic_back"],
#                         "players": result["players"],
#                         "player_number": result["player_number"],
#                         "fact": result["fact"]
#                     }, f_out, ensure_ascii=False)
#                     f_out.write("\n")
#             except Exception as e:
#                 print("处理异常：", e)


# datas = open('./data/case_back.json', "r").readlines()

# player_number = 0
# min_number = 100000
# max_number = 0
# for data in datas:
#     data = json.loads(data)
#     player_number += data["player_number"]
#     if data["player_number"] < min_number:
#         min_number = data["player_number"]
#     if data["player_number"] > max_number:
#         max_number = data["player_number"]
    
# print("最少对立方数量：", min_number)
# print("最多对立方数量：", max_number)
# print("平均每个案件的对立方数量：", player_number / len(datas))


# ------------ step 2: 提取 争议焦点 和 法条 label

model_name = "gpt-4o-2024-11-20"

def generate_point(content):
        """
        从内容中提取案件的争议焦点
        """
        prompt = f"""请你结合案件信息，提取其中的争议焦点
【案件信息开始】        
{content}
【案件信息结束】    

提取要求：
- 请从案件材料中提炼出具有决定性法律意义的实质争议焦点，并用一段具有法律规范性的语言进行表述。
- 争议焦点应具备以下特点：
        - 明确体现当事人之间在关键法律事实或适用上的对立分歧；
        - 聚焦“行为是否合法”“是否构成侵权/违约/不正当竞争”等具有裁判意义的问题；
        - 用词客观中立、简明准确、具有法条对接性；
        - 表述形式应为一句完整法律判断式句子。

参考示例：
- 本案的主要争议焦点为被告天津小拇指公司、天津华商公司所实施的被诉侵权行为是否侵害了原告兰建军、杭州小拇指公司的注册商标专用权，以及是否构成对杭州小拇指公司的不正当竞争。
- 本案主要涉及费列罗巧克力是否为在先知名商品，费列罗巧克力使用的包装、装潢是否为特有的包装、装潢，以及蒙特莎公司生产的金莎TRESORDORE巧克力包装、装潢是否构成不正当竞争行为等争议焦点问题。

禁止输出：
- 情绪化或倾向性用语（如“恶意”“强烈不满”等）；
- 模糊或冗长描述（如“可能涉及一些问题”）；
- 多项列举或拆分子焦点（请整合为一段完整表述）；
- 包含调解建议、处理结果或情感立场。


请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"争议焦点": "请填写一段规范、完整的法律争议焦点表达。"
}}
```
"""

        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, model_name, 0.7, 1024)
        result = prase_json_from_response(result['result'])
        return result

def generate_article(content):
        """
        从内容中提取案件的解纷依据
        """
        prompt = f"""请你将给定的解纷依据转化为指定的输出格式
【解纷依据开始】        
{content}
【解纷依据结束】    

解纷依据：
    - 列举调解方案依据的具体法律条文（如“《中华人民共和国民法典》第236条”）；
    - 输出格式为数组，每个元素形如 `《中华人民共和国民法典》第236条`；

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"解纷依据": list[str],
}}
```
"""

        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, model_name, 0.7, 1024)
        result = prase_json_from_response(result['result'])
        return result

datas = open("./data/data_resource.json", "r").readlines()

data_cases = open('./data/case_back.json', 'r').readlines()

data_cases_dict = {}

for data_case in data_cases:
        data_cases_dict[json.loads(data_case)['basic_back']] = data_case


output_lock = Lock()
output_path = "./data/case_back.json"

def process_single(idx, data_line):
    try:
        data = json.loads(data_line)
        case_text = data['content']['基本案情'] + data['content']['处理方式方法'] + data['content']['处理结果']
        point = generate_point(case_text)
        article = generate_article(data['content']['解纷依据'])
        data_case = json.loads(data_cases_dict[data['content']['基本案情']])

        result = {
            "name": data['filename'],
            "basic_back": data_case['basic_back'],
            "players": data_case['players'],
            "player_number": data_case['player_number'],
            "point": point['争议焦点'],
            "article": article['解纷依据'],
            "fact": data_case['fact'],
            "retrieve_articles": data_case['retrieve_articles']
        }
        return result

    except Exception as e:
        print(f"Error processing index {idx}: {e}")
        return None

with ThreadPoolExecutor(max_workers=50) as executor, open(output_path, "w") as output_file:
    futures = [executor.submit(process_single, idx, data) for idx, data in enumerate(datas)]

    for future in tqdm(as_completed(futures), total=len(futures)):
        result = future.result()
        if result is not None:
            with output_lock:
                output_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                output_file.flush()