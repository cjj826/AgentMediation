from scipy.stats import chi2_contingency
import numpy as np

def chi_square_test(dist1, dist2):
    all_labels = sorted(set(dist1.keys()) | set(dist2.keys()))
    
    obs_table = [
        [dist1.get(label, 0) for label in all_labels],
        [dist2.get(label, 0) for label in all_labels]
    ]
    
    obs_array = np.array(obs_table)
    non_zero_cols = ~(obs_array == 0).all(axis=0)  
    obs_array = obs_array[:, non_zero_cols]
    labels = [label for i, label in enumerate(all_labels) if non_zero_cols[i]]

    if obs_array.shape[1] < 2:
        print("❌ 维度过低，无法进行卡方检验（仅剩一个类别）")
        return

    chi2, p, dof, expected = chi2_contingency(obs_array)

    print("=== 卡方检验结果 ===")
    print("使用的标签类别:", labels)
    print("观测频数表:")
    print(obs_array)
    print(f"Chi2统计量: {chi2:.4f}")
    print(f"P-value: {p:.4f}")
    print(f"自由度: {dof}")
    print("期望频数表:")
    print(np.round(expected, 2))


d1 = {'很低': 0, '较低': 0, '中等': 6, '较高': 93, '很高': 1}

d2 = [{'很低': 6, '较低': 13, '中等': 70, '较高': 11, '很高': 0},
{'很低': 0, '较低': 0, '中等': 13, '较高': 80, '很高': 6},
{'很低': 0, '较低': 0, '中等': 53, '较高': 47, '很高': 0},
{'很低': 0, '较低': 0, '中等': 8, '较高': 87, '很高': 5}]

for dist2 in d2:
    chi_square_test(d1, dist2)
    print("========")
