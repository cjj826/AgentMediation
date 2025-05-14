from src.chat import *

class Mediator:
    def __init__(self, name, global_prompt="", args=None):
        self.name = name
        self.global_prompt = global_prompt
        self.args = args or {}
        self.statement = ""
        self.statement_history = ""
        self.mediation_history = ""
        self.vent_history = ""
        self.bargain_history = ""

    def generate_discuss_prompt(self, observation):
        """
        讨论阶段 的 prompt: role_prompt + 对话历史 + 讨论的注意事项
        """
        lines = []
        history = observation['history']
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        "\n".join(lines) + f"\n{self.name}:"
        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】
【对话历史开始】
{"\n".join(lines)}
【对话历史结束】

您是调解员 {self.name}，当前正在主持一场调解对话。调解已进入关键阶段，你在之前已经拟定了一个初步的调解方案，现阶段的核心目标是引导各方围绕该方案展开实质性讨论，明确立场，逐步缩小分歧，争取达成共识。

请您结合对话历史、各方当前表态与已有的调解方案，发表您在本轮的中立推进性发言。

你可以选择下面一种或几种发言方向：
- 如对话中出现模糊、不理解或误解的情况，可适时进行**释法明理或答疑解释**，帮助各方在法律基础与合理性上统一认识。
- 简要概括当前方案框架或关键共识点，统一认知基础；
- 引导各方对具体条款作出正面回应或修改建议（如金额、时间、付款方式等）；
- 鼓励尚未明确表态的一方清晰表达态度，或回应对方提议；
- 推动各方确认是否接受当前方案草案，或提出剩余争议条款清单；
- 引导将模糊意见转化为“可协商参数”或“有条件接受”语言；


发言规范如下：
- 本轮发言**仅限一句话**，语言应简洁有力，紧扣当前焦点议题；
- 禁止空泛劝和、重复表达或过度冗长；
- 发言应体现您对局势的观察、判断和引导作用，务必具备**明确的推进价值、判断价值或澄清价值**。

---

