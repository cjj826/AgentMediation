import argparse
parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('--num_turns', type=int, default=5, help='对话轮数')
parser.add_argument('--model_name', type=str, default='glm-4-flash', help='模型')
parser.add_argument('--baseline', action='store_true', help='是否默认冲突策略，若是则下两个参数无效，默认为 False')
parser.add_argument('--assertiveness', type=int, default=5, help='竞争度')
parser.add_argument('--cooperativeness', type=int, default=5, help='合作度')
parser.add_argument('--adaptive', action='store_true', help='性格是否动态变化，默认为 False')
parser.add_argument('--conflict_type', type=str, default="无", help='冲突类型，缺省为无')
parser.add_argument('--modify_factor', type=str, default="超级加剧", help='影响因子，缺省为加剧')
parser.add_argument('--vent', action='store_true', help='是否开启情感宣泄阶段，默认为 False')
parser.add_argument('--multi', action='store_true')
parser.add_argument('--date', type=str, required=True, help='实验日期')
parser.add_argument('--retrieve', action='store_true', help='是否使用检索')
parser.add_argument('--topk', type=int, default=1, help='检索的topk')
args = parser.parse_args()
path = f"{args.num_turns}_{args.model_name}_{args.baseline}_{args.assertiveness}_{args.cooperativeness}_{args.adaptive}_{args.conflict_type}_{args.modify_factor}_{args.vent}"

datas = open(f'./test_{args.date}/{path}.json', 'r').readlines()
# print(path)
# print(len(datas))
import json
from collections import Counter, defaultdict
import numpy as np
from tqdm import *
import traceback

token_num = 0
average_round = 0
common_rate = 0
score = {}

from rouge import Rouge
import jieba
import logging
import bert_score
jieba.setLogLevel(logging.CRITICAL)

def evaluate_controversy_point(reference, hypothesis):
    # rouge
    rouge = Rouge()
    reference = " ".join(jieba.lcut(reference))
    hypothesis = " ".join(jieba.lcut(hypothesis))
    scores = rouge.get_scores(hypothesis, reference)[0]
    return scores['rouge-l']['f'], reference, hypothesis

    # bert_score
    reference = " ".join(jieba.lcut(reference))
    hypothesis = " ".join(jieba.lcut(hypothesis))
    P, R, F1 = bert_score.score(cands=[hypothesis], refs=[reference], lang="zh", model_type="bert-base-chinese")

    # print(F1.item())
    return round(F1.item(),4), reference, hypothesis

CN_NUM = {
    '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
}
CN_UNIT = {
    '十': 10,
    '百': 100,
    '千': 1000,
    '万': 10000
}

def chinese_to_arabic(cn: str) -> int:
    unit = 0  # 当前单位
    ldig = []
    for c in reversed(cn):
        if c in CN_UNIT:
            unit = CN_UNIT[c]
            if unit == 10 and (len(ldig) == 0):  # 处理“十” -> 10，而不是 0
                ldig.append(10)
        elif c in CN_NUM:
            num = CN_NUM[c]
            if unit:
                num *= unit
                unit = 0
            ldig.append(num)
    if unit:  # 末尾是单位而非数字
        ldig.append(unit)
    return sum(ldig[::-1])

import re

def standardize_law(law_str):
    match = re.search(r'(《.*?》)[^第]*第?([一二三四五六七八九十百千万零两\d]+)条', law_str)
    if match:
        law_name = match.group(1)
        raw_article = match.group(2)
        # 如果是中文数字，转成阿拉伯数字
        if re.fullmatch(r'[一二三四五六七八九十百千万零两]+', raw_article):
            article = chinese_to_arabic(raw_article)
        else:
            article = int(raw_article)
        return f"{law_name}第{article}条"
    else:
        return law_str  # fallback


retrieve_article_datas = open('./data/case_back.json', 'r').readlines()
retrieve_article_datas_dict = {}
for retrieve_article_data in retrieve_article_datas:
    retrieve_article_datas_dict[json.loads(retrieve_article_data)['basic_back']] = retrieve_article_data

def evaluate_article_score(G, E, retrieve_articles):
    correct_elements = 0
    if len(retrieve_articles) > 0:
        E = [standardize_law(e) for e in E]
        for r in retrieve_articles:
            if standardize_law(r) not in E:
                E.append(standardize_law(r))
    for g in G:
        for e in E:
            if standardize_law(g) == standardize_law(e):
                correct_elements += 1
                break
    
    m = len(E)
    n = len(G)
    
    if m == 0 or n == 0:
        print("here")
        return 0.0
    
    P = correct_elements / m
    R = correct_elements / n

    if P+R != 0:
        F1 = 2 * correct_elements / (m + n)
    else:
        F1 = 0

    return P,R,F1, G, E

case_datas = open('./data/case_back.json', 'r').readlines()

case_datas_dcit = {}
for case_data in case_datas:
    case_datas_dcit[json.loads(case_data)['basic_back']] = case_data

output_file = open(f'./test_{args.date}/{path}_score.json', 'w')
output_point_file = open(f'./test_{args.date}/{path}_point.json', 'w')

mediation_option_point = 0
mediation_option_score_P = 0
mediation_option_score_R = 0
mediation_option_score_F = 0
final_mediation_point = 0
final_mediation_score_P = 0
final_mediation_score_R = 0
final_mediation_score_F = 0

output_data = {
    "score": []
}   

output_point = {
    "point": []
}

for idx, data in (enumerate(datas)):
    try: 
        data = json.loads(data)
        reference_data = json.loads(case_datas_dcit[data['global_prompt']])

        point1, ref_point1, ans_point1 = evaluate_controversy_point(
            reference_data['point'],
            data['mediation_option']['争议焦点']
        )
        mediation_option_point += point1

        retrieve_articles = []
        if args.retrieve:
            retrieve_data = json.loads(retrieve_article_datas_dict[data['global_prompt']])
            if len(retrieve_data['retrieve_articles']) >= args.topk:
                retrieve_articles = retrieve_data['retrieve_articles'][:args.topk]
            else:
                retrieve_articles = retrieve_data['retrieve_articles']

        P, R, F1, ref1, ans1 = evaluate_article_score(
            reference_data['article'],
            data['mediation_option']['解纷依据'],
            retrieve_articles)
        mediation_option_score_P += P
        mediation_option_score_R += R
        mediation_option_score_F += F1


        point2, ref_point2, ans_point2 = evaluate_controversy_point(
            reference_data['point'],
            data['final_mediation']['争议焦点'])
        final_mediation_point += point2
        
        
        P, R, F1, ref2, ans2 = evaluate_article_score(
            reference_data['article'],
            data['final_mediation']['解纷依据'],
            retrieve_articles)
        final_mediation_score_P += P
        final_mediation_score_R += R
        final_mediation_score_F += F1

        output_data['score'].append({
            "ref1": ref1,
            "ref2": ref2,
            "ans1": ans1,
            "ans2": ans2,
            "R": R
        })

        output_point['point'].append({
            "ref1": ref_point1,
            "ref2": ref_point2,
            "ans1": ans_point1,
            "ans2": ans_point2
        })

    except Exception as e:
        print(f"Error processing data at index {idx}: {e}")
        traceback.print_exc()
        break

output_file.write(json.dumps(output_data, ensure_ascii=False) + '\n')
output_point_file.write(json.dumps(output_point, ensure_ascii=False) + '\n')
print(f"{(mediation_option_point + final_mediation_point) / (len(datas) * 2):.4f}", end=';')
print(f"{(mediation_option_score_R + final_mediation_score_R) / (len(datas) * 2):.4f}", end=';')
print()