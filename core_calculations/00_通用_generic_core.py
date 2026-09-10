# -*- coding: utf-8 -*-
"""
实验中文名：<请在此处填写中文名>
实验英文名：<Please fill in the English name>

本文件是 PhyCalc 项目核心计算逻辑的通用模板。
使用说明：
1. 复制本文件，重命名为 "nn_中文名_英文名_core.py"，其中 nn 是两位数字（如 01, 02...）。
2. 修改下面的 UI_SPEC 字典，定义该实验所需的输入参数和输出结果。
3. 实现 calculate 函数，完成实际的计算逻辑。
4. 如需独立运行，保留 main 函数并实现命令行交互。
5. 本模板放置在 core_calculations/ 中，主菜单会跳过以 "00_" 开头的文件，因此本模板不会被识别为实验选项。
"""

import math
import sys

# ============================================================
# 1. UI 规格定义（UI Specification）
#    通用二级界面根据此定义动态生成输入和输出区域。
#    请根据实际实验需求修改以下内容。
# ============================================================
UI_SPEC = {
    # 窗口标题（中英文）
    'title': {
        'zh': '<实验中文名>',
        'en': '<Experiment English Name>'
    },
    # 输入参数定义
    'inputs': [
        # 每个输入项为一个字典，支持两种类型：
        # - 列表型 (type='list')：用于输入多个同类数据，界面提供添加/删除行。
        # - 单值型 (type='float' 或 'int')：单个输入框。
        {
            'name': 'data',          # 参数名称，将作为函数参数传入
            'label': {               # 显示标签（中英文）
                'zh': '测量数据',
                'en': 'Data'
            },
            'type': 'list',          # 类型：列表
            'initial': 6,            # 初始显示行数
            'default': []            # 默认值（可选）
        },
        {
            'name': 'instrument_error',
            'label': {
                'zh': '仪器误差',
                'en': 'Instrument Error'
            },
            'type': 'float',         # 单值浮点数
            'initial': None,         # 无意义
            'default': 0.01          # 默认值（显示在输入框中）
        }
        # 可根据需要增加更多输入项，例如：
        # {
        #     'name': 'sample_id',
        #     'label': {'zh': '样品编号', 'en': 'Sample ID'},
        #     'type': 'int',
        #     'initial': None,
        #     'default': 1
        # }
    ],
    # 输出结果定义
    'outputs': [
        # 每个输出项包含变量名和显示标签（中英文）
        {'name': 'avg', 'label': {'zh': '平均值', 'en': 'Average'}},
        {'name': 'S', 'label': {'zh': '实验标准偏差 S', 'en': 'Std Deviation S'}},
        {'name': 'A', 'label': {'zh': 'A类不确定度', 'en': 'Type A Uncertainty'}},
        {'name': 'B', 'label': {'zh': 'B类不确定度', 'en': 'Type B Uncertainty'}},
        {'name': 'total', 'label': {'zh': '总不确定度', 'en': 'Total Uncertainty'}},
        {'name': 'n', 'label': {'zh': '数据个数 n', 'en': 'Number of data n'}}
    ],
    # 计算函数名称（必须与下面定义的函数名一致）
    'func': 'calculate'
}


# ============================================================
# 2. 核心计算函数
#    参数：必须与 UI_SPEC['inputs'] 中的 'name' 一一对应（顺序可不同）。
#    返回：必须是一个字典，键名必须与 UI_SPEC['outputs'] 中的 'name' 一致。
#    注：可额外接收一个 precision 参数（整数），用于外部显示精度，不影响计算。
# ============================================================
def calculate(data, instrument_error, precision=3):
    """
    计算平均值、标准偏差、A类不确定度、B类不确定度、总不确定度。

    参数:
        data            : list of float，测量数据
        instrument_error: float，仪器误差
        precision       : int，保留小数位数（仅用于外部显示，计算中可使用也可忽略）

    返回:
        dict 或 None : 包含至少 UI_SPEC['outputs'] 中列出的所有键。
                       若数据无效（如数据长度不足），应返回 None。
    """
    # ---------- 在这里编写你的计算逻辑 ----------
    # 示例：计算平均值
    if not data or len(data) < 2:
        return None

    n = len(data)
    avg = sum(data) / n
    # 计算残差平方和
    sum_sq = sum((x - avg) ** 2 for x in data)
    # 标准偏差
    S = math.sqrt(sum_sq / (n - 1))
    # A类不确定度
    A = S / math.sqrt(n)
    # B类不确定度
    B = instrument_error / math.sqrt(3)
    # 总不确定度
    total = math.sqrt(A**2 + B**2)

    # 返回结果字典，键必须与 UI_SPEC['outputs'] 中的 'name' 匹配
    return {
        'avg': avg,
        'S': S,
        'A': A,
        'B': B,
        'total': total,
        'n': n
    }


# ============================================================
# 3. 独立运行入口（方便直接测试本模块）
#    如果不需要独立运行，可保留或删除。
# ============================================================
def main():
    """独立运行时交互入口，调用 calculate 并输出结果。"""
    print("<实验中文名> (<Experiment English Name>)")
    try:
        # 示例：读取数据
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

        precision = 3  # 显示精度，可自行修改
        # 按 UI_SPEC 中的顺序输出
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