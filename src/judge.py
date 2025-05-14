from src.chat import *

class Judge:
    def __init__(self, global_prompt, config):
        self.global_prompt = global_prompt
        self.config = config

    def __call__(self, messages, mediation):
        return self.judge_action(messages, mediation)
    
    def get_history(self, history):
        """
        得到当前的历史对话
        """
        lines = []
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        return "\n".join(lines)

    def judge_action(self, messages, mediation):
        res = {}
        judgement_prompt = f"""以下是一段法律矛盾纠纷的调解对话，请你评估目前各方达成共识的程度，并给出其等级（很低/较低/中等/较高/很高），同时简要说明理由。
【案情背景开始】
{self.global_prompt}
【案情背景结束】
【对话记录开始】
{self.get_history(messages)}
【对话记录结束】
【最终调解方案开始】
{mediation}
【最终调解方案结束】

- 很低：各方缺乏实质表达或回应，常出现沉默、回避或敌意语言，回避关键议题，调解对话停留在形式层面，未建立任何协商基础，无推进信号。
- 较低：双方已展现一定倾听和理解意愿，但互动仍多停留在态度层面，尚未围绕具体议题展开深入协商，初步共识意向尚不清晰。
- 中等：初步共识意向逐步显现，双方均表达了解决问题的愿望，在部分议题上立场已有靠近或方案初步形成，但在关键问题上仍未达成一致，调解具备推进潜力但尚不稳定。
- 较高：各方在主要议题上已形成初步的一致意见，语言具体、互动积极，整体共识框架已基本形成，调解正处于实质性协商阶段。
- 很高：各方在主要议题上已形成清晰的一致意见，配合态度积极，调解方向明确且具可执行性，整体调解进程具备总结归档或起草协议的基础，可进入收尾阶段。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"共识程度评级": "很低/较低/中等/较高/很高",
"理由": "简明说明判断依据"
}}
```
"""

        result = LLM(judgement_prompt, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        result = prase_json_from_response(result['result'])
        
        res['共识程度评级'] = result["共识程度评级"]
        res['共识程度评级理由'] = result["理由"]

        judge_risk_prompt = f"""以下是一段法律矛盾纠纷的调解对话，请你评估当前矛盾升级风险的程度，并给出其等级（很低/较低/中等/较高/很高），同时简要说明理由。
【案情背景开始】
{self.global_prompt}
【案情背景结束】
【对话记录开始】
{self.get_history(messages)}
【对话记录结束】
【最终调解方案开始】
{mediation}
【最终调解方案结束】

- 很低：沟通顺畅、情绪平稳，观点表达**充分且理性**，分歧较小或已达成初步共识，调解实质性推进，无需额外干预即有望顺利完成调解。
- 较低：虽存在分歧，但当事人之间沟通**开放**，**语言有节制**，有明确的协商意愿且互动良性，调解可持续深入推进。
- 中等：存在较明显分歧，或调解推进缓慢。表现包括：语言模糊、频繁让步、逃避实质问题，或过度迁就导致核心诉求未被充分表达，调解虽无激烈对抗但缺乏实质性突破，需引起重视并适时介入引导。
- 较高：对抗性表达频繁，沟通趋于破裂边缘，调解进程基本停滞或遭到抵制，部分当事人可能开始倾向于诉诸司法解决。
- 很高：情绪严重失控、沟通已基本破裂，部分当事人明确表达出诉诸法律等外部手段的意图。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:（不要添加多余解释）：

```json
{{
"矛盾升级风险等级": "很低/较低/中等/较高/很高",
"理由": "简明说明判断依据"
}}
```
"""

        result = LLM(judge_risk_prompt, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        result = prase_json_from_response(result['result'])
        risk = result["矛盾升级风险等级"]
        res['矛盾升级风险等级'] = risk
        res['矛盾升级风险等级理由'] = result["理由"]
        print(f"矛盾升级风险等级：{risk}")
        print(f"共识程度评级：{res['共识程度评级']}")
        print("==========================")
        return res