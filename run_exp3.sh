# The Effect of Different Backbone LLM and Domain Expertise
python run.py --baseline --multi --date 2025 --model_name glm-4-flash &
python run.py --baseline --multi --date 2025 --model_name glm-4-plus &
python run.py --baseline --multi --date 2025 --model_name deepseek-v3-0324 &
python run.py --baseline --multi --date 2025 --model_name gpt-4o-mini-2024-07-18 &
wait
python run.py --baseline --multi --date 2025 --model_name openrouter:qwen-plus &
python run.py --baseline --multi --date 2025 --model_name openrouter:deepseek-r1 &
python run.py --baseline --multi --date 2025 --model_name openrouter:llama-3.1-70b-instruct &
wait


python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:llama-3.1-70b-instruct 
python judge_mediator.py --baseline --multi --date 2025 --model_name glm-4-flash 
python judge_mediator.py --baseline --multi --date 2025 --model_name deepseek-v3-0324 
python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:deepseek-r1

python judge_mediator.py --baseline --multi --date 2025 --model_name glm-4-plus  
python judge_mediator.py --baseline --multi --date 2025 --model_name gpt-4o-mini-2024-07-18  
python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:qwen-plus 


python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:llama-3.1-70b-instruct --retrieve --topk 10
python judge_mediator.py --baseline --multi --date 2025 --model_name glm-4-flash --retrieve --topk 10
python judge_mediator.py --baseline --multi --date 2025 --model_name deepseek-v3-0324 --retrieve --topk 10
python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:deepseek-r1 --retrieve --topk 10

python judge_mediator.py --baseline --multi --date 2025 --model_name glm-4-plus --retrieve --topk 10
python judge_mediator.py --baseline --multi --date 2025 --model_name gpt-4o-mini-2024-07-18 --retrieve --topk 10
python judge_mediator.py --baseline --multi --date 2025 --model_name openrouter:qwen-plus --retrieve --topk 10
