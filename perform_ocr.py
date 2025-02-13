try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import os
from pdf2image import convert_from_path
from bs4 import BeautifulSoup
import time
import sys
from config import output_dir, config_dir
from detection import get_page_layout, get_equation_hocr, get_figure_hocr, get_text_hocr

def parse_boolean(b):
    return b == "True"

# For simpler filename generation
def simple_counter_generator(prefix="", suffix=""):
    i = 400
    while True:
        i += 1
        yield 'p'

def pdf_to_txt(orig_pdf_path, project_folder_name, lang):
    outputDirIn = output_dir
    outputDirectory = outputDirIn + project_folder_name
    print('Output directory is ', outputDirectory)
    # create images,text folder
    print('cwd is ', os.getcwd())
    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)

    if not os.path.exists(outputDirectory + "/Images"):
        os.mkdir(outputDirectory + "/Images")

    imagesFolder = outputDirectory + "/Images"
    imageConvertOption = 'True'

    print("converting pdf to images")
    jpegopt = {
        "quality": 100,
        "progressive": True,
        "optimize": False
    }

    output_file = simple_counter_generator("page", ".jpg")
    print('orig pdf oath is', orig_pdf_path)
    print('cwd is', os.getcwd())
    print("orig_pdf_path is", orig_pdf_path)
    if (parse_boolean(imageConvertOption)):
        convert_from_path(orig_pdf_path, output_folder=imagesFolder, dpi=300, fmt='jpeg', jpegopt=jpegopt,
                          output_file=output_file)

    print("images created.")
    print("Now we will OCR")
    os.environ['IMAGESFOLDER'] = imagesFolder
    os.environ['OUTPUTDIRECTORY'] = outputDirectory
    # tessdata_dir_config = r'--psm 3 --tessdata-dir "/usr/share/tesseract-ocr/4.00/tessdata/"'

    print("Selected language model " + lang)
    # os.environ['CHOSENMODEL'] = lang  # tesslanglist[int(linput)-1]
    # Creating Final set folders and files
    # if not os.path.exists(outputDirectory + "/Comments"):
    #     os.mkdir(outputDirectory + "/Comments")
    #     os.mknod(outputDirectory + "/Comments/" + 'README.md', mode=0o666)
    # if not os.path.exists(outputDirectory + "/VerifierOutput"):
    #     os.mkdir(outputDirectory + "/VerifierOutput")
    #     os.mknod(outputDirectory + "/VerifierOutput/" + 'README.md', mode=0o666)
    # if not os.path.exists(outputDirectory + "/Dicts"):
    #     os.mkdir(outputDirectory + "/Dicts")
    #     os.mknod(outputDirectory + "/Dicts/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/Cropped_Images"):
        os.mkdir(outputDirectory + "/Cropped_Images")
    if not os.path.exists(outputDirectory + "/Inds"):
        os.mkdir(outputDirectory + "/Inds")
        os.mknod(outputDirectory + "/Inds/" + 'README.md', mode=0o666)
    if not os.path.exists(outputDirectory + "/Layout_Images"):
        os.mkdir(outputDirectory + "/Layout_Images")
    if not os.path.exists(outputDirectory + "/CorrectorOutput"):
        os.mkdir(outputDirectory + "/CorrectorOutput")
        os.mknod(outputDirectory + "/CorrectorOutput/" + 'README.md', mode=0o666)

    os.system(f'cp {config_dir}project.xml ' + outputDirectory)
    individualOutputDir = outputDirectory + "/Inds"
    startOCR = time.time()

    for imfile in os.listdir(imagesFolder):
        finalimgtoocr = imagesFolder + "/" + imfile
        dash = imfile.index('-')
        dot = imfile.index('.')
        page = int(imfile[dash + 1 : dot])
        layout_annotated_image_path = outputDirectory + "/Layout_Images/" + imfile

        dets = get_page_layout(finalimgtoocr, layout_annotated_image_path)
        dets.sort(key = lambda x : x[1][1])
        hocr_elements = ''
        eqn_cnt = 1
        fig_cnt = 1
        class_names = {0: 'title', 1: 'plain_text', 2: 'abandon', 3: 'figure', 4: 'figure_caption', 5: 'table', 6: 'table_caption', 7: 'table_footnote', 8: 'isolate_formula', 9: 'formula_caption'}
        for det in dets:
            cls = det[0]
            bbox = det[1]
            if cls == 8:
                # Equations
                eqn_hocr = get_equation_hocr(finalimgtoocr, outputDirectory, page, bbox, eqn_cnt)
                # eqn_cnt += 1
                hocr_elements += eqn_hocr
            elif cls == 3:
                # Figures
                fig_hocr = get_figure_hocr(bbox)
                # fig_hocr = get_figure_hocr(finalimgtoocr, outputDirectory, page, bbox, fig_cnt)
                # fig_cnt += 1
                hocr_elements += fig_hocr
            elif cls == 5:
                # Tables
                hocr = get_text_hocr(finalimgtoocr, bbox, "table")
                hocr_elements += hocr
            else:
                hocr = get_text_hocr(finalimgtoocr, bbox, "text")
                # Can use class_names[cls] for classname instead
                hocr_elements += hocr

        # Write txt files for all pages using Tesseract
        # txt = pytesseract.image_to_string(imagesFolder + "/" + imfile, lang=lang)
        # with open(individualOutputDir + '/' + imfile[:-3] + 'txt', 'w') as f:
        #     f.write(txt)

        # Now we generate HOCRs using Tesseract
        print('We will OCR the image ' + finalimgtoocr)
        final_hocr = '<html><head></head><body>' + hocr_elements + '</body></html>'
        soup = BeautifulSoup(final_hocr, 'html.parser')

        # Write final hocrs
        hocrfile = individualOutputDir + '/' + imfile[:-3] + 'hocr'
        f = open(hocrfile, 'w+')
        f.write(str(soup))

        copy_command = 'cp {}/*.hocr {}/'.format(individualOutputDir, outputDirectory + "/CorrectorOutput")
        os.system(copy_command)
        correctorFolder = outputDirectory + "/CorrectorOutput"
        for hocrfile in os.listdir(correctorFolder):
            if "hocr" in hocrfile:
                htmlfile = hocrfile.replace(".hocr", ".html")
                os.rename(correctorFolder + '/' + hocrfile, correctorFolder + '/' + htmlfile)

    # Calculate the time elapsed for entire OCR process
    endOCR = time.time()
    ocr_duration = round((endOCR - startOCR), 3)
    print('Done with OCR of ' + str(project_folder_name) + ' of ' + str(len(os.listdir(imagesFolder))) + ' pages in ' + str(ocr_duration) + ' seconds')
    return outputDirectory

# Function Calls
if __name__ == "__main__":
    input_file= sys.argv[1]
    outputsetname = sys.argv[2]
    lang = sys.argv[3]
    ocr_only = sys.argv[4]
    pdf_to_txt(input_file, outputsetname, lang)
