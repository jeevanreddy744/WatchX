import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import os


# ============================================================
# WATCHX DESKTOP APPLICATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# When WatchX is running as a normal Python program, BASE_DIR is
# the project folder.
#
# When WatchX is packaged, the final layout will be:
#
#   dist/
#       WatchX/
#           WatchX.exe
#       plate_ocr/
#           plate_ocr.exe
#       dashboard/
#           dashboard.exe
#
# Therefore packaged helper executables are located beside the
# WatchX application folder.
if getattr(sys, "frozen", False):
    # PyInstaller --onedir:
    # BASE_DIR = ...\\dist\\WatchX\\_internal
    # The helper EXEs and writable WatchX data are beside WatchX.exe.
    APP_ROOT = BASE_DIR.parent
else:
    APP_ROOT = BASE_DIR

INPUT_PATH = BASE_DIR / "data" / "videos" / "my_traffic_video.MOV"

OCR_SCRIPT = BASE_DIR / "plate_ocr.py"
DASHBOARD_SCRIPT = BASE_DIR / "dashboard.py"

OCR_EXE = APP_ROOT / "plate_ocr" / "plate_ocr.exe"
DASHBOARD_EXE = APP_ROOT / "dashboard" / "dashboard.exe"

LOGO_PATH = BASE_DIR / "WatchX_Logo.png"

# All WatchX components share this directory.
# This prevents the OCR engine and dashboard from using
# different CSV/evidence locations.
WATCHX_DATA_DIR = (
    APP_ROOT / "watchx_data"
)

WATCHX_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


