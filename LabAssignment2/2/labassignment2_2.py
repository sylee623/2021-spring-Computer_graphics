import glfw
import numpy as np
from OpenGL.GL import *

TIME = 3

def render():
    glClear(GL_COLOR_BUFFER_BIT) 
    glLoadIdentity()
    glBegin(GL_LINE_LOOP) 
    angle_arr = np.arange(0,360,30)
    for i in angle_arr:
        degree = i * np.pi / 180
        glVertex2f(np.cos(degree),np.sin(degree))
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(np.cos(angle_arr[TIME]*np.pi/180),np.sin(angle_arr[TIME]*np.pi/180))
    glVertex2f(0,0)
    glEnd()

def hour_hand(window, key, scancode, action, mods):
    global TIME
    if action == glfw.PRESS:
        if key==glfw.KEY_1:TIME = 2
        elif key==glfw.KEY_2:TIME = 1
        elif key==glfw.KEY_3:TIME = 0
        elif key==glfw.KEY_4:TIME = 11
        elif key==glfw.KEY_5:TIME = 10
        elif key==glfw.KEY_6:TIME = 9
        elif key==glfw.KEY_7:TIME = 8
        elif key==glfw.KEY_8:TIME = 7
        elif key==glfw.KEY_9:TIME = 6
        elif key==glfw.KEY_0:TIME = 5
        elif key==glfw.KEY_Q:TIME = 4
        elif key==glfw.KEY_W:TIME = 3


def main():
    if not glfw.init():
        return
    window = glfw.create_window(480,480,"2018023390", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.set_key_callback(window, hour_hand)
    # Make the window's context current
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        # Poll events
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
