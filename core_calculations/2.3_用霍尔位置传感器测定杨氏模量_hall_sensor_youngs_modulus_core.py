# -*- coding: utf-8 -*-
"""
实验中文名：用霍尔位置传感器测定杨氏模量
实验英文名：Measurement of Young's Modulus Using Hall Position Sensor

文件名：2.3_用霍尔位置传感器测定杨氏模量_hall_sensor_youngs_modulus_core.py
章节：第 2 章第 3 节

依据教材：冯放, 牟艳秋. 大学物理实验[M]. 北京: 高等教育出版社, 2017.

【实验原理】

① 霍尔位置传感器：
    霍尔电压      U_H = K·I·B                      (2.3.1)
    位移关系      ΔU_H = K·I·(dB/dz)·Δz           (2.3.2)
    在均匀梯度磁场中 dB/dz 为常量，故 ΔU_H ∝ Δz。

② 横梁弯曲法测杨氏模量：
    杨氏模量公式  E = d³·mg / (4a³·b·Δz)          (2.3.3)
    其中：
        d  — 两刀口之间的距离
        m  — 砝码质量（本实验取 m = 60.00 g 为基准）
        g  — 重力加速度 9.8 m/s²
        a  — 横梁的厚度
        b  — 横梁的宽度
        Δz — 横梁中心在外力作用下的下降位移

【三个子测量】

    · 传感器定标    : 输入 m、z、U，用逐差法求灵敏度 K = ΔU/Δz
    · 黄铜杨氏模量  : 输入 m、z，用逐差法求 Δz_铜，代入式(2.3.3)
    · 铸铁杨氏模量  : 输入 m、U 与已知 K，由 Δz_铁 = ΔU/K 得位移，代入式(2.3.3)

【单位约定】

    输入：m — g，z — mm，U — mV，d、a、b — mm，K — mV/mm
    内部计算：全部换算为 SI（kg、m、V 与 V/m 量纲保持一致）
    输出：E — Pa（= N/m²），同时也输出 GPa 便于阅读
"""

import math
import sys


# 重力加速度
G = 9.8


