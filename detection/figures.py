import cv2

def get_figure_hocr(image_path, outputDirectory, pagenumber, bbox, count):
    image = cv2.imread(image_path)
    fig = bbox
    cropped_image = image[fig[1]: fig[3], fig[0]: fig[2]]
    image_file_name = '/Cropped_Images/figure_' + str(pagenumber) + '_' + str(count) + '.jpg'
    cv2.imwrite(outputDirectory + image_file_name, cropped_image)
    fig_hocr = f"<img class=\"ocr_figure\" title=\"bbox {fig[0]} {fig[1]} {fig[2]} {fig[3]}\" src=\"..{image_file_name}\">"
    return fig_hocr