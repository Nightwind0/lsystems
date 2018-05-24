#!/usr/bin/env python

import math
import cairo
import copy
import numpy as np

#turtle = Turtle()
#turtle.setSpacing(0.01)
#turtle.penDown()
#turtle.forward(ctx)
#turtle.turnLeft(90)
#turtle.forward(ctx)
#turtle.turnLeft(90);
#turtle.forward(ctx)
#turtle.turnRight(90);
#turtle.forward(ctx)

class Turtle:
    def __init__(self):
        self.loc = np.array([0.0,0.0])
        self.direction = np.array([1.0,0.0])
        self.penOn = True
        self.spacing = 0.02
        
    def setSpacing(self, width):
        self.spacing = width;
    def rotate(self, radians):
        c, s = np.cos(radians), np.sin(radians)
        j = np.matrix([[c,s], [-s, c]])
        m = np.dot(j, [self.direction[0],self.direction[1]])
        self.direction[0] = float(m.T[0])
        self.direction[1] = float(m.T[1])
    def penDown(self):
        self.penOn = True
    def penUp(self):
        self.penOn = False
    def forward(self, ctx):
        #print "fwd"
        newpt = self.loc + self.direction * self.spacing
        if self.penOn:
            #print "draw at %f, %f" % (newpt[0], newpt[1])
            ctx.move_to(self.loc[0], self.loc[1])
            ctx.set_line_width(0.002)
            ctx.set_source_rgb(0,0,0)
            ctx.line_to(newpt[0], newpt[1])
            ctx.close_path()
            ctx.stroke()
        self.loc = newpt
    def turnLeft(self, degrees):
        self.rotate(-np.deg2rad(degrees))
    def turnRight(self, degrees):
        self.rotate(np.deg2rad(degrees))

class LSystem:
    FORWARD = 1
    TURNLEFT = 2
    TURNRIGHT = 3
    PUSH = 4
    POP = 5
    def __init__(self, name):
        self.stack = []
        self.input = ""
        self.rules = {}
        self.bindMap = {}
        self.name = name
        self.scale = 0.02
        self.angle = 90 #degrees
        self.turtle = self.newTurtle()
    def newTurtle(self):
        turtle = Turtle()
        turtle.penDown()
        turtle.setSpacing(self.scale)
        return turtle
    def setScale(self, scale):
        self.scale = scale
        self.turtle.setSpacing(self.scale)
    def doAction(self, action, ctx):
        #print("Doing action %s" % action)
        if action == LSystem.FORWARD:
            self.turtle.forward(ctx)
        elif action == LSystem.TURNLEFT:
            self.turtle.turnLeft(self.angle)
        elif action == LSystem.TURNRIGHT:
            self.turtle.turnRight(self.angle)
    def setAngle(self, angle):
        self.angle = angle
    def addRule(self, start, end):
        self.rules[start] = end
    def bind(self, c, action):
        self.bindMap[c] = action
    def handleChar(self, c, ctx):
        if ctx != None:
            if c == "[":
                #print "push copy"
                self.stack.append(copy.copy(self.turtle))
            elif c == "]":
                #print "pop copy"
                self.turtle = self.stack.pop()
            elif c == "+":
                self.turtle.turnLeft(self.angle)
            elif c == "-":
                self.turtle.turnRight(self.angle)
            if c in self.bindMap:
                self.doAction(self.bindMap[c], ctx)
        if c in self.rules:
            return self.rules[c]
        else:
            return c
    def setStart(self, start):
        self.input = start
    def step(self, ctx):
        newinput = ""
        for c in self.input:
            resp = self.handleChar(c, ctx)
            if resp != None:
                newinput += resp
        self.input = newinput
        print(self.input)
    def drawPng(self, steps, width, height):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.scale(width, height)  # Normalizing the canvas

        pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
        pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
        pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity

        ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
        ctx.set_source(pat)
        ctx.fill()
        ctx.translate(0.5, 0.5)  # Changing the current transformation matrix
        for i in range(0,steps-1):
            self.step(None)
        self.step(ctx)
        surface.write_to_png(self.name + ".png")  # Output to PNG


striangle = LSystem("striangle")
striangle.setAngle(120)
striangle.bind("F", LSystem.FORWARD)
striangle.bind("G", LSystem.FORWARD)
striangle.addRule("F", "F-G+F+G-F")
striangle.addRule("G", "GG")
striangle.setStart("F-G-G")
#striangle.drawPng(7, 4096, 4096)

striangle2 = LSystem("striangle2")
striangle2.setAngle(60)
striangle2.setScale(0.002)
striangle2.bind("A", LSystem.FORWARD)
striangle2.bind("B", LSystem.FORWARD)
striangle2.addRule("A", "B-A-B")
striangle2.addRule("B", "A+B+A")
striangle2.setStart("A")
#striangle2.drawPng(10, 4096, 4096)

dragon = LSystem("dragon")
dragon.setAngle(90)
dragon.bind("F", LSystem.FORWARD)
dragon.addRule("X", "X+YF+")
dragon.addRule("Y", "-FX-Y")
dragon.setStart("FX")
dragon.setScale(0.005)
#dragon.drawPng(18, 4096, 4096)

plant = LSystem("plant")
plant.setAngle(25)
plant.setScale(0.001)
plant.bind("F", LSystem.FORWARD)
plant.addRule("X", "F+[[X]-X]-F[-FX]+X")
plant.addRule("F", "FF")
plant.setStart("X")
plant.drawPng(10, 4096, 4096)
