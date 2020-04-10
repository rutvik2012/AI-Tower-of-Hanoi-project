#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tkinter import *
from turtle import TurtleScreen, RawTurtle


class Disc(RawTurtle):
    
    def __init__(self, cv):
        RawTurtle.__init__(self, cv, shape="square", visible=False)
        self.pu()
        self.goto(-140,200)
    def config(self, k, n):
        self.hideturtle()
        f = float(k+1)/n
        self.shapesize(0.6, 1.6+5*f) 
        self.fillcolor(f, 0, 1-f)
        self.showturtle()


class Tower(list):
    
    def __init__(self, x):
       #empty tower
        self.x = x
    def push(self, d):
        d.setx(self.x)
        d.sety(-60+10*len(self))
        self.append(d)
    def pop(self, y=80):
        d = list.pop(self)
        d.sety(y)
        return d        


class HanoiEngine:
    
    def __init__(self, canvas, nrOfDiscs, speed, moveCntDisplay=None):
    
        self.ts = canvas
        self.ts.tracer(False)
        # setup scene
        self.designer = RawTurtle(canvas, shape="square")
        self.designer.penup()
        self.designer.shapesize(0.4, 25)
        self.designer.goto(0,-81); self.designer.stamp()
        self.designer.shapesize(4, 0.5)
        self.designer.fillcolor('Black')
        for x in -150, 0, 150:
            self.designer.goto(x,-5); self.designer.stamp()

        self.nrOfDiscs = nrOfDiscs
        self.speed = speed
        self.moveDisplay = moveCntDisplay
        self.running = False
        self.moveCnt = 0
        self.discs = [Disc(canvas) for i in range(10)]
        self.towerA = Tower(-150)
        self.towerB = Tower(0)
        self.towerC = Tower(150)
        self.ts.tracer(True)
        
    def setspeed(self):
        for disc in self.discs: disc.speed(self.speed)
   
    def hanoi(self, n, src, dest, temp):
        #use of recurssion for movement 
        if n > 0:
            for x in self.hanoi(n-1, src, temp, dest): yield None
            yield self.move(src, dest)
            for x in self.hanoi(n-1, temp, dest, src): yield None

    def move(self, src_tower, dest_tower):
        #movement of upper disks
        dest_tower.push(src_tower.pop())
        self.moveCnt += 1
        self.moveDisplay(self.moveCnt)

    def reset(self):
        # start a new game
        self.ts.tracer(False)
        self.moveCnt = 0
        self.moveDisplay(0)
        for t in self.towerA, self.towerB, self.towerC:
            while t != []: t.pop(200)
        for k in range(self.nrOfDiscs-1,-1,-1):
            self.discs[k].config(k, self.nrOfDiscs)
            self.towerA.push(self.discs[k])
        self.ts.tracer(True)
        self.HG = self.hanoi(self.nrOfDiscs,
                             self.towerA, self.towerC, self.towerB)
        
    def run(self):
       #true if game is over else false
        self.running = True
        try:
            while self.running:
                result = self.step()
            return result  # True iff done
        except StopIteration:  # game over
            return True

    def step(self):
        """perform one single step of the game,
        returns True if finished, else False"""
        try:
            next(self.HG)
            return 2**self.nrOfDiscs-1 == self.moveCnt
        except TclError: 
            return False
        
    def stop(self):
        """ ;-) """
        self.running = False


