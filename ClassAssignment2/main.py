import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import random


is_orbit = False
is_ortho = False
is_pan = False
is_frame = False
orbit_info = [0.,0.,1.]
pan_info = [0.,0.]
zoom = 1
old =[0., 0., 0.]
u = np.array([0.,0.,0.])
v = np.array([0.,0.,0.])
w = np.array([0.,0.,0.])
##simgle_mesh mode
varr = np.zeros(1)

##hierachial_mode
is_hierachial = False

##wireframe / solid mode
is_solid = False

#extrapoint
is_forced_shading = False
global_path = ""
global_filename=""

def render():
    global is_solid, is_hierachial, is_frame, u, v, w, orbit_info, pan_info
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    if(is_solid):glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
    else:glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,100)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    camera = np.array([3*np.sin(orbit_info[0])*np.cos(orbit_info[1])+u[0]*pan_info[0]+v[0]*pan_info[1],3+3*np.sin(orbit_info[1])+u[1]*pan_info[0]+v[1]*pan_info[1],3*np.cos(orbit_info[0])*np.cos(orbit_info[1])+u[2]*pan_info[0] + v[2]*pan_info[1]])
    target = np.array([u[0]*pan_info[0] + v[0]*pan_info[1],u[1]*pan_info[0] + v[1]*pan_info[1],u[2]*pan_info[0] + v[2]*pan_info[1]])
    up = np.array([0,orbit_info[2],0])
    myLookAt(camera ,target ,up )

    if(is_frame):drawFrame()
    drawGrid()
    
    glEnable(GL_LIGHTING)   # try to uncomment: no lighting
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    glEnable(GL_NORMALIZE)  # try to uncomment: lighting will be incorrect if you scale the object
    # glEnable(GL_RESCALE_NORMAL)

    # light position
    glPushMatrix()
    lightPos1 = (.0,2.,2.,1.)
    lightPos2 = (.0,-2.,-2.,0.)    # try to change 4th element to 0. or 1.
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos1)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos2)
    glPopMatrix()

    # light intensity for each color channel
    lightColor1 = (1.,.8,.8,1.)
    lightColor2 = (.95,.54,.0,43.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor2)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor2)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)

    # material reflectance for each color channel

    if(is_hierachial) :
        global_path = ""
        global_filename = ""
        hierachial_model()
    else : 
        glPushMatrix()
        glColor3ub(0, 0, 255)
        drawObj()
        glPopMatrix()

    glDisable(GL_LIGHTING)

    
