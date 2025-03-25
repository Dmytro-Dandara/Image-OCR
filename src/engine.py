import os
import urllib
from PIL import Image, ImageEnhance
from difflib import SequenceMatcher


def split_bbox(box, txt):
    p0, p1, p2, p3 = box
    p4 = [p0[0] + int((p1[0] - p0[0])/2), p0[1]]
    p5 = [p3[0] + int((p2[0] - p3[0])/2), p3[1]]

    curr = ([p0, p4, p5, p3], "Current")
    pote = ([p4, p1, p2, p5], "Potential")
    
    return curr, pote

def match_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def number_filter(out):
    if len(out) == 0:
        return ""

    number = out.split("|")[0]
    if not number[0].isdigit():
        return ""

    if len(number) > 2:
        number = number[:2]
    return number

def find_value(result, ref_bbox):
    matches = []
    d = int((ref_bbox[0][2][0] - ref_bbox[0][0][0]) / len(ref_bbox[1])) * 4
    for box, (txt, score) in result:
        if match_ratio(txt, ref_bbox[1]) > 0.8:
            continue
        if box[0][0] > (ref_bbox[0][0][0] - d) and box[2][0] < (ref_bbox[0][2][0] + d):
            matches.append((box, txt))

    if len(matches) == 0:
        return ""
    elif len(matches) == 1:
        return matches[0][1]
    else:
        return sorted(matches, reverse=True, key=lambda m: m[0][3][1])[-1][1]  # The most top one
        
def find_right_bbox(bboxes):
    if bboxes[0][0][0] < bboxes[1][0][0]:
        bbox = bboxes[0]
    else:
        bbox = bboxes[1]
    
    return bbox        

def run_ocr(paddleOcr_engine, img_path):
    try:
        try:
            img = Image.open(img_path).convert('L')
        except Exception as e:
            return {
                "Current": "",
                "Potential": "",
                "Message": "Broken file! >>> " + str(e)
            }
        
#         mywidth = 640
#         wpercent = (mywidth / float(img.size[0]))
#         hsize = int((float(img.size[1]) * float(wpercent)))
#         resized = img.resize((mywidth, hsize), Image.ANTIALIAS)
        
        myheight = 640
        hpercent = (myheight / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        resized = img.resize((wsize, myheight), Image.ANTIALIAS)
    
        enhancer = ImageEnhance.Contrast(resized)
        final = enhancer.enhance(0.8)
        final.save("preprocessed_tmp.png", dpi=(400, 400))
        
        try:
            result = paddleOcr_engine.ocr("preprocessed_tmp.png", cls=False)
            os.system("rm preprocessed_tmp.png")
        except Exception as e:
            return {
                "Current": "",
                "Potential": "",
                "Message": "OCR fails! >>> " + str(e)
            }

        if len(result) == 0:
            return {
                "Current": "",
                "Potential": "",
                "Message": "OCR fails! Nothing recoginzed."
            }

        current_bbox, potential_bbox = None, None
        current_bboxes, potential_bboxes = [], []

        for box, (txt, score) in result:
            print("* Recognized text: ", txt)
            
            if match_ratio(txt, "Current") > 0.4 and match_ratio(txt, "Potential") > 0.4:
                curr, pote = split_bbox(box, txt)
                current_bboxes.append(curr)
                potential_bboxes.append(pote)
                continue

            if match_ratio(txt, "Current") > 0.4:
                current_bboxes.append((box, txt))
            if match_ratio(txt, "Potential") > 0.4:
                potential_bboxes.append((box, txt))

        if len(current_bboxes) == 2:
            current_bbox = find_right_bbox(current_bboxes)
        elif len(current_bboxes) == 1:
            current_bbox = current_bboxes[0]

        if len(potential_bboxes) == 2:
            potential_bbox = find_right_bbox(potential_bboxes)
        elif len(potential_bboxes) == 1:
            potential_bbox = potential_bboxes[0]

#         print(">>> current_bbox ", current_bbox)
#         print(">>> potential_bbox ", potential_bbox)
        
        if current_bbox is None and potential_bbox is None:
            return {
                "Current": "",
                "Potential": "",
                "Message": "Wrong file! This file doesn't contain any informations about the current & potential value."
            }

        if current_bbox is not None:
            current = find_value(result, current_bbox)
            message = "No error!"
        else:
            current = ""
            message = "Wrong file! This file doesn't contain any informations about the current value."

        if potential_bbox is not None:
            potential = find_value(result, potential_bbox)
            message = "No error!"
        else:
            potential = ""
            message = "Wrong file! This file doesn't contain any informations about the potential value."

        return {
            "Current": number_filter(current),
            "Potential": number_filter(potential),
            "Message": message
        }
    except Exception as e:
        return {
            "Current": "",
            "Potential": "",
            "Message": "Error! >>> " + str(e)
        }

def ocr_on_single(model, url):
    try:
        tmp_file_path = "-".join(url.split("/")[-3: ])
        urllib.request.urlretrieve(
            url,
            tmp_file_path
        )

        result =  run_ocr(model, tmp_file_path)
        print(f">>> Url: {url} => {result}")
        os.system("rm " + tmp_file_path)

        return result
    except:
        return {
            "Current": "",
            "Potential": "",
            "Message": "Unable to download " + url
        }
