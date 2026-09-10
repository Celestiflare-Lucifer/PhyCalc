# -*- coding: utf-8 -*-
"""
通用二级UI界面模板
文件名：00_通用_generic_page.py

【本文件的三种使用方式】

  1) 通用界面（自动）：
     主菜单在没有找到配套专用 page 时，会自动调用本文件的 open_page。

  2) 个性化模板（推荐）：
     要为某实验定制专属界面，请在 ui_pages/ 下新建
         nn_中文名_英文名_page.py
     并 **只复制本文件【A】区（个性化配置区）的全部内容** 到新文件。
     通用窗口、控件、按钮、滚动区等代码无需复制——它们都在【B】【C】中。

  3) 完全自定义（高级）：
     如果专用页面自己定义了 open_page(parent, settings, core_module)，
     主菜单会直接调用该函数，跳过通用界面。此时才需要复制本文件全部内容。
"""

# ============================================================================
# ============================================================================
# 【A】个性化配置区
#     ┌───────────────────────────────────────────────────────────────────┐
#     │ 复制模板时，只需复制下面这一节（从本行到“【A】结束”）的全部内容。│
#     │ 其余部分（【B】、【C】）不需要复制。                            │
#     │ 复制后按需修改三个变量的值即可。                                │
#     └───────────────────────────────────────────────────────────────────┘
# ============================================================================
# ============================================================================

# ----------------------------------------------------------------------------
# A-1. 默认界面文本
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
# A-2. 语言覆盖（可选），若不需要保持 None
# ----------------------------------------------------------------------------
LANG_OVERRIDE = None

# ----------------------------------------------------------------------------
# A-3. UI_SPEC 覆盖（可选），若不需要保持 None
#      浅合并：提供的键会整体替换 core.UI_SPEC 中的同名键。
#      若只改某一项，务必写完整的 items 数组。
#
#      示例：
#          UI_SPEC_OVERRIDE = {
#              'title': {'zh': '自定义标题', 'en': 'Custom Title'},
#              'inputs': [
#                  {'name': 'data',
#                   'label': {'zh': '数据', 'en': 'Data'},
#                   'type': 'list', 'initial': 8,
#                   'item_prefix': {'zh': '数据', 'en': 'Data'}},
#              ],
#          }
# ----------------------------------------------------------------------------
UI_SPEC_OVERRIDE = None

# ----------------------------------------------------------------------------
# A-4. 二级窗口默认尺寸（宽x高）
# ----------------------------------------------------------------------------
DEFAULT_WINDOW_SIZE = "650x500"

# ============================================================================
# 【A】结束   下面内容在复制模板时不需要包含
# ============================================================================


import tkinter as tk
from tkinter import scrolledtext, simpledialog


# ============================================================================
# ============================================================================
# 【B】通用界面构建
#     ⚠️ 以下为通用机械代码，除有特殊需求外，不建议自行修改。
# ============================================================================
# ============================================================================

def _merge_lang(override_module):
    merged = {k: dict(v) for k, v in LANG.items()}
    if override_module:
        ov = getattr(override_module, 'LANG_OVERRIDE', None)
        if ov:
            for lg, d in ov.items():
                merged.setdefault(lg, {}).update(d)
    return merged


def _merge_spec(core_module, override_module):
    spec = dict(core_module.UI_SPEC)
    if override_module:
        ov = getattr(override_module, 'UI_SPEC_OVERRIDE', None)
        if ov:
            spec.update(ov)
    return spec


def _pick_window_size(override_module):
    if override_module:
        s = getattr(override_module, 'DEFAULT_WINDOW_SIZE', None)
        if s:
            return s
    return DEFAULT_WINDOW_SIZE


def _apply_font_recursive(widget, font, skip=()):
    if widget in skip:
        return
    try:
        widget.config(font=font)
    except (tk.TclError, TypeError):
        pass
    for child in widget.winfo_children():
        _apply_font_recursive(child, font, skip)


def _get_item_prefix(param, L, current_lang):
    """获取列表型参数每项的前缀文字。"""
    prefix = param.get('item_prefix')
    if isinstance(prefix, dict):
        return prefix.get(current_lang, '')
    if isinstance(prefix, str):
        return prefix
    return L[current_lang].get('item_default_prefix', '')


