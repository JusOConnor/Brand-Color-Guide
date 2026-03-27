# Required Notice: Copyright Justin O'Connor
# Licensed under the PolyForm Noncommercial License 1.0.0.
# See LICENSE file in the project root or https://polyformproject.org/licenses/noncommercial/1.0.0/

import tkinter as tk
from tkinter import ttk
import os
import sys
import Tcl

def copy_to_clipboard(value):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.clipboard_clear()
    root.clipboard_append(value)
    root.update()  # Keep the clipboard value until the application closes
    root.destroy()

def hide_terminal():
    if os.name == 'nt':  # Check if the operating system is Windows
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def get_fg_color(hex_value):
    hex_clean = hex_value.lstrip('#').strip()
    if len(hex_clean) == 3:
        hex_clean = ''.join(c*2 for c in hex_clean)
    r = int(hex_clean[0:2], 16) / 255
    g = int(hex_clean[2:4], 16) / 255
    b = int(hex_clean[4:6], 16) / 255
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 'white' if luminance < 0.5 else 'black'

def create_gui(data):
    root = tk.Tk()
    root.title('Brand Color Guide')

    # Set the background and text color of the window
    root.configure(bg='black')
    

    for palette_name, categories in data.items():
        # Add a header for the Palette
        # header = ttk.Label(root, text=palette_name, font=('Arial', 14, 'bold'))
        header = ttk.Label(root, text=palette_name, font=('Arial', 14, 'bold'), background='black', foreground='white')
        header.pack(pady=(10, 5))
        spacer = tk.Frame(root, height=2.5, bg=root.cget('bg'))
        spacer.pack(side='bottom')

        for category_name, hex_values in categories.items():
            # Add a sub-header for the Category
            # subheader = ttk.Label(root, text=category_name, font=('Arial', 12))
            subheader = ttk.Label(root, text=category_name, font=('Arial', 12), background='black', foreground='white')
            subheader.pack(pady=(5, 2))

            # Create a frame for HEX buttons
            button_frame = tk.Frame(root)
            button_frame.pack(pady=5)

            for hex_value in hex_values:
                button = tk.Button(
                    button_frame,
                    text=hex_value,
                    bg=hex_value,
                    fg='white' if int(hex_value[1:], 16) < 0x888888 else 'black',
                    # fg=get_fg_color(hex_value),
                    width=10,
                    command=lambda hv=hex_value: copy_to_clipboard(hv)
                )
                button.pack(side=tk.LEFT, padx=2)

    root.mainloop()

# Sample data structure for the GUI
data = {
    'Color Palette': {
        'Main Colors': ['#003366', '#4D9DE0', '#E84855'],
        '': ['#F4A261', '#2EC4B6', '#C62A47', '#6B3FA0', '#3D3D3D', '#C8CACC']
    },
    'Web Color Palette': {
        'Main Web Colors': ['#001F4D', '#003366', '#1A79C4'],
        'Secondary Web Colors': ['#4D9DE0', '#7BB8ED', '#B0B5BA', '#E84855', '#F07C84']
    },
}
hide_terminal()
create_gui(data)