class Hanoi:
    """GUI for animated towers-of-Hanoi-game with upto 10 discs:"""

    def displayMove(self, move):
        """method to be passed to the Hanoi-engine as a callback
        to report move-count"""
        self.moveCntLbl.configure(text = "move:\n%d" % move)
    
    def adjust_nr_of_discs(self, e):
        """callback function for nr-of-discs-scale-widget"""
        self.hEngine.nrOfDiscs = self.discs.get()
        self.reset()

    def adjust_speed(self, e):
        """callback function for speeds-scale-widget"""
        self.hEngine.speed = self.tempo.get() % 10
        self.hEngine.setspeed()

    def setState(self, STATE):
        """most simple implementation of a finite state machine"""
        self.state = STATE
        try:
            if STATE == "START":
                self.discs.configure(state=NORMAL)
                self.discs.configure(fg="black")
                self.discsLbl.configure(fg="black")
                self.resetBtn.configure(state=DISABLED)
                self.startBtn.configure(text="start", state=NORMAL)
                self.stepBtn.configure(state=NORMAL)
            elif STATE == "RUNNING":
                self.discs.configure(state=DISABLED)
                self.discs.configure(fg="gray70")
                self.discsLbl.configure(fg="gray70")
                self.resetBtn.configure(state=DISABLED)
                self.startBtn.configure(text="pause", state=NORMAL)
                self.stepBtn.configure(state=DISABLED)
            elif STATE == "PAUSE":
                self.discs.configure(state=NORMAL)
                self.discs.configure(fg="black")
                self.discsLbl.configure(fg="black")
                self.resetBtn.configure(state=NORMAL)
                self.startBtn.configure(text="resume", state=NORMAL)
                self.stepBtn.configure(state=NORMAL)
            elif STATE == "DONE":
                self.discs.configure(state=NORMAL)
                self.discs.configure(fg="black")
                self.discsLbl.configure(fg="black")
                self.resetBtn.configure(state=NORMAL)
                self.startBtn.configure(text="start", state=DISABLED)
                self.stepBtn.configure(state=DISABLED)
            elif STATE == "TIMEOUT":
                self.discs.configure(state=DISABLED)
                self.discs.configure(fg="gray70")
                self.discsLbl.configure(fg="gray70")
                self.resetBtn.configure(state=DISABLED)
                self.startBtn.configure(state=DISABLED)
                self.stepBtn.configure(state=DISABLED)
        except TclError:
            pass
           
    def reset(self):
        #reseting the game
        self.hEngine.reset()
        self.setState("START")
        
    def start(self):
        
        if self.state in ["START", "PAUSE"]:
            self.setState("RUNNING")            
            if self.hEngine.run():
                self.setState("DONE")
            else:
                self.setState("PAUSE")
        elif self.state == "RUNNING":
            self.setState("TIMEOUT")
            self.hEngine.stop()

    def step(self):
        """callback function for step button.
        makes hEngine perform a single step"""
        self.setState("TIMEOUT")
        if self.hEngine.step():
            self.setState("DONE")
        else:
            self.setState("PAUSE")
                
    def __init__(self, nrOfDiscs, speed):
        """construct Hanoi-engine, build GUI and set STATE to "START"
        then launch mainloop()"""
        root = Tk()                            
        root.title("tower of hanoi project")
        cv = Canvas(root,width=430,height=200, bg="Black")
        cv.pack()
        cv = TurtleScreen(cv)
        self.hEngine = HanoiEngine(cv, nrOfDiscs, speed, self.displayMove)        
        fnt = ("Arial", 14, "italic")
        # set attributes: nr of discs, speed; display move count
        attrFrame = Frame(root) #contains scales to adjust game's attributes
        self.discsLbl = Label(attrFrame, width=7, height=2, font=fnt,
                              text="Rings:\n")
        self.discs = Scale(attrFrame, from_=1, to_=10, orient=HORIZONTAL,
                           font=fnt, length=75, showvalue=1, repeatinterval=10,
                           command=self.adjust_nr_of_discs)
        self.discs.set(nrOfDiscs)
        self.tempoLbl = Label(attrFrame, width=0,  height=0, font=fnt,
                              text = ":\n")
        self.tempo = Scale(from_=0, to_=10, orient=HORIZONTAL,
                           font=fnt, length=0, showvalue=1,repeatinterval=10,
                           command = self.adjust_speed)
        self.tempo.set(speed)
        self.moveCntLbl= Label(attrFrame, width=5, height=2, font=fnt,
                               padx=20, text=" next:\n0", anchor=CENTER)                        
        for widget in ( self.discsLbl, self.discs, self.tempoLbl, self.tempo,
                                                             self.moveCntLbl ):
            widget.pack(side=LEFT)
        attrFrame.pack(side=TOP)
        # control buttons: reset, step, start/pause/resume    
        ctrlFrame = Frame(root) # contains Buttons to control the game 
        self.resetBtn = Button(ctrlFrame, width=0, text="", font=fnt,
                               state = DISABLED, padx=0)
        self.stepBtn  = Button(ctrlFrame, width=15, text="Next", font=fnt,
                               state = NORMAL,  padx=10, command = self.step)
        self.startBtn = Button(ctrlFrame, width=15, text="Go", font=fnt,
                               state = NORMAL,  padx=10, command = self.start)
        for widget in self.resetBtn, self.stepBtn, self.startBtn:
            widget.pack(side=LEFT)
        ctrlFrame.pack(side=TOP)

        self.state = "START"
        root.mainloop()

if __name__  == "__main__":
    Hanoi(0,0)


# In[ ]:




