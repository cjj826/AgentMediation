from src.chat import *

class Mediator:
    def __init__(self, name, order, global_prompt="", args=None):
        self.name = name
        self.global_prompt = global_prompt
        self.args = args or {}
        self.statement = ""
        self.statement_history = ""
        self.mediation_history = ""
        self.vent_history = ""
        self.bargain_history = ""
        self.order = order

    def generate_discuss_prompt(self, observation):
        """
        讨论阶段 的 prompt: role_prompt + 对话历史 + 讨论的注意事项
        """
        lines = []
        history = observation['history']
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        line_history = "\n".join(lines) + f"\n{self.name}:"
        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】

您是调解员 {self.name}，当前正在主持一场调解对话。调解已进入关键阶段，你在之前已经基于事实调查结果拟定了一个初步的调解方案（尚未达成一致，仅供讨论），当前的主要目标是**引导当事人围绕该方案展开实质性交涉，逐步明确分歧焦点、促成共识**。

请您结合对话历史、各方当前表态与已有的调解方案，发表您在本轮的中立推进性发言。

---

### 您的发言可以包括以下一种或多种功能：

- 释法明理、答疑释义：当某方对方案、法律、权责存在疑问或误解时，请及时、清晰地进行解释；
- 共识归纳、焦点提炼：总结当前各方已达成一致的部分，明确剩余有待协商的要点，帮助稳定协商框架；
- 推动具体回应与协商动作：鼓励当事人围绕金额比例、付款时限、担保方式等焦点提出明确建议或修改条件；
- 引导模糊表态向具体条款靠拢：将“可以考虑”“视情况接受”转化为具体可谈数值或条件（如接受40%等）；
- 引导发言顺序：推动尚未明确立场的当事人尽快表达回应，避免空转；
- 识别低效争议并果断干预：当协商过度停留于边际收益极低、实际无关紧要的细节（如金额就差几百块等），请您适时介入，引导回到关键利益问题，并提醒各方“适度让步、聚焦主线”，必要时作出“定锚性判断”帮助突破僵局。

---

### 发言规范：

- 每轮请控制在**三句话以内**，力求保持真实人类语感，避免重复劝解、泛泛而谈或语言空转；
- 不得重复劝说或泛泛陈述原则，发言必须体现您对当前博弈局势的观察、判断和策略引导能力；
- 结尾处请自然地**引导当事人按顺序（顺序为 {self.order}）继续表达观点或回应提议**，如：“接下来请按顺序谈谈大家的想法。” 或 “咱们可以逐个讨论这个调整，先从{self.order[0]}开始。”

---

现在，请您以调解员 {self.name} 的身份，结合当前对话情况，发表一段**推进性、中立性、具备判断力的发言**，帮助各方厘清焦点、规避无效拉扯、朝达成一致迈出关键一步。
注意：
- 发言形式为自然段，表达自然口语化，仅保留语言，不要包括动作、情景、解释说明等修饰，务必体现出人类语感，保证人类对话的真实感。
- 注意法律术语的正确使用，避免出现明显的法律错误或逻辑矛盾。

【对话历史开始】
{line_history}
"""

    def make_statement(self):
        """
        根据案情背景，扮演指定角色进行自我介绍，描述自己的立场和诉求
        """
        prompt = f"请你作为本次调解的调解员，结合案情背景，进行简洁而专业的自我介绍，并向当事人说明你的中立立场与职责。请用自然段的形式作答，发言限制在三句话以内，务必体现出人类语感，保证人类对话的真实感，语言亲和、专业，体现出尊重、引导和协商的语气。最后，请你自然地引导当事人按照顺序（固定顺序为{self.order}）进行自我介绍。现在请你以{self.name}的身份发言："
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.statement = result['result']
        print(self.statement)
    
    def add_statement_history(self, statement_history):
        """
        agent 自己记忆 立场表达 阶段的记忆
        """
#         prompt = f"""以下是你在立场表达阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
# {statement_history}        
# 请输出一段压缩描述：      
# """
#         messages=[{"role": "system", "content": self.generate_role_prompt()},
#                       {"role": "user", "content": prompt}]
#         result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
#         self.statement_history = result['result']
        self.statement_history = statement_history

    def add_mediation_history(self, mediation_history):
        """
        agent 自己记忆 调解初始方案，由于初始方案可能较短，可以直接记下来
        """
        self.mediation_history = mediation_history

    def add_bargain_history(self, bargain_history):
        """
        agent 自己记忆 讨价还价 阶段的记忆
        """
