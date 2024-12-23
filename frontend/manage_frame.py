import threading

import customtkinter as ctk
from tkinter import filedialog
import os
from backend import manage_images, pdfmaker_thread
import tkinter as tk


class ManageFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.ImageList = []
        self.step_size = 0
        self.images_last_open_directory = None
        self.pdf_last_open_directory = None
        main_label = ctk.CTkLabel(self, text="Manhwa Maker", font=("Comic Sans MS", 25))
        main_label.place(x=120, y=120)
        # use text_var.set("1") to update the value
        self.TextVar = ctk.StringVar(value="No Images ")

        self.AddButton1 = ctk.CTkButton(self, text="Add Images",
                                        fg_color=("#DB3E39", "#821D1A"), command=self.add_image)
        self.AddButton1.place(x=250, y=300)

        self.AddButton2 = ctk.CTkButton(self, text="Add Folder",
                                        fg_color=("#DB3E39", "#821D1A"), command=self.add_image_folder)
        self.AddButton2.place(x=250, y=350)
        self.ImgCounter = ctk.CTkLabel(self, textvariable=self.TextVar, font=("Arial", 17))
        self.ImgCounter.place(x=270, y=400)

        self.ClearButton = ctk.CTkButton(self, text="Clear",
                                         fg_color=("#DB3E39", "#821D1A"), command=self.clear_images)
        self.ClearButton.place(x=250, y=450)

        self.MakePDFButton = ctk.CTkButton(self, text="Make PDF",
                                           fg_color=("#DB3E39", "#821D1A"), command=self.make_pdf)
        self.MakePDFButton.place(x=30, y=300)

        self.SavingPDFLabel = ctk.CTkLabel(self, text="Saving PDF...", font=("Arial", 12))
        self.SavingPDFLabel.place(x=170, y=220)
        self.SavingPDFLabel.configure(state="disabled")
        self.SavingPDFLabel.lower()

        self.ProgressBar = ctk.CTkProgressBar(self, width=200, height=20)
        self.ProgressBar.set(0)
        self.ProgressBar.place(x=110, y=250)

    def disable_buttons(self):
        self._change_button_state("disabled")

    def enable_buttons(self):
        self._change_button_state("normal")

    def _change_button_state(self, state):
        self.AddButton1.configure(state=state)
        self.AddButton2.configure(state=state)
        self.ClearButton.configure(state=state)
        self.MakePDFButton.configure(state=state)

    def clear_images(self):
        self.ImageList.clear()
        self.TextVar.set("0 images")

    def image_progression_step(self):
        if self.ProgressBar.get() == self.step_size:
            self.SavingPDFLabel.lift()
        self.ProgressBar.step()

    def pdf_saved_callback(self):
        self.enable_buttons()
        self.clear_images()
        self.SavingPDFLabel.lower()
        self.ProgressBar.set(0)

    def add_image(self, file_path=None):
        self.disable_buttons()

        if file_path is None:
            if self.images_last_open_directory is None:
                file_path = filedialog.askopenfilenames()
            else:
                file_path = filedialog.askopenfilenames(initialdir=self.images_last_open_directory)
            if file_path:
                self.images_last_open_directory = '/'.join(file_path[0].split('/')[:-1])
            threading.Thread(target=self.manage_and_extend_images, args=(list(file_path),)).start()

    def add_image_folder(self):
        self.disable_buttons()
        folder_path = filedialog.askdirectory()
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        image_paths = []
        for root, dirs, files in os.walk(folder_path):
            dirs.sort(key=lambda x: int(''.join(filter(str.isdigit, str(x)))))
            files.sort(key=lambda x: int(''.join(filter(str.isdigit, str(x)))))
            image_paths.extend(
                os.path.join(root, file)
                for file in files
                if file.lower().endswith(image_extensions)
            )
        threading.Thread(target=self.manage_and_extend_images, args=(list(image_paths),)).start()

    def manage_and_extend_images(self, file_paths):
        images_list = manage_images(file_paths)
        self.ImageList.extend(images_list)
        self.TextVar.set(f"{len(self.ImageList)} images")
        self.enable_buttons()
        self.step_size = 1 / len(self.ImageList)
        self.ProgressBar.configure(determinate_speed=self.step_size * 50)

    def make_pdf(self):
        if self.ImageList:
            if self.pdf_last_open_directory is None:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")]
                )
            else:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")], initialdir=self.pdf_last_open_directory
                )
            if file_path:
                self.pdf_last_open_directory = '/'.join(file_path[0].split('/')[:-1])
                self.disable_buttons()
                threading.Thread(target=pdfmaker_thread,
                                 args=(file_path, self.ImageList, self.pdf_saved_callback,
                                       self.image_progression_step)).start()
