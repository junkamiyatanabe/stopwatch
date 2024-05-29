import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import os
import subprocess

class WorkLogger:

    def __init__(self, master):
        self.master = master
        self.master.title("Stopwatch for working")

        # ファイルロードボタンを保持する辞書
        self.load_buttons = {}

        # 初期ファイルパス
        self.pj_file = os.path.join(os.getcwd(), "pj.txt")
        self.wk_file = os.path.join(os.getcwd(), "wk.txt")
        self.log_file = self.create_log_filename()
        self.f_path = None

        # GUI要素の初期化
        self.create_widgets()
        self.load_project_info()
        self.load_work_info()

        self.sttime = None
        self.etime = None
        self.no = self.get_last_log_number() + 1
        self.running = False

        self.colon_visible = True
        self.update_time()

        #計測中に終了できないような処理を追加
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def create_widgets(self):
        # Frame
        self.frame1=tk.Frame(self.master)#, bd=2, relief=tk.FLAT,bg="RED")
        self.frame2=tk.Frame(self.master)#, bd=2, relief=tk.FLAT,bg="BLUE")
        self.frame3=tk.Frame(self.master)#, bd=2, relief=tk.FLAT,bg="YELLOW")
        self.frame4=tk.Frame(self.master)#, bd=2, relief=tk.FLAT,bg="GREEN")

        # 境界線
        self.sep_style = ttk.Style()
        self.sep_style.configure("Gray.TSeparator", background="DarkGrey")
        self.sep_a = ttk.Separator(self.master, orient="vertical", style="Gray.TSeparator")
        self.sep_b = ttk.Separator(self.master, orient="horizontal", style="Gray.TSeparator")
        self.sep_c = ttk.Separator(self.master, orient="horizontal", style="Gray.TSeparator")

        # 時刻を表示するラベル
        self.time_label = tk.Label(self.frame1, text="00:00",anchor=tk.CENTER, font=("IPAゴシック",18))

        # プロジェクト,作業内容の表示と選択
        self.project_name_label=tk.Label(self.frame2, text="PJ", font=("IPAゴシック",9))
        self.project_combobox = ttk.Combobox(self.frame2, state="readonly", font=("IPAゴシック",9))
        self.work_name_label=tk.Label(self.frame2, text="Wk", font=("IPAゴシック",9))
        self.work_combobox = ttk.Combobox(self.frame2, state="readonly", font=("IPAゴシック",9))
        # 開始終了ボタン
        self.start_button = tk.Button(self.frame2, text="START", command=self.start_work, font=("IPAゴシック",9))
        self.end_button = tk.Button(self.frame2, text=" STOP", command=self.end_work, state=tk.DISABLED, font=("IPAゴシック",9))

        # ステータス表示とログボタン
        self.elapsed_time_label = tk.Label(self.frame3, text="0:00:00",anchor=tk.CENTER, font=("IPAゴシック",14))
        self.status_label = tk.Label(self.frame3, text="  Wait ", fg="red",anchor=tk.CENTER, font=("IPAゴシック",10))
        self.status_pj_wk_a = tk.Label(self.frame3, text="PJ No.",  font=("IPAゴシック",9),anchor=tk.W)
        self.status_pj_wk_b = tk.Label(self.frame3, text="PJ Name",  font=("IPAゴシック",9),anchor=tk.W)
        self.status_pj_wk_c = tk.Label(self.frame3, text="WORK",  font=("IPAゴシック",9),anchor=tk.W)
        self.status_pj_wk_space = tk.Label(self.frame3, text="",  font=("IPAゴシック",9),anchor=tk.W,width=30)
        self.open_log_button = tk.Button(self.frame3, text="Log", font=("", 9), command=lambda: self.open_file(self.log_file))

        #PJ,Wkのリロード
        self.reload_button = tk.Button(self.frame4, text="Re: PJ+Wk", font=("",9) , command=self.reload_pjwk)
        # 各ファイルを開くボタン。ここでラムダ式を使用して、open_fileメソッドにファイルパスを引数として渡す。
        self.open_pj_button = tk.Button(self.frame4, text="PJ", font=("", 9), command=lambda: self.open_file(self.pj_file))
        self.open_wk_button = tk.Button(self.frame4, text="WK", font=("", 9), command=lambda: self.open_file(self.wk_file))

        # PATHの表示
        self.path_label = tk.Label(self.frame4, text="File Path : " + os.getcwd(), font=("",9))

        #配置
        # self.master.columnconfigure(index=0,weight=1)
        # self.master.columnconfigure(index=1,weight=3)
        self.frame1.grid(row=0,column=0, sticky=tk.NSEW, padx=5, pady=(5,0))
        self.frame2.grid(row=0,column=2, sticky=tk.NSEW, padx=5, pady=(5,0))
        self.frame3.grid(row=2,column=0, columnspan=3, sticky=tk.NSEW , padx=5)
        self.frame4.grid(row=4,column=0, columnspan=3, padx=5)
        self.sep_a.grid(row=0, column=1, sticky="ns", padx=1,  pady=(5,0))
        self.sep_b.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(2,0))
        self.sep_c.grid(row=3, column=0, columnspan=3, sticky="ew", padx=20, pady=(0,2))

        self.time_label.grid(row=0, column=0,padx=(5,0))

        self.project_name_label.grid(row=0, column=0,padx=10)
        self.project_combobox.grid(row=0, column=1)
        self.work_name_label.grid(row=1, column=0,padx=10)
        self.work_combobox.grid(row=1, column=1)
        self.start_button.grid(row=0, column=2, padx=10,sticky=tk.E)
        self.end_button.grid(row=1, column=2, padx=10,sticky=tk.E)

        self.elapsed_time_label.grid(row=0,rowspan=2, column=0, padx=10)
        self.status_label.grid(row=2, column=0)
        self.status_pj_wk_a.grid(row=0, column=1,sticky=tk.W)
        self.status_pj_wk_b.grid(row=1, column=1,columnspan=2,sticky=tk.W)
        self.status_pj_wk_c.grid(row=2, column=1,columnspan=2,sticky=tk.W)
        self.status_pj_wk_space.grid(row=3, column=1,sticky=tk.W)
        self.open_log_button.grid(row=1,rowspan=3, column=3,padx=15)

        self.open_pj_button.grid(row=0, column=0,padx=5)
        self.open_wk_button.grid(row=0, column=1,padx=5)
        self.reload_button.grid(row=0, column=2,padx=5)
        self.path_label.grid(row=2,column=0,columnspan=4)

    def select_file(self, path_entry, label):
        file_path = filedialog.askopenfilename()
        if file_path:
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

    # リロードメソッド
    def reload_pjwk(self):
        self.load_project_info()
        self.load_work_info()

    # 時刻を更新するメソッド
    def update_time(self):
        # 現在の時刻を取得します('時:分' の形式)
        current_time = datetime.datetime.now().strftime('%H:%M')
        # フラグに基づいてコロンを表示/非表示にします
        if not self.colon_visible:
            current_time = current_time.replace(':', ' ')
        # ラベルのテキストを現在の時刻に更新します
        self.time_label.config(text=current_time)
        # コロンの表示/非表示を切り替えます
        self.colon_visible = not self.colon_visible
        # 1秒後に再度update_timeメソッドを呼び出します
        self.master.after(1000, self.update_time)

    def start_work(self):
        if not self.project_combobox.get() or not self.work_combobox.get():
            messagebox.showwarning("警告", "プロジェクトと作業内容を選択してください。")
            return

        self.sttime = datetime.datetime.now()
        self.status_label.config(text="Working", fg="green")
        self.pj_dat = str(self.project_combobox.get()).split(",",1)
        # self.status_pj_wk.config(text=self.pj_dat[0] + "/" + self.pj_dat[1]  + "/" + self.work_combobox.get())
        self.status_pj_wk_a.config(text=self.pj_dat[0] )
        self.status_pj_wk_b.config(text=self.pj_dat[1] )
        self.status_pj_wk_c.config(text=self.work_combobox.get())
        self.start_button.config(state=tk.DISABLED)
        self.end_button.config(state=tk.NORMAL)
        self.project_combobox.config(state=tk.DISABLED)
        self.work_combobox.config(state=tk.DISABLED)
        self.running = True
        self.log_action("start")

        self.start_button.config(state=tk.DISABLED)

        # 経過時間ラベルのリセット
        self.elapsed_time_label.config(text="00:00:00")
        self.update_elapsed_time()

        # ファイルロードボタンを無効化（グレーアウト）
        for load_buttons in self.load_buttons.values():
            load_buttons.config(state=tk.DISABLED)

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
        self.project_combobox.config(state=tk.NORMAL)
        self.work_combobox.config(state=tk.NORMAL)
        self.log_action("end")

        # ファイルロードボタンを有効化
        for load_buttons in self.load_buttons.values():
            load_buttons.config(state=tk.NORMAL)

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

    def open_file(self, f_path):
        # ファイルを開くための内部関数。OSに応じて適切なコマンドを実行します。
        if os.name == 'nt':  # Windowsの場合
            os.startfile(f_path)
        elif os.name == 'posix':  # macOS, Linuxの場合
            if os.uname().sysname == 'Darwin':  # macOS
                subprocess.call(["open", f_path])
            else:  # Linux
                subprocess.call(["xdg-open", f_path])

    # ウィンドウを閉じる際の動作を定義
    def on_closing(self):
        if self.running:
            # もしタイマーが計測中なら、ユーザーに終了確認のメッセージボックスを表示
            if messagebox.askokcancel("Quit", "Timer is running. Do you want to quit?"):
                self.master.destroy()  # OKが押されたらウィンドウを閉じる
        else:
            self.master.destroy()  # タイマーが計測中でなければ、直接ウィンドウを閉じる

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkLogger(root)
    root.mainloop()
