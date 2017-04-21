# Panda3d for the advanced feedback of the robot

import advclasses as advclass
import sys

from math import pi, sin, cos, sqrt

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
from direct.actor.Actor import Actor
from panda3d.core import *



class MyApp(ShowBase):

	def __init__(self):
		# Run init of parent
		ShowBase.__init__(self)
		# Disable movement of the camera
		base.disableMouse()
		
		# Initialise exo logic field
		# self.exos = []
		# Initialise scene
		self.build_scene()
		
		# data = self.create_exo_model()
		# self.graphical_objects.append(data)
		
		# data = self.add_exo()
		# self.graphical_objects.append(data)
		
		# Reparent exo models
		
		# for exo in self.graphical_objects:
			# exo['exo'].reparentTo(self.render)
		
		# dc = advclass.ExoDataControllerKeyboard()
		# dc2 = advclass.ExoDataControllerStatic(1,3,20,0,180,-10,10)
		
		# self.logic_objects.append(advclass.ExoLogic(self.graphical_objects[0]['exo'],self.graphical_objects[0]['prono'],self.graphical_objects[0]['findex'],self.graphical_objects[0]['fgroup'],self.graphical_objects[0]['fthumb'],dc))
		
		# self.logic_objects.append(advclass.ExoLogic(self.graphical_objects[1]['exo'],self.graphical_objects[1]['prono'],self.graphical_objects[1]['findex'],self.graphical_objects[1]['fgroup'],self.graphical_objects[1]['fthumb'],dc2))
		
		# Add movement task to task manager
		# taskMgr.add(self.logic_objects[0].getDataTask, "moveTask")
		# taskMgr.add(self.logic_objects[1].getDataTask, "moveTask")
		
		pl = advclass.ProgramLogic(self.render)
		
		# taskMgr.doMethodLater(1,pl.CommandListenerTask, "udptask")
		
		self.accept('f10',self.acceptExoTask,[pl])
		self.accept('f11',self.removeExoTask,[pl])
		self.accept('escape', self.exit_feedback, [pl])
		
		taskMgr.add(pl.tskListenerPolling, "tcp_establish")
		taskMgr.add(pl.tskReaderPolling, "tcp_poll")
		
	def acceptExoTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.addExoTask,'addExoTask', extraArgs = ['keyboard',""])
		
	def removeExoTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.removeExoTask,'removeExoTask', extraArgs = ['last'])
		
		
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
		
	def exit_feedback(self,pl):
		taskMgr.add(pl.tskTerminateConnections, "tcp_disconnect")
		print('Good bye!')
		sys.exit()
		
app = MyApp()
app.run()