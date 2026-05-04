import re
import os
import shutil

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# DMS / Matugen Source of Truth
DMS_COLORS_PATH = os.path.expanduser("~/.config/qt6ct/colors/matugen.conf")
DMS_LAYOUT_PATH = os.path.expanduser("~/.config/niri/dms/layout.kdl")

THEME_DIR = os.path.join(SCRIPT_DIR, "niri")
THEME_CONF_PATH = os.path.join(THEME_DIR, "theme.conf")
PANEL_SVG_PATH = os.path.join(THEME_DIR, "panel.svg")
HIGHLIGHT_SVG_PATH = os.path.join(THEME_DIR, "highlight.svg")
INSTALL_PATH = os.path.expanduser("~/.local/share/fcitx5/themes/niri-dms")

def get_dms_value(path, key_pattern):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        content = f.read()
    match = re.search(key_pattern, content)
    return match.group(1) if match else None

def get_dms_theme_data():
    """Extracts BG, FG, and Primary colors from DMS Matugen config."""
    bg, fg, primary = "#0e1415", "#dee4e4", "#81d4dc" # Fallbacks
    
    if os.path.exists(DMS_COLORS_PATH):
        with open(DMS_COLORS_PATH, 'r') as f:
            content = f.read()
            
        # 1. Extract FG and BG from active_colors line
        match = re.search(r'active_colors=([^,\n]+),\s*([^,\n]+)', content)
        if match:
            fg = match.group(1).strip()
            bg = match.group(2).strip()
            
        # 2. Extract Primary (DecorationFocus)
        # Format: DecorationFocus=R,G,B
        primary_match = re.search(r'DecorationFocus=(\d+),(\d+),(\d+)', content)
        if primary_match:
            r, g, b = primary_match.groups()
            primary = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            
    return bg, fg, primary

def update_svg_paths(path, radius, primary_color, bg_color=None, is_panel=True):
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        content = f.read()
    
    m = 0.5
    s = 48 - m*2
    r = float(radius)
    
    # Path for a rounded rectangle
    new_path = f"M {m+r},{m} h {s-2*r} a {r},{r} 0 0 1 {r},{r} v {s-2*r} a {r},{r} 0 0 1 -{r},{r} h -{s-2*r} a {r},{r} 0 0 1 -{r},-{r} v -{s-2*r} a {r},{r} 0 0 1 {r},-{r} z"
    
    # Replace the 'd' attribute
    content = re.sub(r'(<path[^>]+d=")[^"]+(")', rf'\1{new_path}\2', content)
    
    if is_panel:
        if bg_color:
            content = re.sub(r'fill:#?[a-fA-F0-9]+', f'fill:{bg_color}', content)
        if primary_color:
            content = re.sub(r'stroke:#?[a-fA-F0-9]+', f'stroke:{primary_color}', content)
    else:
        if primary_color:
            content = re.sub(r'fill:#?[a-fA-F0-9]+', f'fill:{primary_color}', content)
            content = re.sub(r'fill-opacity:[0-9.]+', 'fill-opacity:0.3', content)

    with open(path, 'w') as f:
        f.write(content)

def update_theme_conf(primary_color, fg_color):
    if not os.path.exists(THEME_CONF_PATH): return
    with open(THEME_CONF_PATH, 'r') as f:
        content = f.read()
    
    # Update text and highlight colors
    content = re.sub(r'HighlightCandidateColor=#?[a-fA-F0-9]+', f'HighlightCandidateColor={fg_color}', content)
    content = re.sub(r'HighlightColor=#?[a-fA-F0-9]+', f'HighlightColor={primary_color}', content)
    content = re.sub(r'NormalColor=#?[a-fA-F0-9]+', f'NormalColor={fg_color}', content)
    content = re.sub(r'Name=.*', 'Name=DMS Niri Theme', content)
    
    with open(THEME_CONF_PATH, 'w') as f:
        f.write(content)

def main():
    print("--- Fcitx5 Dank Material Shell Theme Sync ---")
    
    # 1. Extract Data from DMS
    bg, fg, primary = get_dms_theme_data()
    radius = get_dms_value(DMS_LAYOUT_PATH, r'geometry-corner-radius\s+(\d+)')
    if not radius: radius = "12"

    print(f"DMS Colors: BG={bg}, FG={fg}, Primary={primary}")
    print(f"DMS Layout: Radius={radius}")

    # 2. Update Files
    update_svg_paths(PANEL_SVG_PATH, radius, primary, bg, is_panel=True)
    update_svg_paths(HIGHLIGHT_SVG_PATH, radius, primary, bg, is_panel=False)
    update_theme_conf(primary, fg)
    
    print("\nSuccess: Theme files updated to match Dank Material Shell!")
    
    # 3. Interactive Install
    choice = input("Do you want to install this theme to ~/.local/share/fcitx5/themes/niri-dms? (y/N): ")
    if choice.lower() == 'y':
        try:
            if os.path.exists(INSTALL_PATH):
                if os.path.islink(INSTALL_PATH): os.unlink(INSTALL_PATH)
                else: shutil.rmtree(INSTALL_PATH)
            os.makedirs(os.path.dirname(INSTALL_PATH), exist_ok=True)
            shutil.copytree(THEME_DIR, INSTALL_PATH)
            print(f"Successfully installed to {INSTALL_PATH}")
        except Exception as e:
            print(f"Error during installation: {e}")
    else:
        print("Installation skipped.")

if __name__ == "__main__":
    main()
