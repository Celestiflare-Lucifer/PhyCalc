# -*- coding: utf-8 -*-
"""
实验中文名：常用的实验数据处理方法
实验英文名：Common Data Processing Methods

文件名：1.4_常用的实验数据处理方法_common_data_processing_core.py
章节：第 1 章第 4 节

依据教材：冯放, 牟艳秋. 大学物理实验[M]. 北京: 高等教育出版社, 2017.

本实验实现教材 1.4 节中两种可数值化的数据处理方法：
    ① 最小二乘法（Least Squares）
       对任意一组 (x, y) 数据做线性拟合 y = b0 + b1·x
       公式参考教材式 (1.4.5)：
           b1 = [ n·Σxiyi − Σxi·Σyi ] / [ n·Σxi² − (Σxi)² ]
           b0 = ȳ − b1·x̄
       附加输出：相关系数 r，用于判断线性拟合质量。

    ② 逐差法（Successive Difference）
       用于处理自变量等间隔、因变量为线性响应的数据（如焦利秤测弹簧劲度系数）。
       将数据平分为前后两组，对应项相减求差：
           Δy_i = y_{n/2+i} − y_i,  Δx_i = x_{n/2+i} − x_i
       最后以 斜率 = ΣΔy_i / ΣΔx_i 作为待定系数的估计。
       要求 x、y 数据个数相同且为偶数，否则无法分组。

教材中另外两种方法（列表法、作图法）不涉及数值计算，故本模块不实现。
"""

