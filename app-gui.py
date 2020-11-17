from Pro import main_app
from create_classifier import train_classifer
from create_dataset import start_capture
import tkinter as tk
from tkinter import font as tkfont, filedialog
from tkinter import messagebox, PhotoImage
import sys
import cv2
from random import randint

names = set()


class MainUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global names
        with open("nameslist.txt", "r") as f:
            x = f.read()
            z = x.rstrip().split(" ")
            for i in z:
                names.add(i)
        self.title_font = tkfont.Font(family='Helvetica', size=16, weight="bold")
        self.title("FaDeD")
        self.resizable(False, False)
        self.geometry("500x260")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.active_name = None
        container = tk.Frame(self)
        container.grid(sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, track):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):

        if messagebox.askokcancel("Quit", "Are you sure?"):
            global names
            f = open("nameslist.txt", "a+")
            for i in names:
                f.write(i+" ")
            self.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        render = PhotoImage(file='logo1.png')
        self.config(bg='#A0A2A3')
        img = tk.Label(self, image=render)
        img.image = render
        img.grid(row=0, column=1, rowspan=4, sticky="nsew")
        label = tk.Label(self, text="        WELCOME        ", font=self.controller.title_font, bg='#A0A2A3',
                         fg="#263942")
        label.grid(row=0, sticky="ew")
        button1 = tk.Button(self, text="Add Data", padx=15, pady=1, fg="#000000", bg="#263942",
                            command=lambda: self.controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Detect", padx=22.5, pady=1, fg="#000000", bg="#263942",
                            command=lambda: self.controller.show_frame("PageTwo"))
        button3 = tk.Button(self, text="Quit", padx=30, pady=1, fg="#263942", bg="#ffffff",
                            command=self.on_closing)
        button4 = tk.Button(self, text="Track", padx=25, pady=1, fg="#000000", bg="#263942",
                            command=lambda: self.controller.show_frame("track"))
        button1.place(x=30, y=60)
        button2.place(x=30, y=100)
        button4.place(x=30, y=140)
        button3.place(x=30, y=180)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure?"):
            global names
            with open("nameslist.txt", "w") as f:
                for i in names:
                    f.write(i + " ")
            self.controller.destroy()


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Label(self, text="Enter the name", fg="#263942",
                 font='Helvetica 12 bold').grid(row=0, column=0, pady=10, padx=5)
        self.user_name = tk.Entry(self, borderwidth=3, bg="lightgrey", font='Helvetica 11')
        self.user_name.grid(row=0, column=1, pady=10, padx=10)
        self.buttoncanc = tk.Button(self, text="Cancel", bg="#ffffff", fg="#263942",
                                    command=lambda: controller.show_frame("StartPage"))
        self.buttonext = tk.Button(self, text="Next", fg="#000000", bg="#263942", command=self.start_training)
        self.buttoncanc.grid(row=1, column=0, pady=10, ipadx=5, ipady=4)
        self.buttonext.grid(row=1, column=1, pady=10, ipadx=5, ipady=4)

    def start_training(self):
        global names
        if self.user_name.get() == "None":
            messagebox.showerror("Error", "Name cannot be 'None'")
            return
        elif self.user_name.get() in names:
            messagebox.showerror("Error", "User already exists!")
            return
        elif len(self.user_name.get()) == 0:
            messagebox.showerror("Error", "Name cannot be empty!")
            return
        name = self.user_name.get()
        names.add(name)
        self.controller.active_name = name
        self.controller.frames["PageTwo"].refresh_names()
        self.controller.show_frame("PageThree")


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        global names
        self.controller = controller
        tk.Label(self, text="Select user", fg="#263942",
                 font='Helvetica 12 bold').grid(row=0, column=0, padx=10, pady=10)
        self.buttoncanc = tk.Button(self, text="Cancel", command=lambda: controller.show_frame("StartPage"),
                                    bg="#ffffff", fg="#263942")
        self.menuvar = tk.StringVar(self)
        self.dropdown = tk.OptionMenu(self, self.menuvar, *names)
        self.dropdown.config(bg="lightgrey")
        self.dropdown["menu"].config(bg="lightgrey")
        self.buttonext = tk.Button(self, text="Next", command=self.nextfoo, fg="#000000", bg="#263942")
        self.dropdown.grid(row=0, column=1, ipadx=8, padx=10, pady=10)
        self.buttoncanc.grid(row=1, ipadx=5, ipady=4, column=0, pady=10)
        self.buttonext.grid(row=1, ipadx=5, ipady=4, column=1, pady=10)

    def nextfoo(self):
        if self.menuvar.get() == "None":
            messagebox.showerror("ERROR", "Name cannot be 'None'")
            return
        self.controller.active_name = self.menuvar.get()
        self.controller.show_frame("PageFour")

    def refresh_names(self):
        global names
        self.menuvar.set('')
        self.dropdown['menu'].delete(0, 'end')
        for name in names:
            self.dropdown['menu'].add_command(label=name, command=tk._setit(self.menuvar, name))


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.numimglabel = tk.Label(self, text="Number of images captured = 0", font='Helvetica 12 bold', fg="#263942")
        self.numimglabel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
        self.capturebutton = tk.Button(self, text="Capture Data Set", fg="#000000", bg="#263942", command=self.capimg)
        self.trainbutton = tk.Button(self, text="Train The Model", fg="#000000", bg="#263942", command=self.trainmodel)
        self.capturebutton.grid(row=1, column=0, ipadx=5, ipady=4, padx=10, pady=20)
        self.trainbutton.grid(row=1, column=1, ipadx=5, ipady=4, padx=10, pady=20)

    def capimg(self):
        self.numimglabel.config(text=str("Captured Images = 0 "))
        messagebox.showinfo("INSTRUCTIONS", "We will Capture 100 pic of your Face.")
        x = start_capture(self.controller.active_name)
        self.controller.num_of_images = x
        self.numimglabel.config(text=str("Number of images captured = "+str(x)))

    def trainmodel(self):
        if self.controller.num_of_images < 100:
            messagebox.showerror("ERROR", "No enough Data, Capture at least 100 images!")
            return
        train_classifer(self.controller.active_name)
        messagebox.showinfo("SUCCESS", "The modele has been successfully trained!")
        self.controller.show_frame("PageFour")


