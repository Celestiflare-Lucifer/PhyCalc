# -*- coding: utf-8 -*-
"""
实验中文名：不确定度估算与测量结果表示
实验英文名：Uncertainty Estimation and Result Expression

文件名：1.2_不确定度估算与测量结果表示_uncertainty_estimation_core.py
章节：第 1 章第 2 节

依据教材：冯放, 牟艳秋. 大学物理实验[M]. 北京: 高等教育出版社, 2017.

本实验实现以下内容：
    1) 多次测量（n ≥ 2）：A 类 + B 类不确定度合成
       u_A = √[ Σ(xi - x̄)² / (n(n-1)) ]
       u_B = Δ_仪 / k（k 由仪器误差的分布类型决定）
       u   = √(u_A² + u_B²)
    2) 单次测量（n = 1）：仅由 B 类不确定度决定
    3) 相对不确定度：U_r = u / x̄ × 100%
    4) 测量结果表示：x = x̄ ± u  (置信概率 P = 0.683)
"""

import math
import sys


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '不确定度估算与测量结果表示',
        'en': 'Uncertainty Estimation and Result Expression',
    },
    'chapter': 1,
    'section': 2,

    'inputs': [
        # -------- 直接测量数据 --------
        {
            'name': 'data',
            'label': {
                'zh': '直接测量数据 x',
                'en': 'Direct Measurement Data x',
            },
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'x', 'en': 'x'},
            'unit': '',
            'hint': {
                'zh': '请输入对同一物理量重复测量的数据（至少 2 个以计算 A 类不确定度）。\n'
                      '若为单次测量，可只填 1 个数据，此时 A 类不确定度记为 0。\n'
                      '留空的输入框会被自动忽略。',
                'en': 'Enter repeated measurements of the same quantity '
                      '(at least 2 for Type A). For single measurement, '
                      'input just 1 value and Type A is set to 0. '
                      'Empty rows are ignored.',
            },
            'default': [],
        },
        # -------- 仪器误差 --------
        {
            'name': 'instrument_error',
            'label': {
                'zh': '仪器误差 Δ仪',
                'en': 'Instrument Error Δ',
            },
            'type': 'float',
            'unit': '',
            'hint': {
                'zh': '按仪器说明书给出，或按教材表 1.2.1 常见仪器的极限误差填写。',
                'en': 'See instrument manual or Table 1.2.1 in the textbook.',
            },
            'default': 0.01,
        },
        # -------- 仪器误差分布 --------
        {
            'name': 'distribution',
            'label': {
                'zh': '仪器误差分布',
                'en': 'Error Distribution',
            },
            'type': 'choice',
            'options': [
                {'value': 'uniform',
                 'label': {'zh': '均匀分布（÷√3）', 'en': 'Uniform (÷√3)'}},
                {'value': 'normal',
                 'label': {'zh': '正态分布（÷3）', 'en': 'Normal (÷3)'}},
                {'value': 'triangular',
                 'label': {'zh': '三角分布（÷√6）', 'en': 'Triangular (÷√6)'}},
                {'value': 'arcsine',
                 'label': {'zh': '反正弦分布（÷√2）', 'en': 'Arcsine (÷√2)'}},
            ],
            'hint': {
                'zh': '默认按教材推荐采用均匀分布。若仪器说明书明确其他分布，'
                      '请按教材式(1.2.6)下方的说明选择。',
                'en': 'Default is uniform distribution as recommended. '
                      'Choose others if the manual specifies.',
            },
            'default': 'uniform',
        },
        # -------- 物理量单位（用于最终结果表达式） --------
        {
            'name': 'unit_name',
            'label': {
                'zh': '物理量单位',
                'en': 'Unit',
            },
            'type': 'text',
            'hint': {
                'zh': '可选，用于在最终结果中附带单位（例如 g、mm、V）。留空则不加单位。',
                'en': 'Optional. Used in the final result expression '
                      '(e.g., g, mm, V). Leave empty to omit.',
            },
            'default': '',
        },
    ],

    'outputs': [
        {'name': 'avg', 'label': {'zh': '平均值 x̄', 'en': 'Average x̄'}},
        {'name': 'S', 'label': {'zh': '标准偏差 S', 'en': 'Standard Deviation S'}},
        {'name': 'A', 'label': {'zh': 'A 类不确定度 u_A', 'en': 'Type A Uncertainty u_A'}},
        {'name': 'B', 'label': {'zh': 'B 类不确定度 u_B', 'en': 'Type B Uncertainty u_B'}},
        {'name': 'total', 'label': {'zh': '合成不确定度 u', 'en': 'Combined Uncertainty u'}},
        {'name': 'Ur_percent', 'label': {'zh': '相对不确定度 U_r (%)', 'en': 'Relative Uncertainty U_r (%)'}},
        {'name': 'n', 'label': {'zh': '数据个数 n', 'en': 'Number of data n'}},
        {'name': 'result_expr', 'label': {'zh': '测量结果表示', 'en': 'Measurement Result'}},
        {'name': 'confidence', 'label': {'zh': '置信概率 P', 'en': 'Confidence Probability P'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(data, instrument_error, distribution='uniform',
              unit_name='', precision=3):
    """
    不确定度估算与测量结果表示。

    参数:
        data            : list of float，直接测量数据（至少 1 个）
        instrument_error: float，仪器误差 Δ_仪
        distribution    : str，仪器误差的分布类型（'uniform'/'normal'/
                          'triangular'/'arcsine'）
        unit_name       : str，物理量单位（可选）
        precision       : int，保留小数位数（仅用于显示）

    返回:
        dict 或 None
    """
    if not data:
        return None

    n = len(data)
    avg = sum(data) / n

    # ---------- A 类不确定度 ----------
    if n >= 2:
        sum_sq = sum((x - avg) ** 2 for x in data)
        S = math.sqrt(sum_sq / (n - 1))
        A = math.sqrt(sum_sq / (n * (n - 1)))
    else:
        S = 0.0
        A = 0.0

    # ---------- B 类不确定度 ----------
    divisors = {
        'uniform': math.sqrt(3),
        'normal': 3.0,
        'triangular': math.sqrt(6),
        'arcsine': math.sqrt(2),
    }
    k = divisors.get(distribution, math.sqrt(3))
    B = instrument_error / k

    # ---------- 合成不确定度 ----------
    total = math.sqrt(A ** 2 + B ** 2)

    # ---------- 相对不确定度 ----------
    if abs(avg) > 1e-15:
        Ur = total / abs(avg) * 100.0
    else:
        Ur = 0.0

    # ---------- 测量结果表示 ----------
    unit_suffix = f" {unit_name}" if unit_name else ""
    result_expr = (f"x = ({avg:.{precision}f} ± "
                   f"{total:.{precision}f}){unit_suffix}")

    return {
        'avg': avg,
        'S': S,
        'A': A,
        'B': B,
        'total': total,
        'Ur_percent': Ur,
        'n': n,
        'result_expr': result_expr,
        'confidence': 0.683,
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("不确定度估算与测量结果表示")
    print("(Uncertainty Estimation and Result Expression)")
    print("=" * 50)

    try:
        s = input("请输入直接测量数据（以空格分隔，例如：27.03 27.08 27.07 27.01 27.05）：").strip()
        if not s:
            print("未输入数据。")
            return
        data = [float(x) for x in s.split()]

        instr = float(input("请输入仪器误差 Δ_仪（例如 0.04）：").strip())

        print("请选择仪器误差的分布类型：")
        options = UI_SPEC['inputs'][2]['options']
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt['label']['zh']}")
        idx = int(input("请输入编号（默认 1）：").strip() or "1")
        distribution = options[idx - 1]['value']

        unit_name = input("请输入物理量单位（例如 g，留空不加）：").strip()
    except (ValueError, IndexError):
        print("输入格式错误。")
        return

    result = calculate(data, instr, distribution, unit_name)
    if result is None:
        print("计算失败，请检查输入。")
        return

    print("=" * 50)
    print(f"平均值 x̄            : {result['avg']:.3f}")
    print(f"标准偏差 S          : {result['S']:.4f}")
    print(f"A 类不确定度 u_A    : {result['A']:.4f}")
    print(f"B 类不确定度 u_B    : {result['B']:.4f}")
    print(f"合成不确定度 u      : {result['total']:.4f}")
    print(f"相对不确定度 U_r    : {result['Ur_percent']:.2f}%")
    print(f"数据个数 n          : {result['n']}")
    print(f"测量结果表示        : {result['result_expr']}")
    print(f"置信概率 P          : {result['confidence']}")


if __name__ == "__main__":
    main()