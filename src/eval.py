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
args = parser.parse_args()
path = f"{args.num_turns}_{args.model_name}_{args.baseline}_{args.assertiveness}_{args.cooperativeness}_{args.adaptive}_{args.conflict_type}_{args.modify_factor}_{args.vent}"
# print(path)
datas = open(f'./test_{args.date}/{path}.json', 'r').readlines()

import json
from collections import Counter, defaultdict
import numpy as np
from chat import *
from judge import Judge
from tqdm import *

token_num = 0
dollar = 0
average_round = 0
common_rate = 0
score = {}

risk_score_map = {
    "很低": 0,
    "较低": 1,
    "中等": 2,
    "较高": 3,
    "很高": 4
}

satisfaction_score_map = {
    "很低": 0,
    "较低": 1,
    "中等": 2,
    "较高": 3,
    "很高": 4
}

consensus_score_map = {
    "很低": 0,
    "较低": 1,
    "中等": 2,
    "较高": 3,
    "很高": 4
}

# 初始化统计players_num
risk_levels = []
risk_scores = []
satisfaction_levels = []
satisfaction_scores = []
consensus_levels = []
consensus_scores = []
acc_rate = 0

for idx, data in enumerate(datas):
    # print(idx)
    try: 
        data = json.loads(data)

        token_num += data['total_token']
        dollar += data['dollar']

        result = data['result'][-1]
        risk_levels.append(result["矛盾升级风险等级"])
        risk_scores.append(risk_score_map.get(result["矛盾升级风险等级"], 0))
        
        acc_score = 0
        for person, acc_dict in result["是否接受"].items():
            acc = acc_dict["是否接受"]
            if acc == "接受":
                acc_score += 1

        if acc_score == len(data['result'][-1]["是否接受"]):
            acc_rate += 1

        cur_status = 0
        for person, sat in result["满意度"].items():
            level = sat["满意度评级"]
            satisfaction_levels.append(level)
            cur_status += satisfaction_score_map.get(level, 0)
            
        satisfaction_scores.append(cur_status / len(data['result'][-1]["满意度"]))

        consensus_level = data['result'][-1]["共识程度评级"]
        consensus_levels.append(consensus_level)
        consensus_scores.append(consensus_score_map.get(consensus_level, 0))
    except Exception as e:
        print(f"exception, {e}, {idx}")
        pass


risk_levels = {
    risk: Counter(risk_levels).get(risk, 0) for risk in risk_score_map.keys()
}
satisfaction_levels = {
    satisfaction: Counter(satisfaction_levels).get(satisfaction, 0) for satisfaction in satisfaction_score_map.keys()
}
consensus_levels = {
    consensus: Counter(consensus_levels).get(consensus, 0) for consensus in consensus_score_map.keys()
}


# 汇总统计
summary = {
    "风险等级分布": dict(risk_levels),
    "风险分数平均值": round(np.mean(risk_scores) / 4 * 100, 2),
    "满意度等级分布": dict(satisfaction_levels),
    "满意度平均分": round(np.mean(satisfaction_scores) / 4 * 100, 2),
    "共识程度分布": dict(consensus_levels),
    "共识程度平均分": round(np.mean(consensus_scores) / 4 * 100, 2)
}
# print(date)
print(token_num, end=";")
print(dollar, end=";")
for v in summary.values():
    print(v, end=";")
print(f"{acc_rate:.2f}", end=";")
print()