This repository includes tutorials, testing notebooks, classes, and notebooks relevant for the metalens dark box experiment at Harvard. Written by: Taylor Contreras (taylorcontreras@g.harvard.edu). 

Tutorial notebooks:
    - Arduino_testing.ipynb: For testing control of the arduino with python within jupyter notebook, has a blinking LED example
    - PyVisa_tutorial.ipynb: For a short tutorial on controling the oscilloscope with python using pyvisa
    - Motor_control_testing.ipynb: For testing control of a motor using the arduino and python
    
Class files: 
    - motor.py: a class to control a motor using python and an arduino. Has functions to monitor and move positions, run a certain number of steps, etc.
    - oscilloscope.py: a class to control the oscilloscope with python (pyvisa). 
    - experimet.py: a class to control motors set up for the metalens experiment, the oscilliscope, and has functions for data taking runs
    
Data taking and analysis notebooks:
    - DiffractionStudy_Automation_new.ipynb: Sets up the metalens experiment 'experiment' class by setting up oscilliscope and motors and perfomring data runs
    - DiffractionStudy_Analysis.ipynb: analyzes data taken by DiffractionStudy_Automation_new.ipynb