class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Face Recognition", font='Helvetica 16 bold')
        label.grid(row=0, column=0, sticky="ew")
        button1 = tk.Button(self, text="Face Recognition", command=self.openwebcam, fg="#ffffff", bg="#263942")
        button4 = tk.Button(self, text="Go to Home Page", command=lambda: self.controller.show_frame("StartPage"),
                            bg="#ffffff", fg="#263942")
        button1.grid(row=1, column=0, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)
        button4.grid(row=1, column=1, sticky="ew", ipadx=5, ipady=4, padx=10, pady=10)

    def openwebcam(self):
        main_app(self.controller.active_name)


text1 = ""


class track(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def fileopen():
            file1 = filedialog.askopenfile()
            entryText.set(file1.name)
            global text1
            text1 = file1.name

        def runtrack():

            print(text1)

            trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']

            def createTrackerByName(trackerType):

                if trackerType == trackerTypes[0]:
                    tracker = cv2.TrackerBoosting_create()

                elif trackerType == trackerTypes[1]:
                    tracker = cv2.TrackerMIL_create()

                elif trackerType == trackerTypes[2]:
                    tracker = cv2.TrackerKCF_create()

                elif trackerType == trackerTypes[3]:
                    tracker = cv2.TrackerTLD_create()

                elif trackerType == trackerTypes[4]:
                    tracker = cv2.TrackerMedianFlow_create()

                elif trackerType == trackerTypes[5]:
                    tracker = cv2.TrackerGOTURN_create()

                elif trackerType == trackerTypes[6]:
                    tracker = cv2.TrackerMOSSE_create()

                elif trackerType == trackerTypes[7]:
                    tracker = cv2.TrackerCSRT_create()
                else:
                    tracker = None
                    print('Incorrect tracker name')
                    print('Available trackers are:')
                    for t in trackerTypes:
                        print(t)

                return tracker

            videoPath = text1

            cap = cv2.VideoCapture(videoPath)

            success, frame = cap.read()

            if not success:
                print('Failed to read video')
                sys.exit(1)

            bboxes = []
            colors = []

            while True:

                bbox = cv2.selectROI('MultiTracker', frame)
                bboxes.append(bbox)
                colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
                print("Press q to quit selecting boxes and start tracking")
                print("Press any other key to select next object")
                k = cv2.waitKey(0) & 0xFF
                if (k == 113):  # q is pressed
                    break

            print('Selected bounding boxes {}'.format(bboxes))

            trackerType = "CSRT"


            multiTracker = cv2.MultiTracker_create()


            for bbox in bboxes:
                multiTracker.add(createTrackerByName(trackerType), frame, bbox)


            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break


                success, boxes = multiTracker.update(frame)


                for i, newbox in enumerate(boxes):
                    p1 = (int(newbox[0]), int(newbox[1]))
                    p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                    cv2.rectangle(frame, p1, p2, colors[i], 2, 1)


                cv2.imshow('Tracker', frame)


                if cv2.waitKey(1) & 0xFF == 27:
                    break




        tk.Label( self, text="Tracker", font='Helvetica 30 bold').place(x=150,y=5)

        button1 = tk.Button(self, text="Upload Video", command=fileopen , bg="#263942")

        tk.Label(self, text="Path :").place(x=30,y=85)

        button2 = tk.Button(self,text="Open Tracker",command=runtrack,bg="#263942")

        button4 = tk.Button(self, text="Back", command=lambda: self.controller.show_frame("StartPage"), bg="#ffffff", fg="#263942")

        entryText = tk.StringVar()
        entry1 = tk.Entry(self,textvariable=entryText).place(x=70,y=85)

        button1.place(x=30,y=50)
        button2.place(x=30,y=130)
        button4.place(x=30,y=170)




app = MainUI()
app.iconphoto(False, tk.PhotoImage(file='icon.ico'))
app.mainloop()