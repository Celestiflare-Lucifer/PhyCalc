# -*- coding: utf-8 -*-
"""
实验中文名：用气垫转盘转动惯量仪测定刚体的转动惯量
实验英文名：Measurement of Moment of Inertia Using Air-Bearing Rotating Disk

文件名：2.2_用气垫转盘转动惯量仪测定刚体的转动惯量_air_bearing_moment_of_inertia_core.py
章节：第 2 章第 2 节

依据教材：冯放, 牟艳秋. 大学物理实验[M]. 北京: 高等教育出版社, 2017.

【实验原理】

设砝码质量为 m，细线缠绕的圆柱半径为 r，两侧砝码各一个，
则动盘所受力矩 M = 2Fr。

砝码下落时（教材式 2.2.1）：
    mg − F = ma
动盘转动方程（教材式 2.2.2）：
    2Fr = Iα
切向加速度 a = αr。两式联立可得（教材式 2.2.3）：
    I = 2mgr/α − 2mr²

角加速度 α 由动盘转动一周的时间 t₁ 和转动两周的时间 t₂ 求得：
    动盘转动 θ₁ = 2π 用时 t₁
    动盘转动 θ₂ = 4π 用时 t₂
由 θ = ω₀t + ½αt²，消去 ω₀ 后得到（教材式 2.2.6）：
    α = 4π(2t₁ − t₂) / [t₁t₂(t₂ − t₁)]

代入 2.2.3，可得（教材式 2.2.7）：
    I = mgr·t₁t₂(t₂ − t₁) / [2π(2t₁ − t₂)] − 2mr²

【本程序的处理方式】

    · 用户输入多组 (m, t₁, t₂) 数据。
    · 对每组数据分别按式 (2.2.6) 计算 α，再按式 (2.2.7) 计算 I_i。
    · 对 I_i 求平均值 Ī，按误差理论计算 A 类、B 类、合成不确定度与相对不确定度，
      最终按标准形式给出结果表达式。

【单位约定】

    输入：m — g，t₁、t₂ — s，r — mm
    内部计算：换算为 SI 单位（kg、s、m），得到 I（kg·m²）
    输出显示：换算为 g·cm²（1 kg·m² = 10⁷ g·cm²）
"""

import math
import sys


