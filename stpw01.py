import tkinter as tk
from tkinter import ttk
import datetime
import os
import subprocess
import platform

# プロジェクトと作業内容のデータを読み込む関数
def load_data():
    with open("pj.txt", "r") as f:
        projects = [line.strip().split(",") for line in f.readlines()]
    with open("wk.txt", "r") as f:
        works = [line.strip() for line in f.readlines()]
    return projects, works

# ログファイルに書き込む関数
def write_log(start=True):
    now = datetime.datetime.now()
    filename = f"log_{now.strftime('%Y%m')}.txt"
    if start:
        with open(filename, "a") as f:
            f.write(f"{app.no},{app.pjno.get()},{app.pjname.get()},{app.work.get()},{now},")
    else:
        with open(filename, "a") as f:
            f.write(f"{app.pjno.get()},{app.pjname.get()},{app.work.get()},{now},")
            delta = now - app.sttime
            hours = delta.total_seconds() / 3600
            f.write(f"{hours}\n")
    app.no += 1

# ログファイルを開く関数
def open_log():
    now = datetime.datetime.now()
    filename = f"log_{now.strftime('%Y%m')}.txt"
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", filename])
    else:
        subprocess.call(["xdg-open", filename])

# 作業開始の処理
def start_work():
    app.sttime = datetime.datetime.now()
    app.state_label.config(text="作業中")
    write_log(start=True)
    app.start_button.config(state="disabled")
    app.end_button.config(state="normal")

# 作業終了の処理
def end_work():
    write_log(start=False)
    app.state_label.config(text="作業前")
    app.start_button.config(state="normal")
    app.end_button.config(state="disabled")

# アプリケーションのGUIを定義
class TimeTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("作業時間トラッカー")
        self.geometry("400x300")

        # 変数の定義
        self.projects, self.works = load_data()
        self.pjno = tk.StringVar()
        self.pjname = tk.StringVar()
        self.work = tk.StringVar()
        self.sttime = None
        self.no = 1

        # プロジェクトの選択
        ttk.Label(self, text="プロジェクト番号:").pack()
        ttk.Combobox(self, textvariable=self.pjno, values=[p[0] for p in self.projects]).pack()
        ttk.Label(self, text="プロジェクト名:").pack()
        ttk.Combobox(self, textvariable=self.pjname, values=[p[1] for p in self.projects]).pack()

        # 作業内容の選択
        ttk.Label(self, text="作業内容:").pack()
        ttk.Combobox(self, textvariable=self.work, values=self.works).pack()

        # 状態表示
        self.state_label = ttk.Label(self, text="作業前")
        self.state_label.pack()

        # 開始、終了、ログボタン
        self.start_button = ttk.Button(self, text="開始", command=start_work)
        self.start_button.pack(pady=5)
        self.end_button = ttk.Button(self, text="終了", command=end_work, state="disabled")
        self.end_button.pack(pady=5)
        ttk.Button(self, text="ログを見る", command=open_log).pack(pady=5)

# アプリケーションの実行
if __name__ == "__main__":
    app = TimeTrackerApp()
    app.mainloop()
