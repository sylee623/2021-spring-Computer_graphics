from logging import setLogRecordFactory
from math import tan
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import os
import random
import time

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

#animation
is_animation = False
is_box = False
is_obj = False

#bvh
filename = ''
n_frame = 0
# bvh_hierachy = []
bvh_motion = []
frame = []
node_list = []
max_scale = 0.

scale_low_y = 0.
scale_high_y = 0.

global_path = os.path.dirname(os.path.abspath(__file__))

class Node():
    def __init__(self, joint_name):
        self.joint_name = joint_name
        self.children = []
        self.parent = None
        self.rotation = None
        self.translation = None
        self.position = None
        self.offset = []
        self.ct = 0
    def concat_bone(self, child):
        child.parent = self
        self.children.append(child)
    

def render(frame_idx):
    global is_frame, u, v, w, orbit_info, pan_info, frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
    
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

    glEnable(GL_NORMALIZE)  # try to uncomment: lighting will be incorrect if you scale the object
    # glEnable(GL_RESCALE_NORMAL)

    # light position
    glPushMatrix()
    lightPos1 = (.0,2.,2.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos1)
    glPopMatrix()

    # light intensity for each color channel
    lightColor1 = (1.,.8,.8,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)


    objectColor = (.5,.8,.8 ,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    
    # if filename != "" : 
    #     if( is_animation ):
    #         draw_bvh(bvh_motion[frame_idx])
    #     else:draw_bvh('')

    
    glPushMatrix()
    glScalef(.5,.5,.5)
    if(len(node_list) > 1):
        frame = bvh_motion[frame_idx]
        draw_bvh([node_list[0]])
    glPopMatrix()
    
    glDisable(GL_LIGHTING)
    

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



def open_bvh(filename):
    global bvh_hierachy , bvh_motion, n_frame 
    file = open(filename,'r')
    file = file.read()
    file = file.split('MOTION')

    for i in file[1].split('\n') :
        if i.startswith('Frames') :
            i = i.split(':')
            n_frame = int(i[1])
        elif len(i) > 50:
            i = i.split()
            tmp = list(map(float, i))
            bvh_motion.append(tmp)
            
    
    draw_hierarchy(file[0].split('\n'))



def draw_hierarchy(bvh_hierachy):
    global node_list, n_frame , max_scale, scale_low_y, scale_high_y
    
    add_subroot = False
    ct, ct_old = 0 ,0
    joint_name_list = list()
    
    rotation_info = [ 'XROTATION', 'YROTATION' , 'ZROTATION' ]
    for line in bvh_hierachy:
        line = line.lstrip()
        line = line.upper()
        if(line.startswith('R')):
            joint_name = line.split()[-1]
            tmp_node = Node(joint_name)
            tmp_node.ct = ct
            joint_name_list.append(joint_name)
            node_list.append(tmp_node)
            
        elif line.startswith('J'):
            add_subroot = True
            joint_name = line.split()[-1]
            tmp_node = Node(joint_name)
            tmp_node.ct = ct
            joint_name_list.append(joint_name)
            node_list.append(tmp_node)

        elif(line == '{'):
            if add_subroot :
                if abs(ct_old - ct) > 1  : 
                    node_list[len(node_list)-ct -2].concat_bone(node_list[-1])
                else:node_list[-2].concat_bone(node_list[-1])
            ct_old = ct

        elif(line.startswith('O')):
            node_list[-1].position = list(map(float,line.split()[-3:]))
            if(scale_high_y< node_list[-1].position[1]): scale_high_y= node_list[-1].position[1]
            if(scale_low_y > node_list[-1].position[1]): scale_low_y= node_list[-1].position[1]
            

        elif(line.startswith('C')):
            line = line.split()
            node_list[-1].offset = line[2:]
            rotation_seq = []
            for i in line[-3:]:
                rotation_seq = ''.join(line[-3:]).split('ROTATION')
                
            node_list[-1].rotation = rotation_seq

        elif(line.startswith('E')):
            node_list.append(Node('End_pos'))
            tmp_node.ct = ct
            # node_list[-2].concat_bone(node_list[-1])

        elif(line.startswith('}')):
            ct = ct + 1
    

    print("file name :"  ,  filename.split('/')[-1])
    print("number of frames :" , n_frame)
    print("FPS :", (1./n_frame))
    print("number of joints :", len(joint_name_list))
    print("name of all joint names :", ', '.join(joint_name_list))

def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5) 
                             
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5) 
                             
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
                             
    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)
 
    glVertex3f(-0.5, 0.5, 0.5) 
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5) 
    glVertex3f(-0.5,-0.5, 0.5) 
                             
    glVertex3f( 0.5, 0.5,-0.5) 
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()

def draw_bvh(lists):
    global frame    
    # if(scale_high_y - scale_low_y > 10) : glScale(1. / (scale_high_y - scale_low_y), 10 / (scale_high_y - scale_low_y), 1. / (scale_high_y - scale_low_y))
    for i in range(len(lists)):
        glPushMatrix()
        
        # if(max_scale > 10):glScale(1. / max_scale, 1. / max_scale, 1. / max_scale)
        p = lists[i].position
        if(max_scale > 10 ) : glScalef(0.3, 0.3 ,0.3)
        if(is_box == False and is_obj == False):
            glBegin(GL_LINES)
            glVertex3f(0.,0.,0.)
            glVertex3f(p[0],p[1],p[2])
            glEnd()

        glTranslatef(p[0], p[1], p[2])

        if is_animation :
            if(len(lists[i].offset) == 6):
                glTranslatef(frame[0], frame[1], frame[2])
                frame = frame[3:]

            if(lists[i].rotation != None):
                for axis in range(0, len(lists[i].rotation)):
                    if(lists[i].rotation[axis].rstrip() == 'X'):
                        angle_x = frame[axis]
                        glRotatef(angle_x, 1, 0, 0)
                    elif(lists[i].rotation[axis].rstrip() == 'Y'):
                        angle_y = frame[axis]
                        glRotatef(angle_y, 0, 1, 0)     
                    elif(lists[i].rotation[axis].rstrip() == 'Z'):
                        angle_z = frame[axis]
                        glRotatef(angle_z, 0, 0, 1)
                frame = frame[3:]

        if(is_box and is_obj == False ):drawBox(lists[i])
        elif(is_obj):
            if not lists[i].joint_name.startswith( 'End') :drawObj(lists[i])
        draw_bvh(lists[i].children)

        glPopMatrix()

