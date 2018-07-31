# Class definitions for the advanced feedback

# ### Imports ### #
from math import pi, sin, cos, sqrt

from panda3d.core import *
from direct.task import Task

import random
import string
import sys
import yaml
#import numpy

# ### Begin ### #

# ### Logic controllers ### #

class Logic(object):
    ''' Superclass for the logic that controls exos and bases. '''
    
    def __init__(self,exo_model,armrest_model,dataController):
        self.exo = exo_model
        self.armrest = armrest_model
        
        self.dc = dataController
        
        self.modelTransparencySet = False
        
    def setColorBaseTask(self,color):
        ''' This task sets to color (lighting) of the base model. '''
        
        material = self.exo.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.exo.setMaterial(material)
        
        return Task.done
        
    def setColorArmRestTask(self,color):
        ''' This task sets to color (lighting) of the base model. '''
        material = self.armrest.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.armrest.setMaterial(material)
        
        return Task.done
    
    def toggleTransparencyTask(self,task):
        ''' This task toggles the transparency of the exo model. '''
        
        self.modelTransparencySet = not self.modelTransparencySet
        
        if self.modelTransparencySet:
            self.exo.setColorScale((1,1,1,0.65))
            self.exo.setTransparency(TransparencyAttrib.MDual)
            tmpMat = self.exo.getMaterial()
            tmpMat.setDiffuse((0.25,0.25,0.25,1))
            self.exo.setMaterial(tmpMat)
        else:
            self.exo.setColorScaleOff()
            self.exo.setTransparency(TransparencyAttrib.MNone)        
            tmpMat = self.exo.getMaterial()
            tmpMat.setDiffuse((0.25,0.25,0.25,.25))
            self.exo.setMaterial(tmpMat)
        
        return Task.done

class ExoLogic(Logic):
    ''' Logic for the movement of the Exo. Inherits from Logic. '''
    
    def __init__(self,exo_model,armrest_model,exo_prono,findex_model,fgroup_model,fthumb_model,dataController):
    
        super(ExoLogic, self).__init__(exo_model,armrest_model,dataController)
        
        self.prono = exo_prono
        self.findex = findex_model
        self.fgroup = fgroup_model
        self.fthumb = fthumb_model
            
    def getDataTask(self,task):
        ''' This is the task that handles the movement of the exo model. '''
        
        # Retrieve the data from the controller
        exo_state = (self.exo.getX(),self.exo.getY(),self.exo.getH(),self.prono.getR(),self.findex.getH(),self.fgroup.getH(),self.fthumb.getH())
        data = self.dc.get_data(exo_state)
        
        # Set parameters of the base
        self.exo.setX(data[0]['x'])
        self.exo.setY(data[0]['y'])
        self.exo.setH(data[0]['heading'])
        
        # Set parameters of the arm module
        self.prono.setR(data[1]['roll'])
        self.findex.setH(data[2]['heading'])
        self.fgroup.setH(data[3]['heading'])
        self.fthumb.setH(data[4]['heading'])
        
        return Task.cont
        
    def setColorPronoTask(self,color):
        ''' This task sets the color (lighting) of the pronation module. '''
        
        material = self.prono.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.prono.setMaterial(material)
        
        return Task.done
    
    def setColorIndexTask(self,color):
        ''' This task sets the color (lighting) of the index finger. '''
        
        material = self.findex.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.findex.setMaterial(material)
        
        return Task.done

    def setColorFingerGroupTask(self,color):
        ''' This task sets the color (lighting) of the finger group. '''
        
        material = self.fgroup.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.fgroup.setMaterial(material)
        
        return Task.done

    def setColorThumbTask(self,color):
        ''' This task sets the color (lighting) of the thumb. '''
        
        material = self.fthumb.getMaterial()
        material.setAmbient((color[0],color[1],color[2],1))
        self.fthumb.setMaterial(material)
        
        return Task.done
    
class BaseLogic(Logic):
    ''' Logic for the movement of the Base '''
    
    def __init__(self,exo_model,armrest_model,dataController):
        super(BaseLogic, self).__init__(exo_model,armrest_model,dataController)
        
    def getDataTask(self,task):
        ''' This is the task the handles the movement of the exo model. '''
        
        # Retrieve the data from the controller
        exo_state = (self.exo.getX(),self.exo.getY(),self.exo.getH())
        data = self.dc.get_data(exo_state)
        
        # Set parameters of the base
        self.exo.setX(data['x'])
        self.exo.setY(data['y'])
        self.exo.setH(data['heading'])
        
        return Task.cont
        
class MatLogic():
    ''' Logic for the mat '''
    
    def __init__(self,model,initial_side):
        self.mat = model
        self.side = initial_side
        
class CameraLogic():
    ''' Logic for the camera. '''
    
    def __init__(self,pl):
        self.pl = pl
    
    def rotate(self,angle):
        ''' Rotate the camera by ANGLE degress while facing the center of the mat. '''
    
        angle_rad = (angle * pi)/180
    
        R = [[cos(angle_rad),-sin(angle_rad)],[sin(angle_rad),cos(angle_rad)]]
    
        dp = self.pl.dotProduct(R,[0,-13-4.65])
        
        dp[0] += 4.4
        dp[1] += 4.65
        dp.append(10)
        dp.append(angle)
        dp.append(-30)
        dp.append(0)
        
        taskMgr.add(self.pl.setCameraOrientationPositionTask,"setCameraOrientationPositionTask",extraArgs = [dp])

# ### Data controllers ### #        

