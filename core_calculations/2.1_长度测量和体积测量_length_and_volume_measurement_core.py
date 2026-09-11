# -*- coding: utf-8 -*-
"""
实验中文名：长度测量和体积测量
实验英文名：Length and Volume Measurement

文件名：2.1_长度测量和体积测量_length_and_volume_measurement_core.py
章节：第 2 章第 1 节

依据教材：冯放, 牟艳秋. 大学物理实验[M]. 北京: 高等教育出版社, 2017.

本实验包含多个子测量，通过“测量类型”下拉选择来确定要计算的量：
    ① 金属丝直径（游标卡尺）
    ② 金属丝直径（螺旋测微器）
    ③ 小球体积（螺旋测微器）
    ④ 空心圆柱体体积（游标卡尺）
    ⑤ 实心圆柱体密度（物理天平 + 游标卡尺）

每种类型所需的输入不同，不需要的输入框可留空。
"""

import math
import sys


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '长度测量和体积测量',
        'en': 'Length and Volume Measurement',
    },
    'chapter': 2,
    'section': 1,

    'inputs': [
        # -------- 测量类型 --------
        {
            'name': 'measurement_type',
            'label': {'zh': '测量类型', 'en': 'Measurement Type'},
            'type': 'choice',
            'options': [
                {'value': 'wire_caliper',
                 'label': {'zh': '① 金属丝直径（游标卡尺）',
                           'en': '① Wire Diameter (Caliper)'}},
                {'value': 'wire_micrometer',
                 'label': {'zh': '② 金属丝直径（螺旋测微器）',
                           'en': '② Wire Diameter (Micrometer)'}},
                {'value': 'sphere_diameter',
                 'label': {'zh': '③ 小球体积（螺旋测微器）',
                           'en': '③ Sphere Volume (Micrometer)'}},
                {'value': 'hollow_cylinder',
                 'label': {'zh': '④ 空心圆柱体体积（游标卡尺）',
                           'en': '④ Hollow Cylinder Volume (Caliper)'}},
                {'value': 'solid_cylinder',
                 'label': {'zh': '⑤ 实心圆柱体密度',
                           'en': '⑤ Solid Cylinder Density'}},
            ],
            'hint': {
                'zh': '请先选择本次要处理的数据属于哪种测量类型，'
                      '然后只填写与该类型相关的输入框。',
                'en': 'Choose the measurement type first, then fill in '
                      'only the relevant inputs.',
            },
            'default': 'wire_caliper',
        },

        # -------- 直径 / 外径 D --------
        {
            'name': 'data_D',
            'label': {'zh': '直径 / 外径 D 数据', 'en': 'Diameter D'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'D', 'en': 'D'},
            'unit': 'mm',
            'hint': {
                'zh': '金属丝直径、小球直径或圆柱体外径，通常测 3 次。\n'
                      '（类型 ①②③④⑤ 均需要）',
                'en': 'Wire/sphere/cylinder outer diameter, usually 3 '
                      'measurements. (Required for types ①②③④⑤)',
            },
            'default': [],
        },

        # -------- 长度 L --------
        {
            'name': 'data_L',
            'label': {'zh': '长度 L 数据', 'en': 'Length L'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'L', 'en': 'L'},
            'unit': 'mm',
            'hint': {
                'zh': '圆柱体长度。仅类型 ④⑤ 需要，其他类型请留空。',
                'en': 'Cylinder length. Only for types ④⑤.',
            },
            'default': [],
            'optional': True,   # 允许留空
        },

        # -------- 内径 d --------
        {
            'name': 'data_d',
            'label': {'zh': '内径 d 数据', 'en': 'Inner Diameter d'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'd', 'en': 'd'},
            'unit': 'mm',
            'hint': {
                'zh': '空心圆柱体内径。仅类型 ④ 需要，其他类型请留空。',
                'en': 'Hollow cylinder inner diameter. Only for type ④.',
            },
            'default': [],
            'optional': True,
        },

        # -------- 孔深 h --------
        {
            'name': 'data_h',
            'label': {'zh': '孔深 h 数据', 'en': 'Hole Depth h'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'h', 'en': 'h'},
            'unit': 'mm',
            'hint': {
                'zh': '空心圆柱体孔深。仅类型 ④ 需要。\n'
                      '若孔贯穿整个圆柱体，可留空（默认与 L 相同）。',
                'en': 'Hole depth for hollow cylinder. Only for type ④. '
                      'Leave empty if the hole is through.',
            },
            'default': [],
            'optional': True,
        },

        # -------- 质量 m --------
        {
            'name': 'mass',
            'label': {'zh': '质量 m', 'en': 'Mass m'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '实心圆柱体的质量，用物理天平称量。\n'
                      '仅类型 ⑤ 需要，其他类型填 0 即可。',
                'en': 'Mass of the solid cylinder, measured by balance. '
                      'Only for type ⑤; fill 0 otherwise.',
            },
            'default': 0,
        },

        # -------- 长度仪器误差 --------
        {
            'name': 'error_length',
            'label': {'zh': '长度仪器误差 Δ仪', 'en': 'Instrument Error (Length)'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '按教材表 2.1.1：游标卡尺 0.02 mm；螺旋测微器 0.004 mm。',
                'en': 'Caliper 0.02 mm; micrometer 0.004 mm.',
            },
            'default': 0.02,
        },

        # -------- 天平仪器误差 --------
        {
            'name': 'error_mass',
            'label': {'zh': '天平仪器误差 Δm', 'en': 'Balance Error Δm'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '物理天平的仪器误差（通常 0.04 g）。仅类型 ⑤ 需要。',
                'en': 'Physical balance error (usually 0.04 g). Only for type ⑤.',
            },
            'default': 0.04,
        },
    ],

    'outputs': [
        # 直径统计
        {'name': 'avg_D', 'label': {'zh': '直径平均值 D̄ (mm)', 'en': 'Average D̄ (mm)'}},
        {'name': 'u_D',   'label': {'zh': '直径不确定度 u(D) (mm)', 'en': 'Uncertainty u(D) (mm)'}},
        {'name': 'Ur_D',  'label': {'zh': '直径相对不确定度 U_r(D) (%)', 'en': 'Relative Uncertainty of D (%)'}},

        # 长度统计
        {'name': 'avg_L', 'label': {'zh': '长度平均值 L̄ (mm)', 'en': 'Average L̄ (mm)'}},
        {'name': 'u_L',   'label': {'zh': '长度不确定度 u(L) (mm)', 'en': 'Uncertainty u(L) (mm)'}},

        # 体积
        {'name': 'V',     'label': {'zh': '体积 V (mm³)', 'en': 'Volume V (mm³)'}},
        {'name': 'u_V',   'label': {'zh': '体积不确定度 u(V) (mm³)', 'en': 'Uncertainty u(V) (mm³)'}},
        {'name': 'Ur_V',  'label': {'zh': '体积相对不确定度 U_r(V) (%)', 'en': 'Relative Uncertainty of V (%)'}},

        # 密度
        {'name': 'rho',   'label': {'zh': '密度 ρ (g/cm³)', 'en': 'Density ρ (g/cm³)'}},
        {'name': 'u_rho', 'label': {'zh': '密度不确定度 u(ρ) (g/cm³)', 'en': 'Uncertainty u(ρ)'}},
        {'name': 'Ur_rho','label': {'zh': '密度相对不确定度 U_r(ρ) (%)', 'en': 'Relative Uncertainty of ρ (%)'}},

        # 结果表达式
        {'name': 'result_expr', 'label': {'zh': '测量结果表示', 'en': 'Measurement Result'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(measurement_type, data_D, data_L, data_d, data_h,
              mass, error_length, error_mass, precision=3):
    """
    根据测量类型计算长度、体积或密度及其不确定度。

    参数:
        measurement_type : str，五选一（见 UI_SPEC['inputs'][0]['options']）
        data_D           : list of float，直径/外径
        data_L           : list of float，长度（可空）
        data_d           : list of float，内径（可空）
        data_h           : list of float，孔深（可空）
        mass             : float，质量（仅实心圆柱体）
        error_length     : float，长度仪器误差
        error_mass       : float，天平仪器误差
        precision        : int，小数位数

    返回:
        dict 或 None
    """
    # ---------- 辅助函数：单组数据的平均值与不确定度 ----------
    def stats(values, error):
        """返回平均值、A 类、B 类、合成与相对不确定度。"""
        n = len(values)
        if n == 0:
            return None
        avg = sum(values) / n
        if n >= 2:
            sum_sq = sum((x - avg) ** 2 for x in values)
            A = math.sqrt(sum_sq / (n * (n - 1)))
        else:
            A = 0.0
        B = error / math.sqrt(3)   # 按均匀分布取 ÷√3
        u = math.sqrt(A ** 2 + B ** 2)
        Ur = (u / abs(avg) * 100) if abs(avg) > 1e-15 else 0.0
        return {'n': n, 'avg': avg, 'A': A, 'B': B, 'u': u, 'Ur': Ur}

    result = {}

    # ---------- 计算各组数据的统计量 ----------
    st_D = stats(data_D, error_length) if data_D else None
    st_L = stats(data_L, error_length) if data_L else None
    st_d = stats(data_d, error_length) if data_d else None
    st_h = stats(data_h, error_length) if data_h else None

    # 输出直径统计
    if st_D:
        result['avg_D'] = st_D['avg']
        result['u_D'] = st_D['u']
        result['Ur_D'] = st_D['Ur']

    # 输出长度统计（如有）
    if st_L:
        result['avg_L'] = st_L['avg']
        result['u_L'] = st_L['u']

    # ---------- 按测量类型计算 ----------
    if measurement_type in ('wire_caliper', 'wire_micrometer'):
        # ① ② 金属丝直径：只需输出直径和结果表达式
        if not st_D:
            return None
        result['result_expr'] = (
            f"d = ({st_D['avg']:.{precision}f} ± "
            f"{st_D['u']:.{precision}f}) mm"
        )

    elif measurement_type == 'sphere_diameter':
        # ③ 小球体积
        # V = (4/3)·π·(D/2)³ = π·D³ / 6
        # U_r(V) = 3·U_r(D)
        if not st_D:
            return None
        D = st_D['avg']
        u_D = st_D['u']
        V = math.pi / 6 * D ** 3
        Ur_V_frac = 3 * u_D / D if abs(D) > 1e-15 else 0.0
        u_V = Ur_V_frac * V
        result['V'] = V
        result['u_V'] = u_V
        result['Ur_V'] = Ur_V_frac * 100
        result['result_expr'] = (
            f"V = ({V:.{precision}f} ± {u_V:.{precision}f}) mm³"
        )

    elif measurement_type == 'hollow_cylinder':
        # ④ 空心圆柱体体积
        # V = π/4 · (D²·L − d²·h)
        # 若未填孔深 h，默认孔贯穿，h = L
        if not (st_D and st_L and st_d):
            return None
        D = st_D['avg']; L = st_L['avg']
        d = st_d['avg']
        h = st_h['avg'] if st_h else L

        V = math.pi / 4 * (D ** 2 * L - d ** 2 * h)

        # 误差传播（偏导数法）：
        # ∂V/∂D = π/2 · D · L
        # ∂V/∂L = π/4 · D²
        # ∂V/∂d = -π/2 · d · h
        # ∂V/∂h = -π/4 · d²
        u_D = st_D['u']; u_L = st_L['u']
        u_d = st_d['u']; u_h = st_h['u'] if st_h else u_L
        u_V = math.sqrt(
            (math.pi / 2 * D * L * u_D) ** 2 +
            (math.pi / 4 * D ** 2 * u_L) ** 2 +
            (math.pi / 2 * d * h * u_d) ** 2 +
            (math.pi / 4 * d ** 2 * u_h) ** 2
        )
        Ur_V_frac = u_V / V if abs(V) > 1e-15 else 0.0
        result['V'] = V
        result['u_V'] = u_V
        result['Ur_V'] = Ur_V_frac * 100
        result['result_expr'] = (
            f"V = ({V:.{precision}f} ± {u_V:.{precision}f}) mm³"
        )

    elif measurement_type == 'solid_cylinder':
        # ⑤ 实心圆柱体密度
        # ρ = 4m / (π·D²·L)，单位 g/cm³（D、L 从 mm 转 cm）
        if not (st_D and st_L and mass and mass > 0):
            return None
        D = st_D['avg']; L = st_L['avg']
        u_D = st_D['u']; u_L = st_L['u']

        D_cm = D / 10.0
        L_cm = L / 10.0
        rho = 4 * mass / (math.pi * D_cm ** 2 * L_cm)

        # 相对不确定度传播：
        # ln ρ = ln(4m) − ln(π) − 2·ln D − ln L
        # U_r(ρ) = √[ (u_m/m)² + (2·u_D/D)² + (u_L/L)² ]
        # 质量单次测量，只有 B 类：u_m = error_mass / √3
        u_m = error_mass / math.sqrt(3)
        Ur_rho_frac = math.sqrt(
            (u_m / mass) ** 2 +
            (2 * u_D / D) ** 2 +
            (u_L / L) ** 2
        )
        u_rho = Ur_rho_frac * rho
        result['rho'] = rho
        result['u_rho'] = u_rho
        result['Ur_rho'] = Ur_rho_frac * 100
        result['result_expr'] = (
            f"ρ = ({rho:.{precision}f} ± {u_rho:.{precision}f}) g/cm³"
        )

    else:
        return None

    return result


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("长度测量和体积测量")
    print("(Length and Volume Measurement)")
    print("=" * 50)

    print("请选择测量类型：")
    for i, opt in enumerate(UI_SPEC['inputs'][0]['options'], 1):
        print(f"  {i}. {opt['label']['zh']}")
    try:
        idx = int(input("请输入编号（默认 1）：").strip() or "1")
        measurement_type = UI_SPEC['inputs'][0]['options'][idx - 1]['value']

        def read_list(prompt):
            s = input(prompt).strip()
            return [float(x) for x in s.split()] if s else []

        data_D = read_list("请输入直径/外径 D 数据（以空格分隔）：")
        data_L = read_list("请输入长度 L 数据（可留空，直接回车）：")
        data_d = read_list("请输入内径 d 数据（可留空）：")
        data_h = read_list("请输入孔深 h 数据（可留空）：")
        mass_str = input("请输入质量 m（g，仅类型⑤需要，可留空）：").strip()
        mass = float(mass_str) if mass_str else 0.0
        err_len = float(input("请输入长度仪器误差（默认 0.02 mm）：").strip() or "0.02")
        err_mass = float(input("请输入天平仪器误差（默认 0.04 g）：").strip() or "0.04")
    except (ValueError, IndexError):
        print("输入格式错误。")
        return

    result = calculate(measurement_type, data_D, data_L, data_d, data_h,
                       mass, err_len, err_mass)
    if result is None:
        print("计算失败，请检查输入是否与测量类型匹配。")
        return

    print("=" * 50)
    for out in UI_SPEC['outputs']:
        key = out['name']
        if key in result:
            label = out['label']['zh']
            val = result[key]
            if isinstance(val, float):
                print(f"{label}: {val:.4f}")
            else:
                print(f"{label}: {val}")


if __name__ == "__main__":
    main()