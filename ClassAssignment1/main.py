import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


is_orbit = False
is_ortho = False
is_pan = False
is_frame = False
orbit_info = [0,0,1]
pan_info = [0,0]
zoom = 1
old =[0, 0, 0]
u = np.array([0,0,0])
v = np.array([0,0,0])
w = np.array([0,0,0])



def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    if(is_ortho):
        glLoadIdentity()
        ortho = 10 * zoom
        glOrtho(-ortho,ortho, -ortho,ortho, -ortho,ortho)
    else:
        glLoadIdentity()
        gluPerspective(45, 1, 1,100)
    camera = np.array([3*np.sin(orbit_info[0])*np.cos(orbit_info[1])+u[0]*pan_info[0]+v[0]*pan_info[1],3+3*np.sin(orbit_info[1])+u[1]*pan_info[0]+v[1]*pan_info[1],3*np.cos(orbit_info[0])*np.cos(orbit_info[1])+u[2]*pan_info[0] + v[2]*pan_info[1]])
    target = np.array([u[0]*pan_info[0] + v[0]*pan_info[1],u[1]*pan_info[0] + v[1]*pan_info[1],u[2]*pan_info[0] + v[2]*pan_info[1]])
    up = np.array([0,orbit_info[2],0])
    myLookAt(camera ,target ,up )
    if(is_frame):drawFrame()
    drawGrid()

def myLookAt(eye, at, up):
    global u, v, w
    w = (eye-at)/np.sqrt(np.dot(eye-at,eye-at))
    tmp_w = w
    if zoom != 0 :w = tmp_w*zoom
    u = np.cross(up,tmp_w)/np.sqrt(np.dot(np.cross(up,tmp_w),np.cross(up,tmp_w))) 
    v = np.cross(tmp_w,u)
    M = np.array([[u[0],u[1],u[2],-np.dot(u,eye)],
                 [v[0],v[1],v[2],-np.dot(v,eye)],
                 [w[0],w[1],w[2],-np.dot(w,eye)],
                 [0,0,0,1]])
    glMultMatrixf(M.T)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-10.,0.,0.])) 
    glVertex3fv(np.array([10.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.])) 
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,-10.])) 
    glVertex3fv(np.array([0.,0.,10.]))
    glEnd()

def drawGrid():
    glBegin(GL_LINES)
    glColor3ub(100,100,100)
    for i in range(-20,20) :
        glVertex3fv(np.array([i*0.5,0,-10]))
        glVertex3fv(np.array([i*0.5, 0, 10]))
        glVertex3fv(np.array([-10,0,i*0.5]))
        glVertex3fv(np.array([10, 0, i*0.5]))
    glEnd()

def button_callback(window, button, action, mod):
    global is_orbit, is_pan
    if button == glfw.MOUSE_BUTTON_RIGHT :
        if action==glfw.PRESS:is_pan = True         
        elif action == glfw.RELEASE : is_pan = False

    elif button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:is_orbit = True
        elif action == glfw.RELEASE :is_orbit = False

def cursor_pos_callback(window, xpos, ypos) :
        global pan_info,orbit_info, gCamHeight, old
        if (is_pan):
            pan_info[0] = pan_info[0] + (old[0] - xpos) * 1e-2
            pan_info[1] = pan_info[1] - (old[1] - ypos) * 1e-2
        if (is_orbit):
            orbit_info[0] = orbit_info[0] + ((old[0] - xpos)* 1e-2 )
            orbit_info[1] = orbit_info[1] - ((old[1] - ypos) * 1e-2 )
            if old[1] - ypos < 0 and np.sin(orbit_info[1]) < old[2] : orbit_info[2] = -1
            elif old[1] - ypos > 0 and np.sin(orbit_info[1])> old[2]:orbit_info[2] = -1
            else :orbit_info[2] = 1
        old = [xpos, ypos, np.sin(orbit_info[1])]

def scroll_callback(window, xoffset, yoffset) :
    global zoom
    zoom -= yoffset * 0.1

def key_callback(window, key, scancode, action, mods):
    global is_ortho, is_frame
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            if(is_ortho):is_ortho = False
            else: is_ortho = True
        if key==glfw.KEY_F:
            if(is_frame):is_frame = False
            else: is_frame = True

def main():
    if not glfw.init():
        return

    window = glfw.create_window(1280,1280, 'Class_assignment1', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_mouse_button_callback(window,button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
