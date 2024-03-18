from frontend.manage_frame import ManageFrame

if __name__ == "__main__":
    import customtkinter as ctk

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("400x500")
    app.title("Manhwa maker")

    main_frame = ctk.CTkFrame(app)
    main_frame.pack(side="left", fill="both", expand=True)

    # Create an instance of ManageFrame and add it to the main_frame
    manage_frame = ManageFrame(main_frame)
    manage_frame.pack(fill="both", expand=True)
    ctk.set_default_color_theme("dark-blue")

    app.mainloop()