#         prompt = f"""以下是你在讨价还价阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
# {bargain_history}        
# 请输出一段压缩描述：      
# """
#         messages=[{"role": "system", "content": self.generate_role_prompt()},
#                       {"role": "user", "content": prompt}]
#         result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
#         self.bargain_history = result['result']
        self.bargain_history = bargain_history

    def generate_reflection_prompt(self, observation, recent_dialogue):
        """
        每轮发言的反思 prompt: 
        """
        history = observation['history']
        lines = []
        my_line = []

        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
            if msg['agent_name'] == self.name:
                my_line.append(f"{msg['agent_name']}: {msg['content']}")

        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】
【对话历史开始】
{"\n".join(lines)}
【对话历史结束】
【你刚才的发言开始】
{recent_dialogue}
【你刚才的发言结束】

你是调解员 {self.name}。请你对刚刚生成的发言内容进行**自我反思和评估**，请依次检查是否存在以下问题，这些问题可能会严重削弱发言在真实调解场景中的可信度与博弈合理性：

---

### 1. **是否聚焦关键争议，有效引导协商路径**
- 发言是否帮助当事人聚焦核心争议（如责任划分、赔偿金额、履行方式）？
- 是否避免陷入程序性重复或边缘性议题（如赔偿表述语义、次要物品等）？
- 是否引导各方按照“核心优先”的顺序逐步展开讨论？

---

### 2. **是否及时识别边际收益低的争执并合理止损**
- 是否主动介入、终止当事人对几百元、几袋粮等细枝末节（相对于总金额来说比较少）的纠缠？
- 是否提醒各方这些细节对整体结构影响有限，应适度让步集中资源？
- 是否善于使用“定锚语言”引导博弈回到主线？

---

### 3. **是否具备阶段推进与定锚能力**
- 当前发言是否在博弈失速或反复时主动提出具备中立性和现实性的折中建议？
- 是否帮助当事人收束争议、推动达成决断而非继续兜圈？

---

注意：
- 你可以保持中立和灵活，但不能放任失控或拖延；
- 你的任务是确保每轮发言**推动对话朝达成共识方向演进**，体现出调解员应有的专业判断力、策略引导力与表达克制力。

你是调解员 {self.name}。请你对刚刚生成的发言内容进行**自我反思和评估**。

请一定按照以下 JSON 格式输出，可被 Python `json.loads()` 正确解析（不要添加多余解释）：

```json
{{
    "分析过程": "简要说明分析过程和理由",
    "是否存在严重问题": "是/否",
    "改进发言": "如果存在问题，则修正问题得到一个更加合理的发言内容，确保不再出现上述问题；如果不存在问题，则可以简单地说“无”或“无问题”"
}}
```
"""

    def generate_role_prompt(self):
        """
        生成角色的立场，“你是xx”
        """
    
        return f"""你是李镇，来自社区人民调解委员会的专业法律调解员，具备扎实的法律知识、丰富的实务经验，以及高度的共情与引导能力。你性格耐心、稳重、擅长情绪安抚和谈判协调，能够在复杂的纠纷中引导各方回归理性，推动达成共识。你的职责包括：
