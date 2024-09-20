import os
import threading
import urllib.request
from tkinter import filedialog, messagebox, Toplevel, Label, Button, Frame, Tk, Canvas
from PIL import Image, ImageTk
import customtkinter as ctk
from yt_dlp import YoutubeDL
import io
import webview
import ffmpeg
def search_youtube(query, api_key):
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=api_key)
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=1,
            type='video'
        ).execute()

        video_id = search_response['items'][0]['id']['videoId']
        thumbnail_url = search_response['items'][0]['snippet']['thumbnails']['high']['url']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        video_title = search_response['items'][0]['snippet']['title']

        video_details = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        duration = video_details['items'][0]['contentDetails']['duration']
        video_length = parse_duration(duration)

        return video_link, thumbnail_url, video_title, video_length

    except Exception as e:
        print(f"Error searching YouTube: {str(e)}")
        return None, None, None, None

def parse_duration(duration):
    import re
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def jls_extract_def():
    return (800, 450)

def show_thumbnail(thumbnail_url):
    try:
        with urllib.request.urlopen(thumbnail_url) as url:
            raw_data = url.read()

        image = Image.open(io.BytesIO(raw_data))

        image = image.resize(jls_extract_def(), Image.LANCZOS)

        ctk_image = ImageTk.PhotoImage(image)

        thumbnail_label.configure(image=ctk_image)
        thumbnail_label.image = ctk_image

    except Exception as e:
        print(f"Error displaying thumbnail: {str(e)}")

def show_progress(d):
    if d['status'] == 'downloading':
        total_size = d.get('total_bytes') or d.get('total_bytes_estimate')
        bytes_downloaded = d.get('downloaded_bytes', 0)
        percentage = bytes_downloaded / total_size * 100

        progress_var.set(percentage)
        progress_bar.set(percentage)
        progress_label.configure(text=f"Download progress: {percentage:.2f}%")
        root.update_idletasks()

def download_youtube_audio(url, save_path, output_format):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'progress_hooks': [show_progress],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return False

def download_youtube_video(url, save_path, resolution, output_format):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'progress_hooks': [show_progress],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

def custom_confirm_dialog(video_title, thumbnail_url, video_length, download_callback):
    confirm_dialog = Toplevel(root)
    confirm_dialog.title("Confirmation")

    confirm_label = Label(confirm_dialog, text=f"Do you want to download '{video_title}'?\nDuration: {video_length}")
    confirm_label.pack(pady=10)

    try:
        with urllib.request.urlopen(thumbnail_url) as url:
            raw_data = url.read()

        thumbnail_image = Image.open(io.BytesIO(raw_data))

        thumbnail_image = thumbnail_image.resize((400, 225), Image.LANCZOS)

        thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)

        thumbnail_label = Label(confirm_dialog, image=thumbnail_photo)
        thumbnail_label.image = thumbnail_photo
        thumbnail_label.pack(pady=10)

    except Exception as e:
        print(f"Error displaying thumbnail in confirmation: {str(e)}")

    button_frame = Frame(confirm_dialog)
    button_frame.pack(pady=10)

    yes_button = Button(button_frame, text="Yes", command=lambda: [download_callback(), confirm_dialog.destroy()])
    yes_button.grid(row=0, column=0, padx=10)

    no_button = Button(button_frame, text="No", command=confirm_dialog.destroy)
    no_button.grid(row=0, column=1, padx=10)

def download():
    api_key = "AIzaSyBLXw0XmHNsgOuPqN2ZbpFWNvEAtuGTG2o"
    search_query = query_entry.get()
    video_url = url_entry.get()
    output_format = format_var.get().upper()
    save_path = save_path_entry.get()
    resolution = resolution_var.get().replace('p', '')

    if not search_query and not video_url:
        messagebox.showwarning("Input Error", "Please provide either a video title or a URL.")
        return

    if not output_format or not save_path:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if search_query:
        yt_url, thumbnail_url, video_title, video_length = search_youtube(search_query, api_key)
    else:
        yt_url = video_url
        video_title = "Selected Video"
        video_length = "Unknown"
        thumbnail_url = ""

    if yt_url is None:
        messagebox.showerror("Error", "Error searching YouTube.")
        return

    if thumbnail_url:
        show_thumbnail(thumbnail_url)

    def download_in_thread(url, save_path, resolution, output_format):
        if output_format == "MP3":
            success = download_youtube_audio(url, save_path, output_format)
            if not success:
                messagebox.showerror("Error", "Error downloading audio.")
                return
        elif output_format == "MP4":
            success = download_youtube_video(url, save_path, resolution, output_format)
            if not success:
                messagebox.showerror("Error", f"Error downloading video in {resolution} resolution.")
                return
        else:
            messagebox.showerror("Error", "Invalid output format. Please enter MP3 or MP4.")
            return

        messagebox.showinfo("Success", "Download process completed successfully.")
        reset_gui()

    custom_confirm_dialog(video_title, thumbnail_url, video_length,
                          lambda: threading.Thread(target=download_in_thread, args=(yt_url, save_path, resolution, output_format)).start())

