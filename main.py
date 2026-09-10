# -*- coding: utf-8 -*-
"""
PhyCalc - 格物算：大学物理实验数据处理工具
主菜单
"""
import os
import sys
import json
import glob
import importlib.util
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

sys.path.insert(0, os.path.dirname(__file__))

# ========== 项目元信息 ==========
APP_VERSION = 'v0.1.0'

ABOUT_TEXT = {
    'zh': (
        "PhyCalc·格物算\n"
        "格物算：大学物理实验数据处理工具\n\n"
        f"版本：{APP_VERSION}\n\n"
        "作者：星辰蝶语 (Celestiflare Lucifer)\n\n"
        "本工具基于 DeepSeek + Python + Tkinter 制作，\n"
        "使用 PyInstaller 打包分发。\n\n"
        "如有需要，可通过GitHub个人页面联系作者，\n"
        "或者发送邮件到：15114671359@nefu.edu.cn\n\n"
        "感谢使用！"
    ),
    'en': (
        "PhyCalc · Scientific Calculations\n"
        "Scientific Calculations: A Data Processing Tool for University Physics Experiments\n\n"        
        f"Version: {APP_VERSION}\n\n"        
        "Author: Celestiflare Lucifer\n\n"        
        "This tool is developed based on DeepSeek + Python + Tkinter,\n"
        "and distributed using PyInstaller.\n"        
        "If needed, you can contact the author through the GitHub profile,\n"
        "or send an email to: 15114671359@nefu.edu.cn\n\n"        
        "Thank you for using!"
    )
}

# ========== 语言字典 ==========
LANG = {
    'zh': {
        'app_title': '格物算：大学物理实验数据处理工具',
        'about': '关于',
        'settings': '设置',
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision': '计算精度（小数位数）',
        'layout': '选项布局',
        'layout_button': '按钮模式',
        'layout_text': '文字模式',
        'default_size': '默认窗口大小',
        'increase_font': '增大字体',
        'decrease_font': '减小字体',
        'no_experiments': '未找到实验选项',
        'restart_hint': '更改默认窗口大小需要重启程序生效。',
        'width': '宽度：',
        'height': '高度：',
        'chapter': '第{0}章',
        'chapter_en': 'Chapter {0}',
        'ok': '确定',
    },
    'en': {
        'app_title': 'PhyCalc: Physics Experiment Data Processing Tool',
        'about': 'About',
        'settings': 'Settings',
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision': 'Precision (decimal places)',
        'layout': 'Layout',
        'layout_button': 'Button Mode',
        'layout_text': 'Text Mode',
        'default_size': 'Default Window Size',
        'increase_font': 'Increase Font',
        'decrease_font': 'Decrease Font',
        'no_experiments': 'No experiments found.',
        'restart_hint': 'Changing default window size requires restart.',
        'width': 'Width:',
        'height': 'Height:',
        'chapter': 'Chapter {0}',
        'chapter_en': 'Chapter {0}',
        'ok': 'OK',
    }
}

