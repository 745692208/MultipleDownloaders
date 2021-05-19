import os
import sys
import time
from threading import Timer
from concurrent import futures
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog

import pyperclip  # pip install pyperclip
import config
import core


class App:
    class RepeatingTimer(Timer):
        def run(self):
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    def set_perclip_text(self):
        text = '剪切板：{}'.format(pyperclip.paste()[0:75])
        self.perclip_text.set(text.replace('\n', '').replace('\r', ''))

    def open_folder(self):
        try:
            os.startfile(self.entry_path.get())
        except Exception:
            messagebox.showerror("错误", "请输入正确的文件夹路径！")

    def open_latest_folder(self):
        path = self.cf.load('base', 'save_path')
        if path != '':
            try:
                os.startfile(path)
            except Exception:
                messagebox.showerror("错误", "往期路径不存在！")
        else:
            messagebox.showinfo('无最新保存', '没有保存过作品！')

    def browse(self):
        print('browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            self.cf.save('base', 'path', dir)
            self.save_path = dir
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, self.save_path)

    def run(self, code):
        core.entry_path = self.entry_path.get()
        core.b_is_create_folder = self.ckbtn_create_folder_var.get()
        core.b_is_custom_name = self.ckbtn_custom_name_var.get()
        self.cf.save('base', 'path', self.entry_path.get())
        url = pyperclip.paste()
        if code == 'core_zb.get_work':
            self.core_zb.b_is_down_video = self.zb_is_down_video.get()
            self.core_zb.get_work(url)
        if code == 'core_art.get_work':
            self.core_art.get_work(url)
        if code == 'core_art.get_user_works':
            self.core_art.b_is_down_video = self.ckbtn_down_video_var.get()
            self.core_art.get_user_works(url)

    def changeTab(self, index):
        self.cf.save('base', 'tab_index', str(index))
        self.fLogs.pack_forget()
        for ftab in self.ftab_list:
            ftab.pack_forget()
        self.ftab_list[index].pack(fill='x')
        self.fLogs.pack(side='top', fill='both', expand=1)

    def create_widget(self):
        # 1 第一行 标签容器 创建标签
        fTab = tk.Frame(self.app)
        fTab.pack(side='top', fill='x')
        ttk.Radiobutton(
            fTab, text="ArtStation", value=0,
            variable=self.tab_index, command=lambda: self.changeTab(0))\
            .pack(side='left')
        ttk.Radiobutton(
            fTab, text="ZBrushCentral", value=1,
            variable=self.tab_index, command=lambda: self.changeTab(1))\
            .pack(side='left')

        # 2 第二行 save
        fSave = tk.Frame(self.app)
        fSave.pack(side='top', fill='x')
        ttk.Label(fSave, text='Save Path').pack(side='left')
        self.entry_path = ttk.Entry(fSave)
        self.entry_path.pack(side='left', fill='x', expand=True)
        self.entry_path.insert(0, self.save_path)

        ttk.Button(fSave, text='浏览', command=self.browse).pack(side='left')
        ttk.Button(fSave, text='打开文件夹', command=self.open_folder)\
            .pack(side='left')
        ttk.Button(
            fSave, text='打开最近保存文件夹',
            command=self.open_latest_folder)\
            .pack(side='left')

        fSave_2 = tk.Frame(self.app)
        fSave_2.pack(side='top', fill='x')

        self.ckbtn_custom_name_var = tk.IntVar()
        self.ckbtn_custom_name_var.set(
            self.cf.load('art', 'ckbtn_custom_name', 1))
        self.ckbtn_custom_name = ttk.Checkbutton(
            fSave_2,
            text='自定义命名',
            variable=self.ckbtn_custom_name_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_custom_name',
                str(self.ckbtn_custom_name_var.get())
            )
        )
        self.ckbtn_custom_name.pack(side='left')
        self.ckbtn_create_folder_var = tk.IntVar()
        self.ckbtn_create_folder_var.set(
            self.cf.load('art', 'ckbtn_create_folder', 1))
        self.ckbtn_create_folder = ttk.Checkbutton(
            fSave_2,
            text='创建文件夹',
            variable=self.ckbtn_create_folder_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_create_folder',
                str(self.ckbtn_create_folder_var.get())
            )
        )
        self.ckbtn_create_folder.pack(side='left')
        # 3 第三行
        # ArtStation页面
        self.fTool_art = ttk.LabelFrame(self.app, text='ArtStation')
        self.fTool_art.pack(side='top', fill='x')
        self.ftab_list.append(self.fTool_art)

        self.ckbtn_down_video_var = tk.IntVar()
        self.ckbtn_down_video_var.set(self.cf.load(
            'art', 'ckbtn_down_video', 1))
        ttk.Checkbutton(
            self.fTool_art,
            text='下载视频',
            variable=self.ckbtn_down_video_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_down_video',
                str(self.ckbtn_down_video_var.get())
            )
        ).pack(side='left')

        ttk.Button(
            self.fTool_art, text='爬取单个作品',
            command=lambda: self.executor_ui.submit(
                self.run, 'core_art.get_work')
        ).pack(side='left')
        ttk.Button(
            self.fTool_art, text='爬取用户',
            command=lambda: self.executor_ui.submit(
                self.run, 'core_art.get_user_works')
        ).pack(side='left')

        # ZBrushCentral界面
        self.fTool_zb = ttk.LabelFrame(self.app, text='ZBrushCentral')
        self.fTool_zb.pack(side='top', fill='both')
        self.ftab_list.append(self.fTool_zb)

        self.zb_is_down_video = tk.IntVar()
        self.zb_is_down_video.set(self.cf.load(
            'zb', 'zb_is_down_video', 1))
        ttk.Checkbutton(
            self.fTool_zb,
            text='下载视频',
            variable=self.zb_is_down_video,
            command=lambda: self.cf.save(
                'zb', 'zb_is_down_video',
                str(self.zb_is_down_video.get())
            )
        ).pack(side='left')
        ttk.Button(
            self.fTool_zb, text='爬取单个作品',
            command=lambda: self.executor_ui.submit(
                self.run, 'core_zb.get_work')
        ).pack(side='left')
        # 4 第四行 Logs界面
        self.fLogs = ttk.LabelFrame(self.app, text='Logs')
        self.fLogs.pack()

        self.perclip_text = tk.StringVar()
        ttk.Label(self.fLogs, anchor='w', textvariable=self.perclip_text)\
            .pack(side='top', fill='x')
        fLogs_box = ttk.Frame(self.fLogs)
        fLogs_box.pack(side='left', fill='both', expand=1)
        self.logs_box = tk.Text(fLogs_box)
        self.logs_box.pack(side='left', fill='both', expand=1)
        self.logs_box.configure(state="disabled")
        self.logs_box.focus()
        # Logs界面 滚动条
        self.scrollbar = ttk.Scrollbar(fLogs_box)
        self.scrollbar.pack(side='left', fill='y')
        self.scrollbar.config(command=self.logs_box.yview)
        self.logs_box.config(yscrollcommand=self.scrollbar.set)

    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = '[{}]{}'.format(time_date, value)
        self.logs_box.configure(state="normal")
        self.logs_box.insert('end', value + '\n')
        self.logs_box.see('end')
        self.logs_box.configure(state="disabled")

    def __init__(self, title, ver, suffix):
        self.cf = config.Config('ArtDown', 1, './test/')
        core.cf = self.cf
        core.Utils(self.app_log)
        self.core_zb = core.ZBrush()
        self.core_art = core.ArtStation()
        self.core_utils = core.Utils()
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.app = tk.Tk()
        self.app.title('{} {} {}'.format(title, ver, suffix))
        # 变量
        self.ftab_list = []
        self.save_path = self.cf.load('base', 'path')
        self.tab_index = tk.IntVar()
        self.tab_index.set(self.cf.load('base', 'tab_index', 0))
        # 运行
        self.create_widget()
        self.changeTab(self.tab_index.get())
        self.t = self.RepeatingTimer(1, self.set_perclip_text)
        self.t.start()


if __name__ == '__main__':
    app = App('GUI Test', '2.0.0', '')
    app.app.mainloop()
    app.t.cancel()
    sys.exit()
