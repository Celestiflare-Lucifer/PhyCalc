# -*- coding: utf-8 -*-
"""
实验中文名：<请在此处填写中文名>
实验英文名：<Please fill in the English name>

本文件是 PhyCalc 项目核心计算逻辑的通用模板。

【使用说明】
1. 复制本文件，重命名为 "n.m_中文名_英文名_core.py"：
   - n = 章号（整数，如 1、2、3）
   - m = 节号（整数，如 1、2、3；无节可写 0）
   例：1.2_不确定度估算与测量结果表示_uncertainty_estimation_core.py

2. 修改下面的 UI_SPEC 字典，定义该实验所需的输入与输出。

3. 实现 calculate 函数，完成实际计算。

4. 如需独立运行，保留 main 函数并实现命令行交互。

5. 本模板以 "0.0_" 开头，主菜单会自动跳过。
"""

import math
import sys


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    # 实验标题
    'title': {
        'zh': '<实验中文名>',
        'en': '<Experiment English Name>',
    },

    # 章节号（可选；文件名已带可省略）
    'chapter': 0,
    'section': 0,

    # 输入参数定义
    # 支持以下类型：
    #   'list'   : 多行数据输入
    #   'float'  : 单值浮点数
    #   'int'    : 单值整数
    #   'text'   : 单行自由文本
    #   'choice' : 单选项（单选按钮组），返回选项 value 字符串
    #
    # 每个输入项的字段：
    #   name         : 变量名，将作为 calculate() 的关键字参数
    #   label        : 中英文显示标签（LabelFrame / Label 标题）
    #   type         : 输入类型
    #   initial      : (仅 list) 初始行数
    #   item_prefix  : (仅 list) 每行前缀（会拼上编号，如 x1、x2）
    #   unit         : (仅 list/float) 单位文字，如 "cm"
    #   hint         : 在输入组顶部显示的灰色提示文字
    #   default      : 默认值
    #   options      : (仅 choice) 选项列表，每项含 value 和 label
    'inputs': [
        {
            'name': 'data',
            'label': {'zh': '测量数据', 'en': 'Measured Data'},
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'x', 'en': 'x'},
            'unit': '',
            'hint': {
                'zh': '请在此输入多次测量数据；留空的输入框会被忽略。',
                'en': 'Enter repeated measurements; empty rows are ignored.',
            },
            'default': [],
        },
        {
            'name': 'instrument_error',
            'label': {'zh': '仪器误差', 'en': 'Instrument Error'},
            'type': 'float',
            'unit': '',
            'hint': {
                'zh': '按仪器说明书给出的最大允许误差填写',
                'en': 'Enter the maximum permissible error of the instrument',
            },
            'default': 0.01,
        },
    ],

    # 输出结果定义
    'outputs': [
        {'name': 'avg', 'label': {'zh': '平均值', 'en': 'Average'}},
        {'name': 'n', 'label': {'zh': '数据个数 n', 'en': 'Number of data n'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(data, instrument_error, precision=3):
    """
    参数:
        data            : list of float
        instrument_error: float
        precision       : int，小数位数（仅用于显示）

    返回:
        dict，键名与 UI_SPEC['outputs'] 一致；若输入无效则返回 None。
    """
    if not data:
        return None

    n = len(data)
    avg = sum(data) / n

    return {
        'avg': avg,
        'n': n,
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print(UI_SPEC['title']['zh'])
    print("=" * 40)

    args = {}
    try:
        for param in UI_SPEC['inputs']:
            name = param['name']
            label = param['label']['zh']
            ptype = param.get('type', 'float')
            default = param.get('default')

            if ptype == 'list':
                s = input(f"请输入{label}（以空格分隔）：").strip()
                args[name] = [float(x) for x in s.split()] if s else []
            elif ptype == 'choice':
                print(f"{label} 选项：")
                for i, opt in enumerate(param.get('options', []), 1):
                    print(f"  {i}. {opt['label']['zh']}")
                i = int(input("请选择编号：").strip())
                args[name] = param['options'][i - 1]['value']
            elif ptype == 'text':
                s = input(f"请输入{label}：").strip()
                args[name] = s if s else (default or '')
            else:
                prompt = f"请输入{label}"
                if default is not None:
                    prompt += f"（默认 {default}）"
                prompt += "："
                s = input(prompt).strip()
                if not s and default is not None:
                    args[name] = default
                elif ptype == 'int':
                    args[name] = int(s)
                else:
                    args[name] = float(s)
    except (ValueError, IndexError):
        print("输入格式错误，请重新运行。")
        return

    result = calculate(**args, precision=3)
    if result is None:
        print("计算失败，请检查输入。")
        return

    print("=" * 40)
    for out in UI_SPEC['outputs']:
        key = out['name']
        if key in result:
            label = out['label']['zh']
            val = result[key]
            if isinstance(val, float):
                print(f"{label}: {val:.3f}")
            else:
                print(f"{label}: {val}")


if __name__ == "__main__":
    main()