class ExoDataControllerKeyboard():
    ''' A DataController that returns the robot position according to the keyboard input '''
    
    def __init__(self,id,handedness):
        self.id = id
        if handedness == 'right':
            self.handedness_switch = 1
        else:
            self.handedness_switch = -1
        
        self.robot = {}
        self.prono = {}
        self.findex = {}
        self.fgroup = {}
        self.fthumb = {}
        
        self.robot['x'] = 0
        self.robot['y'] = 0
        self.robot['heading'] = 0
        
        self.prono['roll'] = 0
        self.findex['heading'] = 0
        self.fgroup['heading'] = -10
        self.fthumb['heading'] = 10
            
    def get_data(self,exo_state):
        ''' Function that returns the position data to the exo logic object '''
        self.move(exo_state)
        
        return (self.robot,self.prono,self.findex,self.fgroup,self.fthumb)
    
    def move(self,exo_state):
        ''' Polls the keys and executes the functions that compute the target positions '''
        # Initialise polling
        is_down = base.mouseWatcherNode.is_button_down
        # Define keys
        b_arrow_up = KeyboardButton.up()
        b_arrow_down = KeyboardButton.down()
        b_arrow_left = KeyboardButton.left()
        b_arrow_right = KeyboardButton.right()
        b_q = KeyboardButton.asciiKey('q')
        b_a = KeyboardButton.asciiKey('a')
        b_w = KeyboardButton.asciiKey('w')
        b_s = KeyboardButton.asciiKey('s')
        b_e = KeyboardButton.asciiKey('e')
        b_d = KeyboardButton.asciiKey('d')
        b_r = KeyboardButton.asciiKey('r')
        b_f = KeyboardButton.asciiKey('f')
        
        # Polling logic and execution of movements
        
        # Button "UP" moves robot forward
        if is_down(b_arrow_up):
            movement = self.compute_moveExo('forward',exo_state)
            self.move_x(movement[0])
            self.move_y(movement[1])
        
        # Button "DOWN" moves robot forward
        if is_down(b_arrow_down):
            movement = self.compute_moveExo('backward',exo_state)
            self.move_x(movement[0])
            self.move_y(movement[1])
        
        # Button "LEFT" turns robot to the left
        if is_down(b_arrow_left):
            movement = self.compute_turnExo('left',exo_state)
            self.turn(movement)
        
        # Button "RIGHT" moves robot to the right
        if is_down(b_arrow_right):
            movement = self.compute_turnExo('right',exo_state)
            self.turn(movement)
            
        # Button "Q" opens the index finger
        if is_down(b_q):
            movement = self.compute_findex('open',exo_state)
            self.turn_findex(movement)
        
        # Button "A" closes the index finger        
        if is_down(b_a):
            movement = self.compute_findex('close',exo_state)
            self.turn_findex(movement)
        
        # Button "W" opens the finger group        
        if is_down(b_w):
            movement = self.compute_fgroup('open',exo_state)
            self.turn_fgroup(movement)
        
        # Button "S" closes the finger group
        if is_down(b_s):
            movement = self.compute_fgroup('close',exo_state)
            self.turn_fgroup(movement)
            
        # Button "E" opens the thumb
        if is_down(b_e):
            movement = self.compute_fthumb('open',exo_state)
            self.turn_fthumb(movement)
            
        # Button "D" closes the thumb
        if is_down(b_d):
            movement = self.compute_fthumb('close',exo_state)
            self.turn_fthumb(movement)
            
        # Button "R" pronates the hand
        if is_down(b_r):
            movement = self.compute_prono('pronate',exo_state)
            self.turn_prono(movement)
            
        # Button "D" supinates the hand
        if is_down(b_f):
            movement = self.compute_prono('supinate',exo_state)
            self.turn_prono(movement)
        
    
    # Functions computing and storing the movement
    def move_x(self,x):
        self.robot['x'] = x
    
    def move_y(self,y):
        self.robot['y'] = y
        
    def turn(self,h):
        self.robot['heading'] = h
        
    def turn_findex(self,angle):
        self.findex['heading'] = angle
        
    def turn_fgroup(self,angle):
        self.fgroup['heading'] = angle
        
    def turn_fthumb(self,angle):
        self.fthumb['heading'] = angle
        
    def turn_prono(self,angle):
        self.prono['roll'] = angle
    
    def compute_turnExo(self,heading,exo_state):
        ''' Turn the exo toward a target position '''
        headingOld = exo_state[2]
        if heading == 'right':
            return (headingOld - 2)%360
        elif heading == 'left':
            return (headingOld + 2)%360
        
    def compute_moveExo(self,direction,exo_state):
        ''' Compute the target coordinates of a 2d movement (forward or backward) '''
        # Get current heading in degrees
        heading = exo_state[2]
        if heading < 0:
            heading = heading + 360
        
        # Determine correct direction to turn the robot
        distx_fact = 1
        disty_fact = 1
        
        beta = 0.0
        
        if heading > 0 and heading <= 90:
            beta = heading
            distx_fact = 1
            disty_fact = -1
        elif heading > 90 and heading <= 180:
            beta = 180-heading
            distx_fact = 1
            disty_fact = 1
        elif heading > 180 and heading <= 270:
            beta = heading-180
            distx_fact = -1
            disty_fact = 1
        elif heading > 270 and heading <= 360:
            beta = 360-heading
            distx_fact = -1
            disty_fact = -1
        elif heading == 0.0:
            beta = 0.0
            distx_fact = -1
            disty_fact = -1

        # Compute distance on x and y axis
        dist = 0.1
        disty = cos((beta*pi)/180) * dist
        distx = sqrt(pow(dist,2)-pow(disty,2))
            
        distx *= distx_fact
        disty *= disty_fact
            
        # Set new position
        posOldX = exo_state[0]
        posOldY = exo_state[1]
        
        if direction == 'forward':
            return (posOldX-distx,posOldY-disty)
        elif direction == 'backward':
            return (posOldX+distx,posOldY+disty)
            
    def compute_findex(self,dir,exo_state):
        ''' Turn the index fingers '''
        if self.handedness_switch == 1:
            if dir == 'open':
                return (exo_state[4] - 2)%360
            else:
                return (exo_state[4] + 2)%360
        else:
            if dir == 'open':
                return (exo_state[4] + 2)%360
            else:
                return (exo_state[4] - 2)%360
            
    def compute_fgroup(self,dir,exo_state):
        ''' Turn the finger group '''
        if self.handedness_switch == 1:
            if dir == 'open':
                return (exo_state[5] - 2)%360
            else:
                return (exo_state[5] + 2)%360
        else:
            if dir == 'open':
                return (exo_state[5] + 2)%360
            else:
                return (exo_state[5] - 2)%360
            
    def compute_fthumb(self,dir,exo_state):
        ''' Turn the thumb '''
        if self.handedness_switch == 1:
            if dir == 'open':
                return (exo_state[6] + 2)%360
            else:
                return (exo_state[6] - 2)%360
        else:
            if dir == 'open':
                return (exo_state[6] - 2)%360
            else:
                return (exo_state[6] + 2)%360
            
    def compute_prono(self,dir,exo_state):
        ''' Pronate or supinate '''
        if dir == 'pronate':
            return (exo_state[3] + 2)%360
        else:
            return (exo_state[3] - 2)%360

