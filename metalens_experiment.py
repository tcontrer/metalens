"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)
Daet: 2021

This class controls defines the functions avaible
to align the motors in the
metalens black box experiment. 
"""

from motor import Motor
import matplotlib.pyplot as plt
from scipy import signal
from oscilloscope import MeasurePeaktoPeak
import csv
import time
from IPython.display import display, clear_output
import numpy as np

class Experiment:
    
    def __init__(self, rot_motor, lens_motor, led_motor, scope):
        self.rot_motor = rot_motor
        self.lens_motor = lens_motor
        self.led_motor = led_motor
        self.scope = scope
        
        self.grating_led_pos = 70. # LED position for alignment with grating
        self.below_grating_led_pos = 67 # LED position for alignment below grating
        self.below_mount_led_pos = 45 # LED position for alignment below grating
        self.num_sweeps = 15
        
    def Set_sweeps(self, num_sweeps):
        self.num_sweeps = num_sweeps
        return
    
    def Set_grating_led_pos(self, grating_led_pos):
        self.grating_led_pos = grating_led_pos
        return
    
    def Set_below_grating_led_pos(self, below_grating_led_pos):
        self.below_grating_led_pos = below_grating_led_pos
       
    def Set_below_mount_led_pos(self, below_mount, led_pos):
        self.below_mount_led_pos = below_mount_led_pos
        
    def Align(self, align_to='grating'):
        """
        """

        return


    def GetAlignment(self):
        """
        """
        return

    def ResetZero(self):
        """
        Writes the positions as zero. This is for
        a hard reset of the positions in case of
        skipping motors and incorrect position output. 
        """
        # Unplug motors and move them to bottom first
        print('Unplug motors and move them to the bottom')
        self.lens_motor.WriteNewNumSteps(0)
        self.led_motor.WriteNewNumSteps(0)

        return
    
    def Reset(self):
        """
        Resets the motors to align at the top of the poles. 
        The buttons will align them 10mm below the push button. 
        """
        self.lens_motor.MoveMotor(250.)
        self.led_motor.MoveMotor(250.)
        return
    
  