- 控制对话节奏，引导当事人表达真实诉求；
- 帮助厘清责任、误解和可能的协商路径；
- 安抚激烈情绪，缓和紧张气氛，提出专业、中立、具有建设性的建议；
- 在任何情况下，都应保持语言克制、表达真实、避免偏袒，促成有效调解。
你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。

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
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        old_statement = result['result']
        if stage == 5:
            # 考虑加入反思，检查这轮发言的质量，避免简单的幻觉问题
            retry = 3
            while retry > 0:
                messages = [{"role": "user", "content": self.generate_role_prompt() + self.generate_reflection_prompt(observation, old_statement)}]
                new_result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
                new_result = prase_json_from_response(new_result['result'])

                if new_result['是否存在严重问题'] == '是':
                    print("\n\n", new_result)
                    print("\n\n原来的发言：", old_statement)
                    print("\n\n修正后的发言：", new_result['改进发言'])
                    old_statement = new_result['改进发言']
                    retry -= 1
                else:
                    break

        return old_statement
    
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
3. 调解方案：用自然段方式输出初始调解方案，内容包括：
    - 简明总结当前争议核心；
    - 清晰表达对各方利益、现实处境与诉求的理解与平衡；
    - 提出具体、可协商的方案条款，避免泛泛而谈：
        - 包括但不限于：赔偿金额（建议具体金额或区间）、责任比例（如 7:3 分担）、付款期限（如“30日内一次性支付”）、担保形式、合同修正建议等；
        - 所提方案必须具备可执行性和可谈性，便于当事人在此基础上展开下一轮协商；
        - 注意所提方案应该计算准确，避免出现明显的数学错误或逻辑矛盾；
    - 可适当引用常见调解经验或法律常识，说明该方案对各方的现实好处，以及如不接受可能面临的风险（如诉讼周期长、执行困难、继续对抗可能带来的损失）；
    - 整体语气应体现出调解员的专业判断力、人情理解力和中立姿态，做到“以理服人、以情动人”；

特别强调：
- 请务必提出至少一项带有明确数值或比例的可协商条件，避免出现“建议双方协商解决”或“由双方另行商定”的空泛表述；
- 初步调解方案不等于最终意见，可以保留一定模糊空间，但必须为当事人提供可落地、有框架可谈的实质基础。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"争议焦点": str,
"解纷依据": list[str],
"调解方案": str,
}}
```
"""
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        result = prase_json_from_response(result['result'])
        print()
        print("=====初步调解方案=====")
        print(result['调解方案'])
        
        # result = "造成羊群死亡的直接的管理人简某承担60%的责任，剩余的40%的责任由张某和姜某分别承担。"
        # print()
        # print("=====初步调解方案=====")
        # print(result)
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
【初识调解方案开始】
{self.mediation_history}
【初识调解方案结束】
【协商阶段对话历史开始】
{self.bargain_history}
【协商阶段对话历史结束】
{add_retrieve_articles}

当前调解已进行至最后阶段。您作为调解员，已充分听取各方立场与意见，并主持了围绕初步方案的多轮协商。考虑到现实时间与程序限制，调解工作已接近尾声，不具备无限延长协商的条件。

在此背景下，请您结合案件事实、法律依据、对各方表达的充分理解，以及协商过程中展现出的主要分歧与可能共识，提出一份具有判断性、中立性和操作性的最终调解建议方案。该方案应为“各方下一步是否接受”提供现实依据。

输出字段要求：

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
3. 调解方案：请以调解员身份、在调解即将结束的背景下，基于已有的协商阶段对话历史，提出一份最终的建议，应包括以下要素：
    - 简明总结案件争议本质；
    - 表达对当事人各自处境、意图、利益与分歧点的理解；
    - 明确给出建议条款：例如金额、履行时间、责任比例、担保方式等；
    - 指出该方案在现实中如何帮助各方达成利益平衡；
    - 强调该建议是基于已有协商进展和调解时间现实所作出的折中方案；
    - 注意所提方案应该计算准确，避免出现明显的数学错误或逻辑矛盾；
    - 结尾可以适当引导当事人理性考虑、作出决定，例如：
        - “本方案并非强制决定，而是基于本次调解讨论所能提出的最具平衡性的建议，供各方审慎参考并最终作出判断。”

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:

```json
{{
"争议焦点": str,
"解纷依据": list[str],
"调解方案": str,
}}
```
"""

        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
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
    
    def add_vent_history(self, vent_history):
        """
        agent 自己记忆 情感发泄 阶段的记忆
        """
        prompt = f"""以下是你在情感发泄阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
{vent_history}        
请输出一段压缩描述：      
"""
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.vent_history = result['result']