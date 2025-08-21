import cv2
import numpy as np
import os
import pixels2svg
from fpdf import FPDF
import argparse
import glob

# Page dimensions at 300 DPI for image processing (Width x Height)
PAGE_SIZES_PX = {
    "5x8": (1500, 2400),
    "5.06x7.81": (1518, 2343),
    "5.25x8": (1575, 2400),
    "5.5x8.5": (1650, 2550),
    "6x9": (1800, 2700),
    "6.14x9.21": (1842, 2763),
    "6.69x9.61": (2007, 2883),
    "7x10": (2100, 3000),
    "7.44x9.69": (2232, 2907),
    "7.5x9.25": (2250, 2775),
    "8x10": (2400, 3000),
    "8.25x6": (2475, 1800),
    "8.25x8.25": (2475, 2475),
    "8.5x8.5": (2550, 2550),
    "US_LETTER": (2550, 3300),
    "A4": (2481, 3507),
}

# Page dimensions in inches for PDF generation (Width x Height)
PAGE_SIZES_IN = {
    "5x8": (5, 8),
    "5.06x7.81": (5.06, 7.81),
    "5.25x8": (5.25, 8),
    "5.5x8.5": (5.5, 8.5),
    "6x9": (6, 9),
    "6.14x9.21": (6.14, 9.21),
    "6.69x9.61": (6.69, 9.61),
    "7x10": (7, 10),
    "7.44x9.69": (7.44, 9.69),
    "7.5x9.25": (7.5, 9.25),
    "8x10": (8, 10),
    "8.25x6": (8.25, 6),
    "8.25x8.25": (8.25, 8.25),
    "8.5x8.5": (8.5, 8.5),
    "US_LETTER": (8.5, 11),
    "A4": (8.27, 11.69),
}

BLEED_IN = 0.125
DPI = 300

