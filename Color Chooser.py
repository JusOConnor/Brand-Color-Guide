# Required Notice: Copyright Justin O'Connor
# Licensed under the PolyForm Noncommercial License 1.0.0.
# See LICENSE file in the project root or https://polyformproject.org/licenses/noncommercial/1.0.0/

import os
import sys
import tkinter as tk
import customtkinter as ctk

# ── Button size controls ───────────────────────────────────────────────────────
BUTTON_WIDTH  = 60  # px — width of each color button
BUTTON_HEIGHT = 36  # px — height of each color button
BUTTON_GAP    = 6   # px — spacing between buttons in a row
# ──────────────────────────────────────────────────────────────────────────────

# Layout padding (px)
WINDOW_PADDING = 10


def copy_to_clipboard(window, value):
    window.clipboard_clear()
    window.clipboard_append(value)
    window.update()


def hide_terminal():
    if os.name == 'nt':  # Windows
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    elif sys.platform == 'darwin':  # macOS
        import subprocess
        subprocess.run(
            ['osascript', '-e', 'tell application "Terminal" to set visible of front window to false'],
            capture_output=True
        )
    elif sys.platform.startswith('linux'):  # Linux (X11)
        try:
            import subprocess
            window_id = subprocess.check_output(['xdotool', 'getactivewindow']).strip()
            subprocess.run(['xdotool', 'windowunmap', window_id])
        except Exception:
            pass  # xdotool may not be installed; fail silently


def get_fg_color(hex_value):
    hex_clean = hex_value.lstrip('#').strip()
    if len(hex_clean) == 3:
        hex_clean = ''.join(c * 2 for c in hex_clean)
    r = int(hex_clean[0:2], 16) / 255
    g = int(hex_clean[2:4], 16) / 255
    b = int(hex_clean[4:6], 16) / 255
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return '#ffffff' if luminance < 0.5 else '#000000'


def create_gui(data):
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')

    # Disable customtkinter's built-in Windows DPI scaling — it conflicts with
    # tkinter's own scaling and causes the oversized layout
    if os.name == 'nt':
        ctk.deactivate_automatic_dpi_awareness()

    window = ctk.CTk()
    window.title('Brand Color Guide')
    window.configure(fg_color='#000000')

    # Canvas + inner frame for scroll support without a visible scrollbar
    canvas = tk.Canvas(window, bg='#000000', highlightthickness=0, borderwidth=0)
    canvas.pack(fill='both', expand=True)

    inner = ctk.CTkFrame(canvas, fg_color='#000000', corner_radius=0)
    canvas_window = canvas.create_window((0, 0), window=inner, anchor='n')

    # Keep inner frame centered as window width changes
    def on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind('<Configure>', on_canvas_resize)

    # Enable mousewheel scrolling without a visible scrollbar
    def on_mousewheel(event):
        if sys.platform == 'darwin':
            canvas.yview_scroll(-1 * int(event.delta), 'units')
        else:
            canvas.yview_scroll(-1 * int(event.delta / 120), 'units')
    canvas.bind_all('<MouseWheel>', on_mousewheel)

    outer = ctk.CTkFrame(inner, fg_color='#000000', corner_radius=0)
    outer.pack(fill='both', expand=True, padx=WINDOW_PADDING, pady=(4, WINDOW_PADDING))

    # Palette section
    for palette_index, (palette_name, categories) in enumerate(data.items()):
        if palette_name:
            # Thick separator row between palettes but not before the first one
            if palette_index > 0:
                ctk.CTkFrame(outer, height=3, fg_color='#333333', corner_radius=0).pack(fill='x', pady=(6, 6))

            header = ctk.CTkLabel(
                outer,
                text=palette_name.upper(),
                font=ctk.CTkFont(family='Helvetica Neue', size=14, weight='bold'),
                text_color='#ffffff',
                anchor='n'
            )
            header.pack(fill='x', pady=(0,0))

            divider = ctk.CTkFrame(outer, height=1, fg_color='#333333', corner_radius=0)
            divider.pack(fill='x', pady=(0, 4))

        # Category section
        for category_name, hex_values in categories.items():
            if category_name:
                subheader = ctk.CTkLabel(
                    outer,
                    text=category_name.upper(),
                    font=ctk.CTkFont(family='Helvetica Neue', size=11),
                    text_color='#aaaaaa',
                    anchor='n',
                    height=16,
                )
                subheader.pack(fill='x', pady=(3, 0))

            button_row = ctk.CTkFrame(outer, fg_color='#000000', corner_radius=0)
            button_row.pack(anchor='center', pady=(0 if category_name else BUTTON_GAP // 2, BUTTON_GAP // 2))

            for i, hex_value in enumerate(hex_values):
                fg = get_fg_color(hex_value)

                btn = ctk.CTkButton(
                    button_row,
                    text=hex_value.upper(),
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    corner_radius=4,
                    fg_color=hex_value,
                    hover_color=hex_value,
                    text_color=fg,
                    font=ctk.CTkFont(family='Courier New', size=8, weight='bold'),
                    border_width=0,
                    anchor='center',
                )

                def make_hover_in(b):
                    def fn(e):
                        b.configure(border_width=2, border_color='#ffffff')
                    return fn

                def make_hover_out(b):
                    def fn(e):
                        b.configure(border_width=0)
                    return fn

                def make_copy_handler(hv, button):
                    def handler():
                        copy_to_clipboard(window, hv)
                        original = button.cget('text')
                        button.configure(text='Copied!')
                        window.after(1000, lambda: button.configure(text=original))
                    return handler

                btn.bind('<Enter>', make_hover_in(btn))
                btn.bind('<Leave>', make_hover_out(btn))
                btn.configure(command=make_copy_handler(hex_value, btn))
                btn.grid(row=0, column=i, padx=(0 if i == 0 else BUTTON_GAP, 0))

    # Update canvas scroll region whenever inner frame changes size
    def on_inner_resize(event):
        canvas.configure(scrollregion=canvas.bbox('all'))
    inner.bind('<Configure>', on_inner_resize)

    # Size window to content, capped at 90% screen height
    window.update_idletasks()
    content_w = outer.winfo_reqwidth() + WINDOW_PADDING * 2
    content_h = outer.winfo_reqheight() + WINDOW_PADDING * 2
    screen_h  = window.winfo_screenheight()
    capped_h  = min(content_h, int(screen_h * 0.9))

    window.resizable(False, False)
    window.geometry(f'{content_w}x{capped_h}')

    window.mainloop()


# ── Sample data ────────────────────────────────────────────────────────────────
COLORDATA = {
    'Color Palette': {
        'Main Colors': ['#003366', '#4D9DE0', '#E84855'],
        '': ['#F4A261', '#2EC4B6', '#C62A47', '#6B3FA0', '#3D3D3D', '#C8CACC']
    },
    'Web Color Palette': {
        'Main Web Colors': ['#001F4D', '#003366', '#1A79C4'],
        'Secondary Web Colors': ['#4D9DE0', '#7BB8ED', '#B0B5BA', '#E84855', '#F07C84']
    },
    # 'MORE COLORS': {
    #     'Yes please!' : ['#FF6A00', '#59C43E', '#A81B40', '#430491', '#000000', '#FFFFFF', '#304DCC', '#EBDB50']
    # },
}
# ──────────────────────────────────────────────────────────────────────────────

hide_terminal()
create_gui(COLORDATA)