# Baseline
python run.py --model_name deepseek-v3-0324 --baseline --multi --date 2025

# The Effect of Behavioral Strategies
python run.py --model_name deepseek-v3-0324 --assertiveness 5 --cooperativeness 5 --date 2025 --multi &
python run.py --model_name deepseek-v3-0324 --assertiveness 10 --cooperativeness 0 --date 2025 --multi &
python run.py --model_name deepseek-v3-0324 --assertiveness 0 --cooperativeness 10 --date 2025 --multi &
python run.py --model_name deepseek-v3-0324 --assertiveness 0 --cooperativeness 0 --date 2025 --multi &
python run.py --model_name deepseek-v3-0324 --assertiveness 10 --cooperativeness 10 --date 2025 --multi & 

# The Effect of Dispute Causes
python run.py --model_name deepseek-v3-0324 --baseline --conflict_type "信息冲突" --multi --date 2025 &
python run.py --model_name deepseek-v3-0324 --baseline --conflict_type "资源冲突" --multi --date 2025 &
python run.py --model_name deepseek-v3-0324 --baseline --conflict_type "主体行为问题" --multi --date 2025 &
python run.py --model_name deepseek-v3-0324 --baseline --conflict_type "法律缺陷" --multi --date 2025 &
python run.py --model_name deepseek-v3-0324 --baseline --conflict_type "其他外部因素" --multi --date 2025 &
wait

python eval.py --model_name deepseek-v3-0324 --assertiveness 5 --cooperativeness 5 --date 2025 --multi 
python eval.py --model_name deepseek-v3-0324 --assertiveness 10 --cooperativeness 0 --date 2025 --multi 
python eval.py --model_name deepseek-v3-0324 --assertiveness 0 --cooperativeness 10 --date 2025 --multi 
python eval.py --model_name deepseek-v3-0324 --assertiveness 0 --cooperativeness 0 --date 2025 --multi 
python eval.py --model_name deepseek-v3-0324 --assertiveness 10 --cooperativeness 10 --date 2025 --multi 
wait

python eval.py --model_name deepseek-v3-0324 --baseline --multi --date 2025 
python eval.py --model_name deepseek-v3-0324 --baseline --conflict_type "信息冲突" --multi --date 2025
python eval.py --model_name deepseek-v3-0324 --baseline --conflict_type "资源冲突" --multi --date 2025
python eval.py --model_name deepseek-v3-0324 --baseline --conflict_type "主体行为问题" --multi --date 2025
python eval.py --model_name deepseek-v3-0324 --baseline --conflict_type "法律缺陷" --multi --date 2025
python eval.py --model_name deepseek-v3-0324 --baseline --conflict_type "其他外部因素" --multi --date 2025
wait