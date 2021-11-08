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
    
    def __init__(self, rot_motor, lens_motor, led_motor, sipm_motor, scope, align_file=None):
        self.rot_motor = rot_motor
        self.lens_motor = lens_motor
        self.led_motor = led_motor
        self.sipm_motor = sipm_motor
        self.scope = scope
        
        if align_file:
            pass
        else:
            self.sipm_center = 117.37 #  mm 
            self.led_center = 170.41 # mm 
            self.lens_center = 155.37 # lens centered to LED in mm
            self.lens_diam = 4.90*2. # diameter of lens in mm
            self.rot_center = 0 
            self.num_sweeps = 15
        
        # We only have enough power for 3 motors, so
        # switch power between these motors to use and
        # change rot_or_led to either 'rot' or 'led'
        self.rot_or_led_on = 'rot' 
        
    def PrintInfo(self):
        print('---Experiment---')
        self.lens_motor.PrintInfo()
        print('    Center: '+str(self.lens_center))
        print('    Diam: '+str(self.lens_diam))
        self.sipm_motor.PrintInfo()
        print('    Center: '+str(self.sipm_center))
        if self.rot_or_led_on == 'rot':
            self.rot_motor.PrintInfo()
            print('    Center: '+str(self.rot_center))
            print('LED motor off')
        else:
            self.led_motor.PrintInfo
            print('    Center: '+str(self.led_center))
            print('Rotation motor off')
        print('Oscilloscope: '+self.scope.query('*IDN?'))
        print('    Number of Sweeps: '+str(self.num_sweeps))
        
    def Set_sweeps(self, num_sweeps):
        self.num_sweeps = num_sweeps
        return
    
    def Set_grating_led_pos(self, grating_led_pos):
        self.grating_led_pos = grating_led_pos
        return
        
    def Set_height(self, height):
        self.height = height
        return
        
    def Set_led_x(self, led_x):
        self.led_x = led_x
        return
        
    def SwitchMotor(self, motor_name):
        """
        Switches which of the rot or led motor
        is currently powered.
        """
        print('Manually connect '+motor_name+' motor and disconnect '+self.rot_or_led_on+' motor')
        self.rot_or_led_on = motor_name
        return
    
    def ScanLens(self, width=40., num_measurements=200):
        """
        Scans the peaks while moving the lens. Assums lens is 
        centered
        """

        distance_to_move = width/num_measurements
        maxes = []
        positions_lens = []
        self.lens_motor.MoveMotor(-width/2.)
        for i in range(num_measurements):
            clear_output(wait=True)
            display(str(i+1)+"/"+str(num_measurements))

            self.lens_motor.MoveMotor(distance_to_move)
            positions_lens.append(self.lens_motor.GetCurrentPosition())

            maxes.append(MeasurePeaktoPeak(self.scope, self.num_sweeps))
        self.lens_motor.MoveMotor(-width/2.)

        return positions_lens, maxes
    
    def ScanLED(self, width_led=12., width_lens=12., num_measurements_led=20, num_measurements_lens=20):
        """
        Scans the led across the lens, while scanning the lens across the led at each position of the led.
        Assumes everything centers initially.
        """

        dist_move_led = width_led/num_measurements_led
        self.led_motor.MoveMotor(-width_led/2.)
        self.lens_motor.MoveMotor(-width_lens/2.)
        led_data = []
        for step_led in range(num_measurements_led):
            clear_output(wait=True)
            display('LED step: '+str(step_led+1)+"/"+str(num_measurements_led))

            positions_lens, maxes = self.ScanLens(width_lens, num_measurements_lens)
            led_data.append([positions_lens, maxes, self.led_motor.GetCurrentPosition()])
            self.led_motor.MoveMotor(dist_move_led)
        self.led_motor.MoveMotor(-width_led/2.)
        self.lens_motor.MoveMotor(width_lens/2.)
        
        return led_data
    
    def FindSiPMCenter(self, width=20., num_measurements=100):
        """
        Moves the lens away from the center, scans the sipm across
        the led and finds the center position of the SiPM. 
        """
        self.lens_motor.MoveMotor(-40)
        position_led, positions_sipm, maxes = self.ScanMaxes(width, num_measurements)
        self.lens_motor.MoveMotor(40)
        plt.plot(positions_sipm, maxes)
        
        print('Old SiPM center = '+str(self.sipm_center))
        self.sipm_center = positions_sipm[np.argmax(np.array(maxes))]
        print('New SiPM center = '+str(self.sipm_center))
        
        return position_led, positions_sipm, maxes
    
    def FindMountCenter(self, positions_lens, maxes, width=4, prominence=0.02):
        """
        Calls ScanLens to measure the signal as you scan the lens across the LED
        and finds the diameter of the mount.
        """
       
        peaks, _ = signal.find_peaks(np.array(maxes)*-1, width=width, prominence=prominence)
        widths = signal.peak_widths(np.array(maxes)*-1, peaks)
        [print('Mount edges', positions_lens[int(widths[2][peak])], positions_lens[int(widths[3][peak])]) for peak in range(len(peaks))]

        if len(peaks) > 1:
            left_edge = positions_lens[int(widths[3][0])]
            right_edge = positions_lens[int(widths[2][1])]
        
            print('Mount diameter = '+str(right_edge - left_edge))
            print('Mount center = '+str(right_edge - (right_edge - left_edge)/2))
        else:
            print('Could not find enough peaks')
        
        return 
    
    def FindLensCenter(self, positions_lens, maxes, prominence=0.02):
        """
        Finds the center of the lens, by finding the two peaks 
        corresponding to the glass around the edge and of the
        lens and calculating the center. 
        """
        
        peaks, _ = signal.find_peaks(np.array(maxes),prominence=prominence)
        widths = signal.peak_widths(np.array(maxes), peaks)
        [print('Peak edges', positions_lens[int(widths[2][peak])], positions_lens[int(widths[3][peak])]) for peak in range(len(peaks))]

        if len(peaks) > 1:
            peak1_right = positions_lens[int(widths[3][0])]
            peak2_left = positions_lens[int(widths[2][-1])]

            print('Old values: Lens width = '+str(self.lens_diam)+', lens center =  '+str(self.lens_center))
            self.lens_diam = (peak2_left - peak1_right)
            self.lens_center = (peak2_left + peak1_right)/2.
            print('New values: Lens width = '+str(self.lens_diam)+', lens center =  '+str(self.lens_center))
        else:
            print('Could not find enough peaks')
            
        return 
    
    def FindLEDCenter(self, led_data, prominence):
        """
        Calls ScanLED to measure the signal as you scan across the edge of the lens
        and finds the center position of the lens for the LED, and sets the global 
        variable of the led_center.
        """
        
        left_edges = []
        right_edges = []
        led_positions = []
        for step in led_data:
            positions_lens = step[0]
            maxes = step[1]
            led_position = step[2]

            # Find peak
            peaks, _ = signal.find_peaks(np.array(maxes), prominence=prominence)
            widths = signal.peak_widths(np.array(maxes), peaks)

            if len(peaks) > 0:
                left_edges.append(positions_lens[int(widths[2][0])])
                right_edges.append(positions_lens[int(widths[3][0])])
                led_positions.append(led_position)

        plt.plot(led_positions, left_edges, 'o', label='left')
        plt.plot(led_positions, right_edges, 'o', label='right')
        plt.legend()
        plt.xlabel('LED position [mm]')
        plt.ylabel('Edge of mount position [mm]')
        plt.show()
        
        print('Old LED center = '+str(self.led_center))
        self.led_center = led_positions[np.argmin(right_edges)]
        print('New LED center = '+str(self.led_center))
        
        return

    def Align(self):
        """
        Align the sipm, lens, and led to center
        """
        self.sipm_motor.MoveMotor(self.sipm_center - self.sipm_motor.GetCurrentPosition())
        self.led_motor.MoveMotor(self.led_center - self.led_motor.GetCurrentPosition())
        
        if self.rot_or_led_on == 'led':
            self.lens_motor.MoveMotor(self.lens_center - self.lens_motor.GetCurrentPosition())
            print('Rotation motor is off. Switch motors to align')
        else:
            self.rot_motor.MoveMotor(self.rot_center - self.rot_motor.GetCurrentNumSteps())
            print('LED motor is off. Switch motors to align')

        return

    def ResetZero(self):
        """
        Writes the positions as zero. This is for
        a hard reset of the positions in case of
        skipping motors and incorrect position output. 
        """
        # Unplug motors and move them to bottom first
        print('Unplug motors and move them to the bottom or front of box')
        self.lens_motor.WriteNewNumSteps(0)
        self.led_motor.WriteNewNumSteps(0)
        self.rot_motor.WriteNewNumSteps(0)
        self.sipm_motor.WriteNewNumSteps(0)

        return
    
    def Reset(self):
        """
        Resets the lens and sipm motors to align at the 
        top of the poles. The buttons will align them 
        10mm below the push button. 
        """
        self.lens_motor.MoveMotor(250.)
        self.sipm_motor.MoveMotor(250.)
        return
    
    def ScanMaxes(self, width=40., num_measurements=200, align_to=None):
        """
        Scan the max signal across the sipm with and without
        the diffraction grating. 
        """     
        # Align and measure
        if align_to:
            self.Align(align_to)
        self.sipm_motor.MoveMotor(-width/2.)

        # Measure voltage at each distance
        distance_to_move = width/num_measurements
        maxes = []
        positions_sipm = []
        position_led = self.led_motor.GetCurrentPosition()
        for i in range(num_measurements):
            clear_output(wait=True)
            display(str(i+1)+"/"+str(num_measurements))
            self.sipm_motor.MoveMotor(distance_to_move)
            maxes.append(MeasurePeaktoPeak(self.scope, self.num_sweeps))
            positions_sipm.append(self.sipm_motor.GetCurrentPosition())
        self.sipm_motor.MoveMotor(-width/2.)
            
        return position_led, positions_sipm, maxes
    
  