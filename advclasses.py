# Class definitions for the advanced feedback

# ### Imports ### #
from math import pi, sin, cos, sqrt

from panda3d.core import *
from direct.task import Task

import random
import string

# ### Begin ### #

class ExoLogic():
	''' Logic for the movement of the Exo '''
	
	def __init__(self,exo_model,exo_prono,findex_model,fgroup_model,fthumb_model,dataController):
		self.exo = exo_model
		self.prono = exo_prono
		self.findex = findex_model
		self.fgroup = fgroup_model
		self.fthumb = fthumb_model
			
		self.dc = dataController
		
	def getDataTask(self,task):
		''' This is the task the handles the movement of the exo model. '''
		
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

# ### Data controllers ### #		

class ExoDataControllerKeyboard():
	''' A DataController that returns the robot position according to the keyboard input '''
	
	def __init__(self,id):
		self.id = id
		
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
		if dir == 'open':
			return (exo_state[4] - 2)%360
		else:
			return (exo_state[4] + 2)%360
			
	def compute_fgroup(self,dir,exo_state):
		''' Turn the finger group '''
		if dir == 'open':
			return (exo_state[5] - 2)%360
		else:
			return (exo_state[5] + 2)%360
			
	def compute_fthumb(self,dir,exo_state):
		''' Turn the thumb '''
		if dir == 'open':
			return (exo_state[6] + 2)%360
		else:
			return (exo_state[6] - 2)%360
			
	def compute_prono(self,dir,exo_state):
		''' Pronate or supinate '''
		if dir == 'pronate':
			return (exo_state[3] + 2)%360
		else:
			return (exo_state[3] - 2)%360

class ExoDataControllerStatic():
	''' A DataController that returns the static position value with which it was initialised. '''
	
	def __init__(self,id,exo_x,exo_y,exo_h,prono_r,findex_h,fgroup_h,fthumb_h):
		
		self.id = id
		
		self.robot = {}
		self.prono = {}
		self.findex = {}
		self.fgroup = {}
		self.fthumb = {}
				
		self.robot['x'] = exo_x
		self.robot['y'] = exo_y
		self.robot['heading'] = exo_h
		
		self.prono['roll'] = prono_r
		self.findex['heading'] = findex_h
		self.fgroup['heading'] = fgroup_h
		self.fthumb['heading'] = fthumb_h
			
	def get_data(self,exo_state):
		''' Function that returns the position data to the exo logic object '''
		
		return (self.robot,self.prono,self.findex,self.fgroup,self.fthumb)
		
# class DataControllerPlayback():
# Playback predefined trajectory at the correct speed
#FIXME This is not necessary! Instead a DataControllerRealTime should be created and the client should read a file and send it via TCP

class ExoDataControllerRealTime():
	''' A DataController that returns the position value which it has received through TCP. '''
	
	def __init__(self, id):
	
		self.id = id
	
		# Setup exo model
		self.robot = {}
		self.prono = {}
		self.findex = {}
		self.fgroup = {}
		self.fthumb = {}
		
				
	def set_data(self,exo_state):
		''' Function that sets the parameters of the degrees of freedom of the robot. '''
		
		self.robot['x'] = exo_state[0]
		self.robot['y'] = exo_state[1]
		self.robot['heading'] = exo_state[2]
		
		self.prono['roll'] = exo_state[3]
		self.findex['heading'] = exo_state[4]
		self.fgroup['heading'] = exo_state[5]
		self.fthumb['heading'] = exo_state[6]
		
		
	def get_data(self,exo_state):
		''' Function that returns the position data to the exo logic object '''
		
		return (self.robot,self.prono,self.findex,self.fgroup,self.fthumb)
		
		

# class DataControllerRealTime():
# A roboter that gets data via UDP
		

