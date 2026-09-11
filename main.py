# -*- coding: utf-8 -*-
"""
PhyCalc - 格物算：大学物理实验数据处理工具
主菜单（两级导航：章节 -> 小节）

命名规则：
    core_calculations/n.m_中文名_英文名_core.py
    ui_pages/n.m_中文名_英文名_ui.py

主菜单展示逻辑：
    章节视图：显示所有章节按钮 + 一个“其他实验”按钮（非标准命名文件）
    小节视图：显示某章节下所有小节按钮，顶部有一个 ← 返回 按钮

章节名称来源优先级：
    1. core 文件中 UI_SPEC['chapter_name']（若定义）
    2. main.py 中的 CHAPTER_NAMES 常量
    3. 默认“第 n 章” / “Chapter n”
"""
import os
import sys
import json
import glob
import importlib.util
import tkinter as tk
from tkinter import messagebox, simpledialog

sys.path.insert(0, os.path.dirname(__file__))

APP_VERSION = 'v0.3.1'

# ============================================================================
# 章节名称配置（可选）
#   · key 为章节号；value 为 {'zh': ..., 'en': ...}
#   · 若某个实验的 UI_SPEC 里定义了 'chapter_name'，则优先使用 UI_SPEC 的
#   · 未在此字典中列出的章节，会显示为“第 n 章” / “Chapter n”
# ============================================================================
CHAPTER_NAMES = {
    1: {'zh': '数据处理与不确定度估算',
        'en': 'Data Processing and Uncertainty Estimation'},
    2: {'zh': '基础实验',
        'en': 'Basic Experiments'},
    3: {'zh': '综合实验',
        'en': 'Comprehensive Experiments'},
}

ABOUT_TEXT = {
    'zh': (
        "PhyCalc·格物算\n"
        "格物算：大学物理实验数据处理工具\n\n"
        f"版本：{APP_VERSION}\n\n"
        "作者：星辰蝶语 (Celestiflare Lucifer)\n\n"
        "本工具基于 DeepSeek + Python + Tkinter 制作，\n"
        "使用 PyInstaller 打包分发。\n\n"
        "如有需要，可通过 GitHub 个人页面联系作者，\n"
        "或者发送邮件到：15114671359@nefu.edu.cn\n\n"
        "感谢使用！"
    ),
    'en': (
        "PhyCalc\n"
        "A Data Processing Tool for University Physics Experiments\n\n"
        f"Version: {APP_VERSION}\n\n"
        "Author: Celestiflare Lucifer\n\n"
        "Developed with DeepSeek + Python + Tkinter,\n"
        "distributed using PyInstaller.\n\n"
        "Contact via GitHub profile,\n"
        "or email: 15114671359@nefu.edu.cn\n\n"
        "Thank you for using!"
    )
}

LANG = {
    'zh': {
        'app_title': '格物算：大学物理实验数据处理工具',
        'about': '关于',
        'settings': '设置',
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision': '计算精度（小数位数）',
        'default_size': '默认窗口大小',
        'no_experiments': '未找到实验选项',
        'restart_hint': '更改默认窗口大小需要重启程序生效。',
        'ok': '确定',
        'back': '← 返回',
        'other_experiments': '其他实验',
        'chapter_fmt': '第 {n} 章',
        'chapter_fmt_en': 'Chapter {n}',
    },
    'en': {
        'app_title': 'PhyCalc: Physics Experiment Data Processing Tool',
        'about': 'About',
        'settings': 'Settings',
        'lang_zh': '中文',
        'lang_en': 'English',
        'precision': 'Precision (decimal places)',
        'default_size': 'Default Window Size',
        'no_experiments': 'No experiments found.',
        'restart_hint': 'Changing default window size requires restart.',
        'ok': 'OK',
        'back': '← Back',
        'other_experiments': 'Other Experiments',
        'chapter_fmt': '第 {n} 章',
        'chapter_fmt_en': 'Chapter {n}',
    }
}

