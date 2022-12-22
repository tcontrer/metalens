This repository includes tutorials, testing notebooks, classes, and notebooks 
relevant for the metalens dark box experiment at Harvard. 
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu). 
    
Class files: 
    - motor.py: a class to control a motor using python and an arduino. Has 
          functions to monitor and move positions, run a certain number of 
          steps, write position to a file
    - oscilloscope.py: a class to control the oscilloscope with python (pyvisa)
          and take data for the SiPM. 
    - experiment.py: a class to control a sipm motor, diffractiong grating
          motor, and led motor, aligning these motors and controling the 
          oscilliscope, and has functions for data taking runs
    - metalens_experiment.py: a class to control a sipm motor, metalens motor,
         metalens rotation motor, led motor, aligning these motors and controling 
         the oscilliscope, and has functions for data taking runs
    - metaslaens_experiment_power.py: a class to control a power meter motor,
         metalens motor, metalens rotation motor, led motor, aligning these 
         motors and controling the power meter, and has functions for data 
         taking runs
    
Tutorial notebooks:
    - tutoriol_arduino.ipynb: For testing control of the arduino with python within 
          jupyter notebook, has a blinking LED example
    - tutorial_pyvisa.ipynb: For a short tutorial on controling the oscilloscope 
          with python using pyvisa
    - tutorial_motor.ipynb: For testing control of a motor using the arduino and python
    - tutorial_powrmeter.ipynb: For testing the use of the power meter with python    
    
Data taking and analysis notebooks:
    - Automation_diffractionlens.ipynb: Sets up the experiment with a diffraction grating
          by setting up oscilliscope and motors and performing data runs, using the
          experiment.py class
    - Automation_metalens.ipynb: Sets up the experiment with a metalens
          by setting up oscilliscope and motors and performing data runs, using the
          metalens_experiment.py class.
    - Automation_metalens_powermeter.ipynb: Sets up the experiment with a metalens
          by setting up the power meter and motors and performing data runs, using the
          metalens_experiment_power.py class.
    - Automation_sipm_linearity.ipynb: Sets up the experiment with a diffractiion grating
          by setting up the oscilloscope and motors and performing data runs, using the
          experiment.py class to meaure the sipm linearity.
          
Analysis notebooks (/analysis/)
    - DiffractionStudy_Analysis.ipynb: analyzes data taken by 
          Automation_diffractionlens.ipynb
    - Metalens_Analysis.ipynb: analyzes data taken by Automation_metalens.ipynb
    - Linearity_Analysis.ipynb: analyzed data taken by Automation_sipm_linearity.ipynb

