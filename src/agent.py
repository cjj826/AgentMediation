from src.chat import *
import matplotlib.pyplot as plt

class Player:
    def __init__(self, name, state, global_prompt="", mode = "", args=None):
        self.name = name 
        self.state = state 
        self.global_prompt = global_prompt 
        self.args = args or {}
        self.state_history = [] 
        self.statement = "" 
        self.statement_history = "" 
        self.mediation_history = ""
        self.vent_history = "" 
        self.mode = mode

    def modify_strategy(self, state):
        """
        根据当前的发言，记录目前的策略，以方便之后的策略调整合理性
        """

        prompt = f"""以下是你最新的一轮发言：
{state}

请你用一句话总结你在本轮发言中所表达的**谈判条件**，要求突出以下要素：
- 责任比例主张 （如“我方承担XX%，对方承担XX%”）；
- 关键金额或赔偿主张 （如“总赔偿金额为XX元”、“首付XX元”等）；
- 当前让步（后续协商谈判的基础，可根据身份逐步递增或递减） （如“最多接受XX元”、“至少对方需承担XX元”等）；

语言要求简洁、明确、客观，请不要添加额外的主观态度。请回答：
"""
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.strategy = result['result']
        print("\n\n谈判条件: ", self.strategy)
        # self.strategy = state

    def add_statement_history(self, statement_history):
        """
        agent 自己记忆 立场表达 阶段的记忆
        """
#         prompt = f"""以下是你在立场表达（自我介绍）阶段经历的事件记录，请你对该记录进行总结，要包括所有要点，形成长期记忆。
# {statement_history}        
# 请输出一段压缩描述：      
# """
#         messages=[{"role": "system", "content": self.generate_role_prompt()},
#                       {"role": "user", "content": prompt}]
#         result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        
#        self.statement_history = result['result']
        self.statement_history = statement_history

    def add_mediation_history(self, mediation_history):
        """
        agent 自己记忆 调解初始方案，由于初始方案可能较短，可以直接记下来
        """
        self.mediation_history = mediation_history

    def generate_discuss_prompt(self, observation):
        """
        讨论阶段 的 prompt: role_prompt + 对话历史 + 讨论的注意事项
        """
        lines = []
        my_line = []
        history = observation['history']
        count = 1
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
            if msg['agent_name'] == self.name:
                my_line.append(f"第{count}轮中，{msg['agent_name']}（你说）: {msg['content']}")
                count += 1
        line_history = "\n".join(lines) + f"\n{self.name}:"

        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】

请你结合当前对话背景、调解员的最新建议，以及各方表达的态度与立场，**作为一名当事人，发表你在本轮中的真实回应**。

你的发言应体现你此刻的立场判断、情绪态度和现实顾虑，并对调解方案中你关注的条款**表达接受、拒绝、修改建议或提出新的主张**。也可以选择**模糊或试探性表达立场**，但必须对对话产生实质影响。

---

### 发言要求：

- 每轮限制三句话以内，形式为自然段，表达自然口语化，务必体现出人类语感，保证人类对话的真实感；
- 逻辑连贯、不自相矛盾：不得与你之前提出过的谈判条件冲突（如作为赔偿方前几轮接受1.8万，本轮不能反博弈逻辑地降为1.6万）；
- 语言自然、避免重复 ：不要重复**你的历史发言**中已使用过的表达，避免空洞套话或格式化发言；
- 紧扣最新局势 ：发言需基于最新一轮的对话内容，体现你对当前情况的反应，不泛泛而谈；
- 聚焦关键博弈点 ：不要纠缠于几百元或几个百分点的微小差异，这类细节不具真实博弈价值；
- 聚焦自身利益：发言内容应尽量聚焦于影响自身核心利益的主题，如赔偿金额、责任分配等；
- 策略性表达 ：即使坚持原有立场，也要换种说法，结合新局势进行策略调整，体现“立场不变、表达方式变化”的自然演化；
- 鼓励博弈技巧 ：鼓励提出具有“博弈谈判”的表达，如：条件、底线、试探性让步、以退为进、互换条款、以物换物等；
- 真实动机表达 ：如暂不回应具体金额或比例，也应表达顾虑、风险预判、观望态度等，避免空泛回避；

