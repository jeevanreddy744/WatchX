import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os


def select_video():
    video_path = filedialog.askopenfilename(
        title="Select Traffic Video",
        filetypes=[
            ("Video files", "*.mp4 *.MP4 *.mov *.MOV *.avi *.AVI *.mkv *.MKV"),
            ("All files", "*.*")
        ]
    )

    if not video_path:
        return

    selected_video.config(text=os.path.basename(video_path))

    start_button.config(state="normal")
    start_button.video_path = video_path


def start_processing():
    video_path = start_button.video_path

    start_button.config(state="disabled")
    select_button.config(state="disabled")
    status_label.config(text="WatchX is processing the video...")

    root.update()

    try:
        subprocess.run(
            [sys.executable, "plate_ocr.py", video_path],
            check=True
        )

        status_label.config(
            text="Processing completed successfully!"
        )

        messagebox.showinfo(
            "WatchX",
            "Video processing completed successfully.\n\n"
            "Vehicle records have been saved."
        )

    except subprocess.CalledProcessError:
        status_label.config(
            text="Processing failed."
        )

        messagebox.showerror(
            "WatchX Error",
            "WatchX could not process the video."
        )

    finally:
        start_button.config(state="normal")
        select_button.config(state="normal")


root = tk.Tk()

root.title("WatchX - AI Vehicle Investigation")
root.geometry("700x450")
root.minsize(600, 400)
root.configure(bg="#111827")


title = tk.Label(
    root,
    text="WatchX",
    font=("Arial", 32, "bold"),
    fg="#00ff88",
    bg="#111827"
)
title.pack(pady=(60, 5))


subtitle = tk.Label(
    root,
    text="AI Vehicle Investigation System",
    font=("Arial", 16),
    fg="white",
    bg="#111827"
)
subtitle.pack(pady=(0, 40))


select_button = tk.Button(
    root,
    text="SELECT INPUT VIDEO",
    font=("Arial", 14, "bold"),
    width=25,
    height=2,
    command=select_video
)
select_button.pack(pady=10)


selected_video = tk.Label(
    root,
    text="No video selected",
    font=("Arial", 11),
    fg="#cccccc",
    bg="#111827"
)
selected_video.pack(pady=10)


start_button = tk.Button(
    root,
    text="START PROCESSING",
    font=("Arial", 14, "bold"),
    width=25,
    height=2,
    state="disabled",
    command=start_processing
)
start_button.pack(pady=20)


status_label = tk.Label(
    root,
    text="Select a traffic video to begin",
    font=("Arial", 11),
    fg="#00ff88",
    bg="#111827"
)
status_label.pack(pady=20)


root.mainloop()