# Class definitions for the advanced feedback

class SpeedVector():

	def __init__(self,robot_pos_x, robot_pos_y, robot_pos_z, robot_heading, fgroup_heading, fthumb_heading, findex_heading):
		self.robot = {}
		self.fgroup = {}
		self.fthumb = {}
		self.findex = {}
		
		self.robot['x'] = robot_pos_x
		self.robot['y'] = robot_pos_y
		self.robot['heading'] = robot_heading
		
		self.fgroup['heading'] = fgroup_heading
		self.fthumb['heading'] = fthumb_heading
		self.findex['heading'] = findex_heading
		
	def move_x(self,x):
		self.robot['x'] = x
	
	def move_y(self,y):
		self.robot['y'] = y
		
	def turn(self,h):
		self.robot['heading'] = h
		
	def turn_fgroup(self,angle):
		self.fgroup['heading'] = angle
		
	def turn_fthumb(self,angle):
		self.fthumb['heading'] = angle
		
	def turn_findex(self,angle):
		self.findex['heading'] = angle
		
		
# Superclass Robot
# Class Robot_keyboard: Initialisiert mit Speedvector