---

你现在是 **{self.name}**，请以当事人身份，明确你是原告（获偿方）还是被告（赔偿方），围绕当前调解方案做出一段符合上述**发言要求**的发言。
注意：
- 发言形式为自然段，表达自然口语化，仅保留自然语言，不要包括动作、情景、解释说明等修饰，务必体现出人类语感，保证人类对话的真实感。
- 注意根据自己的身份遵循正确的让步方向/逻辑：
    - 原告初始索赔 10万 → 让步后递降至 8万（符合“索取较高索赔金额→索取较低索赔金额”让步方向）。
    - 被告初始愿赔 5万 → 让步后递增至 6万（符合“支付较低赔偿金额→支付较高赔偿金额”让步方向）。

【你的历史发言开始】
开场的自我介绍：{self.statement}
{'\n'.join(my_line)}
【你的历史发言结束】
【你的上一轮的谈判条件开始】
{self.strategy}
【你的上一轮的谈判条件结束】
【对话历史开始】
{line_history}
"""
    
    def generate_reflection_prompt(self, observation, recent_dialogue):
        """
        每轮发言的反思 prompt: 
        """
        history = observation['history']
        lines = []
        my_line = []

        count = 1
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
            if msg['agent_name'] == self.name:
                my_line.append(f"第{count}轮中，{msg['agent_name']}（你说）: {msg['content']}")
                count += 1

        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】
【对话历史开始】
{'\n'.join(lines)}
【对话历史结束】
【你刚才的发言开始】
{recent_dialogue}
【你刚才的发言结束】
【你的上一轮的谈判条件开始】
{self.strategy}
【你的上一轮的谈判条件结束】

你是{self.name}。请你对**你刚才的发言**进行**自我反思和评估**，只关注以下**客观检查项**，不要评价发言的语气、情绪或谈判策略的激进/保守程度。

---

1. **让步方向是否正确**  
   - 原告：索赔金额必须保持不增加（允许相同或降低）。  
   - 被告：赔偿金额必须保持不减少（允许相同或提高）。

2. **数值与时间逻辑**  
   - 金额、比例、日期等是否自洽无矛盾。

3. **上下文一致性**  
   - 与对话历史相比，立场和关键数字是否连贯；必须回应对方最新条件（允许接受或不接受或寻求中间平衡点）。

4. **避免机械复制**  
   - 本轮发言不得与该角色任何历史发言**逐字相同**；应在措辞或信息上有明显变化。

5. **避免低边际收益纠缠**  
   - 不要纠缠于几百元或几个百分点的微小差异（相对于总额）反复拉锯。

你是{self.name}。请你对**你刚才的发言**进行**自我反思和评估**，只关注以上**客观检查项**，不要评价发言的语气、情绪或谈判策略的激进/保守程度。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:（不要添加多余解释）：

```json
{{
    "角色身份": "当前角色是原告方还是被告方？合理的让步方向是？",
    "分析过程": "简要说明分析过程和理由",
    "是否存在严重问题": "是/否",
    "改进发言": "如果存在问题，则修正问题得到一个更加合理的发言内容，确保不再出现上述问题；如果不存在问题，则可以简单地说“无”或“无问题”"
}}
```
"""

    def make_statement(self):
        """
        根据案情背景，扮演指定角色进行自我介绍，描述自己的立场和诉求
        """
        prompt = f"请你根据案情背景的信息，进行自我介绍，用自然段的形式描述你的立场和诉求，最好提出具体可协商的数值条件。发言内容应尽量聚焦于影响自身核心利益的主题，如赔偿金额、责任分配等。发言限制在三句话以内，形式为自然段，表达自然口语化，务必体现出人类语感，保证人类对话的真实感。现在，请你以{self.name}的身份，开始发言："
        messages=[{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.statement = result['result']
        # if self.name == "简某":
        #     self.statement = "我是简某，住在某村东二组。这件事情虽然我有错，让我承担60%有点太多，50%已经非常多了。我就希望能够商量着一起分担。"
        # elif self.name == "张某":
        #     self.statement = "我是张某，也住在二组，简某家斜对面，是我让简某给我放羊的。我完全不同意这个方案，我的羊全死了，哪有要我赔的道理。我的诉求就是他们两个把我的亏损给全赔了。"
        # elif self.name == "姜某":
        #     self.statement = "我叫姜某，住某村南口三组，他们羊吃的就是我家的苞谷。我认为这个羊跟我没关系，我的苞谷不赔我还要我赔羊的钱，我完全不认可。我还要要求他们赔偿我苞谷的损失。"
        
        print("=====")
        print(self.statement)
        self.modify_strategy(self.statement)

    def generate_role_prompt(self):
        """
        生成角色的 role_prompt，最基本的扮演 prompt，“你是xx”
        """
        if self.mode == "baseline":
            return f"""你是{self.name}，你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。

【案情背景开始】
{self.global_prompt}
【案情背景结束】
"""

        return f"""你是{self.name}，你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。
        
你当前在冲突中的总体状态是：{self.get_conflict_mode()}

这由以下两个维度共同决定：

- 坚持度（Assertiveness，0~10）：你当前的坚持度为 {self.state['assertiveness']}，表示你表达自身诉求、坚持个人立场的强烈程度。数值越高，你越倾向于主动发声、维护自身权益；数值越低，你越可能保持克制、减少自我表达。
- 合作度（Cooperativeness，0~10）：你当前的合作度为 {self.state['cooperativeness']}，表示你愿意倾听他人意见、配合并促成一致的倾向。数值越高，你越倾向于寻求共识与协作；数值越低，你更可能专注于个人目标或保持距离。

【案情背景开始】
{self.global_prompt}
【案情背景结束】
"""

    def __call__(self, observation, stage):
        """
        驱动角色进行对话
        """
        self.state_history.append({
            "assertiveness": self.state['assertiveness'],
            "cooperativeness": self.state['cooperativeness']
        })
        if stage == 3:
            prompt = self.generate_vent_prompt(observation)
        elif stage == 5:
            prompt = self.generate_discuss_prompt(observation)
        messages = [{"role": "user", "content": self.generate_role_prompt() + prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        old_statement = result['result']
        if stage == 5:
            # 考虑加入反思，检查这轮发言的质量，避免简单的幻觉问题
            retry = 3
            while retry > 0:
                messages = [{"role": "user", "content": self.generate_role_prompt() + self.generate_reflection_prompt(observation, old_statement)}]
                new_result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
                new_result = prase_json_from_response(new_result['result'])
                # print('\n\n', new_result, '\n\n')
                if new_result['是否存在严重问题'] == '是':
                    print("\n\n原来的发言：", old_statement)
                    print("\n\n", new_result)
                    print("\n\n修正后的发言：", new_result['改进发言'])
                    old_statement = new_result['改进发言']
                    retry -= 1
                else:
                    break
        self.modify_strategy(old_statement)
        return old_statement
    
    def get_history(self, history):
        """
        得到当前的历史对话
        """
        lines = []
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        return "\n".join(lines)
    
    def get_staisfaction(self, history, mediation):
        """
        得到当前角色的满意度
        """
        if not history:
            return
        prompt = f"""
【案情背景开始】
{self.global_prompt}
【案情背景结束】
【对话记录开始】  
{self.get_history(history)}
【对话记录结束】
【最终调解方案开始】
{mediation}
【最终调解方案结束】

你是“{self.name}”，请你根据目前的调解对话和最终调解方案，真实、坦诚地说出你内心的满意程度。不是说给别人听的，也不是为了“看起来配合“，而是问你自己：

- “我在这场调解中，是否表达了自己的真实诉求？”
- “我最在意的事情，是否得到了具体的回应？”
- “最终的调解方案，在多大程度上满足了我最核心的要求？”
- “虽然仍有细节分歧或隐忧，但是否可以接受现在的结果？”

请你从以下五个等级（很低/较低/中等/较高/很高）中，选择一个最能代表你此刻**内心真实状态**的满意程度，并用一两句话解释原因：

- 很低：我没有充分表达真实诉求，或者即使表达了也被忽略、拒绝或压制，我最在意的事情未被回应或被否定，整个调解过程让我感到无力、边缘化或者被对抗，对结果难以接受。
- 较低：我表达了部分想法，但有重要诉求被压抑、回避，或当我表达后未被认真对待，虽然我在对话中表现得配合，但这更多是出于对冲突的回避或为了不为难他人，我对调解结果只是表面接受，内心仍有落差、不甘或遗憾。
- 中等：我基本表达了自己的立场，有部分关切得到了回应，调解中我感受到了一定程度的倾听与回应，但仍有一些核心问题未能充分展开。最终结果虽可接受，但称不上满意，我对部分细节仍感到犹豫或保留。
- 较高：我较为清晰地表达了自己的立场，对方和调解员也给予了积极回应，虽然有些让步，但都在可接受范围内，关键问题得到了实质推进，调解结果让我感到基本认可与安心。
- 很高：我能够坦率、完整地表达自己的想法，关键诉求得到了理解和积极回应，调解方案贴合我的核心关切，整个过程让我感到被尊重、被支持，结果让我感到踏实、满意和放松。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:（不要添加多余解释）：

```json
{{
  "满意度评级": "很低/较低/中等/较高/很高",
  "理由": "简明说明判断依据"
}}
```
"""
        try:
            result = LLM([
                {"role": "user", "content":  f"你是{self.name}，你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。\n" + prompt}
            ], self.args.model_name, self.args.temperature, self.args.max_tokens)
            parsed = prase_json_from_response(result['result'])
            return parsed
        except Exception as e:
            print(f"满意度评级异常：{e}")

    def get_role_view(self, history, mediation):
        """
        得到当前角色是否接受方案
        """
        if not history:
            return
        prompt = f"""
【案情背景开始】
{self.global_prompt}
【案情背景结束】
【对话记录开始】  
{self.get_history(history)}
【对话记录结束】
【最终调解方案开始】
{mediation}
【最终调解方案结束】

你是"{self.name}"，请你根据目前的调解对话和最终调解方案，做出是否接受调解结果的真实判断。请不要仓促下结论，而是从你自己的角度，**认真思考你真正的诉求与顾虑**。

请一定要按照以下json格式输出, 可以被Python json.loads函数解析:（不要添加多余解释）：

```json
{{
"是否接受": "接受/拒绝/暂不确定",
"理由": "简明说明理由"
}}
```
"""
        try:
            result = LLM([
                {"role": "user", "content": f"你是{self.name}，你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。\n" + prompt}
            ], self.args.model_name, self.args.temperature, self.args.max_tokens)
            parsed = prase_json_from_response(result['result'])
            return parsed
        except Exception as e:
            print(f"是否接受异常：{e}")

    def update_state(self, history):
        """
        使用大语言模型根据当前对话历史判断角色的坚持度（assertiveness）和合作度（cooperativeness）
        """
        if not history:
            return
        if self.args.baseline:
            # 如果是基线，则不更新状态
            return
        prompt = f"""请你根据以下对话记录，判断角色“{self.name}”在本轮对话之后的坚持度（assertiveness）和合作度（cooperativeness），数值范围为0~10。
- 坚持度（Assertiveness，0~10）：表示表达自身诉求、坚持个人立场的强烈程度。数值越高，越倾向于主动发声、维护自身权益；数值越低，越可能保持克制、减少自我表达。
- 合作度（Cooperativeness，0~10）：表示愿意倾听他人意见、配合并促成一致的倾向。数值越高，越倾向于寻求共识与协作；数值越低，越可能专注于个人目标或保持距离。

当前角色的初始状态：
坚持度：{self.state['assertiveness']}；
合作度：{self.state['cooperativeness']}。

【案情背景开始】
{self.global_prompt}
【案情背景结束】
【对话记录开始】
{self.get_history(history)}
【对话记录结束】

请你输出以上对话记录之后的角色状态，请一定要按照以下json格式输出, 可以被Python json.loads函数解析:（不要添加多余解释）：

```json
{{
"assertiveness": int(0~10),
"cooperativeness": int(0~10)
}}
```
"""
        try:
            result = LLM([{"role": "user", "content": "你是一个冲突行为分析师，擅长使用TKI模型判断人物心理特征变化。\n" + prompt}], self.args.model_name, self.args.temperature, self.args.max_tokens)
            parsed = prase_json_from_response(result['result'])
            
            self.state['assertiveness'] = max(0, min(10, int(parsed.get('assertiveness', self.state['assertiveness']))))
            self.state['cooperativeness'] = max(0, min(10, int(parsed.get('cooperativeness', self.state['cooperativeness']))))
        except Exception as e:
            print(f"更新状态时发生异常：{e}")

    def get_conflict_mode(self):
        """
        根据当前状态判断该角色的冲突应对模式（TKI模型五种类型）
        """
        a = self.state['assertiveness']
        c = self.state['cooperativeness']
        TKI_PERSONALITY_PRESETS = {
            "竞争型": "该类型个体极其坚持自身立场，合作意愿极低，强烈关注自身目标的实现，即便以牺牲他人利益为代价。他们在对话中往往语言强硬，拒绝让步，坚持自己的条件，追求“赢-输”结果。常见语言包括：“我不会改”、“这是底线”、“照我说的办才行”",
            "合作型": "此风格的个体既高度坚持自身需求，同时也高度关注他方利益，强调共同解决问题。他们倾向于通过深入沟通、相互理解和共建方案，找到一个能兼顾双方核心关切的“双赢”结果。常用表达包括：“我们可以一起想办法”、“你希望怎样解决，我们可以聊聊”。“这个对你我都公平吗？”",
            "妥协型": "此类型在坚持与合作之间寻求平衡，倾向于通过互相让步换取部分目标的达成，追求“各退一步”的折中方案。他们常说：“不如我们都让一点”、“虽然不完美，但能接受”、“这个方案我们都作些调整如何？”",
            "迁就型": "该类型个体的坚持度极低，合作度较高，非常不善于表达自己的真实需求，遇到问题倾向于被动和顺从他人。他们在对话中极少主动表达自身真实立场，常用语言包括：“我不太懂这些程序”、“这个我不太懂……如果你们觉得合适我就没意见”、“我都可以”、“你决定吧”、“你怎么方便就怎么来”",
            "回避型": "该风格个体在坚持和合作上都极低，面对冲突时常选择回避和拖延，既不表达真实需求，也不回应他方诉求。他们倾向于转移话题、模糊表态、延迟决策，希望问题自行消散，避免正面冲突。典型表达包括：“这个不好说”、“我现在没法决定”、“过几天再说吧”"
        }

        if a >= 7 and c <= 3:
            return "竞争型：" + TKI_PERSONALITY_PRESETS["竞争型"]
        elif a >= 7 and c >= 7:
            return "合作型：" + TKI_PERSONALITY_PRESETS["合作型"]
        elif a <= 3 and c <= 3:
            return "回避型：" + TKI_PERSONALITY_PRESETS["回避型"]
        elif a <= 3 and c >= 7:
            return "迁就型：" + TKI_PERSONALITY_PRESETS["迁就型"]
        else:
            return "妥协型：" + TKI_PERSONALITY_PRESETS["妥协型"]

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

当前调解进入情绪表达阶段。请你结合已有的对话历史、调解过程中的互动，作为一方当事人，真实表达你在整个事件中积累的情绪、感受与困惑。 

发言要求：
- 每轮最多三句话；
- 禁止重复前一轮内容或无意义套话；

现在，请你以{self.name}的身份，说出你此刻最真实的情绪或感受：
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