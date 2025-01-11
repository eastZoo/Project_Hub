import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from PIL import Image, ImageTk
import shutil
import threading

CONFIG_FILE = "config.json"
APP_ICON = "./app_icon.ico"

class ProjectOpenerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Hub")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # 아이콘 설정
        if os.path.exists(APP_ICON):
            self.root.iconbitmap(APP_ICON)

        # Config 파일에서 데이터 불러오기
        config = self.load_config()
        self.dev_path = config.get("dev_path", "")
        self.favorites = config.get("favorites", [])
        self.editor = config.get("editor", "vscode")
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')

        # Dev 폴더 설정 UI
        self.dev_path_frame = tk.Frame(root, bg="#f0f0f0")
        self.dev_path_frame.pack(pady=10)
        tk.Label(self.dev_path_frame, text="Dev 폴더 경로: ", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.dev_path_entry = tk.Entry(self.dev_path_frame, width=50)
        self.dev_path_entry.pack(side=tk.LEFT, padx=5)
        self.dev_path_entry.insert(0, self.dev_path)
        ttk.Button(self.dev_path_frame, text="Browse", command=self.select_dev_folder).pack(side=tk.LEFT)

        # 편집기 선택 UI
        self.editor_frame = tk.Frame(root, bg="#f0f0f0")
        self.editor_frame.pack(pady=10)
        tk.Label(self.editor_frame, text="편집기:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.editor_var = tk.StringVar(value=self.editor)
        tk.Radiobutton(self.editor_frame, text="VS Code", variable=self.editor_var, value="vscode", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(self.editor_frame, text="Cursor", variable=self.editor_var, value="cursor", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)

        # 메인 프로젝트 및 하위 프로젝트 리스트
        self.project_frame = tk.Frame(root, bg="#f0f0f0")
        self.project_frame.pack(pady=10)
        tk.Label(self.project_frame, text="메인 프로젝트:", bg="#f0f0f0").pack(anchor="w")
        self.project_list = ttk.Combobox(self.project_frame, state="readonly", width=60)
        self.project_list.pack(pady=5)
        self.project_list.bind("<<ComboboxSelected>>", self.show_subfolders)
        tk.Label(self.project_frame, text="하위 프로젝트:", bg="#f0f0f0").pack(anchor="w")
        self.subfolder_list = tk.Listbox(self.project_frame, selectmode="multiple", height=10, width=60)
        self.subfolder_list.pack(pady=5)

        # 즐겨찾기 UI
        self.favorites_frame = tk.Frame(root, bg="#f0f0f0")
        self.favorites_frame.pack(pady=10)
        tk.Label(self.favorites_frame, text="즐겨찾기:", bg="#f0f0f0").pack(anchor="w")
        self.favorites_list = tk.Listbox(self.favorites_frame, height=5, width=60)
        self.favorites_list.pack(pady=5)
        self.favorites_list.bind("<<ListboxSelect>>", self.show_favorites_subfolders)

        self.fav_button_frame = tk.Frame(self.favorites_frame, bg="#f0f0f0")
        self.fav_button_frame.pack()
        ttk.Button(self.fav_button_frame, text="추가", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.fav_button_frame, text="제거", command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)

        # 열기 버튼
        ttk.Button(root, text="열기", command=self.open_selected_projects).pack(pady=10)

        # 초기 Dev 폴더 로드
        if self.dev_path:
            self.populate_main_projects(self.dev_path)
            self.update_favorites_list()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        config = {
            "dev_path": self.dev_path,
            "favorites": self.favorites,
            "editor": self.editor_var.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def select_dev_folder(self):
        dev_path = filedialog.askdirectory(title="Select Dev Folder")
        if dev_path:
            self.dev_path_entry.delete(0, tk.END)
            self.dev_path_entry.insert(0, dev_path)
            self.dev_path = dev_path
            self.save_config()
            self.populate_main_projects(dev_path)

    def populate_main_projects(self, dev_path):
        if not os.path.isdir(dev_path):
            messagebox.showerror("Error", "올바른 폴더 경로가 아닙니다.")
            return
        main_projects = [
            folder for folder in os.listdir(dev_path)
            if os.path.isdir(os.path.join(dev_path, folder))
        ]
        self.project_list["values"] = main_projects
        self.project_list.set("")
        self.subfolder_list.delete(0, tk.END)

    def show_subfolders(self, event):
        dev_path = self.dev_path_entry.get()
        selected_project = self.project_list.get()
        if not selected_project:
            return
        subfolder_path = os.path.join(dev_path, selected_project)
        subfolders = [
            folder for folder in os.listdir(subfolder_path)
            if os.path.isdir(os.path.join(subfolder_path, folder))
        ]
        self.subfolder_list.delete(0, tk.END)
        for subfolder in subfolders:
            self.subfolder_list.insert(tk.END, subfolder)

    def show_favorites_subfolders(self, event):
        selection = self.favorites_list.curselection()
        if not selection:
            return
        selected_project = self.favorites[selection[0]]
        self.project_list.set(selected_project)
        self.show_subfolders(None)

    def get_editor_path(self, editor):
        paths = {
            "vscode": os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code', 'Code.exe'),
            "cursor": os.path.join(os.environ.get('ProgramFiles', ''), 'Cursor', 'Cursor.exe')
        }
        path = paths.get(editor, "")
        if not os.path.exists(path):
            messagebox.showerror("Error", f"{editor.capitalize()}가 설치되어 있지 않습니다.")
            return None
        return path

    def create_progress_window(self):
        progress_window = tk.Toplevel(self.root)
        progress_window.title("작업 진행 중")
        progress_window.geometry("300x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # 진행 상황 표시 레이블
        self.progress_label = tk.Label(progress_window, text="프로젝트 준비 중...", pady=10)
        self.progress_label.pack()
        
        # 프로그레스 바
        self.progress_bar = ttk.Progressbar(
            progress_window, 
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(pady=10)
        
        return progress_window

    def process_project(self, folder_path, project_name, progress_window):
        try:
            self.progress_label.config(text=f"{project_name}: git pull 실행 중...")
            subprocess.run(['git', 'pull'], cwd=folder_path, check=True)
            
            if os.path.exists(os.path.join(folder_path, 'package.json')):
                self.progress_label.config(text=f"{project_name}: npm install 실행 중...")
                subprocess.run([self.npm_path, 'i'], cwd=folder_path, check=True)
            
            return None  # 성공 시 None 반환
        except subprocess.CalledProcessError as e:
            return f"{project_name}: {'git pull' if 'git' in str(e) else 'npm i'} 실패"

    def open_selected_projects(self):
        editor_path = self.get_editor_path(self.editor_var.get())
        if not editor_path:
            return

        dev_path = self.dev_path_entry.get()
        selected_project = self.project_list.get()
        selected_indices = self.subfolder_list.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "하위 프로젝트를 선택하세요.")
            return

        self.npm_path = shutil.which('npm')
        if not self.npm_path:
            messagebox.showerror("오류", "npm이 설치되어 있지 않습니다. PATH를 확인하세요.")
            return

        # 프로그레스 창 생성
        progress_window = self.create_progress_window()
        self.progress_bar.start()
        
        error_messages = []
        
        def process_all_projects():
            for i in selected_indices:
                project_name = self.subfolder_list.get(i)
                folder_path = os.path.join(dev_path, selected_project, project_name)
                
                error = self.process_project(folder_path, project_name, progress_window)
                if error:
                    error_messages.append(error)
                else:
                    subprocess.Popen([editor_path, folder_path], shell=False)
            
            # UI 업데이트는 메인 스레드에서 실행
            self.root.after(0, lambda: self.finish_processing(progress_window, error_messages))
        
        # 별도 스레드에서 프로젝트 처리 실행
        threading.Thread(target=process_all_projects, daemon=True).start()

    def finish_processing(self, progress_window, error_messages):
        progress_window.destroy()
        if error_messages:
            messagebox.showerror("오류", "\n".join(error_messages))

    def add_to_favorites(self):
        selected_project = self.project_list.get()
        if selected_project and selected_project not in self.favorites:
            self.favorites.append(selected_project)
            self.update_favorites_list()
            self.save_config()

    def remove_from_favorites(self):
        selected_index = self.favorites_list.curselection()
        if selected_index:
            del self.favorites[selected_index[0]]
            self.update_favorites_list()
            self.save_config()

    def update_favorites_list(self):
        self.favorites_list.delete(0, tk.END)
        for favorite in self.favorites:
            self.favorites_list.insert(tk.END, favorite)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectOpenerApp(root)
    root.mainloop()
