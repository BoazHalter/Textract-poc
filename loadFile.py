import tkinter as tk
from tkinter import filedialog

def open_file_dialog():
    file_path = filedialog.askopenfilename()
    if file_path:
        label_file_path.config(text="Selected file: " + file_path)
        button_process.pack()  # Display the process button after file selection

def process_file():
    # Replace this function with the actual processing logic for the selected file
    pass

# Create the main window
root = tk.Tk()
root.title("File Upload")

# Set the window size (width x height)
window_width = 500
window_height = 300
root.geometry(f"{window_width}x{window_height}")

# Create a label to display the selected file path
label_file_path = tk.Label(root, text="No file selected")
label_file_path.pack()

# Create a button to open the file dialog
button_browse = tk.Button(root, text="Browse", command=open_file_dialog)
button_browse.pack()

# Create a button to process the selected file (initially hidden)
button_process = tk.Button(root, text="Process File", command=process_file)
button_process.pack_forget()  # Hide the button initially

# Run the main loop
root.mainloop()
