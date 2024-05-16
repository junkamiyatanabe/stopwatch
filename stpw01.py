import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import datetime
import os
import subprocess

# プロジェクトと作業内容を読み込む関数
def load_projects_and_works():
    global projects, works
    try:
        with open("pj.txt", "r") as f:
            projects = [line.strip().split(",") for line in f.readlines()]
        with open("wk.txt", "r") as f:
            works = [line.strip() for line in f.readlines()]
    except Exception as e:
        messagebox.showerror("読み込みエラー", f"ファイルの読み込み中にエラーが発生しました: {e}")
        root.quit()

# ログファイルのパスを取得
def get_log_file_path():
    now = datetime.datetime.now()
    return f"log_{now.strftime('%Y%m')}.txt"

# 開始ボタン押下時の処理
def start_task():
    global sttime
    if not (pjno_var.get() and work_var.get()):
        messagebox.showwarning("警告", "プロジェクト番号と作業内容を選択してください。")
        return
    sttime = datetime.datetime.now()
    status_label.config(text="作業中")
    start_button.config(state="disabled")
    end_button.config(state="normal")
    project_combobox.config(state="disabled")
    work_combobox.config(state="disabled")
    log_path = get_log_file_path()
    no = 1
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()
            if lines:
                last_no = int(lines[-1].split(",")[0])
                no = last_no + 1
    with open(log_path, "a") as f:
        f.write(f"{no},{pjno_var.get()},{pjname_var.get()},{work_var.get()},{sttime.strftime('%Y-%m-%d %H:%M')},")
    update_elapsed_time()

# 終了ボタン押下時の処理
def end_task():
    global etime, ttime
    etime = datetime.datetime.now()
    ttime = (etime - sttime).total_seconds() / 3600  # 時間単位に変換
    status_label.config(text="作業前")
    start_button.config(state="normal")
    end_button.config(state="disabled")
    project_combobox.config(state="normal")
    work_combobox.config(state="normal")
    log_path = get_log_file_path()
    with open(log_path, "a") as f:
        f.write(f"{pjno_var.get()},{pjname_var.get()},{work_var.get()},{etime.strftime('%Y-%m-%d %H:%M')},{ttime:.2f}\n")

# 経過時間の更新
def update_elapsed_time():
    if status_label.cget("text") == "作業中":
        now = datetime.datetime.now()
        elapsed = now - sttime
        elapsed_label.config(text=f"{elapsed}")
        root.after(1000, update_elapsed_time)

# ログファイルを開く
def open_log():
    log_path = get_log_file_path()
    if os.path.exists(log_path):
        if os.name == 'nt':  # Windows
            os.startfile(log_path)
        elif os.name == 'posix':  # macOS, Linux
            subprocess.call(('open', log_path))
    else:
        messagebox.showinfo("情報", "ログファイルが存在しません。")

# GUIの設定
root = tk.Tk()
root.title("作業時間記録アプリ")

# プロジェクトと作業内容の変数
pjno_var = tk.StringVar()
pjname_var = tk.StringVar()
work_var = tk.StringVar()

load_projects_and_works()

# プロジェクト選択
project_frame = ttk.Frame(root)
project_frame.pack(pady=10)
ttk.Label(project_frame, text="プロジェクト:").pack(side="left")
project_combobox = ttk.Combobox(project_frame, textvariable=pjname_var, values=[f"{p[0]}, {p[1]}" for p in projects])
project_combobox.pack(side="left")
project_combobox.bind("<<ComboboxSelected>>", lambda e: pjno_var.set(project_combobox.get().split(",")[0]))

# 作業内容選択
work_frame = ttk.Frame(root)
work_frame.pack(pady=10)
ttk.Label(work_frame, text="作業内容:").pack(side="left")
work_combobox = ttk.Combobox(work_frame, textvariable=work_var, values=works)
work_combobox.pack(side="left")

# 状態表示
status_label = ttk.Label(root, text="作業前")
status_label.pack(pady=10)

# 経過時間表示
elapsed_label = ttk.Label(root, text="")
elapsed_label.pack(pady=5)

# ボタン配置
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)
start_button = ttk.Button(button_frame, text="開始", command=start_task)
start_button.pack(side="left", padx=5)
end_button = ttk.Button(button_frame, text="終了", command=end_task, state="disabled")
end_button.pack(side="left", padx=5)
log_button = ttk.Button(button_frame, text="ログを開く", command=open_log)
log_button.pack(side="left", padx=5)

root.mainloop()
