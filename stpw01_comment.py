import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# ttk:Tkinterの拡張ウィジェットセット
# filedialog:ファイル選択ダイアログを表示するために使用
# messagebox:メッセージボックスを表示するために使用
import datetime
# datetime:日付や時刻を扱うためのモジュール
import os
# os:オペレーティングシステムとのやり取りをするためのモジュール


class WorkLogger:

    # クラスのインスタンスが生成された際に自動的に呼び出される初期化メソッド
    def __init__(self, master): # selfはインスタンス自身？？
        self.master = master # master変数をインスタンス変数に設定→他のメソッドからtkinterの親ウィンドウにアクセスできるように
        self.master.title("作業時間記録システム")

        # 初期ファイルパス
        # os.path.join()：文字列を結合させ、一つのパスにする事ができる関数
        # os.getcwd()：Pythonが実行されている作業ディレクトリ（カレントディレクトリ）の絶対パスを文字列として返す関数
        self.pj_file = os.path.join(os.getcwd(), "pj.txt")
        self.wk_file = os.path.join(os.getcwd(), "wk.txt")
        self.log_file = self.create_log_filename() # ログファイルのファイル名を生成するメソッドを呼び出し

        # GUI要素の初期化
        self.create_widgets() # GUIウィジェットを作成するメソッドを呼び出し
        self.load_project_info() # プロジェクト情報を読み込むメソッドを呼び出し
        self.load_work_info() # 作業内容情報を読み込むメソッドを呼び出し

        self.sttime = None # 作業開始時間を初期化Noneは未設定
        self.etime = None # 作業終了時間を初期化
        # 通し番号は最後のログ番号を取得して、1加算
        # get_last_log_number()：最後に記録されたログの番号を取得するメソッド
        self.no = self.get_last_log_number() + 1
        self.running = False # 作業中の状態を管理。Trueなら作業中、Falseなら作業中ではない

    def create_widgets(self):
        # プロジェクト情報の表示と選択
        tk.Label(self.master, text="プロジェクト").grid(row=0, column=0)
        self.project_combobox = ttk.Combobox(self.master, state="readonly")
        self.project_combobox.grid(row=0, column=1, columnspan=2)

        # 作業内容の表示と選択
        tk.Label(self.master, text="作業内容").grid(row=1, column=0)
        self.work_combobox = ttk.Combobox(self.master, state="readonly")
        self.work_combobox.grid(row=1, column=1, columnspan=2)

        # ステータス表示
        self.status_label = tk.Label(self.master, text="作業前", fg="red")
        self.status_label.grid(row=2, column=0, columnspan=3)

        # 開始ボタン
        self.start_button = tk.Button(self.master, text="開始", command=self.start_work)
        self.start_button.grid(row=3, column=0)

        # 終了ボタン
        self.end_button = tk.Button(self.master, text="終了", command=self.end_work, state=tk.DISABLED)
        self.end_button.grid(row=3, column=1)

        # ログボタン
        self.log_button = tk.Button(self.master, text="ログを開く", command=self.open_log)
        self.log_button.grid(row=3, column=2)

        # 経過時間表示ラベルの追加
        self.elapsed_time_label = tk.Label(self.master, text="経過時間: 00:00:00")
        self.elapsed_time_label.grid(row=4, column=0, columnspan=3)

        # ファイルパスの表示と選択ボタン
        self.create_file_selector("pj-file", self.pj_file, 5)
        self.create_file_selector("wk-file", self.wk_file, 6)
        self.create_file_selector("log-file", self.log_file, 7)

    # ファイル選択のためのウィジェットを作成するメソッド
    def create_file_selector(self, label, filepath, row):
        # 指定されたラベルを持つLabelウィジェットを作成、指定された行の0列目に配置
        tk.Label(self.master, text=label).grid(row=row, column=0)
        # 指定されたファイルパスを初期値として持つEntryウィジェットを作成、指定された行の1列目に配置
        path_entry = tk.Entry(self.master, width=50)
        path_entry.insert(0, filepath)
        path_entry.grid(row=row, column=1)
        # 選択ボタンを指定された行の2列目に配置、クリックでselect_fileメソッドが呼び出し
        tk.Button(self.master, text="選択", command=lambda: self.select_file(path_entry, label)).grid(row=row, column=2)

    # ファイル選択ダイアログを表示、選択されたファイルパスをエントリーウィジェットに反映するメソッド
    def select_file(self, path_entry, label):
        # ファイル選択ダイアログを表示、選択されたファイルのパスを取得
        file_path = filedialog.askopenfilename()
        # ファイルパスが選択された場合
        if file_path:
            path_entry.delete(0, tk.END) # エントリーウィジェットの内容をクリア
            path_entry.insert(0, file_path) # エントリーウィジェットに新しいファイルパスを挿入
            # ラベルに基づいて処理
            if label == "pj-file":
                self.pj_file = file_path
                self.load_project_info() # プロジェクト情報読み込み
            elif label == "wk-file":
                self.wk_file = file_path
                self.load_work_info() # 作業情報読み込み
            elif label == "log-file":
                self.log_file = file_path # ログファイルとして保存

    # プロジェクト情報を読み込み、コンボボックスに設定するメソッド
    def load_project_info(self):
        try: # try構文＝例外処理（try, except, else, finally）
            with open(self.pj_file, "r", encoding="utf-8") as f:  # プロジェクト情報ファイルを読み込む
                projects = [line.strip() for line in f.readlines()]  # 各行を読み込み、前後の空白を削除してリストに格納
                self.project_combobox['values'] = projects  # 読み込んだプロジェクト情報をコンボボックスの選択肢に設定
        except FileNotFoundError:
            messagebox.showerror("エラー", f"{self.pj_file} が見つかりません。")  # ファイルが見つからない場合、エラーメッセージを表示

    # 作業内容情報を読み込み、コンボボックスに設定するメソッド
    def load_work_info(self):
        try:
            with open(self.wk_file, "r", encoding="utf-8") as f:  # 作業内容情報ファイルを開き、読み込む
                works = [line.strip() for line in f.readlines()]  # 各行を読み込み、前後の空白を削除してリストに格納
                self.work_combobox['values'] = works  # 読み込んだ作業内容情報をコンボボックスの選択肢に設定
        except FileNotFoundError:
            messagebox.showerror("エラー", f"{self.wk_file} が見つかりません。")  # ファイルが見つからない場合、エラーメッセージを表示

    # ログファイルのファイル名を作成するメソッド
    def create_log_filename(self):
        now = datetime.datetime.now()
        # 現在作業中のディレクトリのパスに、"log_年月.csv" という形式のファイル名を結合して返す
        return os.path.join(os.getcwd(), f"log_{now.strftime('%Y%m')}.csv")

    # 最後に記録されたログの番号を取得するメソッド
    def get_last_log_number(self):
        try:
            # log_file属性に指定されたファイルを読み込む
            with open(self.log_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()  # 全ての行を読み込む
                if lines:
                    last_line = lines[-1]  # 最後の行を取得
                    last_no = int(last_line.split(',')[0])  # 最後の行の最初の要素（ログ番号）を整数に変換して取得
                    return last_no  # 取得したログ番号を返す
        except FileNotFoundError:
            # ファイルが見つからない場合は0を返す
            return 0
        except Exception as e: # try発生した例外オブジェクト は except Exception as e: の e に格納
            # その他のエラーが発生した場合、エラーメッセージを表示し、0を返す
            messagebox.showerror("エラー", f"ログファイルの読み込み中にエラーが発生しました: {e}")
            return 0
        # tryブロック内でreturnされなかった場合も0を返す
        return 0

    # 作業開始処理のメソッド
    def start_work(self):
        # プロジェクトと作業内容が選択されていない場合、警告を表示して処理を中断
        if not self.project_combobox.get() or not self.work_combobox.get():
            messagebox.showwarning("警告", "プロジェクトと作業内容を選択してください。")
            return

        self.sttime = datetime.datetime.now()  # 作業開始時刻を記録
        self.status_label.config(text="作業中", fg="green")  # 状態ラベルを「作業中」に更新
        self.start_button.config(state=tk.DISABLED)  # 開始ボタンを無効化
        self.end_button.config(state=tk.NORMAL)  # 終了ボタンを有効化
        self.running = True  # 作業中フラグを立てる
        self.log_action("start")  # ログに作業開始を記録

        # 経過時間ラベルのリセット
        self.elapsed_time_label.config(text="経過時間: 00:00:00")
        self.update_elapsed_time()  # 経過時間の更新を開始

    # 経過時間を更新するメソッド
    def update_elapsed_time(self):
        if self.running:
            # 現在時刻と作業開始時刻の差を計算
            elapsed_time = datetime.datetime.now() - self.sttime
            elapsed_time_str = str(elapsed_time).split('.')[0]  # ミリ秒を除外して文字列化
            self.elapsed_time_label.config(text=f"経過時間: {elapsed_time_str}") # 経過時間ラベルを更新
            # 1秒後に再度このメソッドを呼び出して更新を続ける
            self.master.after(1000, self.update_elapsed_time)

    # 作業を終了するメソッド
    def end_work(self):
        self.etime = datetime.datetime.now()  # 作業終了時刻を記録
        self.status_label.config(text="作業前", fg="red")  # 状態ラベルを「作業前」に更新
        self.start_button.config(state=tk.NORMAL)  # 開始ボタンを有効化
        self.end_button.config(state=tk.DISABLED)  # 終了ボタンを無効化
        self.running = False  # 作業中フラグを下ろす
        self.log_action("end")  # ログに作業終了を記録

        # ログに記録するメソッド
    def log_action(self, action):
        if action == "start":
            # 開始時には何もしない
            pass
        elif action == "end":
            ttime = (self.etime - self.sttime).total_seconds() / 3600  # 作業時間を計算、秒から時間に変換
            with open(self.log_file, "a", encoding="utf-8-sig") as f:
                # ログファイルに作業記録を追記する。ファイルエンコーディングは utf-8-sig を使用
                # 開始時刻、終了時刻、作業時間を同じ1行に記録、「YYYY-MM-DD HH:MM:SS」形式で
                sttime_str = self.sttime.strftime('%Y-%m-%d %H:%M:%S')
                etime_str = self.etime.strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{self.no},{self.project_combobox.get()},{self.work_combobox.get()},{sttime_str},{etime_str},{ttime:.2f}\n")
            self.no += 1 # 作業記録の番号をインクリメント

    # ログファイルをデフォルトのプログラムで開くメソッド
    def open_log(self):
        if os.name == 'nt':  # Windows
            os.startfile(self.log_file)
        elif os.name == 'posix':  # macOS, Linux
            # macOSの場合は`open`コマンド、それ以外のPOSIXシステムでは`xdg-open`コマンドを使用してログファイルを開く
            os.system(f"open {self.log_file}" if os.uname().sysname == 'Darwin' else f"xdg-open {self.log_file}")

if __name__ == "__main__":
    # プログラム自身（モジュールではなくメインプログラムとして）で実行されているかどうかの判定
    #  →この ***.py は python ***.py のように実行された
    #  （== importされたことで動作したのではない）と判定する
    root = tk.Tk()
    app = WorkLogger(root)  # WorkLoggerクラスのインスタンスを作成し、GUIを初期化
    root.mainloop()  # GUIのメインループを開始
