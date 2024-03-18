import customtkinter as ctk
from tkinter import filedialog

from backend import manage_images
from backend import make_pdf


class ManageFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.ImageList = []
        # use text_var.set("1") to update the value
        self.TextVar = ctk.StringVar(value="0")

        self.AddButton1 = ctk.CTkButton(self, text="Add Images",
                                        fg_color=("#DB3E39", "#821D1A"), command=self.add_image)
        self.AddButton1.place(x=250, y=300)

        self.ImgCounter = ctk.CTkLabel(self, textvariable=self.TextVar, font=("Arial", 20))
        self.ImgCounter.place(x=300, y=350)

        self.ClearButton = ctk.CTkButton(self, text="Clear",
                                         fg_color=("#DB3E39", "#821D1A"), command=self.clear_images)
        self.ClearButton.place(x=250, y=400)

        self.MakePDFButton = ctk.CTkButton(self, text="Make PDF",
                                           fg_color=("#DB3E39", "#821D1A"), command=self.make_pdf)
        self.MakePDFButton.place(x=30, y=300)

    def add_image(self, file_path=None):
        if file_path is None:
            file_path = filedialog.askopenfilenames()
            self.ImageList.extend(manage_images(list(file_path)))
            self.TextVar.set(f"{len(self.ImageList)} images")

    def clear_images(self):
        self.ImageList.clear()
        self.TextVar.set("0 images")

    def make_pdf(self):
        if self.ImageList:
            if file_path := filedialog.asksaveasfilename(
                    defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")]
            ):
                self.AddButton1.configure(state="disabled")
                self.ClearButton.configure(state="disabled")
                make_pdf(file_path, self.ImageList)
                self.clear_images()
