import customtkinter as ctk
from tkinter import filedialog
import main as cli_main
import threading
import sys
import io
from types import SimpleNamespace

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KDP Image Processing Tool")
        self.geometry("850x650")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_view.add("Resize")
        self.tab_view.add("Upscale")
        self.tab_view.add("SVG")
        self.tab_view.add("PDF")
        self.tab_view.add("Collage")

        self.setup_resize_tab()
        self.setup_upscale_tab()
        self.setup_svg_tab()
        self.setup_pdf_tab()
        self.setup_collage_tab()

        self.status_textbox = ctk.CTkTextbox(main_frame, height=200)
        self.status_textbox.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.log("Welcome! Ready to process your images.")

    def log(self, message):
        """Safely logs a message to the status textbox from any thread."""
        if not isinstance(message, str):
            message = str(message)
        self.status_textbox.insert("end", message + "\n")
        self.status_textbox.see("end")

    def _browse_file(self, entry_widget):
        path = filedialog.askopenfilename()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _browse_directory(self, entry_widget):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _browse_save_as(self, entry_widget):
        path = filedialog.asksaveasfilename()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _create_io_widgets(self, parent, is_dir_input=False, is_dir_output=False):
        io_frame = ctk.CTkFrame(parent)

        input_label = "Input Directory:" if is_dir_input else "Input File:"
        output_label = "Output Directory:" if is_dir_output else "Output File:"

        ctk.CTkLabel(io_frame, text=input_label).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        input_entry = ctk.CTkEntry(io_frame, width=450)
        input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        browse_input_func = self._browse_directory if is_dir_input else self._browse_file
        input_browse_btn = ctk.CTkButton(io_frame, text="Browse...", command=lambda: browse_input_func(input_entry))
        input_browse_btn.grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(io_frame, text=output_label).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        output_entry = ctk.CTkEntry(io_frame, width=450)
        output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        browse_output_func = self._browse_directory if is_dir_output else self._browse_save_as
        output_browse_btn = ctk.CTkButton(io_frame, text="Browse...", command=lambda: browse_output_func(output_entry))
        output_browse_btn.grid(row=1, column=2, padx=5, pady=5)

        io_frame.column_configure(1, weight=1)
        return io_frame, input_entry, output_entry

    def _start_task(self, worker_func):
        """Starts a new thread for a given worker function to keep the GUI responsive."""
        self.log("Starting process...")
        thread = threading.Thread(target=worker_func, daemon=True)
        thread.start()

    def _process_command_worker(self, args):
        """Generic worker to run a command and log its output."""
        # Redirect stdout to capture print statements from the backend
        old_stdout = sys.stdout
        sys.stdout = redirected_output = io.StringIO()

        try:
            cli_main.run_command(args)
        except Exception as e:
            print(f"An unexpected error occurred: {e}") # also redirect this
        finally:
            sys.stdout = old_stdout # Restore stdout
            # Schedule the GUI update on the main thread
            self.after(0, self.log, redirected_output.getvalue())
            self.after(0, self.log, "...Process finished.")

    def _start_resize(self, input_path, output_path, size, is_batch):
        args = SimpleNamespace(
            command='resize',
            input=None if is_batch else input_path,
            directory=input_path if is_batch else None,
            output=output_path,
            size=size
        )
        self._start_task(lambda: self._process_command_worker(args))

    def _start_upscale(self, input_path, output_path, factor, is_batch):
        args = SimpleNamespace(
            command='upscale',
            input=None if is_batch else input_path,
            directory=input_path if is_batch else None,
            output=output_path,
            factor=float(factor)
        )
        self._start_task(lambda: self._process_command_worker(args))

    def _start_svg(self, input_path, output_path, preprocess, is_batch):
        args = SimpleNamespace(
            command='svg',
            input=None if is_batch else input_path,
            directory=input_path if is_batch else None,
            output=output_path,
            preprocessing='threshold' if preprocess else None
        )
        self._start_task(lambda: self._process_command_worker(args))

    def _start_pdf(self, input_path, output_path, size, is_batch):
        args = SimpleNamespace(
            command='pdf',
            input=None if is_batch else input_path,
            directory=input_path if is_batch else None,
            output=output_path,
            size=size
        )
        self._start_task(lambda: self._process_command_worker(args))

    def _start_collage(self, input_dir, output_path, size, grid, padding):
        args = SimpleNamespace(
            command='collage',
            input_dir=input_dir,
            output=output_path,
            size=size,
            grid=grid,
            padding=int(padding)
        )
        self._start_task(lambda: self._process_command_worker(args))

    def _create_batch_toggle_tab(self, tab_name, setup_content_func):
        tab = self.tab_view.tab(tab_name)
        is_batch = ctk.BooleanVar(value=False)

        def toggle_mode():
            # Clear all widgets from the tab before redrawing
            for widget in tab.winfo_children():
                widget.destroy()
            # Redraw the content with the new mode
            setup_content_func(tab, is_batch.get(), is_batch)

        setup_content_func(tab, is_batch.get(), is_batch)

    def setup_resize_tab(self):
        self._create_batch_toggle_tab("Resize", self._setup_resize_tab_content)

    def _setup_resize_tab_content(self, tab, is_dir, is_batch_var):
        ctk.CTkCheckBox(tab, text="Batch Mode (Process Directory)", variable=is_batch_var, command=lambda: self._create_batch_toggle_tab("Resize", self._setup_resize_tab_content)).pack(anchor="w", padx=10, pady=5)
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir)
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        ctk.CTkLabel(options_frame, text="Page Size:").pack(side="left", padx=10)
        size_menu = ctk.CTkOptionMenu(options_frame, values=list(cli_main.PAGE_SIZES_IN.keys()))
        size_menu.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start Resize", font=("", 16), command=lambda: self._start_resize(input_entry.get(), output_entry.get(), size_menu.get(), is_batch_var.get())).pack(pady=20)

    def setup_upscale_tab(self):
        self._create_batch_toggle_tab("Upscale", self._setup_upscale_tab_content)

    def _setup_upscale_tab_content(self, tab, is_dir, is_batch_var):
        ctk.CTkCheckBox(tab, text="Batch Mode (Process Directory)", variable=is_batch_var, command=lambda: self._create_batch_toggle_tab("Upscale", self._setup_upscale_tab_content)).pack(anchor="w", padx=10, pady=5)
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir)
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        ctk.CTkLabel(options_frame, text="Scale Factor:").pack(side="left", padx=10)
        factor_entry = ctk.CTkEntry(options_frame, width=80)
        factor_entry.insert(0, "2.0")
        factor_entry.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start Upscale", font=("", 16), command=lambda: self._start_upscale(input_entry.get(), output_entry.get(), factor_entry.get(), is_batch_var.get())).pack(pady=20)

    def setup_svg_tab(self):
        self._create_batch_toggle_tab("SVG", self._setup_svg_tab_content)

    def _setup_svg_tab_content(self, tab, is_dir, is_batch_var):
        ctk.CTkCheckBox(tab, text="Batch Mode (Process Directory)", variable=is_batch_var, command=lambda: self._create_batch_toggle_tab("SVG", self._setup_svg_tab_content)).pack(anchor="w", padx=10, pady=5)
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir)
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        preprocess_check = ctk.CTkCheckBox(options_frame, text="Apply B&W Threshold Preprocessing")
        preprocess_check.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start SVG Conversion", font=("", 16), command=lambda: self._start_svg(input_entry.get(), output_entry.get(), preprocess_check.get(), is_batch_var.get())).pack(pady=20)

    def setup_pdf_tab(self):
        self._create_batch_toggle_tab("PDF", self._setup_pdf_tab_content)

    def _setup_pdf_tab_content(self, tab, is_dir, is_batch_var):
        ctk.CTkCheckBox(tab, text="Batch Mode (Process Directory)", variable=is_batch_var, command=lambda: self._create_batch_toggle_tab("PDF", self._setup_pdf_tab_content)).pack(anchor="w", padx=10, pady=5)
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir)
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        ctk.CTkLabel(options_frame, text="Page Size:").pack(side="left", padx=10)
        size_menu = ctk.CTkOptionMenu(options_frame, values=list(cli_main.PAGE_SIZES_IN.keys()))
        size_menu.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start PDF Creation", font=("", 16), command=lambda: self._start_pdf(input_entry.get(), output_entry.get(), size_menu.get(), is_batch_var.get())).pack(pady=20)

    def setup_collage_tab(self):
        tab = self.tab_view.tab("Collage")
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=True, is_dir_output=False)
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        ctk.CTkLabel(options_frame, text="Page Size:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        size_menu = ctk.CTkOptionMenu(options_frame, values=list(cli_main.PAGE_SIZES_IN.keys()))
        size_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(options_frame, text="Grid (e.g., 3x4):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        grid_entry = ctk.CTkEntry(options_frame)
        grid_entry.insert(0, "3x4")
        grid_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(options_frame, text="Padding (px):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        padding_entry = ctk.CTkEntry(options_frame)
        padding_entry.insert(0, "10")
        padding_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkButton(tab, text="Create Collage PDF", font=("", 16), command=lambda: self._start_collage(input_entry.get(), output_entry.get(), size_menu.get(), grid_entry.get(), padding_entry.get())).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
