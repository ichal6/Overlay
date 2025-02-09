import tkinter as tk
from tkinter import StringVar
import time
import threading
import pystray
from PIL import Image, ImageDraw

def create_overlay():
    # Create a new window
    overlay = tk.Tk()
    overlay.title("Always On-Screen Text")

    # Make the window transparent and always on top
    overlay.attributes('-topmost', True)
    overlay.attributes('-alpha', 0.7)  # 1.0 is opaque, 0.0 is fully transparent
    overlay.configure(bg="black")      # Background color for contrast

    # Remove window borders
    overlay.overrideredirect(True)

    # Get screen width and height
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()

    # Set the size and position (left bottom corner)
    overlay_width = 300
    overlay_height = 50
    x_position = 350  # Left edge
    y_position = screen_height - overlay_height - 50  # Bottom edge

    overlay.geometry(f"{overlay_width}x{overlay_height}+{x_position}+{y_position}")

    # Text variable for displaying time
    text_var = StringVar()

    def update_time():
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        text_var.set(current_time)
        overlay.after(1000, update_time)

    update_time()  # Start updating the time

    label = tk.Label(overlay, textvariable=text_var, fg="white", bg="black", font=("Arial", 16))
    label.pack(fill="both", expand=True)

    # Variables to track the state
    is_focusable = True  # True means the overlay is clickable
    is_on_top = True     # True means the overlay is always on top

    # Instruction label (used for blinking on toggle)
    instructions = tk.Label(
        overlay,
        text="Press 't' to toggle focus mode",
        fg="white",
        bg="black",
        font=("Arial", 10)
    )
    instructions.pack()

    # Function to toggle clickable (focusable) state
    def toggle_focus():
        nonlocal is_focusable
        try:
            if is_focusable:
                # Make non-focusable (click-through)
                overlay.attributes('-disabled', True)
                is_focusable = False
            else:
                # Make focusable again
                overlay.attributes('-disabled', False)
                overlay.lift()        # Bring window to the front
                overlay.focus_force() # Force focus
                is_focusable = True
        except Exception as e:
            print("Failed to toggle focusable mode:", e)
        blink_instructions()

    # Function to blink instructions in red
    def blink_instructions():
        def set_red():
            instructions.config(fg="red")
        def set_white():
            instructions.config(fg="white")
        overlay.after(100, set_red)
        overlay.after(300, set_white)
        overlay.after(500, set_red)
        overlay.after(700, set_white)

    # Function to toggle the always on top state
    def toggle_on_top():
        nonlocal is_on_top
        if is_on_top:
            overlay.attributes('-topmost', False)
            is_on_top = False
        else:
            overlay.attributes('-topmost', True)
            is_on_top = True

    # Bind the 't' key to toggle the clickable state
    overlay.bind('t', lambda event: toggle_focus())

    # Allow user to move the overlay by dragging with the mouse
    def start_drag(event):
        overlay.x = event.x
        overlay.y = event.y

    def drag(event):
        x = overlay.winfo_x() + event.x - overlay.x
        y = overlay.winfo_y() + event.y - overlay.y
        overlay.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_drag)
    label.bind("<B1-Motion>", drag)

    # --- Tray Icon Setup using pystray ---

    # Create a simple icon image for the tray
    def create_image():
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        dc = ImageDraw.Draw(image)
        # Draw a white rectangle as a simple design
        dc.rectangle(
            [width // 4, height // 4, width * 3 // 4, height * 3 // 4],
            fill='white'
        )
        return image

    # Container to hold the tray icon instance (so it can be stopped on exit)
    tray_icon_ref = [None]

    # Function to handle exit from the tray menu
    def on_exit():
        if tray_icon_ref[0]:
            tray_icon_ref[0].stop()  # Stop the tray icon
        overlay.destroy()            # Close the overlay window

    # Function to run the tray icon in its own thread
    def run_tray_icon():
        image = create_image()
        menu = pystray.Menu(
            pystray.MenuItem(
                'Clickable (t)',
                lambda: overlay.after(0, toggle_focus),
                # Check symbol: shows checked if overlay is clickable (focusable)
                checked=lambda item: is_focusable
            ),
            pystray.MenuItem(
                'On-top/normal',
                lambda: overlay.after(0, toggle_on_top),
                # Check symbol: shows checked if overlay is set as always on top
                checked=lambda item: is_on_top
            ),
            pystray.MenuItem(
                'Exit (ALT+F4)',
                lambda: overlay.after(0, on_exit)
            )
        )
        icon = pystray.Icon("overlay", image, "Overlay", menu)
        tray_icon_ref[0] = icon
        icon.run()

    # Start the tray icon in a separate daemon thread
    tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
    tray_thread.start()

    # Start Tkinter's event loop
    overlay.mainloop()

if __name__ == "__main__":
    create_overlay()
