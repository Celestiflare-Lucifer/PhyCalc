# -*- coding: utf-8 -*-
"""
通用二级 UI 界面模板
文件名：0.0_通用_generic_ui.py

【本文件的三种使用方式】

  1) 通用界面（自动）：
     主菜单在没有找到配套专用 UI 时，会自动调用本文件的 open_page。

  2) 个性化模板（推荐）：
     要为某实验定制专属界面，请在 ui_pages/ 下新建
         n.m_中文名_英文名_ui.py
     并 **只复制本文件【A】区（个性化配置区）的全部内容** 到新文件。
     通用窗口、控件、按钮、滚动区等代码无需复制——它们都在【B】【C】中。

  3) 完全自定义（高级）：
     如果专用 UI 自己定义了 open_page(parent, settings, core_module)，
     主菜单会直接调用该函数，跳过通用界面。

【支持的输入类型】
    - 'list'   : 多行数据，可增删行，每行可带前缀与单位
    - 'float'  : 单个浮点数
    - 'int'    : 单个整数
    - 'text'   : 单行自由文本（不参与数值计算）
    - 'choice' : 单选项（单选按钮组），返回选项 value 字符串

================================================================================
【可修改数值速查表】
    在编辑器中搜索 “★”，可以快速跳到每一个推荐修改的位置。
================================================================================

    【A 区】配置区
      1. DEFAULT_WINDOW_SIZE    → 二级窗口初始大小（宽x高）
      2. LANG                   → 界面通用文字（中英文）
      3. LANG_OVERRIDE          → 局部覆盖 LANG 中的某几条文字
      4. UI_SPEC_OVERRIDE       → 覆盖 core 文件中的输入/输出定义

    【B 区】通用区（这些值出现在通用代码里，也可按需微调）
      5. wraplength             → 提示文字自动换行宽度（像素）
      6. width（列表标签）      → 列表项前缀标签宽度（字符数）
      7. width（列表输入框）    → 列表输入框宽度（字符数）
      8. width（单值标签）      → 单值参数标签宽度（字符数）
      9. height（输出框）       → 输出文本框高度（行数）
     10. 字体族 / 字号范围      → get_font() 与 change_font() 中
     11. 颜色（提示 / 背景）    → fg='#555'、bg='lightgray' 等

================================================================================
"""

# ============================================================================
# ============================================================================
# 【A】个性化配置区
#     ┌───────────────────────────────────────────────────────────────────┐
#     │ 复制模板时，只需复制下面这一节（从本行到“【A】结束”）的全部内容。│
#     │ 其余部分（【B】、【C】）不需要复制。                            │
#     └───────────────────────────────────────────────────────────────────┘
# ============================================================================
# ============================================================================

# ----------------------------------------------------------------------------
# ★ A-0. 界面默认文本
#     这里定义了所有界面通用提示文字的中英文版本。
#     如果只想为某一个实验替换某一条文字，请**不要**直接改这里，
#     而是在专用 UI 文件里使用 LANG_OVERRIDE（见 A-2）。
# ----------------------------------------------------------------------------
LANG = {
    'zh': {
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision_label': '精度',
        'precision_dialog_title': '精度设置',
        'precision_dialog_prompt': '请输入小数位数（整数）：',
        'input_section_title': '输入',
        'add_data': '添加数据',
        'delete': '删除',
        'output_section_title': '输出',
        'calculate': '计算',
        'result_prefix': '计算结果：',
        'empty_error': '请至少输入一个有效数据。',
        'invalid_error': '输入包含非数字字符，请检查。',
        'enter_error': '请输入 {label}。',
        'core_missing': 'Core 模块缺少函数 {func}。',
        'calc_failed': '计算返回空结果，请检查输入。',
        'calc_error': '计算错误：{err}',
        'item_default_prefix': '数据',
    },
    'en': {
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision_label': 'Precision',
        'precision_dialog_title': 'Precision Settings',
        'precision_dialog_prompt': 'Enter decimal places (integer):',
        'input_section_title': 'Input',
        'add_data': 'Add Data',
        'delete': 'Delete',
        'output_section_title': 'Output',
        'calculate': 'Calculate',
        'result_prefix': 'Results:',
        'empty_error': 'Please enter at least one valid data.',
        'invalid_error': 'Input contains non-numeric characters.',
        'enter_error': 'Please enter {label}.',
        'core_missing': 'Core module is missing function {func}.',
        'calc_failed': 'Calculation returned empty. Check inputs.',
        'calc_error': 'Calculation error: {err}',
        'item_default_prefix': 'Data',
    }
}

