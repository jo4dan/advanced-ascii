import sys
import os
import cv2
import numpy as np
import time
import shutil
import signal
import threading
import readline
import tty
import curses
import termios
from datetime import datetime, timedelta
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

# ASCII Density Modes
ASCII_MODES = {
    "monochrome": "@%#*+=-:. ",
    "block": "█▓▒░ ",
    "dots": "•· ",
    "alphanumeric": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ9876543210?!;:,. ",
    "custom": None,
    "16bit": "█▓▒░▀▄"
}

# Common directories to search for images
COMMON_DIRS = [
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~"),
]

# Supported image extensions
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif")

def get_key():
    """Get single key press without requiring Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Arrow keys
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return {
        '\x1b[A': 'up',
        '\x1b[B': 'down',
        ' ': 'space',
        '\r': 'enter',
        '\n': 'enter'
    }.get(ch, ch)

import curses

def select_formats():
    """Interactive format selection using the curses library."""
    formats = [
        ("PNG", True),
        ("TIFF", False),
        ("SVG", True),
        ("HTML", True),
        ("ASC (Text)", False)
    ]
    selected_index = 0

    def main_menu(stdscr):
        nonlocal selected_index, formats
        curses.curs_set(0)  # Hide the cursor
        while True:
            stdscr.clear()
            stdscr.addstr("Select output formats (Use UP/DOWN to navigate, SPACE to toggle, ENTER to confirm, Q to quit):\n\n")
            # Print the menu items
            for i, (name, selected) in enumerate(formats):
                if i == selected_index:
                    prefix = ">"  # Highlight the current selection
                else:
                    prefix = " "
                checkbox = "[✓]" if selected else "[ ]"
                stdscr.addstr(f"{prefix} {checkbox} {i+1}. {name}\n")
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP and selected_index > 0:
                selected_index -= 1
            elif key == curses.KEY_DOWN and selected_index < len(formats) - 1:
                selected_index += 1
            elif key == ord(" "):
                # Toggle the selection
                name, sel = formats[selected_index]
                formats[selected_index] = (name, not sel)
            elif key in [10, 13]:  # Enter key
                selected = [name.lower().split()[0] for name, sel in formats if sel]
                if selected:
                    return selected
                else:
                    stdscr.addstr("\n❌ Please select at least one format!")
                    stdscr.refresh()
                    curses.napms(1000)  # Wait for 1 second
            elif key in [ord('q'), ord('Q')]:
                return None

    return curses.wrapper(main_menu)


def find_image(filename):
    """Search for an image file in common directories."""
    for dir_path in COMMON_DIRS:
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower() == filename.lower() and file.lower().endswith(SUPPORTED_EXTENSIONS):
                    return os.path.join(root, file)
    return None

def get_image_path():
    """Get image path from user input with auto-completion."""
    while True:
        file_name = input("Enter the image file name: ").strip()
        if not file_name:
            print("❌ No file name entered. Please try again.")
            continue
        if not file_name.lower().endswith(SUPPORTED_EXTENSIONS):
            print(f"❌ Invalid file extension. Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}")
            continue
        img_path = find_image(file_name)
        if img_path:
            return img_path
        else:
            print(f"❌ File '{file_name}' not found in common directories. Please try again.")

def auto_adjust_brightness_contrast(img):
    """Auto-adjusts image brightness and contrast for better detail."""
    img = np.array(img)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    return Image.fromarray(img)

def quantize_to_16bit_palette(color):
    """Map RGB to nearest in 16-color NES box-art-inspired palette for 16-bit mode."""
    # Cast to Python int to avoid numpy uint8 wraparound/overflow warnings
    color = [int(x) for x in color]
    
    # 16-color palette tuned to NES box art vibrancy: saturated primaries/secondaries from reference grid
    palette = [
        (0, 0, 0),          # Black (universal BG void)
        (166, 39, 33),      # Bold red (Contra/Metal Gear fire)
        (225, 147, 33),     # Vivid orange (River City/Dragon Warrior glow)
        (173, 214, 0),      # Yellow-green (Zelda grass)
        (81, 223, 0),       # Strong lime (Duck Hunt fields)
        (57, 195, 223),     # Cyan/teal (Mega Man skies)
        (11, 83, 215),      # Deep blue (Star Wars/Mario Bros. depths)
        (102, 33, 247),     # Electric purple (Ninja Gaiden shadows)
        (241, 91, 254),     # Hot magenta (Bubble Bobble pops)
        (254, 94, 196),     # Vivid pink (TMNT accents)
        (121, 211, 0),      # Bright green (Ghosts 'n Goblins foliage)
        (134, 67, 0),       # Earthy brown (Castlevania dirt)
        (0, 109, 133),      # Deep teal (Adventure Island waves)
        (66, 66, 66),       # Dark gray (shading steps)
        (161, 161, 161),    # Light gray (highlights)
        (255, 255, 255)     # Pure white (blasts/explosions)
    ]
    # Simple Euclidean distance to find nearest color
    distances = [((color[0]-c[0])**2 + (color[1]-c[1])**2 + (color[2]-c[2])**2) for c in palette]
    nearest_idx = distances.index(min(distances))
    return palette[nearest_idx]

def preprocess_16bit_image(img_path, target_res=128):
    """Downscale, quantize, and add CRT scanlines for 16-bit mode."""
    # Load and downscale to fixed low-res for pixelation
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    scale_h, scale_w = target_res / h, target_res / w
    new_w, new_h = int(w * scale_w), int(h * scale_h)
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_NEAREST)  # Nearest-neighbor for crisp pixels
    
    # Quantize to 16-color palette (using our function; convert BGR to RGB first)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    quantized = np.zeros_like(img_rgb)
    for i in range(img_rgb.shape[0]):
        for j in range(img_rgb.shape[1]):
            quantized[i, j] = quantize_to_16bit_palette(img_rgb[i, j])
    
    # Add CRT scanlines: Alternate dark/bright rows for flicker (subtle, ~10% opacity)
    scanline_img = np.copy(quantized)
    for i in range(scanline_img.shape[0]):
        if i % 2 == 0:  # Even rows slightly dimmed
            scanline_img[i] = scanline_img[i] * 0.9  # Quick "phosphor" dim
    
    # Optional dithering: Apply Floyd-Steinberg for better gradients (if you want to add it)
    # For now, skip or use cv2 for simple error diffusion—keeps it lightweight
    
    return Image.fromarray(scanline_img.astype(np.uint8))

def resize_image(img, width):
    """Resize image while maintaining aspect ratio for ASCII characters."""
    orig_width, orig_height = img.size
    aspect_ratio = orig_height / orig_width
    height = int(width * aspect_ratio * 0.5)
    return img.resize((width, height), Image.LANCZOS)

def image_to_ascii(img, ascii_chars, progress_callback=None):
    """Convert image pixels to ASCII characters (grayscale)."""
    arr = np.array(img)
    ascii_art = []
    total_rows = len(arr)
    for i, row in enumerate(arr):
        ascii_row = "".join([ascii_chars[int(pixel / 255 * (len(ascii_chars) - 1))] for pixel in row])
        ascii_art.append(ascii_row)
        if progress_callback:
            progress_callback("convert", (i + 1) / total_rows)
    return ascii_art

def save_ascii_as_asc(ascii_art, output_path, progress_callback=None):
    """Save ASCII art as .asc file with progress reporting."""
    total = len(ascii_art)
    with open(output_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(ascii_art):
            f.write(line + "\n")
            if progress_callback:
                progress_callback((i + 1) / total)

def save_ascii_as_image(ascii_art, output_path, mode, font_path, font_size, colored, color_img, progress_callback=None):
    """Save ASCII art as image file with progress reporting."""
    if font_path is None:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    background_color = "black" if mode == "16bit" else ("white" if mode == "block" else "#2B3338")
    
    background_color = "white" if mode == "block" else "#2B3338"
    text_color = "#FAFAFA"
    bbox = font.getbbox("A")
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]
    total_lines = len(ascii_art)
    img_width = max(len(line) for line in ascii_art) * char_width
    img_height = total_lines * char_height
    
    out_img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(out_img)
    
    for idx, line in enumerate(ascii_art):
        y = idx * char_height
        if colored and color_img is not None:
            color_arr = np.array(color_img)
            for col_idx, char in enumerate(line):
                if idx < color_arr.shape[0] and col_idx < color_arr.shape[1]:
                    r, g, b = color_arr[idx, col_idx]
                    if mode == "16bit":
                        r, g, b = quantize_to_16bit_palette((r, g, b))
                else:
                    r, g, b = (255, 255, 255)
                x_pos = col_idx * char_width
                draw.text((x_pos, y), char, fill=(r, g, b), font=font)
        else:
            draw.text((0, y), line, fill=text_color, font=font)
        
        if progress_callback:
            progress_callback((idx + 1) / total_lines)
    
    out_img.save(output_path)

def save_ascii_as_tiff(ascii_art, output_path, mode, font_path, font_size, colored, color_img, progress_callback=None):
    """Save ASCII art as TIFF file with progress reporting."""
    save_ascii_as_image(ascii_art, output_path, mode, font_path, font_size, colored, color_img, progress_callback)

def save_ascii_as_svg(ascii_art, output_path, mode, font_size, colored, color_img, progress_callback=None):
    """Save ASCII art as SVG file with progress reporting."""
    char_width = font_size * 0.6
    char_height = font_size
    total_lines = len(ascii_art)
    svg_width = int(max(len(line) for line in ascii_art) * char_width)
    svg_height = int(total_lines * char_height)
    background_color = "white" if mode == "block" else "#2B3338"
    background_color = "black" if mode == "16bit" else ("white" if mode == "block" else "#2B3338")
    default_text_color = "black" if mode == "block" else "#FAFAFA"
    
    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">')
    svg_lines.append(f'<rect width="100%" height="100%" fill="{background_color}" />')
    
    for i, line in enumerate(ascii_art):
        y = (i + 1) * char_height
        if colored and color_img is not None:
            color_arr = np.array(color_img)
            tspans = []
            for j, char in enumerate(line):
                if i < color_arr.shape[0] and j < color_arr.shape[1]:
                    r, g, b = color_arr[i, j]
                    if mode == "16bit":
                        r, g, b = quantize_to_16bit_palette((r, g, b))
                    fill = f"rgb({r},{g},{b})"
                else:
                    fill = default_text_color
                tspans.append(f'<tspan x="{j*char_width}" dy="0" fill="{fill}">{char}</tspan>')
            text_line = "".join(tspans)
            svg_lines.append(f'<text x="0" y="{y}" font-family="monospace" font-size="{font_size}">{text_line}</text>')
        else:
            svg_lines.append(f'<text x="0" y="{y}" font-family="monospace" font-size="{font_size}" fill="{default_text_color}">{line}</text>')
        
        if progress_callback:
            progress_callback((i + 1) / total_lines)
    
    svg_lines.append("</svg>")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))

def save_ascii_as_html(ascii_art, output_path, mode, colored, color_img, progress_callback=None):
    """Save ASCII art as HTML file with progress reporting."""
    total_lines = len(ascii_art)
    bg_color = "#2B3338" if mode != "block" else "white"
    bg_color = "#000000" if mode == "16bit" else ("#FFFFFF" if mode != "block" else "white")
    text_color = "#FAFAFA" if mode != "block" else "black"
    
    html_lines = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="UTF-8">',
        '<title>ASCII Art</title>',
        '<style>',
        'body {',
        f'  background-color: {bg_color};',
        '  font-family: monospace;',
        '  white-space: pre;',
        '  line-height: 1;',
        '}',
        '</style>',
        '</head>',
        '<body>'
    ]
    
    if colored and color_img is not None:
        color_arr = np.array(color_img)
        for i, line in enumerate(ascii_art):
            html_line = []
            for j, char in enumerate(line):
                if i < color_arr.shape[0] and j < color_arr.shape[1]:
                    r, g, b = color_arr[i, j]
                    if mode == "16bit":
                        r, g, b = quantize_to_16bit_palette((r, g, b))
                    html_line.append(f'<span style="color:rgb({r},{g},{b})">{char}</span>')
                else:
                    html_line.append(char)
            html_lines.append("".join(html_line))
            if progress_callback:
                progress_callback((i + 1) / total_lines)
    else:
        for i, line in enumerate(ascii_art):
            html_lines.append(f'<span style="color:{text_color}">{line}</span>')
            if progress_callback:
                progress_callback((i + 1) / total_lines)
    
    html_lines.extend(['</body>', '</html>'])
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

class ProgressTracker:
    def __init__(self, tasks):
        self.progress = {task: 0.0 for task in tasks}
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.last_update = time.time()
        self.eta = "Calculating..."
        
    def update(self, task, value):
        with self.lock:
            self.progress[task] = value
            now = time.time()
            elapsed = now - self.start_time
            completed = sum(self.progress.values()) / len(self.progress)
            
            if completed > 0:
                total_estimated = elapsed / completed
                remaining = total_estimated - elapsed
                self.eta = str(timedelta(seconds=int(remaining)))
            
            self.last_update = now
            self.display()
    
    def display(self):
        total = sum(self.progress.values()) / len(self.progress)
        bar_length = 30
        filled = int(bar_length * total)
        bar = '█' * filled + '-' * (bar_length - filled)
        
        details = []
        for task, value in self.progress.items():
            percent = int(value * 100)
            details.append(f"{task}: {percent}%")
        
        line = f"\r\033[KProcessing: |{bar}| {int(total*100)}%  [{' | '.join(details)}]  ETA: {self.eta}"
        sys.stdout.write(line)
        sys.stdout.flush()
        
        if total >= 1.0:
            print("\n✅ All tasks completed!")

def save_all_files(ascii_art, output_dir, base_filename, mode, font_path, font_size, apply_color, color_img, width, selected_formats):
    """Save only selected file formats."""
    os.makedirs(output_dir, exist_ok=True)
    
    format_handlers = {
        "png": (lambda p, cb: save_ascii_as_image(ascii_art, p, mode, font_path, font_size, apply_color == "y", color_img, cb)),
        "tiff": (lambda p, cb: save_ascii_as_tiff(ascii_art, p, mode, font_path, font_size, apply_color == "y", color_img, cb)),
        "svg": (lambda p, cb: save_ascii_as_svg(ascii_art, p, mode, font_size, apply_color == "y", color_img, cb)),
        "html": (lambda p, cb: save_ascii_as_html(ascii_art, p, mode, apply_color == "y", color_img, cb)),
        "asc": (lambda p, cb: save_ascii_as_asc(ascii_art, p, cb))
    }
    
    paths = []
    progress = ProgressTracker(selected_formats)
    
    for fmt in selected_formats:
        if fmt in format_handlers:
            path = os.path.join(output_dir, f"{base_filename}.{fmt}")
            format_handlers[fmt](path, lambda v: progress.update(fmt, v))
            paths.append(path)
    
    return paths

def live_render(ascii_lines):
    """Print ASCII art line by line with a slight delay."""
    print("\n🎞 Live Rendering...\n")
    for line in ascii_lines:
        print(line)
        time.sleep(0.02)

def build_color_console(ascii_art, color_img):
    """
    Build a list of strings for live rendering in color (ANSI).
    Map each ASCII character to its pixel color.
    """
    color_lines = []
    color_arr = np.array(color_img)
    for row_idx, line in enumerate(ascii_art):
        color_line = []
        for col_idx, char in enumerate(line):
            if row_idx < color_arr.shape[0] and col_idx < color_arr.shape[1]:
                r, g, b = color_arr[row_idx, col_idx]
            else:
                r, g, b = (255, 255, 255)
            ansi_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            color_line.append(ansi_char)
        color_lines.append("".join(color_line))
    return color_lines

def signal_handler(sig, frame):
    print()
    print("\n🎉 Thank you for using the ASCII Image Converter! Exiting...\n")
    sys.exit(0)

def main():

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        print("\n====================================================================")
        print(" 🎨 ASCII Image Converter - Real-Time Progress By \033[1;38;2;57;255;20mgithub.com/jo4dan\033[0m ")
        print("====================================================================\n")
        
        # Get user input
        img_path = get_image_path()
        print(f"✅ Selected Image: {os.path.basename(img_path)}\n")
        
        try:
            width_input = input("Enter ASCII width (default: 100): ").strip()
            width = int(width_input) if width_input else 100
        except ValueError:
            width = 100
            
        print("\nChoose ASCII Mode:")
        print("  1️⃣ Monochrome")
        print("  2️⃣ Block Characters (█▓▒░)")
        print("  3️⃣ Dots (•·)")
        print("  4️⃣ Alphanumeric")
        print("  5️⃣ Custom Character Set")
        print(" \033[1;33m 6️⃣ 16-bit (Blocky Pixel Style) \033[0m " )  # Golden retro glow
        mode_choice = input("Select (1-6, or default: Monochrome): ") or "1" 
        print()
        mode_choice = ["monochrome", "block", "dots", "alphanumeric", "custom", "16bit"][int(mode_choice) - 1]
        
        if mode_choice == "custom":
            custom_chars = input("Enter custom characters from dark to light: ").strip()
            if not custom_chars:
                print("❌ No characters entered! Using default...")
                custom_chars = ASCII_MODES["monochrome"]
        else:
            custom_chars = ASCII_MODES[mode_choice]
            
        print(f"✅ Mode set to: {mode_choice.capitalize()}")
        if mode_choice == "16bit":
            print("ℹ️ 16-bit auto-downscales to 128x128 pixels for retro vibe (width scales output). \n")
        apply_color = input("Apply color to saved ASCII? (Y/n): ").strip().lower() or "y"
        
        # Format selection
        print("\n🖼 Select output formats:")
        selected_formats = select_formats()
        if not selected_formats:
            print("❌ No formats selected! Please try again.")
            continue
            
        # Show settings summary and confirm
        print("\n🛠 Conversion Settings Summary:")
        print("=" * 40)
        print(f"Source Image: {os.path.basename(img_path)}")
        print(f"ASCII Width: {width} characters")
        print(f"Color Mode: {'Enabled' if apply_color == 'y' else 'Disabled'}")
        print(f"ASCII Style: {mode_choice.capitalize()}")
        print(f"Output Formats: {', '.join(selected_formats)}")
        print("=" * 40)
        
        proceed = input("\nProceed with these settings? (Y/n): ").strip().lower() or "y"
        if proceed != "y":
            print("❌ Settings not confirmed. Returning to image selection...")
            continue
        
        # Generate live preview
        live_width = min(width, 100)
        if apply_color == "y":
            live_gray = Image.open(img_path).convert("L")
            live_gray = resize_image(live_gray, live_width)
            live_ascii = image_to_ascii(live_gray, custom_chars)
            live_color = Image.open(img_path).convert("RGB")
            live_color = resize_image(live_color, live_width)
            render_lines = build_color_console(live_ascii, live_color)
        else:
            live_gray = Image.open(img_path).convert("L")
            live_gray = auto_adjust_brightness_contrast(live_gray)
            live_gray = resize_image(live_gray, live_width)
            render_lines = image_to_ascii(live_gray, custom_chars)
            
        live_render(render_lines)
        
        # Process the full image
        base_filename = os.path.splitext(os.path.basename(img_path))[0]
        output_dir = os.path.join(os.path.dirname(img_path), f"{base_filename}_ascii")

        if mode_choice == "16bit" and apply_color == "y":
            # Preprocess for retro low-res (color version)
            color_img = preprocess_16bit_image(img_path)
            grayscale_img = color_img.convert("L")
        else:
            if apply_color == "y":
                grayscale_img = Image.open(img_path).convert("L")
                color_img = Image.open(img_path).convert("RGB")
            else:
                grayscale_img = Image.open(img_path).convert("L")
                grayscale_img = auto_adjust_brightness_contrast(grayscale_img)
                color_img = Image.open(img_path).convert("RGB")

        # Now resize and convert (applies to both branches)
        grayscale_img = resize_image(grayscale_img, width)
        if apply_color == "y":
            color_img = resize_image(color_img, width)
        ascii_art = image_to_ascii(grayscale_img, custom_chars) 
        
        # Save files with real-time progress
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        font_size = 10
        
        print("\n⏳ Processing and saving files...")
        output_paths = save_all_files(
            ascii_art, output_dir, base_filename, mode_choice,
            font_path, font_size, apply_color, color_img, width, selected_formats
        )
        
        def get_file_size(path):
            if os.path.exists(path):
                size = os.path.getsize(path)
                if size < 1024:
                    return f"{size} bytes"
                elif size < 1024*1024:
                    return f"{size/1024:.1f} KB"
                else:
                    return f"{size/(1024*1024):.1f} MB"
            return "N/A"
        
        print("\n✅ Conversion Summary:")
        print("="*60)
        print(f"Source Image: {os.path.basename(img_path)}")
        print(f"ASCII Width: {width} characters")
        print(f"Color Mode: {'Enabled' if apply_color == 'y' else 'Disabled'}")
        print(f"ASCII Style: {mode_choice.capitalize()}")
        print("\nOutput Files:")
        for path in output_paths:
            print(f"• {path} ({get_file_size(path)})")
        print("="*60)
        
        another = input("\nWould you like to make another ASCII art? (Y/n): ").strip().lower() or "y"
        if another != "y":
            print("\n🎉 Thank you for using the ASCII Image Converter! Exiting...\n")
            break

if __name__ == "__main__":
    main()
