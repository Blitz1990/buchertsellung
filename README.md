# KDP Image Processing Tool

A versatile command-line tool to prepare images and documents for print-on-demand (POD) services, with a focus on Amazon KDP's requirements.

This tool allows you to resize, upscale, and convert images, as well as generate print-ready, full-bleed PDF files from single images or a collage of multiple images.

## Features

- **Resize Images:** Resize images to fit standard KDP trim sizes (e.g., 6x9, 8.5x11) while maintaining aspect ratio.
- **Upscale Images:** Increase the resolution of your images by a given factor.
- **SVG Conversion:** Convert raster images (PNG, JPG) to SVG vector format.
  - **Preprocessing:** Apply a black-and-white threshold filter before conversion to create simple line art.
- **KDP PDF Generation:** Create print-ready PDF files from your images with the correct bleed automatically applied for KDP.
- **Collage Creation:** Arrange multiple images from a folder into a grid on a single PDF page to create sticker sheets or collections.
- **Batch Processing:** Process an entire directory of images with a single command for all functions (resize, upscale, svg, pdf).
- **Extensive Size Support:** Supports a wide range of standard KDP paperback trim sizes.

## Usage

This tool can be run in two modes: Command-Line Interface (CLI) for scripting and automation, and a Graphical User Interface (GUI) for ease of use.

### Graphical User Interface (GUI)

To launch the user-friendly graphical interface, run the following command:

```bash
python gui.py
```

The GUI provides access to all the tool's features through a tabbed interface with buttons and forms.

### Command-Line Interface (CLI)

The tool is operated via the command line. The basic structure is:
`python main.py <command> [options]`

### Common Arguments

- `--output`: Specifies the output file path. For batch mode (`--directory`), this specifies the output *directory*.

### Commands

#### 1. Resize

Resizes one or more images to fit a specific page size.

**Single File:**
```bash
python main.py resize --input path/to/image.png --output path/to/resized.png --size 6x9
```

**Batch Mode (Entire Folder):**
```bash
python main.py resize --directory path/to/images/ --output path/to/output_folder/ --size 6x9
```

- `--size`: The target page size. See below for a list of supported sizes.

#### 2. Upscale

Increases the size of one or more images by a factor.

**Single File:**
```bash
python main.py upscale --input path/to/image.png --output path/to/upscaled.png --factor 2.0
```

**Batch Mode:**
```bash
python main.py upscale --directory path/to/images/ --output path/to/output_folder/ --factor 2.0
```
- `--factor`: The number to multiply the image dimensions by (e.g., 2.0 for 200%).

#### 3. SVG Conversion

Converts one or more raster images to SVG.

**Single File:**
```bash
python main.py svg --input path/to/image.png --output path/to/vector.svg
```

**With Preprocessing (Threshold):**
```bash
python main.py svg --input path/to/image.png --output path/to/lineart.svg --preprocessing threshold
```

**Batch Mode:**
```bash
python main.py svg --directory path/to/images/ --output path/to/svg_folder/
```

#### 4. KDP PDF Generation

Creates a print-ready PDF from one or more images with bleed.

**Single File:**
```bash
python main.py pdf --input path/to/image.png --output path/to/book.pdf --size 6x9
```

**Batch Mode:**
```bash
python main.py pdf --directory path/to/images/ --output path/to/pdf_folder/ --size 6x9
```

#### 5. Collage PDF Creation

Arranges multiple images into a grid on a single PDF page.

```bash
python main.py collage --input-dir path/to/images/ --output path/to/collage.pdf --size US_LETTER --grid 3x4 --padding 50
```
- `--input-dir`: The directory containing the images for the collage.
- `--grid`: The layout of the collage (e.g., '3x4' for 3 columns and 4 rows).
- `--padding`: The space in pixels between images on the page (default: 10).


### Supported Page Sizes (`--size`)

`5x8`, `5.06x7.81`, `5.25x8`, `5.5x8.5`, `6x9`, `6.14x9.21`, `6.69x9.61`, `7x10`, `7.44x9.69`, `7.5x9.25`, `8x10`, `8.25x6`, `8.25x8.25`, `8.5x8.5`, `US_LETTER`, `A4`