# ----------------------------------------------------------------------------
# ★ A-2. 语言覆盖（可选）
#     只覆盖 LANG 中某几个键，不必重写整个 LANG。
#
#     示例：想让“计算”按钮在本实验里显示为“开始计算”：
#         LANG_OVERRIDE = {
#             'zh': {'calculate': '开始计算'},
#             'en': {'calculate': 'Start'},
#         }
#     不需要覆盖时保持 None。
# ----------------------------------------------------------------------------
LANG_OVERRIDE = None

# ----------------------------------------------------------------------------
# ★ A-3. UI_SPEC 覆盖（可选）
#     用于覆盖 core 中 UI_SPEC 的同名键（浅合并：整体替换，不是逐项合并）。
#     通常用于：
#       · 修改窗口标题
#       · 重写 inputs 数组，为某实验补充提示文字、单位、前缀等
#
#     示例：
#         UI_SPEC_OVERRIDE = {
#             'title': {'zh': '自定义标题', 'en': 'Custom Title'},
#             'inputs': [
#                 {'name': 'data',
#                  'label': {'zh': '数据', 'en': 'Data'},
#                  'type': 'list', 'initial': 8,
#                  'item_prefix': {'zh': 'x', 'en': 'x'},
#                  'unit': 'cm',
#                  'hint': {'zh': '多次测量', 'en': 'Repeat'}},
#             ],
#         }
#     注意：如果只改 inputs 中的某一项，也必须写出完整的 inputs 数组。
# ----------------------------------------------------------------------------
UI_SPEC_OVERRIDE = None

# ----------------------------------------------------------------------------
# ★ A-4. 二级窗口默认尺寸（宽x高）
#     格式为字符串 "宽x高"，单位为像素。
#     例："750x600" 表示初始宽 750 px、高 600 px。
#     用户仍可手动拖动窗口边框改变大小。
#     专用 UI 若也定义了 DEFAULT_WINDOW_SIZE，则专用 UI 优先。
# ----------------------------------------------------------------------------
DEFAULT_WINDOW_SIZE = "750x600"

# ============================================================================
# 【A】结束   下面内容在复制模板时不需要包含
# ============================================================================


import tkinter as tk
from tkinter import scrolledtext, simpledialog


# ============================================================================
# ============================================================================
# 【B】通用界面构建
#     ⚠️ 以下为通用机械代码，除有特殊需求外，不建议自行修改。
#     带 ★ 的行表示“可以调、但通常不必要”，如果你对布局不满意可微调。
# ============================================================================
# ============================================================================

def _merge_lang(override_module):
    """合并默认 LANG 与 override_module.LANG_OVERRIDE。"""
    merged = {k: dict(v) for k, v in LANG.items()}
    if override_module:
        ov = getattr(override_module, 'LANG_OVERRIDE', None)
        if ov:
            for lg, d in ov.items():
                merged.setdefault(lg, {}).update(d)
    return merged


def _merge_spec(core_module, override_module):
    """合并 core.UI_SPEC 与 override_module.UI_SPEC_OVERRIDE（浅合并）。"""
    spec = dict(core_module.UI_SPEC)
    if override_module:
        ov = getattr(override_module, 'UI_SPEC_OVERRIDE', None)
        if ov:
            spec.update(ov)
    return spec


def _pick_window_size(override_module):
    """优先使用专用 UI 的 DEFAULT_WINDOW_SIZE，否则用通用默认值。"""
    if override_module:
        s = getattr(override_module, 'DEFAULT_WINDOW_SIZE', None)
        if s:
            return s
    return DEFAULT_WINDOW_SIZE


def _apply_font_recursive(widget, font, skip=()):
    """递归地把字体应用到 widget 及其子控件（skip 中列出的除外）。"""
    if widget in skip:
        return
    try:
        widget.config(font=font)
    except (tk.TclError, TypeError):
        pass
    for child in widget.winfo_children():
        _apply_font_recursive(child, font, skip)


def _get_item_prefix(param, L, current_lang):
    """获取列表型参数每项的前缀文字（如 x、数据、L 等）。"""
    prefix = param.get('item_prefix')
    if isinstance(prefix, dict):
        return prefix.get(current_lang, '')
    if isinstance(prefix, str):
        return prefix
    return L[current_lang].get('item_default_prefix', '')


