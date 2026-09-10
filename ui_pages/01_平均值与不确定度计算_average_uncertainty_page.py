# -*- coding: utf-8 -*-
"""
专用页面 - 平均值与不确定度计算
文件名：01_平均值与不确定度计算_average_uncertainty_page.py

本文件只包含从 00_通用_generic_page.py 的【A】区复制的配置变量。
通用窗口构建、控件布局、语言切换、字体调节等逻辑
全部由通用界面统一实现。
"""

# ============================================================
# 【A】个性化配置区
# ============================================================

# 本实验不新增界面文本
LANG_OVERRIDE = None

# 覆盖 core 的 UI_SPEC：
#   为数据列表增加 item_prefix（每一项前面显示“数据1”“数据2”…）
UI_SPEC_OVERRIDE = {
    'inputs': [
        {
            'name': 'data',
            'label': {'zh': '测量数据', 'en': 'Data'},
            'type': 'list',
            'initial': 6,
            'item_prefix': {'zh': '数据', 'en': 'Data'},
            'default': []
        },
        {
            'name': 'instrument_error',
            'label': {'zh': '仪器误差', 'en': 'Instrument Error'},
            'type': 'float',
            'default': 0.01
        }
    ]
}

# 二级窗口初始尺寸
DEFAULT_WINDOW_SIZE = "650x500"