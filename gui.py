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
        self.geometry("900x700")

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
        self.tab_view.add("Pipeline")
        self.tab_view.add("Help / About") # New Tab

        self.setup_resize_tab()
        self.setup_upscale_tab()
        self.setup_svg_tab()
        self.setup_pdf_tab()
        self.setup_collage_tab()
        self.setup_pipeline_tab()
        self.setup_help_tab() # New Setup Method

        self.status_textbox = ctk.CTkTextbox(main_frame, height=200)
        self.status_textbox.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.log("Welcome! Ready to process your images.")

    # ... (All helper and backend methods like log, _browse_file, _start_task, etc. remain the same) ...
    def log(self, message):
        if not isinstance(message, str):
            message = str(message)
        self.status_textbox.insert("end", message + "\n")
        self.status_textbox.see("end")

    def _browse_file(self, entry_widget, filetypes=None):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _browse_directory(self, entry_widget):
        path = filedialog.askdirectory()
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _browse_save_as(self, entry_widget, filetypes=None):
        path = filedialog.asksaveasfilename(filetypes=filetypes)
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _create_io_widgets(self, parent, is_dir_input=False, is_dir_output=False, save_types=None):
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
        browse_output_func = self._browse_directory if is_dir_output else lambda: self._browse_save_as(output_entry, filetypes=save_types)
        output_browse_btn = ctk.CTkButton(io_frame, text="Browse...", command=browse_output_func)
        output_browse_btn.grid(row=1, column=2, padx=5, pady=5)
        io_frame.columnconfigure(1, weight=1)
        return io_frame, input_entry, output_entry

    def _start_task(self, worker_func):
        self.log("Starting process...")
        thread = threading.Thread(target=worker_func, daemon=True)
        thread.start()

    def _process_command_worker(self, args):
        old_stdout = sys.stdout
        sys.stdout = redirected_output = io.StringIO()
        try:
            if args.command == 'run-pipeline':
                cli_main.run_pipeline_command(args)
            else:
                cli_main.run_command(args)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            sys.stdout = old_stdout
            self.after(0, self.log, redirected_output.getvalue())
            self.after(0, self.log, "...Process finished.")

    def _start_resize(self, input_path, output_path, size, is_batch):
        args = SimpleNamespace(command='resize', input=None if is_batch else input_path, directory=input_path if is_batch else None, output=output_path, size=size)
        self._start_task(lambda: self._process_command_worker(args))

    def _start_upscale(self, input_path, output_path, factor, is_batch):
        args = SimpleNamespace(command='upscale', input=None if is_batch else input_path, directory=input_path if is_batch else None, output=output_path, factor=float(factor))
        self._start_task(lambda: self._process_command_worker(args))

    def _start_svg(self, input_path, output_path, preprocess, colors, is_batch):
        if preprocess == "None":
            preprocess = None
        args = SimpleNamespace(command='svg', input=None if is_batch else input_path, directory=input_path if is_batch else None, output=output_path, preprocessing=preprocess, colors=int(colors))
        self._start_task(lambda: self._process_command_worker(args))

    def _start_pdf(self, input_path, output_path, size, is_batch):
        args = SimpleNamespace(command='pdf', input=None if is_batch else input_path, directory=input_path if is_batch else None, output=output_path, size=size)
        self._start_task(lambda: self._process_command_worker(args))

    def _start_collage(self, input_dir, output_path, size, grid, padding):
        args = SimpleNamespace(command='collage', input_dir=input_dir, output=output_path, size=size, grid=grid, padding=int(padding))
        self._start_task(lambda: self._process_command_worker(args))

    def _start_pipeline(self, config_path, input_dir, output_path):
        args = SimpleNamespace(command='run-pipeline', config=config_path, input_dir=input_dir, output=output_path)
        self._start_task(lambda: self._process_command_worker(args))

    def _create_batch_toggle_tab(self, tab_name, setup_content_func):
        tab = self.tab_view.tab(tab_name)
        is_batch = ctk.BooleanVar(value=False)
        def toggle_mode():
            for widget in tab.winfo_children():
                widget.destroy()
            setup_content_func(tab, is_batch.get(), is_batch)
        setup_content_func(tab, is_batch.get(), is_batch)

    # ... (Setup methods for Resize, Upscale, SVG, PDF, Collage, Pipeline remain the same) ...
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
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir, save_types=[("SVG files", "*.svg")])
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        colors_frame = ctk.CTkFrame(options_frame)
        colors_label = ctk.CTkLabel(colors_frame, text="Num Colors (for Quantize):")
        colors_entry = ctk.CTkEntry(colors_frame, width=80)
        colors_entry.insert(0, "16")
        def on_preprocess_change(choice):
            if choice == "color_quantization":
                colors_frame.pack(side="left", padx=10, pady=5)
                colors_label.pack(side="left", padx=5)
                colors_entry.pack(side="left", padx=5)
            else:
                colors_frame.pack_forget()
        ctk.CTkLabel(options_frame, text="Preprocessing:").pack(side="left", padx=10)
        preprocess_menu = ctk.CTkOptionMenu(options_frame, values=["None", "threshold", "edge_detection", "color_quantization"], command=on_preprocess_change)
        preprocess_menu.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start SVG Conversion", font=("", 16), command=lambda: self._start_svg(input_entry.get(), output_entry.get(), preprocess_menu.get(), colors_entry.get(), is_batch_var.get())).pack(pady=20)
    def setup_pdf_tab(self):
        self._create_batch_toggle_tab("PDF", self._setup_pdf_tab_content)
    def _setup_pdf_tab_content(self, tab, is_dir, is_batch_var):
        ctk.CTkCheckBox(tab, text="Batch Mode (Process Directory)", variable=is_batch_var, command=lambda: self._create_batch_toggle_tab("PDF", self._setup_pdf_tab_content)).pack(anchor="w", padx=10, pady=5)
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=is_dir, is_dir_output=is_dir, save_types=[("PDF files", "*.pdf")])
        frame.pack(padx=10, pady=10, fill="x")
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(padx=10, pady=5, fill="x", anchor="w")
        ctk.CTkLabel(options_frame, text="Page Size:").pack(side="left", padx=10)
        size_menu = ctk.CTkOptionMenu(options_frame, values=list(cli_main.PAGE_SIZES_IN.keys()))
        size_menu.pack(side="left", padx=10, pady=5)
        ctk.CTkButton(tab, text="Start PDF Creation", font=("", 16), command=lambda: self._start_pdf(input_entry.get(), output_entry.get(), size_menu.get(), is_batch_var.get())).pack(pady=20)
    def setup_collage_tab(self):
        tab = self.tab_view.tab("Collage")
        frame, input_entry, output_entry = self._create_io_widgets(tab, is_dir_input=True, is_dir_output=False, save_types=[("PDF files", "*.pdf")])
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

    def setup_pipeline_tab(self):
        tab = self.tab_view.tab("Pipeline")
        frame = ctk.CTkFrame(tab)
        frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(frame, text="Config File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        config_entry = ctk.CTkEntry(frame, width=450)
        config_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(frame, text="Browse...", command=lambda: self._browse_file(config_entry, filetypes=[("YAML files", "*.yaml *.yml")])).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(frame, text="Input Directory:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        input_entry = ctk.CTkEntry(frame, width=450)
        input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(frame, text="Browse...", command=lambda: self._browse_directory(input_entry)).grid(row=1, column=2, padx=5, pady=5)
        ctk.CTkLabel(frame, text="Final Output Path:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        output_entry = ctk.CTkEntry(frame, width=450)
        output_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(frame, text="Browse...", command=lambda: self._browse_save_as(output_entry)).grid(row=2, column=2, padx=5, pady=5)
        frame.column_configure(1, weight=1)
        ctk.CTkButton(tab, text="Run Pipeline", font=("", 16), command=lambda: self._start_pipeline(config_entry.get(), input_entry.get(), output_entry.get())).pack(pady=20)

    def setup_help_tab(self):
        tab = self.tab_view.tab("Help / About")
        scrollable_frame = ctk.CTkScrollableFrame(tab)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Helper to add text blocks
        def add_text(text, is_heading=False):
            font_size = 16 if is_heading else 12
            font_weight = "bold" if is_heading else "normal"
            label = ctk.CTkLabel(scrollable_frame, text=text, font=("", font_size, font_weight), wraplength=750, justify="left")
            label.pack(anchor="w", pady=(10 if is_heading else 2), padx=5)

        # Content
        add_text("Help & About", is_heading=True)
        add_text("This tool helps you prepare images for Amazon KDP and other print-on-demand services.", is_heading=False)

        add_text("Resize", is_heading=True)
        add_text("What it does: Changes the size of your image(s) to perfectly fit a standard book trim size.\nWhen to use it: To make sure your cover image or full-page illustrations have the correct dimensions for KDP.", is_heading=False)

        add_text("Upscale", is_heading=True)
        add_text("What it does: Increases the resolution of your image(s) by a certain factor.\nWhen to use it: To make smaller images larger without losing too much quality, important for meeting the 300 DPI printing requirement.", is_heading=False)

        add_text("SVG", is_heading=True)
        add_text("What it does: Converts your pixel-based images (PNG, JPG) into scalable vector graphics (SVG).\nWhen to use it: For creating scalable designs that can be resized to any dimension without pixelation.", is_heading=False)
        add_text("Preprocessing Options:\n- None: Direct conversion.\n- threshold: Creates a simple black-and-white line drawing.\n- edge_detection: Creates artistic line art based on outlines.\n- color_quantization: Reduces the image to a small number of colors for a 'poster' effect.", is_heading=False)

        add_text("PDF", is_heading=True)
        add_text("What it does: Takes a single image and turns it into a print-ready PDF with the correct bleed for KDP.\nWhen to use it: For creating a full-bleed cover or a single-page print from one image.", is_heading=False)

        add_text("Collage", is_heading=True)
        add_text("What it does: Arranges multiple images from a folder into a grid on a single PDF page.\nWhen to use it: For creating sticker sheets, collections of small designs, or a photo gallery page.", is_heading=False)

        add_text("Pipeline", is_heading=True)
        add_text("What it does: Automates a multi-step workflow defined in a YAML file.\nWhen to use it: To save time on complex, repetitive tasks that involve multiple steps. See README.md for how to create a pipeline file.", is_heading=False)

        add_text("About", is_heading=True)
        add_text("KDP Image Processing Tool v1.0\nBuilt by Jules, an AI Software Engineer.\n\nPowered by: OpenCV, CustomTkinter, FPDF2, PyYAML, pixels2svg.", is_heading=False)

if __name__ == "__main__":
    app = App()
    app.mainloop()