def drawBox(node):
    p = node.position
    x,y,z = p
    length = np.sqrt(x**2+y**2+z**2)

    if length == 0:return
    # y- rotation
    y_rot = [1, 0]
    if x == 0 and z == 0: 
        y_rot[0] = 1
        y_rot[1] = 0
    else:
        y_rot[1] = z/np.sqrt(x**2+z**2) 
        y_rot[0] = x/np.sqrt(x**2+z**2)
    R1 = np.identity(4)
    R1[:3,:3] = [[y_rot[0],0.,-y_rot[1]],
                 [0.,1.,0.],
                 [y_rot[1],0.,y_rot[0]]]
    glPushMatrix()    
    glMultMatrixf(R1.T)
    x_rot = [0, 0]
    x_rot[0] = y/length  
    x_rot[1] = np.sqrt(x**2+z**2)/length
    R2 = np.identity(4)
    R2[:3,:3] = [[x_rot[1],-x_rot[0],0.],
                 [x_rot[0],x_rot[1],0.],
                 [0.,0.,1.]]
    glMultMatrixf(R2.T)

    glScalef(length*.5,.04,.04)
    drawUnitCube()
    glPopMatrix()

def drawObj(node):
    varr = file_reader(global_path  , node.joint_name + '.obj')
    x,y,z = node.position
    length = np.sqrt(x**2+y**2+z**2)
    glPushMatrix()
    if('ARM' in node.joint_name or 'HAND' in node.joint_name) : 
        glScalef(length * 2,1,1)
        if('RIGHTFOREARM' in node.joint_name) : glTranslatef(-.1,0.,0.)
        elif('LEFTFOREARM' in node.joint_name) : glTranslatef(.1,0.,0.)
    elif('HEAD' in node.joint_name ) : glScalef(length * 2,length * 2,length * 2)
    elif('LEG' in node.joint_name or 'FOOT' in node.joint_name) :
        if('UPLEG' in node.joint_name) : 
            xc, yc, zc = node.children[0].position
            length = length + np.sqrt(xc**2+yc**2+zc**2)
        glScalef(1,length * 2,1)
    glRotatef(180,0.,1.,0.)
    drawvarr(varr)
    glPopMatrix()


def drawvarr(local_varr = 0):
    global varr
    if type(local_varr) == int : local_varr = varr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*local_varr.itemsize, local_varr)
    glVertexPointer(3, GL_FLOAT, 6*local_varr.itemsize, ctypes.c_void_p(local_varr.ctypes.data + 3*local_varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(local_varr.size/6))


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
    varr = make_varr(vlist, vnlist, flist, fnlist)
    return make_varr(vlist, vnlist, flist, fnlist)

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
    return np.array(varr, 'float32')

# def loadObj(path):
    

def button_callback(window, button, action, mod):
    global is_orbit, is_pan
    if button == glfw.MOUSE_BUTTON_RIGHT :
        if action==glfw.PRESS:is_pan = True         
        elif action == glfw.RELEASE : is_pan = False

    elif button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:is_orbit = True
        elif action == glfw.RELEASE :is_orbit = False

def cursor_pos_callback(window, xpos, ypos) :
        global pan_info,orbit_info , old
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
    global is_ortho, is_frame, is_animation, is_box, is_obj
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            if(is_ortho):is_ortho = False
            else: is_ortho = True
        if key==glfw.KEY_F:
            if(is_frame):is_frame = False
            else: is_frame = True
        if key==glfw.KEY_SPACE:
            if(is_animation):is_animation = False
            else: is_animation = True
        if key==glfw.KEY_B:
            if(is_box):is_box = False
            else: is_box = True
            if(is_obj):is_obj = False
        if key==glfw.KEY_O:
            if(is_obj):is_obj = False
            else: is_obj = True
            if(is_box):is_box = False
            
def drop_callback(window, callback ):
    global filename, bvh_motion, n_frame, frame, node_list
    filename = callback[0]
    print(callback[0])
    bvh_motion = []
    n_frame = 0
    frame = []
    node_list = []
    if(filename.split('.')[-1] == 'bvh'):open_bvh(filename)


def main():
    if not glfw.init():
        return
    window = glfw.create_window(700,700, 'Class_assignment3', None,None)
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

    

    # if n_frame > 0 : limit = 1.0 / n_frame
    last_update_time = 0.
    last_frame_time = 0.
    frame = 0
    while not glfw.window_should_close(window):
        
        if(is_animation and n_frame > 0):
            now = glfw.get_time()
            delta_time = now - last_update_time
            glfw.poll_events()
            if frame >= n_frame : 
                frame = 0
            render(frame)
            frame += 1
            if (now -last_frame_time)>= 1.0 / n_frame:
                glfw.swap_buffers(window)
                last_frame_time = now
        
        else:
            glfw.poll_events()
            render(-1)
            glfw.swap_buffers(window)
        
    glfw.terminate()

if __name__ == "__main__":
    main()
