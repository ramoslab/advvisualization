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
		
		dc = advclass.DataControllerKeyboard()
		self.exoLogic = advclass.ExoLogic(self.exo,self.fthumb,self.fgroup,self.findex,dc)
		
		# Add movement task to task manager
		taskMgr.add(self.exoLogic.getDataTask, "moveTask")
		
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
		
		
	
			
	def applySpeedVector(self):
		self.exo.setX(self.sv.robot['x'])
		self.exo.setY(self.sv.robot['y'])
		self.exo.setH(self.sv.robot['heading'])
		
app = MyApp()
app.run()