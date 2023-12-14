import tkinter as tk
from tkinter import filedialog
import boto3
from tkinter import messagebox

def open_file_dialog():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        label_file_path.config(text="Selected file: " + file_path)
        button_process.pack(side=tk.BOTTOM,expand=1)  # Display the process button after file selection

def process_file():
    if file_path:
        response = upload_to_s3(file_path)
        show_response(response)

def upload_to_s3(file):
    bucket_name = 'your_bucket_name'  # Replace with your S3 bucket name
    s3 = boto3.client('s3')
    try:
        file_name = file.split('/')[-1]  # Extract file name from the path
        s3.upload_file(file, bucket_name, file_name)
        return f"{file_name} uploaded successfully to {bucket_name}"
    except Exception as e:
        return f"Error uploading file: {e}"

def show_response(response):
    messagebox.showinfo("S3 Upload Response", response)

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
button_browse.pack(side=tk.BOTTOM,expand=1)

# Create a button to process the selected file (initially hidden)
button_process = tk.Button(root, text="Upload to AWS S3", command=process_file)
button_process.pack_forget()  # Hide the button initially

# Run the main loop
root.mainloop()
