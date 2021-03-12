from tkinter import *
import os
import os.path, sys
from tkinter import messagebox, filedialog
from tkinter.simpledialog import askstring
import pandas as pd

from scipy import misc
import PIL
from PIL import Image
import numpy as np

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
            # print(color_index)
            if oddity % 2 != 0:
                knitting_color = list(color_dict.values())[color_index + 8]
            else:
                knitting_color = list(color_dict.values())[color_index]
            pixels[x, y] = knitting_color
            oddity += 1
        oddity+=1
    return pic


def sort_colors(colors):
    ranks = []
    results = []
    for color in colors:
        ranks.append(base_colors_8[color][0])
        print(ranks)
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
        if num_colors_in_row == 1:
            if colors_in_row[0] not in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[0]
            else:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = pair_3[0]

        elif num_colors_in_row == 2:
            if colors_in_row[0] not in base_colors_3 and colors_in_row[1] in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[0]
            elif colors_in_row[1] not in base_colors_3 and colors_in_row[0] in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = colors_in_row[1]
            elif colors_in_row[0] not in base_colors_3 and colors_in_row[1] not in base_colors_3:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = colors_in_row[0]
                pixels[2, y] = colors_in_row[1]
            else:
                pixels[0, y] = pair_1[0]
                pixels[1, y] = pair_2[0]
                pixels[2, y] = pair_3[0]

        elif num_colors_in_row == 3:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
        elif num_colors_in_row == 4:
            pixels[0, y] = colors_in_row[0]
            pixels[1, y] = colors_in_row[1]
            pixels[2, y] = colors_in_row[2]
            pixels[3, y] = colors_in_row[3]

    return barcode_row, reduction_counts


def caclulate_reduction(counts):
    count_total = np.sum(np.array(counts))
    adjusted_counts = np.array(
        [counts[0], counts[1], counts[2], counts[3] * 1.031, counts[4] * 1.1, counts[5] * 1.222, counts[6] * 1.294,
         counts[7] * 1.31])
    adjusted_total = np.sum(adjusted_counts) - count_total
    return adjusted_total


def remove_lines(bitmap, line_begin, reduction_count):
    true_count = int(np.round(reduction_count / 2))
    if true_count % 2 != 0:
        true_count += 1
    size = bitmap.size
    canvas = Image.new('RGB', (481, size[1] - true_count), color_dict['.'])
    pixels = np.array(bitmap)
    part1 = bitmap.crop((0, 0, 482, int(line_begin)))
    # part2=bitmap.crop()
    # part3=bitmap.crop()
    # part4=bitmap.crop()
    canvas.paste(part1)
    bitmap.show()
    canvas.show()

    #print(pixels)


class MyFirstGUI:
    LABEL_TEXT = [
        "This is our first GUI!",
        "Actually, this is our second GUI.",
        "We made it more interesting...",
        "...by making this label interactive.",
        "Go on, click on it again.",
    ]

    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label_index = 0
        self.label_text = StringVar()
        self.label_text.set(self.LABEL_TEXT[self.label_index])
        self.label = Label(master, textvariable=self.label_text)
        self.label.bind("<Button-1>", self.cycle_label_text)
        self.label.pack()

        #   self.read_button = Button(master, text="Read the Bitmap", command=self.read)
        #   self.read_button.pack()

        self.plain_button = Button(master, text="Finish it. Not Personalized", command=self.plain)
        self.plain_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def read(self):
        large = (483, 510)
        regular = (483, 360)
        small = (483, 296)

        file_path = filedialog.askopenfilename()
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
                    print(pic[x, y])
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
        img2 = img.crop((6, 6, 479, height+1))
        img2 = img2.transpose(PIL.Image.FLIP_TOP_BOTTOM)
        size_num = img2.size
        # pic=img2.load()

        # Convert the bitmap to it's knitting colors
        img3 = convert_colors_to_knitting(img2, size_num, colors)
        # img3.show()

        return img3, colors

    def plain(self):
        img, colors = self.read()
        # img.show()
        barcoded, reduction_counts = make_barcode(img, colors)
        reduction_count = caclulate_reduction(reduction_counts)
        line_begin = askstring("Begin Reduction", "How far in from the edge should I start my removal?")
        reduced = remove_lines(barcoded, line_begin, reduction_count)
        #reduced.show()

    def cycle_label_text(self, event):
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT)  # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
