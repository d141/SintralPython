import math
import ntpath
import os
import os.path
import textwrap
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.messagebox import askokcancel, showinfo, QUESTION, askyesno
from tkinter.simpledialog import askstring
import re
import PIL
import labels
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.graphics import shapes
from datetime import datetime

color_dict = {'.': (255, 255, 255),
              'A': (0, 0, 0),
              'Y': (0, 60, 167),
              'T': (0, 149, 55),
              '*': (160, 72, 0),
              'I': (255, 62, 255),
              '+': (198, 1, 45),
              'B': (255, 141, 17),
              'G': (33, 58, 5),
              'H': (122, 174, 213),
              'O': (245, 196, 0),
              'W': (152, 0, 152),
              'Z': (128, 255, 0),
              'E': (104, 96, 104),
              'K': (64, 0, 56),
              'L': (17, 27, 78),
              'X': (137, 138, 142),
              'N': (75, 8, 103),
              'S': (167, 20, 51),
              'M': (2, 86, 48),
              'P': (64, 0, 0),
              'Q': (255, 183, 12),
              'a': (60, 56, 52),
              'y': (0, 136, 136),
              't': (133, 226, 29),
              'i': (252, 218, 17),
              'b': (196, 73, 0),
              'g': (213, 144, 0),
              'h': (61, 71, 19),
              'o': (213, 199, 186),
              'w': (249, 218, 224),
              'z': (112, 2255, 112),
              'e': (235, 254, 1),
              'k': (194, 148, 113),
              'l': (108, 23, 50),
              'm': (128, 128, 255),
              'p': (81, 43, 28),
              'q': (41, 86, 154)}

color_words = {(255, 255, 255): "White",
               (0, 0, 0): "Black",
               (0, 60, 167): "Royal",
               (0, 149, 55): "Kelly",
               (255, 62, 255): "Hot Pink",
               (198, 1, 45): "Real Red",
               (255, 141, 17): "Trad. Orange",
               (122, 174, 213): "Columbia",
               (245, 196, 0): "Mustard",
               (17, 27, 78): "Navy",
               (137, 138, 142): "Silver",
               (75, 8, 103): "Purple",
               (167, 20, 51): "Barn Red",
               (2, 86, 48): "Forest",
               (255, 183, 12): "S Gold",
               (60, 56, 52): "Charcoal",
               (0, 136, 136): "Teal",
               (133, 226, 29): "Hot Green",
               (252, 218, 17): "Canary",
               (196, 73, 0): "Burnt Orange",
               (213, 144, 0): "Old Gold",
               (61, 71, 19): "Olive",
               (213, 199, 186): "Van Cream",
               (249, 218, 224): "Light Pink",
               (235, 254, 1): "Safety Yellow",
               (194, 148, 113): "Sandstone",
               (108, 23, 50): "Maroon",
               (81, 43, 28): "Brown",
               (41, 86, 154): "Denim"}

sintral_template_txt = open("sintral_template.txt")
sintral_template = list(enumerate(sintral_template_txt))
# sintral_template_for_bottom = enumerate(sintral_template_txt)

base_colors_3 = [color_dict['.'], color_dict['A'], color_dict['Y']]
base_colors_8 = {color_dict['.']: [1, color_dict['G']], color_dict['A']: [2, color_dict['H']],
                 color_dict['Y']: [3, color_dict['O']], color_dict['T']: [4, color_dict['W']],
                 color_dict['*']: [5, color_dict['Z']], color_dict['I']: [6, color_dict['E']],
                 color_dict['+']: [7, color_dict['K']], color_dict['B']: [8, color_dict['L']]}
pair_1 = [color_dict['.'], color_dict['G']]
pair_2 = [color_dict['A'], color_dict['H']]
pair_3 = [color_dict['Y'], color_dict['O']]
pair_4 = [color_dict['T'], color_dict['W']]
pair_5 = [color_dict['*'], color_dict['Z']]
pair_6 = [color_dict['I'], color_dict['E']]
pair_7 = [color_dict['+'], color_dict['K']]
pair_8 = [color_dict['B'], color_dict['L']]

systems = ['2', '3', '4', '5', '6', '7', '1', '8']


def read_color_code(pic, size_num):
    """
    If there is a color code in the bottom left corner, read it. Not often used
    --------------
    :param pic: (PIL Image)Original bitmap, full size
    :param size_num:(tuple) Dimensions of the bitmap
    :return:(list) Actual yarn colors in the pattern
    """
    yarn_colors = []
    for i in range(8):
        current_color = pic[i, size_num[1] - 1]
        if current_color != color_dict['K']:
            yarn_colors.append(current_color)
    if all(x == yarn_colors[0] for x in yarn_colors):
        return False
    return yarn_colors


def read_bitmap_for_colors(pic, size_num):
    """
    Read the original bitmap and return the yarn colors
    --------------
    :param pic: (PIL Image).pixels()
    :param size_num: (tuple) Size of the bitmap
    :return: (list) Yarn colors in the blanket as they are first seen from the bottom up
    """
    yarn_colors = []
    for x in reversed(range(size_num[0])):
        for y in reversed(range(size_num[1] - 15)):
            if pic[x, y] not in yarn_colors:
                yarn_colors.append(pic[x, y])
    return yarn_colors


def convert_colors_to_knitting(pic, size_num, colors):
    """
    Function to convert the bitmap from knitting colors associated with yarn feeders to birdseye
    --------------
    :param pic: (PIL Image) Original size and in original colors only (Purple, Yellow, Pink)
    :param size_num: (tuple) Size of the bitmap
    :param colors: (list of RGB) Colors in the bitmap [Purple,Yellow,Pink]
    :return: New bitmap that has been birdseyed (.G,AH,YO)
    """
    pixels = pic.load()
    img_array = np.array(pic, dtype=np.uint8)
    oddity = 0
    this_line = []
    last_line = []
    found_center = False
    streak = 0
    for y in range(size_num[1]):
        if not found_center:
            this_line = img_array[y]
            if y > 0 and (this_line == last_line).all():
                streak += 1
            if y > 0 and (this_line != last_line).any() and streak > 40:
                center = ((streak / 2) - 20) + (y - streak)
                found_center = True
            if y > 0 and (this_line != last_line).any() and streak < 40:
                streak = 0
        for x in range(size_num[0]):
            current_color = pixels[x, y]
            if current_color == color_dict["P"]:
                knitting_color = color_dict["P"]
            else:
                color_index = colors.index(current_color)
                if oddity % 2 != 0:
                    knitting_color = list(color_dict.values())[color_index + 8]
                else:
                    knitting_color = list(color_dict.values())[color_index]
            pixels[x, y] = knitting_color
            oddity += 1
        # oddity += 1
        last_line = this_line
    if not found_center:
        center = 0
    return pic, center


def sort_colors(colors):
    """
    Sort colors from how they appear in a row to how they should appear in the barcode
    --------------
    :param colors: (list) Colors in a given row in any order. Ex: [Y,A,T,.]
    :return: (list) Colors sorted according to knitting order. Ex: [.,A,Y,T]
    """
    ranks = []
    results = []
    for color in colors:
        ranks.append(base_colors_8[color][0])
    for color in colors:
        min_idx = ranks.index(min(ranks))
        results.append(colors[min_idx])
        ranks[min_idx] = 42

    return results


