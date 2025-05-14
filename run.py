from src.agent import Player
from src.arena import SimpleArena
from src.env import SimpleDebateEnv
from argparse import Namespace
from src.preliminary import Back
from src.statements import State
from src.judge import Judge
import json
import concurrent.futures as cf
import os
import argparse
from tqdm import *
import src.globals as globals

def run(data, id, dir, args):
    globals.total_token = 0
    globals.this_question_input_token = 0
    globals.this_question_output_token = 0
    config = {
        "num_turns": args.num_turns,
        "case_content": "default",
        "model_name": args.model_name,
        "temperature": 0,
        "max_tokens": 1024,
        "default": True,
        "basic_back": data['basic_back'],
        "players": data['players'],
        "facts": data['fact']['facts'],
        "baseline": args.baseline, # True表示不设定特殊冲突策略
        "state": {
            "assertiveness": args.assertiveness,
            "cooperativeness": args.cooperativeness
        },
        "conflict_type": args.conflict_type,
        "modify_factor": args.modify_factor,
    }
    retrieve_articles = None
    if args.retrieve:
        retrieve_articles = data['retrieve_articles']
    output_dict = {"id": id}
    # output_dict['case_type'] = data['result']

    # Stage1: preliminary
    background = Back(config)
    players = background.players
    mediator = background.mediator
    facts = background.facts
    print("=====案情背景=====")
    print(background.global_prompt)
    output_dict["global_prompt"] = background.global_prompt
    output_dict["facts"] = background.facts

    # Stage2: statements
    state = State(players, mediator)
    output_dict['statement_history'] = state.statement_history

    # Stage3: Venting
    # 情感宣泄阶段，鼓励各方宣泄自己的情感
    if args.vent:
        vent_env = SimpleDebateEnv(players, mediator, num_turns=3)
        vent_arena = SimpleArena(players, mediator, stage=3, environment=vent_env, adaptive=args.adaptive)
        vent_history, vent_messages = vent_arena.launch_cli(interactive=False)
        output_dict['vent_messages'] = vent_messages
    else:
        vent_history = []

    mediator.add_vent_history(vent_history)
    for player in players:
        player.add_vent_history(vent_history)

    # Stage4: Option generation
    mediation_option = mediator.generate_mediation_option(facts, retrieve_articles)

    output_dict['mediation_option'] = mediation_option

    mediator.add_mediation_history(mediation_option['调解方案'])
    for player in players:
        player.add_mediation_history(mediation_option)

    # Stage5: Bargaining and negotiation 
    # 各方对调解方案进行讨论
    bargain_env = SimpleDebateEnv(players, mediator, num_turns=config["num_turns"])
    bargain_arena = SimpleArena(players, mediator, stage=5, environment=bargain_env, adaptive=args.adaptive)
    bargain_history, bargain_messages = bargain_arena.launch_cli(interactive=False)
    output_dict['bargain_messsages'] = bargain_messages

    mediator.add_bargain_history(bargain_history)

    # Final: 调解员总结出一个调解方案
    final_mediation = mediator.generate_final_option(facts, retrieve_articles)
    print("=====")
    print(final_mediation)
    print("调解结束")

    output_dict['final_mediation'] = final_mediation

    # judge 阶段
    output_dict['result'] = []
    judge = Judge(background.global_prompt, config)
    result = judge(bargain_messages, final_mediation['调解方案'])
    statis_dict = {}
    accept_dict = {}
    for p in players:
        statisfaction = p.get_staisfaction(bargain_messages, final_mediation['调解方案'])
        accept = p.get_role_view(bargain_messages, final_mediation['调解方案'])
        statis_dict[p.name] = statisfaction
        accept_dict[p.name] = accept
    result['是否接受'] = accept_dict
    result['满意度'] = statis_dict
    output_dict['result'].append(result)
    
    output_dict["total_token"] = globals.total_token
    output_dict["input_token"] = globals.this_question_input_token
    output_dict["output_token"] = globals.this_question_output_token
    output_dict['dollar'] = globals.this_question_input_token / 1e6 * 0.286 + globals.this_question_output_token / 1e6 * 1.143
    print("累计 token 消耗数：", globals.total_token)
    print("累计 input token 消耗数：", globals.this_question_input_token)
    print("累计 output token 消耗数：", globals.this_question_output_token)
    print("消耗美金：", globals.this_question_input_token / 1e6 * 0.286 + globals.this_question_output_token / 1e6 * 1.143)
    p = ""

    for player in players:
        p += player.print_info()  
   
    output_dict["players_num"] = len(players)
    output_dict["players_info"] = p


    return output_dict

def run_with_cache(data, date, path, idx, args):
    """ 运行任务，先检查缓存是否已存在，避免重复计算 """
    cache_dir = f"./output_{date}/temp_{path}"
    os.makedirs(f'./output_{date}/temp_{path}', exist_ok=True)
    file_path = os.path.join(cache_dir, f"{idx}.json")
    print(file_path)

    if os.path.exists(file_path):
        print("已存在")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    result = run(data, idx, cache_dir, args)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--num_turns', type=int, default=5, help='对话轮数')
    parser.add_argument('--model_name', type=str, default='glm-4-flash', help='模型')
    parser.add_argument('--baseline', action='store_true', help='是否默认冲突策略，若是则下两个参数无效，默认为 False')
    parser.add_argument('--assertiveness', type=int, default=5, help='竞争度')
    parser.add_argument('--cooperativeness', type=int, default=5, help='合作度')
    parser.add_argument('--adaptive', action='store_true', help='性格是否动态变化，默认为 False')
    parser.add_argument('--conflict_type', type=str, default="无", help='冲突类型，缺省为无')
    parser.add_argument('--modify_factor', type=str, default="超级加剧", help='影响因子，缺省为加剧')
    parser.add_argument('--multi', action='store_true', help='是否开启多进程，默认为 False')
    parser.add_argument('--vent', action='store_true', help='是否开启情感宣泄阶段，默认为 False')
    parser.add_argument('--retrieve', action='store_true', help='是否使用检索')
    parser.add_argument('--date', type=str, required=True, help='实验日期')

    args = parser.parse_args()
    path = f"{args.num_turns}_{args.model_name}_{args.baseline}_{args.assertiveness}_{args.cooperativeness}_{args.adaptive}_{args.conflict_type}_{args.modify_factor}_{args.vent}"
    input_datas = open('./data/case_back.json', 'r').readlines()[:1]
    result_json_list = []
    os.makedirs(f'./test_{args.date}', exist_ok=True)
    output = open(f'./test_{args.date}/{path}.json', 'w')

    if args.multi:
        with cf.ProcessPoolExecutor(max_workers=30) as executor:
            future_list = [executor.submit(run_with_cache, json.loads(data), args.date, path, idx, args) for idx, data in enumerate(input_datas)]
            for future in tqdm(cf.as_completed(future_list), total=len(future_list), desc="Processing", ncols=100):
                try:
                    result = future.result()
                    if isinstance(result, dict) and "id" in result:
                        result_json_list.append(result)
                    else:
                        print(f"收到异常结果（非dict或缺id）：{result}")
                except Exception as e:
                    print("任务执行异常：", e)
        result_json_list = [r for r in result_json_list if isinstance(r.get("id"), (int, str))]
        result_json_list.sort(key=lambda x: x["id"])
        for result in result_json_list:
            output.write(json.dumps(result, ensure_ascii=False) + '\n')
    else:
        run(json.loads(input_datas[0]), 1, f"./output_{args.date}/temp_{path}", args)