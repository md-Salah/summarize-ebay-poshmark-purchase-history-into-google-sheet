from tkinter import Tk
from tkinter.filedialog import askopenfilename

def open_file():
    root = Tk.Tk()
    root.withdraw()
    path_name = askopenfilename()
    root.destroy()
    return path_name