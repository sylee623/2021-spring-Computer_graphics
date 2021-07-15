# A. Set the window title to your student ID and the window size to (480,480).
# B. Use the following drawFrame() and drawTriangle() to draw the frame and triangle:
# C. First draw an untransformed white triangle and a global frame.
# D. Then draw a transformed blue triangle and its local frame. The triangle should be first rotated by 30 degrees and then translated by (0.6, 0, 0) w.r.t. the global frame.
# E. Then draw a transformed red triangle and its local frame. The triangle should be first translated by (0.6, 0, 0) and then rotated by 30 degrees w.r.t the global frame.
import glfw
import numpy as np
from OpenGL.GL import *

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    ## C
    drawFrame()
    glColor3ub(255, 255, 255)
    drawTriangle()
    glTranslatef(0.6, 0., 0.)
    glRotatef(30, 0., 0., 1.)
    drawFrame()
    glColor3ub(0, 0, 255)
    drawTriangle()
    glLoadIdentity()
    glRotatef(30, 0., 0., 1.)
    glTranslatef(0.6, 0., 0.)
    drawFrame()
    glColor3ub(255, 0, 0)
    drawTriangle()

## B
def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.])) 
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.])) 
    glVertex2fv(np.array([0.,1.]))
    glEnd()

def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

def main():
    if not glfw.init():
        return
    ## A
    window = glfw.create_window(480,480, '2018023390', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()