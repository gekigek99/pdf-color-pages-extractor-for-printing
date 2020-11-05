'''
pdf-color-pages-extractor-for-printing.py is used to analyze a pdf file and output 2 pdf files containing either color either white-black images (layout ready for double-sided printing)
Copyright (C) 2020  gekigek99
v4.0
visit my github page: https://github.com/gekigek99
If you like what I do please consider having a cup of coffee with me at: https://www.buymeacoffee.com/gekigek99
''' 

import fitz
import time, os
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader

grey_approx_coeff = 5   #between 0 and 50 (0 --> must be perfect gray (eg. 154,154,154))
precision = 5           #between 1 and 10 (1 --> more precise)

def main():
    inputfile = input('insert pdf to analyze: ')
    doc = fitz.open(inputfile)
    doc_lenght = len(doc)
    lenXREF = doc._getXrefLength()
    print("file: %s, pages: %s, objects: %s" % (inputfile, doc_lenght, lenXREF-1))

    pages_containing_images = []
    rgb_pages = []
    rgb_pages_printable = []
    wb_pages_printable = []

    t0 = time.time()
    
    pages_containing_images, rgb_pages = extract_images_rgb(doc)

    rgb_pages_printable = convert_to_printable_pages(rgb_pages, doc_lenght)
    wb_pages_printable = get_wb_pages_printable(doc_lenght, rgb_pages_printable)

    makepdf(inputfile, rgb_pages_printable, 'rgb')
    makepdf(inputfile, wb_pages_printable, 'wb')

    pages_containing_images = pageshifter(pages_containing_images, 1)
    rgb_pages = pageshifter(rgb_pages, 1)
    rgb_pages_printable = pageshifter(rgb_pages_printable, 1)
    wb_pages_printable = pageshifter(wb_pages_printable, 1)
    
    t1 = time.time()
    print("run time:", round(t1-t0, 2), 's')
    print('pages that contain images:\n', pages_containing_images)
    print('pages that contain RGB images:\n', rgb_pages)
    print('rgb pages to print (', len(rgb_pages_printable), '):\n', rgb_pages_printable)
    print('wb pages to print (', len(wb_pages_printable), '):\n', wb_pages_printable)
    print('press enter to do an other document...')
    os.system("PAUSE")

def extract_images_rgb(doc):
    pages_containing_images = []
    rgb_pages = []
    imgcount = 0
    for i in range(len(doc)):
        print(' ' * 10, end = '\r')
        print(round(100 * i / len(doc)), '%', end = '')
        imglist = doc.getPageImageList(i)
        if len(imglist) != 0:
            pages_containing_images.append(i)
        for img in imglist:
            xref = img[0]                  # xref number
            pix = fitz.Pixmap(doc, xref)   # make pixmap from image
            imgcount += 1
            if pix.n < 5:                  # can be saved as PNG
                pix.writePNG("img.png")
                if i not in rgb_pages:
                    if RGBimageanalyze("img.png") == True:
                        rgb_pages.append(i)
            else:                          # must convert CMYK first
                pix0 = fitz.Pixmap(fitz.csRGB, pix)
                pix0.writePNG("img.png")
                pix0 = None                # free Pixmap resources
                if i not in rgb_pages:
                    if RGBimageanalyze("img.png") == True:
                        rgb_pages.append(i)
            pix = None                     # free Pixmap resources
    try:
        os.remove("img.png")
    except:
        print('unable to remove img.png')
    finally:
        print(' ' * 10,end = '\r')
        print('100 %')
    return pages_containing_images, rgb_pages

def convert_to_printable_pages(rgb_pages, doc_lenght):
    rgb_pages_printable = []
    for i in range(len(rgb_pages)):
        if rgb_pages[i] % 2 == 0:           #even (page 0,2,4...)
            if rgb_pages[i] not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i])
            if rgb_pages[i] + 1 not in rgb_pages_printable and rgb_pages[i] +1 < doc_lenght:
                rgb_pages_printable.append(rgb_pages[i] + 1)
        else:                               #odd (page 1,3,5...)
            if rgb_pages[i] - 1 not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i] - 1)
            if rgb_pages[i] not in rgb_pages_printable:
                rgb_pages_printable.append(rgb_pages[i])
    return rgb_pages_printable

def get_wb_pages_printable(doc_lenght, rgb_pages_printable):
    wb_pages_printable = []
    for i in range(doc_lenght):
        if i not in rgb_pages_printable:
            wb_pages_printable.append(i)
    return wb_pages_printable

def makepdf(inputfile, pages_printable, color):                
    inpdf = PdfFileReader(inputfile, strict=False)
    outpdf = PdfFileWriter()

    for i in range(len(pages_printable)):
       outpdf.addPage(inpdf.getPage(pages_printable[i]))

    if color == 'rgb':
        with open(inputfile.replace('.pdf', ' ') + '(for color pages printing).pdf', "wb") as out_file:
            outpdf.write(out_file)
            print('written file: rgb_pages_to_print.pdf')
    if color == 'wb':
        with open(inputfile.replace('.pdf', ' ') + '(for wb pages printing).pdf', "wb") as out_file:
            outpdf.write(out_file)
            print('written file: wb_pages_to_print.pdf')

#-------------------------------TOOLS-------------------------------#

def RGBimageanalyze(input_image):
    im = Image.open(input_image)
    if im.mode != "RGB" and im.mode != "RGBA":
        im = im.convert("RGB")
    pix = im.load()
    for y in range(0, im.size[1], precision):
        for x in range(0, im.size[0], precision):
            r = pix[x,y][0]
            b = pix[x,y][1]
            g = pix[x,y][2]
            avg = (r + b + g) / 3
            if avg - grey_approx_coeff <= r <= avg + grey_approx_coeff and avg - grey_approx_coeff <= b <= avg + grey_approx_coeff and avg - grey_approx_coeff <= g <= avg + grey_approx_coeff:
                continue
            else:
                im.close()
                return True
    im.close()
    return False

def pageshifter(input_list, shift):
    output_list = []
    for i in range(len(input_list)):
        output_list.append(input_list[i] + shift)
    return output_list
    
    
if __name__ == '__main__':
    print('pdf-color-pages-extractor-for-printing v4.0')
    print('Copyright (C) 2020 gekigek99')
    print('visit my github page for updates: https://github.com/gekigek99')
    while True:
        main()
