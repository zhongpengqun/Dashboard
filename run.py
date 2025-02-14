import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
from sample import 托盘, PH集
from 天平 import 读取天平数据
from ph import read_ph
from utils import dprint
import winsound
import time
import datetime

from settings import VERSION, 中联品牌色_绿, 中联品牌色_深绿, 中联品牌色_浅绿, 中联品牌色_暗绿, 中联品牌色_草绿, 读取设备数据时间间隔

# 表格单元格宽度
CELL_WIDTH = 140

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.window_height = 800
        # self.window_height = 350
        self.window_width = self.root.winfo_screenwidth() - 100

        self.Label_有机质称重 = None
        self.Label_PH值测量 = None

        self.Radiobuttons_tab = []
        self.Radiobuttons_区 = []
        self.Radiobuttons_重 = []
        self.Radiobuttons_ph = []

        self.当前托盘 = None
        self.读取数据开关 = False
        self.读取PH设备开关 = False

        self.selected_tab = tk.StringVar()
        self.selected_tab.set("有机质称重")

        self.selected_area = tk.StringVar()
        self.selected_area.set("1区")

        self.selected_重 = tk.StringVar()
        self.selected_重.set("坩埚净重")

        self.selected_ph_type = tk.StringVar()
        self.selected_ph_type.set("PH")

        self.ph集 = PH集(self.selected_ph_type.get())
        self.ph集.treeview = ttk.Treeview(self.root, height= len((self.ph集.shape)) + 1)
        self.ph集.verscrlbar = ttk.Scrollbar(self.root, orient ="vertical", command = self.ph集.treeview.yview)
        self.ph集.verscrlbar.pack(side ='right', fill ='x')
        # self.ph集.verscrlbar.config(command=self.ph集.treeview.yview)
        # self.ph集.treeview.configure(yscrollcommand = self.ph集.verscrlbar.set)
        # self.ph集.treeview.pack(pady=100)

        self.message_label = tk.Label(self.root, text="", fg=中联品牌色_暗绿, bg=中联品牌色_绿)
        self.control_label = tk.Label(self.root, text="点击开始读取数据", fg=中联品牌色_暗绿, bg=中联品牌色_深绿)
        self.export_label = tk.Label(self.root, text="导出数据", fg=中联品牌色_暗绿, bg=中联品牌色_深绿)

        self.init_window()
        self.init_style()
        self.init_components()
        # self.init_layout()

        self.refresh_ph集_treeview()

    def refresh_ph集_treeview(self):
        self.ph集.treeview = ttk.Treeview(self.root, height= min(len((self.ph集.shape)) + 1, 15), selectmode="extended")
        self.ph集.treeview.pack(pady=100)
        if hasattr(self.ph集, 'verscrlbar') and self.ph集.verscrlbar:
            self.ph集.verscrlbar.config(command=self.ph集.treeview.yview)
            self.ph集.treeview.configure(yscrollcommand = self.ph集.verscrlbar.set)

    def init_window(self):
        self.root.configure(bg=中联品牌色_绿)
        self.root.title(f"实验室小助手 V{VERSION}")
        self.root.resizable(False, False)  # This code helps to disable windows from resizing
        # self.root.resizable(False, True)  # This code helps to disable windows from resizing

        x_cordinate = int((self.root.winfo_screenwidth()/2) - (self.window_width/2))
        y_cordinate = int((self.root.winfo_screenheight()/2) - (self.window_height/2)) - 100

        self.root.geometry("{}x{}+{}+{}".format(self.window_width, self.window_height, x_cordinate, y_cordinate))

        ###
        self.export_label.place(relx=0.8, rely=.8, anchor='center')
        self.export_label.bind("<Button-1>", lambda e: self.export())
        self.export_label.config(font=("", 15))

        ###
        w = tk.Label(self.root, text="© 中联智慧农业", fg=中联品牌色_暗绿, bg=中联品牌色_绿)
        w.place(relx=.5, rely=.94, anchor="center")

    def init_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background=中联品牌色_深绿, foreground=中联品牌色_暗绿)
        style.configure("Treeview",
                        background=中联品牌色_浅绿,
                        foreground=中联品牌色_暗绿,
                        rowheight=35,
                        rowwidth=10,
                        fieldbackground=中联品牌色_浅绿,
                        )
        style.configure('IndicatorOff.TRadiobutton',
                        indicatorrelief=tk.SUNKEN,
                        indicatormargin=10,
                        indicatordiameter=6,
                        relief=tk.SUNKEN,
                        # focusthickness=2,
                        # highlightthickness=2,
                        padding=2,
                        font=("", 9),
                        background=中联品牌色_绿
        )
        style.configure('X.TRadiobutton',
                        indicatorrelief=tk.SUNKEN,
                        indicatormargin=-1,
                        indicatordiameter=-1,
                        relief=tk.SUNKEN,
                        # focusthickness=2,
                        # highlightthickness=2,
                        padding=2,
                        font=("", 15),
                        background=中联品牌色_深绿
        )
        style.map("Treeview",
                    background=[('selected', 中联品牌色_深绿)])
        style.map("IndicatorOff.TRadiobutton",
            background=[('selected', 中联品牌色_浅绿), ('active', 中联品牌色_浅绿)]
        )
        style.map("X.TRadiobutton",
            background=[('selected', 中联品牌色_浅绿), ('active', 中联品牌色_浅绿)]
        )

    def 点击读取数据开关(self):
        self.读取数据开关 = {True: False, False: True}.get(self.读取数据开关)
        self.control_label.config(text={True: f'正在读取数据..(点击暂停)', False: '已暂停读取数据'}.get(self.读取数据开关))

    def show_区_重_tabs(self):
        for _index, rb in enumerate(self.Radiobuttons_区):
            rb.place(relx=0.05 * (_index + 1), rely=.06, anchor='center')

        for _index, rb in enumerate(self.Radiobuttons_重):
            rb.place(relx=0.05*5 + 0.05 * (_index + 1), rely=.06, anchor='center')

    def hide_区_重_tabs(self):
        for rb in self.Radiobuttons_区:
            rb.place_forget()

        for rb in self.Radiobuttons_重:
            rb.place_forget()

    def show_Radiobuttons_ph(self):
        for _index, rb in enumerate(self.Radiobuttons_ph):
            rb.place(relx=0.05 * (_index + 1), rely=.06, anchor='center')

    def hide_Radiobuttons_ph(self):
        for rb in self.Radiobuttons_ph:
            rb.place_forget()

    def init_components(self):
        ###
        for _index, (text, mode) in enumerate([
            ("有机质称重", "有机质称重"),
            ("PH值测量", "PH值测量")
        ]):
            ttk.Radiobutton(self.root, text=text, value=mode, width=25, variable=self.selected_tab, style='X.TRadiobutton', takefocus=False).place(relx= 0.082 + 0.1 * _index, rely=.02, anchor='center')

        ###
        for _index, (text, mode) in enumerate([
            ("1区", "1区"),
            ("2区", "2区"),
            ("3区", "3区"),
            ("4区", "4区"),
        ]):
            rb = ttk.Radiobutton(self.root, text=text, value=mode, width=15, variable=self.selected_area, name=f"{_index + 1}区",
                            style='IndicatorOff.TRadiobutton', takefocus=False)
            # rb.place(relx=0.05 * (_index + 1), rely=.06, anchor='center')
            self.Radiobuttons_区.append(rb)

        ###
        for _index, (text, mode) in enumerate([
            ("坩埚净重", "坩埚净重"),
            ("第1次测重", "第1次测重"),
            ("第2次测重", "第2次测重"),
            # ("测重结果", "测重结果"),
        ]):
            rb = ttk.Radiobutton(self.root, text=text, value=mode, width=15, variable=self.selected_重,
                            style='IndicatorOff.TRadiobutton', takefocus=False)
            # rb.place(relx=0.05*5 + 0.05 * (_index + 1), rely=.06, anchor='center')
            self.Radiobuttons_重.append(rb)

        ###
        for _index, (text, mode) in enumerate([
            ("PH", "PH"),
            ("Buffer PH", "Buffer_PH"),
        ]):
            rb = ttk.Radiobutton(self.root, text=text, value=mode, width=15, variable=self.selected_ph_type,
                            style='IndicatorOff.TRadiobutton', takefocus=False)
            # rb.place(relx=0.05*5 + 0.05 * (_index + 1), rely=.06, anchor='center')
            self.Radiobuttons_ph.append(rb)

    def refresh_ui(self):
        # 先清除全部
        for ins in 托盘.instances:
            if ins.treeview:
                # hidden treeview
                ins.treeview.pack_forget()
        for ins in PH集.instances:
            if ins.treeview:
                ins.treeview.pack_forget()

        if self.selected_tab.get() == "有机质称重":
            ###
            self.message_label.place(relx=0.5, rely=.8, anchor='center')
            self.message_label.config(font=("", 25))

            ###
            self.control_label.place(relx=0.5, rely=.7, anchor='center')
            self.control_label.bind("<Button-1>", lambda e: self.点击读取数据开关())
            self.control_label.config(font=("", 25))

            ###
            self.hide_Radiobuttons_ph()
            self.show_区_重_tabs()

            ###
            tv = ttk.Treeview(self.root, height= len((self.当前托盘.shape)) + 1)
            self.当前托盘.treeview = tv

            dprint('-------self.当前托盘-------')
            dprint(self.当前托盘.df)

            tv.pack(pady=100)
            tv["columns"] = list(self.当前托盘.df.columns)
            for i in tv["columns"]:
                tv.column(i, anchor="w", width=int(self.window_width / int(len(self.当前托盘.columns) + 1)) - 5)
                tv.heading(i, text=f'{i}', anchor='w')

            for index, row in self.当前托盘.df.iterrows():
                tv.insert("", "end", iid=f'iid-{index}', text=index, values=[_ if _ is not None else '-' for _ in list(row)])

        elif self.selected_tab.get() == "PH值测量":
            self.message_label.place_forget()
            self.control_label.place_forget()

            self.hide_区_重_tabs()
            self.show_Radiobuttons_ph()

            self.refresh_ph集_treeview()

            self.ph集.treeview["columns"] = list(self.ph集.df.columns)
            for i in self.ph集.treeview["columns"]:
                self.ph集.treeview.column(i, anchor="w", width=int(self.window_width / (len(self.ph集.columns) + 1)) - 5)
                self.ph集.treeview.heading(i, text=f'{i}', anchor='w')

            for index, row in self.ph集.df.iterrows():
                self.ph集.treeview.insert("", "end", text=index, values=[_ if _ is not None else '-' for _ in list(row)])

        # if self.selected_重.get() == '测重结果':
        #     self.control_label.place_forget()
            # TODO
            # 完成, msg = 托盘.三次测重已完成(self.selected_area.get())
            # if not 完成:
            #     self.update_message_label(f"无法显示测重结果, 因为{msg}！")

        #####
        if hasattr(self, 'export_label_msg_duration'):
            self.export_label_msg_duration -= 1
            if self.export_label_msg_duration <= 0:
                self.export_label.config(text="导出数据")
                self.export_label_msg_duration = 99999

    def update_message_label(self, message):
        self.message_label.config(text=message)

    def update_export_label(self, message, 留存时间秒):
        self.export_label_msg_duration = 留存时间秒
        self.export_label.config(text=message)

    def export(self):
        if self.selected_tab == "有机质称重":
            # directory = os.getcwd()
            # filepath = os.path.join(directory, f"{self.当前托盘.selected_area}_有机质含量检测_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.xlsx")
            # df = pd.DataFrame([[x, y] for x, y in zip(list(range(1, len(self.当前托盘.as_list()) + 1)), self.当前托盘.as_list())], columns=['序号', '样品中有机物含量'])
            # df.to_excel(filepath, index=False)
            # self.update_export_label(f"保存在{filepath}", 10)
            # TODO
            pass

        elif self.selected_tab == "PH值测量":
            # directory = os.getcwd()
            # filepath = os.path.join(directory, f"{self.当前托盘.selected_area}_PH检测_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.xlsx")
            # ##
            # df = pd.DataFrame([[x, y] for x, y in zip(list(range(1, len(self.当前托盘.as_list()) + 1)), self.当前托盘.as_list())], columns=['序号', '样品中有机物含量'])
            # df.to_excel(filepath, index=False)
            # self.update_export_label(f"保存在{filepath}", 10)
            # TODO
            pass

    def refresh(self):
        dprint(time.time())
        if self.selected_tab.get() == '有机质称重':
            self.当前托盘 = 托盘.get_or_create_instance(self.selected_area.get(), self.selected_重.get())

            if self.selected_重.get() == '测重结果':
                # TODO
                pass
                # success = 托盘.得出测重结果(self.selected_area.get())
            else:
                self.update_message_label("")
                if self.读取数据开关:
                    self.样本称重()

        elif self.selected_tab.get() == 'PH值测量':
            self.ph集 = PH集.get_or_create_instance(self.selected_ph_type.get())
            self.读取ph设备()

            # todo
            # if self.selected_ph_type == 

        self.refresh_ui()
        time.sleep(0.5)

    def listen(self):
        self.refresh()
        self.root.after(读取设备数据时间间隔, self.listen)

    def 样本称重(self):
        if self.当前托盘.当前正在检测的坩埚的顺序 >= self.当前托盘.所有坩埚个数:
            self.update_message_label('样品已全部测量完毕！')
            return

        index, column = self.当前托盘.当前正在检测的坩埚所在位置的index和column
        是新样品, 新样品重量, 本次读取到的重量_str = 读取天平数据()

        if 是新样品:
            self.当前托盘.更新测量结果(self.当前托盘.当前正在检测的坩埚的顺序, str(新样品重量))
            winsound.Beep(1500, 500)
            self.update_message_label(str(新样品重量))
        else:
            # 等待读取的闪烁效果
            # self.当前托盘.treeview.set(f'iid-{index}', column, '.' * int(time.time() % 3))
            self.update_message_label('')

    def 读取ph设备(self):
        ph值s = read_ph()

        for ph值 in ph值s:
            self.ph集.添加一个ph检测结果(ph值)

application = Application()

application.listen()
application.root.mainloop()
