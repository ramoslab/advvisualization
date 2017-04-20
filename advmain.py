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
		self.accept('f10',self.acceptExoTask,[pl])
		self.accept('f11',self.removeExoTask,[pl])
		
		# taskMgr.add(pl.CommandListenerTask, "keytask")
		
	def acceptExoTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.addExoTask,'addExoTask', extraArgs = [pl,'keyboard',""])
		
	def removeExoTask(self,pl):
		### Temporary function for testing ###
		taskMgr.add(pl.removeExoTask,'removeExoTask', extraArgs = [pl,'last'])
		
		
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
		
	def create_exo_model(self):
		''' Function that loads an exo model '''
		# Load models
		data = {}
		data['exo'] = loader.loadModel('models/exo3_base.egg')
		data['arm_rest'] = loader.loadModel('models/exo3_arm_rest.egg')
		data['prono'] = loader.loadModel('models/exo3_prono.egg')
		data['fthumb'] = loader.loadModel('models/exo3_fthumb.egg')
		data['fgroup'] = loader.loadModel('models/exo3_fgroup.egg')
		data['findex'] = loader.loadModel('models/exo3_findex.egg')
	
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
		
app = MyApp()
app.run()