def hierachial_model():
    path = os.path.dirname(os.path.abspath(__file__))

    t =glfw.get_time()
    t = t
    trans = 0

    singing_term = random.randrange(0,30)
    parent = file_reader(path, "base_body_low.obj")
    child1 = file_reader(path, "right_foot_low.obj")
    child2 = file_reader(path, "left_foot.obj")
    child3 = file_reader(path, "head_low.obj")
    child4 = file_reader(path, "arm.obj")

    upperburi = file_reader(path, "upperburi.obj")
    lowerburi = file_reader(path, "lowerburi.obj")

    #몸체 Transformation
    glPushMatrix()
    glScalef(.1,.1,.1)
    glRotatef(t*0.5*(180/np.pi),0,1,0)

    #몸체 그리기
    glPushMatrix()    
    objectColor = (.70,.86,0.89,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    drawObj(parent)
    glPopMatrix()

    #자식 1 - 머리 Transformation
    glPushMatrix()
    glTranslate(0.1, 4, 0.5)
    # glScalef(.1,.1,.1)
    angle = 1- np.cos(t)
    # glRotate(-30, 1,0,0)
    if(angle > 1 ) : 
        glRotate(45,0,1,0)
    else:
        glRotate(-45,0,1,0)
    glRotate(-30, 1,0,0)
    glRotate(0.4 * np.degrees((1-np.cos(t))), 0,1,0)

    #자식 1 - 머리 그리기
    glPushMatrix()
    objectColor = (.36,.51,0.77,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    drawObj(child3)
    glPopMatrix()

    #자식 1 - 1 윗부리
    glPushMatrix()
    glTranslate(-0.55,-0.45,1.5)
    glRotate(singing_term, 1,0,0)
    

    #자식 1 - 1 윗부리 그리기
    glPushMatrix()
    objectColor = (.97,.83,0.47,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    drawObj(upperburi)
    glPopMatrix()
    glPopMatrix()

    #자식 1 - 2 아랫부리 움직임.
    glPushMatrix()
    glTranslate(-0.3,-0.55,1.75)
    glRotate(-singing_term, 1,0,0)

    #자식 1 - 2 아랫부리 그리기
    glPushMatrix()

    objectColor = (.97,.83,0.47,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    drawObj(lowerburi)
    glPopMatrix()
    glPopMatrix()

    glPopMatrix() # 머리 transformation의 Pop

    # 오른쪽발 움직임
    glPushMatrix()
    glTranslate(-1.3,-0.3,2.1)
    glRotatef(0.3*(1-np.cos(t*3))*(180/np.pi) - 45 ,0,0,1)

    # 오른쪽 발 그리기
    glPushMatrix()

    objectColor = (.97,.83,0.47,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    drawObj(child1)
    glPopMatrix()
    glPopMatrix()

    #왼쪽발 움직임
    glPushMatrix()
    glTranslate(1.6,-0.3,1.6)
    glRotatef(-30,0,1,0)
    glRotatef(0.3 * (1-np.cos(t*3))*(180/np.pi) - 15,1,0,0)

    glPushMatrix()

    objectColor = (.97,.83,0.47,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    drawObj(child2)
    glPopMatrix()
    glPopMatrix()

    # # 오른쪽팔
    glPushMatrix()
    
    glTranslate(-1,1,0.3)
    glRotatef(0.3 * (1-np.cos(t * 5))*(180/np.pi),1,0,0)

    glPushMatrix()
    
    objectColor = (.70,.86,0.89,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    drawObj(child4)
    glPopMatrix()
    glPopMatrix()

    glPopMatrix()


def file_reader(path, name):
    global varr
    tmp_obj = open(path + "/" + name).readlines()
    vlist , vnlist, flist, fnlist = [] ,[] ,[] ,[] 
    count = [0, 0, 0, 0] # [총 faces 수, vertex가 3개인 face의 수, vertex가 4개인 face의 수, vertex가 4개 이상인 face의 수]

    for line in tmp_obj:
        tmp_flist, tmp_fnlist = [], []
        if(line.startswith("v ")):
            line = line.split()[1:]
            line = list(map(float, line))
            vlist.append(line)
        elif(line.startswith("vn")):
            line = line.split()[1:]
            line = list(map(float, line))
            vnlist.append(line)
        elif(line.startswith("f")):
            line = line.split()[1:]
            count[0] += 1
            if (len(line) == 3) : count[1] += 1
            elif (len(line) == 4) : count[2] += 1
            elif (len(line) >= 5) : count[3] += 1
            for i in line:
                i = i.split("/")
                tmp_flist.append(int(i[0])-1)
                tmp_fnlist.append(int(i[2])-1)
            flist.append(tmp_flist)
            fnlist.append(tmp_fnlist)
        else:continue
    if name == global_filename : varr = make_varr(vlist, vnlist, flist, fnlist)
    return make_varr(vlist, vnlist, flist, fnlist)


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
    glColor3ub(50,50,50)
    for i in range(-10,11) :
        glVertex3fv(np.array([i*0.1,0,-1]))
        glVertex3fv(np.array([i*0.1, 0, 1]))
        glVertex3fv(np.array([-1,0,i*0.1]))
        glVertex3fv(np.array([1, 0, i*0.1]))
    glEnd()

def drop_callback(window, callback ):
    global varr, path , global_path, global_filename
    path = str(callback[0])
    filename = path.split("/")[-1]
    global_path = '/'.join(path.split("/")[:-1])
    global_filename = filename

    path = open(path, 'r').readlines()
    vlist , vnlist, flist, fnlist = [] ,[] ,[] ,[] 
    count = [0, 0, 0, 0] # [총 faces 수, vertex가 3개인 face의 수, vertex가 4개인 face의 수, vertex가 4개 이상인 face의 수]
    for line in path:
        tmp_flist, tmp_fnlist = [], []
        if(line.startswith("v ")):
            line = line.split()[1:]
            line = list(map(float, line))
            vlist.append(line)
        elif(line.startswith("vn")):
            line = line.split()[1:]
            line = list(map(float, line))
            vnlist.append(line)
        elif(line.startswith("f")):
            line = line.split()[1:]
            count[0] += 1
            if (len(line) == 3) : count[1] += 1
            elif (len(line) == 4) : count[2] += 1
            elif (len(line) >= 5) : count[3] += 1
            for i in line:
                i = i.split("/")
                tmp_flist.append(int(i[0])-1)
                tmp_fnlist.append(int(i[2])-1)
            flist.append(tmp_flist)
            fnlist.append(tmp_fnlist)
        else:continue

    print("1. Filename : ", filename)
    print("2. Total number of faces : ", count[0])
    print("3. Total number of 3 vertices : ", count[1])
    print("4. Total number of 4 vertices : ", count[2])
    print("5. Total number of more than 4 vertices : ", count[3], "\n")

    varr = make_varr(vlist, vnlist, flist, fnlist)

def make_varr(vlist, vnlist, flist, fnlist):
    global is_forced_shading
    varr = []
    new_flist=[]

    for i in range(0, len(flist)) :
        # print(flist[i])
        if(len(flist[i]) > 3):
            tmp_flist=[]
            tmp_fnlist=[]
            for vertex in range(1, len(flist[i])) :
                if vertex  < len(flist[i]) -1 : 
                    tmp_flist.append([flist[i][0], flist[i][vertex], flist[i][vertex + 1]])
                    tmp_fnlist.append([fnlist[i][0], fnlist[i][vertex], fnlist[i][vertex + 1]])
            for plane in range(len(tmp_flist)):
                for vertex in range(3):
                    new_flist.append(tmp_flist[plane][vertex])
                    varr.append(tuple(vnlist[tmp_fnlist[plane][vertex]]))
                    varr.append(tuple(vlist[tmp_flist[plane][vertex]]))
        else:
            for vertex in range(3) : 
                new_flist.append(flist[i][vertex])
                varr.append(tuple(vnlist[fnlist[i][vertex]]))
                varr.append(tuple(vlist[flist[i][vertex]]))

    if is_forced_shading :
        print("now_forced_shading")
        face_normal_list = []
        for vt in range(0,len(varr),6):
            v1 = np.array(varr[vt+1]) - np.array(varr[vt+3])
            v2 = np.array(varr[vt+1]) - np.array(varr[vt+5])
            face_normal_list.append(np.cross(v1 , v2))
        
        close_plane_dict={}
        for vt in range(0,len(vlist)):
            close_plane_dict[vt] = 0
            total = 0
            for fn in range(0,len(varr),6):
                test_list = [varr[fn+1] ,varr[fn+3] ,varr[fn+5]]
                if(tuple(vlist[vt]) in test_list):
                    close_plane_dict[vt] += face_normal_list[fn // 6]
                    total += 1
            close_plane_dict[vt] /= total

        for vt in range(0, len(new_flist)):
            varr[vt * 2] = close_plane_dict[new_flist[vt]]

    return np.array(varr, 'float32')


def drawObj(local_varr = 0):
    global varr
    if type(local_varr) == int : local_varr = varr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*local_varr.itemsize, local_varr)
    glVertexPointer(3, GL_FLOAT, 6*local_varr.itemsize, ctypes.c_void_p(local_varr.ctypes.data + 3*local_varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(local_varr.size/6))

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
    global is_ortho, is_frame, is_solid, is_hierachial, is_forced_shading, global_path, global_filename
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            if(is_ortho):is_ortho = False
            else: is_ortho = True
        if key==glfw.KEY_F:
            if(is_frame):is_frame = False
            else: is_frame = True
        if key==glfw.KEY_Z:
            if(is_solid):is_solid = False
            else: is_solid = True
        if key==glfw.KEY_H:
            if(is_hierachial):is_hierachial = False
            else: is_hierachial = True
        if key==glfw.KEY_S:
            if(is_forced_shading):is_forced_shading = False
            else: is_forced_shading = True
            if(global_path != "" and global_filename != ""):file_reader(global_path, global_filename)

def main():
    if not glfw.init():
        return

    window = glfw.create_window(700,700, 'Class_assignment2', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
  
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_key_callback(window,key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    
    glfw.set_drop_callback(window, drop_callback)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
        
    glfw.terminate()

if __name__ == "__main__":
    main()