# ### Program logic ### #
class ProgramLogic():
	''' ProgramLogic that controls creating and removing exos and their corresponding data controllers '''
	
	def __init__(self,render):
		# Dict that contains all exos (Using a dict to be able to use hashmap-like random ids. Better for adding and removing exos.)
		self.exos = {}
		# This list contains all the ids of the exos in the order they were added to the program
		self.exo_ids_in_order = []
		# This is referring to the root of the rendering tree
		self.rootNode = render
		
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
		''' Function that parses the commands that are received through TCP. '''
		# Extract message from the data
		command = datagram.getMessage()
		connection = datagram.getConnection()
		print("MESSAGE: Command '"+command+"' received.")
		
		comm_parts = command.split(" ")
		
		# Check if command has valid length
		if len(comm_parts) < 2:
			print('ERROR: did not understand command')
			taskMgr.doMethodLater(0.5,self.send_message,'Send_error_not_understood',extraArgs = ['Command not understood.',connection])
			return
		
		# Check which command is being send
		# "ADD" command
		if comm_parts[0] == 'ADD':
			exotype = comm_parts[1]
			# Check which type of exo should be added
			if exotype == 'EXOSTATIC':
				if len(comm_parts) < 3:
					print('MESSAGE: Invalid command')
					taskMgr.doMethodLater(0.5,self.send_message,'Invalid command',extraArgs = ['Invalid command.',connection])
				else:
					try:
						exoparams = comm_parts[2].split(",")
					except:
						print('ERROR: did not understand command')
						taskMgr.doMethodLater(0.5,self.send_message,'Send_error_not_understood',extraArgs = ['Not enough parameters.',connection])
					if len(exoparams) < 7:
						print('MESSAGE: Not enough parameters')
						taskMgr.doMethodLater(0.5,self.send_message,'Send_parameters_wrong',extraArgs = ['Not enough parameters.',connection])
					elif len(exoparams) > 7:
						print('MESSAGE: Too many parameters')
						taskMgr.doMethodLater(0.5,self.send_message,'Send_parameters_wrong',extraArgs = ['Too many paramters.',connection])
					else:
						print('MESSAGE: Adding exo of type ' + exotype)

						try:
							# Convert input strings to floats
							exoparams_num = [ float(x) for x in exoparams ]
							# Add exo
							taskMgr.add(self.addExoTask, "addExoTask",extraArgs = ["static",exoparams_num])
							# Send ID of the last added exo back to the client
							taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
						except:
							print('ERROR: Could not convert input data. Please only use numbers!')
							taskMgr.doMethodLater(0.5,self.send_message,'Send_error_not_understood',extraArgs = ['Could not convert input data. Please only use numbers!',connection])
						
			elif exotype == 'EXOREALTIME':
				if len(comm_parts) < 2:
					print('MESSAGE: Invalid command')
				else:
					print('MESSAGE: Adding exo of type ' + exotype)

					taskMgr.add(self.addExoTask, "addExoTask",extraArgs = ["realtime",""])
						
					# Send ID of the last added exo back to the client
					taskMgr.doMethodLater(0.5,self.send_latest_id,'Send_Latest_Exo_id',extraArgs = [connection])
					
		# "DELETE" command
		elif comm_parts[0] == 'DELETE':
			# Get the id of the exo
			id = comm_parts[1]
			if id in self.exos:
				print('MESSAGE: Deleting exo: '+id)
				taskMgr.add(self.removeExoTask, "removeExoTask", extraArgs = [id])
			
				taskMgr.doMethodLater(0.5,self.send_message,'Send_delete_confirmation',extraArgs = ['Deleted exo '+id,connection])
			else:
				print("MESSAGE: ID " + id + " not found.")
				taskMgr.doMethodLater(0.5,self.send_message,'Send_delete_not_found',extraArgs = ['Exo '+id+' not found.',connection])
			
		# "DATA" command
		elif comm_parts[0] == 'DATA':
			# Get the id of the exo
			id = comm_parts[1]
			# Check if this exo is of type RealTime (implicitely by using catching exceptions)
			try:
				exoparams = comm_parts[2].split(",")
				if len(exoparams) < 7:
					print('MESSAGE: Not enough parameters')
				elif len(exoparams) > 7:
					print('MESSAGE: Too many parameters')
				else:
					# Cast input strings to int
					try:
						exoparams_num = [ float(x) for x in exoparams ]
						self.exos[id].dc.set_data(exoparams_num)
					except:
						print('ERROR: Could not convert input data. Please only use numbers!')
						taskMgr.doMethodLater(0.5,self.send_message,'Send_error_not_understood',extraArgs = ['Could not convert input data. Please only use numbers!',connection])
					
			except:
				print("MESSAGE: Moving robot "+id+" failed.")
			
		# Invalid command
		else:
			print('ERROR: did not understand command')
			taskMgr.doMethodLater(0.5,self.send_message,'Send_error_not_understood',extraArgs = ['Command not understood.',connection])
			
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
		
		if type == 'keyboard':
			# Load, modify and reparent models
			modeldata = self.create_exo_model()
			
			# Create unique ID for exo
			rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
			
			# Create logic objects
			dc = ExoDataControllerKeyboard(rand_id)
			exo = ExoLogic(modeldata['exo'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
			
			# Add Exo to the program logic
			self.exos[rand_id] = exo
			self.exo_ids_in_order.append(rand_id)
			taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
			self.exos[rand_id].exo.reparentTo(self.rootNode)
			
		elif type == 'static':
			# Load, modify and reparent models
			modeldata = self.create_exo_model()
			
			# Create unique ID for exo
			rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
			
			print(data)
			
			# Create logic objects
			dc = ExoDataControllerStatic(rand_id,data[0],data[1],data[2],data[3],data[4],data[5],data[6])
			exo = ExoLogic(modeldata['exo'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
			
			# Add Exo to the program logic
			self.exos[rand_id] = exo
			self.exo_ids_in_order.append(rand_id)
			taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
			self.exos[rand_id].exo.reparentTo(self.rootNode)
			
		elif type == 'realtime':
			# Load, modify and reparent models
			modeldata = self.create_exo_model()
			
			# Create unique ID for exo
			rand_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(5))
			
			# Create logic objects
			dc = ExoDataControllerRealTime(rand_id)
			# Set initial data
			exo_initial_state = (0,0,0,0,0,-10,10)
			dc.set_data(exo_initial_state)
			exo = ExoLogic(modeldata['exo'],modeldata['prono'],modeldata['findex'],modeldata['fgroup'],modeldata['fthumb'],dc)
			
			# Add Exo to the program logic
			self.exos[rand_id] = exo
			self.exo_ids_in_order.append(rand_id)
			taskMgr.add(self.exos[rand_id].getDataTask, "moveTask")
			self.exos[rand_id].exo.reparentTo(self.rootNode)
			
		print("MESSAGE: # Exos in scene: "+ str(len(self.exos)) +"; Last id: "+self.exo_ids_in_order[-1])
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
	
	def create_exo_model(self):
		''' Function that loads an exo model '''
		# Load models
		data = {}
		data['exo'] = loader.loadModel('models/exo3_base')
		data['arm_rest'] = loader.loadModel('models/exo3_arm_rest')
		data['prono'] = loader.loadModel('models/exo3_prono')
		data['fthumb'] = loader.loadModel('models/exo3_fthumb')
		data['fgroup'] = loader.loadModel('models/exo3_fgroup')
		data['findex'] = loader.loadModel('models/exo3_findex')
	
		# Define and set materials
		exoMaterial = Material()
		exoMaterial.setShininess(5.0)
		exoMaterial.setAmbient((0.6,0.6,0.6,1))
		exoMaterial.setDiffuse((0.5,0.5,0.5,1))
		
		armMaterial = Material()
		armMaterial.setShininess(12.0)
		armMaterial.setAmbient((0.6,0.6,0.6,1))
		armMaterial.setDiffuse((0.3,0.3,0.3,1))
		
		data['exo'].setMaterial(exoMaterial)
		data['arm_rest'].setMaterial(armMaterial)
		data['prono'].setMaterial(armMaterial)
		
		# Set model properties
		data['prono'].setPos(0.1,1.8,1.5)
		data['prono'].setP(0)
		data['fthumb'].setPos(-0.5,0.3,0.5)
		data['fgroup'].setPos(0.6,0.3,0.3)
		data['fgroup'].setH(120)
		data['findex'].setPos(0.6,0.3,1)
		data['findex'].setH(120)
		
		data['arm_rest'].reparentTo(data['exo'])
		data['prono'].reparentTo(data['arm_rest'])
		data['fthumb'].reparentTo(data['prono'])
		data['fgroup'].reparentTo(data['prono'])
		data['findex'].reparentTo(data['prono'])
		
		return data