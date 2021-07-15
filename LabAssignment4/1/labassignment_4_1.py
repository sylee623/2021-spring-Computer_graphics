import glfw
import numpy as np
from OpenGL.GL import *

KEY = []

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255,0,0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0,255,0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    glColor3ub(255,255,255)
    #glMultMatrixf(M.T)
    if(len(KEY) > 0):
        for i in reversed(KEY) :
            if (i == 'Q') : glTranslatef(-0.1, 0., 0.)
            elif (i == 'E') : glTranslatef(0.1, 0., 0.)
            elif (i == 'A') : glRotatef(10, 0., 0., 1.)
            elif (i == 'D') : glRotatef(-10, 0., 0., 1.)
    drawTriangle()

def drawTriangle():
    glBegin(
    GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global KEY
    if action == glfw.PRESS:
        if key == glfw.KEY_Q : KEY.append('Q')
        elif key == glfw.KEY_E : KEY.append('E')
        elif key == glfw.KEY_A : KEY.append('A')
        elif key == glfw.KEY_D : KEY.append('D')
        elif key == glfw.KEY_1 : KEY = []
def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480, '2018023390', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
