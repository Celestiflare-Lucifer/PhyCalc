# -*- coding: utf-8 -*-
"""
实验中文名：平均值与不确定度计算
实验英文名：Average and Uncertainty Calculation

本文件为平均值与不确定度计算实验的核心计算逻辑。
它遵循通用模板的框架，包含 UI_SPEC 定义、calculate 函数和独立运行入口。
"""

import math
import sys

# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '平均值与不确定度计算',
        'en': 'Average and Uncertainty Calculation'
    },
    'inputs': [
        {
            'name': 'data',
            'label': {'zh': '测量数据', 'en': 'Data'},
            'type': 'list',
            'initial': 6,
            'default': []
        },
        {
            'name': 'instrument_error',
            'label': {'zh': '仪器误差', 'en': 'Instrument Error'},
            'type': 'float',
            'initial': None,
            'default': 0.01
        }
    ],
    'outputs': [
        {'name': 'avg', 'label': {'zh': '平均值', 'en': 'Average'}},
        {'name': 'S', 'label': {'zh': '实验标准偏差 S', 'en': 'Std Deviation S'}},
        {'name': 'A', 'label': {'zh': 'A类不确定度', 'en': 'Type A Uncertainty'}},
        {'name': 'B', 'label': {'zh': 'B类不确定度', 'en': 'Type B Uncertainty'}},
        {'name': 'total', 'label': {'zh': '总不确定度', 'en': 'Total Uncertainty'}},
        {'name': 'n', 'label': {'zh': '数据个数 n', 'en': 'Number of data n'}}
    ],
    'func': 'calculate'
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(data, instrument_error, precision=3):
    """
    计算平均值、标准偏差、A类不确定度、B类不确定度、总不确定度。

    参数:
        data            : list of float，测量数据
        instrument_error: float，仪器误差
        precision       : int，保留小数位数（不影响计算）

    返回:
        dict 或 None : 包含 avg, S, A, B, total, n 的字典；
                       data 长度 < 2 时返回 None
    """
    if not data or len(data) < 2:
        return None

    n = len(data)
    avg = sum(data) / n
    sum_sq = sum((x - avg) ** 2 for x in data)
    S = math.sqrt(sum_sq / (n - 1))
    A = S / math.sqrt(n)
    B = instrument_error / math.sqrt(3)
    total = math.sqrt(A**2 + B**2)

    return {
        'avg': avg,
        'S': S,
        'A': A,
        'B': B,
        'total': total,
        'n': n
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("平均值与不确定度计算 (Average and Uncertainty Calculation)")
    try:
        data_input = input("请输入测量数据，以空格分隔（例如：1.2 2.3 3.4）：")
        if not data_input.strip():
            print("未输入数据。")
            return
        data = [float(x) for x in data_input.strip().split()]
        if len(data) < 2:
            print("至少需要两个数据。")
            return

        instr = float(input("请输入仪器误差："))
        result = calculate(data, instr)
        if result is None:
            print("计算失败，请检查输入。")
            return

        precision = 3
        for out in UI_SPEC['outputs']:
            key = out['name']
            if key in result:
                val = result[key]
                if isinstance(val, float):
                    print(f"{out['label']['zh']}: {val:.{precision}f}")
                else:
                    print(f"{out['label']['zh']}: {val}")
    except ValueError:
        print("输入格式错误，请输入数字。")

if __name__ == "__main__":
    main()