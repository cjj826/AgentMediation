from zhipuai import ZhipuAI
import json
import re
import random
from openai import OpenAI
import httpx
import src.globals as globals

openai_client = OpenAI(
    base_url="your_base_url",
    api_key="your_key")


def LLM(query, model_name, temperature, max_tokens):
    if isinstance(query, list):
        messages = query
    else:
        messages = [{"role": "user","content": query}]

    # diff model
    if model_name.find("gpt") != -1 or model_name.find("deepseek") != -1 or model_name.find("openrouter") != -1:
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature = temperature,
            max_tokens=max_tokens,
        )

    elif model_name.find('claude') != -1:
        response = claude_client.chat.completions.create(
                model=model_name, 
                messages=messages,
                temperature = temperature,
                max_tokens=max_tokens,
            )
    
    elif model_name.find('qwen') != -1:
        response = qianwen_client.chat.completions.create(
            model=model_name, # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=messages,
            temperature = temperature,
            max_tokens=max_tokens,
        )
    
    elif model_name.find('glm') != -1 or model_name.find('GLM') != -1:
        client = ZhipuAI(api_key="your_key")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False,
            temperature = temperature,
            max_tokens=max_tokens,
        )

    globals.total_token += response.usage.total_tokens
    globals.this_question_input_token += response.usage.prompt_tokens
    globals.this_question_output_token += response.usage.completion_tokens

    res =  {
        "result": response.choices[0].message.content.strip(),
    }

    if res['result'].find('</think>') != -1:
        res['result'] = res['result'].split('</think>')[-1]

    return res

def prase_json_from_response(rsp: str):
    pattern = r"```json(.*?)```"
    rsp_json = None
    try:
        match = re.search(pattern, rsp, re.DOTALL)
        if match is not None:
            try:
                rsp_json = json.loads(match.group(1).strip())
            except:
                pass
        else:
            rsp_json = json.loads(rsp)
        return rsp_json
    except json.JSONDecodeError as e: 
        try:
            match = re.search(r"\{(.*?)\}", rsp, re.DOTALL)
            if match:
                content = "[{" + match.group(1) + "}]"
                return json.loads(content)
        except:
            pass
        print(rsp)
        raise ("Json Decode Error: {error}".format(error=e))
