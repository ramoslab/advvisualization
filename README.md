# Readme file for the code of the advanced visualisation

In order to understand the code it might be necessary to read at least the
introduction of the documentation of the Panda3D engine (www.panda3d.org).
The script advtcp_commandclient.py can be used to send TCP commands to the
program. The commands are explained in adv_command_structure.txt.
In order to run the code the use of the Panda3D SDK is necessary.
In order to run the packaged version of the code the Panda3D Runtime is
necessary.

The main code consists of two files: advmain.py and advclasses.py

advmain.py contains all the code necessary to start up the visualisation
system and the main loop of the program.

advclasses.py contains the program logic, i.e. the logic that reads commands
from TCP, creates, controls and deletes entities in the visualisation (e.g.
the exos, the mat, the camera).

The code containts comments that should explain the responsibilities of
each code segment.

The large code file is separated into three segments: Logic controllers, data
controllers and the program logic.

The logic controllers are classes that represent the entities in the
visualisation scene (i.e. the exos, the mat, the camera). There is a logic
controller superclass and a logic class for each type of exo that inherits from the
superclass. These classes have fields that specify a model (i.e. the actual 3D
representation of the entity that is rendered on the screen) and a data
controller for each exo type.
The other logic controllers control the mat and the camera.

A data controller takes care of the behaviour of an entity in the scene. The
ExoDataControllerKeyboard, for instance, moves the exo that it belongs to
according to keyboard input.

The program logic is a large class that handles reading the commands sent via
TCP and creates, controls, modifies and deletes exos in the scene accordingly.
Furthermore, it manipulates mat and camera.
All commands are encapsulated in Tasks, which is a class of the Panda3D
engine. The engine has an integrated task manager. It is highly recommended to
use the internal task manager because of stability.

Reading the code from this class would probably be a good
starting point.