class ExoDataControllerStatic():
<<<<<<< HEAD
	''' A DataController that returns the static position value with which it was initialised. '''
	
	def __init__(self,id,calibration,handedness,exo_x,exo_y,exo_h,prono_r,findex_h,fgroup_h,fthumb_h):
		
                self.id = id
                self.calibration = calibration
                self.handedness = handedness
		
                self.robot = {}
		self.prono = {}
		self.findex = {}
		self.fgroup = {}
		self.fthumb = {}
=======
    ''' A DataController that returns the static position value with which it was initialised. '''
    
    def __init__(self,id,calibration,handedness,exo_x,exo_y,exo_h,prono_r,findex_h,fgroup_h,fthumb_h):
        
        self.id = id
                self.calibration = calibration
                self.handedness = handedness
        
        self.robot = {}
        self.prono = {}
        self.findex = {}
        self.fgroup = {}
        self.fthumb = {}
>>>>>>> 560b9f95ece7603a49370bbc3d102101dc66135e

                # Set multiplication factor to mirror rotation of the wrist module
                mf = 1
                if self.handedness.upper() == "LEFT":
                    mf = -1

        self.robot['x'] = exo_x + self.calibration['x']
        self.robot['y'] = exo_y + self.calibration['y']
        self.robot['heading'] = exo_h + self.calibration['angle_base']
        
        self.prono['roll'] = mf * (prono_r + self.calibration['angle_suppro'])
        self.findex['heading'] = findex_h + self.calibration['angle_index']
        self.fgroup['heading'] = fgroup_h + self.calibration['angle_fingergroup']
        self.fthumb['heading'] = fthumb_h + self.calibration['angle_thumb']
            
    def get_data(self,exo_state):
        ''' Function that returns the position data to the exo logic object '''
        
        return (self.robot,self.prono,self.findex,self.fgroup,self.fthumb)
        
# class DataControllerPlayback():
# Playback predefined trajectory at the correct speed
#FIXME This is not necessary! Instead a DataControllerRealTime should be created and the client should read a file and send it via TCP

class ExoDataControllerRealTime():
    ''' A DataController that holds the kinematics data which it has received through TCP. '''
    
    def __init__(self, id, calibration, handedness):
    
        self.id = id
        self.calibration = calibration
        self.handedness = handedness
    
        # Setup exo model
        self.robot = {}
        self.prono = {}
        self.findex = {}
        self.fgroup = {}
        self.fthumb = {}
        
    def set_data(self,exo_state):
        ''' Function that sets the parameters of the degrees of freedom of the robot relative to the values specified in the calibration profile. '''
                # Set multiplication factor to mirror rotation of the wrist module
                mf = 1
                if self.handedness.upper() == "LEFT":
                    mf = -1

        self.robot['x'] = exo_state[0] + self.calibration['x']
        self.robot['y'] = exo_state[1] + self.calibration['y']
        self.robot['heading'] = exo_state[2] + self.calibration['angle_base']
        
        self.prono['roll'] = mf * (exo_state[3] + self.calibration['angle_suppro'])
        self.findex['heading'] = exo_state[4] + self.calibration['angle_index']
        self.fgroup['heading'] = exo_state[5] + self.calibration['angle_fingergroup']
        self.fthumb['heading'] = exo_state[6] + self.calibration['angle_thumb']
        
    def get_data(self,exo_state):
        ''' Function that returns the position data to the exo logic object '''
        
        return (self.robot,self.prono,self.findex,self.fgroup,self.fthumb)
        
        def setconfig(self,calibration):
            ''' Sets the given cfgprofile as calibration profile.'''
            self.calibration = calibration
        
class BaseDataControllerKeyboard():
    ''' A DataController that is used to control the kinematics of an exo that has only a base and no arm position according to the keyboard input. '''
    
    def __init__(self,id):
        self.id = id
        
        self.robot = {}
        
        self.robot['x'] = 0
        self.robot['y'] = 0
        self.robot['heading'] = 0
                
    def get_data(self,exo_state):
        ''' Function that returns the position data to the exo logic object '''
        self.move(exo_state)
        
        return (self.robot)
    
    def move(self,exo_state):
        ''' Polls the keys and executes the functions that compute the target positions '''
        # Initialise polling
        is_down = base.mouseWatcherNode.is_button_down
        # Define keys
        b_arrow_up = KeyboardButton.up()
        b_arrow_down = KeyboardButton.down()
        b_arrow_left = KeyboardButton.left()
        b_arrow_right = KeyboardButton.right()
        
        # Polling logic and execution of movements
        
        # Button "UP" moves robot forward
        if is_down(b_arrow_up):
            movement = self.compute_moveExo('forward',exo_state)
            self.move_x(movement[0])
            self.move_y(movement[1])
        
        # Button "DOWN" moves robot forward
        if is_down(b_arrow_down):
            movement = self.compute_moveExo('backward',exo_state)
            self.move_x(movement[0])
            self.move_y(movement[1])
        
        # Button "LEFT" turns robot to the left
        if is_down(b_arrow_left):
            movement = self.compute_turnExo('left',exo_state)
            self.turn(movement)
        
        # Button "RIGHT" moves robot to the right
        if is_down(b_arrow_right):
            movement = self.compute_turnExo('right',exo_state)
            self.turn(movement)
            
    # Functions computing and storing the movement
    def move_x(self,x):
        self.robot['x'] = x
    
    def move_y(self,y):
        self.robot['y'] = y
        
    def turn(self,h):
        self.robot['heading'] = h
            
    def compute_turnExo(self,heading,exo_state):
        ''' Turn the exo toward a target position '''
        headingOld = exo_state[2]
        if heading == 'right':
            return (headingOld - 2)%360
        elif heading == 'left':
            return (headingOld + 2)%360
        
    def compute_moveExo(self,direction,exo_state):
        ''' Compute the target coordinates of a 2d movement (forward or backward) '''
        # Get current heading in degrees
        heading = exo_state[2]
        if heading < 0:
            heading = heading + 360
        
        # Determine correct direction to turn the robot
        distx_fact = 1
        disty_fact = 1
        
        beta = 0.0
        
        if heading > 0 and heading <= 90:
            beta = heading
            distx_fact = 1
            disty_fact = -1
        elif heading > 90 and heading <= 180:
            beta = 180-heading
            distx_fact = 1
            disty_fact = 1
        elif heading > 180 and heading <= 270:
            beta = heading-180
            distx_fact = -1
            disty_fact = 1
        elif heading > 270 and heading <= 360:
            beta = 360-heading
            distx_fact = -1
            disty_fact = -1
        elif heading == 0.0:
            beta = 0.0
            distx_fact = -1
            disty_fact = -1

        # Compute distance on x and y axis
        dist = 0.1
        disty = cos((beta*pi)/180) * dist
        distx = sqrt(pow(dist,2)-pow(disty,2))
            
        distx *= distx_fact
        disty *= disty_fact
            
        # Set new position
        posOldX = exo_state[0]
        posOldY = exo_state[1]
        
        if direction == 'forward':
            return (posOldX-distx,posOldY-disty)
        elif direction == 'backward':
            return (posOldX+distx,posOldY+disty)
        