def load_image(filepath: str) -> np.ndarray:
    """Loads an image from a file path."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image file not found at: {filepath}")
    image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"Could not read image from: {filepath}")
    return image

def save_image(image: np.ndarray, filepath: str):
    """Saves an image to a file path."""
    output_dir = os.path.dirname(filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        cv2.imwrite(filepath, image)
        print(f"Image saved to {filepath}")
    except Exception as e:
        raise IOError(f"Could not save image to {filepath}: {e}")

def resize_image_to_fit(image: np.ndarray, target_size_str: str) -> np.ndarray:
    """
    Resizes an image to fit within the specified page dimensions (e.g., "A4")
    while maintaining the aspect ratio.
    """
    if target_size_str not in PAGE_SIZES_PX:
        raise ValueError(f"Invalid target size. Choose from: {list(PAGE_SIZES_PX.keys())}")

    target_w, target_h = PAGE_SIZES_PX[target_size_str]
    img_h, img_w = image.shape[:2]

    img_ratio = img_w / img_h
    target_ratio = target_w / target_h

    if img_ratio > target_ratio:
        new_w = target_w
        new_h = int(new_w / img_ratio)
    else:
        new_h = target_h
        new_w = int(new_h * img_ratio)

    if new_w < img_w or new_h < img_h:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC

    resized_image = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
    return resized_image

def upscale_image(image: np.ndarray, factor: float) -> np.ndarray:
    """
    Upscales an image by a given factor.
    """
    if factor <= 1.0:
        print("Upscale factor should be greater than 1.0. Returning original image.")
        return image

    img_h, img_w = image.shape[:2]
    new_w = int(img_w * factor)
    new_h = int(img_h * factor)

    upscaled_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return upscaled_image

def preprocess_image(image: np.ndarray, processing_type: str) -> np.ndarray:
    """Applies preprocessing to an image before SVG conversion."""
    if processing_type == 'threshold':
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, processed_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        return processed_image
    else:
        raise ValueError(f"Unknown preprocessing type: {processing_type}")

def convert_image_to_svg(image_path: str, svg_path: str):
    """
    Converts a raster image file to an SVG file.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image file not found at: {image_path}")

    output_dir = os.path.dirname(svg_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        pixels2svg.pixels2svg(image_path, svg_path)
        print(f"Image converted to SVG and saved at {svg_path}")
    except Exception as e:
        raise IOError(f"Failed to convert image to SVG: {e}")

def resize_image_for_bleed(image: np.ndarray, target_size_str: str) -> np.ndarray:
    """
    Resizes and crops an image to fit the full bleed page size for KDP.
    """
    if target_size_str not in PAGE_SIZES_IN:
        raise ValueError(f"Invalid target size. Choose from: {list(PAGE_SIZES_IN.keys())}")

    trim_w_in, trim_h_in = PAGE_SIZES_IN[target_size_str]
    bleed_w_in = trim_w_in + BLEED_IN
    bleed_h_in = trim_h_in + (2 * BLEED_IN)

    target_w_px = int(bleed_w_in * DPI)
    target_h_px = int(bleed_h_in * DPI)

    img_h, img_w = image.shape[:2]
    img_ratio = img_w / img_h
    target_ratio = target_w_px / target_h_px

    if img_ratio > target_ratio:
        scale_factor = target_h_px / img_h
        resized_w = int(img_w * scale_factor)
        resized_h = target_h_px
    else:
        scale_factor = target_w_px / img_w
        resized_w = target_w_px
        resized_h = int(img_h * scale_factor)

    resized_image = cv2.resize(image, (resized_w, resized_h), interpolation=cv2.INTER_CUBIC)

    crop_x = (resized_w - target_w_px) // 2
    crop_y = (resized_h - target_h_px) // 2

    cropped_image = resized_image[crop_y:crop_y + target_h_px, crop_x:crop_x + target_w_px]
    return cropped_image

def create_collage(image_paths: list, target_size_str: str, grid_str: str, padding: int) -> np.ndarray:
    """Creates a collage image from a list of image paths."""
    # Parse grid string
    try:
        cols, rows = map(int, grid_str.lower().split('x'))
    except ValueError:
        raise ValueError("Invalid grid format. Use '_columns_x_rows_' (e.g., '3x4').")

    # Calculate canvas size
    trim_w_in, trim_h_in = PAGE_SIZES_IN[target_size_str]
    bleed_w_in = trim_w_in + BLEED_IN
    bleed_h_in = trim_h_in + (2 * BLEED_IN)
    canvas_w_px = int(bleed_w_in * DPI)
    canvas_h_px = int(bleed_h_in * DPI)

    # Create blank canvas
    canvas = np.full((canvas_h_px, canvas_w_px, 3), 255, dtype=np.uint8)

    # Calculate cell size
    cell_w = (canvas_w_px - (cols + 1) * padding) // cols
    cell_h = (canvas_h_px - (rows + 1) * padding) // rows

    if cell_w <= 0 or cell_h <= 0:
        raise ValueError("Padding is too large for the given grid and page size.")

    # Iterate and place images
    img_idx = 0
    for row in range(rows):
        for col in range(cols):
            if img_idx >= len(image_paths):
                break

            # Load and resize image to fit cell
            image = load_image(image_paths[img_idx])
            img_h, img_w = image.shape[:2]

            # Resize to fit within cell_w x cell_h
            scale = min(cell_w / img_w, cell_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Calculate paste position
            paste_x = col * (cell_w + padding) + padding + (cell_w - new_w) // 2
            paste_y = row * (cell_h + padding) + padding + (cell_h - new_h) // 2

            canvas[paste_y:paste_y + new_h, paste_x:paste_x + new_w] = resized_img
            img_idx += 1
        if img_idx >= len(image_paths):
            break

    return canvas

def create_kdp_pdf(image_path: str, pdf_path: str, target_size_str: str):
    """
    Creates a print-ready PDF with a full-bleed image for KDP.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found at: {image_path}")

    if target_size_str not in PAGE_SIZES_IN:
        raise ValueError(f"Invalid target size. Choose from: {list(PAGE_SIZES_IN.keys())}")

    output_dir = os.path.dirname(pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    trim_w_in, trim_h_in = PAGE_SIZES_IN[target_size_str]
    bleed_w_in = trim_w_in + BLEED_IN
    bleed_h_in = trim_h_in + (2 * BLEED_IN)

    pdf = FPDF(orientation='P', unit='in', format=(bleed_w_in, bleed_h_in))
    pdf.add_page()
    pdf.image(image_path, x=0, y=0, w=bleed_w_in, h=bleed_h_in)
    pdf.output(pdf_path)
    print(f"KDP PDF created at: {pdf_path}")


def main():
    """Main function to drive the image processing tool via CLI."""
    parser = argparse.ArgumentParser(description="KDP Image Processing Tool. Provide a command (e.g., resize, svg) and its options. Use --input for a single file or --directory for batch processing.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Parent parser for common arguments ---
    parent_parser = argparse.ArgumentParser(add_help=False)
    input_group = parent_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", help="Path to a single input image.")
    input_group.add_argument("--directory", help="Path to a directory of images for batch processing.")
    parent_parser.add_argument("--output", required=True, help="Path to the output file or directory (for batch mode).")

    # --- Resize command ---
    parser_resize = subparsers.add_parser("resize", help="Resize image(s) to fit a standard page size.", parents=[parent_parser])
    parser_resize.add_argument("--size", required=True, choices=PAGE_SIZES_IN.keys(), help="Target page size.")

    # --- Upscale command ---
    parser_upscale = subparsers.add_parser("upscale", help="Upscale image(s) by a factor.", parents=[parent_parser])
    parser_upscale.add_argument("--factor", required=True, type=float, help="Scaling factor (e.g., 2.5).")

    # --- SVG command ---
    parser_svg = subparsers.add_parser("svg", help="Convert raster image(s) to SVG.", parents=[parent_parser])
    parser_svg.add_argument("--preprocessing", choices=['threshold'], help="Apply preprocessing before converting.")

    # --- PDF command ---
    parser_pdf = subparsers.add_parser("pdf", help="Create KDP-ready PDF(s) from image(s).", parents=[parent_parser])
    parser_pdf.add_argument("--size", required=True, choices=PAGE_SIZES_IN.keys(), help="Target page size for the PDF.")

    # --- Collage command ---
    parser_collage = subparsers.add_parser("collage", help="Arrange multiple images onto a single PDF page.")
    parser_collage.add_argument("--input-dir", required=True, help="Path to the directory of images.")
    parser_collage.add_argument("--output", required=True, help="Path to save the output PDF file.")
    parser_collage.add_argument("--size", required=True, choices=PAGE_SIZES_IN.keys(), help="Target page size for the PDF.")
    parser_collage.add_argument("--grid", required=True, help="Grid layout for the collage (e.g., '3x4' for 3 columns by 4 rows).")
    parser_collage.add_argument("--padding", type=int, default=10, help="Padding in pixels between images.")


    args = parser.parse_args()

    try:
        if args.command == "collage":
            # --- Collage command logic ---
            if not os.path.isdir(args.input_dir):
                raise FileNotFoundError(f"Input directory not found: {args.input_dir}")

            image_extensions = ["*.png", "*.jpg", "*.jpeg"]
            collage_files = []
            for ext in image_extensions:
                collage_files.extend(glob.glob(os.path.join(args.input_dir, ext)))

            if not collage_files:
                print("No images found in the specified directory for collage.")
                return

            print(f"Creating collage from {len(collage_files)} images...")
            collage_canvas = create_collage(collage_files, args.size, args.grid, args.padding)

            temp_collage_path = "temp_collage.png"
            save_image(collage_canvas, temp_collage_path)

            print("Creating final PDF from collage...")
            create_kdp_pdf(temp_collage_path, args.output, args.size)

            os.remove(temp_collage_path)
            print(f"Removed temporary file: {temp_collage_path}")

        else:
            # --- Logic for all other commands (single file or batch) ---
            if args.directory:
                if not os.path.isdir(args.directory):
                    raise FileNotFoundError(f"Input directory not found: {args.directory}")
                image_extensions = ["*.png", "*.jpg", "*.jpeg"]
                input_files = []
                for ext in image_extensions:
                    input_files.extend(glob.glob(os.path.join(args.directory, ext)))
                if not input_files:
                    print("No images found in the specified directory.")
                    return
            else:
                input_files = [args.input]

            for input_path in input_files:
                base_name, ext = os.path.splitext(os.path.basename(input_path))

                if args.directory:
                    output_dir = args.output
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                else:
                    output_dir = os.path.dirname(args.output) or '.'

                print(f"\n--- Processing {input_path} ---")

                if args.command == "resize":
                    output_path = os.path.join(output_dir, f"{base_name}_resized{ext}") if args.directory else args.output
                    image = load_image(input_path)
                    processed_image = resize_image_to_fit(image, args.size)
                    save_image(processed_image, output_path)

                elif args.command == "upscale":
                    output_path = os.path.join(output_dir, f"{base_name}_upscaled{ext}") if args.directory else args.output
                    image = load_image(input_path)
                    processed_image = upscale_image(image, args.factor)
                    save_image(processed_image, output_path)

                elif args.command == "svg":
                    output_path = os.path.join(output_dir, f"{base_name}.svg") if args.directory else args.output
                    input_for_svg = input_path
                    temp_image_path = None

                    if args.preprocessing:
                        print(f"Preprocessing image with: {args.preprocessing}")
                        image = load_image(input_path)
                        processed_image = preprocess_image(image, args.preprocessing)
                        temp_image_path = f"temp_{base_name}.png"
                        save_image(processed_image, temp_image_path)
                        input_for_svg = temp_image_path

                    convert_image_to_svg(input_for_svg, output_path)

                    if temp_image_path:
                        os.remove(temp_image_path)
                        print(f"Removed temporary file: {temp_image_path}")

                elif args.command == "pdf":
                    output_path = os.path.join(output_dir, f"{base_name}.pdf") if args.directory else args.output
                    print("Resizing image for bleed...")
                    image = load_image(input_path)
                    bleed_image = resize_image_for_bleed(image, args.size)

                    temp_image_path = f"temp_{base_name}.png"
                    save_image(bleed_image, temp_image_path)

                    print("Creating PDF...")
                    create_kdp_pdf(temp_image_path, output_path, args.size)

                    os.remove(temp_image_path)
                    print(f"Removed temporary file: {temp_image_path}")

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
