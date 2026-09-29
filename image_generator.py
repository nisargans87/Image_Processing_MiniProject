import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# Global variables
image = None
gray_3ch = None
edges_3ch = None
is_running = False

# Convert image
def convert_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(img))

def show_image(img):
    img_tk = convert_img(img)
    panel.config(image=img_tk)
    panel.image = img_tk

# Popup
def show_popup(msg):
    popup.config(text=msg)
    popup.place(relx=0.5, rely=0.12, anchor="n")
    root.after(2000, lambda: popup.place_forget())

# Upload
def upload_image():
    global image, gray_3ch, edges_3ch

    path = filedialog.askopenfilename()
    if not path:
        return

    image = cv2.imread(path)
    image = cv2.resize(image, (500, 500))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(gray, 100, 200)

    gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    show_image(image)
    enable_buttons()
    show_popup("Image Uploaded ✔")

# Enable buttons
def enable_buttons():
    for b in action_buttons:
        b.config(state="normal")

def disable_buttons():
    for b in action_buttons:
        b.config(state="disabled")

# Basic views
def show_original():
    show_image(image)
    show_popup("Original")

def show_gray():
    show_image(gray_3ch)
    show_popup("Grayscale")

def show_edges():
    show_image(edges_3ch)
    show_popup("Edges")

# 📸 Filters
def snapchat_filter():
    img = cv2.bilateralFilter(image, 9, 75, 75)
    img = cv2.convertScaleAbs(img, alpha=1.2, beta=30)
    show_image(img)
    show_popup("Snapchat Filter 📸")

def insta_warm():
    img = image.astype(np.float32)
    img[:,:,2] += 40
    img[:,:,1] += 20
    img = np.clip(img, 0, 255).astype(np.uint8)
    show_image(img)
    show_popup("Instagram Warm 🌈")

def insta_bw():
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bw = cv2.convertScaleAbs(gray, alpha=1.5, beta=20)
    show_image(cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR))
    show_popup("B&W 🖤")

def cool_filter():
    img = image.astype(np.float32)
    img[:,:,0] += 40
    img = np.clip(img, 0, 255).astype(np.uint8)
    show_image(img)
    show_popup("Cool Tone 💙")

# 🧠 3D Model
def show_3d():
    global is_running
    if image is None or is_running:
        return

    is_running = True
    show_popup("Generating 3D...")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    height_map = (gray * 0.6 + edges * 0.4) / 255.0

    x = np.linspace(0, 1, height_map.shape[1])
    y = np.linspace(0, 1, height_map.shape[0])
    x, y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, projection='3d')

    angle = 0

    def animate():
        nonlocal angle
        global is_running

        if not is_running:
            plt.close(fig)
            show_popup("Ready ✔")
            return

        ax.clear()
        ax.plot_surface(x, y, height_map, cmap='plasma')
        ax.axis('off')
        ax.view_init(30, angle)

        fig.canvas.draw()
        img_3d = np.asarray(fig.canvas.buffer_rgba())
        img_3d = cv2.cvtColor(img_3d, cv2.COLOR_RGBA2BGR)

        show_image(img_3d)

        angle += 10
        root.after(100, animate)

    animate()

def stop_3d():
    global is_running
    is_running = False
    show_popup("3D Stopped")

# 🎁 Sticker (FINAL)
def create_sticker():
    if image is None:
        return

    mask = np.zeros((500, 500), dtype=np.uint8)
    cv2.circle(mask, (250, 250), 200, 255, -1)

    result = cv2.bitwise_and(image, image, mask=mask)

    bg = np.ones_like(image) * 255
    inv = cv2.bitwise_not(mask)
    bg = cv2.bitwise_and(bg, bg, mask=inv)

    final = cv2.add(result, bg)

    border_color = (180,105,255)
    framed = cv2.copyMakeBorder(final, 40, 80, 40, 40,
                                cv2.BORDER_CONSTANT,
                                value=border_color)

    text = "Thank You, Visit Again"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.2
    thickness = 3

    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    x = (framed.shape[1] - tw) // 2
    y = framed.shape[0] - 30

    # Background box
    cv2.rectangle(framed,
                  (x-10, y-th-10),
                  (x+tw+10, y+10),
                  (255,182,193),
                  -1)

    cv2.putText(framed, text, (x, y),
                font, scale, (147,20,255),
                thickness, cv2.LINE_AA)

    cv2.imwrite("sticker.png", framed)
    show_popup("Sticker Saved 🎁")

# Button style
def create_button(frame, text, command):
    btn = tk.Button(frame, text=text, command=command,
                    font=("Comic Sans MS", 11, "bold"),
                    bg="#ffb6c1", fg="black",
                    width=22, height=2, bd=0)
    btn.pack(pady=6)
    return btn

# GUI
root = tk.Tk()
root.title("Yours Image Processor")
root.geometry("1100x650")

# Background
bg = Image.open("rose_bg.jpg").resize((2600,1100))
bg_photo = ImageTk.PhotoImage(bg)
tk.Label(root, image=bg_photo).place(x=0,y=0,relwidth=1,relheight=1)

# Sidebar
sidebar = tk.Frame(root, bg="#ffe4e1", width=260)
sidebar.place(x=0,y=0,height=1000)

tk.Label(sidebar, text="🌸Image Tools",
         font=("Comic Sans MS",18,"bold"),
         fg="#d63384", bg="#ffe4e1").pack(pady=20)

create_button(sidebar,"Upload Image",upload_image)
btn_original=create_button(sidebar,"Original",show_original)
btn_gray=create_button(sidebar,"Grayscale",show_gray)
btn_edges=create_button(sidebar,"Edges",show_edges)

# Filters
btn_snap=create_button(sidebar,"Snapchat Filter",snapchat_filter)
btn_warm=create_button(sidebar,"Instagram Warm",insta_warm)
btn_bw=create_button(sidebar,"B&W",insta_bw)
btn_cool=create_button(sidebar,"Cool Tone",cool_filter)

btn_3d=create_button(sidebar,"Generate 3D",show_3d)
btn_stop=create_button(sidebar,"Stop 3D",stop_3d)
btn_sticker=create_button(sidebar,"Create Sticker",create_sticker)
create_button(sidebar,"Exit",root.quit)

action_buttons=[btn_original,btn_gray,btn_edges,
                btn_snap,btn_warm,btn_bw,btn_cool,
                btn_3d,btn_stop,btn_sticker]
disable_buttons()

# Main area
main=tk.Frame(root,bg="#fff0f5")
main.place(x=260,y=0,width=840,height=650)

tk.Label(main,text="I am yours Image Processor 💖",
         font=("Comic Sans MS",28,"bold"),
         fg="#ff1493",bg="#fff0f5").pack(pady=20)

panel=tk.Label(main,bg="#fff0f5")
panel.pack(expand=True)

popup=tk.Label(main,font=("Comic Sans MS",12,"bold"),
               bg="#ff69b4",fg="white",padx=20,pady=5)

root.mainloop()