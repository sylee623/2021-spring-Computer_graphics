import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import time

gCamAng = 0.
gCamHeight = 1.

#################################################
def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def lerp(v1, v2, t):
    return (1-t)*v1 + t*v2

# euler[0]: zang
# euler[1]: yang
# euler[2]: xang
def ZYXEulerToRotMat(euler):
    zang, yang, xang = euler
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    return Rx @ Ry @ Rz

#################################################
def exp(rv):
    vhat = l2norm(np.sqrt(np.dot(rv[0],rv[0]) + np.dot(rv[1],rv[1]) + np.dot(rv[2], rv[2])))
    v = normalized(rv)
    return np.array([[np.cos(vhat)+((v[0]*v[0])*(1-np.cos(vhat))), ((v[0]*v[1])*(1-np.cos(vhat)))-(v[2]*np.sin(vhat)), (v[0]*v[2]*(1-np.cos(vhat))) + v[1]*np.sin(vhat)],
                    [(v[1]*v[0]*(1-np.cos(vhat)))+(v[2]*np.sin(vhat)), np.cos(vhat)+((v[1]*v[1])*(1-np.cos(vhat))), ((v[1]*v[2])*(1-np.cos(vhat)))-(v[0]*np.sin(vhat))],
                    [(v[2]*v[0]*(1-np.cos(vhat)))-(v[1]*np.sin(vhat)), (v[2]*v[1]*(1-np.cos(vhat)))+v[0]*np.sin(vhat),np.cos(vhat)+(v[2]*v[2])*(1-np.cos(vhat))]])

def log(R):
    theta = np.arccos((R[0][0]+R[1][1]+R[2][2]-1)/2)
    v1 = (R[2][1] - R[1][2]) / (2*np.sin(theta))
    v2 = (R[0][2] - R[2][0]) / (2*np.sin(theta))
    v3 = (R[1][0] - R[0][1]) / (2*np.sin(theta))
    return (theta * np.array([v1 ,v2 ,v3])) ## 60페이지에 있는 구현도 시도해봤는데 잘 안되어서 59페이지에 있는 것을 그대로 쳤습니다.

def slerp(R1, R2, t):
    return R1 @ exp(t * log((R1.T) @ R2))

def interpolateRotVec(rv1, rv2, t):
    return exp(lerp(rv1,rv2,t))

def interpolateZYXEuler(euler1, euler2, t):
    return exp(lerp(euler1, euler2, t))

def interpolateRotMat(R1, R2, t):
    return lerp(R1, R2, t)

def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()

def render(t):
    global gCamAng, gCamHeight

    frame = { 0 : [[20, 30 ,30],[15, 30 ,25]] ,20 : [[45,60,40],[25,40,40]], 40 : [[60,70,50],[40,60,50]], 60 : [[80,85,70],[55,80,65]]}
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    objectColor = (1.,1.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    for f in frame.keys():
        R1 = np.identity(4)
        euler1 = np.array([frame[f][0][0], frame[f][0][1], frame[f][0][2]])
        if(f < 60) : euler1_1 = np.array([frame[f + 20][0][0], frame[f + 20][0][1], frame[f + 20][0][2]])    # in ZYX Euler angles
        R1_1[:3,:3] = ZYXEulerToRotMat(euler1)
        J1 = R1
        
        glPushMatrix()
        glMultMatrixf(J1.T)
        glPushMatrix()
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()

        R2 = np.identity(4)
        euler2 = np.array([frame[f][1][1], frame[f][1][1], frame[f][1][2]])
        R2[:3,:3] = ZYXEulerToRotMat(euler2)
        T1 = np.identity(4)
        T1[0][3] = 1.
        

        J2 = R1 @ T1 @ R2

        glPushMatrix()
        glMultMatrixf(J2.T)
        glPushMatrix()
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()

    for f in frame.keys():
        glPushMatrix()
        if f == 0 : objectColor = (1.,0.,0.,1.)
        elif f == 20 :objectColor = (1.,1.,0.,1.)
        elif f == 40 :objectColor = (0.,1.,0.,1.)
        elif f == 60 :objectColor = (0.,0.,1.,1.)
        specularObjectColor = (1.,1.,1.,1.)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
        
        R1 = np.identity(4)
        euler1 = np.array([frame[f][0][0], frame[f][0][1], frame[f][0][2]])   # in ZYX Euler angles
        R1[:3,:3] = ZYXEulerToRotMat(euler1)
        J1 = R1
        
        glPushMatrix()
        glMultMatrixf(J1.T)
        glPushMatrix()
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()

        R2 = np.identity(4)
        euler2 = np.array([frame[f][1][1], frame[f][1][1], frame[f][1][2]])
        R2[:3,:3] = ZYXEulerToRotMat(euler2)
        
        T1 = np.identity(4)
        T1[0][3] = 1.

        J2 = R1 @ T1 @ R2

        glPushMatrix()
        glMultMatrixf(J2.T)
        glPushMatrix()
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()

        glPopMatrix()

    glDisable(GL_LIGHTING)
    # 20(R1: X 45 Y 60 Z 40) (R2: X 25 Y 40 Z 40)
    # 40(R1: X 60 Y 70 Z 50) (R2: X 40 Y 60 Z 50)
    # 60(R1: X 80 Y 85Z 70) (R2: X 55 Y 80 Z 65)

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2018023390', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

