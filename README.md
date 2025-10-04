# Advanced ASCII Image Converter - Free Python ASCII Art Generator

![Demo](https://github.com/jo4dan/advanced-ascii/releases/download/v1.0/Demo.gif)

Transform images into stunning ASCII art with this advanced, interactive Python tool. Featuring retro 16-bit pixel art styles, color support, live previews, and multiple output formats, it's the ultimate free ASCII image converter for developers, artists, and retro gaming enthusiasts.

[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-red.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![PyPI](https://img.shields.io/badge/pip-install%20advanced--ascii-brightgreen)](https://pypi.org/project/advanced-ascii/)
[![GitHub](https://img.shields.io/github/stars/jo4dan/advanced-ascii?style=social)](https://github.com/jo4dan/advanced-ascii)

## Table of Contents
- [Features](#features)
  - [Core Conversion and Processing Features](#core-conversion-and-processing-features)
  - [Retro 16-Bit Mode Details](#retro-16-bit-mode-details)
  - [Interactive User Interface Features](#interactive-user-interface-features)
  - [Output and Saving Features](#output-and-saving-features)
  - [Advanced Technical Features](#advanced-technical-features)
- [Installation](#installation)
  - [Quick Install (Recommended)](#quick-install-recommended)
  - [Install from Source](#install-from-source)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Step-by-Step User-Friendly Instructions](#step-by-step-user-friendly-instructions)
- [ASCII Art Modes](#ascii-art-modes)
- [Output Formats](#output-formats)
- [Examples](#examples)
  - [Monochrome Mode Output](#monochrome-mode-output)
  - [16-Bit Retro Example](#16-bit-retro-example)
  - [Sample Session](#sample-session)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features

This advanced ASCII image converter is designed to stand out among other ASCII tools on GitHub by offering a rich set of features that combine ease of use with powerful customization. It's perfect for creating high-quality ASCII art from images, with support for retro effects, interactive interfaces, and efficient processing.

### Core Conversion and Processing Features

The tool excels in transforming images into ASCII art with advanced image handling techniques:

- **Diverse ASCII Art Styles**: Choose from six density modes for tailored rendering, including monochrome, block characters, dots, alphanumeric, custom sets, and a unique 16-bit retro mode inspired by NES box art.
- **Smart Image Search**: Automatically scans common directories (e.g., ~/Pictures, ~/Downloads, ~/Desktop, ~) to locate image files by name, supporting formats like PNG, JPG, JPEG, WEBP, BMP, TIFF, and GIF.
- **Auto Brightness and Contrast Adjustment**: Uses OpenCV's CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance image details automatically for superior ASCII output quality.
- **Aspect Ratio Maintenance**: Resizes images while preserving the original aspect ratio, with height adjusted to approximately 50% of width for optimal ASCII character proportions.
- **Grayscale to ASCII Mapping**: Converts pixel intensities to ASCII characters with density-based selection, including optional progress callbacks for monitoring during conversion.
- **Color Preservation**: Optionally maps original RGB pixel colors to ASCII characters in outputs, with ANSI escape codes for terminal previews and full support in saved files.

### Retro 16-Bit Mode Details

One of the tool's standout features is its dedicated 16-bit mode, which brings nostalgic gaming aesthetics to ASCII art:

- **Image Downscaling and Pixelation**: Automatically resizes to a low-resolution 128x128 grid using nearest-neighbor interpolation via OpenCV for a crisp, blocky retro look.
- **16-Color Palette Quantization**: Maps colors to a vibrant NES-inspired palette (16 colors, e.g., bold red, vivid orange, cyan teal) using Euclidean distance calculations to find the nearest match.
- **CRT Scanline Simulation**: Applies subtle alternating dimming (10% on even rows) to mimic old CRT monitor effects, enhancing the 80s gaming nostalgia.
- **Palette Customization Potential**: The palette is defined in code as a list of RGB tuples, allowing easy tweaks for different retro styles (e.g., Contra fire reds, Zelda greens).

This mode makes the tool SEO-friendly for queries like "retro NES ASCII art generator" or "pixelated ASCII converter."

### Interactive User Interface Features

The tool prioritizes user-friendliness with a terminal-based interface that's intuitive and engaging:

- **Single-Key Press Detection**: Utilizes termios and tty modules to capture key inputs (e.g., arrows, space, enter) without requiring Enter, for seamless navigation.
- **Curses-Based Format Selection Menu**: An interactive menu with highlighted selections, checkboxes ([✓] or [ ]), and validation (requires at least one format; shows error if none selected).
- **Settings Summary and Confirmation Prompt**: Displays a boxed summary of choices (image, width, color mode, style, formats) and requires user confirmation before proceeding.
- **Live Terminal Preview**: Renders a scaled-down ASCII art (max 100 characters wide) line-by-line with a 0.02-second delay for a "live rendering" effect; supports colored ANSI previews.
- **Batch Conversion Loop**: Enables multiple conversions in one session via a "Would you like to make another?" prompt, streamlining workflows.
- **Signal Handling for Graceful Exit**: Catches Ctrl+C (SIGINT) with a custom handler to print a friendly exit message and terminate cleanly.

### Output and Saving Features

Saving is flexible and user-centric, with real-time feedback:

- **Multi-Format Exports**: Saves to PNG, TIFF, SVG, HTML, or ASC (plain text) files, each with mode-specific backgrounds (e.g., black for 16-bit, white for block).
- **Font Rendering**: Uses PIL for image/SVG outputs with monospace fonts (defaults to DejaVuSansMono at size 10; falls back to default if not found).
- **Real-Time Progress Tracker**: A threaded class with locking for safe updates, displaying a progress bar, per-task percentages, and ETA calculated via timedelta.
- **File Organization**: Creates a dedicated output directory (e.g., {base_filename}_ascii/) and reports file paths with sizes (bytes/KB/MB) in a post-conversion summary.
- **Colored Output Support**: Applies colors via RGB fills in images/SVG, spans in HTML, and ANSI in previews; quantizes in 16-bit mode.

### Advanced Technical Features

For developers and tinkerers:

- **Custom Character Sets**: In custom mode, users input characters (dark to light); falls back to monochrome if empty.
- **Progress Callbacks**: Integrated in conversion and saving functions for detailed tracking.
- **Threading Safety**: Uses threading.Lock to handle concurrent progress updates.
- **ANSI Color Building for Console**: Constructs colored terminal lines by mapping pixels to escape codes.
- **Input Validation**: Checks file extensions, handles empty inputs, and provides error messages (e.g., "Invalid file extension").

These features ensure the tool is more comprehensive than basic ASCII converters, optimizing for searches like "advanced Python ASCII art tool with progress bar."

## Installation

### Quick Install (Recommended)

Install directly from PyPI using pip:

```bash
pip install advanced-ascii
```

### Install from Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/jo4dan/advanced-ascii.git
cd advanced-ascii
pip install -r requirements.txt
```

Or install dependencies manually:

```bash
pip install opencv-python numpy pillow
```

### Prerequisites

- **Python 3.8 or higher**
- **Required libraries**: OpenCV (cv2), NumPy, Pillow (PIL)
- **Standard libraries**: curses, termios, threading (included with Python)

**Note**: On Windows, install `windows-curses` for curses support:
```bash
pip install windows-curses
```

Tested on Linux/macOS; use WSL for Windows if issues arise.

## Usage

Run the tool with this command:

```bash
python advanced_ascii.py
```

Or if installed via pip:

```bash
advanced-ascii
```

### Step-by-Step User-Friendly Instructions

1. **Enter Image File Name**: Provide the filename (e.g., cat.jpg); it auto-searches common folders. If not found, retry with a valid extension.
2. **Set ASCII Width**: Input a number (default: 100 characters) for output width.
3. **Choose ASCII Mode**: Select 1-6 (e.g., 6 for 16-bit); see table below for details.
4. **Apply Color**: Answer Y/n (default: Y) to enable color mapping.
5. **Select Output Formats**: Use the curses menu—UP/DOWN to navigate, SPACE to toggle, ENTER to confirm, Q to quit. Must select at least one.
6. **Review and Confirm**: Check the settings summary; proceed with Y/n.
7. **View Live Preview**: Watch the terminal render the ASCII art.
8. **Monitor Progress**: See the real-time bar with ETA as files save.
9. **Review Summary**: Get file paths and sizes; opt to convert another.
10. **Exit Gracefully**: Ctrl+C anytime for a clean shutdown.

This flow makes it easy for beginners while powerful for pros.

## ASCII Art Modes

Customize with these modes for different visual effects:

| Mode | Characters (Dark → Light) | Best For |
|------|---------------------------|----------|
| **Monochrome** | `@` `%` `#` `*` `+` `=` `-` `:` `.` ` ` | Classic detailed grayscale |
| **Block** | `█` `▓` `▒` `░` ` ` | Bold, graphic designs |
| **Dots** | `•` `·` ` ` | Minimalist, subtle art |
| **Alphanumeric** | `a-z` `A-Z` `9-0` `?` `!` `;` `:` `,` `.` ` ` | Text-like, readable outputs |
| **Custom** | User-defined (specify dark to light order) | Personalized character sets |
| **16-Bit** | `█` `▓` `▒` `░` `▀` `▄` | Retro pixelated NES-style art |

## Output Formats

Interactively select these formats:

- **PNG**: Raster image with font rendering and colors.
- **TIFF**: High-quality image for archiving.
- **SVG**: Vector for scalable art.
- **HTML**: Web-ready with CSS and colored spans.
- **ASC**: Plain text for terminal or sharing.

All support colors and custom backgrounds.

## Examples

### Monochrome Mode Output

```text
@%#*+=-:. 
... (ASCII art lines here)
```

### 16-Bit Retro Example

(Visualize a pixelated scene with scanlines and vibrant palette.)

### Sample Session

```text
Enter the image file name: example.jpg
Enter ASCII width (default: 100): 80
Select (1-6, or default: Monochrome): 6
Apply color to saved ASCII? (Y/n): y
... (menu selects PNG, HTML)
Proceed with these settings? (Y/n): y
... (preview and progress)
✅ Conversion Summary: Files in example_ascii/
```

Add screenshots to an `examples/` folder for visuals.

## Configuration Options

- **Width**: Controls detail level; edit in input prompt.
- **Font**: Change `font_path` and `font_size` in code (default: DejaVuSansMono, 10).
- **Color Toggle**: Enables RGB/quantized mapping.
- **Directories/Palette**: Modify `COMMON_DIRS` or palette list in code.
- **Progress ETA**: Uses `datetime.timedelta` for estimates.

Edit `advanced_ascii.py` for tweaks like adding dithering.

## Troubleshooting

- **File Not Found**: Check directories or add to `COMMON_DIRS`.
- **Dependency Missing**: Rerun `pip install`; verify Python version.
- **Curses Errors**: On Windows, use `windows-curses` or WSL.
- **Slow Performance**: Reduce width for large images.
- **Font Issues**: Set `font_path` to a valid TTF file.

File bugs on [GitHub Issues](https://github.com/jo4dan/advanced-ascii/issues).

## Contributing

Fork, branch, and PR! Welcome: bug fixes, new modes, docs. Follow PEP8.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

GPL-3.0 License - see [LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html) for details.

## Credits

Built by [jo4dan](https://github.com/jo4dan). Inspired by retro ASCII tools with modern twists & VIBE CODING.

Star if useful! ⭐ Questions: [GitHub Issues](https://github.com/jo4dan/advanced-ascii/issues) or [jordannissi7@gmail.com](mailto:jordannissi7@gmail.com).

---

**SEO Keywords**: free ASCII art generator Python, convert image to ASCII text, retro 16-bit ASCII tool, command-line image converter, GitHub ASCII art creator, colored ASCII art software, NES-inspired ASCII generator, terminal ASCII art tool, Python ASCII converter, pixel art to ASCII
)
