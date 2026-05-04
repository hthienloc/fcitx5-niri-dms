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

# Tune highlight size (px)
HIGHLIGHT_V_PADDING = 2
HIGHLIGHT_H_PADDING = 1

# Override border thickness (px). None = lấy từ layout.kdl
PANEL_BORDER_WIDTH_OVERRIDE = 4


def get_dms_value(path, key_pattern):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        content = f.read()
    match = re.search(key_pattern, content)
    return match.group(1) if match else None


def get_dms_theme_data():
    """Extracts BG, FG, Primary, and OnPrimary colors from DMS Matugen config."""
    bg, fg, primary, on_primary = "#0e1415", "#dee4e4", "#81d4dc", "#00363b"  # Fallbacks

    if not os.path.exists(DMS_COLORS_PATH):
        return bg, fg, primary, on_primary

    with open(DMS_COLORS_PATH, "r") as f:
        content = f.read()

    match = re.search(r"active_colors=([^,\n]+),\s*([^,\n]+)", content)
    if match:
        fg = match.group(1).strip()
        bg = match.group(2).strip()

    primary_match = re.search(r"DecorationFocus=(\d+),(\d+),(\d+)", content)
    if primary_match:
        r, g, b = primary_match.groups()
        primary = f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    on_primary_match = re.search(
        r"\[Colors:Selection\].*?ForegroundNormal=(\d+),(\d+),(\d+)", content, re.DOTALL
    )
    if on_primary_match:
        r, g, b = on_primary_match.groups()
        on_primary = f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    return bg, fg, primary, on_primary


def build_rounded_rect_path(svg_size, border_width, radius, v_padding=0, h_padding=0):
    """Returns an SVG path string for a rounded rectangle with optional padding."""
    w = float(border_width) * 0.5
    m = w / 2.0
    r = float(radius)

    x = m + h_padding
    y = m + v_padding
    width = svg_size - w - 2 * h_padding
    height = svg_size - w - 2 * v_padding

    # Clamp radius so it never exceeds half of the smaller dimension
    r = min(r, width / 2, height / 2)

    return (
        f"M {x+r},{y} "
        f"h {width-2*r} a {r},{r} 0 0 1 {r},{r} "
        f"v {height-2*r} a {r},{r} 0 0 1 -{r},{r} "
        f"h -{width-2*r} a {r},{r} 0 0 1 -{r},-{r} "
        f"v -{height-2*r} a {r},{r} 0 0 1 {r},-{r} z"
    )


def update_svg_paths(path, radius, primary_color, bg_color=None, border_width="1",
                     is_panel=True, v_padding=0, h_padding=0):
    if not os.path.exists(path):
        print(f"Warning: {path} not found, skipping.")
        return

    with open(path, "r") as f:
        content = f.read()

    w = float(border_width) * 0.5
    new_path = build_rounded_rect_path(48, w * 2, radius, v_padding, h_padding)

    content = re.sub(r'(<path[^>]+d=")[^"]+(")', rf"\1{new_path}\2", content)

    if is_panel:
        if bg_color:
            content = re.sub(r"fill:#?[a-fA-F0-9]+", f"fill:{bg_color}", content)
        if primary_color:
            content = re.sub(r"stroke:#?[a-fA-F0-9]+", f"stroke:{primary_color}", content)
            content = re.sub(r"stroke-width:[0-9.]+", f"stroke-width:{w}", content)
    else:
        if primary_color:
            content = re.sub(r"fill:#?[a-fA-F0-9]+", f"fill:{primary_color}", content)
            content = re.sub(r"fill-opacity:[0-9.]+", "fill-opacity:0.8", content)

    with open(path, "w") as f:
        f.write(content)


def update_theme_conf(primary_color, fg_color, on_primary_color):
    if not os.path.exists(THEME_CONF_PATH):
        print(f"Warning: {THEME_CONF_PATH} not found, skipping.")
        return

    with open(THEME_CONF_PATH, "r") as f:
        content = f.read()

    content = re.sub(r"HighlightCandidateColor=#?[a-fA-F0-9]+", f"HighlightCandidateColor={on_primary_color}", content)
    content = re.sub(r"HighlightColor=#?[a-fA-F0-9]+", f"HighlightColor={primary_color}", content)
    content = re.sub(r"NormalColor=#?[a-fA-F0-9]+", f"NormalColor={fg_color}", content)
    content = re.sub(r"Name=.*", "Name=DMS Niri", content)
    content = re.sub(r"ScaleWithDPI=.*", "ScaleWithDPI=True", content)

    with open(THEME_CONF_PATH, "w") as f:
        f.write(content)


def install_theme():
    try:
        if os.path.exists(INSTALL_PATH):
            if os.path.islink(INSTALL_PATH):
                os.unlink(INSTALL_PATH)
            else:
                shutil.rmtree(INSTALL_PATH)
        os.makedirs(os.path.dirname(INSTALL_PATH), exist_ok=True)
        shutil.copytree(THEME_DIR, INSTALL_PATH)
        print(f"Installed → {INSTALL_PATH}")
    except Exception as e:
        print(f"Install failed: {e}")
        return False
    return True


def restart_fcitx5():
    print("Restarting fcitx5...")
    os.system("pkill fcitx5; sleep 0.5; fcitx5 -d &")
    print("fcitx5 restarted.")


def main():
    print("--- Fcitx5 DMS Theme Sync ---")

    bg, fg, primary, on_primary = get_dms_theme_data()

    radius = get_dms_value(DMS_LAYOUT_PATH, r"geometry-corner-radius\s+(\d+)") or "12"
    border_width = get_dms_value(DMS_LAYOUT_PATH, r"width\s+(\d+)") or "2"
    if PANEL_BORDER_WIDTH_OVERRIDE is not None:
        border_width = str(PANEL_BORDER_WIDTH_OVERRIDE)

    print(f"Colors : BG={bg}  FG={fg}  Accent={primary}  OnAccent={on_primary}")
    print(f"Layout : radius={radius}  border={border_width}")
    print(f"Padding: v={HIGHLIGHT_V_PADDING}  h={HIGHLIGHT_H_PADDING}")

    highlight_radius = max(0, float(radius) - max(HIGHLIGHT_V_PADDING, HIGHLIGHT_H_PADDING))

    update_svg_paths(PANEL_SVG_PATH, radius, primary, bg, border_width,
                     is_panel=True)
    update_svg_paths(HIGHLIGHT_SVG_PATH, highlight_radius, primary, bg, border_width,
                     is_panel=False,
                     v_padding=HIGHLIGHT_V_PADDING,
                     h_padding=HIGHLIGHT_H_PADDING)
    update_theme_conf(primary, fg, on_primary)

    print("Theme files updated.")

    if input("\nInstall to ~/.local/share/fcitx5/themes/niri-dms? (y/N): ").lower() == "y":
        if install_theme():
            if input("Restart fcitx5 now? (y/N): ").lower() == "y":
                restart_fcitx5()
    else:
        print("Install skipped.")


if __name__ == "__main__":
    main()