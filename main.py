
from tkinter import *
import os
import os.path, sys
from tkinter import messagebox, filedialog

from scipy import misc
from PIL import Image

color_dict={'.':(255,255,255),
    'A':(0,0,0),
    'Y':(0,60,167),
    'T':(0,149,55),
    '*':(160,72,0),
    'I':(255,62,255),
    '+':(198,1,45),
    'B':(255,141,17),
    'G':(33,58,5),
    'H':(122,174,213),
    'O':(245,196,0),
    'W':(152,0,152),
    'Z':(128,255,0),
    'X':(137,138,142),
    'N':(75,8,103),
    'S':(167,20,51),
    'E':(104,96,104),
    'K': (64,0,56),
    'L': (17,27,78),
    'M': (2,86,48),
    'P': (64,0,0),
    'Q': (255,183,12),
    'a': (60,56,52),
    'y': (0,136,136),
    't': (133,226,29),
    'i': (252,218,17),
    'b': (196,73,0),
    'g': (213,144,0),
    'h': (61,17,19),
    'o': (213,199,186),
    'w': (249,218,224),
    'z': (112,2255,112),
    'e': (235,254,1),
    'k': (194,148,113),
    'l': (108,23,50),
    'm': (128,128,255),
    'p': (81,43,28),
    'q': (41,86,154)}

def read_color_code(pic,size_num):
    yarn_colors = []
    for i in range(8):
        current_color = pic[i, size_num[1] - 1]
        if current_color != color_dict['K']:
            yarn_colors.append(current_color)
    if all(x == yarn_colors[0] for x in yarn_colors):
        return False
    return yarn_colors

def read_bitmap_for_colors(pic,size_num):
    yarn_colors=[]
    for x in reversed(range(size_num[0])):
        for y in reversed(range(size_num[1]-15)):
            if pic[x,y] not in yarn_colors:
                yarn_colors.append(pic[x,y])
    return yarn_colors


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

        self.greet_button = Button(master, text="Barcode", command=self.read)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def read(self):
        large=(483,510)
        regular=(483,360)
        small=(483,296)

        file_path = filedialog.askopenfilename()
        img = Image.open(file_path)
        rgb_im = img.convert('RGB')
        pic=img.load()
        size_num=rgb_im.size

#Check that the size is right
        if size_num==large:
            size='large'
        elif size_num==regular:
            size='regular'
        elif size_num==small:
            size='small'
        else:
            messagebox.showinfo("Uh-oh,", f":( The dimensions are wrong.")
            return

#Check to see if there are unknown colors
        for x in range(size_num[0]):
            for y in range(size_num[1]):
                if pic[x,y] not in color_dict.values():
                    print(pic[x,y])
                    messagebox.showinfo("Uh-oh,",f":( there's an unknown color located at {x},{y}")
                    return
        messagebox.showinfo("Congrats","No unknown colors! Nice")

#Read the color coding in the bottom left corner or scan it to get them.
        colors_from_code=read_color_code(pic,size_num)
        if not colors_from_code:
            messagebox.showinfo("Don't worry", f"There's no color code for this one. I'll scan it myself.")

        colors_from_reading=read_bitmap_for_colors(pic,size_num)
        print(colors_from_code,colors_from_reading)



#Trim the edges and rotate
        height=size_num[1]-15
        img2 = img.crop((6,6, 478,height))
        img2.show(title=" ")
        img2.save('Cropped.bmp',"BMP",quality=100)
        #pic=img2.load()


        return

    def cycle_label_text(self, event):
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT) # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])

root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