# 重力加速度（本项目取 9.8 m/s²，与教材一致）
G = 9.8


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '用气垫转盘转动惯量仪测定刚体的转动惯量',
        'en': 'Moment of Inertia with Air-Bearing Rotating Disk',
    },
    'chapter': 2,
    'section': 2,
    'chapter_name': {
        'zh': '基础实验',
        'en': 'Basic Experiments',
    },

    'inputs': [
        # -------- 砝码质量列表 --------
        {
            'name': 'data_m',
            'label': {'zh': '砝码质量 m', 'en': 'Weight Mass m'},
            'type': 'list',
            'initial': 5,
            'item_prefix': {'zh': 'm', 'en': 'm'},
            'unit': 'g',
            'hint': {
                'zh': '每次实验两个砝码盘内放入相同质量的砝码，输入每个砝码的质量。\n'
                      '• 建议在不同质量下重复测量（例如 1、2、3、5、6、7、8 g）。\n'
                      '• 三组输入（m、t₁、t₂）的长度必须相同，一一对应。',
                'en': 'Enter the mass of each weight (same on both sides).\n'
                      '• Repeat with different masses (e.g., 1, 2, 3, 5, 6, 7, 8 g).\n'
                      '• The three lists (m, t₁, t₂) must have the same length.',
            },
            'default': [],
        },

        # -------- 转动一周时间 t₁ --------
        {
            'name': 'data_t1',
            'label': {'zh': '转动一周的时间 t₁', 'en': 'Time t₁ (one turn)'},
            'type': 'list',
            'initial': 5,
            'item_prefix': {'zh': 't1', 'en': 't1'},
            'unit': 's',
            'hint': {
                'zh': '动盘转动一周（θ₁ = 2π）所用的时间，由数字计时器读出。\n'
                      '单位：秒（s）。',
                'en': 'Time for the disk to rotate one turn (θ₁ = 2π), '
                      'read from the digital timer. Unit: seconds.',
            },
            'default': [],
        },

        # -------- 转动两周时间 t₂ --------
        {
            'name': 'data_t2',
            'label': {'zh': '转动两周的时间 t₂', 'en': 'Time t₂ (two turns)'},
            'type': 'list',
            'initial': 5,
            'item_prefix': {'zh': 't2', 'en': 't2'},
            'unit': 's',
            'hint': {
                'zh': '动盘从静止开始转动两周（θ₂ = 4π）所用的时间。\n'
                      '单位：秒（s）。\n'
                      '正常加速时应有 t₁ < t₂ < 2t₁。',
                'en': 'Time for the disk to rotate two turns (θ₂ = 4π).\n'
                      'Unit: seconds. Normally t₁ < t₂ < 2t₁.',
            },
            'default': [],
        },

        # -------- 圆柱半径 r --------
        {
            'name': 'radius',
            'label': {'zh': '圆柱半径 r', 'en': 'Cylinder Radius r'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '本仪器细线缠绕的圆柱半径 r = 10.00 mm（教材给出）。',
                'en': 'The radius of the cylinder on which the thread is wound '
                      '(r = 10.00 mm as specified by the manual).',
            },
            'default': 10.00,
        },

        # -------- 质量仪器误差 --------
        {
            'name': 'error_m',
            'label': {'zh': '质量仪器误差 Δm', 'en': 'Mass Instrument Error'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '砝码质量的仪器误差（按所用天平或砝码精度填写，一般 0.04 g 左右）。',
                'en': 'Instrument error of the weight mass '
                      '(typically around 0.04 g).',
            },
            'default': 0.04,
        },

        # -------- 时间仪器误差 --------
        {
            'name': 'error_t',
            'label': {'zh': '时间仪器误差 Δt', 'en': 'Time Instrument Error'},
            'type': 'float',
            'unit': 's',
            'hint': {
                'zh': '数字计时器的时间分辨力（JO201-CC 型时基精度约 1 μs，'
                      '一般取 0.000 1 s 即可，对结果影响极小）。',
                'en': 'Time resolution of the digital timer '
                      '(about 1 μs for JO201-CC; 0.000 1 s is usually enough).',
            },
            'default': 0.0001,
        },
    ],

    'outputs': [
        {'name': 'I_per_trial',
         'label': {'zh': '各次测得的 I (g·cm²)', 'en': 'I per trial (g·cm²)'}},
        {'name': 'I_avg',
         'label': {'zh': '转动惯量平均值 Ī (g·cm²)', 'en': 'Average I (g·cm²)'}},
        {'name': 'u_A',
         'label': {'zh': 'A 类不确定度 u_A (g·cm²)', 'en': 'Type A u_A (g·cm²)'}},
        {'name': 'u_B',
         'label': {'zh': 'B 类不确定度 u_B (g·cm²)', 'en': 'Type B u_B (g·cm²)'}},
        {'name': 'u_total',
         'label': {'zh': '合成不确定度 u(I) (g·cm²)', 'en': 'Combined u(I) (g·cm²)'}},
        {'name': 'Ur_percent',
         'label': {'zh': '相对不确定度 U_r (%)', 'en': 'Relative U_r (%)'}},
        {'name': 'n',
         'label': {'zh': '测量组数 n', 'en': 'Number of trials n'}},
        {'name': 'result_expr',
         'label': {'zh': '测量结果表示', 'en': 'Measurement Result'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(data_m, data_t1, data_t2, radius, error_m, error_t, precision=3):
    """
    计算转动惯量及其不确定度。

    参数:
        data_m    : list of float，砝码质量（g）
        data_t1   : list of float，转动一周时间（s）
        data_t2   : list of float，转动两周时间（s）
        radius    : float，圆柱半径（mm）
        error_m   : float，质量仪器误差（g）
        error_t   : float，时间仪器误差（s）
        precision : int，显示精度（不影响计算）

    返回:
        dict 或 None
    """
    # ---------- 基本校验 ----------
    if not (data_m and data_t1 and data_t2):
        return None
    n = len(data_m)
    if len(data_t1) != n or len(data_t2) != n or n < 1:
        return None

    # ---------- 单位换算到 SI ----------
    r = radius * 1e-3                    # mm → m
    error_m_SI = error_m * 1e-3          # g → kg

    # ---------- 单次 I 的计算函数 ----------
    def compute_I(m, t1, t2):
        """
        I = 2mgr/α − 2mr²，α = 4π(2t₁ − t₂)/[t₁t₂(t₂ − t₁)]
        单位：m — kg，t — s，r — m，返回 I — kg·m²
        """
        denom_a = t1 * t2 * (t2 - t1)
        num_a = 4 * math.pi * (2 * t1 - t2)
        if abs(denom_a) < 1e-15:
            return None
        alpha = num_a / denom_a
        if abs(alpha) < 1e-15:
            return None
        return 2 * m * G * r / alpha - 2 * m * r * r

    # ---------- 逐组计算 I ----------
    I_list_SI = []                        # 单位：kg·m²
    for i in range(n):
        Ii = compute_I(data_m[i], data_t1[i], data_t2[i])
        if Ii is None:
            return None
        I_list_SI.append(Ii)

    # ---------- 换算为 g·cm² 显示（1 kg·m² = 10^7 g·cm²） ----------
    I_list = [Ii * 1e7 for Ii in I_list_SI]

    # ---------- 平均值 ----------
    I_avg = sum(I_list) / n

    # ---------- A 类不确定度（对平均值的标准偏差） ----------
    if n >= 2:
        sum_sq = sum((Ii - I_avg) ** 2 for Ii in I_list)
        u_A = math.sqrt(sum_sq / (n * (n - 1)))
    else:
        u_A = 0.0

    # ---------- B 类不确定度（误差传播） ----------
    # 单次 I 的不确定度由 ∂I/∂m·u_m、∂I/∂t1·u_t、∂I/∂t2·u_t 三项合成
    # 再用平方和开方的方式得到对平均值的合成 B 类不确定度
    def I_SI(m, t1, t2):
        return 2 * m * G * r / ((4 * math.pi * (2 * t1 - t2)) / (t1 * t2 * (t2 - t1))) \
               - 2 * m * r * r

    def partial(func, m, t1, t2, var, h_rel=1e-6):
        """对 m、t1、t2 中某个变量求数值偏导数（中心差分）。"""
        kwargs = {'m': m, 't1': t1, 't2': t2}
        base = kwargs[var]
        h = max(abs(base), 1.0) * h_rel
        k1 = dict(kwargs); k1[var] = base + h
        k2 = dict(kwargs); k2[var] = base - h
        return (func(**k1) - func(**k2)) / (2 * h)

    u_B_sq = 0.0
    for i in range(n):
        m_SI = data_m[i] * 1e-3
        t1 = data_t1[i]
        t2 = data_t2[i]

        dIdm = partial(I_SI, m_SI, t1, t2, 'm')
        dIdt1 = partial(I_SI, m_SI, t1, t2, 't1')
        dIdt2 = partial(I_SI, m_SI, t1, t2, 't2')

        # B 类分量：仪器误差按均匀分布，除以 √3
        u_m_B = error_m_SI / math.sqrt(3)
        u_t_B = error_t / math.sqrt(3)

        uBi_sq = (dIdm * u_m_B) ** 2 \
                 + (dIdt1 * u_t_B) ** 2 \
                 + (dIdt2 * u_t_B) ** 2
        u_B_sq += uBi_sq

    # 平均值的合成 B 类不确定度：除以 n 后开方
    u_B_SI = math.sqrt(u_B_sq) / n
    u_B = u_B_SI * 1e7                     # kg·m² → g·cm²

    # ---------- 合成不确定度与相对不确定度 ----------
    u_total = math.sqrt(u_A ** 2 + u_B ** 2)
    Ur_percent = (u_total / abs(I_avg) * 100) if abs(I_avg) > 1e-15 else 0.0

    # ---------- 结果表达式 ----------
    result_expr = (f"I = ({I_avg:.{precision}f} ± "
                   f"{u_total:.{precision}f}) g·cm²")

    # ---------- 各次 I 的显示字符串 ----------
    I_per_trial = ", ".join(f"{v:.{precision}f}" for v in I_list)

    return {
        'I_per_trial': I_per_trial,
        'I_avg': I_avg,
        'u_A': u_A,
        'u_B': u_B,
        'u_total': u_total,
        'Ur_percent': Ur_percent,
        'n': n,
        'result_expr': result_expr,
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("用气垫转盘转动惯量仪测定刚体的转动惯量")
    print("(Moment of Inertia with Air-Bearing Rotating Disk)")
    print("=" * 60)

    try:
        n = int(input("请输入测量组数 n（例如 5）：").strip() or "5")
        data_m, data_t1, data_t2 = [], [], []
        for i in range(n):
            print(f"\n--- 第 {i + 1} 组数据 ---")
            m = float(input(f"  砝码质量 m_{i + 1} (g)：").strip())
            t1 = float(input(f"  转动一周时间 t1_{i + 1} (s)：").strip())
            t2 = float(input(f"  转动两周时间 t2_{i + 1} (s)：").strip())
            data_m.append(m)
            data_t1.append(t1)
            data_t2.append(t2)

        radius = float(input("\n圆柱半径 r (mm，默认 10.00)：").strip() or "10.00")
        error_m = float(input("质量仪器误差 Δm (g，默认 0.04)：").strip() or "0.04")
        error_t = float(input("时间仪器误差 Δt (s，默认 0.0001)：").strip() or "0.0001")
    except ValueError:
        print("输入格式错误。")
        return

    result = calculate(data_m, data_t1, data_t2, radius, error_m, error_t)
    if result is None:
        print("计算失败，请检查输入：")
        print("  · 三组数据的个数是否相同？")
        print("  · 是否满足 t1 < t2 < 2t1？")
        return

    print("=" * 60)
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