# ============================================================
# 1. UI 规格定义
# ============================================================
UI_SPEC = {
    'title': {
        'zh': '用霍尔位置传感器测定杨氏模量',
        'en': "Young's Modulus via Hall Sensor",
    },
    'chapter': 2,
    'section': 3,
    'chapter_name': {
        'zh': '基础实验',
        'en': 'Basic Experiments',
    },

    'inputs': [
        # -------- 测量类型 --------
        {
            'name': 'measurement_type',
            'label': {'zh': '测量类型', 'en': 'Measurement Type'},
            'type': 'choice',
            'options': [
                {'value': 'calibration',
                 'label': {'zh': '① 传感器定标（求 K）',
                           'en': '① Sensor Calibration (K)'}},
                {'value': 'brass',
                 'label': {'zh': '② 黄铜杨氏模量',
                           'en': '② Brass Young\'s Modulus'}},
                {'value': 'cast_iron',
                 'label': {'zh': '③ 铸铁杨氏模量',
                           'en': '③ Cast-Iron Young\'s Modulus'}},
            ],
            'hint': {
                'zh': '按教材 2.3 节的三个子任务分别选择：\n'
                      '① 定标：用逐差法求灵敏度 K = ΔU/Δz；\n'
                      '② 黄铜：用逐差法从读数显微镜的 z 求出 Δz，再算 E；\n'
                      '③ 铸铁：用电压 U 除以已知 K 求 Δz，再算 E。',
                'en': 'Choose one of the three tasks in the textbook:\n'
                      '① Calibration: obtain K = ΔU/Δz by successive difference;\n'
                      '② Brass: obtain Δz from microscope readings, then E;\n'
                      '③ Cast iron: Δz = ΔU/K from voltage readings, then E.',
            },
            'default': 'calibration',
        },

        # -------- 砝码质量 m --------
        {
            'name': 'data_m',
            'label': {'zh': '砝码质量 m', 'en': 'Weight Mass m'},
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'm', 'en': 'm'},
            'unit': 'g',
            'hint': {
                'zh': '通常从 0.00 g 起，每次增加 20.00 g，共 6 个数据：\n'
                      '0.00, 20.00, 40.00, 60.00, 80.00, 100.00 g。',
                'en': 'Typically 0.00, 20.00, 40.00, 60.00, 80.00, 100.00 g '
                      '(6 points, step 20.00 g).',
            },
            'default': [],
        },

        # -------- 位移 z（读数显微镜） --------
        {
            'name': 'data_z',
            'label': {'zh': '位移 z（读数显微镜）', 'en': 'Displacement z (Microscope)'},
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'z', 'en': 'z'},
            'unit': 'mm',
            'hint': {
                'zh': '对应每个砝码质量，读数显微镜上读出的位移。\n'
                      '用于“① 传感器定标”和“② 黄铜杨氏模量”。\n'
                      '“③ 铸铁杨氏模量”请留空。',
                'en': 'Microscope reading at each weight mass. Used for '
                      '① Calibration and ② Brass. Leave empty for ③.',
            },
            'default': [],
            'optional': True,
        },

        # -------- 电压 U（传感器输出） --------
        {
            'name': 'data_U',
            'label': {'zh': '电压 U（传感器输出）', 'en': 'Voltage U (Sensor Output)'},
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': 'U', 'en': 'U'},
            'unit': 'mV',
            'hint': {
                'zh': '对应每个砝码质量，数字电压表读出的电压值。\n'
                      '用于“① 传感器定标”和“③ 铸铁杨氏模量”。\n'
                      '“② 黄铜杨氏模量”请留空。',
                'en': 'Digital voltmeter reading at each weight mass. Used for '
                      '① Calibration and ③ Cast Iron. Leave empty for ②.',
            },
            'default': [],
            'optional': True,
        },

        # -------- 灵敏度 K（仅铸铁模式使用） --------
        {
            'name': 'sensitivity_K',
            'label': {'zh': '灵敏度 K', 'en': 'Sensitivity K'},
            'type': 'float',
            'unit': 'mV/mm',
            'hint': {
                'zh': '仅“③ 铸铁杨氏模量”需要。\n'
                      '由“① 传感器定标”得到的 K 值填入此处，'
                      '或用图解法从 U-z 直线斜率获得。',
                'en': 'Only for ③ Cast Iron. Fill in the K value obtained '
                      'from ① Calibration, or from the slope of the U–z line.',
            },
            'default': 0.1,
        },

        # -------- 梁参数：两刀口间距 d --------
        {
            'name': 'd_param',
            'label': {'zh': '两刀口间距 d', 'en': 'Distance between Knife Edges d'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '用游标卡尺测量横梁两刀口之间的距离 d。',
                'en': 'Distance between the two knife edges of the beam, '
                      'measured by vernier caliper.',
            },
            'default': 200.00,
        },

        # -------- 梁厚度 a --------
        {
            'name': 'a_param',
            'label': {'zh': '梁的厚度 a', 'en': 'Beam Thickness a'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '用螺旋测微器测量梁的厚度 a，需多次测量取平均值。',
                'en': 'Beam thickness a, measured by micrometer; multiple '
                      'readings and take the average.',
            },
            'default': 1.00,
        },

        # -------- 梁宽度 b --------
        {
            'name': 'b_param',
            'label': {'zh': '梁的宽度 b', 'en': 'Beam Width b'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '用游标卡尺测量梁的宽度 b，需多次测量取平均值。',
                'en': 'Beam width b, measured by vernier caliper; multiple '
                      'readings and take the average.',
            },
            'default': 10.00,
        },

        # -------- 位移仪器误差 --------
        {
            'name': 'error_z',
            'label': {'zh': '位移仪器误差 Δz', 'en': 'Displacement Error Δz'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '读数显微镜的仪器误差，一般取 0.005 mm 左右。',
                'en': 'Instrument error of the reading microscope, '
                      'typically around 0.005 mm.',
            },
            'default': 0.005,
        },

        # -------- 质量仪器误差 --------
        {
            'name': 'error_m',
            'label': {'zh': '质量仪器误差 Δm', 'en': 'Mass Instrument Error'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '砝码质量的仪器误差，一般取 0.04 g 左右。',
                'en': 'Instrument error of the weight mass, '
                      'typically around 0.04 g.',
            },
            'default': 0.04,
        },
    ],

    'outputs': [
        # 定标输出
        {'name': 'K',
         'label': {'zh': '灵敏度 K (mV/mm)', 'en': 'Sensitivity K (mV/mm)'}},
        {'name': 'K_note',
         'label': {'zh': 'K 说明', 'en': 'K Note'}},

        # 黄铜 / 铸铁输出
        {'name': 'delta_z',
         'label': {'zh': '位移 Δz (mm)', 'en': 'Displacement Δz (mm)'}},
        {'name': 'E_Pa',
         'label': {'zh': '杨氏模量 E (Pa)', 'en': "Young's Modulus E (Pa)"}},
        {'name': 'E_GPa',
         'label': {'zh': '杨氏模量 E (GPa)', 'en': "Young's Modulus E (GPa)"}},
        {'name': 'Ur_percent',
         'label': {'zh': '相对不确定度 U_r (%)', 'en': 'Relative Uncertainty U_r (%)'}},
        {'name': 'u_E_GPa',
         'label': {'zh': '不确定度 u(E) (GPa)', 'en': 'Uncertainty u(E) (GPa)'}},

        # 结果表达式
        {'name': 'result_expr',
         'label': {'zh': '测量结果表示', 'en': 'Measurement Result'}},
    ],

    'func': 'calculate',
}