DEFAULT_SETTINGS = {
    'language': 'zh',
    'precision': 3,
    'layout': 'button',
    'window_width': 600,
    'window_height': 400,
    'font_size': 10,
}

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[设置] 读取 settings.json 失败，使用默认值：{e}")
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """保存设置。写失败时只打印警告，不打断主流程。"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[设置] 保存 settings.json 失败（本次修改仅当前会话有效）：{e}")


class MainApp:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.lang = self.settings.get('language', 'zh')
        self.precision = self.settings.get('precision', 3)
        self.layout_mode = self.settings.get('layout', 'button')
        self.font_size = self.settings.get('font_size', 10)
        self.window_width = self.settings.get('window_width', 600)
        self.window_height = self.settings.get('window_height', 400)

        self.child_windows = []

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.title(LANG[self.lang]['app_title'])

        self.create_toolbar()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.scan_experiments()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---------------------------------------------------------------
    # 通用辅助
    # ---------------------------------------------------------------
    def get_font(self, size=None):
        if size is None:
            size = self.font_size
        family = "Times New Roman" if self.lang == 'en' else "宋体"
        return (family, size)

    # ---------------------------------------------------------------
    # 工具栏
    # ---------------------------------------------------------------
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg='lightgray', height=30)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.about_btn = tk.Button(toolbar, text=LANG[self.lang]['about'],
                                   font=self.get_font(), bg='lightgray',
                                   relief=tk.FLAT, command=self.show_about)
        self.about_btn.pack(side=tk.LEFT, padx=5)

        self.settings_btn = tk.Menubutton(toolbar, text=LANG[self.lang]['settings'],
                                          font=self.get_font(), bg='lightgray')
        self.settings_menu = tk.Menu(self.settings_btn, tearoff=0)
        self.settings_btn.config(menu=self.settings_menu)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        self._build_settings_menu()

        self.increase_btn = tk.Button(toolbar, text="A+", font=self.get_font(),
                                      command=self.increase_font, bg='lightgray')
        self.increase_btn.pack(side=tk.RIGHT, padx=2)
        self.decrease_btn = tk.Button(toolbar, text="A-", font=self.get_font(),
                                      command=self.decrease_font, bg='lightgray')
        self.decrease_btn.pack(side=tk.RIGHT, padx=2)

        self.toolbar = toolbar

    def show_about(self):
        win = tk.Toplevel(self.root)
        win.title(LANG[self.lang]['about'])
        win.geometry("440x340")
        win.transient(self.root)

        txt = tk.Text(win, wrap=tk.WORD, font=self.get_font(), padx=15, pady=15,
                      relief=tk.FLAT)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert('1.0', ABOUT_TEXT[self.lang])
        txt.config(state=tk.DISABLED)

        ok_btn = tk.Button(win, text=LANG[self.lang]['ok'],
                           font=self.get_font(), command=win.destroy)
        ok_btn.pack(pady=5)

    def _build_settings_menu(self):
        self.settings_menu.delete(0, 'end')
        lang = self.lang
        self.settings_menu.add_command(label=LANG[lang]['lang_zh'],
                                       command=self.set_language_zh)
        self.settings_menu.add_command(label=LANG[lang]['lang_en'],
                                       command=self.set_language_en)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label=LANG[lang]['precision'],
                                       command=self.set_precision)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label=LANG[lang]['layout_button'],
                                       command=lambda: self.set_layout('button'))
        self.settings_menu.add_command(label=LANG[lang]['layout_text'],
                                       command=lambda: self.set_layout('text'))
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label=LANG[lang]['default_size'],
                                       command=self.set_default_size)

    # ---------------------------------------------------------------
    # 语言
    # ---------------------------------------------------------------
    def set_language_zh(self):
        self.set_language('zh')

    def set_language_en(self):
        self.set_language('en')

    def set_language(self, lang):
        if lang == self.lang:
            return
        self.lang = lang
        self.settings['language'] = lang

        # 先刷新界面，再持久化
        self.root.title(LANG[lang]['app_title'])
        self.about_btn.config(text=LANG[lang]['about'])
        self.settings_btn.config(text=LANG[lang]['settings'])
        self._build_settings_menu()
        self.scan_experiments()

        save_settings(self.settings)

    # ---------------------------------------------------------------
    # 精度 / 布局 / 窗口大小 / 字号
    # ---------------------------------------------------------------
    def set_precision(self):
        dlg = simpledialog.askinteger("精度设置", "请输入小数位数（整数）：",
                                      initialvalue=self.precision)
        if dlg is not None and dlg >= 0:
            self.precision = dlg
            self.settings['precision'] = dlg
            save_settings(self.settings)

    def set_layout(self, mode):
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        self.settings['layout'] = mode
        self.scan_experiments()
        save_settings(self.settings)

    def set_default_size(self):
        w = simpledialog.askinteger("默认宽度", "请输入窗口宽度（像素）：",
                                    initialvalue=self.window_width)
        if w is None:
            return
        h = simpledialog.askinteger("默认高度", "请输入窗口高度（像素）：",
                                    initialvalue=self.window_height)
        if h is None:
            return
        if w > 0 and h > 0:
            self.window_width = w
            self.window_height = h
            self.settings['window_width'] = w
            self.settings['window_height'] = h
            save_settings(self.settings)
            messagebox.showinfo("提示", LANG[self.lang]['restart_hint'])

    def increase_font(self):
        if self.font_size < 20:
            self.font_size += 2
            self.settings['font_size'] = self.font_size
            self._update_all_fonts()
            save_settings(self.settings)

    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 2
            self.settings['font_size'] = self.font_size
            self._update_all_fonts()
            save_settings(self.settings)

    def _update_all_fonts(self):
        font = self.get_font()
        self.about_btn.config(font=font)
        self.settings_btn.config(font=font)
        self.increase_btn.config(font=font)
        self.decrease_btn.config(font=font)
        self.scan_experiments()

    # ---------------------------------------------------------------
    # 从 core 文件读取标题（zh / en）
    # ---------------------------------------------------------------
    def _read_core_titles(self, core_path):
        """
        加载 core 模块并读取 UI_SPEC['title']。
        返回 (zh_title, en_title) 或 (None, None)。
        """
        try:
            spec = importlib.util.spec_from_file_location(
                f"_scan_{id(core_path)}", core_path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            title = getattr(mod, 'UI_SPEC', {}).get('title', {})
            return title.get('zh'), title.get('en')
        except Exception as e:
            print(f"[扫描] 无法读取 {core_path} 的标题：{e}")
            return None, None

    # ---------------------------------------------------------------
    # 扫描 core_calculations 并跳过 00_ 模板
    # ---------------------------------------------------------------
    def scan_experiments(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        core_dir = os.path.join(os.path.dirname(__file__), 'core_calculations')
        if not os.path.exists(core_dir):
            tk.Label(self.main_frame, text=LANG[self.lang]['no_experiments'],
                     font=self.get_font()).pack()
            return

        pattern = os.path.join(core_dir, '*_core.py')
        all_files = glob.glob(pattern)
        core_files = [f for f in all_files
                      if not os.path.basename(f).startswith('00_')]

        if not core_files:
            tk.Label(self.main_frame, text=LANG[self.lang]['no_experiments'],
                     font=self.get_font()).pack()
            return

        experiments = []
        for f in core_files:
            basename = os.path.basename(f)
            stem = basename[:-3] if basename.endswith('.py') else basename
            parts = stem.split('_')
            # 标准命名：nn_中文名_英文名_core
            if len(parts) >= 3 and parts[-1] == 'core' and parts[0].isdigit():
                nn = int(parts[0])   # int 转换，自动去掉前导零

                # 优先从 core 模块读取标题
                zh_title, en_title = self._read_core_titles(f)

                # 回退：文件名解析
                if not zh_title or not en_title:
                    zh_title = parts[1]
                    en_title = '_'.join(parts[2:-1]).replace('_', ' ').title()

                experiments.append((nn, zh_title, en_title, f))
            else:
                # 非标准命名：整名显示
                experiments.append((None, basename, basename, f))

        standard = [e for e in experiments if e[0] is not None]
        non_std = [e for e in experiments if e[0] is None]
        standard.sort(key=lambda x: x[0])
        non_std.sort(key=lambda x: x[1])
        sorted_exps = standard + non_std

        if self.layout_mode == 'button':
            self._display_buttons(sorted_exps)
        else:
            self._display_text(sorted_exps)

    # ---------------------------------------------------------------
    # 按钮文字
    #   中文：第1章 平均值与不确定度计算          （不带前导零）
    #   英文：Chapter 1 Average and Uncertainty Calculation
    #   nn 已为 int，f"{nn}" 天然不带前导零
    # ---------------------------------------------------------------
    def _format_label(self, nn, zh_title, en_title):
        if nn is not None:
            if self.lang == 'zh':
                return f"第{nn}章 {zh_title}"
            else:
                return f"Chapter {nn} {en_title}"
        else:
            return zh_title

    def _display_buttons(self, experiments):
        n = len(experiments)
        if n == 0:
            return
        container = tk.Frame(self.main_frame)
        container.pack(expand=True)

        cols = 2 if n > 1 else 1
        rows = (n + cols - 1) // cols

        for i, exp in enumerate(experiments):
            row = i // cols
            col = i % cols
            nn, zh, en, core_path = exp
            text = self._format_label(nn, zh, en)

            btn = tk.Button(container, text=text, font=self.get_font(),
                            command=lambda p=core_path: self.launch_experiment(p))
            btn.grid(row=row, column=col, padx=10, pady=5, sticky='nsew')

        for col in range(cols):
            container.grid_columnconfigure(col, weight=1)
        for row in range(rows):
            container.grid_rowconfigure(row, weight=1)

    def _display_text(self, experiments):
        container = tk.Frame(self.main_frame)
        container.pack(expand=True, fill=tk.BOTH)

        for exp in experiments:
            nn, zh, en, core_path = exp
            text = self._format_label(nn, zh, en)

            lbl = tk.Label(container, text=text, font=self.get_font(),
                           fg='blue', cursor='hand2')
            lbl.pack(pady=2, anchor='center')
            lbl.bind('<Button-1>',
                     lambda e, p=core_path: self.launch_experiment(p))

    # ---------------------------------------------------------------
    # 打开实验页面
    # ---------------------------------------------------------------
    def launch_experiment(self, core_path):
        # ---------- 1. 加载 core 模块 ----------
        try:
            spec = importlib.util.spec_from_file_location("core_module", core_path)
            core_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(core_module)
        except Exception as e:
            messagebox.showerror("错误", f"加载核心模块失败: {e}")
            return

        # ---------- 2. 加载通用页面 ----------
        page_dir = os.path.join(os.path.dirname(__file__), 'ui_pages')
        generic_path = os.path.join(page_dir, '00_通用_generic_page.py')
        if not os.path.exists(generic_path):
            messagebox.showerror("错误", "通用页面模板缺失！")
            return
        try:
            spec_g = importlib.util.spec_from_file_location("generic_page", generic_path)
            generic_module = importlib.util.module_from_spec(spec_g)
            spec_g.loader.exec_module(generic_module)
        except Exception as e:
            messagebox.showerror("错误", f"加载通用页面失败: {e}")
            return

        # ---------- 3. 尝试加载专用页面 ----------
        core_basename = os.path.basename(core_path)
        page_basename = core_basename.replace('_core.py', '_page.py')
        page_path = os.path.join(page_dir, page_basename)

        override_module = None
        if os.path.exists(page_path):
            try:
                spec_p = importlib.util.spec_from_file_location("page_module", page_path)
                override_module = importlib.util.module_from_spec(spec_p)
                spec_p.loader.exec_module(override_module)
            except Exception as e:
                messagebox.showerror("错误", f"加载专用页面失败: {e}")
                return

        # ---------- 4. 初始 settings ----------
        settings = {
            'language': self.lang,
            'precision': self.precision,
            'font_size': self.font_size,
        }

        # ---------- 5. 专用页面若自带 open_page → 完全自定义 ----------
        if override_module is not None and hasattr(override_module, 'open_page'):
            try:
                win = override_module.open_page(self.root, settings, core_module)
                if win:
                    self.child_windows.append(win)
                    win.protocol("WM_DELETE_WINDOW",
                                 lambda w=win: self._on_child_close(w))
                return
            except Exception as e:
                messagebox.showerror("错误", f"打开自定义页面失败: {e}")
                return

        # ---------- 6. 否则走通用界面 ----------
        try:
            win = generic_module.open_page(
                self.root, settings, core_module,
                override_module=override_module
            )
            if win:
                self.child_windows.append(win)
                win.protocol("WM_DELETE_WINDOW",
                             lambda w=win: self._on_child_close(w))
        except Exception as e:
            messagebox.showerror("错误", f"打开实验页面失败: {e}")

    # ---------------------------------------------------------------
    # 子窗口管理
    # ---------------------------------------------------------------
    def _on_child_close(self, win):
        if win in self.child_windows:
            self.child_windows.remove(win)
        win.destroy()

    def on_closing(self):
        for win in self.child_windows[:]:
            try:
                win.destroy()
            except Exception:
                pass
        self.child_windows.clear()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()