def make_barcode(img, colors):
    """
    Key function for adding the barcode. Contains all logic to ensure even number of lines per combination
    --------------
    :param img: (PIL Image) Has been flipped and birdseyed
    :param colors: list of colors used in the bitmap (not used)
    :return: (PIL Image) 8 extra columns with barcode & (list) number of rows for each number of knitting colors
    """
    size = img.size
    barcode_row = Image.new('RGB', (481, size[1]), color_dict['.'])
    barcode_row.paste(img, (8, 0))
    pixels = barcode_row.load()
    reduction_counts = [0, 0, 0, 0, 0, 0, 0, 0]
    last_row = []
    for y in range(size[1]):
        num_colors_in_row = 0
        colors_in_row = []
        for x in range(473):
            current_color = pixels[x + 8, y]
            if current_color == color_dict["P"]:
                break
            current_color_pair = ()
            if current_color not in base_colors_8.keys():
                current_color_pair = list(color_dict.values())[list(color_dict.values()).index(current_color) - 8]
                current_color = current_color_pair
            if current_color not in colors_in_row:
                if current_color in pair_1:
                    colors_in_row.append(pair_1[0])
                    num_colors_in_row += 1
                elif current_color in pair_2:
                    colors_in_row.append(pair_2[0])
                    num_colors_in_row += 1
                elif current_color in pair_3:
                    colors_in_row.append(pair_3[0])
                    num_colors_in_row += 1
                elif current_color in pair_4:
                    colors_in_row.append(pair_4[0])
                    num_colors_in_row += 1
                elif current_color in pair_5:
                    colors_in_row.append(pair_5[0])
                    num_colors_in_row += 1
                elif current_color in pair_6:
                    colors_in_row.append(pair_6[0])
                    num_colors_in_row += 1
                elif current_color in pair_7:
                    colors_in_row.append(pair_7[0])
                    num_colors_in_row += 1
                elif current_color in pair_8:
                    colors_in_row.append(pair_8[0])
                    num_colors_in_row += 1
        colors_in_row = sort_colors(colors_in_row)
        reduction_counts[num_colors_in_row - 1] += 1
        go_backwards = False

        if colors_in_row != last_row and y > 0 and y % 2 != 0:
            if len(last_row) == num_colors_in_row:
                in_first = set(colors_in_row)
                in_second = set(last_row)
                in_second_but_not_in_first = in_second - in_first
                num_colors_in_row += len(list(in_second_but_not_in_first))
                colors_in_row = sort_colors(colors_in_row + list(in_second_but_not_in_first))
                go_backwards = True
            elif len(last_row) > num_colors_in_row:
                colors_in_row = last_row
                num_colors_in_row = len(last_row)
            else:
                go_backwards = True

        if num_colors_in_row == 1:
            if colors_in_row[0] not in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[0]
                if go_backwards:
                    pixels[0, y - 1] = pair_1[0]
                    pixels[1, y - 1] = pair_2[0]
                    pixels[2, y - 1] = colors_in_row[0]
            else:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = pair_3[0]
                """
                if go_backwards:
                    pixels[0, y - 1] = pair_1[0]
                    pixels[1, y - 1] = pair_2[0]
                    pixels[2, y - 1] = pair_3[0]
                """
        elif num_colors_in_row == 2:
            if colors_in_row[0] not in base_colors_3 and colors_in_row[1] in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[0]
                if go_backwards:
                    pixels[0, y - 1] = pair_1[0]
                    pixels[1, y - 1] = pair_2[0]
                    pixels[2, y - 1] = colors_in_row[0]
            elif colors_in_row[1] not in base_colors_3 and colors_in_row[0] in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[1]
                if go_backwards:
                    pixels[0, y - 1] = pair_1[0]
                    pixels[1, y - 1] = pair_2[0]
                    pixels[2, y - 1] = colors_in_row[1]
            elif colors_in_row[0] not in base_colors_3 and colors_in_row[1] not in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = colors_in_row[0]
                pixels[2, y] = colors_in_row[1]
                if go_backwards:
                    pixels[0, y - 1] = pair_1[0]
                    pixels[1, y - 1] = colors_in_row[0]
                    pixels[2, y - 1] = colors_in_row[1]
            else:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = pair_3[0]
                '''
                if go_backwards:
                    pixels[0, y] = pair_1[0]
                    pixels[1, y] = colors_in_row[0]
                    pixels[2, y] = colors_in_row[1]
                '''
        elif num_colors_in_row == 3:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
        elif num_colors_in_row == 4:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
                pixels[3, y - 1] = colors_in_row[3]
        elif num_colors_in_row == 5:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]
            pixels[4, y] = colors_in_row[4]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
                pixels[3, y - 1] = colors_in_row[3]
                pixels[4, y - 1] = colors_in_row[4]
        elif num_colors_in_row == 6:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]
            pixels[4, y] = colors_in_row[4]
            pixels[5, y] = colors_in_row[5]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
                pixels[3, y - 1] = colors_in_row[3]
                pixels[4, y - 1] = colors_in_row[4]
                pixels[5, y - 1] = colors_in_row[5]
        elif num_colors_in_row == 7:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]
            pixels[4, y] = colors_in_row[4]
            pixels[5, y] = colors_in_row[5]
            pixels[6, y] = colors_in_row[6]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
                pixels[3, y - 1] = colors_in_row[3]
                pixels[4, y - 1] = colors_in_row[4]
                pixels[5, y - 1] = colors_in_row[5]
                pixels[6, y - 1] = colors_in_row[6]
        elif num_colors_in_row == 8:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]
            pixels[4, y] = colors_in_row[4]
            pixels[5, y] = colors_in_row[5]
            pixels[6, y] = colors_in_row[6]
            pixels[7, y] = colors_in_row[7]
            if go_backwards:
                pixels[0, y - 1] = colors_in_row[0]
                pixels[1, y - 1] = colors_in_row[1]
                pixels[2, y - 1] = colors_in_row[2]
                pixels[3, y - 1] = colors_in_row[3]
                pixels[4, y - 1] = colors_in_row[4]
                pixels[5, y - 1] = colors_in_row[5]
                pixels[6, y - 1] = colors_in_row[6]
                pixels[7, y - 1] = colors_in_row[7]

        last_row = colors_in_row

    return barcode_row, reduction_counts


def calculate_reduction(counts):
    """
    Performs calculation to determine how many lines should be removed
    --------------
    :param counts: (list) returned from make_barcode. Number of rows for each number of knitting colors
    :return: (int) number of lines to remove
    """
    count_total = np.sum(np.array(counts))
    adjusted_counts = np.array(
        [counts[0], counts[1], counts[2], counts[3] * 1.031, counts[4] * 1.1, counts[5] * 1.222, counts[6] * 1.294,
         counts[7] * 1.31])
    adjusted_total = np.sum(adjusted_counts) - count_total
    return adjusted_total


def confirm():
    """
    Simple function to ask if the user is happy with results of the line reduction
    --------------
    :return: boolean
    """

    answer = askokcancel(
        title='Proceed?',
        message='Are you happy with the results? Or do you want to try again',
        icon=QUESTION)
    return answer


def ask_grid_background():
    """
    Simple function to ask if the user is happy with results of the line reduction
    --------------
    :return: boolean
    """

    answer = askyesno(
        title='Proceed?',
        message='Is it a basic set up? (If you answer no, the background will be white)',
        icon=QUESTION)
    return answer


def ask_multiple_grids():
    """
    Simple function to ask if the user is happy with results of the line reduction
    --------------
    :return: boolean
    """

    answer = askyesno(
        title='Proceed?',
        message='Are there any more grids?',
        icon=QUESTION)
    return answer


def remove_lines(bitmap, line_begin, reduction_count):
    """
    Function for automatically removing required lines based on input for the user.
    Uses confirm() at the end to proceed
    --------------
    :param bitmap: (PIL Image) Already flipped, birdseyed, and barcoded
    :param line_begin: (str) User input from a get_info box
    :param reduction_count: (int) Result from calculate_reduction()
    :return: (PIL Image) Reduced bitmap
    """
    true_count = int(np.round(reduction_count / 2))
    line_begin = int(line_begin)
    if true_count % 2 != 0:
        true_count += 1
    size = bitmap.size
    new_height = size[1] - (true_count * 2)
    canvas = Image.new('RGB', (481, new_height), color_dict['.'])
    part1 = bitmap.crop((0, 0, 482, line_begin))
    midsection = new_height - (true_count + line_begin)
    part2 = bitmap.crop((0, line_begin + true_count, 482, midsection + true_count + line_begin))
    part3 = bitmap.crop((0, size[1] - line_begin, 482, size[1]))
    canvas.paste(part1)
    canvas.paste(part2, (0, line_begin))
    canvas.paste(part3, (0, new_height - line_begin))
    canvas.show()
    decision = confirm()

    if decision is True:
        return canvas
    else:
        showinfo("OK", "Alrighty...let's try again", )
        line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
        remove_lines(bitmap, line_begin, reduction_count)