现在，请你以调解员{self.name}的身份，发表本轮推进性发言，帮助各方围绕方案条款进行深入讨论、消除疑问，并逐步靠近达成最终共识：
"""

    def generate_vent_prompt(self, observation):
        """
        情感宣泄阶段 的 prompt: role_prompt + 对话历史 + 讨论的注意事项
        """
        lines = []
        history = observation['history']
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        "\n".join(lines) + f"\n{self.name}:"
        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【对话历史开始】
{"\n".join(lines)}
【对话历史结束】

您是调解员 {self.name}，正在主持一场调解对话。当前调解处于“情绪表达阶段”，此阶段的目标不是提出解决方案，而是帮助各方当事人表达真实感受，宣泄情绪，缓解矛盾冲突。

发言要求：
- 禁止重复前一轮内容或无意义套话；
- 禁止反问、质问或指责，应该表达理解，或规劝，或缓解气氛；

现在，请你以调解员 {self.name} 的身份，结合当前局势与各方表现，引导各方表达真实感受、松动对抗态度、激活理解与合作的心理准备，为后续理性协商创造情感与关系的过渡通道，请开始你的发言：
"""

    def make_statement(self):
        """
        根据案情背景，扮演指定角色进行自我介绍，描述自己的立场和诉求
        """
        prompt = f"请你作为本次调解的调解员，结合案情背景，进行简洁而专业的自我介绍，并向当事人说明你的中立立场与职责。请用自然段的形式作答，语言亲和、专业，体现出尊重、引导和协商的语气。现在请你以{self.name}的身份发言："
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.statement = result['result']
        print(self.statement)
    
    def add_statement_history(self, statement_history):
        """
        agent 自己记忆 立场表达 阶段的记忆
        """
        prompt = f"""以下是你在立场表达阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
{statement_history}        
请输出一段压缩描述：      
"""
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.statement_history = result['result']

    def add_mediation_history(self, mediation_history):
        """
        agent 自己记忆 调解初始方案，由于初始方案可能较短，可以直接记下来
        """
        self.mediation_history = mediation_history

    def add_vent_history(self, vent_history):
        """
        agent 自己记忆 情感发泄 阶段的记忆
        """
        prompt = f"""以下是你在情感发泄阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
{vent_history}        
请输出一段压缩描述：      
"""
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.vent_history = result['result']

    def add_bargain_history(self, bargain_history):
        """
        agent 自己记忆 讨价还价 阶段的记忆
        """
        prompt = f"""以下是你在讨价还价阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
{bargain_history}        
请输出一段压缩描述：      
"""
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.bargain_history = result['result']

    def generate_role_prompt(self):
        """
        生成角色的立场，“你是xx”
        """
    
        return f"""你是李镇，来自社区人民调解委员会的专业法律调解员，具备扎实的法律知识、丰富的实务经验，以及高度的共情与引导能力。你性格耐心、稳重、擅长情绪安抚和谈判协调，能够在复杂的纠纷中引导各方回归理性，推动达成共识。你的职责包括：
- 控制对话节奏，引导当事人表达真实诉求；
- 帮助厘清责任、误解和可能的协商路径；
- 安抚激烈情绪，缓和紧张气氛，必要时提出专业、中立、具有建设性的建议；
- 在任何情况下，都应保持语言克制、表达真实、避免偏袒，促成有效调解。
你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。你的发言必须真实，每次发言一句话。
现在，请以调解员李镇的身份，依据你的专业判断与性格风格，开始发言。

【案情背景开始】
{self.global_prompt}
【案情背景结束】
"""

    def __call__(self, observation, stage):
        """
        驱动调解员说话
        """
        if stage == 3:
            prompt = self.generate_vent_prompt(observation)
        elif stage == 5:
            prompt = self.generate_discuss_prompt(observation)
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        return result['result']
    
    def generate_mediation_option(self, facts, retrieve_articles):
        """
        调解员根据 了解/搜集 到的事实证据，拟定一个双方都可能满意的调解方案，涵盖：
        1. 争议焦点识别；
        2. 多方利益考量；
        3. 合理的调解建议；
        4. 法律或专业依据，说明利弊，晓之以理，动之以情。
        """
        if retrieve_articles is not None:
            add_retrieve_articles = f"""
【经过检索外部知识库得到的相关法条开始】
{retrieve_articles}
【经过检索外部知识库得到的相关法条结束】            
""" 
        else:
            add_retrieve_articles = ""
        prompt = f"""你在调解过程中搜集到了以下客观信息：
【客观信息开始】        
{facts}
【客观信息结束】    
【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【情感表达阶段对话开始】
{self.vent_history}
【情感表达阶段对话结束】
{add_retrieve_articles}
请你结合案件信息、各方立场和搜集到的客观信息，提出一份初步调解方案，并精准输出以下字段：

1. 争议焦点：
    - 请从案件材料中提炼出具有决定性法律意义的实质争议焦点，并用一段具有法律规范性的语言进行表述。
    - 争议焦点应具备以下特点：
        - 明确体现当事人之间在关键法律事实或适用上的对立分歧；
        - 聚焦“行为是否合法”“是否构成侵权/违约/不正当竞争”等具有裁判意义的问题；
        - 用词客观中立、简明准确、具有法条对接性；
        - 表述形式应为一句完整法律判断式句子。
    - 参考示例：
        - 本案的主要争议焦点为被告天津小拇指公司、天津华商公司所实施的被诉侵权行为是否侵害了原告兰建军、杭州小拇指公司的注册商标专用权，以及是否构成对杭州小拇指公司的不正当竞争。
        - 本案主要涉及费列罗巧克力是否为在先知名商品，费列罗巧克力使用的包装、装潢是否为特有的包装、装潢，以及蒙特莎公司生产的金莎TRESORDORE巧克力包装、装潢是否构成不正当竞争行为等争议焦点问题。
    - 禁止输出：
        - 情绪化或倾向性用语（如“恶意”“强烈不满”等）；
        - 模糊或冗长描述（如“可能涉及一些问题”）；
        - 多项列举或拆分子焦点（请整合为一段完整表述）；
        - 包含调解建议、处理结果或情感立场。
2. 解纷依据：
    - 列举调解方案依据的具体法律条文（如“《中华人民共和国民法典》第236条”）；
    - 输出格式为数组，每个元素形如 `《中华人民共和国民法典》第236条`；
3. 调解方案：用自然段方式输出调解方案，内容包括：
   - 简要总结争议的核心焦点；
   - 说明你对各方利益的理解和权衡；
   - 给出你认为可行的调解方案；
   - 引用适当的法律常识或调解经验，说明这样做对双方的好处，不这样做可能的风险；
   - 表达出中立、公正、诚恳的语气，做到晓之以理、动之以情。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"争议焦点": str,
"解纷依据": list[str],
"调解方案": str,
}}
```
"""
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        result = prase_json_from_response(result['result'])
        print()
        print("=====初步调解方案=====")
        print(result)
        return result
    
    def generate_final_option(self, facts, retrieve_articles):
        """
        调解员输出最终的调解方案
        """
        if retrieve_articles is not None:
            add_retrieve_articles = f"""
【经过检索外部知识库得到的相关法条开始】
{retrieve_articles}
【经过检索外部知识库得到的相关法条结束】            
""" 
        else:
            add_retrieve_articles = ""
        prompt = f"""你在调解过程中搜集到了以下客观信息：
【客观信息开始】        
{facts}
【客观信息结束】    
【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【情感表达阶段对话历史开始】
{self.vent_history}
【情感表达阶段对话历史结束】
【初识调解方案开始】
{self.mediation_history}
【初识调解方案结束】
【最终协商阶段对话历史开始】
{self.bargain_history}
【最终协商阶段对话历史结束】
{add_retrieve_articles}

请你结合案件信息、各方立场、搜集到的客观信息、初步的调解方案以及和当事人之间的充分讨论，提出一份最终具有说服力的调解方案，并精准输出以下字段：

1. 争议焦点：
    - 请从案件材料中提炼出具有决定性法律意义的实质争议焦点，并用一段具有法律规范性的语言进行表述。
    - 争议焦点应具备以下特点：
        - 明确体现当事人之间在关键法律事实或适用上的对立分歧；
        - 聚焦“行为是否合法”“是否构成侵权/违约/不正当竞争”等具有裁判意义的问题；
        - 用词客观中立、简明准确、具有法条对接性；
        - 表述形式应为一句完整法律判断式句子。
    - 参考示例：
        - 本案的主要争议焦点为被告天津小拇指公司、天津华商公司所实施的被诉侵权行为是否侵害了原告兰建军、杭州小拇指公司的注册商标专用权，以及是否构成对杭州小拇指公司的不正当竞争。
        - 本案主要涉及费列罗巧克力是否为在先知名商品，费列罗巧克力使用的包装、装潢是否为特有的包装、装潢，以及蒙特莎公司生产的金莎TRESORDORE巧克力包装、装潢是否构成不正当竞争行为等争议焦点问题。
    - 禁止输出：
        - 情绪化或倾向性用语（如“恶意”“强烈不满”等）；
        - 模糊或冗长描述（如“可能涉及一些问题”）；
        - 多项列举或拆分子焦点（请整合为一段完整表述）；
        - 包含调解建议、处理结果或情感立场。
2. 解纷依据：
    - 列举调解方案依据的具体法律条文（如“《中华人民共和国民法典》第236条”）；
    - 输出格式为数组，每个元素形如 `《中华人民共和国民法典》第236条`；
3. 调解方案：用自然段方式输出调解方案，内容包括：
   - 简要总结争议的核心焦点；
   - 说明你对各方利益的理解和权衡；
   - 给出你认为可行的调解方案；
   - 引用适当的法律常识或调解经验，说明这样做对双方的好处，不这样做可能的风险；
   - 表达出中立、公正、诚恳的语气，做到晓之以理、动之以情。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"争议焦点": str,
"解纷依据": list[str],
"调解方案": str,
}}
```
"""

        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        result = prase_json_from_response(result['result'])
        return result

    def print_info(self):
        """
        打印 player 的配置信息，便于调试。
        """
        history_info = "\n最近状态变化记录："
        for i, record in enumerate(self.state_history[-5:]):
            history_info += f"\n  Round {i+1}: assertiveness={record['assertiveness']}, cooperativeness={record['cooperativeness']}"

        return f"\n🧠 Player 信息 - {self.name}" + \
            "\n" + "=" * 40 + \
            "\n🧾 Role Description:" + \
            "\n" + history_info