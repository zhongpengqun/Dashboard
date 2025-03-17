import collections
import tkinter as tk
from functools import partial
from tkinter import messagebox  # Button经常会和messagebox控件一起使用


button_groups = collections.OrderedDict()

SELECTED_GROUP_NAME = ''

# Count of buttons of a row
COLUMNS = 5
WINDOW_WIDTH = 590
WINDOW_HEIGHT = 800
# Unit is a charactor
BUTTON_WIDTH = 12

LEFT_FRAME_WIDTH = 100
RIGHT_FRAME_WIDTH = WINDOW_WIDTH - LEFT_FRAME_WIDTH


root = tk.Tk()
# 第1个加数是距离屏幕左边的宽，第2个加数是距离屏幕顶部的高
root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+10+10')
root.title('Hello')

left_Frame = tk.Frame(root
                   , width=LEFT_FRAME_WIDTH
                   , height=WINDOW_HEIGHT
                   , highlightbackground="black"
                   , highlightthickness=1
                   , bd=3)
right_Frame = tk.Frame(root
                  , width=RIGHT_FRAME_WIDTH
                  , height=WINDOW_HEIGHT
                  , highlightbackground="black"
                  , highlightthickness=1
                  , bd=3)

left_Frame.grid(row=0, column=0, padx=5, pady=5)
right_Frame.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=tk.N)

def register(button_object, group_name):
    global button_groups
    button_groups.setdefault(group_name, [])
    button_groups[group_name].append(button_object)

def select_group(group_name):
    global SELECTED_GROUP_NAME
    SELECTED_GROUP_NAME = group_name

    refresh()

def alert():  # 定义事件函数
    messagebox.showinfo(title='hello', message='Hello world') #弹出消息框，标题为hello，消息为Hello world


def refresh():
    # Firstly, clear all buttons in frames
    for widget in left_Frame.winfo_children():
        widget.pack_forget()
    for widget in right_Frame.winfo_children():
        widget.grid_forget()

    for group_name in button_groups.keys():
        _btn = tk.Button(left_Frame, text=group_name, command=partial(select_group, group_name), width=BUTTON_WIDTH, bg='blue' if group_name == SELECTED_GROUP_NAME else 'white')
        _btn.pack()

    buttons = button_groups[SELECTED_GROUP_NAME]

    print(f'---SELECTED_GROUP_NAME---------{SELECTED_GROUP_NAME}')
    print(f'---buttons-------{buttons}')

    rows_count = int((len(buttons) / COLUMNS)) + 1 if int(len(buttons) % COLUMNS) !=0 else int((len(buttons) / COLUMNS))

    print(f'---------rows_count:{rows_count}')

    for row_index in range(rows_count):
        for column_index in range(COLUMNS):
            try:
                button_obj = buttons[row_index*COLUMNS + column_index]
            except IndexError:
                button_obj = tk.Button(right_Frame, text='', width=BUTTON_WIDTH)

            button_obj.grid(row=row_index, column=column_index)

btn = tk.Button(right_Frame, text='点我', command=alert, width=BUTTON_WIDTH)
register(btn, 'Python')

btn = tk.Button(right_Frame, text='点我1', command=alert, width=BUTTON_WIDTH)
register(btn, 'Python')

btn = tk.Button(right_Frame, text='点我', command=alert, width=BUTTON_WIDTH)
register(btn, 'Python')

btn = tk.Button(right_Frame, text='点我', command=alert, width=BUTTON_WIDTH)
register(btn, 'Python')

btn = tk.Button(right_Frame, text='点我5', command=alert, width=BUTTON_WIDTH)
register(btn, 'Python')

#
btn = tk.Button(right_Frame, text='点我', command=alert, width=BUTTON_WIDTH)
register(btn, 'Linux')

btn = tk.Button(right_Frame, text='点我5', command=alert, width=BUTTON_WIDTH)
register(btn, 'Linux')
#
SELECTED_GROUP_NAME = list(button_groups.keys())[0]
refresh()


tk.mainloop()
