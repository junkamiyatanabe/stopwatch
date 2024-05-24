import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import os

class WorkLogger:

    def __init__(self, master):
        self.master = master
        self.master.title("Stopwatch for working")

        # 初期ファイルパス
        self.pj_file = os.path.join(os.getcwd(), "pj.txt")
        self.wk_file = os.path.join(os.getcwd(), "wk.txt")
        self.log_file = self.create_log_filename()

        # GUI要素の初期化
        self.create_widgets()
        self.load_project_info()
        self.load_work_info()

        self.sttime = None
        self.etime = None
        self.no = self.get_last_log_number() + 1
        self.running = False

        self.update_time()


    def create_widgets(self):
        #Frame
        self.frame1=tk.Frame(self.master)
        self.frame2=tk.Frame(self.master)

        # プロジェクト情報の表示と選択
        self.project_name_label=tk.Label(self.frame1, text="PJ")
        self.project_combobox = ttk.Combobox(self.frame1, state="readonly")

        # 作業内容の表示と選択
        self.work_name_label=tk.Label(self.frame1, text="Wk")
        self.work_combobox = ttk.Combobox(self.frame1, state="readonly")

        # 時刻を表示するラベル
        self.time_label = tk.Label(self.frame1, text="00:00:00")

        # ステータス表示
        self.status_label = tk.Label(self.frame1, text="Wait", fg="red")

        # 開始ボタン
        self.start_button = tk.Button(self.frame1, text="START", command=self.start_work)
        # 終了ボタン
        self.end_button = tk.Button(self.frame1, text="STOP", command=self.end_work, state=tk.DISABLED)
        # ログボタン
        self.log_button = tk.Button(self.frame1, text="Log", command=self.open_log)
        # 経過時間表示ラベルの追加
        self.elapsed_time_label = tk.Label(self.frame1, text="00:00:00")

        # ファイルパスの表示と選択ボタン
        self.create_file_selector("pj-file: ", self.pj_file, 5)
        self.create_file_selector("wk-file: ", self.wk_file, 6)
        self.create_file_selector("log-file: ", self.log_file, 7)

        #配置
        self.frame1.grid(row=0,column=0,sticky=tk.NE, pady=10)
        self.frame2.grid(row=1,column=0,sticky=tk.NW, pady=10,padx=5)

        self.project_name_label.grid(row=0, column=2,padx=10)
        self.project_combobox.grid(row=0, column=3, columnspan=2)
        self.work_name_label.grid(row=1, column=2,padx=10)
        self.work_combobox.grid(row=1, column=3, columnspan=2)

        self.time_label.grid(row=0, column=0, columnspan=2)
        self.status_label.grid(row=1, column=0, columnspan=2)
        self.elapsed_time_label.grid(row=2, column=0, columnspan=2)

        self.start_button.grid(row=0, column=5, padx=10,sticky=tk.E)
        self.end_button.grid(row=1, column=5, padx=10,sticky=tk.E)
        self.log_button.grid(row=2, column=5, padx=10,sticky=tk.E)

    def create_file_selector(self, label, filepath, row):
        tk.Label(self.frame2, text=label).grid(row=row, column=0)
        path_entry = tk.Label(self.frame2,width=35,text=filepath,anchor=tk.W)
        # path_entry = tk.Entry(self.master, width=50)
        # path_entry.insert(0, filepath)
        path_entry.grid(row=row, column=1, columnspan=4)
        tk.Button(self.frame2, text="load", command=lambda: self.select_file(path_entry, label)).grid(row=row, column=5)

    # def select_file(self, path_entry):
    def select_file(self, path_entry, label):
        file_path = filedialog.askopenfilename()
        if file_path:
            # path_entry.delete(0, tk.END)
            # path_entry.insert(0, file_path)
            path_entry.config(text=file_path)
            # 以下追加
            if label == "pj-file":
                self.pj_file = file_path
                self.load_project_info()
            elif label == "wk-file":
                self.wk_file = file_path
                self.load_work_info()
            elif label == "log-file":
                self.log_file = file_path

    def load_project_info(self):
        try:
            with open(self.pj_file, "r", encoding="utf-8") as f:
                projects = [line.strip() for line in f.readlines()]
                self.project_combobox['values'] = projects
        except FileNotFoundError:
            messagebox.showerror("エラー", f"{self.pj_file} が見つかりません。")

    def load_work_info(self):
        try:
            with open(self.wk_file, "r", encoding="utf-8") as f:
                works = [line.strip() for line in f.readlines()]
                self.work_combobox['values'] = works
        except FileNotFoundError:
            messagebox.showerror("エラー", f"{self.wk_file} が見つかりません。")

    def create_log_filename(self):
        now = datetime.datetime.now()
        return os.path.join(os.getcwd(), f"log_{now.strftime('%Y%m')}.csv")

    def get_last_log_number(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    last_no = int(last_line.split(',')[0])
                    return last_no
        except FileNotFoundError:
            return 0
        except Exception as e:
            messagebox.showerror("エラー", f"ログファイルの読み込み中にエラーが発生しました: {e}")
            return 0
        return 0

    # 時刻を更新するメソッド
    def update_time(self):
        # 現在の時刻を取得します('時:分:秒' の形式)
        current_time = datetime.datetime.now().strftime('%H:%M')
        # ラベルのテキストを現在の時刻に更新します
        self.time_label.config(text=current_time)
        # 3秒後にこの関数を再び呼び出して時刻を更新し続けます
        self.master.after(3000, self.update_time)

    def start_work(self):
        if not self.project_combobox.get() or not self.work_combobox.get():
            messagebox.showwarning("警告", "プロジェクトと作業内容を選択してください。")
            return

        self.sttime = datetime.datetime.now()
        self.status_label.config(text="Working", fg="green")
        self.start_button.config(state=tk.DISABLED)
        self.end_button.config(state=tk.NORMAL)
        self.running = True
        self.log_action("start")

        # 経過時間ラベルのリセット
        self.elapsed_time_label.config(text="00:00:00")
        self.update_elapsed_time()

    def update_elapsed_time(self):
        if self.running:
            elapsed_time = datetime.datetime.now() - self.sttime
            elapsed_time_str = str(elapsed_time).split('.')[0]  # ミリ秒を除外
            self.elapsed_time_label.config(text=f"{elapsed_time_str}")
            # 1秒後に再度このメソッドを呼び出して更新を続ける
            self.master.after(1000, self.update_elapsed_time)

    def end_work(self):
        self.etime = datetime.datetime.now()
        self.status_label.config(text="Wait", fg="red")
        self.start_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        self.running = False
        self.log_action("end")

    def log_action(self, action):
        if action == "start":
            # 開始時には何もしない
            pass
        elif action == "end":
            ttime = (self.etime - self.sttime).total_seconds() / 3600  # 作業時間を計算
            with open(self.log_file, "a", encoding="utf-8-sig") as f:  # utf-8-sig エンコーディングを使用
                # 開始時刻、終了時刻、作業時間を同じ1行に記録
                # 日時を「YYYY-MM-DD HH:MM:SS」形式でフォーマット
                sttime_str = self.sttime.strftime('%Y-%m-%d %H:%M:%S')
                etime_str = self.etime.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{self.no},{self.project_combobox.get()},{self.work_combobox.get()},{sttime_str},{etime_str},{ttime:.2f}\n")
            self.no += 1

    def open_log(self):
        if os.name == 'nt':  # Windows
            os.startfile(self.log_file)
        elif os.name == 'posix':  # macOS, Linux
            os.system(f"open {self.log_file}" if os.uname().sysname == 'Darwin' else f"xdg-open {self.log_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkLogger(root)
    root.mainloop()
