# KDP Image & Document Processing Tool

A versatile command-line and graphical tool to prepare images and documents for print-on-demand (POD) services, with a focus on Amazon KDP's requirements.

This tool allows you to resize, upscale, and convert images, as well as generate print-ready, full-bleed PDF files from single images or a collage of multiple images. It also supports chaining these operations together using a powerful pipeline feature.

## Features

- **Graphical & Command-Line Interfaces:** Use the simple GUI for ease of use, or the powerful CLI for scripting and automation.
- **Image Resizing:** Resize images to fit standard KDP trim sizes while maintaining aspect ratio.
- **Image Upscaling:** Increase the resolution of your images by a given factor to meet print quality standards.
- **Advanced SVG Conversion:** Convert raster images (PNG, JPG) to SVG with preprocessing effects like `threshold` (for B&W line art), `edge_detection`, and `color_quantization`.
- **KDP PDF Generation:** Create print-ready PDFs from your images with the correct bleed automatically applied for KDP.
- **Collage Creation:** Arrange multiple images from a folder into a grid on a single PDF page, perfect for sticker sheets or photo collections.
- **Workflow Pipelines:** Automate complex, multi-step tasks by defining them in a simple YAML file.
- **Batch Processing:** Process an entire directory of images at once for most commands.

## Usage

This tool can be run in two modes: a Graphical User Interface (GUI) and a Command-Line Interface (CLI).

### Graphical User Interface (GUI)

To launch the user-friendly graphical interface, run the following command in your terminal:

```bash
python gui.py
```

The GUI provides access to all the tool's features through a tabbed interface. For detailed explanations of each feature, please see the **"Help / About"** tab inside the application.

### Command-Line Interface (CLI)

The basic structure is: `python main.py <command> [options]`

---

### CLI Commands

#### 1. Resize
- **What it does:** Changes the size of your image(s) to perfectly fit a standard book trim size.
- **When to use it:** To make sure your cover image or full-page illustrations have the correct dimensions for KDP.

*Single File:*
```bash
python main.py resize --input path/to/image.png --output path/to/resized.png --size 6x9
```
*Batch Mode (Entire Folder):*
```bash
python main.py resize --directory path/to/images/ --output path/to/output_folder/ --size 6x9
```

#### 2. Upscale
- **What it does:** Increases the resolution of your image(s) by a certain factor.
- **When to use it:** To make smaller images larger without losing too much quality, which is important for meeting the 300 DPI printing requirement.

*Single File:*
```bash
python main.py upscale --input path/to/image.png --output path/to/upscaled.png --factor 2.0
```

#### 3. SVG Conversion
- **What it does:** Converts your pixel-based images (PNG, JPG) into scalable vector graphics (SVG).
- **When to use it:** For creating scalable designs that can be resized to any dimension without pixelation.
- **Preprocessing Options:**
    - `threshold`: Creates a simple black-and-white line drawing. Perfect for coloring book pages.
    - `edge_detection`: Creates artistic line art based on the outlines in your image.
    - `color_quantization`: Reduces the image to a small number of colors for a "poster" effect. Use `--colors` to specify how many.

*Example (Edge Detection):*
```bash
python main.py svg --input path/to/image.png --output path/to/edges.svg --preprocessing edge_detection
```
*Example (Color Quantization):*
```bash
python main.py svg --input path/to/image.png --output path/to/quantized.svg --preprocessing color_quantization --colors 8
```

#### 4. KDP PDF Generation
- **What it does:** Takes a single image and turns it into a print-ready PDF with the correct bleed for KDP.
- **When to use it:** For creating a full-bleed cover or a single-page print from one image.

*Single File:*
```bash
python main.py pdf --input path/to/image.png --output path/to/book.pdf --size 6x9
```

#### 5. Collage PDF Creation
- **What it does:** Arranges multiple images from a folder into a grid on a single PDF page.
- **When to use it:** For creating sticker sheets, collections of small designs, or a photo gallery page.

*Example:*
```bash
python main.py collage --input-dir path/to/images/ --output path/to/collage.pdf --size US_LETTER --grid 3x4 --padding 50
```

#### 6. Run Pipeline
- **What it does:** Automates a multi-step workflow defined in a YAML file.
- **When to use it:** To save time on complex, repetitive tasks that involve multiple steps.

*Example:*
```bash
python main.py run-pipeline --config path/to/pipeline.yaml --input-dir path/to/images/ --output path/to/final_output_dir/
```
*Example `pipeline.yaml`:*
```yaml
pipeline:
  - name: "Step 1: Upscale all images"
    command: "upscale"
    params:
      factor: 2.0
  - name: "Step 2: Create individual PDFs from upscaled images"
    command: "pdf"
    params:
      size: "6x9"
```

---

### Supported Page Sizes (`--size`)
`5x8`, `5.06x7.81`, `5.25x8`, `5.5x8.5`, `6x9`, `6.14x9.21`, `6.69x9.61`, `7x10`, `7.44x9.69`, `7.5x9.25`, `8x10`, `8.25x6`, `8.25x8.25`, `8.5x8.5`, `US_LETTER`, `A4`