def read(file_path, design_colors=None):
    """
    First function called to introduce the bitmap into the program
    --------------
    :param file_path: Gathered from a file_chooser()
    :param design_colors: list of colors. for use when reading a personalization grid where color order is already established
    :return: list color colors & The image cropped, flipped, and re-colored to main knitting colors
    """
    large = (483, 510)
    regular = (483, 360)
    small = (483, 296)
    grid = (473,821)
    new_grid = (473,841)
    img = Image.open(file_path)
    rgb_im = img.convert('RGB')
    pic = img.load()
    size_num = rgb_im.size
    grid_correction = 0
    # Check that the size is right
    if size_num == large:
        size = 'large'
    elif size_num == regular:
        size = 'regular'
    elif size_num == small:
        size = 'small'
    elif size_num == grid:
        size = 'grid'
        grid_correction = 5
    elif size_num == new_grid:
        size = 'new_grid'
        pic = img.crop((0, 0, 473, 481)).load()
        grid_correction = 5
        size_num = img.crop((0, 0, 473, 481)).convert('RGB').size
    else:
            messagebox.showinfo("Uh-oh,", f"I don't recognize these dimensions")
            return


    # Check to see if there are unknown colors
    for x in range(size_num[0]):
        for y in range(size_num[1]):
            if pic[x, y] not in color_dict.values():
                messagebox.showinfo("Uh-oh,", f":( there's an unknown color located at {x},{y}")
                return
    messagebox.showinfo("Congrats", "No unknown colors! Nice")

    # Read the color coding in the bottom left corner or scan it to get them.
    if not design_colors:
        colors = read_color_code(pic, size_num)
        if not colors:
            messagebox.showinfo("Don't worry", f"There's no color code for this one. I'll scan it myself.")
        colors = read_bitmap_for_colors(pic, size_num)
    else:
        colors = design_colors

    # Trim the edges and rotate
    height = size_num[1] - 15 + (3 * grid_correction)
    img2 = img.crop((5 - grid_correction, 5 - grid_correction, 478 - grid_correction, height))
    if grid_correction == 0:
        img2 = img2.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    size_num = img2.size
    # pic=img2.load()

    # Convert the bitmap to it's knitting colors
    img3, center = convert_colors_to_knitting(img2, size_num, colors)
    return img3, colors, center


def convert_to_jtxt(image, start_line=None):
    """
    Takes the completed birdseyed bitmap and converts it to Run-Length Encoded _J.txt
    --------------
    :param image: (PIL image type), rotated, birdseyed, and barcode written
    :return:
    """
    pixels = image.load()
    size = image.size
    big_string = ""
    # grid_correction
    for y in range(size[1]):
        string = ""
        for x in range(481):
            current_color = pixels[x, y]
            string += list(color_dict.keys())[list(color_dict.values()).index(current_color)]
        big_string += string + '\n'

    txt_list = big_string.split('\n')[:-1]
    if start_line:
        line_num = start_line
    else:
        line_num = 1002

    compressed = ""
    counts_found = find_counts(txt_list)
    compressed_list = find_patterns(counts_found)

    for line in compressed_list:
        # string = line
        # length = len(big_string)
        # new_string = ""
        # i = 1
        '''
        #Original Compression Algorithm
        
        while i <= length - 1 and string:
            if i > length - i:
                pass
            sub_string1 = string[:i]
            sub_string2 = string[i:i + i]
            if sub_string1 == sub_string2:
                match = True
                count = 1
                while match is True:
                    sub_string1 = string[count * i:(count + 1) * i]
                    sub_string2 = string[(count + 1) * i:(count + 2) * i]
                    if sub_string1 == sub_string2:
                        count += 1
                    else:
                        match = False
                        new_string += f"{count + 1}({sub_string1})"
                        string = string[count * i + i:]
                        i = 1
            else:
                if i == len(string):
                    new_string += string[0]
                    string = string[1:]
                    i = 1
                else:
                    i += 1
        '''

        new_lines = []
        while len(line) > 120:

            last_char_idx = 119
            last_char = line[last_char_idx]
            while last_char == "(" or last_char.isdigit():
                last_char_idx -= 1
                last_char = line[last_char_idx]
            new_lines.append(line[:last_char_idx] + "$")
            line = "$" + line[last_char_idx:]
        new_lines.append(line)

        if len(new_lines) == 4:
            compressed = compressed + str(line_num) + " " + new_lines[0] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[1] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[2] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[3] + "\n"
            line_num += 1

        elif len(new_lines) == 3:
            compressed = compressed + str(line_num) + " " + new_lines[0] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[1] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[2] + "\n"
            line_num += 1

        elif len(new_lines) == 2:

            compressed = compressed + str(line_num) + " " + new_lines[0] + "\n"
            line_num += 1
            compressed = compressed + str(line_num) + " " + new_lines[1] + "\n"
            line_num += 1

        else:
            compressed = compressed + str(line_num) + " " + new_lines[0] + "\n"
            line_num += 1

    return compressed[:compressed.rfind('\n')], line_num


def find_ja1(grid):
    lines = grid.split('\n')
    index = 1
    ja1_list = ""
    for line in lines[1:]:
        if "P" in line:
            ja1_list += f"IF #50={index} JA1={str(int(line[0:4]) - 1)}\n"
            index += 1
    return ja1_list




# def add_ja1(list)