class BaseDataControllerStatic():
    ''' A DataController that controls an exo that only consists of a base. It is initialised with static kinematics. '''
    
    def __init__(self,id,calibration,exo_x,exo_y,exo_h):
        
        self.id = id
                self.calibration = calibration
        
        self.robot = {}
        self.prono = {}
                
        self.robot['x'] = exo_x + self.calibration['x']
        self.robot['y'] = exo_y + self.calibration['y']
        self.robot['heading'] = exo_h + self.calibration['angle_base']
                
    def get_data(self,exo_state):
        ''' Function that returns the kinematics data to the base logic object '''
        
        return (self.robot)
        
class BaseDataControllerRealTime():
    ''' A DataController that is used to control an exo that has only a base and no arm. It receives the kinematics data through TCP. '''
    
        def __init__(self, id, calibration):
    
        self.id = id
                self.calibration = calibration
    
        # Setup exo model
        self.robot = {}
        self.prono = {}
                    
    def set_data(self,exo_state):
        ''' Function that sets the parameters of the degrees of freedom of the robot relative to the values specified in the calibration profile. '''
        
        self.robot['x'] = exo_state[0] + self.calibration['x'] 
        self.robot['y'] = exo_state[1] + self.calibration['y'] 
        self.robot['heading'] = exo_state[2] + self.calibration['angle_base'] 
        
    def get_data(self,exo_state):
        ''' Function that returns the position data to the exo logic object '''
        
        return (self.robot)
        
        def setconfig(self,calibration):
            ''' Sets the given cfgprofile as calibration profile.'''
            self.calibration = calibration
        
        