import math
import sys


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '常用的实验数据处理方法',
        'en': 'Common Data Processing Methods',
    },
    'chapter': 1,
    'section': 4,

    'inputs': [
        # -------- 处理方法选择 --------
        {
            'name': 'method',
            'label': {
                'zh': '处理方法',
                'en': 'Method',
            },
            'type': 'choice',
            'options': [
                {'value': 'least_squares',
                 'label': {'zh': '最小二乘法',
                           'en': 'Least Squares'}},
                {'value': 'difference',
                 'label': {'zh': '逐差法',
                           'en': 'Successive Difference'}},
            ],
            'hint': {
                'zh': '最小二乘法：适用于任意一组 (x, y) 数据对的线性拟合。\n'
                      '逐差法：适用于 x 等间隔、y 为线性响应的数据；\n'
                      '        要求 x、y 数据个数相同且为偶数。',
                'en': 'Least Squares: linear fit for any (x, y) pairs.\n'
                      'Difference: for evenly spaced x with linear response;\n'
                      'requires even number of data points.',
            },
            'default': 'least_squares',
        },

        # -------- 自变量 x --------
        {
            'name': 'x_data',
            'label': {
                'zh': '自变量 x 数据',
                'en': 'Independent Variable x',
            },
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'x', 'en': 'x'},
            'unit': '',
            'hint': {
                'zh': '请输入自变量 x 的取值。数量应与下方 y 数据相同。',
                'en': 'Enter independent variable values. '
                      'Count must equal the y data below.',
            },
            'default': [],
        },

        # -------- 因变量 y --------
        {
            'name': 'y_data',
            'label': {
                'zh': '因变量 y 数据',
                'en': 'Dependent Variable y',
            },
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'y', 'en': 'y'},
            'unit': '',
            'hint': {
                'zh': '请输入因变量 y 的取值，按与 x 一一对应的顺序填写。\n'
                      '• 最小二乘法：个数 ≥ 2 即可；\n'
                      '• 逐差法：个数必须为偶数（如 4、6、10）。',
                'en': 'Enter dependent variable values in the same order as x.\n'
                      '• Least Squares: at least 2 pairs;\n'
                      '• Difference: even count required (e.g., 4, 6, 10).',
            },
            'default': [],
        },
    ],

    'outputs': [
        # 最小二乘法输出
        {'name': 'slope',     'label': {'zh': '斜率 b1',      'en': 'Slope b1'}},
        {'name': 'intercept', 'label': {'zh': '截距 b0',      'en': 'Intercept b0'}},
        {'name': 'r',         'label': {'zh': '相关系数 r',   'en': 'Correlation r'}},

        # 逐差法输出
        {'name': 'dy_avg',    'label': {'zh': '平均 Δy',      'en': 'Average Δy'}},
        {'name': 'dx_avg',    'label': {'zh': '平均 Δx',      'en': 'Average Δx'}},

        # 共用输出
        {'name': 'n',         'label': {'zh': '数据对数 n',   'en': 'Number of pairs'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(method, x_data, y_data, precision=3):
    """
    根据所选方法处理数据。

    参数:
        method    : str，'least_squares' 或 'difference'
        x_data    : list of float，自变量
        y_data    : list of float，因变量
        precision : int，小数位数（仅用于显示，不影响计算）

    返回:
        dict 或 None
    """
    if not x_data or not y_data:
        return None
    if len(x_data) != len(y_data):
        return None
    n = len(x_data)
    if n < 2:
        return None

    if method == 'least_squares':
        return _least_squares(x_data, y_data)
    elif method == 'difference':
        return _successive_difference(x_data, y_data)
    else:
        return None


def _least_squares(x_data, y_data):
    """
    最小二乘法线性拟合 y = b0 + b1·x。

    公式（教材式 1.4.5）：
        b1 = [ n·Σxiyi − Σxi·Σyi ] / [ n·Σxi² − (Σxi)² ]
        b0 = ȳ − b1·x̄
    相关系数：
        r = [ n·Σxiyi − Σxi·Σyi ] /
            sqrt( [n·Σxi² − (Σxi)²] · [n·Σyi² − (Σyi)²] )
    """
    n = len(x_data)
    sum_x = sum(x_data)
    sum_y = sum(y_data)
    sum_xy = sum(xi * yi for xi, yi in zip(x_data, y_data))
    sum_x2 = sum(xi ** 2 for xi in x_data)
    sum_y2 = sum(yi ** 2 for yi in y_data)

    denom = n * sum_x2 - sum_x ** 2
    if abs(denom) < 1e-15:
        # x 全部相同，无法拟合
        return None

    b1 = (n * sum_xy - sum_x * sum_y) / denom
    b0 = (sum_y - b1 * sum_x) / n

    # 相关系数
    num_r = n * sum_xy - sum_x * sum_y
    denom_r = math.sqrt((n * sum_x2 - sum_x ** 2) *
                        (n * sum_y2 - sum_y ** 2))
    r = num_r / denom_r if denom_r > 1e-15 else 0.0

    return {
        'slope': b1,
        'intercept': b0,
        'r': r,
        'n': n,
    }


def _successive_difference(x_data, y_data):
    """
    逐差法处理等间隔数据。

    将数据平分为前后两组，对应项相减：
        Δy_i = y[n/2 + i] − y[i]
        Δx_i = x[n/2 + i] − x[i]
    最后以 ΣΔy / ΣΔx 作为线性系数估计。
    """
    n = len(x_data)
    if n % 2 != 0:
        # 奇数个数据无法平分两组
        return None
    half = n // 2

    dy_list = [y_data[half + i] - y_data[i] for i in range(half)]
    dx_list = [x_data[half + i] - x_data[i] for i in range(half)]

    sum_dy = sum(dy_list)
    sum_dx = sum(dx_list)
    dy_avg = sum_dy / half
    dx_avg = sum_dx / half

    slope = sum_dy / sum_dx if abs(sum_dx) > 1e-15 else 0.0

    return {
        'slope': slope,
        'dy_avg': dy_avg,
        'dx_avg': dx_avg,
        'n': n,
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("常用的实验数据处理方法")
    print("(Common Data Processing Methods)")
    print("=" * 50)

    print("请选择处理方法：")
    print("  1. 最小二乘法 (Least Squares)")
    print("  2. 逐差法 (Successive Difference)")
    try:
        choice = input("请输入编号（默认 1）：").strip() or "1"
        method = 'least_squares' if choice == "1" else 'difference'

        x_input = input("请输入自变量 x 数据（以空格分隔）：").strip()
        if not x_input:
            print("未输入 x 数据。")
            return
        x_data = [float(v) for v in x_input.split()]

        y_input = input("请输入因变量 y 数据（以空格分隔）：").strip()
        if not y_input:
            print("未输入 y 数据。")
            return
        y_data = [float(v) for v in y_input.split()]
    except ValueError:
        print("输入格式错误，请输入数字。")
        return

    result = calculate(method, x_data, y_data)
    if result is None:
        print("计算失败，请检查输入：")
        print("  · x、y 数量是否相同？")
        print("  · 逐差法是否使用了偶数个数据？")
        return

    print("=" * 50)
    if method == 'least_squares':
        print(f"斜率 b1          : {result['slope']:.4f}")
        print(f"截距 b0          : {result['intercept']:.4f}")
        print(f"相关系数 r       : {result['r']:.6f}")
        print(f"数据对数 n       : {result['n']}")
    else:
        print(f"平均 Δy          : {result['dy_avg']:.4f}")
        print(f"平均 Δx          : {result['dx_avg']:.4f}")
        print(f"斜率 (ΣΔy/ΣΔx)   : {result['slope']:.4f}")
        print(f"数据对数 n       : {result['n']}")


if __name__ == "__main__":
    main()