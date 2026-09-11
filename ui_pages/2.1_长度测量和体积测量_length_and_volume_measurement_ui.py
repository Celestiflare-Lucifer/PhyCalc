# -*- coding: utf-8 -*-
"""
专用 UI - 长度测量和体积测量
文件名：2.1_长度测量和体积测量_length_and_volume_measurement_ui.py

本文件只包含从 0.0_通用_generic_ui.py 的【A】区复制的配置变量。
通用窗口构建、控件布局、语言切换、字体调节等逻辑
全部由通用界面统一实现。

--------------------------------------------------------------------
【教材依据】
    本实验对应教材 2.1 节「长度测量和体积测量」，包含五个子测量：
      ① 金属丝直径（游标卡尺）
      ② 金属丝直径（螺旋测微器）
      ③ 小球体积（螺旋测微器）
      ④ 空心圆柱体体积（游标卡尺）
      ⑤ 实心圆柱体密度（物理天平 + 游标卡尺）

    每个子测量所需的输入不同，用户通过“测量类型”下拉选择后，
    只需填写与所选类型相关的输入框，其他留空即可。
--------------------------------------------------------------------
"""

# ============================================================
# 【A】个性化配置区
# ============================================================

# ----------------------------------------------------------------------------
# A-1. 语言覆盖
#     沿用通用界面所有提示文字，不新增，故设为 None。
# ----------------------------------------------------------------------------
LANG_OVERRIDE = None