DEFAULT_SETTINGS = {
    'language': 'zh',
    'precision': 3,
    'window_width': 600,
    'window_height': 500,
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
        self.font_size = self.settings.get('font_size', 10)
        self.window_width = self.settings.get('window_width', 600)
        self.window_height = self.settings.get('window_height', 500)

        self.child_windows = []

        # 数据缓存
        self._chapter_data = {}       # {chapter_num: {'experiments': [...], 'name': ...}}
        self._non_standard = []       # 非标准命名实验

        # 视图状态：None = 章节列表；数字 = 该章节小节列表；'non_std' = 非标准列表
        self._current_chapter = None

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.title(LANG[self.lang]['app_title'])

        self.create_toolbar()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.scan_experiments()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---------------------------------------------------------------
    # 字体 / 工具栏
    # ---------------------------------------------------------------
    def get_font(self, size=None):
        if size is None:
            size = self.font_size
        family = "Times New Roman" if self.lang == 'en' else "宋体"
        return (family, size)

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

        txt = tk.Text(win, wrap=tk.WORD, font=self.get_font(),
                      padx=15, pady=15, relief=tk.FLAT)
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
        self.settings_menu.add_command(label=LANG[lang]['default_size'],
                                       command=self.set_default_size)

    # ---------------------------------------------------------------
    # 语言 / 精度 / 窗口 / 字号
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

        self.root.title(LANG[lang]['app_title'])
        self.about_btn.config(text=LANG[lang]['about'])
        self.settings_btn.config(text=LANG[lang]['settings'])
        self._build_settings_menu()

        # 重绘当前视图（章节或小节）
        self._render_main()
        save_settings(self.settings)

    def set_precision(self):
        dlg = simpledialog.askinteger("精度设置", "请输入小数位数（整数）：",
                                      initialvalue=self.precision)
        if dlg is not None and dlg >= 0:
            self.precision = dlg
            self.settings['precision'] = dlg
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
        # 重绘当前视图
        self._render_main()

    # ---------------------------------------------------------------
    # 扫描 core_calculations，按章节分组
    # ---------------------------------------------------------------
    @staticmethod
    def _parse_chapter_section(basename):
        """
        解析文件名，返回 (chapter, section) 或 (None, None)。
            1.2_xxx_core.py  → (1, 2)
            01_xxx_core.py   → (1, None)
            其他             → (None, None)
        """
        stem = basename
        if stem.endswith('.py'):
            stem = stem[:-3]
        if stem.endswith('_core'):
            stem = stem[:-5]

        parts = stem.split('_', 1)
        if len(parts) < 2:
            return None, None

        num = parts[0]
        if '.' in num:
            ch_s, sec_s = num.split('.', 1)
            if ch_s.isdigit() and sec_s.isdigit():
                return int(ch_s), int(sec_s)
        elif num.isdigit():
            return int(num), None
        return None, None

    def _load_core_spec(self, core_path):
        try:
            spec = importlib.util.spec_from_file_location(
                f"_scan_{abs(hash(core_path))}", core_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return getattr(mod, 'UI_SPEC', None)
        except Exception as e:
            print(f"[扫描] 无法读取 {core_path}：{e}")
            return None

    def scan_experiments(self):
        core_dir = os.path.join(os.path.dirname(__file__), 'core_calculations')
        chapter_data = {}
        non_std = []

        if os.path.exists(core_dir):
            all_files = glob.glob(os.path.join(core_dir, '*_core.py'))
            # 跳过 00_ 或 0.0_ 模板
            core_files = [f for f in all_files
                          if not os.path.basename(f).startswith(('00_', '0.0_'))]

            for f in core_files:
                basename = os.path.basename(f)
                chapter, section = self._parse_chapter_section(basename)

                spec = self._load_core_spec(f)
                zh_title = en_title = None
                chapter_name = None
                if spec:
                    title = spec.get('title', {})
                    zh_title = title.get('zh')
                    en_title = title.get('en')
                    chapter_name = spec.get('chapter_name')  # 可选
                    # UI_SPEC 里的 chapter / section 优先
                    if spec.get('chapter') is not None:
                        chapter = spec['chapter']
                    if spec.get('section') is not None:
                        section = spec['section']

                if not zh_title:
                    zh_title = basename
                if not en_title:
                    en_title = basename

                exp = {
                    'chapter': chapter,
                    'section': section,
                    'zh': zh_title,
                    'en': en_title,
                    'path': f,
                }

                if chapter is None:
                    non_std.append(exp)
                else:
                    if chapter not in chapter_data:
                        chapter_data[chapter] = {
                            'experiments': [],
                            'name': None,        # UI_SPEC 提供的章节名
                        }
                    chapter_data[chapter]['experiments'].append(exp)
                    # 取第一个非空的 chapter_name
                    if chapter_name and chapter_data[chapter]['name'] is None:
                        chapter_data[chapter]['name'] = chapter_name

        # 每章内按 section 排序
        for ch in chapter_data.values():
            ch['experiments'].sort(key=lambda e: (
                e['section'] is None,
                e['section'] if e['section'] is not None else 0
            ))

        self._chapter_data = chapter_data
        self._non_standard = non_std
        self._current_chapter = None
        self._render_main()

    # ---------------------------------------------------------------
    # 视图渲染总入口
    # ---------------------------------------------------------------
    def _render_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

        if self._current_chapter is None:
            self._render_chapters()
        elif self._current_chapter == 'non_std':
            self._render_non_std()
        else:
            self._render_sections(self._current_chapter)

    # ---------------------------------------------------------------
    # 章节视图
    # ---------------------------------------------------------------
    def _render_chapters(self):
        # 外层：让按钮组整体居中
        outer = tk.Frame(self.main_frame)
        outer.pack(expand=True)

        inner = tk.Frame(outer)
        inner.pack()

        if not self._chapter_data and not self._non_standard:
            tk.Label(inner, text=LANG[self.lang]['no_experiments'],
                     font=self.get_font()).pack(pady=20)
            return

        for chapter_num in sorted(self._chapter_data.keys()):
            ch = self._chapter_data[chapter_num]
            text = self._format_chapter_label(chapter_num, ch.get('name'))
            btn = tk.Button(inner, text=text, font=self.get_font(),
                            width=30,
                            command=lambda c=chapter_num: self._enter_chapter(c))
            btn.pack(pady=6, ipady=6)

        # 非标准实验入口
        if self._non_standard:
            btn = tk.Button(inner,
                            text=LANG[self.lang]['other_experiments'],
                            font=self.get_font(),
                            width=30,
                            command=self._enter_non_std)
            btn.pack(pady=6, ipady=6)

    def _format_chapter_label(self, chapter_num, chapter_name):
        """章节按钮显示文字。"""
        if self.lang == 'zh':
            base = LANG['zh']['chapter_fmt'].format(n=chapter_num)
            name = None
            if chapter_name and chapter_name.get('zh'):
                name = chapter_name['zh']
            elif chapter_num in CHAPTER_NAMES:
                name = CHAPTER_NAMES[chapter_num].get('zh')
            return f"{base} {name}" if name else base
        else:
            base = LANG['en']['chapter_fmt_en'].format(n=chapter_num)
            name = None
            if chapter_name and chapter_name.get('en'):
                name = chapter_name['en']
            elif chapter_num in CHAPTER_NAMES:
                name = CHAPTER_NAMES[chapter_num].get('en')
            return f"{base} {name}" if name else base

    # ---------------------------------------------------------------
    # 小节视图
    # ---------------------------------------------------------------
    def _render_sections(self, chapter_num):
        outer = tk.Frame(self.main_frame)
        outer.pack(expand=True)

        inner = tk.Frame(outer)
        inner.pack()

        ch = self._chapter_data.get(chapter_num)
        if not ch:
            return

        # 返回按钮
        back_btn = tk.Button(inner, text=LANG[self.lang]['back'],
                             font=self.get_font(),
                             width=30,
                             command=self._back_to_chapters)
        back_btn.pack(pady=(0, 14), ipady=6)

        # 小节按钮
        for exp in ch['experiments']:
            text = self._format_section_label(exp)
            btn = tk.Button(inner, text=text, font=self.get_font(),
                            width=30,
                            command=lambda p=exp['path']: self.launch_experiment(p))
            btn.pack(pady=6, ipady=6)

    def _format_section_label(self, exp):
        """小节按钮显示文字，如“1.2 不确定度估算与测量结果表示”。"""
        title = exp['zh'] if self.lang == 'zh' else exp['en']
        ch = exp['chapter']
        sec = exp['section']
        if sec is not None and sec > 0:
            return f"{ch}.{sec} {title}"
        return f"{ch} {title}"

    # ---------------------------------------------------------------
    # 非标准实验视图
    # ---------------------------------------------------------------
    def _render_non_std(self):
        outer = tk.Frame(self.main_frame)
        outer.pack(expand=True)

        inner = tk.Frame(outer)
        inner.pack()

        # 返回按钮
        back_btn = tk.Button(inner, text=LANG[self.lang]['back'],
                             font=self.get_font(),
                             width=30,
                             command=self._back_to_chapters)
        back_btn.pack(pady=(0, 14), ipady=6)

        # 非标准实验按钮
        for exp in self._non_standard:
            text = exp['zh'] if self.lang == 'zh' else exp['en']
            btn = tk.Button(inner, text=text, font=self.get_font(),
                            width=30,
                            command=lambda p=exp['path']: self.launch_experiment(p))
            btn.pack(pady=6, ipady=6)

    # ---------------------------------------------------------------
    # 视图切换
    # ---------------------------------------------------------------
    def _enter_chapter(self, chapter_num):
        self._current_chapter = chapter_num
        self._render_main()

    def _enter_non_std(self):
        self._current_chapter = 'non_std'
        self._render_main()

    def _back_to_chapters(self):
        self._current_chapter = None
        self._render_main()

    # ---------------------------------------------------------------
    # 打开实验（与之前逻辑一致）
    # ---------------------------------------------------------------
    def launch_experiment(self, core_path):
        # 1. 加载 core
        try:
            spec = importlib.util.spec_from_file_location("core_module", core_path)
            core_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(core_module)
        except Exception as e:
            messagebox.showerror("错误", f"加载核心模块失败: {e}")
            return

        # 2. 加载通用 UI
        page_dir = os.path.join(os.path.dirname(__file__), 'ui_pages')
        generic_path = os.path.join(page_dir, '0.0_通用_generic_ui.py')
        if not os.path.exists(generic_path):
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

        # 3. 尝试加载专用 UI
        core_basename = os.path.basename(core_path)
        page_basename = core_basename.replace('_core.py', '_ui.py')
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

        settings = {
            'language': self.lang,
            'precision': self.precision,
            'font_size': self.font_size,
        }

        # 4. 专用 UI 自带 open_page → 完全自定义
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

        # 5. 否则走通用 UI
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