def path_leaf(path):
    """
    Takes a full filepath and removes the filename so that you can save other files in same location
    --------------
    :param path: full filepath including the filename
    :return: filepath without the filename
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def make_label(colors):
    """
    Generate a sheet object that can be saved as a pdf.
    Contains the correctly ordered yarn colors for tying up on the machine
    --------------
    :param colors: RGB values of original bitmap colors. Converted to (str) by matching index in (dict)color_words
    :return: a sheet object that is saved in project folder as an appropriately sized pdf
    """

    specs = labels.Specification(90, 14, 1, 1, 90, 14, left_padding=0, top_padding=0, bottom_padding=0, right_padding=0,
                                 padding_radius=0)

    # Create a function to draw each label. This will be given the ReportLab drawing
    # object to draw on, the dimensions (NB. these will be in points, the unit
    # ReportLab uses) of the label, and the object to render.
    def draw_label(label, width, height, obj):
        # Just convert the object to a string and print this at the bottom left of
        # the label.
        label.add(shapes.String(2, 10, str(obj), fontName="Helvetica", fontSize=8))

    # Create the sheet.
    sheet = labels.Sheet(specs, draw_label, border=True)

    # Add a couple of labels.
    string = ""
    for i in range(len(colors)):
        string += f"{color_words[colors[i]]}/"
    wrapper = textwrap.TextWrapper(width=90)
    string = wrapper.fill(text=string)
    sheet.add_label(string)
    return sheet


def add_bottom_of_sintral():
    """
    grabs pieces from sintral_template.txt
    very sensitive to changes in the template
    --------------
    :return: sintral_bottom, sintral2x_bottom
    """

    sintral_bottom = ""
    sintral2x_bottom = ""
    lines_to_read = list(range(166, 253))
    for position, line in sintral_template:
        if position in lines_to_read:
            sintral_bottom += line
            sintral2x_bottom += line
    return sintral_bottom, sintral2x_bottom


def add_top_of_sintral():
    """
    grabs pieces from sintral_template.txt
    very sensitive to changes in the template
    --------------
    :return: sintral_top, sintral2x_top
    """
    sintral_top = ""
    sintral2x_top = ""
    lines_to_read = list(range(0, 22))
    for position, line in sintral_template:
        if position in lines_to_read:
            sintral_top += line
            sintral2x_top += line
    return sintral_top, sintral2x_top


def make_3_color_line(combo, speed, wm_440, wm_TC, wmi_440, wmi_TC):
    """
    makes 3 color knitting lines
    reverts to single production on TC combinations that are not evenly divisible by 4
    --------------
    Parameters:
    --------------
    :param combo: (str)previous line from make_sintral loop through jtxt. Ex: .AY
    :param speed: (str): come entries dictionary, universal throughout sintral
    :param wm_440: (str)entries['wm36'], main takedown setting for single production 3-6 colors
    :param wm_TC: (str)entries['wm32x'], main takedown setting for double production
    :param wmi_440: (str)entries['wmi'], impulse takedown setting for 440
    :param wmi_TC: (str)entries['wmi78'], impulse takedown for
    :return: line1_440, line2_440, line1_TC, line2_TC
    """
    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    line1_440 = f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-R(6)/{combo[1]}{combo_1_pair}-{combo[1]}{combo_1_pair}{combo[0]}{combo_0_pair}{combo_2_pair}/{combo[2]}{combo_2_pair}-{combo[2]}{combo_2_pair}{combo[0]}{combo[1]};		Y:{system_0}/{system_1}/{system_2};	WM={wm_440}		WMI={wmi_440}	SX SX SX  MSEC={speed}"
    line2_440 = f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-R(6)/{combo[1]}{combo_1_pair}-{combo[1]}{combo_1_pair}{combo[0]}{combo_0_pair}{combo_2_pair}/{combo[2]}{combo_2_pair}-{combo[2]}{combo_2_pair}{combo[0]}{combo[1]};		Y:{system_0}/{system_1}/{system_2};	WM={wm_440}		WMI={wmi_440}	SX SX SX"
    if combo[0] == '.' and combo[1] == 'A' and combo[2] == 'Y':
        line1_TC = f"<<	S:<1+>.G(5)-R(6)/AH-AH.GO/YO-YO.A;		Y:2/3/4/2/3/4;	WM={wm_TC}		WMI={wmi_TC}	SX SX SX SX SX SX   MSEC={speed}"
        line2_TC = f">>	S:<1+>.G(5)-R(6)/AH-AH.GO/YO-YO.A;		Y:2/3/4/2/3/4;	WM={wm_TC}		WMI={wmi_TC}	SX SX SX SX SX SX   MSEC={speed}"
    else:
        line1_TC = line1_440
        line2_TC = line2_440
    return line1_440, line2_440, line1_TC, line2_TC


def make_4_color_line(combo, speed, wm, wmi):
    """

    :param combo:
    :param speed:
    :param wm:
    :param wmi:
    :return:
    """
    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    combo_3_pair = list(color_dict)[list(color_dict).index(combo[3]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    system_3 = systems[list(color_dict).index(combo[3])]
    line1 = f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3};	WM={wm}	WMI={wmi}	SX SX SX SX MSEC={speed}"
    line2 = f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3};	WM={wm}	WMI={wmi}	SX SX SX SX "

    return line1, line2


def make_5_color_line(combo, speed, empty_speed, wm_440, wm_tc, wmi):
    """

    :return:
    """

    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    combo_3_pair = list(color_dict)[list(color_dict).index(combo[3]) + 8]
    combo_4_pair = list(color_dict)[list(color_dict).index(combo[4]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    system_3 = systems[list(color_dict).index(combo[3])]
    system_4 = systems[list(color_dict).index(combo[4])]

    lines_440 = [
        f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4};	WM={wm_440}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f">>	S0 MSEC={empty_speed}",
        f"<<    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B;						WM={wm_440}	WMI={wmi}		SX",
        f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;			WM={wm_440}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f"<<	S0 MSEC={empty_speed}",
        f">>    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B;						WM={wm_440}	WMI={wmi}		SX"]

    lines_tc = [
        f"<<    S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL/{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4};	WM={wm_tc}	WMI={wmi}	SX SX SX SX SX  MSEC={speed}",
        f">>    S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL/{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4};	WM={wm_tc}	WMI={wmi}	SX SX SX SX SX"
    ]

    return lines_440, lines_tc


def make_6_color_line(combo, speed, empty_speed, wm_440, wm_tc, wmi):
    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    combo_3_pair = list(color_dict)[list(color_dict).index(combo[3]) + 8]
    combo_4_pair = list(color_dict)[list(color_dict).index(combo[4]) + 8]
    combo_5_pair = list(color_dict)[list(color_dict).index(combo[5]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    system_3 = systems[list(color_dict).index(combo[3])]
    system_4 = systems[list(color_dict).index(combo[4])]
    system_5 = systems[list(color_dict).index(combo[5])]

    lines_440 = [
        f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4}/{system_5};	WM={wm_440}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f">>	S0 MSEC={empty_speed}",
        f"<<    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL;					WM={wm_440}	WMI={wmi}		SX SX",
        f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;			WM={wm_440}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f"<<	S0 MSEC={empty_speed}",
        f">>    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL;					WM={wm_440}	WMI={wmi}		SX SX"]

    lines_tc = [
        f"<<    S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL/{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4}/{system_5};	WM={wm_tc}	WMI={wmi}	SX SX SX SX SX SX  MSEC={speed}",
        f">>    S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL/{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4}/{system_5};	WM={wm_tc}	WMI={wmi}	SX SX SX SX SX SX"
    ]

    return lines_440, lines_tc


def make_7_color_line(combo, speed, empty_speed, wm, wmi):
    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    combo_3_pair = list(color_dict)[list(color_dict).index(combo[3]) + 8]
    combo_4_pair = list(color_dict)[list(color_dict).index(combo[4]) + 8]
    combo_5_pair = list(color_dict)[list(color_dict).index(combo[5]) + 8]
    combo_6_pair = list(color_dict)[list(color_dict).index(combo[6]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    system_3 = systems[list(color_dict).index(combo[3])]
    system_4 = systems[list(color_dict).index(combo[4])]
    system_5 = systems[list(color_dict).index(combo[5])]
    system_6 = systems[list(color_dict).index(combo[6])]

    lines = [
        f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4}/{system_5}/{system_6};	WM={wm}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f">>	S0 MSEC={empty_speed}",
        f"<<    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL/{combo[6]}{combo_6_pair}-{combo_6_pair}.AYT*I+B;				WM={wm}	WMI={wmi}		SX SX SX MSEC={speed}",
        f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;		WM={wm}		WMI={wmi}		SX SX SX SX ",
        f"<<	S0 MSEC={empty_speed}",
        f">>    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL/{combo[6]}{combo_6_pair}-{combo_6_pair}.AYT*I+B;				WM={wm}	WMI={wmi}		SX SX SX MSEC={speed}",
    ]

    return lines


def make_8_color_line(combo, speed, empty_speed, wm, wmi):
    combo_0_pair = list(color_dict)[list(color_dict).index(combo[0]) + 8]
    combo_1_pair = list(color_dict)[list(color_dict).index(combo[1]) + 8]
    combo_2_pair = list(color_dict)[list(color_dict).index(combo[2]) + 8]
    combo_3_pair = list(color_dict)[list(color_dict).index(combo[3]) + 8]
    combo_4_pair = list(color_dict)[list(color_dict).index(combo[4]) + 8]
    combo_5_pair = list(color_dict)[list(color_dict).index(combo[5]) + 8]
    combo_6_pair = list(color_dict)[list(color_dict).index(combo[6]) + 8]
    combo_7_pair = list(color_dict)[list(color_dict).index(combo[7]) + 8]
    system_0 = systems[list(color_dict).index(combo[0])]
    system_1 = systems[list(color_dict).index(combo[1])]
    system_2 = systems[list(color_dict).index(combo[2])]
    system_3 = systems[list(color_dict).index(combo[3])]
    system_4 = systems[list(color_dict).index(combo[4])]
    system_5 = systems[list(color_dict).index(combo[5])]
    system_6 = systems[list(color_dict).index(combo[6])]
    system_7 = systems[list(color_dict).index(combo[7])]

    lines = [
        f"<<	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;	Y:{system_0}/{system_1}/{system_2}/{system_3}/{system_4}/{system_5}/{system_6}/{system_7};	WM={wm}	WMI={wmi}		SX SX SX SX  MSEC={speed}",
        f">>	S0 MSEC={empty_speed}",
        f"<<    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL/{combo[6]}{combo_6_pair}-{combo_6_pair}.AYT*I+B/{combo[7]}{combo_7_pair}-{combo[7]}GHOWZEKL;				WM={wm}	WMI={wmi}		SX SX SX SX MSEC={speed}",
        f">>	S:<1+>{combo[0]}{combo_0_pair}(5)-{combo_0_pair}.AYT*I+B(7)/{combo[1]}{combo_1_pair}-{combo[1]}GHOWZEKL/{combo[2]}{combo_2_pair}-{combo_2_pair}.AYT*I+B/{combo[3]}{combo_3_pair}-{combo[3]}GHOWZEKL;		WM={wm}		WMI={wmi}		SX SX SX SX ",
        f"<<	S0 MSEC={empty_speed}",
        f">>    S:{combo[4]}{combo_4_pair}-{combo_4_pair}.AYT*I+B/{combo[5]}{combo_5_pair}-{combo[5]}GHOWZEKL/{combo[6]}{combo_6_pair}-{combo_6_pair}.AYT*I+B/{combo[7]}{combo_7_pair}-{combo[7]}GHOWZEKL;;				WM={wm}	WMI={wmi}		SX SX SX SX MSEC={speed}",
    ]

    return lines


def find_counts(text_list):
    new_list = []
    for line in text_list:
        string = line
        new_string = ""
        while string:
            if "P" in string:
                new_list.append("481P")
                break

            if len(string) == 1:
                new_string += string[0]
                new_list.append(new_string)
                break
            sub_string1 = string[0]
            sub_string2 = string[1]
            if sub_string1 == sub_string2:
                match = True
                count = 1
                while match is True:
                    if count == (len(string) - 1):
                        match = False
                        new_string += f"{count + 1}{sub_string1}"
                        string = string[count + 1:]

                    else:
                        sub_string1 = string[count]
                        sub_string2 = string[count + 1]
                        if sub_string1 == sub_string2:
                            count += 1
                        else:
                            match = False
                            new_string += f"{count + 1}{sub_string1}"
                            string = string[count + 1:]
            else:
                new_string += string[0]
                string = string[1:]
        # new_list.append(new_string)
    return new_list


def find_patterns(text_list):
    new_list = []
    for line in text_list:
        new_line = ""

        while line:

            index = 0
            current = line[index]
            color_1 = ""
            while current.isnumeric():
                index += 1
                current = line[index]

            color_1 = line[:index + 1]

            line = line[index + 1:]

            if len(line) == 0:
                new_line += color_1
                # new_list.append(new_line)
                break

            color_2 = ""
            index = 0
            current = line[index]

            while current.isnumeric():
                index += 1
                current = line[index]

            color_2 = line[:index + 1]

            color_pair = color_1 + color_2

            index = 0
            pair_length = len(color_pair)
            next_pair = line[index + 1: index + 1 + pair_length]
            pair_count = 1

            while color_pair == next_pair:
                pair_count += 1
                index += pair_length
                next_pair = line[index + 1: index + 1 + pair_length]

            if pair_count == 1:
                new_line += color_1
                # line = line[len(color_1):]
            else:
                new_line += f"{pair_count}({color_pair})"
                line = line[pair_count * len(color_pair) - 1:]

        new_list.append(new_line)
    return new_list


def make_plain_sintral(jtxt, entries, ja1=None):
    """

    pattern_color_dict={}
    for i in range(len(colors)):
        pattern_color_dict[colors[i]]=(systems[i],list(base_colors_8.values)[i][])
