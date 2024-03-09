if __name__ == "__main__":

    import customtkinter as ctk  # Assuming ctk is an alias for a custom Tkinter module

    ctk.set_appearance_mode("Dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    app = ctk.CTk()
    app.geometry("400x600")  # Adjust the width to accommodate two tables
    app.title("Manhwa maker")
    frame = ctk.CTkFrame(app)
    AddButton_ctk = ctk.CTkButton(frame, text="Add Images", fg_color=("#DB3E39", "#821D1A"))  # This button does nothing when pressed
    AddButton_ctk.place(x=250, y=120)
    frame.pack(side="left", fill="both", expand=True)
    ctk.set_default_color_theme("dark-blue")

    app.mainloop()  # Start the application
