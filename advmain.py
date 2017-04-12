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
		base.disableMouse()
		
		self.graphical_objects = []
		self.logic_objects = []
		
		self.build_scene()
		
		data = self.add_exo()
		self.graphical_objects.append(data)
		
		data = self.add_exo()
		self.graphical_objects.append(data)
		
		# Reparent exo models
		
		self.graphical_objects[0]['exo'].reparentTo(self.render)
		self.graphical_objects[1]['exo'].reparentTo(self.render)
		
		dc = advclass.ExoDataControllerKeyboard()
		dc2 = advclass.ExoDataControllerStatic(1,3,20,180,20,0)
		
		self.logic_objects.append(advclass.ExoLogic(self.graphical_objects[0]['exo'],self.graphical_objects[0]['findex'],self.graphical_objects[0]['fgroup'],self.graphical_objects[0]['fthumb'],dc))
		
		self.logic_objects.append(advclass.ExoLogic(self.graphical_objects[1]['exo'],self.graphical_objects[1]['findex'],self.graphical_objects[1]['fgroup'],self.graphical_objects[1]['fthumb'],dc2))
		
		# Add movement task to task manager
		taskMgr.add(self.logic_objects[0].getDataTask, "moveTask")
		taskMgr.add(self.logic_objects[1].getDataTask, "moveTask")
		
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

		data = self.add_exo()
		
		# Reparent models
		self.objects.append(data)
		self.objects[0]['exo'].reparentTo(self.render)
		
	def add_exo(self):
		''' Function that loads an exo model '''
		# Load models
		data = {}
		data['exo'] = loader.loadModel('models/exo3_base.egg')
		data['arm'] = loader.loadModel('models/exo3_arm.egg')
		data['fthumb'] = loader.loadModel('models/exo3_fthumb.egg')
		data['fgroup'] = loader.loadModel('models/exo3_fgroup.egg')
		data['findex'] = loader.loadModel('models/exo3_findex.egg')
	
		# Define and set materials
		exoMaterial = Material()
		exoMaterial.setShininess(5.0)
		exoMaterial.setAmbient((0.6,0.6,0.6,1))
		exoMaterial.setDiffuse((0.5,0.5,0.5,1))
		
		armMaterial = Material()
		armMaterial.setShininess(5.0)
		armMaterial.setAmbient((0.6,0.6,0.7,0.7))
		armMaterial.setDiffuse((0.4,0.4,0.4,1))
		
		data['exo'].setMaterial(exoMaterial)
		data['arm'].setMaterial(armMaterial)
		
		# Set model properties
		data['fthumb'].setPos(-0.5,1.5,2)
		data['fthumb'].setP(12)
		data['fgroup'].setPos(0.8,1.65,2)
		data['fgroup'].setP(12)
		data['findex'].setPos(0.8,1.5,2.6)
		data['findex'].setP(12)
		
		data['arm'].reparentTo(data['exo'])
		data['fthumb'].reparentTo(data['arm'])
		data['fgroup'].reparentTo(data['arm'])
		data['findex'].reparentTo(data['arm'])
		
		return data
		
app = MyApp()
app.run()