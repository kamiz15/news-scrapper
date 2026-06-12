import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import sys
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Ansu Invest Desktop App")
        self.root.geometry("680x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f6")

        try:
            self.root.iconbitmap(default=os.path.join(BASE_DIR, "assets", "dist", "icon", "favicon.ico"))
        except Exception:
            pass

        self.dashboard_process = None

        main_frame = tk.Frame(root, bg="#f0f2f6", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            main_frame, text="Ansu Invest Desktop App",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f2f6", fg="#032033"
        )
        title.pack(pady=(0, 5))

        subtitle = tk.Label(
            main_frame, text="News Scraper & Hydropower Dashboard",
            font=("Segoe UI", 10),
            bg="#f0f2f6", fg="#595959"
        )
        subtitle.pack(pady=(0, 20))

        btn_frame = tk.Frame(main_frame, bg="#f0f2f6")
        btn_frame.pack(fill=tk.X)

        self.scrape_btn = tk.Button(
            btn_frame, text="Fetch All Data",
            font=("Segoe UI", 11, "bold"),
            bg="#032033", fg="white",
            padx=20, pady=8, border=0,
            cursor="hand2", command=self.start_scrape
        )
        self.scrape_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.dashboard_btn = tk.Button(
            btn_frame, text="Open Dashboard",
            font=("Segoe UI", 11, "bold"),
            bg="#f79920", fg="white",
            padx=20, pady=8, border=0,
            cursor="hand2", command=self.open_dashboard
        )
        self.dashboard_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.logs_btn = tk.Button(
            btn_frame, text="View Logs",
            font=("Segoe UI", 10),
            bg="#6c757d", fg="white",
            padx=15, pady=8, border=0,
            cursor="hand2", command=self.open_logs
        )
        self.logs_btn.pack(side=tk.RIGHT, padx=(0, 5))

        self.quit_btn = tk.Button(
            btn_frame, text="Quit",
            font=("Segoe UI", 10),
            bg="#dc3545", fg="white",
            padx=15, pady=8, border=0,
            cursor="hand2", command=self.quit_app
        )
        self.quit_btn.pack(side=tk.RIGHT)

        progress_frame = tk.Frame(main_frame, bg="#f0f2f6")
        progress_frame.pack(fill=tk.X, pady=(20, 5))

        self.progress = ttk.Progressbar(
            progress_frame, mode="determinate",
            length=640, value=0
        )
        self.progress.pack(fill=tk.X)

        self.status_label = tk.Label(
            main_frame, text="Ready. Click 'Fetch All Data' to start.",
            font=("Segoe UI", 9),
            bg="#f0f2f6", fg="#595959", anchor="w",
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        self.log_box = scrolledtext.ScrolledText(
            main_frame, height=12,
            font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4",
            state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)

        self.log("Ansu Invest Desktop App v1.0")
        self.log("Ready. Click 'Fetch All Data' to scrape all news and research.")

    def log(self, msg):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)
        self.root.update()

    def set_status(self, msg, progress=None):
        self.status_label.config(text=msg)
        if progress is not None:
            self.progress["value"] = progress
        self.root.update()

    def progress_callback(self, msg, pct):
        self.set_status(msg, pct)
        self.log(msg)

    def start_scrape(self):
        self.scrape_btn.config(state=tk.DISABLED, text="Fetching...")
        self.progress["value"] = 0
        self.log("=== Starting data fetch ===")
        self.log("Fetching all news articles and research reports...")
        thread = threading.Thread(target=self._run_scrape, daemon=True)
        thread.start()

    def _run_scrape(self):
        try:
            from scraper.runner import run_all
            run_all(progress_callback=self.progress_callback)
            self.root.after(0, self._scrape_done)
        except Exception as e:
            self.root.after(0, lambda: self._scrape_error(str(e)))

    def _scrape_done(self):
        self.scrape_btn.config(state=tk.NORMAL, text="Fetch All Data")
        self.log("=== Data fetch complete! ===")
        self.set_status("Done! Click 'Open Dashboard' to view data.", 100)

    def _scrape_error(self, err):
        self.scrape_btn.config(state=tk.NORMAL, text="Fetch All Data")
        self.log(f"ERROR: {err}")
        self.set_status(f"Error: {err}", 0)

    def _kill_process_tree(self, pid):
        """Kill a process and all its children (streamlit.exe spawns python.exe)."""
        subprocess.run(
            ["taskkill", "/pid", str(pid), "/t", "/f"],
            capture_output=True,
        )

    def _kill_port_8501(self):
        """Kill whatever is still listening on the dashboard port (leftover from a crash)."""
        try:
            out = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            ).stdout
            for line in out.splitlines():
                parts = line.split()
                if (len(parts) >= 5 and parts[0] == "TCP"
                        and parts[1].endswith(":8501")
                        and parts[3] == "LISTENING"):
                    self.log(f"Stopping leftover dashboard process (PID {parts[4]})...")
                    self._kill_process_tree(parts[4])
        except Exception:
            pass

    def open_dashboard(self):
        self.log("Starting Streamlit dashboard...")
        self.set_status("Launching dashboard...")
        try:
            streamlit_path = r"C:\Users\User\AppData\Roaming\Python\Python310\Scripts\streamlit.exe"
            if not os.path.exists(streamlit_path):
                streamlit_path = "streamlit"

            if self.dashboard_process and self.dashboard_process.poll() is None:
                self._kill_process_tree(self.dashboard_process.pid)
            self._kill_port_8501()

            self.dashboard_process = subprocess.Popen(
                [streamlit_path, "run", os.path.join(BASE_DIR, "dashboard", "app.py")],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
            )
            webbrowser.open("http://localhost:8501")
            self.log("Dashboard launched at http://localhost:8501")
            self.set_status("Dashboard is running in your browser.")
        except Exception as e:
            self.log(f"Failed to launch dashboard: {e}")
            self.set_status("Dashboard failed to launch.")

    def open_logs(self):
        log_path = os.path.join(BASE_DIR, "scraper.log")
        if os.path.exists(log_path):
            os.startfile(log_path)
            self.log(f"Opened log file: {log_path}")
        else:
            self.log("No log file found. Run 'Fetch All Data' first.")
            self.set_status("No log file yet.")

    def quit_app(self):
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self._kill_process_tree(self.dashboard_process.pid)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.mainloop()
