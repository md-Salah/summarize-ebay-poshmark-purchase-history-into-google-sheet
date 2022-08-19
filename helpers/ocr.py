from pdf2image import convert_from_path
import easyocr
import os

def pdf_to_image_path(filename = 'files/test.pdf', first_page=None, last_page=None):
    poppler_path=r'C:\Program Files\poppler-0.68.0\bin'

    images = convert_from_path(
        filename, 
        dpi=600, 
        first_page=first_page, 
        last_page=last_page, 
        fmt='png', 
        poppler_path = poppler_path, 
        grayscale=False
    )

    paths = []
    for i in range(len(images)):
        paths.append('files/page'+ str(i) +'.png')
        # Save pages as images in the pdf
        images[i].save(paths[i], 'PNG')
    return paths

def image_to_python_list(paths = []):
    reader = easyocr.Reader(['ch_sim', 'en']) # this needs to run only once to load the model into memory
    os.system('cls') # Remove warnings
    
    data = []
    for path in paths:
        result = reader.readtext(path, detail=0) # result = [] (list of strings)
        data.append(result)
    return data
