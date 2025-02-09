import tkinter as tk
from tkinter import StringVar
import sys
import time

def create_overlay():
    # Create a new window
    overlay = tk.Tk()
    overlay.title("Always On-Screen Text")

    # Make the window transparent and always on top
    overlay.attributes('-topmost', True)
    overlay.attributes('-alpha', 0.7)  # Transparency (1.0 is opaque, 0.0 is fully transparent)
    overlay.configure(bg="black")  # Background color for better contrast

    # Remove window borders
    overlay.overrideredirect(True)

    # Get the screen width and height
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()

    # Set the size of the overlay window and position it at the left bottom corner
    overlay_width = 300
    overlay_height = 50
    x_position = 350  # Left edge
    y_position = screen_height - overlay_height - 50  # Bottom edge

    overlay.geometry(f"{overlay_width}x{overlay_height}+{x_position}+{y_position}")

    # Text to display
    text_var = StringVar()

    def update_time():
        # Get the current date and time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        text_var.set(current_time)  # Update the text variable
        overlay.after(1000, update_time)  # Schedule the next update after 1 second

    update_time()  # Initial call to display the time

    label = tk.Label(overlay, textvariable=text_var, fg="white", bg="black", font=("Arial", 16))
    label.pack(fill="both", expand=True)

    # Variable to track the focusable state
    is_focusable = True

    # Instructions for toggling
    instructions = tk.Label(
        overlay,
        text="Press 'T' to toggle focus mode",
        fg="white",
        bg="black",
        font=("Arial", 10)
    )
    instructions.pack()
    
    # Function to toggle focusable mode
    def toggle_focus():
        nonlocal is_focusable
        try:
            if is_focusable:
                # Try to make non-focusable
                overlay.attributes('-disabled', True)  # Make non-focusable
                is_focusable = False
            else:
                # Try to make focusable by lifting and forcing focus
                overlay.attributes('-disabled', False)  # Make focusable
                overlay.lift()  # Bring window to the front
                overlay.focus_force()  # Force focus on the window
                is_focusable = True
        except Exception as e:
            # Print the error if toggling fails
            print("Failed to toggle focusable mode:", e)

        # Blink the instructions in red to indicate the toggle
        blink_instructions()

    # Function to blink instructions in red
    def blink_instructions():
        def set_red():
            instructions.config(fg="red")
        def set_white():
            instructions.config(fg="white")

        # Blink twice
        overlay.after(100, set_red)  # Set to red after 100ms
        overlay.after(300, set_white)  # Back to white after 300ms
        overlay.after(500, set_red)  # Red again after 500ms
        overlay.after(700, set_white)  # Back to white after 700ms

    # Bind a key (e.g., 't') to toggle focusable mode
    overlay.bind('t', lambda event: toggle_focus())

    # Allow user to move the overlay with a mouse drag
    def start_drag(event):
        overlay.x = event.x
        overlay.y = event.y

    def drag(event):
        x = overlay.winfo_x() + event.x - overlay.x
        y = overlay.winfo_y() + event.y - overlay.y
        overlay.geometry(f"+{x}+{y}")

    label.bind("<Button-1>", start_drag)
    label.bind("<B1-Motion>", drag)

    # Keep the application running
    overlay.mainloop()

if __name__ == "__main__":
    create_overlay()
