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
		
		# Initialise program logic
		pl = advclass.ProgramLogic(self.render)
		
		# Initialise scene
		self.build_scene()
		
		# Set accepted keys for keyboard control of the program logic
		self.accept('f10',self.addExoTask,[pl,'left'])
		self.accept('f9',self.addBaseTask,[pl])
		self.accept('f11',self.addExoTask,[pl,'right'])
		self.accept('f12',self.removeExoTask,[pl])
		self.accept('escape', self.exit_feedback, [pl])
		
		taskMgr.add(pl.tskListenerPolling, "tcp_establish")
		taskMgr.add(pl.tskReaderPolling, "tcp_poll")
		
	def addExoTask(self,pl,handedness):
		### Temporary function for testing ###
		
		taskMgr.add(pl.addExoTask,'addExoTask', extraArgs = [('keyboard',handedness),""])
		
	def removeExoTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.removeExoTask,'removeExoTask', extraArgs = ['last'])
		
	def addBaseTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.addBaseTask,'addBaseTask', extraArgs = ['keyboard',""])
		
		
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
		self.mat = loader.loadModel('models/mat')
		
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