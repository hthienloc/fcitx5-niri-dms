# Fcitx5 Niri DMS Theme

A dynamic Fcitx5 theme that automatically synchronizes with **Dank Material Shell (DMS)** and **Matugen** colors/layout.

Inherits the sleek border style from [Ori-fcitx5](https://github.com/Reverier-Xu/Ori-fcitx5) but adds dynamic capabilities.

## Features

- **Color Sync:** Automatically pulls Background, Foreground, and Primary (Accent) colors from Matugen (`qt6ct/matugen.conf`).
- **Layout Sync:** Matches the `geometry-corner-radius` defined in your DMS layout.
- **Easy Installation:** Interactive script to generate and install the theme locally.

## Requirements

- Fcitx5
- Dank Material Shell (for color/layout sources)
- Python 3

## Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/hthienloc/fcitx5-niri-dms.git
   cd fcitx5-niri-dms
   ```

2. Run the generator script:
   ```bash
   python3 generate.py
   ```

3. Follow the prompt to install the theme to `~/.local/share/fcitx5/themes/niri-dms`.

4. Open **Fcitx5 Configuration** and navigate to:
   `Addons` > `Classic User Interface` (click Configure) > `Theme` (or `Dark Theme`) > Select **DMS Niri**.

## Credits

- Base SVG assets and layout ideas from [Ori-fcitx5](https://github.com/Reverier-Xu/Ori-fcitx5).
- Designed for use with [Dank Material Shell](https://github.com/hthienloc/DankMaterialShell).