# ============================================================
# 2. 核心计算函数
# ============================================================
def calculate(measurement_type, data_m, data_z, data_U, sensitivity_K,
              d_param, a_param, b_param, error_z, error_m, precision=3):
    """
    根据测量类型进行定标或计算杨氏模量。

    参数:
        measurement_type : 'calibration' / 'brass' / 'cast_iron'
        data_m           : 砝码质量列表（g）
        data_z           : 位移列表（mm），① ② 使用
        data_U           : 电压列表（mV），① ③ 使用
        sensitivity_K    : 灵敏度 K（mV/mm），③ 使用
        d_param, a_param, b_param : 梁参数（mm），② ③ 使用
        error_z, error_m : 仪器误差，用于 B 类不确定度
        precision        : 小数位数（仅用于显示）

    返回:
        dict 或 None
    """
    if measurement_type == 'calibration':
        return _calibrate(data_m, data_z, data_U)
    elif measurement_type == 'brass':
        return _youngs_modulus(data_m, data_z, None,
                               d_param, a_param, b_param,
                               error_z, error_m)
    elif measurement_type == 'cast_iron':
        return _youngs_modulus(data_m, None, data_U,
                               d_param, a_param, b_param,
                               error_z, error_m,
                               sensitivity_K=sensitivity_K)
    else:
        return None


# ---------------------------------------------------------------
# ① 传感器定标：用逐差法求 K = ΔU/Δz
# ---------------------------------------------------------------
def _successive_difference(values):
    """
    对等间隔数据用逐差法求平均差值。
    输入列表长度必须为偶数，返回 Δ 平均值。
    """
    n = len(values)
    if n < 2 or n % 2 != 0:
        return None
    half = n // 2
    diffs = [values[half + i] - values[i] for i in range(half)]
    return sum(diffs) / half


def _calibrate(data_m, data_z, data_U):
    if not (data_m and data_z and data_U):
        return None
    if not (len(data_m) == len(data_z) == len(data_U)):
        return None
    if len(data_m) % 2 != 0 or len(data_m) < 4:
        return None

    dz_avg = _successive_difference(data_z)
    dU_avg = _successive_difference(data_U)
    if dz_avg is None or dU_avg is None or abs(dz_avg) < 1e-15:
        return None

    K = dU_avg / dz_avg

    return {
        'K': K,
        'K_note': f"Δz = {dz_avg:.4f} mm, ΔU = {dU_avg:.4f} mV",
        'result_expr': f"K = {K:.{3}f} mV/mm",
    }