# ----------------------------------------------------------------------------
# A-2. UI_SPEC 覆盖
#     整体替换 inputs 数组，为本实验每个输入项补充更详尽、更贴合教材的提示。
#
#     ⚠️ 注意：这里是“整体替换”，不是“逐项合并”。
#        必须写出完整的 inputs 数组，且数组顺序与 core 文件一致。
# ----------------------------------------------------------------------------
UI_SPEC_OVERRIDE = {
    'inputs': [
        # ================================================================
        # 输入项 1：测量类型（单选）
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：measurement_type
        # 类型：choice —— 返回选中项的 value 字符串
        # ================================================================
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
                'zh': '先选择要处理的数据属于哪种测量类型，再填写下方对应的输入框。\n'
                      '不同类型所需的输入：\n'
                      '  ① 金属丝直径（游标卡尺）  → 仅需 D\n'
                      '  ② 金属丝直径（螺旋测微器）→ 仅需 D\n'
                      '  ③ 小球体积（螺旋测微器）  → 仅需 D\n'
                      '  ④ 空心圆柱体体积          → 需 D、L、d（h 可选）\n'
                      '  ⑤ 实心圆柱体密度          → 需 D、L、m',
                'en': 'Choose the measurement type first, then fill in relevant inputs.\n'
                      '  ① Wire diameter (Caliper)      → D only\n'
                      '  ② Wire diameter (Micrometer)   → D only\n'
                      '  ③ Sphere volume (Micrometer)   → D only\n'
                      '  ④ Hollow cylinder volume       → D, L, d (h optional)\n'
                      '  ⑤ Solid cylinder density       → D, L, m',
            },
            'default': 'wire_caliper',
        },

        # ================================================================
        # 输入项 2：直径 / 外径 D
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：data_D
        # 类型：list
        # 显示为 D_1、D_2、D_3……
        # ================================================================
        {
            'name': 'data_D',
            'label': {'zh': '直径 / 外径 D 数据', 'en': 'Diameter D'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'D', 'en': 'D'},
            'unit': 'mm',
            'hint': {
                'zh': '金属丝直径、小球直径、圆柱体外径，通常测 3 次。\n'
                      '游标卡尺精度 0.02 mm；螺旋测微器精度 0.004 mm。\n'
                      '（类型 ①②③④⑤ 均需要）',
                'en': 'Wire / sphere / cylinder outer diameter, usually 3 measurements.\n'
                      'Caliper precision 0.02 mm; micrometer 0.004 mm.\n'
                      '(Required for types ①②③④⑤)',
            },
            'default': [],
        },

        # ================================================================
        # 输入项 3：长度 L
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：data_L
        # optional=True → 其他测量类型时可留空
        # ================================================================
        {
            'name': 'data_L',
            'label': {'zh': '长度 L 数据', 'en': 'Length L'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'L', 'en': 'L'},
            'unit': 'mm',
            'hint': {
                'zh': '圆柱体长度。\n'
                      '• 类型 ④ 空心圆柱体：需要\n'
                      '• 类型 ⑤ 实心圆柱体：需要\n'
                      '• 其他类型：可留空',
                'en': 'Cylinder length.\n'
                      '• Type ④ hollow cylinder: required\n'
                      '• Type ⑤ solid cylinder: required\n'
                      '• Other types: leave empty',
            },
            'default': [],
            'optional': True,
        },

        # ================================================================
        # 输入项 4：内径 d
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：data_d
        # optional=True → 只有空心圆柱体需要
        # ================================================================
        {
            'name': 'data_d',
            'label': {'zh': '内径 d 数据', 'en': 'Inner Diameter d'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'd', 'en': 'd'},
            'unit': 'mm',
            'hint': {
                'zh': '空心圆柱体内孔直径，用游标卡尺的内测量爪测量。\n'
                      '仅类型 ④ 需要，其他类型请留空。',
                'en': 'Hollow cylinder inner diameter, measured with caliper inner jaws.\n'
                      'Only for type ④.',
            },
            'default': [],
            'optional': True,
        },

        # ================================================================
        # 输入项 5：孔深 h
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：data_h
        # optional=True → 若孔贯穿圆柱体可留空（默认与 L 相同）
        # ================================================================
        {
            'name': 'data_h',
            'label': {'zh': '孔深 h 数据', 'en': 'Hole Depth h'},
            'type': 'list',
            'initial': 3,
            'item_prefix': {'zh': 'h', 'en': 'h'},
            'unit': 'mm',
            'hint': {
                'zh': '空心圆柱体内孔的深度，用游标卡尺的深度尺测量。\n'
                      '仅类型 ④ 需要。若内孔贯穿整个圆柱体（h = L），'
                      '可留空，程序会自动使用 L 作为 h。',
                'en': 'Hole depth, measured with the caliper depth rod.\n'
                      'Only for type ④. Leave empty if the hole is through '
                      '(h = L); the program will use L by default.',
            },
            'default': [],
            'optional': True,
        },

        # ================================================================
        # 输入项 6：质量 m
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：mass
        # 类型：float，单值
        # ================================================================
        {
            'name': 'mass',
            'label': {'zh': '质量 m', 'en': 'Mass m'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '用物理天平称量的实心圆柱体质量。\n'
                      '仅类型 ⑤ 需要，其他类型填 0 即可。\n'
                      '物理天平感量 0.1 ~ 0.01 g，称量 1000 g。',
                'en': 'Mass of the solid cylinder, measured with a physical balance.\n'
                      'Only for type ⑤. Fill 0 otherwise.\n'
                      'Physical balance sensitivity: 0.1 ~ 0.01 g; max load 1000 g.',
            },
            'default': 0,
        },

        # ================================================================
        # 输入项 7：长度仪器误差
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：error_length
        # ================================================================
        {
            'name': 'error_length',
            'label': {'zh': '长度仪器误差 Δ仪', 'en': 'Instrument Error (Length)'},
            'type': 'float',
            'unit': 'mm',
            'hint': {
                'zh': '按教材表 2.1.1：\n'
                      '• 游标卡尺（0.02 mm）：Δ仪 = 0.02 mm\n'
                      '• 螺旋测微器：Δ仪 = 0.004 mm\n'
                      'B 类不确定度按 u_B = Δ仪 / √3 计算。',
                'en': 'Caliper: 0.02 mm; Micrometer: 0.004 mm.\n'
                      'Type B: u_B = Δ / √3.',
            },
            'default': 0.02,
        },

        # ================================================================
        # 输入项 8：天平仪器误差
        # ----------------------------------------------------------------
        # 对应 calculate() 的参数名：error_mass
        # ================================================================
        {
            'name': 'error_mass',
            'label': {'zh': '天平仪器误差 Δm', 'en': 'Balance Error Δm'},
            'type': 'float',
            'unit': 'g',
            'hint': {
                'zh': '物理天平的仪器误差（通常 0.04 g）。\n'
                      '仅类型 ⑤ 需要。质量单次测量，'
                      '故其 B 类不确定度 u_B(m) = Δm / √3。',
                'en': 'Physical balance error (usually 0.04 g). Only for type ⑤.\n'
                      'Single measurement, u_B(m) = Δm / √3.',
            },
            'default': 0.04,
        },
    ]
}


# ----------------------------------------------------------------------------
# A-3. 二级窗口初始尺寸
#     本实验输入项较多（8 组），高度适当加大。
# ----------------------------------------------------------------------------
DEFAULT_WINDOW_SIZE = "1050x600"