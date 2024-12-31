import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ffpyplayer.player import MediaPlayer
import threading
from PIL import Image, ImageTk

class VideoPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Player")
        self.master.configure(bg='black')  # Set background color of the main window to black

        # Create a larger dropdown menu with increased font size
        self.video_selector = ttk.Combobox(master, values=["Manjummel Boys 1.mp4", "Manjummel Boys 2.mp4", "Manjummel Boys 3.mp4"], width=40, height=30, font=('Arial', 22))  # Adjust width and height as desired
        self.video_selector.set("Select a video")
        self.video_selector.bind("<<ComboboxSelected>>", self.on_select)
        self.video_selector.place(relx=0.5, rely=0.1, anchor=tk.CENTER)  # Adjust position using relative coordinates

        # Create frame for buttons
        button_frame = tk.Frame(master, bg='black')
        button_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # Button configurations
        button_config = {
            'bg': 'black',
            'fg': 'white',
            'width': 12,  # Increase the width of the buttons
            'height': 1,  # Increase the height of the buttons
            'font': ('Arial', 21, 'bold')  # Change font size and make it bold
        }

        # Create Browse button with color, size, and font
        button_config_browse = button_config.copy()
        button_config_browse['bg'] = 'orange'  # Change color to orange
        self.browse_button = tk.Button(button_frame, text="Browse", command=self.browse_video, **button_config_browse)
        self.browse_button.pack(side=tk.LEFT, padx=10)

        # Create Start button with color, size, and font
        button_config_start = button_config.copy()
        button_config_start['bg'] = 'green'  # Change color to green
        self.start_button = tk.Button(button_frame, text="Start", command=self.start_video, **button_config_start)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Create Pause button with color, size, and font
        button_config_pause = button_config.copy()
        button_config_pause['bg'] = 'blue'  # Change color to blue
        self.pause_button = tk.Button(button_frame, text="Pause", command=self.pause_video, **button_config_pause)
        self.pause_button.pack(side=tk.LEFT, padx=10)

        # Create Stop button with color, size, and font
        button_config_stop = button_config.copy()
        button_config_stop['bg'] = 'red'  # Change color to red
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_video, **button_config_stop)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Create a label to display the video
        self.video_label = tk.Label(master, bg='black')
        self.video_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Adjust position using relative coordinates

        self.media_player = None
        self.video_thread = None
        self.stop_event = threading.Event()

        # Set the desired size for the video
        self.video_width = 800  # Desired width of the video
        self.video_height = 450  # Desired height of the video

        self.selected_video = None

    def on_select(self, event):
        self.selected_video = self.video_selector.get()

    def browse_video(self):
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi")])
        if video_path:
            self.video_selector.set(video_path)
            self.selected_video = video_path

    def start_video(self):
        if self.media_player and self.media_player.get_pause():
            self.media_player.set_pause(False)
        else:
            if self.selected_video:
                self.stop_video()  # Stop any currently playing video
                self.video_thread = threading.Thread(target=self.play_video, args=(self.selected_video,))
                self.video_thread.start()

    def play_video(self, video_path):
        self.stop_event.clear()
        self.media_player = MediaPlayer(video_path)
        self.update_frame()

    def update_frame(self):
        if self.stop_event.is_set():
            return

        frame, val = self.media_player.get_frame()
        if val == 'eof':
            self.stop_video()
            return

        if frame is not None:
            img, t = frame
            img_array = img.to_bytearray()[0]
            img = Image.frombuffer('RGB', (img.get_size()[0], img.get_size()[1]), img_array, 'raw', 'RGB', 0, 1)

            # Resize the frame
            img = img.resize((self.video_width, self.video_height), Image.LANCZOS)

            img_tk = ImageTk.PhotoImage(img)
            self.video_label.config(image=img_tk)
            self.video_label.image = img_tk

        # Schedule the next frame update
        if not self.stop_event.is_set():
            self.master.after(int(val * 1000), self.update_frame)

    def pause_video(self):
        if self.media_player:
            self.media_player.set_pause(True)

    def stop_video(self):
        if self.media_player:
            self.stop_event.set()
            self.media_player.close_player()
            self.media_player = None
            self.video_label.config(image='')

    def __del__(self):
        self.stop_video()

# Create the main window
root = tk.Tk()
video_player = VideoPlayer(root)
root.mainloop()