"""
    sintral_top, sintral2x_top = add_top_of_sintral()
    # Why did I make this?
    # colors=sort_colors(colors)
    # Make sintral_middle
    lines = jtxt.split('\n')
    last_line = ""
    idx = 0
    rep_count = 0
    sintral_middle = ""
    sintral2x_middle = ""
    lines[-1] = lines[-1][0:5] + 'Q' + lines[-1][6:]
    pers_middle = False
    for line in lines:
        if "$" in line[:7]:
            continue
        this_line = ""
        line_slice = line[5:13]
        for char in line_slice:
            if char.isdigit():
                break
            else:
                this_line += char
        pers_start = False
        pers_stop = False
        if this_line != last_line and idx > 0:

            # We have a change in color combinations
            num_colors = len(last_line)

            if "k" in this_line:
                pers_start = True
                this_line = last_line
                start_line = int(line[0:4])
                lines[idx + 39] = lines[idx + 39][0:5] + 'X' + lines[idx + 39][6:]

            if 'X' in this_line:
                pers_stop = True
                this_line = last_line
                stop_line = str(start_line + 40)

            if 'Q' in this_line:
                rep_count += 1

            if num_colors == 3:
                line1_440, line2_440, line1_TC, line2_TC = make_3_color_line(last_line, entries['speed'],
                                                                             entries['wm36'],
                                                                             entries['wm32x'], entries['wmi'],
                                                                             entries['wmi78'])

                if pers_middle:
                    line1_440 = re.sub(r"S:<1\+>", r"S:<1->", line1_440)
                    line2_440 = re.sub(r"S:<1\+>", r"S:<1->", line2_440)
                    line1_TC = re.sub(r"S:<1\+>", r"S:<1->", line1_TC)
                    line2_TC = re.sub(r"S:<1\+>", r"S:<1->", line2_TC)

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                sintral_middle += f"{line1_440}\n"
                sintral_middle += f"{line2_440}\n"
                sintral_middle += f"REPEND\n"

                # Deal with an uneven number of double production strokes
                if rep_count == 2:
                    sintral2x_middle += f"{line1_440}\n"
                    sintral2x_middle += f"{line2_440}\n"

                elif last_line != ".AY":
                    sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                    sintral2x_middle += f"{line1_440}\n"
                    sintral2x_middle += f"{line2_440}\n"
                    sintral2x_middle += f"REPEND\n"

                elif rep_count % 4 == 0:
                    sintral2x_middle += f"REP*{int(rep_count / 4)}\n"
                    sintral2x_middle += f"{line1_TC}\n"
                    sintral2x_middle += f"{line2_TC}\n"
                    sintral2x_middle += f"REPEND\n"

                else:
                    sintral2x_middle += f"REP*{int((rep_count - 2) / 4)}\n"
                    sintral2x_middle += f"{line1_TC}\n"
                    sintral2x_middle += f"{line2_TC}\n"
                    sintral2x_middle += f"REPEND\n"
                    sintral2x_middle += f"{line1_440}\n"
                    sintral2x_middle += f"{line2_440}\n"

            if num_colors == 4:
                line1, line2 = make_4_color_line(last_line, entries['speed'], entries['wm36'], entries['wmi'])

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                sintral_middle += f"{line1}\n"
                sintral_middle += f"{line2}\n"
                sintral_middle += f"REPEND\n"

                sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                sintral2x_middle += f"{line1}\n"
                sintral2x_middle += f"{line2}\n"
                sintral2x_middle += f"REPEND\n"

            if num_colors == 5:
                lines_440, lines_tc = make_5_color_line(last_line, entries['speed'],
                                                        entries['empty_speed'],
                                                        entries['wm36'],
                                                        entries['wm56'], entries['wmi'])

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines_440:
                    sintral_middle += f"{line}\n"
                sintral_middle += f"REPEND\n"

                sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines_tc:
                    sintral2x_middle += f"{line}\n"
                sintral2x_middle += f"REPEND\n"

            if num_colors == 6:
                lines_440, lines_tc = make_6_color_line(last_line, entries['speed'],
                                                        entries['empty_speed'],
                                                        entries['wm36'],
                                                        entries['wm56'], entries['wmi'])

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines_440:
                    sintral_middle += f"{line}\n"
                sintral_middle += f"REPEND\n"

                sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines_tc:
                    sintral2x_middle += f"{line}\n"
                sintral2x_middle += f"REPEND\n"

            if num_colors == 7:
                lines = make_7_color_line(last_line, entries['speed'],
                                          entries['empty_speed'],
                                          entries['wm7'], entries['wmi78'])

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines:
                    sintral_middle += f"{line}\n"
                sintral_middle += f"REPEND\n"

                sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines:
                    sintral2x_middle += f"{line}\n"
                sintral2x_middle += f"REPEND\n"

            if num_colors == 8:

                lines = make_8_color_line(last_line, entries['speed'],
                                          entries['empty_speed'],
                                          entries['wm8'], entries['wmi78'])

                sintral_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines:
                    sintral_middle += f"{line}\n"
                sintral_middle += f"REPEND\n"

                sintral2x_middle += f"REP*{int(rep_count / 2)}\n"
                for line in lines:
                    sintral2x_middle += f"{line}\n"
                sintral2x_middle += f"REPEND\n"

            if pers_start:
                sintral_middle += ja1
                sintral2x_middle += ja1
                pers_start = False
                rep_count = 2
                pers_middle = True
            elif pers_stop:
                pers_middle = False
                sintral_middle += f"JA1={stop_line}\n"
                sintral2x_middle += f"JA1={stop_line}\n"
                pers_stop = False
                rep_count = 0
            else:
                rep_count = 1
        else:
            rep_count += 1

        last_line = this_line
        idx += 1

    # Add sintral lines 900 and below
    sintral_bottom, sintral2x_bottom = add_bottom_of_sintral()

    sintral = sintral_top + sintral_middle + sintral_bottom
    sintral2x = sintral2x_top + sintral2x_middle + sintral2x_bottom

    line_number = 1
    sintral_final = ""
    for line in sintral.split("\n"):
        if line[0] == "9":
            sintral_final += f"{line}\n"
        else:
            sintral_final += f"{str(line_number)} {line}\n"
        line_number += 1

    line_number = 1
    sintral2x_final = ""
    for line in sintral2x.split("\n"):
        if line[0] == "9":
            sintral2x_final += f"{line}\n"
        else:
            sintral2x_final += f"{str(line_number)} {line}\n"
        line_number += 1

    return sintral_final, sintral2x_final


def add_pers_barcode(bitmap, start_pers):
    pixels = bitmap.load()
    pixels[0, start_pers] = color_dict["k"]
    bitmap.show()
    return bitmap


def get_text_width(text_string, font):
    if text_string == " ":
        return font.getsize(text_string)[0]

    return font.getmask(text_string).getbbox()[2]


def kern(name, draw_object, y, space, font_name, font_size, fill, alignment):
    chars = [char for char in name]

    total_width = 0

    fnt = ImageFont.truetype(f"Fonts/{font_name}.ttf", font_size)

    width = fnt.getsize(name)[0]

    # check and adjust font_size
    while width > 360:
        font_size -= 2
        fnt = ImageFont.truetype(f"Fonts/{font_name}.ttf", font_size)
        width = fnt.getsize(name)[0]

    for char in chars:
        width_text = get_text_width(char, fnt)
        total_width += (width_text + int(space))

    __, height_text = draw_object.textsize(name, fnt)
    __, offset_y = fnt.getoffset(name)
    height_text += offset_y

    width_adjuster = 0

    if alignment == "Center":
        alignment_adjuster = 0
    elif alignment == "Align Left":
        alignment_adjuster = -((473 / 2 - total_width / 2) - 36)
    elif alignment == "Align Right":
        alignment_adjuster = (473 / 2 + total_width / 2) - total_width - 36

    for char in chars:
        width_text = get_text_width(char, fnt)
        top_left_x = (473 / 2 - total_width / 2) + width_adjuster + alignment_adjuster
        top_left_y = (40 / 2 - height_text / 2) + y
        xy = top_left_x, top_left_y
        width_adjuster += width_text + int(space)
        draw_object.text(xy, char, font=fnt, fill=fill)


def TitleCase(string):
    return re.sub(r"['\w]+", lambda m: m.group(0).capitalize(), string)


class MyGUI:

    def __init__(self, master):
        self.master = master
        master.title("Logo Knits Production App")

        self.plain_folder_button = Button(master, text="Do a Whole Folder All The Way. Not Personalized",
                                          command=self.plain_folder,
                                          highlightbackground="#7eb6ff")
        self.plain_folder_button.grid(row=0, column=0, columnspan=2)

        self.plain_button = Button(master, text="Do a Single All The Way. Not Personalized", command=self.plain,
                                   highlightbackground="#7EB6FF")
        self.plain_button.grid(row=0, column=2, columnspan=2)

        # DON'T FORGET TO CHANGE THE COMMAND
        self.pers_folder_button = Button(master, text="Do a Whole Folder. Personalized", command=self.plain_folder,
                                         highlightbackground="#838EDE")
        self.pers_folder_button.grid(row=1, column=0, columnspan=2)

        self.pers_button = Button(master, text="Do a Single. Personalized", command=self.pers_single,
                                  highlightbackground="#838EDE")
        self.pers_button.grid(row=1, column=2, columnspan=2, )

        self.skip_reduction_var = IntVar()
        self.skip_reduction_button = Checkbutton(master, text="Skip the Color Reduction",
                                                 variable=self.skip_reduction_var,
                                                 highlightbackground="#7eb8ff")
        self.skip_reduction_button.grid(row=2, column=0, columnspan=2)

        self.sintral_button = Button(master, text="Make a Sintral", command=self.just_sintral,
                                     highlightbackground="#7EB8FF")
        self.sintral_button.grid(row=2, column=2, columnspan=2)

        self.speed_label = Label(master, text="Speed", bg="#8FBC8F")
        self.speed_entry = Entry(master)
        self.speed_entry.insert(0, ".65")
        self.speed_label.grid(row=6, column=0)
        self.speed_entry.grid(row=6, column=1)

        self.empty_speed_label = Label(master, text="Empty Stroke Speed", bg="#8FBC8F")
        self.empty_speed_entry = Entry(master)
        self.empty_speed_entry.insert(0, "1.0")
        self.empty_speed_label.grid(row=6, column=2)
        self.empty_speed_entry.grid(row=6, column=3)

        self.wm32x_label = Label(master, text="3 Color TC WM", bg="#90EE90")
        self.wm32x_entry = Entry(master)
        self.wm32x_entry.insert(0, "8.5")
        self.wm32x_label.grid(row=7, column=0)
        self.wm32x_entry.grid(row=7, column=1)

        self.wm36_label = Label(master, text="3-6 Color 440 WM", bg="#90EE90")
        self.wm36_entry = Entry(master)
        self.wm36_entry.insert(0, "7")
        self.wm36_label.grid(row=7, column=2)
        self.wm36_entry.grid(row=7, column=3)

        self.wm56_label = Label(master, text="5-6 Color TC WM", bg="#90EE90")
        self.wm56_entry = Entry(master)
        self.wm56_entry.insert(0, "7.2")
        self.wm56_label.grid(row=8, column=0)
        self.wm56_entry.grid(row=8, column=1)

        self.wm7_label = Label(master, text="7 Color WM", bg="#90EE90")
        self.wm7_entry = Entry(master)
        self.wm7_entry.insert(0, "7.5")
        self.wm7_label.grid(row=8, column=2)
        self.wm7_entry.grid(row=8, column=3)

        self.wm8_label = Label(master, text="8 Color TC WM", bg="#90EE90")
        self.wm8_entry = Entry(master)
        self.wm8_entry.insert(0, "7.5")
        self.wm8_label.grid(row=9, column=0)
        self.wm8_entry.grid(row=9, column=1)

        self.wmi_label = Label(master, text="3-6 Color WMI", bg="#71C671")
        self.wmi_entry = Entry(master)
        self.wmi_entry.insert(0, "11")
        self.wmi_label.grid(row=9, column=2)
        self.wmi_entry.grid(row=9, column=3)

        self.wmi78_label = Label(master, text="2x and 7-8 Color WMI", bg="#71C671")
        self.wmi78_entry = Entry(master)
        self.wmi78_entry.insert(0, "12")
        self.wmi78_label.grid(row=10, column=0)
        self.wmi78_entry.grid(row=10, column=1)

        self.front_stitch_label = Label(master, text="NP 5", bg="#699864")
        self.front_stitch_entry = Entry(master)
        self.front_stitch_entry.insert(0, "5")
        self.front_stitch_label.grid(row=10, column=2)
        self.front_stitch_entry.grid(row=10, column=3)

        self.back_stitch_label = Label(master, text="NP 6", bg="#699864")
        self.back_stitch_entry = Entry(master)
        self.back_stitch_entry.insert(0, "8")
        self.back_stitch_label.grid(row=11, column=0)
        self.back_stitch_entry.grid(row=11, column=1)

        self.personalize_label = Button(master, text="Make Grids", highlightbackground="#688264",
                                        command=self.personalize)
        self.personalize_entry = Text(master)
        # self.back_stitch_entry.insert(0, "8")
        self.personalize_label.grid(row=16, column=2)
        self.personalize_entry.grid(row=12, column=1)

        self.scrollbar = Scrollbar(master)
        self.personalize_entry.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.personalize_entry.yview)
        self.scrollbar.grid(column=3, row=12, rowspan=1, sticky='NS')

        self.close_button = Button(master, text="Close", command=master.quit, highlightbackground="#B0E2FF")
        self.close_button.grid(row=16, column=0, pady=30, columnspan=2)

        font_size_options = ["10", "12", "14", "16", "20", "24", "30", "36", "40"]
        self.font_size_var = StringVar(master)
        self.font_size_var.set("24")
        self.font_size_label = Label(master, text="Font Size", bg="#699864")
        self.font_size = OptionMenu(master, self.font_size_var, *font_size_options)
        self.font_size.grid(row=13, column=1, pady=10)
        self.font_size_label.grid(row=13, column=0, pady=10)

        alignment_options = ["Center", "Align Left", "Align Right"]
        self.alignment_var = StringVar(master)
        self.alignment_var.set("Center")
        self.alignment_label = Label(master, text="Alignment", bg="#699864")
        self.alignment_size = OptionMenu(master, self.alignment_var, *alignment_options)
        self.alignment_size.grid(row=13, column=3, pady=10)
        self.alignment_label.grid(row=13, column=2, pady=10)

        font_options = []
        for file in os.listdir("Fonts/"):
            font_options.append(path_leaf(os.fsdecode(file))[:-4])
        self.font_var = StringVar(master)
        self.font_var.set(font_options[0])
        self.font_label = Label(master, text="Font", bg="#699864")
        self.font = OptionMenu(master, self.font_var, *sorted(font_options))
        self.font.grid(row=14, column=3, pady=10)
        self.font_label.grid(row=14, column=2, pady=10)

        kern_options = ["1", "2", "3", "4", "5"]
        self.kern_var = StringVar(master)
        self.kern_var.set("2")
        self.kern_label = Label(master, text="Kern", bg="#699864")
        self.kern = OptionMenu(master, self.kern_var, *kern_options)
        self.kern.grid(row=14, column=1, pady=10)
        self.kern_label.grid(row=14, column=0, pady=10)

        capitalize_options = ['Leave it alone', 'ALL CAPS', 'all lower', 'Title Case']
        self.capitalize_var = StringVar(master)
        self.capitalize_var.set("Leave it alone")
        self.capitalize_label = Label(master, text="Capitalize", bg="#699864")
        self.capitalize = OptionMenu(master, self.capitalize_var, *capitalize_options)
        self.capitalize.grid(row=15, column=1, pady=10)
        self.capitalize_label.grid(row=15, column=0, pady=10)

    def personalize(self):
        alignment = self.alignment_var.get()
        font_name = self.font_var.get()

        kern_value = self.kern_var.get()

        names = self.personalize_entry.get("1.0", 'end-1c').split('\n')
        num_names = len(names)
        num_grids = math.ceil(num_names / 20)
        answer = ask_grid_background()
        separator = Image.new('RGB', (473, 1), color_dict['P'])

        background = Image.new('RGB', (473, 841), color_dict['.'])
        filename = ""
        messagebox.showinfo("Name Count", f"There are {num_names} names in this list.")

        if answer:
            messagebox.showinfo("Bitmap", "Give me the design.")
            file_path = filedialog.askopenfilename()
            filename = path_leaf(file_path)
            filename = filename[:-4]
            __, __, center = read(file_path)
            center_string = "Auto"
            if center == 0:
                if messagebox.askyesno("Hmmm", f"I couldn't find a center...Do you want to tell me where to begin?"):
                    center = int(askstring("Where's the grid?", "How far in from the bottom edge does the grid start?"))
                    center_string = str(center)
                else:
                    return False
            img = Image.open(file_path)
            size_num = img.size
            section = img.crop((5, (size_num[1] - 55 - center), 478, (size_num[1] - center - 15)))
            background.paste(separator, (0, 0))
            for i in range(20):
                background.paste(section, (0, (41 * i + 1)))
                background.paste(separator, (0, (41 * i) + 41))
            # background.paste(info_section, (0, (41 * i) + 42))

        else:
            # background.paste(separator, (0, 0))
            center_string = "Blank"
            for i in range(20):
                # background.paste(section,(0,(41*i+1)))
                background.paste(separator, (0, (41 * i) + 41))

        today = datetime.today().strftime('%b-%d-%y')
        file_name = str(askstring("File Name", f"Name the files. The format will be:\n [your choice]-Grid n-{today}"))

        for i in range(num_grids):

            grid = background.copy()

            draw = ImageDraw.Draw(grid)
            font_size = math.ceil(int(self.font_size_var.get()) * 1.333)
            draw.fontmode = '1'

            y = 0
            n = 0

            for name in names:

                if self.capitalize_var.get() == "ALL CAPS":
                    name = name.upper()
                elif self.capitalize_var.get() == "all lower":
                    name = name.lower()
                elif self.capitalize_var.get() == "Title Case":
                    name = TitleCase(name)
                else:
                    pass

                kern(name=name, draw_object=draw, y=y, space=self.kern_var.get(), font_name=font_name,
                     font_size=font_size, fill=(152, 0, 152),
                     alignment=alignment)
                y += 41
                n += 1

                if n == 20:
                    if filename:
                        # print(f"C:/Users/Sitex.9.10.2020.A/Desktop/{file_name}-Grid {i+1}-{today}.bmp")
                        grid.save(f"C:/Sitex/Files/Working Folder/Bitmaps/{file_name}-Grid {i + 1}-{today}.bmp")
                    else:
                        grid.save(f"C:/Sitex/Files/Working Folder/Bitmaps/Current Grid {i + 1}-{today}.bmp")

                    names = names[20:]
                    break
            info_string = f"LineBeg:{center_string} Font:{font_name} Font Size:{self.font_size_var.get()} Kern:{kern_value}"
            kern(name=info_string, draw_object=draw, y=810, space=2, font_name='Arial', font_size=16,
                 fill=(0, 0, 0),
                 alignment="Align Left")
            grid.show()
            if filename:
                grid.save(f"C:/Sitex/Files/Working Folder/Bitmaps/{file_name}-Grid {i + 1}-{today}.bmp")
            else:
                grid.save(f"C:/Sitex/Files/Working Folder/Bitmaps/Current Grid {i + 1}-{today}.bmp")

    def plain(self):
        """
        What sintral color combinations are each of these used it?
        Speed: 3,4,5,6,7,8
        Empty Speed: 5,6,7,8
        WM32X: 3
        WM36: 3,4,5,6
        WM56: 5,6
        WM7: 7
        WM8: 8
        WMI: 3,4,5,6
        WMI78: 3,7,8
        """

        entries = {"speed": self.speed_entry.get(),
                   "empty_speed": self.empty_speed_entry.get(),
                   "wm32x": self.wm32x_entry.get(),
                   "wm36": self.wm36_entry.get(),
                   "wm56": self.wm56_entry.get(),
                   "wm7": self.wm7_entry.get(),
                   "wm8": self.wm8_entry.get(),
                   "wmi": self.wmi_entry.get(),
                   "wmi78": self.wmi78_entry.get(),
                   "front_stitch": self.front_stitch_entry.get(),
                   "back_stitch": self.back_stitch_entry.get()}

        file_path = filedialog.askopenfilename()
        filename = path_leaf(file_path)
        filename = filename[:-4]
        img, colors, center = read(file_path)
        barcoded, reduction_counts = make_barcode(img, colors)
        reduction_count = calculate_reduction(reduction_counts)
        if self.skip_reduction_var.get() == 1:
            reduction_count = 0
        line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
        reduced = remove_lines(barcoded, line_begin, reduction_count)
        folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
        new_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(new_path)
        reduced.save(f"{new_path}/{filename}-birdseye.bmp")
        compressed_txt, line_num = convert_to_jtxt(reduced)
        new_txt_file = open(f"{new_path}/{filename}_J.txt", 'w')
        new_txt_file.write(compressed_txt)
        new_txt_file.close()
        # not sure if this is necessary
        os.chdir('..')
        sheet = make_label(colors)
        sheet.save(f"{new_path}/{filename}-color_label.pdf")
        sintral, sintral2x = make_plain_sintral(compressed_txt, entries)
        new_txt_file = open(f"{new_path}/{filename}-sintral440.txt", 'w')
        new_txt_file.write(sintral)
        new_txt_file.close()
        new_txt_file = open(f"{new_path}/{filename}-sintralTC.txt", 'w')
        new_txt_file.write(sintral2x)
        new_txt_file.close()

    def plain_folder(self):
        folder_path = filedialog.askdirectory()
        directory = os.fsencode(folder_path)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            filename1 = path_leaf(file)
            filename1 = filename[:-4]
            if filename.endswith(".bmp") or filename.endswith(".Bmp"):
                messagebox.showinfo("Working", f"We're about to work on {filename}")
                file_path = os.fsdecode(os.path.join(directory, file))
                img, colors, center = read(file_path)
                barcoded, reduction_counts = make_barcode(img, colors)
                reduction_count = calculate_reduction(reduction_counts)
                line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
                reduced = remove_lines(barcoded, line_begin, reduction_count)
                folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
                new_path = os.path.join(os.path.dirname(file_path), folder_name)
                os.makedirs(new_path)
                reduced.save(f"{new_path}/{filename1}birdseyed.bmp")
                compressed_txt = convert_to_jtxt(reduced)
                new_txt_file = open(f"{new_path}/{filename1}_J.txt", 'w')
                new_txt_file.write(compressed_txt)
                new_txt_file.close()
                # not sure if this is necessary
                os.chdir('..')
                sheet = make_label(colors)
                sheet.save(f"{new_path}/{filename1}color_label.pdf")




    def just_birdseye(self):
        file_path = filedialog.askopenfilename()
        filename = path_leaf(file_path)
        filename = filename[:-4]
        img, colors, center = read(file_path)
        barcoded, reduction_counts = make_barcode(img, colors)
        reduction_count = calculate_reduction(reduction_counts)
        messagebox.showinfo("Reduction", f"Remove {int(reduction_count)} lines")
        folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
        new_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(new_path)
        barcoded.save(f"{new_path}/{filename}-birdseye.bmp")
        sheet = make_label(colors)
        sheet.save(f"{new_path}/{filename}-color_label.pdf")

    def just_sintral(self):

        entries = {"speed": self.speed_entry.get(),
                   "empty_speed": self.empty_speed_entry.get(),
                   "wm32x": self.wm32x_entry.get(),
                   "wm36": self.wm36_entry.get(),
                   "wm56": self.wm56_entry.get(),
                   "wm7": self.wm7_entry.get(),
                   "wm8": self.wm8_entry.get(),
                   "wmi": self.wmi_entry.get(),
                   "wmi78": self.wmi78_entry.get(),
                   "front_stitch": self.front_stitch_entry.get(),
                   "back_stitch": self.back_stitch_entry.get()}

        file_path = filedialog.askopenfilename()
        filename = path_leaf(file_path)
        filename = filename[:-4]
        with open(file_path, "r") as text_file:
            compressed_txt = ''.join(text_file.readlines())
        folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
        new_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(new_path)
        print(compressed_txt)
        #new_txt_file = open(f"{new_path}/{filename}_J.txt", 'w')
        #new_txt_file.write(compressed_txt)
        #new_txt_file.close()
        # not sure if this is necessary
        #os.chdir('..')

        sintral, sintral2x = make_plain_sintral(compressed_txt, entries)
        new_txt_file = open(f"{new_path}/{filename}-sintral440.txt", 'w')
        new_txt_file.write(sintral)
        new_txt_file.close()
        new_txt_file = open(f"{new_path}/{filename}-sintralTC.txt", 'w')
        new_txt_file.write(sintral2x)
        new_txt_file.close()

    def pers_single(self):

        entries = {"speed": self.speed_entry.get(),
                   "empty_speed": self.empty_speed_entry.get(),
                   "wm32x": self.wm32x_entry.get(),
                   "wm36": self.wm36_entry.get(),
                   "wm56": self.wm56_entry.get(),
                   "wm7": self.wm7_entry.get(),
                   "wm8": self.wm8_entry.get(),
                   "wmi": self.wmi_entry.get(),
                   "wmi78": self.wmi78_entry.get(),
                   "front_stitch": self.front_stitch_entry.get(),
                   "back_stitch": self.back_stitch_entry.get()}

        showinfo("Bitmap", "Give me the main design bitmap first.")
        file_path = filedialog.askopenfilename()
        filename = path_leaf(file_path)
        filename = filename[:-4]
        img, colors, center = read(file_path)
        barcoded, reduction_counts = make_barcode(img, colors)
        reduction_count = calculate_reduction(reduction_counts)
        start_pers = center - (reduction_count / 2)
        start_pers = math.floor(start_pers / 2.) * 2
        line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
        reduced = remove_lines(barcoded, line_begin, reduction_count)
        reduced = add_pers_barcode(reduced, start_pers)
        # Do the same thing now for the personalization grid
        # But no reductions
        grids = []
        grid_filenames = []
        showinfo("Grid", "Give me the personalization grid now.")
        grid_file_path = filedialog.askopenfilename()
        grid_filename = path_leaf(grid_file_path)
        grid_filename = grid_filename[:-4]
        grid_filenames.append(grid_filename)
        grid_img, grid_colors, center = read(grid_file_path, design_colors=colors)
        grid_barcoded, reduction_counts = make_barcode(grid_img, colors)
        grids.append(grid_barcoded)
        grid_answer = ask_multiple_grids()

        while grid_answer:
            showinfo("Grid", "Give me another grid now.")
            grid_file_path = filedialog.askopenfilename()
            grid_filename = path_leaf(grid_file_path)
            grid_filename = grid_filename[:-4]
            grid_filenames.append(grid_filename)
            grid_img, grid_colors, center = read(grid_file_path, design_colors=colors)
            grid_barcoded, reduction_counts = make_barcode(grid_img, colors)
            grids.append(grid_barcoded)
            grid_answer = ask_multiple_grids()

        # Save both new birdseyed bitmaps
        folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
        new_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(new_path)
        reduced.save(f"{new_path}/{filename}-birdseye.bmp")

        for i in range(len(grids)):
            grids[i].save(f"{new_path}/{grid_filenames[i]}-birdseye.bmp")

            compressed_txt, end_line_num = convert_to_jtxt(reduced)
            compressed_grid, end_line_num = convert_to_jtxt(grids[i], start_line=end_line_num)
            new_txt_file = open(f"{new_path}/{filename}_J.txt", 'w')
            new_txt_file.write(compressed_txt)
            new_txt_file.close()
            grid_new_txt_file = open(f"{new_path}/{grid_filenames[i]}_J.txt", 'w')
            grid_new_txt_file.write(compressed_grid)
            grid_new_txt_file.close()

            # make the new combined file
            combined = compressed_txt + "\n" + compressed_grid
            combined_new_txt_file = open(f"{new_path}/{grid_filenames[i]} Combined_J.txt", 'w')
            combined_new_txt_file.write(combined)
            combined_new_txt_file.close()

        # not sure if this is necessary
        os.chdir('..')
        sheet = make_label(colors)
        sheet.save(f"{new_path}/{filename}-color_label.pdf")
        ja1 = find_ja1(compressed_grid)
        sintral, sintral2x = make_plain_sintral(compressed_txt, entries, ja1)
        new_txt_file = open(f"{new_path}/{filename}-sintral440.txt", 'w')
        new_txt_file.write(sintral)
        new_txt_file.close()
        new_txt_file = open(f"{new_path}/{filename}-sintralTC.txt", 'w')
        new_txt_file.write(sintral2x)
        new_txt_file.close()


root = Tk()
my_gui = MyGUI(root)
root.mainloop()
