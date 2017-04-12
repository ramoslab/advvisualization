# Class definitions for the advanced feedback

# TODOS und FIXMES
# Pronation - Supination fehlt noch
# Logik fuer das Hinzufuegen und Entfernen von verschiedenen Typen von Exos und ExoLogics fehlt noch
# 	Dazu braucht es dann auch mehrere Interfaces (Tastatur + GUI, UDP)

from math import pi, sin, cos, sqrt

from panda3d.core import *
from direct.task import Task

class ExoLogic():
	''' Logic for the movement of the Exo '''
	
	def __init__(self,exo_model,findex_model,fgroup_model,fthumb_model,dataController):
		self.exo = exo_model
		self.findex = findex_model
		self.fgroup = fgroup_model
		self.fthumb = fthumb_model
			
		self.dc = dataController
		
	def getDataTask(self,task):
		''' This is the task the handles the movement of the exo model. '''
		
		# Retrieve the data from the controller
		exo_state = (self.exo.getX(),self.exo.getY(),self.exo.getH(),self.findex.getH(),self.fgroup.getH(),self.fthumb.getH())
		data = self.dc.get_data(exo_state)
		
		# Set parameters of the base
		self.exo.setX(data[0]['x'])
		self.exo.setY(data[0]['y'])
		self.exo.setH(data[0]['heading'])
		
		# Set parameters of the arm module
		self.findex.setH(data[1]['heading'])
		self.fgroup.setH(data[2]['heading'])
		self.fthumb.setH(data[3]['heading'])
		
		return Task.cont

class ExoDataControllerKeyboard():
	''' A DataController that returns the robot position according to the keyboard input '''
	
	def __init__(self):
		self.robot = {}
		self.findex = {}
		self.fgroup = {}
		self.fthumb = {}
		
		self.robot['x'] = 0
		self.robot['y'] = 0
		self.robot['heading'] = 0
		
		self.findex['heading'] = 0
		self.fgroup['heading'] = 0
		self.fthumb['heading'] = 0
			
	def get_data(self,exo_state):
		''' Function that returns the position data to the exo logic object '''
		self.move(exo_state)
		
		return (self.robot,self.findex,self.fgroup,self.fthumb)
	
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
		
		# Apply speedvector
		#FIMXE Speedvector tied to robot needed; Robot controller needed
		#FIXME Move keyboard control to Controller class; Robot accepts controller that is its data provider throughout its lifetime
	
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
		if dir == 'open':
			return (exo_state[3] - 2)%360
		else:
			return (exo_state[3] + 2)%360
			
	def compute_fgroup(self,dir,exo_state):
		''' Turn the finger group '''
		if dir == 'open':
			return (exo_state[4] - 2)%360
		else:
			return (exo_state[4] + 2)%360
			
	def compute_fthumb(self,dir,exo_state):
		''' Turn the thumb '''
		if dir == 'open':
			return (exo_state[5] + 2)%360
		else:
			return (exo_state[5] - 2)%360

class ExoDataControllerStatic():
	''' A DataController that returns the static position value with which it was initialised. '''
	
	def __init__(self,exo_x,exo_y,exo_h,findex_h,fgroup_h,fthumb_h):
		self.robot = {}
		self.findex = {}
		self.fgroup = {}
		self.fthumb = {}
		
		self.robot['x'] = exo_x
		self.robot['y'] = exo_y
		self.robot['heading'] = exo_h
		
		self.findex['heading'] = findex_h
		self.fgroup['heading'] = fgroup_h
		self.fthumb['heading'] = fthumb_h
			
	def get_data(self,exo_state):
		''' Function that returns the position data to the exo logic object '''
		
		return (self.robot,self.findex,self.fgroup,self.fthumb)

# class DataControllerPlayback():
# Playback predefined trajectory at the correct speed

# class DataControllerRealTime():
# A roboter that gets data via UDP