def _get_localized(d, lang, default=''):
    """从 {'zh': ..., 'en': ...} 中取对应语言的文本。"""
    if isinstance(d, dict):
        return d.get(lang, default)
    if isinstance(d, str):
        return d
    return default


def _build_ui(parent, settings, core_module, override_module=None):
    if not hasattr(core_module, 'UI_SPEC'):
        raise ValueError("Core 模块缺少 UI_SPEC 定义。")

    L = _merge_lang(override_module)
    ui_spec = _merge_spec(core_module, override_module)
    win_size = _pick_window_size(override_module)

    lang = settings.get('language', 'zh')
    precision = settings.get('precision', 3)
    font_size = settings.get('font_size', 10)

    # ---------- 组装窗口标题（带章节号） ----------
    def make_title(lg):
        t = ui_spec['title'][lg]
        ch = ui_spec.get('chapter')
        sec = ui_spec.get('section')
        if ch:
            if sec and sec > 0:
                return f"{ch}.{sec} {t}"
            return f"{ch} {t}"
        return t

    win = tk.Toplevel(parent)
    win.title(make_title(lang))
    win.geometry(win_size)

    # ---------- 内部状态 ----------
    current_lang = lang
    current_precision = precision
    current_font_size = font_size

    input_widgets = {}      # {name: [Entry,...] 或 Entry 或 StringVar}
    input_labels = {}       # {name: LabelFrame / Label} 用于语言切换时改标题
    list_labels = {}        # {name: [Label,...]} 每行前缀标签
    hint_labels = {}        # {name: Label} 提示文字
    choice_buttons = {}     # {name: [(Radiobutton, option_dict), ...]}

    # ---------- 字体 ----------
    def get_font(size=None):
        if size is None:
            size = current_font_size
        # ★ 字体族：中文用宋体，英文用 Times New Roman；可自行替换
        family = "Times New Roman" if current_lang == 'en' else "宋体"
        return (family, size)

    def update_all_fonts():
        font = get_font()
        for child in toolbar.winfo_children():
            try:
                child.config(font=font)
            except (tk.TclError, TypeError):
                pass
        _apply_font_recursive(content, font, skip=(title_label,))
        # ★ 标题字号（相对正文 +4），可自行调整
        title_label.config(font=get_font(14))

    # ---------- 工具栏按钮刷新 ----------
    def refresh_precision_button():
        precision_btn.config(
            text=f"{L[current_lang]['precision_label']}: {current_precision}"
        )

    def refresh_lang_buttons():
        # ★ 语言按钮选中/未选中时的背景色
        if current_lang == 'zh':
            lang_zh_btn.config(relief=tk.SUNKEN, bg='#d0d0d0')
            lang_en_btn.config(relief=tk.RAISED, bg='lightgray')
        else:
            lang_zh_btn.config(relief=tk.RAISED, bg='lightgray')
            lang_en_btn.config(relief=tk.SUNKEN, bg='#d0d0d0')

    # ---------- 重新编号列表前缀 ----------
    def renumber_list(param_name):
        if param_name not in list_labels:
            return
        param = next((p for p in ui_spec['inputs']
                      if p['name'] == param_name), None)
        if param is None:
            return
        prefix = _get_item_prefix(param, L, current_lang)
        for i, lbl in enumerate(list_labels[param_name], start=1):
            # ★ 前缀与编号之间加下划线，例如 x_1、数据_2
            lbl.config(text=f"{prefix}_{i}" if prefix else str(i))

    def renumber_all_lists():
        for name in list_labels:
            renumber_list(name)

    # ---------- 语言切换 ----------
    def set_language(new_lang):
        nonlocal current_lang
        if new_lang == current_lang:
            return
        current_lang = new_lang
        win.title(make_title(current_lang))

        for param in ui_spec['inputs']:
            name = param['name']
            if name in input_labels:
                input_labels[name].config(text=param['label'][current_lang])
            if name in hint_labels:
                h = param.get('hint')
                hint_labels[name].config(text=_get_localized(h, current_lang))
            if name in choice_buttons:
                for rb, opt in choice_buttons[name]:
                    rb.config(text=opt['label'][current_lang])

        renumber_all_lists()

        calc_btn.config(text=L[current_lang]['calculate'])
        input_section.config(text=L[current_lang]['input_section_title'])
        output_section.config(text=L[current_lang]['output_section_title'])
        title_label.config(text=make_title(current_lang))

        refresh_lang_buttons()
        refresh_precision_button()
        update_all_fonts()

    # ---------- 精度设置 ----------
    def set_precision():
        nonlocal current_precision
        dlg = simpledialog.askinteger(
            L[current_lang]['precision_dialog_title'],
            L[current_lang]['precision_dialog_prompt'],
            initialvalue=current_precision
        )
        if dlg is not None and dlg >= 0:
            current_precision = dlg
            refresh_precision_button()

    # ---------- 构建输入区 ----------
    def build_input_area(parent_frame, spec):
        widgets = {}
        for param in spec['inputs']:
            name = param['name']
            label = param['label'][current_lang]
            ptype = param.get('type', 'float')
            initial = param.get('initial', 1)
            unit = param.get('unit', '') or ''
            hint_text = _get_localized(param.get('hint'), current_lang)

            # ============ 列表型 ============
            if ptype == 'list':
                frame = tk.LabelFrame(parent_frame, text=label, font=get_font())
                # ★ 外层 LabelFrame 的边距 (padx, pady)
                frame.pack(fill=tk.X, padx=4, pady=3)
                input_labels[name] = frame

                if hint_text:
                    hint_lbl = tk.Label(
                        frame, text=hint_text,
                        font=get_font(),
                        fg='#555',           # ★ 提示文字颜色
                        anchor='w', justify='left',
                        wraplength=620       # ★ 提示文字自动换行宽度（像素）
                    )
                    hint_lbl.pack(fill=tk.X, padx=6, pady=(3, 1))
                    hint_labels[name] = hint_lbl

                container = tk.Frame(frame)
                container.pack(fill=tk.X, padx=3, pady=2)

                entries = []
                labels = []
                list_labels[name] = labels

                def make_add_row(container_ref, entries_ref, labels_ref,
                                 p=param, u=unit):
                    def add_row():
                        idx = len(entries_ref) + 1
                        prefix = _get_item_prefix(p, L, current_lang)
                        row = tk.Frame(container_ref)
                        row.pack(fill=tk.X, pady=1)

                        # ★ 前缀与编号之间加下划线，例如 x_1、数据_2
                        # ★ width 由 6 调整为 8，避免 x_10 等编号被截断
                        lbl = tk.Label(
                            row,
                            text=f"{prefix}_{idx}" if prefix else str(idx),
                            font=get_font(),
                            width=8,              # ★ 前缀标签宽度（字符数）
                            anchor='w'
                        )
                        lbl.pack(side=tk.LEFT, padx=2)

                        entry = tk.Entry(
                            row, font=get_font(),
                            width=15              # ★ 列表输入框宽度（字符数）
                        )
                        entry.pack(side=tk.LEFT, padx=2)

                        if u:
                            tk.Label(row, text=u, font=get_font()).pack(
                                side=tk.LEFT, padx=(0, 6))

                        del_btn = tk.Button(
                            row, text=L[current_lang]['delete'],
                            font=get_font(),
                            command=lambda e=entry: remove_row(e))
                        del_btn.pack(side=tk.LEFT, padx=2)

                        entries_ref.append(entry)
                        labels_ref.append(lbl)
                        update_del_btns()
                    return add_row

                def remove_row(entry):
                    if len(entries) <= 1:
                        return
                    idx = entries.index(entry)
                    row = entry.master
                    row.destroy()
                    entries.pop(idx)
                    labels.pop(idx)
                    renumber_list(name)
                    update_del_btns()

                def update_del_btns():
                    """只有一行时禁用删除按钮。"""
                    for row_frame in container.winfo_children():
                        for child in row_frame.winfo_children():
                            if isinstance(child, tk.Button):
                                child.config(
                                    state=tk.NORMAL if len(entries) > 1
                                    else tk.DISABLED)

                add_row = make_add_row(container, entries, labels, param, unit)
                for _ in range(max(1, initial)):
                    add_row()

                tk.Button(frame, text=L[current_lang]['add_data'],
                          font=get_font(), command=add_row).pack(pady=2)
                widgets[name] = entries

            # ============ 单选项 ============
            elif ptype == 'choice':
                frame = tk.LabelFrame(parent_frame, text=label, font=get_font())
                frame.pack(fill=tk.X, padx=4, pady=3)
                input_labels[name] = frame

                if hint_text:
                    hint_lbl = tk.Label(
                        frame, text=hint_text,
                        font=get_font(),
                        fg='#555',           # ★ 提示文字颜色
                        anchor='w', justify='left',
                        wraplength=620       # ★ 提示文字自动换行宽度
                    )
                    hint_lbl.pack(fill=tk.X, padx=6, pady=(3, 1))
                    hint_labels[name] = hint_lbl

                row = tk.Frame(frame)
                row.pack(fill=tk.X, padx=3, pady=3)

                var = tk.StringVar(value=param.get('default', ''))
                choice_buttons[name] = []
                for opt in param.get('options', []):
                    val = opt['value']
                    opt_lbl = opt['label'][current_lang]
                    rb = tk.Radiobutton(row, text=opt_lbl, variable=var,
                                        value=val, font=get_font(),
                                        anchor='w')
                    rb.pack(side=tk.LEFT, padx=4)
                    choice_buttons[name].append((rb, opt))
                widgets[name] = var

            # ============ 单行文本 ============
            elif ptype == 'text':
                frame = tk.Frame(parent_frame)
                frame.pack(fill=tk.X, padx=4, pady=3)
                lbl = tk.Label(
                    frame, text=label, font=get_font(),
                    width=14,                     # ★ 单值标签宽度（字符数）
                    anchor='w'
                )
                lbl.pack(side=tk.LEFT, padx=3)
                input_labels[name] = lbl

                entry = tk.Entry(frame, font=get_font())
                entry.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                if 'default' in param:
                    entry.insert(0, str(param['default']))
                widgets[name] = entry

            # ============ 单值数值 (float/int) ============
            else:
                frame = tk.Frame(parent_frame)
                frame.pack(fill=tk.X, padx=4, pady=3)
                lbl = tk.Label(
                    frame, text=label, font=get_font(),
                    width=14,                     # ★ 单值标签宽度（字符数）
                    anchor='w'
                )
                lbl.pack(side=tk.LEFT, padx=3)
                input_labels[name] = lbl

                entry = tk.Entry(frame, font=get_font())
                entry.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                if 'default' in param:
                    entry.insert(0, str(param['default']))
                if unit:
                    tk.Label(frame, text=unit, font=get_font()).pack(
                        side=tk.LEFT, padx=(0, 4))

                if hint_text:
                    hint_lbl = tk.Label(
                        frame, text=hint_text,
                        font=get_font(),
                        fg='#555',           # ★ 提示文字颜色
                        anchor='w', justify='left'
                    )
                    hint_lbl.pack(side=tk.LEFT, padx=(6, 4))
                    hint_labels[name] = hint_lbl

                widgets[name] = entry

        return widgets

    # ---------- 计算 ----------
    def calculate():
        args = {}
        for param in ui_spec['inputs']:
            name = param['name']
            ptype = param.get('type', 'float')

            if ptype == 'list':
                entries = input_widgets[name]
                values = []
                for entry in entries:
                    val = entry.get().strip()
                    if val:
                        try:
                            values.append(float(val))
                        except ValueError:
                            output_text.insert(
                                tk.END,
                                L[current_lang]['invalid_error'] + "\n")
                            return
                if not values:
                    output_text.insert(
                        tk.END,
                        L[current_lang]['empty_error'] + "\n")
                    return
                args[name] = values

            elif ptype == 'choice':
                args[name] = input_widgets[name].get()

            elif ptype == 'text':
                args[name] = input_widgets[name].get().strip()

            else:
                entry = input_widgets[name]
                val = entry.get().strip()
                if not val:
                    label = param['label'][current_lang]
                    output_text.insert(
                        tk.END,
                        L[current_lang]['enter_error'].format(label=label) + "\n")
                    return
                try:
                    args[name] = int(val) if ptype == 'int' else float(val)
                except ValueError:
                    output_text.insert(
                        tk.END,
                        L[current_lang]['invalid_error'] + "\n")
                    return

        func_name = ui_spec.get('func', 'calculate')
        if not hasattr(core_module, func_name):
            output_text.insert(
                tk.END,
                L[current_lang]['core_missing'].format(func=func_name) + "\n")
            return
        calc_func = getattr(core_module, func_name)

        try:
            result = calc_func(**args, precision=current_precision)
        except Exception as e:
            output_text.insert(
                tk.END,
                L[current_lang]['calc_error'].format(err=e) + "\n")
            return

        if result is None:
            output_text.insert(tk.END, L[current_lang]['calc_failed'] + "\n")
            return

        output_text.insert(tk.END, L[current_lang]['result_prefix'] + "\n")
        for out in ui_spec.get('outputs', []):
            out_name = out['name']
            if out_name in result:
                label = out['label'][current_lang]
                value = result[out_name]
                if isinstance(value, float):
                    output_text.insert(
                        tk.END,
                        f"{label}: {value:.{current_precision}f}\n")
                else:
                    output_text.insert(tk.END, f"{label}: {value}\n")
        output_text.see(tk.END)

    # ---------- 字号增减 ----------
    def change_font(delta):
        nonlocal current_font_size
        new_size = current_font_size + delta
        # ★ 字号范围限制：8 ~ 20
        if 8 <= new_size <= 20:
            current_font_size = new_size
            update_all_fonts()

    # =========================================================
    # 构建工具栏
    # =========================================================
    toolbar = tk.Frame(win, bg='lightgray', height=30)
    toolbar.pack(side=tk.TOP, fill=tk.X)

    lang_zh_btn = tk.Button(toolbar, text=L[current_lang]['lang_zh'],
                            font=get_font(), command=lambda: set_language('zh'),
                            relief=tk.SUNKEN, bg='#d0d0d0', bd=1)
    lang_zh_btn.pack(side=tk.LEFT, padx=(5, 0))
    lang_en_btn = tk.Button(toolbar, text=L[current_lang]['lang_en'],
                            font=get_font(), command=lambda: set_language('en'),
                            relief=tk.RAISED, bg='lightgray', bd=1)
    lang_en_btn.pack(side=tk.LEFT, padx=(0, 5))

    precision_btn = tk.Button(toolbar, text="", font=get_font(),
                              command=set_precision, bg='lightgray', bd=1)
    precision_btn.pack(side=tk.LEFT, padx=5)
    refresh_precision_button()

    increase_btn = tk.Button(toolbar, text="A+", font=get_font(),
                             command=lambda: change_font(2), bg='lightgray')
    increase_btn.pack(side=tk.RIGHT, padx=2)
    decrease_btn = tk.Button(toolbar, text="A-", font=get_font(),
                             command=lambda: change_font(-2), bg='lightgray')
    decrease_btn.pack(side=tk.RIGHT, padx=2)

    refresh_lang_buttons()

    # =========================================================
    # 构建主区域
    # =========================================================
    main_frame = tk.Frame(win)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 可滚动区域：canvas + scrollbar
    canvas = tk.Canvas(main_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    content = scrollable_frame

    # 顶部标题
    title_label = tk.Label(content, text=make_title(current_lang),
                           font=get_font(14))
    title_label.pack(pady=5)

    # “输入”区块
    input_section = tk.LabelFrame(content,
                                  text=L[current_lang]['input_section_title'],
                                  font=get_font())
    # ★ “输入”区块距离窗口左右与上下的边距 (padx, pady)
    input_section.pack(fill=tk.X, padx=8, pady=3)

    input_widgets = build_input_area(input_section, ui_spec)

    # “计算”按钮
    calc_btn = tk.Button(content, text=L[current_lang]['calculate'],
                         font=get_font(), command=calculate)
    calc_btn.pack(pady=4)

    # “输出”区块
    output_section = tk.LabelFrame(content,
                                   text=L[current_lang]['output_section_title'],
                                   font=get_font())
    output_section.pack(fill=tk.BOTH, expand=True, padx=8, pady=3)

    output_text = scrolledtext.ScrolledText(
        output_section,
        font=get_font(),
        height=10                # ★ 输出框高度（行数）
    )
    output_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

    return win


# ============================================================================
# ============================================================================
# 【C】窗口启动入口
#     ⚠️ 主菜单通过 open_page 调用本页面，函数签名不建议修改。
# ============================================================================
# ============================================================================

def open_page(parent, settings, core_module, override_module=None):
    """
    启动二级界面。

    参数:
        parent          : 父窗口
        settings        : dict，含 language / precision / font_size
        core_module     : 已加载的核心模块（必须含 UI_SPEC）
        override_module : 可选，专用 UI 模块
    """
    return _build_ui(parent, settings, core_module, override_module)