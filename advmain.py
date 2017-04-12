# Panda3d for the advanced feedback of the robot

import advclasses as advclass

from math import pi, sin, cos, sqrt

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
from direct.actor.Actor import Actor
from panda3d.core import *



class MyApp(ShowBase):

	def __init__(self):
		ShowBase.__init__(self)
		
		self.build_scene()
		self.load_objects()
		
		self.sv = advclass.SpeedVector(0,0,0,0,0,0,0)
		
		base.disableMouse()
		
		# Add movement task to task manager
		taskMgr.add(self.moveTask, "moveTask")
		
	def build_scene(self):
		# Define the lights
		alight = AmbientLight('alight1')
		alight.setColor(VBase4(1,1,1,1))
		alnp = self.render.attachNewNode(alight)
	
		plight = PointLight('plight')
		plight.setColor(VBase4(1,1,1,1))
		plnp = render.attachNewNode(plight)
		plnp.setPos(0, 0, 10)
	
		# Define the camera
		self.camera.setPos(0,-20,10)
		self.camera.setHpr(0,-25,0)
		
		# Floor mat
		self.mat = loader.loadModel('models/mat.egg')
		
		# Reparent objects
		self.render.setLight(alnp)
		self.render.setLight(plnp)
		self.mat.reparentTo(self.render)
	
	def load_objects(self):

		# Load models
		self.exo = loader.loadModel('models/exo3_base.egg')
		self.arm = loader.loadModel('models/exo3_arm.egg')
		self.fthumb = loader.loadModel('models/exo3_fthumb.egg')
		self.fgroup = loader.loadModel('models/exo3_fgroup.egg')
		self.findex = loader.loadModel('models/exo3_findex.egg')
	
		# Define and set materials
		exoMaterial = Material()
		exoMaterial.setShininess(5.0)
		exoMaterial.setAmbient((0.6,0.6,0.6,1))
		exoMaterial.setDiffuse((0.5,0.5,0.5,1))
		
		armMaterial = Material()
		armMaterial.setShininess(5.0)
		armMaterial.setAmbient((0.6,0.6,0.7,0.7))
		armMaterial.setDiffuse((0.4,0.4,0.4,1))
		
		self.exo.setMaterial(exoMaterial)
		self.arm.setMaterial(armMaterial)
		
		# Set model properties
		self.fthumb.setPos(-0.5,1.5,2)
		self.fthumb.setP(12)
		self.fgroup.setPos(0.8,1.65,2)
		self.fgroup.setP(12)
		self.findex.setPos(0.8,1.5,2.6)
		self.findex.setP(12)
		
		# Reparent models
		self.arm.reparentTo(self.exo)
		self.fthumb.reparentTo(self.arm)
		self.fgroup.reparentTo(self.arm)
		self.findex.reparentTo(self.arm)
		self.exo.reparentTo(self.render)
		
		
	def moveTask(self,task):
		''' The movement task that polls the keys and executes the target functions '''
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
			movement = self.moveTarget('forward')
			self.sv.move_x(movement[0])
			self.sv.move_y(movement[1])
		
		# Button "DOWN" moves robot forward
		if is_down(b_arrow_down):
			movement = self.moveTarget('backward')
			self.sv.move_x(movement[0])
			self.sv.move_y(movement[1])
		
		# Button "LEFT" turns robot to the left
		if is_down(b_arrow_left):
			movement = self.turnTarget('left')
			self.sv.turn(movement)
		
		# Button "RIGHT" moves robot to the right
		if is_down(b_arrow_right):
			movement = self.turnTarget('right')
			self.sv.turn(movement)
			
		# Button "Q" opens the index finger
		if is_down(b_q):
			movement = self.turn_findex('open')
		
		# Button "A" closes the index finger		
		if is_down(b_a):
			movement = self.turn_findex('close')
		
		# Button "W" opens the finger group		
		if is_down(b_w):
			movement = self.turn_fgroup('open')
		
		# Button "S" closes the finger group
		if is_down(b_s):
			movement = self.turn_fgroup('close')
			
		# Button "E" opens the thumb
		if is_down(b_e):
			movement = self.turn_fthumb('open')
			
		# Button "D" closes the thumb
		if is_down(b_d):
			movement = self.turn_fthumb('close')
		
		# Apply speedvector
		#FIMXE Speedvector tied to robot needed; Robot controller needed
		#FIXME Move keyboard control to Controller class; Robot accepts controller that is its data provider throughout its lifetime
		
		self.applySpeedVector()
			
		# Continue task indefinitely
		return Task.cont 
	
	def turnTarget(self,heading):
		headingOld = self.exo.getH()
		if heading == 'right':
			return (headingOld - 2)%360
		elif heading == 'left':
			return (headingOld + 2)%360
		
	def moveTarget(self,direction):
		''' Compute the target coordinates of a 2d movement initiated by the keyboard '''
		# Get current heading in degrees
		heading = self.exo.getH()
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
		posOld = self.exo.getPos()
		if direction == 'forward':
			return (posOld.x-distx,posOld.y-disty)
		elif direction == 'backward':
			return (posOld.x+distx,posOld.y+disty)
			
	def turn_findex(self,dir):
		''' Turn the index fingers '''
		if dir == 'open':
			findex_headingOld = self.findex.getH()
			self.findex.setH((findex_headingOld - 2)%360)
		else:
			findex_headingOld = self.findex.getH()
			self.findex.setH((findex_headingOld + 2)%360)
			
	def turn_fgroup(self,dir):
		''' Turn the finger group '''
		if dir == 'open':
			fgroup_headingOld = self.fgroup.getH()
			self.fgroup.setH((fgroup_headingOld - 2)%360)
		else:
			fgroup_headingOld = self.fgroup.getH()
			self.fgroup.setH((fgroup_headingOld + 2)%360)
			
	def turn_fthumb(self,dir):
		''' Turn the thumb '''
		if dir == 'open':
			fthumb_headingOld = self.fthumb.getH()
			self.fthumb.setH((fthumb_headingOld - 2)%360)
		else:
			fthumb_headingOld = self.fthumb.getH()
			self.fthumb.setH((fthumb_headingOld + 2)%360)
			
	def applySpeedVector(self):
		self.exo.setX(self.sv.robot['x'])
		self.exo.setY(self.sv.robot['y'])
		self.exo.setH(self.sv.robot['heading'])
		
app = MyApp()
app.run()