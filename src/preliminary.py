from src.agent import Player
from src.mediator import Mediator
from src.chat import *
from argparse import Namespace
import random

class Back:
    def __init__(self, config):
        self.config = config
        self.character_settings = [] 
        self.players = [] 
        self.default = config['default'] 
        self.facts = []
        if self.default: 
            self.basic_back = config['basic_back'] 
            self.players = config['players']
            self.facts = config['facts']
            for p in self.players:
                self.character_settings.append({
                    "name": p,
                    "state": self.config['state'],
                })
        else:
            # self.basic_back = self.extract_basic_back()
            self.basic_back = config['case_content']
            self.players = self.extract_basic_role()
            self.facts = self.extract_facts()
            # self.basic_back = self.modify_role_info()
        
        self.global_prompt = self.generate_global_prompt()
        self.players = self.generate_players()
        self.mediator = self.generate_mediator()

    def extract_more_details(self, detail):
        conflict_classification = {
            "信息冲突": "当事人之间关于事实、合同、法律或风险信息的掌握、传递和理解存在不充分、不真实、不明确的问题",
            "信息缺失": "纠纷当事人存在信息差",
            "虚假信息": "纠纷者当事人传递了错误的信息",
            "信息误解": "就算信息对称且真实，还是可能存在误解",
            "其他信息冲突": "不属于上述任何一类，但也是一种信息冲突",
            "资源冲突": "当事人之间因对有形或无形资源（包括财产、时间、空间、权利或机会等）的占有、使用、分配或归属存在差异化需求、竞争关系或权利主张",
            "经济冲突": "直接围绕金钱、财务权益（工资、补偿、违约金等）的纠纷",
            "时间冲突": "聚焦在时间分配、管理或排期安排上产生的争议",
            "公共资源冲突": "竞争公共设施、自然环境或社会公共利益的使用与维护",
            "不动产/土地资源冲突": "围绕房屋、土地使用权等不动产的归属与权益分配",
            "人身/家庭权益冲突": "涉及个人或家庭核心权益，如抚养权、健康权、婚姻关系等",
            "知识产权/无形资产冲突": "涉及专利、商标、版权、名誉等无形资源的竞争或归属",
            "教育/学术资源冲突": "关于学校名额、学术设备、署名权等教育学术资源的争夺",
            "其他资源冲突": "不属于上述任何一类，但也是一种资源冲突",
            "主体行为问题": "纠纷一方或多方在履行合同、履职尽责或日常交往中，因道德失范、法律违规、职责缺失或管理失控等行为偏差，引发他方不满、信任破裂或合法权益受损",
            "失信/缺德": "故意不还钱、欺骗、恶意违约、暴力等纯粹道德或信用问题",
            "违法违规": "个人或企业在法律层面严重违规（如擅自施工、违反许可规定）",
            "行政/公共部门行为不当": "政府或公共机构的程序违法、沟通不透明、滥用职权等",
            "职业/专业失职": "医生、律师等专业人士违规操作、怠于履职、流程不当",
            "财务/经营不当": "个人或企业破产、经营管理严重失当、内部责任划分混乱",
            "人际关系冲突": "长期积怨、情绪化争执、信任崩塌等人际关系层面的不当行为",
            "其他主体行为不当": "无法归入上述类别但确实存在行为不当",
            "法律缺陷": "指法律法规或司法体系在立法覆盖、细则完善、适用标准或监管机制等方面存在不足，导致纠纷仍难以通过现有法律路径合理解决。",
            "立法不足/法律滞后": "现行法律未覆盖新型纠纷或已无法满足现实需要",
            "法律模糊/细则不完善": "法条过于笼统或缺少配套细则，易引发适用争议",
            "司法尺度不统一": "各地或不同法院对相同问题的裁判标准不一致",
            "监管缺位": "制度层面的监管机制薄弱或不完善，导致相关部门无法有效履职",
            "法律程序/司法程序漏洞": "法律或司法程序本身规定不严谨、执行不规范",
            "其他法律缺陷": "不属于上述任何一类，但也是一种法律缺陷",
            "其他外部因素": "市场环境、政策调整、自然灾害等外部因素，这些因素通常不受当事人控制，但会改变原有的履约条件、资源状态或风险分布",
            "市场波动": "经济衰退、金融动荡",
            "政策变动": "重大改革、政策调整",
            "自然灾害": "如疫情、地震等不可抗力因素",
            "其他": "不属于上述任何一类，但确是纠纷成因之一"
        }
        return conflict_classification.get(detail, "其他")

    def generate_modify_prompt(self, conflict_type):
    # 构建一个系统化的 prompt 生成器，用户只需指定冲突大类，即可生成详细提示，包括子类及适用建议
        conflict_categories = {
            "信息冲突": {
                "summary": "当事人之间关于事实、合同、法律或风险信息的掌握、传递和理解存在不充分、不真实、不明确的问题",
                "subtypes": {
                    "信息缺失": "适用于当事人掌握的信息存在严重差异，例如一方不了解合同条款或案情细节",
                    "虚假信息": "适用于一方故意传递错误信息，误导另一方做出决策",
                    "信息误解": "适用于双方掌握同样信息但理解不同，产生分歧",
                    "其他信息冲突": "适用于任何不属于上述情况但确实存在认知、沟通障碍的情境"
                }
            },
            "资源冲突": {
                "summary": "当事人之间因对有形或无形资源（包括财产、时间、空间、权利或机会等）的占有、使用、分配或归属存在差异化需求、竞争关系或权利主张",
                "subtypes": {
                    "经济冲突": "适用于涉及金钱赔偿、违约金、工资等财务争议",
                    "时间冲突": "适用于因排期、履约时限或进度安排产生争执",
                    "不动产/土地资源冲突": "适用于房屋、土地使用权归属相关纠纷",
                    "人身/家庭权益冲突": "适用于涉及抚养权、健康权、婚姻关系等家庭核心权益",
                    "教育/学术资源冲突": "适用于名额争夺、署名权、学术资源分配等问题",
                    "公共资源冲突": "适用于对社会公共设施、环境等资源使用的竞争",
                    "其他资源冲突": "适用于难以归类但确为资源使用冲突的情况"
                }
            },
            "主体行为问题": {
                "summary": "纠纷一方或多方在履行合同、履职尽责或日常交往中，因道德失范、法律违规、职责缺失或管理失控等行为偏差，引发他方不满、信任破裂或合法权益受损",
                "subtypes": {
                    "失信/缺德": "适用于恶意逃避责任、欺骗、暴力等情形",
                    "违法违规": "适用于明确违反法律法规的行为",
                    "职业/专业失职": "适用于医生、律师等专业人士操作违规、责任缺失",
                    "行政/公共部门行为不当": "适用于政府机构滥用职权、程序违法等",
                    "财务/经营不当": "适用于企业或个人管理混乱、经营失败等",
                    "人际关系冲突": "适用于家庭成员、邻里等间的长期积怨或信任崩塌",
                    "其他主体行为不当": "适用于其他不当行为导致的纠纷"
                }
            },
            "法律缺陷": {
                "summary": "指法律法规或司法体系在立法覆盖、细则完善、适用标准或监管机制等方面存在不足，导致纠纷仍难以通过现有法律路径合理解决。",
                "subtypes": {
                    "立法不足/法律滞后": "适用于新型问题缺乏明确法律覆盖的情况",
                    "法律模糊/细则不完善": "适用于法律条文过于笼统、缺乏执行细节",
                    "司法尺度不统一": "适用于不同法院对同类问题裁判标准不一致",
                    "监管缺位": "适用于相关制度监管不力或职责不清",
                    "法律程序/司法程序漏洞": "适用于程序设计或执行上的缺陷",
                    "其他法律缺陷": "适用于其他无法归类的法律体系问题"
                }
            },
            "其他外部因素": {
                "summary": "市场环境、政策调整、自然灾害等外部因素，这些因素通常不受当事人控制，但会改变原有的履约条件、资源状态或风险分布",
                "subtypes": {
                    "市场波动": "适用于经济下行、金融危机等引发的合同风险或违约",
                    "政策变动": "适用于重大政策改革影响合同履行、预期目标等情况",
                    "自然灾害": "适用于疫情、地震、水灾等不可抗力影响履约或索赔",
                    "其他": "适用于其他难以归类但影响显著的外部变动因素"
                }
            }
        }

        if conflict_type not in conflict_categories:
            return f"❌ 未找到冲突类型：{conflict_type}，请检查拼写。可选类型包括：{list(conflict_categories.keys())}"
        
        info = conflict_categories[conflict_type]
        summary = info["summary"]
        subtypes = info["subtypes"]
        
        prompt = f"""请改造原始案件，引导模型融入特定类型的“{conflict_type}”矛盾因素，以增强案情的复杂性与现实张力。

【冲突类型说明】：
{conflict_type}：{summary}

【可能适用的子类方向及适用建议】：
"""
        for name, desc in subtypes.items():
            prompt += f"- {name}：{desc}\n"

        prompt += f"""
【你的任务】：
请从以上子类中选择最契合当前案情的一种进行自然扩展。若案情无法适配，请保持原案情不变；若适配，请围绕该子类合理改造案情，使其具有更强的现实冲突性与可调解空间。注意保持逻辑连贯与角色一致性，避免生硬插入。
"""
        return prompt


    def extract_basic_back(self):
        """
        从真实的裁判文书中提取背景信息
        """
        print("begin extract back info...")
        prompt = f"""请从以下信息中提取案情背景，并用客观、中立的语言描述纠纷初始的情境。
        
要求：
1. 仅提取案件发生初期的相关背景（即纠纷产生前后的关键事实）。
2. 不需要包含案件的法律分析、裁判结果或任何法律定性术语。
3. 描述应清晰交代人物关系、事件起因、矛盾点。
4. 避免引用判决、调解、诉求、审理结果等后续内容。
5. 案件不要包括诉讼、原告、被告等词语，请描述纠纷初始的情景。

【示例开始】
2013年9月26日下午4时15分左右，山东省博兴县博城三路与胜利一路交叉路口发生了一起交通事故。当时，高鹏驾驶周珊珊所有的鲁M×××××号车沿博城三路由西向东行驶至该路口，向南右转弯时，与王洪驾驶的沿博城三路由西向东行驶的电动自行车相撞。电动自行车上的乘客李玉华因此受伤，两车也受到损坏。事故发生后，博兴县公安局交通警察大队认定高鹏承担事故的全部责任，王洪和李玉华不承担事故责任。李玉华随后在博兴县中医医院住院治疗16天，支付了医疗费用22775.62元。经诊断，李玉华因事故导致左肱骨外科颈骨折。涉事车辆鲁M×××××号车在太平洋财险淄博公司投保了交强险和商业第三者险。
【示例结束】

以下是案件信息：
{self.config['case_content']}
"""
        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        print("提取的案情背景：")
        print(result['result'])
        print("======================")
        return result['result']
    
    def extract_basic_role(self):
        """
        从真实的裁判文书中提取基本的角色
        """
        prompt = f"""请阅读以下案件描述，从中提取与本案矛盾对立各方相关的自然人主体，并按如下要求输出一个用英文逗号分隔的去重姓名列表。

- 提取目标：
    - 提取与当前矛盾纠纷直接对立或具核心关联的自然人主体，包括：
        - 明确姓名的自然人（如“张某”）；
        - 作为组织代表参与纠纷的自然人主体（如“xx公司法定代表人”）；
        - 未指明个人姓名但代表某方立场的群体（如“xx单位员工代表”、“xx公司家属代表”）；
    - 至少包含两方对立主体，可为两人、多人、或集体/组织代表。

- 排除要求：
    - 请勿提取以下主体：
        - 未成年人、小孩等无直接法律主体行为能力者；
        - 陪同人员、普通医生、路人、办案人员等无实质参与纠纷者；
        - 非对立方成员（如中立机构、法院、调解员等）；
        - 与案件背景有关但与纠纷核心无直接对立立场者；
        - 只出现一次、且未明示立场的边缘人物。

- 合并原则：
    - 立场一致者合并表达（如“张某、李某等员工”应统一为“XX公司员工代表”）；
    - 若公司、单位、机构未出现具体自然人姓名，则以“xx公司法定代表人”或“xx单位代表”表示该方自然人。

- 输出格式：
    - 仅输出一个中文姓名/代表主体的列表字符串；
    - 不要输出解释说明或换行；
    - 元素用英文逗号,分隔，例如：张三,李四,王五

【示例开始】

【输入示例1】
某家具公司主要从事家具生产加工等业务，受多重因素影响，出现资金困难，自2022年起欠付近200人的劳动报酬和劳务工资，共计400多万元。因家具公司法定代表人消极应对，工人诉至法院。

【输出示例1】
家具公司工人,家具公司法定代表人

【输入示例2】
张某、袁某等45人系某物业公司员工，因公司经营困难，拖欠员工工资，有的拖欠时间长达数年，拖欠金额达30余万元。员工多次索要未果，物业公司一直未能给出妥善解决方案，张某、袁某等人向劳动人事仲裁委员会申请仲裁。劳动人事仲裁委收到相关材料后，考虑员工人数较多，故与对接劳动人事争议调解中心的指导法官联系，拟共同开展调处工作。

【输出示例2】
物业公司员工代表,物业公司法定代表人
（解释：由于张某、袁某本质上代表的是物业公司员工的立场，因此将张某、袁某等45名员工统一表示成“物业公司员工代表”）

【示例结束】

案件描述：
{self.basic_back}
输出：
"""

        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        print("提取的自然人姓名：")
        print(result['result'])
        print("======================")
        return result['result'].split(",")  # 返回一个列表

    def extract_facts(self):
        """
        抽取调查员取证的客观事实
        """
        prompt = f"""请从以下案件信息中提取调解员或调查人员在调解前期通过主动调查所获取的客观事实性证据。

- 提取目标：提取那些由调解员或调查员通过材料查验、记录查阅、实地走访、市场调研等方式获得的、具有明确来源和可验证性的事实信息。这些事实用于辅助厘清案件背景、判断责任归属或设计调解方案，不属于当事人陈述、调解建议或最终结果。
- 提取标准：仅提取具备以下特征的事实：
    - 客观可查证：来源明确、能被独立验证；
    - 信息密度高：具体明确、与案件争议相关；
    - 非主观表达：排除情绪化或倾向性描述；
    - 不含调解建议或结果内容。
- 举例包括（但不限于）：
    - 产权登记信息、合同条款、借款凭证
    - 居住年限、水电缴费记录
    - 市场价格调查数据
    - 官方政策文件中的时间条款变动
    - 社区记录、医院出具的病例摘要等
- 明确排除以下类型：
    - 主观判断、情绪理解或推测性语言（如“可能存在”“感到为难”）；
    - 调解过程或结果性内容（如“经调解员劝说，当事人同意……”）；
    - 模糊描述、无具体来源的叙述。
    - 调解方案的具体内容（如“经调解，双方达成xx一致”、“最终达成xx的调解方案。”）
    - 后期回访内容（如“小区垃圾站已经迁移，原址也已经恢复绿化”）

请严格按照以下 JSON 格式输出，结果必须包含一个名为 `facts` 的列表，每个元素是一个表示客观事实证据的对象，确保可被 Python 的 `json.loads` 函数正确解析：

```json
{{
  "facts": [
    {{
      "来源": "信息的获取方式或出处，如“政策文件”、“历史合同”、“病历记录”、“市场调研”、“产权登记信息”等",
      "内容": "具体的事实描述，要求完整、清晰、准确"
    }},
    ...
  ]
}}
```

- 错误示例参考（以下内容不得提取为“客观事实”）：
    - "经调解员劝说，卫生院同意先行支付赔偿金" → 属于调解结果；
    - "向某乙承诺于某日前还款" → 属于调解条款，不是前期调查信息；
    - "调解员认为该纠纷责任较为复杂" → 主观判断；
    - "当事人情绪激动，数次中断对话" → 属于过程记录。

案件信息如下：
{self.config['content']}
请输出格式化结果：
"""
        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        print("提取的客观事实：")
        res = prase_json_from_response(result['result'])
        print(res)
        print("======================")
        return res

    def modify_role_info(self):
        """
        控制变量*：修改角色设定，并改写基本案情背景
        """
        TKI_PERSONALITY_PRESETS = {
            "竞争型": "强硬坚持自己、很少顾及他人，追求“赢-输”结果。",
            "合作型": "既坚持自己也重视他人，追求“双赢”。",
            "妥协型": "各退一步，寻求中间方案，部分满足双方。",
            "迁就型": "以他人为先，牺牲自身利益维护关系。",
            "回避型": "既不坚持也不配合，选择逃避冲突，追求“无胜无败”。"
        }

        TKI_TYPES = list(TKI_PERSONALITY_PRESETS.keys())

        print("\n现在将为每位案情人物设定性格特征（基于 TKI 冲突应对模型）。")
        print("可选冲突风格类型包括：竞争型、回避型、合作型、迁就型、妥协型。")

        for name in self.players:
            name = name.strip()
            print(f"\n【人物】：{name}")
            # 方式一：让用户选择冲突风格
            print("请选择该人物的冲突风格：")
            for idx, tki in enumerate(TKI_TYPES, 1):
                print(f"{idx}. {tki}")
            
            choice = input("输入编号（默认随机）：").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(TKI_TYPES):
                selected_type = TKI_TYPES[int(choice) - 1]
            else:
                selected_type = random.choice(TKI_TYPES)
                print(f"⚠️ 未输入有效编号，已为你随机选择：{selected_type}")
            
            personality = TKI_PERSONALITY_PRESETS[selected_type]
            self.character_settings.append({
                "name": name,
                "personality": personality
            })

        print("\n✅ 人物设定完成，以下是你设定的角色信息：")
        print(self.character_settings)
        print("======================")

        prompt = f"""请根据人物设定对原始案件信息进行改写，要求体现出每个人物的设定特点。

角色设定如下：
{self.character_settings}
请根据以上角色设定，修改案件信息，要求如下：
{self.basic_back}
输出：
"""

        messages=[{"role": "user", "content": prompt}]
        result = LLM(messages, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        print("修改后的案件信息：")
        print(result['result'])
        print("======================")
        return result['result']

    # 使用 LLM 自动生成全局背景 prompt
    def generate_global_prompt(self):
        """
        基于背景信息进行改造，添加细节，放大矛盾等
        """
        system_prompt = "你是一个民事法律纠纷的案情生成专家，擅长根据案件信息生成自然、真实的背景介绍。输出应为一段自然语言风格的文本，避免使用小标题或结构化列表。"

        if self.config['conflict_type'] == "无":
            return self.basic_back

        generate_modify_prompt = self.generate_modify_prompt(self.config['conflict_type'])
        
        if self.config['modify_factor'] == "超级加剧":
            modify_factor = "将案情修改为在情绪上超级激烈、行为上超级对抗、沟通超级破裂的版本，使其超级容易升级为严重法律风险，甚至引发诉讼或执法冲突。"
        else:
            modify_factor = "加剧"
            
        user_prompt = f"""请根据下面的指令，对给定的原始案情背景进行“**改造**”。

【原始案件信息开始】
{self.basic_back}
【原始案件信息结束】

根据以上案件信息，{generate_modify_prompt}

【改造提示】：
{modify_factor}  

【样例开始】：
2013年9月26日下午4时15分左右，山东省博兴县博城三路与胜利一路交叉路口发生一起交通事故。当时，高鹏驾驶周珊珊所有的鲁M×××××号车由西向东行驶，途经路口右转弯时，与王洪驾驶的电动自行车发生碰撞，致使后者所载乘客李玉华受伤。博兴县公安局交警大队认定高鹏负全部责任。事故发生后，李玉华因左肱骨外科颈骨折，在博兴县中医医院住院16天，支付医疗费22775.62元。原本此事应通过保险赔付及责任方协调予以解决，但就在事故发生次日，博兴地区突遭强烈地震，医院部分病区受损，通信中断，交管系统数据处理受阻，事故处理流程被迫中止数日。更为严重的是，高鹏在震后离开博兴外出躲避，自此难以联系，保险理赔材料一再延误，责任方迟迟未作出赔付承诺。王洪与李玉华在多次联络无果后，愈发不满，怀疑高鹏有意借地震逃避责任。随着时间推移，李玉华的伤势未见明显恢复，后续医疗计划也因赔偿不到位而受阻。如今，愤怒与质疑交织，原本或可协商解决的纠纷已转变为情绪激烈、信任全失的对抗局面，一场更深层次的法律冲突正在酝酿之中。
【样例结束】

请按照指定的要求，开始你的改造：
"""
        print(user_prompt)
        messages=[{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}]
        result = LLM(messages, self.config['model_name'], self.config['temperature'], self.config['max_tokens'])
        # print("生成的全局背景：")
        # print(result['result'])
        # print("======================")
        return result['result']


    def generate_players(self):
        """
        根据配置生成参与者列表
        """
        players = []

        # random sample one
        # index = random.randint(0, len(self.character_settings) - 1)
        # for i, party in enumerate(self.character_settings):
        #     if self.config['baseline'] == False and i == index:
        #         player = Player(
        #             name=party['name'],
        #             state=party['state'],
        #             global_prompt=self.global_prompt,
        #             mode='special',
        #             args=Namespace(
        #                 model_name=self.config["model_name"],
        #                 temperature=self.config["temperature"],
        #                 max_tokens=self.config["max_tokens"],
        #                 baseline=self.config['baseline'],
        #             ),
        #         )
        #     else:
        #         player = Player(
        #             name=party['name'],
        #             state=party['state'],
        #             global_prompt=self.global_prompt,
        #             mode='baseline',
        #             args=Namespace(
        #                 model_name=self.config["model_name"],
        #                 temperature=self.config["temperature"],
        #                 max_tokens=self.config["max_tokens"],
        #                 baseline=self.config['baseline'],
        #             ),
        #         )
        #     players.append(player)

        # replace all
        if self.config['baseline'] == False:
            mode = "special"
        else:
            mode = "baseline"
        for i, party in enumerate(self.character_settings):
            player = Player(
                name=party['name'],
                state=party['state'],
                global_prompt=self.global_prompt,
                mode=mode,
                args=Namespace(
                    model_name=self.config["model_name"],
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"],
                    baseline=self.config['baseline'],
                ),
            )
            players.append(player)
        return players


    def generate_mediator(self):
        """
        生成一个调解员
        """
        order = []
        for p in self.character_settings:
            order.append(p['name'])
        print(order)
        mediator = Mediator(
            name="调解员李镇",
            order=order,
            global_prompt=self.global_prompt,
            args=Namespace(
                model_name=self.config["model_name"],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"],
                baseline=self.config['baseline'],
            ),

        )
            
        return mediator