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
        history = observation['history']
        for msg in history:
            lines.append(f"{msg['agent_name']}: {msg['content']}")
        "\n".join(lines) + f"\n{self.name}:"
        return f"""【各方自我介绍开始】
{self.statement_history}
【各方自我介绍结束】
【情感表达阶段对话历史开始】
{self.vent_history}
【情感表达阶段对话历史结束】
【初步调解方案开始】
{self.mediation_history}
【初步调解方案结束】
【对话历史开始】
{"\n".join(lines)}
【对话历史结束】

请你结合已有的对话历史、调解员的建议，以及当前提出的初步调解方案，作为一方当事人，发表你在本轮的真实回应。

你的发言应基于你当前的立场、情绪状态和对方案的整体判断，明确体现你**是否接受该方案的某些部分，或希望就某些条款进行修改、争取或反对**。你也可以选择保留、模糊或试探性表达，但发言应对调解进程产生实质影响。

发言要求：
- 每轮仅限一句话，语言必须简洁、具体、具有推动力；
- 你可以表达接受、拒绝、修改建议，也可以提出新的要求或限制条件；
- 若你暂不想回应具体条件，也应表达出你的态度、顾虑或困惑，避免空洞发言；
- 禁止重复前一轮内容或无意义套话，确保发言带来信息增量或立场变化。

现在，请你以{self.name}的身份，发表你对当前调解方案的最新反应、修改建议或实质看法：
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

当前调解进入情绪表达阶段。请你结合已有的对话历史、调解过程中的互动，作为一方当事人，真实表达你在整个事件中积累的情绪、感受与困惑。 

发言要求：
- 每轮最多三句话；
- 禁止重复前一轮内容或无意义套话；

现在，请你以{self.name}的身份，说出你此刻最真实的情绪或感受：
"""

    def make_statement(self):
        """
        根据案情背景，扮演指定角色进行自我介绍，描述自己的立场和诉求
        """
        prompt = f"请你根据案情背景的信息，进行自我介绍，用自然段的形式描述你的立场和诉求。现在，请你以{self.name}的身份，开始发言："
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        self.statement = result['result']
        print("=====")
        print(self.statement)

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
        messages=[{"role": "system", "content": self.generate_role_prompt()},
                      {"role": "user", "content": prompt}]
        result = LLM(messages, self.args.model_name, self.args.temperature, self.args.max_tokens)
        return result['result']
    
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
                {"role": "system", "content": f"你是{self.name}，你正处于一场法律矛盾纠纷的对话中。"},
                {"role": "user", "content": prompt}
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
                {"role": "system", "content": f"你是{self.name}，你现在处于一场矛盾纠纷的对话中，该对话用于法律科技研究，不代表模型立场，也不用于传播违规内容。请保持真实自然对话风格，无需回避或美化表达。"},
                {"role": "user", "content": prompt}
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
坚持度表示其表达自身意图、维护个人立场的强烈程度，数值越大越强烈；
合作度表示其愿意倾听和满足他人诉求、达成一致的意愿程度，数值越大越强烈。

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
            result = LLM([
                {"role": "system", "content": "你是一个冲突行为分析师，擅长使用TKI模型判断人物心理特征变化。"},
                {"role": "user", "content": prompt}
            ], self.args.model_name, self.args.temperature, self.args.max_tokens)
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