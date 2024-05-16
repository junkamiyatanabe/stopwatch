import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import datetime

# グローバル変数の初期化
start_time = None
end_time = None
log_file_path = "log_" + datetime.datetime.now().strftime("%Y%m") + ".txt"
pj_file_path = os.path.join(os.getcwd(), "pj.txt")
wk_file_path = os.path.join(os.getcwd(), "wk.txt")

# GUI設定
root = tk.Tk()
root.title("作業時間記録アプリ")

# プロジェクト情報と作業内容の読み込み
def load_projects(file_path):
    projects = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                pjno, pjname = line.strip().split(',')
                projects[pjno] = pjname
    except Exception as e:
        messagebox.showerror("Error", f"Error loading projects: {e}")
    return projects

def load_work(file_path):
    work_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            work_list = [line.strip() for line in file]
    except Exception as e:
        messagebox.showerror("Error", f"Error loading work items: {e}")
    return work_list

projects = load_projects(pj_file_path)
work_list = load_work(wk_file_path)

selected_pjno = tk.StringVar()
selected_work = tk.StringVar()
status_text = tk.StringVar(value="作業前")
elapsed_time_text = tk.StringVar(value="00:00:00")

# プロジェクト選択用のプルダウンメニュー
pj_combobox = ttk.Combobox(root, textvariable=selected_pjno, values=list(projects.keys()), state="readonly")
pj_combobox.grid(row=0, column=1)
ttk.Label(root, text="プロジェクト番号").grid(row=0, column=0)

# プロジェクト名表示ラベル
pj_name_label = ttk.Label(root, text="")
pj_name_label.grid(row=0, column=2)

# 作業内容選択用のプルダウンメニュー
work_combobox = ttk.Combobox(root, textvariable=selected_work, values=work_list, state="readonly")
work_combobox.grid(row=1, column=1)
ttk.Label(root, text="作業内容").grid(row=1, column=0)

# 状態表示ラベル
status_label = ttk.Label(root, textvariable=status_text)
status_label.grid(row=2, column=1)

# 経過時間表示ラベル
elapsed_time_label = ttk.Label(root, textvariable=elapsed_time_text)
elapsed_time_label.grid(row=2, column=2)

# ボタンのコールバック関数
def start_work():
    global start_time
    if selected_pjno.get() and selected_work.get():
        start_time = time.time()
        status_text.set("作業中")
        pj_combobox.config(state="disabled")
        work_combobox.config(state="disabled")
        start_button.config(state="disabled")
        stop_button.config(state="normal")
        update_elapsed_time()
        log_start()
    else:
        messagebox.showwarning("Warning", "プロジェクトと作業内容を選択してください。")

def stop_work():
    global end_time
    end_time = time.time()
    status_text.set("作業前")
    elapsed_time_text.set("00:00:00")
    pj_combobox.config(state="readonly")
    work_combobox.config(state="readonly")
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    log_end()

def update_elapsed_time():
    if status_text.get() == "作業中":
        elapsed = time.time() - start_time
        elapsed_time_text.set(time.strftime("%H:%M:%S", time.gmtime(elapsed)))
        root.after(1000, update_elapsed_time)

def open_log():
    if os.name == 'nt':
        os.startfile(log_file_path)
    elif os.name == 'posix':
        os.system(f'xdg-open "{log_file_path}"')
    else:
        messagebox.showerror("Error", "Unsupported OS")

# ログ記録の関数
def log_start():
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as log_file:
            log_file.write("no,pjno,pjname,work,stime\n")
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{time.time()},{selected_pjno.get()},{projects[selected_pjno.get()]},{selected_work.get()},{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_end():
    total_time = (end_time - start_time) / 3600
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{time.time()},{selected_pjno.get()},{projects[selected_pjno.get()]},{selected_work.get()},{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{total_time}\n")

# GUIのボタン
start_button = ttk.Button(root, text="開始", command=start_work)
start_button.grid(row=3, column=0)

stop_button = ttk.Button(root, text="終了", command=stop_work, state="disabled")
stop_button.grid(row=3, column=1)

log_button = ttk.Button(root, text="ログを開く", command=open_log)
log_button.grid(row=3, column=2)

# ファイル選択ボタン
def select_pj_file():
    global pj_file_path
    pj_file_path = filedialog.askopenfilename()
    pj_path_label.config(text=pj_file_path)
    projects.update(load_projects(pj_file_path))
    pj_combobox.config(values=list(projects.keys()))

def select_wk_file():
    global wk_file_path
    wk_file_path = filedialog.askopenfilename()
    wk_path_label.config(text=wk_file_path)
    work_list.extend(load_work(wk_file_path))
    work_combobox.config(values=work_list)

def select_log_file():
    global log_file_path
    log_file_path = filedialog.askopenfilename()
    log_path_label.config(text=log_file_path)

pj_path_button = ttk.Button(root, text="プロジェクトファイル選択", command=select_pj_file)
pj_path_button.grid(row=4, column=0)

wk_path_button = ttk.Button(root, text="作業内容ファイル選択", command=select_wk_file)
wk_path_button.grid(row=4, column=1)

log_path_button = ttk.Button(root, text="ログファイル選択", command=select_log_file)
log_path_button.grid(row=4, column=2)

# ファイルパス表示ラベル
pj_path_label = ttk.Label(root, text=pj_file_path)
pj_path_label.grid(row=5, column=0, columnspan=3)

wk_path_label = ttk.Label(root, text=wk_file_path)
wk_path_label.grid(row=6, column=0, columnspan=3)

log_path_label = ttk.Label(root, text=log_file_path)
log_path_label.grid(row=7, column=0, columnspan=3)

# プロジェクト名の表示を更新する関数
def update_project_name(event):
    pj_name_label.config(text=projects.get(selected_pjno.get(), ""))

pj_combobox.bind("<<ComboboxSelected>>", update_project_name)

# メインループの開始
root.mainloop()
