import re
import os
import shutil

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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
    """Extracts BG, FG, Primary, and OnPrimary colors from DMS Matugen config."""
    bg, fg, primary, on_primary = "#0e1415", "#dee4e4", "#81d4dc", "#00363b" # Fallbacks
    
    if os.path.exists(DMS_COLORS_PATH):
        with open(DMS_COLORS_PATH, 'r') as f:
            content = f.read()
            
        match = re.search(r'active_colors=([^,\n]+),\s*([^,\n]+)', content)
        if match:
            fg = match.group(1).strip()
            bg = match.group(2).strip()
            
        primary_match = re.search(r'DecorationFocus=(\d+),(\d+),(\d+)', content)
        if primary_match:
            r, g, b = primary_match.groups()
            primary = f"#{int(r):02x}{int(g):02x}{int(b):02x}"

        # Try to find OnPrimary from Selection Foreground
        on_primary_match = re.search(r'\[Colors:Selection\].*?ForegroundNormal=(\d+),(\d+),(\d+)', content, re.DOTALL)
        if on_primary_match:
            r, g, b = on_primary_match.groups()
            on_primary = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            
    return bg, fg, primary, on_primary

def update_svg_paths(path, radius, primary_color, bg_color=None, border_width="1", is_panel=True):
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        content = f.read()
    
    # Scale border width slightly for the small 48x48 SVG
    # If Niri uses 2px, we use 1px here as a good balance
    w = float(border_width) * 0.5
    m = w / 2.0
    s = 48 - w
    r = float(radius)
    
    new_path = f"M {m+r},{m} h {s-2*r} a {r},{r} 0 0 1 {r},{r} v {s-2*r} a {r},{r} 0 0 1 -{r},{r} h -{s-2*r} a {r},{r} 0 0 1 -{r},-{r} v -{s-2*r} a {r},{r} 0 0 1 {r},-{r} z"
    
    content = re.sub(r'(<path[^>]+d=")[^"]+(")', rf'\1{new_path}\2', content)
    
    if is_panel:
        if bg_color:
            content = re.sub(r'fill:#?[a-fA-F0-9]+', f'fill:{bg_color}', content)
        if primary_color:
            content = re.sub(r'stroke:#?[a-fA-F0-9]+', f'stroke:{primary_color}', content)
            content = re.sub(r'stroke-width:[0-9.]+', f'stroke-width:{w}', content)
    else:
        if primary_color:
            content = re.sub(r'fill:#?[a-fA-F0-9]+', f'fill:{primary_color}', content)
            # Increase opacity slightly for better color matching
            content = re.sub(r'fill-opacity:[0-9.]+', 'fill-opacity:0.8', content)

    with open(path, 'w') as f:
        f.write(content)

def update_theme_conf(primary_color, fg_color, on_primary_color):
    if not os.path.exists(THEME_CONF_PATH): return
    with open(THEME_CONF_PATH, 'r') as f:
        content = f.read()
    
    # Update Colors
    content = re.sub(r'HighlightCandidateColor=#?[a-fA-F0-9]+', f'HighlightCandidateColor={on_primary_color}', content)
    content = re.sub(r'HighlightColor=#?[a-fA-F0-9]+', f'HighlightColor={primary_color}', content)
    content = re.sub(r'NormalColor=#?[a-fA-F0-9]+', f'NormalColor={fg_color}', content)
    content = re.sub(r'Name=.*', 'Name=DMS Niri', content)
    
    with open(THEME_CONF_PATH, 'w') as f:
        f.write(content)

def main():
    print("--- Fcitx5 Dank Material Shell Theme Sync ---")
    
    bg, fg, primary, on_primary = get_dms_theme_data()
    
    # Extract Layout Data
    radius = get_dms_value(DMS_LAYOUT_PATH, r'geometry-corner-radius\s+(\d+)')
    if not radius: radius = "12"
    
    border_width = get_dms_value(DMS_LAYOUT_PATH, r'width\s+(\d+)')
    if not border_width: border_width = "2"

    print(f"DMS Colors: BG={bg}, FG={fg}, Accent={primary}, OnAccent={on_primary}")
    print(f"DMS Layout: Radius={radius}, BorderWidth={border_width}")

    # 2. Update Files
    update_svg_paths(PANEL_SVG_PATH, radius, primary, bg, border_width, is_panel=True)
    update_svg_paths(HIGHLIGHT_SVG_PATH, radius, primary, bg, border_width, is_panel=False)
    update_theme_conf(primary, fg, on_primary)
    
    print("\nSuccess: Theme files optimized for visual consistency!")
    
    choice = input("Do you want to install this theme to ~/.local/share/fcitx5/themes/niri-dms? (y/N): ")
    if choice.lower() == 'y':
        try:
            if os.path.exists(INSTALL_PATH):
                if os.path.islink(INSTALL_PATH): os.unlink(INSTALL_PATH)
                else: shutil.rmtree(INSTALL_PATH)
            os.makedirs(os.path.dirname(INSTALL_PATH), exist_ok=True)
            shutil.copytree(THEME_DIR, INSTALL_PATH)
            print(f"Successfully installed to {INSTALL_PATH}")
            
            # 5. Optional Restart
            restart_choice = input("Do you want to restart Fcitx5 to apply the theme immediately? (y/N): ")
            if restart_choice.lower() == 'y':
                print("Restarting Fcitx5...")
                os.system("fcitx5 -r &")
                print("Fcitx5 is restarting in the background.")
        except Exception as e:
            print(f"Error during installation: {e}")
    else:
        print("Installation skipped.")

if __name__ == "__main__":
    main()
