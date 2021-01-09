import tkinter as tk

class Example(tk.Frame):
    def __init__(self, parent):

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, background="black", height = 900, width = 800)
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.populate()

    def populate(self):
        '''Put in some fake data'''
        for row in range(100):
            tk.Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            t="this is the second column for row %s" %row
            tk.Label(self.frame, text=t).grid(row=row, column=2)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root=tk.Tk()
    example = Example(root)
    example.pack(side="top", fill="both", expand=True)
    root.mainloop()


    [[1.jpg, 2-2.jpg, ARTBOARD+final+grayArtboard+52.jpg, BFF+ARTBOARD+finalArtboard+68.jpg, BFF+ARTBOARD+finalArtboard+76.jpg, BFF+ARTBOARD+finalArtboard+85.jpg, FRANKBOWLINGSWANICOLLARLESSSHIRT1.jpg, NOSESSO19_cutout_1000x1500.png, purpletote.jpg, ROOTSPYJAMATROUSERS1.jpg, SCARF1.jpg, Screen+Shot+2020-09-18+at+9.38.37+AM.png], [SOULDBTAILOREDJACKET1.jpg, Untitled-1Artboard+22.jpg, white_front_1000x1500.png]]
pyimage2