# ### Program logic ### #
class ProgramLogic():
    ''' ProgramLogic that controls creating and removing exos and their corresponding data controllers '''
    
    def __init__(self,render):
        # Dict that contains all exos (Using a dict to be able to use hashmap-like random ids. Better for adding and removing exos.)
        self.exos = {}
        # This list contains all the ids of the exos in the order they were added to the program
        self.exo_ids_in_order = []
        # This is the mat of the scene
        self.mat = []
        # This is referring to the root of the rendering tree
        self.rootNode = render
                # Representation of a configuration profile (calibration file)
                tmp_profile = self.loadconfig('default')

                if not(tmp_profile):
                    raise IOError('Default profile (default.yml) not found. Exiting.')
                    sys.exit
                else:
                    self.cfgprofile = tmp_profile
        
        # Setup network protocol for the command interface
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cReader.setRawMode(True)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        
        # Network protocol configuration for the command interface
        self.activeConnections = []
        self.port_address=9900
        self.backlog = 2
        self.tcpSocket = self.cManager.openTCPServerRendezvous(self.port_address,self.backlog)
        
        # Startup network protocol for the command interface
        self.cListener.addConnection(self.tcpSocket)
        
        print('MESSAGE: Ready to accept connections.')
            
    def tskListenerPolling(self,task):
        ''' The task the polls the TCP port for new connections. Runs indefinitely. '''
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
     
            if self.cListener.getNewConnection(rendezvous,netAddress,newConnection):
              newConnection = newConnection.p()
              self.activeConnections.append(newConnection) # Remember connection
              self.cReader.addConnection(newConnection)     # Begin reading connection
              print('MESSAGE: Client connected.')
          
        return Task.cont
        
    def tskReaderPolling(self,task):
        ''' The task the continuously reads new data. '''
        if self.cReader.dataAvailable():
            datagram=NetDatagram()
            if self.cReader.getData(datagram):
                print("MESSAGE: Data received.")
                # Call function that parses the data received
                self.parse_commands(datagram)
        
        return Task.cont
        
    def tskTerminateConnections(self,task):
        ''' The task that terminates all client connections. '''
        connections_exist = False
        for client in self.activeConnections:
            self.cReader.removeConnection(client)
            connections_exist = True
            
        if connections_exist:
            self.activeConnections = []
            self.cManager.closeConnection(self.tcpSocket)
        
        return Task.done
            
    def parse_commands(self,datagram):
        ''' Function that parses a series of commands that are received through TCP. Only writes back to TCP in two cases:
        1. If an exo is added the id is written back.
        2. If an exo has been removed successfully.
        
        The command series is first split into single commands. These commands are then parsed and executed.'''
        # Extract message from the data
        commands = datagram.getMessage()
        connection = datagram.getConnection()
        
        commands_split = commands.split("::")
        
        for command in commands_split:
        
            if command != '':
        
                print("MESSAGE: Command '"+command+"' received.")

                # Process command
                comm_parts = command.split(" ")
                
                # Check which command is being send
                try:
                    # "ADDEXO" command
                    if comm_parts[0] == 'ADDEXO':
                        exotype = comm_parts[1]
                        # Check which type of exo should be added
                        if exotype == 'EXOSTATIC':
                            if len(comm_parts) < 4:
                                raise TypeError('Not enough command parameters supplied.')
                            else:
                                exoparams = comm_parts[3].split(",")
                                if len(exoparams) != 7:
                                    raise TypeError('Wrong number of kinematics parameters supplied.')
                                else:
                                    # Check handedness
                                    handedness = comm_parts[2]
                                    print(handedness)
                                    if not(handedness == 'RIGHT' or handedness == 'LEFT'):
                                        raise ValueError('Handedness '+handedness+' not recognised. Please use either "left" or "right".')

                                    # Convert input strings to floats
                                    try:
                                        exoparams_num = [ float(x) for x in exoparams ]
                                        # Divide x and y paramters by 10
                                        exoparams_num[0] /= 10
                                        exoparams_num[1] /= 10
                                    except TypeError:
                                        raise
                                    
                                    print('MESSAGE: Adding exo of type ' + exotype + '(' + handedness + ').')
                                    
                                    # Add exo
                                    taskMgr.add(self.addExoTask, "addExoTask",extraArgs = [("static",handedness.lower()),exoparams_num])
                                    # Send ID of the last added exo back to the client
                                    taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                                    
                        elif exotype == 'EXOREALTIME':
                            if len(comm_parts) < 4:
                                raise TypeError('Not enough command parameters supplied.')
                            else:
                                exoparams = comm_parts[3].split(",")
                                if len(exoparams) != 7:
                                    raise TypeError('Wrong number of kinematics parameters supplied.')
                                else:
                                    # Check handedness
                                    handedness = comm_parts[2]
                                    print(handedness)
                                    if not(handedness == 'RIGHT' or handedness == 'LEFT'):
                                        raise ValueError('Handedness '+handedness+' not recognised. Please use either "left" or "right".')

                                    # Convert input strings to floats
                                    try:
                                        exoparams_num = [ float(x) for x in exoparams ]
                                        # Divide x and y paramters by 10
                                        exoparams_num[0] /= 10
                                        exoparams_num[1] /= 10
                                    except TypeError:
                                        raise
                                    
                                    print('MESSAGE: Adding exo of type ' + exotype + '(' + handedness + ').')
                                    
                                    # Add exo
                                    taskMgr.add(self.addExoTask, "addExoTask",extraArgs = [("realtime",handedness.lower()),exoparams_num])
                                    # Send ID of the last added exo back to the client
                                    taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                        
                        elif exotype == 'EXOKEYBOARD':
                            if len(comm_parts) < 3:
                                raise TypeError('Not enough command parameters supplied.')
                            else:
                                # Check handedness
                                handedness = comm_parts[2]
                                print(handedness)
                                if not(handedness == 'RIGHT' or handedness == 'LEFT'):
                                    raise ValueError('Handedness '+handedness+' not recognised. Please use either "left" or "right".')
                                    
                                print('MESSAGE: Adding exo of type ' + exotype + '(' + handedness + ').')
                                    
                                # Add exo
                                taskMgr.add(self.addExoTask, "addExoTask",extraArgs = [("keyboard",handedness.lower()),""])
                                # Send ID of the last added exo back to the client
                                taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                                    
                        else:
                            raise ValueError('"'+exotype+'"'+' is an exo unknown type.')
                                    
                    # "DELETE" command
                    elif comm_parts[0] == 'DELETE':
                        # Get the id of the exo
                        id = comm_parts[1]
                        if id in self.exos:
                            print('MESSAGE: Deleting exo: '+id)
                            taskMgr.add(self.removeExoTask, "removeExoTask", extraArgs = [id])
                        else:
                            print("MESSAGE: ID " + id + " not found.")
                        
                    # "ADDBASE" command
                    elif comm_parts[0] == 'ADDBASE':
                        exotype = comm_parts[1]
                        # Check which type of exo should be added
                        if exotype == 'EXOSTATIC':
                            if len(comm_parts) < 3:
                                raise TypeError('Not enough command parameters supplied.')
                            else:
                                exoparams = comm_parts[2].split(",")
                                if len(exoparams) != 3:
                                    raise TypeError('Wrong number of kinematics parameters supplied.')
                                else:
                                    # Convert input strings to floats
                                    try:
                                        exoparams_num = [ float(x) for x in exoparams ]
                                        # Divide x and y paramters by 10
                                        exoparams_num[0] /= 10
                                        exoparams_num[1] /= 10
                                    except TypeError:
                                        raise
                                    
                                    print('MESSAGE: Adding exo (base only) of type ' + exotype +'.')
                                    
                                    # Add exo
                                    taskMgr.add(self.addBaseTask, "addBaseTask",extraArgs = ["static",exoparams_num])
                                    # Send ID of the last added exo back to the client
                                    taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                                    
                        elif exotype == 'EXOREALTIME':
                            if len(comm_parts) < 3:
                                raise TypeError('Not enough command parameters supplied.')
                            else:
                                exoparams = comm_parts[2].split(",")
                                if len(exoparams) != 3:
                                    raise TypeError('Wrong number of kinematics parameters supplied.')
                                else:
                                    # Convert input strings to floats
                                    try:
                                        exoparams_num = [ float(x) for x in exoparams ]
                                        # Divide x and y paramters by 10
                                        exoparams_num[0] /= 10
                                        exoparams_num[1] /= 10
                                    except TypeError:
                                        raise
                                    
                                    print('MESSAGE: Adding exo (base only) of type ' + exotype + '.')
                                    
                                    # Add exo
                                    taskMgr.add(self.addBaseTask, "addBaseTask",extraArgs = ["realtime",exoparams_num])
                                    # Send ID of the last added exo back to the client
                                    taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                        
                        elif exotype == 'EXOKEYBOARD':
                            if len(comm_parts) < 2:
                                raise TypeError('Not enough command parameters supplied.')
                            else:                                    
                                print('MESSAGE: Adding exo (base only) of type ' + exotype + '.')
                                    
                                # Add exo
                                taskMgr.add(self.addBaseTask, "addBaseTask",extraArgs = ["keyboard",""])
                                # Send ID of the last added exo back to the client
                                taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
                                    
                        else:
                            raise ValueError('"'+exotype+'"'+' is an exo unknown type.')
                                
                    # "DATA" command
                    elif comm_parts[0] == 'DATA':
                        # Get the id of the exo. If the id does not exist a KeyError is raised and caught.
                        id = comm_parts[1]
                        exoparams = comm_parts[2].split(",")
                        if len(exoparams) != 7:
                            raise TypeError('Wrong number of kinematics parameters supplied.')
                        else:
                            # Convert input strings to floats
                            try:
                                exoparams_num = [ float(x) for x in exoparams ]
                                # Divide x and y paramters by 10
                                exoparams_num[0] /= 10
                                exoparams_num[1] /= 10
                            except TypeError:
                                raise

                            if not(id in self.exos):
                                raise KeyError('Id '+id+' of Exo not found.')
                            else:
                                                            if (isinstance(self.exos[id].dc,ExoDataControllerRealTime) or isinstance(self.exos[id].dc, BaseDataControllerRealTime)):
                                self.exos[id].dc.set_data(exoparams_num)
                                                            else:
                                                                raise TypeError('Cannot send data to static or keyboard-controlled exo.')

                                        # "LOADCONFIG" command
                                        elif comm_parts[0] == 'LOADCONFIG':
                                            # Get the filename
                                            fname = comm_parts[1]

                                            taskMgr.add(self.loadConfigTask, "loadConfigTask",extraArgs = [fname])

                                        # "SETCONFIG" command
                                        elif comm_parts[0] == 'SETCONFIG': 
                                            # Get the id of the exo. If the id does not exist a KeyError is raised and caught.
                                            exo_id = comm_parts[1]
                                            
                                            if not(exo_id in self.exos):
                                                raise KeyError('Id '+exo_id+' of Exo not found.')
                                            else:
                        taskMgr.add(self.setConfigTask, "setConfigTask",extraArgs = [exo_id])

                    # "SETCOLORBASE" command
                    elif comm_parts[0] == 'SETCOLORBASE':
                        # Get the id of the exo. If the id does not exist a KeyError is raised and caught.
                        id = comm_parts[1]
                        # Get the target part of the exo to be coloured.
                        target = comm_parts[2]
                        # Get the rgb colour information
                        colors = comm_parts[3].split(",")
                        if len(colors) != 3:
                            raise TypeError('Not enough color parameters supplied.')
                        else:
                            # Convert input strings to floats
                            try:
                                colors_num = [ float(x) for x in colors ]
                            except TypeError:
                                raise
                                
                            for number in colors_num:
                                if number < 0 or number > 1:
                                    raise ValueError('RGB values are only allowed between 0 and 1');

                            if not(id in self.exos):
                                raise KeyError('Id '+id+' of Exo not found.')
                            else:
                                if target == 'BASE':
                                    taskMgr.add(self.exos[id].setColorBaseTask, "setColorBaseTask",extraArgs = [colors_num])
                                elif target == 'ARMREST':
                                    taskMgr.add(self.exos[id].setColorArmRestTask,"setColorArmRestTask",extraArgs = [colors_num])
                                else:
                                    raise ValueError('Target "' + target +'" unknown.')
                    
                    # "SETCOLORHAND" command
                    elif comm_parts[0] == 'SETCOLORHAND':
                        # Get the id of the exo. If the id does not exist a KeyError is raised and caught.
                        id = comm_parts[1]
                        # Get the target part of the exo to be coloured.
                        target = comm_parts[2]
                        # Get the rgb colour information
                        colors = comm_parts[3].split(",")
                        if len(colors) != 3:
                            raise TypeError('Not enough color parameters supplied.')
                        else:
                            # Convert input strings to floats
                            try:
                                colors_num = [ float(x) for x in colors ]
                            except TypeError:
                                raise
                                
                            for number in colors_num:
                                if number < 0 or number > 1:
                                    raise ValueError('RGB values are only allowed between 0 and 1');

                            if not(id in self.exos):
                                raise KeyError('Id '+id+' of Exo not found.')
                            # Catch colour commands for the hand from being send to the base
                            elif(isinstance(self.exos[id],BaseLogic)):
                                raise TypeError('Cannot set color of hand module for EXOBASE object.')
                            
                            else:
                                if target == 'SUPPRO':
                                    taskMgr.add(self.exos[id].setColorPronoTask, "setColorPronoTask",extraArgs = [colors_num])
                                elif target == 'INDEX':
                                    taskMgr.add(self.exos[id].setColorIndexTask, "setColorIndexTask",extraArgs = [colors_num])    
                                elif target == 'FINGERGROUP':
                                    taskMgr.add(self.exos[id].setColorFingerGroupTask, "setColorFingerGroupTask",extraArgs = [colors_num])
                                elif target == 'THUMB':
                                    taskMgr.add(self.exos[id].setColorThumbTask, "setColorThumbTask",extraArgs = [colors_num])
                                else:
                                    raise ValueError('Target "'+target+'" unknown.')
                                
                    # "SETBGCOLOR" command
                    elif comm_parts[0] == 'SETBGCOLOR':
                        # Get the colors
                        colors = comm_parts[1].split(",")
                        if len(colors) != 3:
                            raise TypeError('Wrong number of parameters supplied.')
                        else:
                            # Convert input strings to floats
                            try:
                                colors_num = [ float (x) for x in colors ]
                            except TypeError:
                                raise
                            
                            for number in colors_num:
                                if number < 0 or number > 1:
                                    raise ValueError('RGB values are only allowed between 0 and 1');
                            
                            taskMgr.add(self.changeBgColorTask,"setBgColorTask",extraArgs = [colors_num])
                            
                    # "SETCAMERA" command
                    elif comm_parts[0] == 'SETCAMERA':
                        # Get the coordinates
                        coord_vector = comm_parts[1].split(",")
                        if len(coord_vector) != 6:
                            raise TypeError('Wrong number of parameters supplied.')
                        else:
                            # Convert input strings to floats
                            try:
                                coord_vector_num = [ float (x) for x in coord_vector ]
                            except TypeError:
                                raise
                            
                            taskMgr.add(self.setCameraOrientationPositionTask,"setCameraOrientationPositionTask",extraArgs = [coord_vector_num])
                            
                    # "ROTATECAMERA" command
                    elif comm_parts[0] == 'ROTATECAMERA':
                        # Get the angle
                        angle = comm_parts[1]
                        print(angle)
                        # Convert input strings to floats
                        try:
                            angle_num = float(angle)
                        except TypeError:
                            raise
                                
                        taskMgr.add(self.rotateCameraTask,"rotateCameraTask",extraArgs = [angle_num])
                    
                    # "TOGGLETRANSPARENCY" command
                    elif comm_parts[0] == 'TOGGLETRANSPARENCY':
                        # Get the id of the exo. If the id does not exist a KeyError is raised and caught.
                        id = comm_parts[1]
                        
                        if not(id in self.exos):
                            raise KeyError('Id '+id+' of Exo not found.')
                        else:
                            taskMgr.add(self.exos[id].toggleTransparencyTask, "toggleTransparencyTask")
                            
                    # "TOGGLEMAT" command
                    elif comm_parts[0] == 'TOGGLEMAT':
                        side = comm_parts[1]
                        
                        if side in ('LEFT','RIGHT'):
                            taskMgr.add(self.toggleMatTask,"toggleMatTask",extraArgs = [side])
                        else:
                            raise ValueError('Value for type of the mat not understood. Please use "LEFT" or "RIGHT".')
                
                    # "EXIT" command
                    elif comm_parts[0] == 'EXIT':
                        taskMgr.add(self.tskTerminateConnections, "tcp_disconnect")
                        print('Good bye!')
                        sys.exit()
                    
                    # Invalid command
                    else:
                        raise TypeError('Invalid command '+command+'.')
                
                except TypeError as t:
                    print('ERROR: ' + str(t))
                except ValueError as v:
                    print('ERROR: ' + str(v))
                except KeyError as k:
                    print('ERROR: ' + str(k))
                except IndexError:
                    print('ERROR: Not enough command parameters supplied.')
            
    def send_latest_id(self,connection):
        ''' This functions responds to the client and sends the ID of the exo that has been added last. '''
        self.cWriter.send(":"+self.exo_ids_in_order[-1],connection)
        return Task.done
        
    def send_message(self,message,connection):
        ''' This function responds to the client and sends a specified message. '''
        # self.cWriter.send(":"+message,self.activeConnections[-1])
        self.cWriter.send(":"+message,connection)
        return Task.done
        
    def addExoTask(self,type,data):
        ''' Function that adds a new task to the taskmanager. The new task adds a new exo of specified type. '''
        
        if type[0] == 'keyboard':
            # Load, modify and reparent models
            modeldata = self.create_exo_model(type[1])
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            # Create logic objects
            dc = ExoDataControllerKeyboard(rand_id,type[1])
            exo = ExoLogic(modeldata['exo'],modeldata['armrest'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        elif type[0] == 'static':
            # Load, modify and reparent models
            modeldata = self.create_exo_model(type[1])
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            print(data)
            
            # Create logic objects
            dc = ExoDataControllerStatic(rand_id,self.cfgprofile['calibration'],type[1],data[0],data[1],data[2],data[3],data[4],data[5],data[6])
            exo = ExoLogic(modeldata['exo'],modeldata['armrest'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        elif type[0] == 'realtime':
            # Load, modify and reparent models
            modeldata = self.create_exo_model(type[1])
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            # Create logic objects
            dc = ExoDataControllerRealTime(rand_id,self.cfgprofile['calibration'],type[1])
            # Set initial data
            dc.set_data(data)
            exo = ExoLogic(modeldata['exo'],modeldata['armrest'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        print("MESSAGE: # Exos in scene: "+ str(len(self.exos)) +"; Last id: "+self.exo_ids_in_order[-1])
        return Task.done
        
    def addBaseTask(self,type,data):
        ''' Function that adds a new task to the taskmanager. The new task adds a new base of specified type. '''
        
        if type == 'keyboard':
            # Load, modify and reparent models
            modeldata = self.create_exo_model_base()
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            # Create logic objects
            dc = BaseDataControllerKeyboard(rand_id)
            exo = BaseLogic(modeldata['exo'],modeldata['armrest'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        elif type == 'static':
            # Load, modify and reparent models
            modeldata = self.create_exo_model_base()
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            print(data)
            
            # Create logic objects
            dc = BaseDataControllerStatic(rand_id,self.cfgprofile['calibration'],data[0],data[1],data[2])
            exo = BaseLogic(modeldata['exo'],modeldata['armrest'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        elif type == 'realtime':
            # Load, modify and reparent models
            modeldata = self.create_exo_model_base()
            
            # Create unique ID for exo
            rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
            
            # Create logic objects
            dc = BaseDataControllerRealTime(rand_id,self.cfgprofile['calibration'])
            dc.set_data(data)
            exo = BaseLogic(modeldata['exo'],modeldata['armrest'],dc)
            
            # Add Exo to the program logic
            self.exos[rand_id] = exo
            self.exo_ids_in_order.append(rand_id)
            taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
            self.exos[rand_id].exo.reparentTo(self.rootNode)
            
        print("MESSAGE: # Exos in scene: "+ str(len(self.exos)) +"; Last id: "+self.exo_ids_in_order[-1])
        return Task.done
        
    def toggleMatTask(self,side):
        ''' Function that adds a task that adds or toggles a new mat to the taskmanager. '''
        
        # Load, modify and reparent models
        modeldata = self.create_mat_model(side)
            
        # Create logic objects
        mat = MatLogic(modeldata['mat'],side)
            
        # Remove existing mat from the rendering tree if necessary
        if self.mat:
            self.mat.mat.detachNode()
            
        # Add Mat to the program logic
        self.mat = mat
        self.mat.mat.reparentTo(self.rootNode)
        
        return Task.done
        
    def removeExoTask(self,id):
        ''' Removes specific exo from program logic (and secene). '''
        
        if id == 'last' and len(self.exos) > 0:
            # Remove exo model from rendering
            self.exos[self.exo_ids_in_order[-1]].exo.detachNode()
            # Remove ExoLogic from ProgramLogic
            del self.exos[self.exo_ids_in_order[-1]]
            # Remove the id of the Exo from ProgramLogic
            del self.exo_ids_in_order[-1]
        
        elif id in self.exos:
            # Remove exo model from rendering
            self.exos[id].exo.detachNode()
            # Remove ExoLogic from ProgramLogic
            del self.exos[id]
            # Remove the id of the Exo from ProgramLogic
            del self.exo_ids_in_order[self.exo_ids_in_order.index(id)]
            
        return Task.done
    
    #TODO: REMOVE Mat
    
    def changeBgColorTask(self,color):
        ''' Changes the background color according to color.'''
        
        base.setBackgroundColor(color[0],color[1],color[2]);
        
        return Task.done
        
    def setCameraOrientationPositionTask(self,coordvec):
        ''' Set position and orientation of the camera. '''
        
        base.camera.setPos(coordvec[0],coordvec[1],coordvec[2])
        base.camera.setHpr(coordvec[3],coordvec[4],coordvec[5])
        
        return  Task.done
        
    def rotateCameraTask(self,angle):
        ''' Rotate camera while facing the center of the mat. '''
        
        camLogic = CameraLogic(self)
        camLogic.rotate(angle)
    
        return Task.done

        def loadConfigTask(self,filename):
            ''' Loads and initializes config.'''
            cfg = {}
            cfg = self.loadconfig(filename)

            if(cfg):
                self.initializeconfig(cfg)

            return Task.done

        def setConfigTask(self,exo_id):
            ''' Sets the current configuration dictionary as calibration profile of the specified exo.'''
            self.exos[exo_id].dc.setconfig(self.cfgprofile['calibration'])

            return Task.done
    
    def create_exo_model(self,handedness):
        ''' Function that loads an exo model with left or right hand arm. '''
        # Load models
        data = {}
        data['exo'] = loader.loadModel('models/exo3_base')
        data['armrest'] = loader.loadModel('models/exo3_arm_rest')
        
        if handedness == 'right':
            data['fthumb'] = loader.loadModel('models/exo3_fthumb_right')
            data['fgroup'] = loader.loadModel('models/exo3_fgroup_right')
            data['findex'] = loader.loadModel('models/exo3_findex_right')
            data['prono'] = loader.loadModel('models/exo3_prono_right2')
            
            data['prono'].setPos(0.1,1.8,1.5)
            data['prono'].setP(0)
            data['fthumb'].setPos(-0.5,0.3,0.5)
            data['fgroup'].setPos(0.6,0.3,0.3)
            data['fgroup'].setH(120)
            data['findex'].setPos(0.6,0.3,1)
            data['findex'].setH(120)
        else:
            data['fthumb'] = loader.loadModel('models/exo3_fthumb_left')
            data['fgroup'] = loader.loadModel('models/exo3_fgroup_left')
            data['findex'] = loader.loadModel('models/exo3_findex_left')
            data['prono'] = loader.loadModel('models/exo3_prono_left')
            
            data['prono'].setPos(0.1,1.8,1.5)
            data['prono'].setP(0)
            data['fthumb'].setPos(0.5,0.3,0.5)
            data['fgroup'].setPos(-0.6,0.3,0.3)
            data['fgroup'].setH(120)
            data['findex'].setPos(-0.6,0.3,1)
            data['findex'].setH(120)
    
        # Define and set materials
        exoMaterial = Material()
        exoMaterial.setShininess(5.0)
        exoMaterial.setAmbient((0.6,0.6,0.6,1))
        exoMaterial.setDiffuse((0.25,0.25,0.25,.25))
        
        armMaterialList = [Material() for i in range(5)]
        for i in range(5):
            armMaterialList[i].setShininess(12.0)
            armMaterialList[i].setAmbient((0.6,0.6,0.6,1))
            armMaterialList[i].setDiffuse((0.3,0.3,0.3,1))
        
        data['exomaterial'] = exoMaterial
        
        data['exo'].setMaterial(exoMaterial)
        data['armrest'].setMaterial(armMaterialList[0])
        data['prono'].setMaterial(armMaterialList[1])
        data['fthumb'].setMaterial(armMaterialList[2])
        data['fgroup'].setMaterial(armMaterialList[3])
        data['findex'].setMaterial(armMaterialList[4])
        
        # Reparent objects        
        data['armrest'].reparentTo(data['exo'])
        data['prono'].reparentTo(data['armrest'])
        data['fthumb'].reparentTo(data['prono'])
        data['fgroup'].reparentTo(data['prono'])
        data['findex'].reparentTo(data['prono'])
        
        return data
        
    def create_exo_model_base(self):
        ''' Function that loads an exo model without arm. '''
        # Load models
        data = {}
        data['exo'] = loader.loadModel('models/exo3_base')
        data['armrest'] = loader.loadModel('models/exo3_arm_rest')
        
        # Define and set materials
        exoMaterial = Material()
        exoMaterial.setShininess(5.0)
        exoMaterial.setAmbient((0.6,0.6,0.6,1))
        exoMaterial.setDiffuse((0.25,0.25,0.25,.25))
        
        armMaterial = Material()
        armMaterial.setShininess(12.0)
        armMaterial.setAmbient((0.6,0.6,0.6,1))
        armMaterial.setDiffuse((0.3,0.3,0.3,1))
        
        data['exomaterial'] = exoMaterial
        
        data['exo'].setMaterial(exoMaterial)
        data['armrest'].setMaterial(armMaterial)
        
        # Reparent objects        
        data['armrest'].reparentTo(data['exo'])
        
        return data
        
    def create_mat_model(self,side):
        ''' Function that loads an exo model without arm. '''
        # Load models
        data = {}
        
        if side.lower() == 'left':
            data['mat'] = loader.loadModel('models/mat_left')
        elif side.lower() == 'right':
            data['mat'] = loader.loadModel('models/mat_right')
        
        return data
        
    def dotProduct(self,matrix,vector):
        ''' Computes the dot product of a matrix and a vector. 
        The matrix is in the format a[d1][d2].'''
        dotProd = []
        for j in range(len(matrix)):
            dotProd.append(sum( [matrix[j][i]*vector[i] for i in range(len(vector))] ))
        
        print(dotProd)
        return dotProd

        def loadconfig(self,filename):
            ''' Loads a yaml configuration file and returns contents as a dictionary.''' 
            try:
                with open(filename+'.yml', 'r') as ymlfile:
                    cfg = yaml.load(ymlfile)
                
                print("Profile "+filename+" loaded.")
                return cfg
            except IOError:
                print("Could not find profile: "+filename+".")

        def initializeconfig(self,config_dictionary):
            ''' Sets a configuration dictionary as cfgprofile in the program logic.'''
            self.cfgprofile = config_dictionary
            print("New profile initialized.")
