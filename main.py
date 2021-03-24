import ntpath
from tkinter import *
import os
import os.path, sys
from tkinter import messagebox, filedialog
from tkinter.messagebox import askokcancel, showinfo, WARNING, QUESTION
from tkinter.simpledialog import askstring
import pandas as pd
import labels
from reportlab.graphics import shapes
from scipy import misc
import PIL
from PIL import Image
import numpy as np
import textwrap
import itertools

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
              'h': (61, 17, 19),
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
               (61, 17, 19): "Olive",
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

systems=['2','3','4','5','6','7','1','8']

def read_color_code(pic, size_num):
    yarn_colors = []
    for i in range(8):
        current_color = pic[i, size_num[1] - 1]
        if current_color != color_dict['K']:
            yarn_colors.append(current_color)
    if all(x == yarn_colors[0] for x in yarn_colors):
        return False
    return yarn_colors


def read_bitmap_for_colors(pic, size_num):
    yarn_colors = []
    for x in reversed(range(size_num[0])):
        for y in reversed(range(size_num[1] - 15)):
            if pic[x, y] not in yarn_colors:
                yarn_colors.append(pic[x, y])
    return yarn_colors


def convert_colors_to_knitting(pic, size_num, colors):
    pixels = pic.load()
    oddity = 0
    for x in range(size_num[0]):
        for y in range(size_num[1]):
            current_color = pixels[x, y]
            color_index = colors.index(current_color)
            if oddity % 2 != 0:
                knitting_color = list(color_dict.values())[color_index + 8]
            else:
                knitting_color = list(color_dict.values())[color_index]
            pixels[x, y] = knitting_color
            oddity += 1
        oddity += 1
    return pic


def sort_colors(colors):
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

        if colors_in_row != last_row and y > 0 and y % 2 == 0:
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
                    pixels[0, y] = pair_1[0]
                    pixels[1, y] = pair_2[0]
                    pixels[2, y] = colors_in_row[1]
            elif colors_in_row[0] not in base_colors_3 and colors_in_row[1] not in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = colors_in_row[0]
                pixels[2, y] = colors_in_row[1]
                if go_backwards:
                    pixels[0, y] = pair_1[0]
                    pixels[1, y] = colors_in_row[0]
                    pixels[2, y] = colors_in_row[1]
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


def caclulate_reduction(counts):
    count_total = np.sum(np.array(counts))
    adjusted_counts = np.array(
        [counts[0], counts[1], counts[2], counts[3] * 1.031, counts[4] * 1.1, counts[5] * 1.222, counts[6] * 1.294,
         counts[7] * 1.31])
    adjusted_total = np.sum(adjusted_counts) - count_total
    return adjusted_total


def confirm():
    answer = askokcancel(
        title='Proceed?',
        message='Are you happy with the results? Or do you want to try again',
        icon=QUESTION)
    return answer


def remove_lines(bitmap, line_begin, reduction_count):
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
        return False


def read(file_path):
    large = (483, 510)
    regular = (483, 360)
    small = (483, 296)
    img = Image.open(file_path)
    rgb_im = img.convert('RGB')
    pic = img.load()
    size_num = rgb_im.size

    # Check that the size is right
    if size_num == large:
        size = 'large'
    elif size_num == regular:
        size = 'regular'
    elif size_num == small:
        size = 'small'
    else:
        messagebox.showinfo("Uh-oh,", f":( The dimensions are wrong.")
        return

    # Check to see if there are unknown colors
    for x in range(size_num[0]):
        for y in range(size_num[1]):
            if pic[x, y] not in color_dict.values():
                messagebox.showinfo("Uh-oh,", f":( there's an unknown color located at {x},{y}")
                return
    messagebox.showinfo("Congrats", "No unknown colors! Nice")

    # Read the color coding in the bottom left corner or scan it to get them.
    colors = read_color_code(pic, size_num)
    if not colors:
        messagebox.showinfo("Don't worry", f"There's no color code for this one. I'll scan it myself.")

    colors = read_bitmap_for_colors(pic, size_num)

    # Trim the edges and rotate
    height = size_num[1] - 15
    img2 = img.crop((5, 5, 478, height))
    img2 = img2.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    size_num = img2.size
    # pic=img2.load()

    # Convert the bitmap to it's knitting colors
    img3 = convert_colors_to_knitting(img2, size_num, colors)
    return img3, colors


