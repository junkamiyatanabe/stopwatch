import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import sys
import subprocess

# ログファイルを開く関数
def open_log():
    log_file_name = f'log_{datetime.now().strftime("%Y%m")}.txt'
    try:
        if sys.platform == "win32":
            os.startfile(log_file_name)
        elif sys.platform == "darwin":  # macOS
            subprocess.call(["open", log_file_name])
        else:  # Linux and others
            subprocess.call(["xdg-open", log_file_name])
    except Exception as e:
        print(f"ログファイルを開けませんでした: {e}")

# 作業開始時の処理
def start_work():
    global sttime, no
    sttime = datetime.now()
    status_var.set('作業中')
    no += 1
    with open(f'log_{sttime.strftime("%Y%m")}.txt', 'a') as log_file:
        log_file.write(f'{no},{pj_var.get()},{pj_name_var.get()},{work_var.get()},{sttime.strftime("%Y-%m-%d %H:%M")},')
    update_time()

# 作業終了時の処理
def stop_work():
    global sttime
    etime = datetime.now()
    ttime = (etime - sttime).total_seconds() / 3600
    status_var.set('作業前')
    with open(f'log_{sttime.strftime("%Y%m")}.txt', 'a') as log_file:
        log_file.write(f'{pj_var.get()},{pj_name_var.get()},{work_var.get()},{etime.strftime("%Y-%m-%d %H:%M")},{ttime:.2f}\n')
    timer_label.after_cancel(update_id)

# 経過時間を更新する関数
def update_time():
    global update_id
    if status_var.get() == '作業中':
        elapsed_time = datetime.now() - sttime
        elapsed_hours, remainder = divmod(elapsed_time.seconds, 3600)
        elapsed_minutes, elapsed_seconds = divmod(remainder, 60)
        elapsed_time_str.set(f'{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}')
        update_id = timer_label.after(1000, update_time)

# プロジェクトと作業内容を読み込む関数
def load_options():
    with open('pj.txt', 'r') as pj_file:
        for line in pj_file:
            pjno, pjname = line.strip().split(',')
            pj_options.append((pjno, pjname))
    with open('wk.txt', 'r') as wk_file:
        for line in wk_file:
            work_options.append(line.strip())

app = tk.Tk()
app.title('作業時間記録')

# 変数
pj_var = tk.StringVar()
pj_name_var = tk.StringVar()
work_var = tk.StringVar()
status_var = tk.StringVar(value='作業前')
elapsed_time_str = tk.StringVar(value='00:00:00')
pj_options = []
work_options = []
no = 0
sttime = None
update_id = None

# プロジェクトと作業内容の読み込み
load_options()

# プロジェクト選択
ttk.Label(app, text='プロジェクト:').grid(column=0, row=0)
pj_combo = ttk.Combobox(app, textvariable=pj_var, values=[option[0] for option in pj_options], state='readonly')
pj_combo.grid(column=1, row=0)

# プロジェクト名選択
pj_name_combo = ttk.Combobox(app, textvariable=pj_name_var, values=[option[1] for option in pj_options], state='readonly')
pj_name_combo.grid(column=2, row=0)

# 作業内容選択
ttk.Label(app, text='作業内容:').grid(column=0, row=1)
work_combo = ttk.Combobox(app, textvariable=work_var, values=work_options, state='readonly')
work_combo.grid(column=1, row=1)

# 状態表示
ttk.Label(app, text='状態:').grid(column=0, row=2)
status_label = ttk.Label(app, textvariable=status_var)
status_label.grid(column=1, row=2)

# 経過時間表示
timer_label = ttk.Label(app, textvariable=elapsed_time_str)
timer_label.grid(column=2, row=2)

# ボタン
start_button = ttk.Button(app, text='開始', command=start_work)
start_button.grid(column=0, row=3)
stop_button = ttk.Button(app, text='終了', command=stop_work)
stop_button.grid(column=1, row=3)
log_button = ttk.Button(app, text='ログ', command=open_log)
log_button.grid(column=2, row=3)

app.mainloop()
