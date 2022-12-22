"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)
Daet: 2021

This class controls defines the functions available
to align the motors in the
diffraction lens black box experiment. 
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
    
    def __init__(self, sipm_motor, led_motor, scope):
        self.sipm_motor = sipm_motor
        self.led_motor = led_motor
        self.scope = scope
        
        self.grating_led_pos = 70. # LED position for alignment with grating
        self.below_grating_led_pos = 67 # LED position for alignment below grating
        self.below_mount_led_pos = 45 # LED position for alignment below grating
        self.sipm_offset = 13.86 #14.355 # Difference in height between SiPM and LeD for direct alignment. LED is lower.
        self.num_sweeps = 15
        
    def Set_sweeps(self, num_sweeps):
        self.num_sweeps = num_sweeps
        return
    
    def Set_sipm_offset(self, sipm_offset):
        self.sipm_offset = sipm_offset
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
        Moves them to align with the diffraction grating and saves 
        the position in the cvs file, if to_lens=True, else aligns
        the sipm and led away from the diffraction grating.

        inputs
            align_to (str): Align the LED and sipm to the diffraction
                grating ('grating'), the substrate without the grating 
                ('below_grating'), or below the mount ('below_mount')
        """


        sipm_pos = self.sipm_motor.GetCurrentPosition()
        led_pos = self.led_motor.GetCurrentPosition()

        if align_to=='grating':
            self.led_motor.MoveMotor(self.grating_led_pos-led_pos)
            self.sipm_motor.MoveMotor(self.grating_led_pos+self.sipm_offset-sipm_pos)
        elif align_to=='below_grating':
            self.led_motor.MoveMotor(self.below_grating_led_pos-led_pos)
            self.sipm_motor.MoveMotor(self.below_grating_led_pos+self.sipm_offset-sipm_pos)
        elif align_to=='below_mount':
            self.led_motor.MoveMotor(self.below_mount_led_pos-led_pos)
            selfsipm_motor.MoveMotor(self.below_mount_led_pos+self.sipm_offset-sipm_pos)
        else:
            print("Incorrect input for align_to (options: 'grating', 'below_grating', 'below_mount')")

        return


    def GetAlignment(self):
        """
        Run this after a change to the setup to get the new offset between SiPM and LED.
        Set both to bottom then move SiPM up 40mm to have it move across the LED. 
        The peak position represents the offset

        inputs
            sipm_motor (Motor class object)
            led_motor (Motor class object)
        returns
            SIPM_OFFSET
        """
        self.sipm_motor.SetToZero()
        self.led_motor.SetToZero()
        self.sipm_motor.MoveMotor(self.below_mount_led_pos)
        self.led_motor.MoveMotor(self.below_mount_led_pos)
        distance_to_move = 30.
        distance_per_step = 0.5
        num_steps = int(distance_to_move/distance_per_step)
        maxes = []
        positions = []
        steps = []
        # Measure voltage at each step
        for i in range(num_steps):
            self.sipm_motor.MoveMotor(distance_per_step)
            max = MeasurePeaktoPeak(self.scope, self.num_sweeps)
            maxes.append(max)
            current_position = sipm_motor.GetCurrentPosition()
            current_steps = sipm_motor.GetCurrentNumSteps()
            clear_output(wait=True)
            display(str(i+1)+"/"+str(num_steps)+": "+str(current_position)+" ("+str(max)+")")
            positions.append(current_position)
            steps.append(current_steps)


        # Locate the peak and set the offset value as a global variable
        rel_positions = np.array(positions) - positions[0]
        plt.plot(rel_positions,maxes)
        plt.xlabel("Position of SiPM relative to LED (mm)")
        NoGrating_peaks, _ = signal.find_peaks(maxes, prominence=0.05)
        NoGrating_widths = signal.peak_widths(maxes, NoGrating_peaks)
        l = rel_positions[int(NoGrating_widths[2][0])]
        r = rel_positions[int(NoGrating_widths[3][0])]
        NoGrating_peak_pos = (r + l)/2
        plt.axvline(NoGrating_peak_pos,color="r")
        print('Before:',self.sipm_offset)
        self.sipm_offset = abs(NoGrating_peak_pos)
        print('New sipm offset: ',self.sipm_offset)

        return

    def ResetZero(self):
        """
        Writes the positions as zero. This is for
        a hard reset of the positions in case of
        skipping motors and incorrect position output. 
        """
        # Unplug motors and move them to bottom first
        print('Unplug motors and move them to the bottom')
        self.sipm_motor.WriteNewNumSteps(0)
        self.led_motor.WriteNewNumSteps(0)

        return
    
    def Reset(self):
        """
        Resets the motors to align at the top of the poles. 
        The buttons will align them 10mm below the push button. 
        """
        self.sipm_motor.MoveMotor(250.)
        self.led_motor.MoveMotor(250.)
        return
    
    def ScanMaxes(self, width=40., num_measurements=200, align_to='grating'):
        """
        Scan the max signal across the sipm with and without
        the diffraction grating and save to a file. 
        """     
        # Align and measure
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

        return position_led, positions_sipm, maxes
    
    def Run_Voltage_v_Intensity(dV=0.1, file_name='new_V_v_I.csv'):
        """
        A run that increased the voltage by dV (currently must
        be done by hand), and plots led voltage versus
        sipm intensity.
        """
        # Run to check voltage to intensity
        self.Align(align='grating')
        num_measurements = 100
        values = []
        for i in range(num_measurements):
            clear_output(wait=True)
            display(str(i+1)+"/"+str(num_measurements))
            values.append(MeasurePeaktoPeak(scope, num_sweeps))
            time.sleep(2)

        plt.plot([dV*(i+1) for i in range(num_measurements)], values)
        plt.xlabel('LED Voltage')
        plt.ylabel('SiPM Max Voltage')

        with open('data/'+file_name, mode='w') as file:
            writer = csv.writer(file)

            writer.writerow(['50ns width'])
            writer.writerow([0.1*(i+1) for i in range(num_measurements)])
            writer.writerow(values_50ns)

            writer.writerow(['250ns width'])
            writer.writerow([0.1*(i+1) for i in range(num_measurements)])
            writer.writerow(values_250ns)

        return

    def Run(self, file_name, voltage=5.0):
        """
        This function takes two data sets, measuring the peak
        intensity of the sipm over a given width centered at 
        the grating and below the grating.
        """

        width = 60.0 # mm
        num_measurements = 150 #300 
        # Create the file to hold the array of max signals
        with open('data/'+file_name, mode='w') as file:
            writer = csv.writer(file)

            print("With grating")
            position_led_g, positions_sipm_g, maxes_g = self.ScanMaxes(width, num_measurements, align_to='grating')
            writer.writerow(['with grating'])
            writer.writerow([position_led_g])
            writer.writerow(positions_sipm_g)
            writer.writerow(maxes_g)

            print('Below grating')
            position_led_bg, positions_sipm_bg, maxes_bg = self.ScanMaxes(width, num_measurements, align_to='below_grating')
            writer.writerow(['below grating'])
            writer.writerow([position_led_bg])
            writer.writerow(positions_sipm_bg)
            writer.writerow(maxes_bg)

    #         print('Below mount')
    #         position_led_bm, positions_sipm_bm, maxes_bm = ScanMaxes(width, num_measurements, align_to='below_mount')
    #         writer.writerow(['below mount'])
    #         writer.writerow([position_led_bm])
    #         writer.writerow(positions_sipm_bm)
    #         writer.writerow(maxes_bm)

            print('Saving Global Variables')
            writer.writerow(['Grating LED Position', self.grating_led_pos])
            writer.writerow(['Below Grating LED Position', self.below_grating_led_pos])
            writer.writerow(['Below Mount LED Position', self.below_mount_led_pos])
            writer.writerow(['Voltage', voltage])

        halfway = len(positions_sipm_g)//2
        plt.plot(np.array(positions_sipm_bg)-self.below_grating_led_pos, maxes_bg, label='below grating')
        plt.plot(np.array(positions_sipm_g)-self.grating_led_pos, maxes_g, label='with grating')
    #     plt.plot(np.array(positions_sipm_bm)-BELOW_MOUNT_LED_POSITION, maxes_bm, label='below mount')
        plt.legend()
        plt.ylabel('Max Voltage [V]')
        plt.xlabel('SiPM Position [mm]')

        return