class WatchXApp:

    def __init__(self, root):

        self.root = root

        self.root.title("WatchX - AI Vehicle Investigation")
        self.root.geometry("900x720")
        self.root.minsize(800, 680)

        self.root.configure(
            bg="#0b1324"
        )

        self.selected_video = None
        self.processing = False
        self.process = None

        # ====================================================
        # TOP LOGO
        # ====================================================

        top = tk.Frame(
            root,
            bg="#0b1324"
        )

        top.pack(
            fill="x",
            pady=(20, 5)
        )

        try:

            img = Image.open(
                LOGO_PATH
            ).convert("RGBA")

            img.thumbnail(
                (125, 125)
            )

            self.logo_img = ImageTk.PhotoImage(img)

            tk.Label(
                top,
                image=self.logo_img,
                bg="#0b1324"
            ).pack()

        except Exception:

            tk.Label(
                top,
                text="WatchX",
                font=("Arial", 38, "bold"),
                fg="#00ff88",
                bg="#0b1324"
            ).pack()

        # ====================================================
        # TITLE
        # ====================================================

        tk.Label(
            root,
            text="WatchX",
            font=("Arial", 34, "bold"),
            fg="#00ff88",
            bg="#0b1324"
        ).pack(
            pady=(0, 2)
        )

        tk.Label(
            root,
            text="AI Vehicle Investigation System",
            font=("Arial", 17),
            fg="white",
            bg="#0b1324"
        ).pack()

        # ====================================================
        # SELECT VIDEO BUTTON
        # ====================================================

        self.select_btn = tk.Button(
            root,
            text="SELECT INPUT VIDEO",
            command=self.select_video,
            font=("Arial", 18, "bold"),
            width=28,
            height=2,
            bg="white",
            fg="#111827",
            relief="flat",
            cursor="hand2"
        )

        self.select_btn.pack(
            pady=(30, 8)
        )

        # ====================================================
        # FILE NAME
        # ====================================================

        self.file_label = tk.Label(
            root,
            text="No video selected",
            font=("Arial", 13),
            fg="#cbd5e1",
            bg="#0b1324"
        )

        self.file_label.pack()

        # ====================================================
        # START PROCESSING BUTTON
        # ====================================================

        self.process_btn = tk.Button(
            root,
            text="START PROCESSING",
            command=self.start_processing,
            font=("Arial", 18, "bold"),
            width=28,
            height=2,
            bg="white",
            fg="#111827",
            relief="flat",
            state="disabled",
            cursor="hand2"
        )

        self.process_btn.pack(
            pady=(25, 10)
        )

        # ====================================================
        # LARGE PROGRESS TEXT
        # ====================================================

        self.progress_text = tk.Label(
            root,
            text="Ready",
            font=("Arial", 22, "bold"),
            fg="#94a3b8",
            bg="#0b1324"
        )

        self.progress_text.pack(
            pady=(10, 5)
        )

        # ====================================================
        # PROGRESS BAR
        # ====================================================

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "WatchX.Horizontal.TProgressbar",
            troughcolor="#1e293b",
            background="#00ff88",
            bordercolor="#1e293b",
            lightcolor="#00ff88",
            darkcolor="#00ff88",
            thickness=22
        )

        self.progress_bar = ttk.Progressbar(
            root,
            style="WatchX.Horizontal.TProgressbar",
            orient="horizontal",
            length=560,
            mode="determinate",
            maximum=100,
            value=0
        )

        self.progress_bar.pack(
            pady=(5, 20)
        )

        # ====================================================
        # STATUS
        # ====================================================

        self.status = tk.Label(
            root,
            text="Ready",
            font=("Arial", 13),
            fg="#94a3b8",
            bg="#0b1324"
        )

        self.status.pack(
            pady=(0, 18)
        )

        # ====================================================
        # DASHBOARD BUTTON
        # ====================================================

        self.dashboard_btn = tk.Button(
            root,
            text="OPEN DASHBOARD",
            command=self.open_dashboard,
            font=("Arial", 16, "bold"),
            width=28,
            height=2,
            bg="#00ff88",
            fg="#07111f",
            relief="flat",
            state="disabled",
            cursor="hand2"
        )

        self.dashboard_btn.pack()

    # ========================================================
    # SELECT VIDEO
    # ========================================================

    def select_video(self):

        if self.processing:
            return

        path = filedialog.askopenfilename(
            title="Select WatchX input video",
            filetypes=[
                (
                    "Video files",
                    "*.mp4 *.mov *.avi *.mkv *.MP4 *.MOV *.AVI *.MKV"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        self.selected_video = Path(path)

        self.file_label.config(
            text=self.selected_video.name,
            fg="white"
        )

        self.process_btn.config(
            state="normal",
            fg="#111827"
        )

        self.dashboard_btn.config(
            state="disabled"
        )

        self.progress_bar["value"] = 0

        self.progress_text.config(
            text="Ready to process",
            fg="#94a3b8"
        )

        self.status.config(
            text="Video selected. Click START PROCESSING.",
            fg="#00ff88"
        )

        print()
        print("==============================================")
        print("WATCHX VIDEO SELECTED")
        print("==============================================")
        print("Video:", self.selected_video)
        print("==============================================")
        print()

    # ========================================================
    # START PROCESSING
    # ========================================================

    def start_processing(self):

        if self.processing:
            return

        if not self.selected_video:

            messagebox.showwarning(
                "WatchX",
                "Please select a video first."
            )

            return

        # Use the Python OCR script during development.
        # Use the standalone OCR executable in the packaged application.
        ocr_target = OCR_EXE if getattr(sys, "frozen", False) else OCR_SCRIPT

        if not ocr_target.exists():

            messagebox.showerror(
                "WatchX",
                f"Could not find the WatchX processing engine:\n{ocr_target}"
            )

            return

        print()
        print("==============================================")
        print("WATCHX START PROCESSING")
        print("==============================================")

        self.processing = True

        self.select_btn.config(
            state="disabled"
        )

        self.process_btn.config(
            state="disabled"
        )

        self.dashboard_btn.config(
            state="disabled"
        )

        self.progress_bar["value"] = 0

        self.progress_text.config(
            text="Processing video... 0%",
            fg="#facc15"
        )

        self.status.config(
            text="WatchX AI is processing the video in the background...",
            fg="#facc15"
        )

        self.root.update_idletasks()

        print("Background processing started.")

        if getattr(sys, "frozen", False):
            print("OCR engine:", OCR_EXE)
        else:
            print("OCR script:", OCR_SCRIPT)

        print("Shared data:", WATCHX_DATA_DIR)
        print("Selected video:", self.selected_video)

        threading.Thread(
            target=self._process_worker,
            daemon=True
        ).start()

    # ========================================================
    # BACKGROUND WORKER
    # ========================================================

    def _process_worker(self):

        try:

            print()
            print("==============================================")
            print("WATCHX BACKGROUND PROCESSING")
            print("==============================================")

            # ------------------------------------------------
            # PREPARE SHARED WATCHX DATA DIRECTORY
            # ------------------------------------------------

            WATCHX_DATA_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            # The OCR engine receives the selected video directly.
            # This removes the old fixed-video/copy dependency.
            selected_video = self.selected_video.resolve()

            print(
                "WatchX shared data:",
                WATCHX_DATA_DIR.resolve()
            )

            print(
                "Selected video:",
                selected_video
            )

            # ------------------------------------------------
            # RUN OCR ENGINE
            # ------------------------------------------------

            print("Starting WatchX processing engine...")

            creation_flags = 0

            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW

            # Pass the shared data directory to the OCR engine.
            # plate_ocr.py / plate_ocr.exe will write its CSV and
            # evidence into this common location.
            process_env = os.environ.copy()
            process_env["WATCHX_DATA_DIR"] = str(
                WATCHX_DATA_DIR.resolve()
            )

            if getattr(sys, "frozen", False):

                if not OCR_EXE.exists():
                    raise FileNotFoundError(
                        "WatchX OCR executable was not found.\\n\\n"
                        f"Expected:\\n{OCR_EXE}"
                    )

                command = [
                    str(OCR_EXE),
                    str(selected_video)
                ]

                # Keep the OCR executable's own directory as its
                # working directory so its bundled models/resources
                # are resolved correctly.
                process_cwd = OCR_EXE.parent

            else:

                if not OCR_SCRIPT.exists():
                    raise FileNotFoundError(
                        "WatchX OCR script was not found.\\n\\n"
                        f"Expected:\\n{OCR_SCRIPT}"
                    )

                command = [
                    sys.executable,
                    "-u",
                    str(OCR_SCRIPT),
                    str(selected_video)
                ]

                process_cwd = BASE_DIR

            self.process = subprocess.Popen(
                command,
                cwd=str(process_cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags,
                env=process_env
            )

            # ------------------------------------------------
            # READ OUTPUT LIVE
            # ------------------------------------------------

            if self.process.stdout:

                for line in iter(
                    self.process.stdout.readline,
                    ""
                ):

                    line = line.strip()

                    if not line:
                        continue

                    # Terminal output
                    print(
                        line,
                        flush=True
                    )

                    # ----------------------------------------
                    # READ PROGRESS
                    # ----------------------------------------

                    if line.startswith("PROGRESS:"):

                        try:

                            value = line.split(
                                ":",
                                1
                            )[1].strip()

                            progress = int(
                                float(value)
                            )

                            progress = max(
                                0,
                                min(
                                    100,
                                    progress
                                )
                            )

                            # Send progress safely
                            # to Tkinter main thread.
                            self.root.after(
                                0,
                                self.update_progress,
                                progress
                            )

                        except Exception as e:

                            print(
                                "Progress error:",
                                e,
                                flush=True
                            )

            # ------------------------------------------------
            # WAIT FOR PROCESS TO FINISH
            # ------------------------------------------------

            return_code = self.process.wait()

            print()
            print(
                "WatchX processing engine finished with code:",
                return_code
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if return_code == 0:

                self.root.after(
                    0,
                    self.processing_completed
                )

            else:

                self.root.after(
                    0,
                    self.processing_failed,
                    f"WatchX processing failed.\n\n"
                    f"WatchX processing engine returned error code "
                    f"{return_code}."
                )

        except Exception as e:

            print()
            print("==============================================")
            print("WATCHX ERROR")
            print("==============================================")
            print(
                repr(e),
                flush=True
            )

            self.root.after(
                0,
                self.processing_failed,
                str(e)
            )

    # ========================================================
    # UPDATE PROGRESS ON INVESTIGATION WINDOW
    # ========================================================

    def update_progress(self, progress):

        # Update progress bar
        self.progress_bar["value"] = progress

        # Update BIG percentage text
        self.progress_text.config(
            text=f"Processing video... {progress}%",
            fg="#facc15"
        )

        # Update small status
        self.status.config(
            text="AI vehicle and number-plate detection in progress...",
            fg="#facc15"
        )

        self.root.update_idletasks()

    # ========================================================
    # PROCESSING COMPLETED
    # ========================================================

    def processing_completed(self):

        self.processing = False
        self.process = None

        # Make sure final value is exactly 100
        self.progress_bar["value"] = 100

        self.progress_text.config(
            text="100% — PROCESSING COMPLETED",
            fg="#00ff88"
        )

        self.status.config(
            text="Processing completed successfully.",
            fg="#00ff88"
        )

        self.select_btn.config(
            state="normal"
        )

        self.process_btn.config(
            state="normal"
        )

        self.dashboard_btn.config(
            state="normal"
        )

        print()
        print("==============================================")
        print("WATCHX PROCESSING COMPLETED SUCCESSFULLY")
        print("==============================================")
        print()

        messagebox.showinfo(
            "WatchX",
            "Processing completed successfully.\n\n"
            "Vehicle and number-plate records have been saved."
        )

    # ========================================================
    # PROCESSING FAILED
    # ========================================================

    def processing_failed(self, error):

        self.processing = False
        self.process = None

        self.progress_text.config(
            text="PROCESSING FAILED",
            fg="#ff6b6b"
        )

        self.status.config(
            text="An error occurred during processing.",
            fg="#ff6b6b"
        )

        self.select_btn.config(
            state="normal"
        )

        self.process_btn.config(
            state="normal"
        )

        self.dashboard_btn.config(
            state="disabled"
        )

        print()
        print("==============================================")
        print("WATCHX PROCESSING FAILED")
        print("==============================================")
        print(error)
        print()

        messagebox.showerror(
            "WatchX",
            error
        )

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    def open_dashboard(self):

        # Use dashboard.py during development.
        # Use dashboard.exe in the packaged desktop application.

        process_env = os.environ.copy()
        process_env["WATCHX_DATA_DIR"] = str(
            WATCHX_DATA_DIR.resolve()
        )

        if getattr(sys, "frozen", False):

            dashboard_target = DASHBOARD_EXE

            command = [
                str(dashboard_target)
            ]

            dashboard_cwd = DASHBOARD_EXE.parent

        else:

            dashboard_target = DASHBOARD_SCRIPT

            command = [
                sys.executable,
                str(dashboard_target)
            ]

            dashboard_cwd = BASE_DIR

        if not dashboard_target.exists():

            messagebox.showerror(
                "WatchX",
                "Could not find the WatchX dashboard.\\n\\n"
                f"Expected:\\n{dashboard_target}"
            )

            return

        try:

            print(
                "Opening dashboard:",
                dashboard_target
            )

            print(
                "Dashboard shared data:",
                WATCHX_DATA_DIR
            )

            subprocess.Popen(
                command,
                cwd=str(dashboard_cwd),
                env=process_env
            )

        except Exception as e:

            messagebox.showerror(
                "WatchX",
                str(e)
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================================")
    print("WATCHX DESKTOP STARTING")
    print("==============================================")
    print("Python:", sys.executable)
    print("Project:", BASE_DIR)
    print("Application root:", APP_ROOT)
    print(
        "OCR:",
        OCR_EXE if getattr(sys, "frozen", False)
        else OCR_SCRIPT
    )
    print("Dashboard:", DASHBOARD_EXE if getattr(sys, "frozen", False) else DASHBOARD_SCRIPT)
    print("Shared data:", WATCHX_DATA_DIR)
    print()

    root = tk.Tk()

    app = WatchXApp(root)

    root.mainloop()