def browse_save_path():
    save_path = filedialog.askdirectory()
    if save_path:
        save_path_entry.delete(0, "end")
        save_path_entry.insert(0, save_path)

def quit_with_confirmation():
    confirm = messagebox.askyesno("Confirmation", "Are you sure you want to quit?")
    if confirm:
        root.destroy()

def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

def reset_gui():
    query_entry.delete(0, 'end')
    url_entry.delete(0, 'end')
    format_var.set("MP4")
    resolution_var.set("720")
    save_path_entry.delete(0, 'end')
    progress_var.set(0)
    progress_bar.set(0)
    progress_label.configure(text="")
    thumbnail_label.configure(image="")
    thumbnail_label.image = None

def browse_youtube():
    def on_closing():
        webview_window.destroy()
        root.deiconify()

    root.withdraw()
    webview_window = webview.create_window('Browse YouTube', 'https://www.youtube.com')
    webview_window.events.closed += on_closing
    webview.start()

# GUI setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("YouTube Video Downloader")
root.geometry("1200x800")

def resize_image(event):
    new_width = event.width
    new_height = event.height
    image = bg_image.resize((new_width, new_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(image)
    bg_canvas.create_image(0, 0, image=bg_photo, anchor='nw')
    bg_canvas.image = bg_photo

bg_image = Image.open("22.jpg")
bg_canvas = Canvas(root, width=1200, height=800)
bg_canvas.pack(fill="both", expand=True)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_canvas.create_image(0, 0, image=bg_photo, anchor='nw')

bg_canvas.bind("<Configure>", resize_image)

frame = ctk.CTkFrame(root)
frame.place(relx=0.5, rely=0.5, anchor='center')

header_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")
label_font = ctk.CTkFont(family="Helvetica", size=14)
button_font = ctk.CTkFont(family="Helvetica", size=12)

query_label = ctk.CTkLabel(frame, text="Enter video title:", anchor="w", font=label_font)
query_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

query_entry = ctk.CTkEntry(frame, width=100, font=label_font)
query_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

url_label = ctk.CTkLabel(frame, text="Enter YouTube URL:", anchor="w", font=label_font)
url_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

url_entry = ctk.CTkEntry(frame, width=100, font=label_font)
url_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

format_var = ctk.StringVar(value="MP4")

mp4_radio = ctk.CTkRadioButton(frame, text="MP4", variable=format_var, value="MP4", font=label_font)
mp4_radio.grid(row=2, column=1, padx=10, pady=5, sticky="w")

mp3_radio = ctk.CTkRadioButton(frame, text="MP3", variable=format_var, value="MP3", font=label_font)
mp3_radio.grid(row=2, column=2, padx=10, pady=5, sticky="w")

format_label = ctk.CTkLabel(frame, text="Select Format:", anchor="w", font=label_font)
format_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

resolution_label = ctk.CTkLabel(frame, text="Select video resolution (MP4 only):", anchor="w", font=label_font)
resolution_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

resolution_var = ctk.StringVar(value="720")
resolution_options = ["320p", "480p", "720p", "1080p", "4K"]
resolution_dropdown = ctk.CTkOptionMenu(frame, variable=resolution_var, values=resolution_options, font=label_font)
resolution_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

save_path_label = ctk.CTkLabel(frame, text="Select save path:", anchor="w", font=label_font)
save_path_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

save_path_entry = ctk.CTkEntry(frame, width=100, font=label_font)
save_path_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

browse_button = ctk.CTkButton(frame, text="Browse", command=browse_save_path, font=button_font)
browse_button.grid(row=4, column=3, padx=10, pady=10, sticky="w")

download_button = ctk.CTkButton(frame, text="Download", command=download, width=browse_button.cget("width"), font=button_font)
download_button.grid(row=5, column=0, columnspan=4, padx=10, pady=20, sticky="ew")

browse_youtube_button = ctk.CTkButton(frame, text="Browse YouTube", command=browse_youtube, width=browse_button.cget("width"), font=button_font)
browse_youtube_button.grid(row=0, column=3, padx=10, pady=10, sticky="w")

thumbnail_label = ctk.CTkLabel(frame, text="", font=label_font)
thumbnail_label.grid(row=0, column=4, rowspan=6, padx=20, pady=20, sticky="ns")
thumbnail_label.configure(width=800, height=450)

progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(frame, variable=progress_var)
progress_bar.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

progress_label = ctk.CTkLabel(frame, text="", font=label_font)
progress_label.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", lambda event: quit_with_confirmation())

root.mainloop()