def convert_to_jtxt(image):
    pixels = image.load()
    size = image.size
    big_string = ""
    for y in range(size[1]):
        string = ""
        for x in range(481):
            current_color = pixels[x, y]
            string += list(color_dict.keys())[list(color_dict.values()).index(current_color)]
        big_string += string + '\n'

    txt_list = big_string.split('\n')
    line_num = 1002
    compressed = ""
    for line in txt_list:
        string = line
        length = len(big_string)
        new_string = ""
        i = 1
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
        compressed = compressed + str(line_num) + " " + new_string + "\n"
        line_num += 1
    return compressed


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def make_label(colors):
    specs = labels.Specification(75, 14, 1, 1, 70, 12, left_padding=0, top_padding=0, bottom_padding=0, right_padding=0,
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
    wrapper = textwrap.TextWrapper(width=60)
    string = wrapper.fill(text=string)
    sheet.add_label(string)
    return sheet


def add_bottom_of_sintral():
    sintral_bottom = ""
    sintral2x_bottom = ""
    lines_to_read = list(range(166, 253))
    for position, line in sintral_template:
        if position in lines_to_read:
            sintral_bottom += line
            sintral2x_bottom += line
    return sintral_bottom, sintral2x_bottom


def add_top_of_sintral():
    sintral_top = ""
    sintral2x_top = ""
    lines_to_read = list(range(0, 22))
    for position, line in sintral_template:
        if position in lines_to_read:
            sintral_top += line
            sintral2x_top += line
    return sintral_top, sintral2x_top

def make_3_color_line(combo,speed,front_ss,back_ss,wm_440,wm_TC,wmi_440,wmi_TC):
    line1_440=f"<<	S:<1+>{combo[0]}~({front_ss})-R({back_ss})/{combo[1]}~-{combo[1]}~{combo[0]}~~/{combo[2]}~-{combo[2]}~{combo[0]}{combo[1]};		Y:~/~/~;	WM={wm_440}		WMI={wmi_440}	SX SX SX  MSEC={speed}"
    line2_440=f">>	S:<1+>{combo[0]}~({front_ss})-R({back_ss})/{combo[1]}~-{combo[1]}~{combo[0]}~~/{combo[2]}~-{combo[2]}~{combo[0]}{combo[1]};		Y:~/~/~;	WM={wm_440}		WMI={wmi_440}	SX SX SX"
    line1_TC=
    line2_TC=

def make_4_color_line():

def make_5_color_line():

def make_6_color_line():

def make_7_color_line():

def make_8_color_line():

def make_plain_sintral(jtxt,colors):
    colors=sort_colors(colors)
    pattern_color_dict={}
    for i in range(len(colors)):
        pattern_color_dict[colors[i]]=(systems[i],list(base_colors_8.values)[i][])

    sintral_top, sintral2x_top = add_top_of_sintral()

    ##### Make sintral_middle
    lines = jtxt.split('\n')
    last_line = ""
    idx = 0
    rep_count = 0
    sintral_middle=""
    sintral2x_middle=""
    for line in lines:
        this_line = ""
        line_slice = line[5:13]
        for char in line_slice:
            if char.isdigit():
                break
            else:
                this_line += char

        if this_line != last_line and idx > 0:
            # We have a change in color combinations
            num_colors = len(this_line)
            print(num_colors,rep_count)


            rep_count=0
        else:
            rep_count += 1


        last_line = this_line
        idx += 1

    # Add sintral lines 900 and below
    sintral_bottom, sintral2x_bottom = add_bottom_of_sintral()

    sintral = sintral_top + sintral_bottom
    sintral2x = sintral2x_top + sintral2x_bottom

    return sintral, sintral2x


class MyFirstGUI:

    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.plain_folder_button = Button(master, text="Do a Whole Folder. Not Personalized", command=self.plain_folder,
                                          highlightbackground="#7eb6ff")
        self.plain_folder_button.grid(row=0, column=0, columnspan=2)

        self.plain_button = Button(master, text="Do a Single. Not Personalized", command=self.plain,
                                   highlightbackground="#7EB6FF")
        self.plain_button.grid(row=1, column=0, columnspan=2)

        # DON'T FORGET TO CHANGE THE COMMAND
        self.pers_folder_button = Button(master, text="Do a Whole Folder. Personalized", command=self.plain_folder,
                                         highlightbackground="#838EDE")
        self.pers_folder_button.grid(row=2, column=0, columnspan=2)
        # DITTO HERE
        self.pers_button = Button(master, text="Do a Single. Personalized", command=self.plain,
                                  highlightbackground="#838EDE")
        self.pers_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        self.speed_label = Label(master, text="Speed", bg="#8FBC8F")
        self.speed_entry = Entry(master)
        self.speed_entry.insert(0, ".65")
        self.speed_label.grid(row=4, column=0)
        self.speed_entry.grid(row=4, column=1)

        self.empty_speed_label = Label(master, text="Empty Stroke Speed", bg="#8FBC8F")
        self.empty_speed_entry = Entry(master)
        self.empty_speed_entry.insert(0, "1.0")
        self.empty_speed_label.grid(row=5, column=0)
        self.empty_speed_entry.grid(row=5, column=1)

        self.wm32x_label = Label(master, text="3 Color TC WM", bg="#90EE90")
        self.wm32x_entry = Entry(master)
        self.wm32x_entry.insert(0, "8.5")
        self.wm32x_label.grid(row=6, column=0)
        self.wm32x_entry.grid(row=6, column=1)

        self.wm36_label = Label(master, text="3-6 Color 440 WM", bg="#90EE90")
        self.wm36_entry = Entry(master)
        self.wm36_entry.insert(0, "7")
        self.wm36_label.grid(row=7, column=0)
        self.wm36_entry.grid(row=7, column=1)

        self.wm56_label = Label(master, text="5-6 Color TC WM", bg="#90EE90")
        self.wm56_entry = Entry(master)
        self.wm56_entry.insert(0, "7.2")
        self.wm56_label.grid(row=8, column=0)
        self.wm56_entry.grid(row=8, column=1)

        self.wm7_label = Label(master, text="7 Color WM", bg="#90EE90")
        self.wm7_entry = Entry(master)
        self.wm7_entry.insert(0, "7.3")
        self.wm7_label.grid(row=9, column=0)
        self.wm7_entry.grid(row=9, column=1)

        self.wm8_label = Label(master, text="8 Color TC WM", bg="#90EE90")
        self.wm8_entry = Entry(master)
        self.wm8_entry.insert(0, "7.5")
        self.wm8_label.grid(row=10, column=0)
        self.wm8_entry.grid(row=10, column=1)

        self.wmi_label = Label(master, text="3-6 Color WMI", bg="#71C671")
        self.wmi_entry = Entry(master)
        self.wmi_entry.insert(0, "11")
        self.wmi_label.grid(row=11, column=0)
        self.wmi_entry.grid(row=11, column=1)

        self.wmi78_label = Label(master, text="2x and 7-8 Color WMI", bg="#71C671")
        self.wmi78_entry = Entry(master)
        self.wmi78_entry.insert(0, "12")
        self.wmi78_label.grid(row=12, column=0)
        self.wmi78_entry.grid(row=12, column=1)

        self.front_stitch_label = Label(master, text="Front Stitch Setting", bg="#699864")
        self.front_stitch_entry = Entry(master)
        self.front_stitch_entry.insert(0, "5")
        self.front_stitch_label.grid(row=13, column=0)
        self.front_stitch_entry.grid(row=13, column=1)

        self.back_stitch_label = Label(master, text="Back Stitch Setting", bg="#699864")
        self.back_stitch_entry = Entry(master)
        self.back_stitch_entry.insert(0, "8")
        self.back_stitch_label.grid(row=14, column=0)
        self.back_stitch_entry.grid(row=14, column=1)

        self.close_button = Button(master, text="Close", command=master.quit, highlightbackground="#B0E2FF")
        self.close_button.grid(row=15, column=0, pady=30, columnspan=2)

    def plain(self):
        file_path = filedialog.askopenfilename()
        filename = path_leaf(file_path)
        filename = filename[:-4]
        img, colors = read(file_path)
        barcoded, reduction_counts = make_barcode(img, colors)
        reduction_count = caclulate_reduction(reduction_counts)
        line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
        reduced = remove_lines(barcoded, line_begin, reduction_count)
        folder_name = str(askstring("Folder Name", "Name the new folder for this pattern"))
        new_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(new_path)
        reduced.save(f"{new_path}/{filename}-birdseye.bmp")
        compressed_txt = convert_to_jtxt(reduced)
        new_txt_file = open(f"{new_path}/{filename}_J.txt", 'w')
        new_txt_file.write(compressed_txt)
        new_txt_file.close()
        # not sure if this is necessary
        os.chdir('..')
        sheet = make_label(colors)
        sheet.save(f"{new_path}/{filename}-color_label.pdf")
        sintral, sintral2x = make_plain_sintral(compressed_txt)
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
                img, colors = read(file_path)
                barcoded, reduction_counts = make_barcode(img, colors)
                reduction_count = caclulate_reduction(reduction_counts)
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


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