# ---------------------------------------------------------------
# ② ③ 杨氏模量：E = d³·mg / (4a³·b·Δz)
# ---------------------------------------------------------------
def _youngs_modulus(data_m, data_z, data_U,
                    d_param, a_param, b_param,
                    error_z, error_m,
                    sensitivity_K=None):
    # ---------- 依据模式决定位移来源 ----------
    if data_z:
        # ② 黄铜：直接用 z 求 Δz
        if len(data_z) % 2 != 0 or len(data_z) < 4:
            return None
        delta_z = _successive_difference(data_z)
        delta_U = None
    elif data_U:
        # ③ 铸铁：Δz = ΔU/K
        if not sensitivity_K or abs(sensitivity_K) < 1e-15:
            return None
        if len(data_U) % 2 != 0 or len(data_U) < 4:
            return None
        delta_U = _successive_difference(data_U)
        delta_z = delta_U / sensitivity_K
    else:
        return None

    if delta_z is None or abs(delta_z) < 1e-15:
        return None

    # ---------- 换算到 SI ----------
    d = d_param * 1e-3       # m
    a = a_param * 1e-3       # m
    b = b_param * 1e-3       # m
    dz = delta_z * 1e-3      # m
    m = 0.060                # 教材要求用 60.00 g 的 Δz 计算 E
    u_m_B = error_m * 1e-3 / math.sqrt(3)  # kg

    # ---------- 杨氏模量 ----------
    E = d ** 3 * m * G / (4 * a ** 3 * b * dz)

    # ---------- 相对不确定度（误差传播） ----------
    # ln E = 3·ln d + ln m − 3·ln a − ln b − ln Δz + const
    # U_r(E) = √[(3·u_d/d)² + (u_m/m)² + (3·u_a/a)² + (u_b/b)² + (u_z/Δz)²]
    # 由于 d、a、b 都是单次测量，其 B 类不确定度按各自仪器的误差给出，
    # 这里简化：直接用 0.02 mm（游标卡尺）、0.004 mm（螺旋测微器）作为估算
    u_d = 0.02e-3 / math.sqrt(3)      # 游标卡尺
    u_a = 0.004e-3 / math.sqrt(3)     # 螺旋测微器
    u_b = 0.02e-3 / math.sqrt(3)      # 游标卡尺
    u_z = error_z * 1e-3 / math.sqrt(3)

    Ur = math.sqrt(
        (3 * u_d / d) ** 2 +
        (u_m_B / m) ** 2 +
        (3 * u_a / a) ** 2 +
        (u_b / b) ** 2 +
        (u_z / dz) ** 2
    )
    u_E = Ur * E

    return {
        'delta_z': delta_z,
        'E_Pa': E,
        'E_GPa': E / 1e9,
        'Ur_percent': Ur * 100,
        'u_E_GPa': u_E / 1e9,
        'result_expr': (f"E = ({E / 1e9:.{precision}f} ± "
                        f"{u_E / 1e9:.{precision}f}) GPa"),
    }


# ============================================================
# 3. 独立运行入口
# ============================================================
def main():
    print("用霍尔位置传感器测定杨氏模量")
    print("(Measurement of Young's Modulus Using Hall Position Sensor)")
    print("=" * 60)
    print("请选择测量类型：")
    for i, opt in enumerate(UI_SPEC['inputs'][0]['options'], 1):
        print(f"  {i}. {opt['label']['zh']}")
    try:
        idx = int(input("请输入编号（默认 1）：").strip() or "1")
        measurement_type = UI_SPEC['inputs'][0]['options'][idx - 1]['value']

        def read_list(prompt):
            s = input(prompt).strip()
            return [float(x) for x in s.split()] if s else []

        data_m = read_list("请输入砝码质量 m（以空格分隔）：")
        data_z = read_list("请输入位移 z（无则留空）：")
        data_U = read_list("请输入电压 U（无则留空）：")

        sensitivity_K = 0.0
        if measurement_type == 'cast_iron':
            sensitivity_K = float(input("请输入灵敏度 K (mV/mm)：").strip())

        d_param = float(input("请输入两刀口间距 d (mm)：").strip() or "200")
        a_param = float(input("请输入梁厚度 a (mm)：").strip() or "1")
        b_param = float(input("请输入梁宽度 b (mm)：").strip() or "10")
        error_z = float(input("请输入位移仪器误差 Δz (mm，默认 0.005)：").strip() or "0.005")
        error_m = float(input("请输入质量仪器误差 Δm (g，默认 0.04)：").strip() or "0.04")
    except (ValueError, IndexError):
        print("输入格式错误。")
        return

    result = calculate(measurement_type, data_m, data_z, data_U,
                       sensitivity_K, d_param, a_param, b_param,
                       error_z, error_m)
    if result is None:
        print("计算失败，请检查输入是否与测量类型匹配。")
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