def _build_ui(parent, settings, core_module, override_module=None):
    if not hasattr(core_module, 'UI_SPEC'):
        raise ValueError("Core 模块缺少 UI_SPEC 定义。")

    L = _merge_lang(override_module)
    ui_spec = _merge_spec(core_module, override_module)
    win_size = _pick_window_size(override_module)

    lang = settings.get('language', 'zh')
    precision = settings.get('precision', 3)
    font_size = settings.get('font_size', 10)

    win = tk.Toplevel(parent)
    win.title(ui_spec['title'][lang])
    win.geometry(win_size)

    # ---------- 状态变量 ----------
    current_lang = lang
    current_precision = precision
    current_font_size = font_size

    input_widgets = {}   # {name: [Entry,...] 或 Entry}
    input_labels = {}    # {name: widget} 供语言切换时改标题
    list_labels = {}     # {name: [Label,...]} 每行前缀标签

    # ---------- 字体 ----------
    def get_font(size=None):
        if size is None:
            size = current_font_size
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
        title_label.config(font=get_font(14))

    # ---------- 工具栏按钮刷新 ----------
    def refresh_precision_button():
        precision_btn.config(
            text=f"{L[current_lang]['precision_label']}: {current_precision}"
        )

    def refresh_lang_buttons():
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
            lbl.config(text=f"{prefix}{i}")

    def renumber_all_lists():
        for name in list_labels:
            renumber_list(name)

    # ---------- 语言切换 ----------
    def set_language(new_lang):
        nonlocal current_lang
        if new_lang == current_lang:
            return
        current_lang = new_lang
        win.title(ui_spec['title'][current_lang])

        for param in ui_spec['inputs']:
            name = param['name']
            if name in input_labels:
                input_labels[name].config(text=param['label'][current_lang])

        renumber_all_lists()

        calc_btn.config(text=L[current_lang]['calculate'])
        input_section.config(text=L[current_lang]['input_section_title'])
        output_section.config(text=L[current_lang]['output_section_title'])

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

            if ptype == 'list':
                frame = tk.LabelFrame(parent_frame, text=label, font=get_font())
                frame.pack(fill=tk.X, padx=4, pady=2)
                input_labels[name] = frame

                container = tk.Frame(frame)
                container.pack(fill=tk.X, padx=3, pady=2)

                entries = []
                labels = []
                list_labels[name] = labels

                def make_add_row(container_ref, entries_ref, labels_ref, p=param):
                    def add_row():
                        idx = len(entries_ref) + 1
                        prefix = _get_item_prefix(p, L, current_lang)
                        row = tk.Frame(container_ref)
                        row.pack(fill=tk.X, pady=1)
                        lbl = tk.Label(row, text=f"{prefix}{idx}",
                                       font=get_font(), width=6, anchor='w')
                        lbl.pack(side=tk.LEFT, padx=2)
                        entry = tk.Entry(row, font=get_font(), width=15)
                        entry.pack(side=tk.LEFT, padx=2)
                        del_btn = tk.Button(
                            row, text=L[current_lang]['delete'],
                            font=get_font(),
                            command=lambda e=entry: remove_row(e)
                        )
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
                    for row_frame in container.winfo_children():
                        for child in row_frame.winfo_children():
                            if isinstance(child, tk.Button):
                                child.config(
                                    state=tk.NORMAL if len(entries) > 1
                                    else tk.DISABLED
                                )

                add_row = make_add_row(container, entries, labels, param)
                for _ in range(max(1, initial)):
                    add_row()

                tk.Button(frame, text=L[current_lang]['add_data'],
                          font=get_font(), command=add_row).pack(pady=2)
                widgets[name] = entries

            else:
                # 非列表型：标签与输入框同行
                frame = tk.Frame(parent_frame)
                frame.pack(fill=tk.X, padx=4, pady=2)
                lbl = tk.Label(frame, text=label, font=get_font(),
                               width=10, anchor='w')
                lbl.pack(side=tk.LEFT, padx=3)
                input_labels[name] = lbl

                entry = tk.Entry(frame, font=get_font())
                entry.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                if 'default' in param:
                    entry.insert(0, str(param['default']))
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
                                L[current_lang]['invalid_error'] + "\n"
                            )
                            return
                if not values:
                    output_text.insert(
                        tk.END,
                        L[current_lang]['empty_error'] + "\n"
                    )
                    return
                args[name] = values
            else:
                entry = input_widgets[name]
                val = entry.get().strip()
                if not val:
                    label = param['label'][current_lang]
                    output_text.insert(
                        tk.END,
                        L[current_lang]['enter_error'].format(label=label) + "\n"
                    )
                    return
                try:
                    args[name] = int(val) if ptype == 'int' else float(val)
                except ValueError:
                    output_text.insert(
                        tk.END,
                        L[current_lang]['invalid_error'] + "\n"
                    )
                    return

        func_name = ui_spec.get('func', 'calculate')
        if not hasattr(core_module, func_name):
            output_text.insert(
                tk.END,
                L[current_lang]['core_missing'].format(func=func_name) + "\n"
            )
            return
        calc_func = getattr(core_module, func_name)

        try:
            result = calc_func(**args, precision=current_precision)
        except Exception as e:
            output_text.insert(
                tk.END,
                L[current_lang]['calc_error'].format(err=e) + "\n"
            )
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
                        f"{label}: {value:.{current_precision}f}\n"
                    )
                else:
                    output_text.insert(tk.END, f"{label}: {value}\n")
        output_text.see(tk.END)

    # ---------- 字号 ----------
    def change_font(delta):
        nonlocal current_font_size
        new_size = current_font_size + delta
        if 8 <= new_size <= 20:
            current_font_size = new_size
            update_all_fonts()

    # =========================================================
    # 构建工具栏
    # =========================================================
    toolbar = tk.Frame(win, bg='lightgray', height=30)
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # 语言切换（两个并排按钮，当前语言为按下状态）
    lang_zh_btn = tk.Button(toolbar, text=L[current_lang]['lang_zh'],
                            font=get_font(), command=lambda: set_language('zh'),
                            relief=tk.SUNKEN, bg='#d0d0d0', bd=1)
    lang_zh_btn.pack(side=tk.LEFT, padx=(5, 0))
    lang_en_btn = tk.Button(toolbar, text=L[current_lang]['lang_en'],
                            font=get_font(), command=lambda: set_language('en'),
                            relief=tk.RAISED, bg='lightgray', bd=1)
    lang_en_btn.pack(side=tk.LEFT, padx=(0, 5))

    # 精度（直接点击弹窗）
    precision_btn = tk.Button(toolbar, text="", font=get_font(),
                              command=set_precision, bg='lightgray', bd=1)
    precision_btn.pack(side=tk.LEFT, padx=5)
    refresh_precision_button()

    # 字号
    increase_btn = tk.Button(toolbar, text="A+", font=get_font(),
                             command=lambda: change_font(2), bg='lightgray')
    increase_btn.pack(side=tk.RIGHT, padx=2)
    decrease_btn = tk.Button(toolbar, text="A-", font=get_font(),
                             command=lambda: change_font(-2), bg='lightgray')
    decrease_btn.pack(side=tk.RIGHT, padx=2)

    refresh_lang_buttons()

    # =========================================================
    # 主区域
    # =========================================================
    main_frame = tk.Frame(win)
    main_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(main_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    content = scrollable_frame

    title_label = tk.Label(content, text=ui_spec['title'][current_lang],
                           font=get_font(14))
    title_label.pack(pady=5)

    input_section = tk.LabelFrame(content,
                                  text=L[current_lang]['input_section_title'],
                                  font=get_font())
    input_section.pack(fill=tk.X, padx=8, pady=3)

    input_widgets = build_input_area(input_section, ui_spec)

    calc_btn = tk.Button(content, text=L[current_lang]['calculate'],
                         font=get_font(), command=calculate)
    calc_btn.pack(pady=4)

    output_section = tk.LabelFrame(content,
                                   text=L[current_lang]['output_section_title'],
                                   font=get_font())
    output_section.pack(fill=tk.BOTH, expand=True, padx=8, pady=3)

    output_text = scrolledtext.ScrolledText(output_section,
                                            font=get_font(), height=8)
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
        override_module : 可选，专用页面模块
    """
    return _build_ui(parent, settings, core_module, override_module)