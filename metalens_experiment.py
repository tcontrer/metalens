"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)
Daet: 2021

This class controls defines the functions avaible
to align the motors in the
metalens black box experiment with a SiPM. 
"""

from motor import Motor
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit
from oscilloscope import MeasurePeaktoPeak
import csv
import time
from IPython.display import display, clear_output
import numpy as np

class Experiment:
    
    def __init__(self, rot_motor, lens_motor, led_motor, sipm_motor, scope, align_with_file=False):
        self.rot_motor = rot_motor
        self.lens_motor = lens_motor
        self.led_motor = led_motor
        self.sipm_motor = sipm_motor
        self.motor_dict = {'rot':self.rot_motor, 'lens':self.lens_motor, 'led':self.led_motor, 'sipm':self.sipm_motor}
        self.scope = scope
        self.motor_dtheta = 1.8/8.
        self.num_sweeps = 15
        
        if align_with_file:
            self.alignments = {}
            with open('motor_positions/alignment.csv', 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == 'rot_center':
                        self.alignments[row[0]] = int(row[1])
                    else:
                        self.alignments[row[0]] = float(row[1])
        else:
            self.alignments = {'sipm_center': 117.37,
                                 'led_center': 161.0,
                                 'lens_center': 176.39,
                                 'lens_diam': 9.8,
                                 'mount_center': 177.0,
                                 'mount_left_outer_edge': 164.49,
                                 'mount_left_inner_edge': 170.69,
                                 'mount_diam': 10.6,
                                 'rot_center': 0}
        
    def PrintInfo(self):
        print('---Experiment---')
        self.lens_motor.PrintInfo()
        self.sipm_motor.PrintInfo()
        
        if self.GetRotOrLED() == 'rot':
            self.rot_motor.PrintInfo()
            print('LED motor off')
        else:
            self.led_motor.PrintInfo
            print('Rotation motor off')
            
        print('--Alignments--')
        for key in self.alignments:
            print('    '+key+' = '+str(self.alignments[key]))

        print('Oscilloscope: '+self.scope.query('*IDN?'))
        print('    Number of Sweeps: '+str(self.num_sweeps))
        
    def Set_sweeps(self, num_sweeps):
        self.num_sweeps = num_sweeps
        return
        
    def GetRotOrLED(self):
        # We only have enough power for 3 motors, so
        # switch power between these motors to use and
        # change rot_or_led to either 'rot' or 'led'
        
        rows = []
        with open('motor_positions/rot_or_led_on.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)
        return rows[0][0]
    
    def SwitchMotor(self, motor_name):
        """
        Switches which of the rot or led motor
        is currently powered.
        """
        print('Manually connect '+motor_name+' motor and disconnect '+self.GetRotOrLED()+' motor')
        with open('motor_positions/rot_or_led_on.csv', 'w', newline='') as file:
            file.truncate()
            writer = csv.writer(file)
            
            writer.writerow([motor_name])

        return
        
        return
    
    def WriteAlignment(self):
        with open('motor_positions/alignment.csv', 'w', newline='') as file:
            file.truncate()
            writer = csv.writer(file)
    
            for key in self.alignments:
                writer.writerow([key, self.alignments[key]])
        return
    
    def MoveMotor(self, motor_name, distance):
        """
        Moves the motor motor_name a distance, checking
        if motor_name is the led that the led is on. 
        """
        
        if motor_name == 'led':
            if self.GetRotOrLED() == 'led':
                self.led_motor.MoveMotor(distance)
            else:
                print('led motor is off. Switch power manually and use SwitchMotor')
        elif motor_name == 'rot':
            print('rot motor is for rotations. Use Rotate()')
        else:
            self.motor_dict[motor_name].MoveMotor(distance)
        return
    
    def RotateLens(self, degrees):
        """
        Rotates the lens, checking that the rotation
        motor has powered. 
        """
        
        if self.GetRotOrLED() == 'rot':
            self.rot_motor.Rotate(degrees)
        else:
            print('rot motor is off. Switch power manually and use SwitchMotor()')
        return  
    
    def ScanLens(self, width=40., num_measurements=200, print_progress=True):
        """
        Scans the peaks while moving the lens. Assums lens is 
        centered
        """

        distance_to_move = width/num_measurements
        maxes = []
        positions_lens = []
        self.lens_motor.MoveMotor(-width/2.)
        for i in range(num_measurements):
            if print_progress:
                clear_output(wait=True)
                display(str(i+1)+"/"+str(num_measurements))
                if i > 0:
                    plt.plot(positions_lens, maxes)
                    plt.title('ScanLens Scanning Progress')
                    plt.show()

            self.lens_motor.MoveMotor(distance_to_move)
            positions_lens.append(self.lens_motor.GetCurrentPosition())

            maxes.append(MeasurePeaktoPeak(self.scope, self.num_sweeps))
        self.lens_motor.MoveMotor(-width/2.)

        clear_output()

        return positions_lens, maxes
    
    def ScanLED(self, width_led=12., width_lens=12., num_measurements_led=20, num_measurements_lens=20, print_progress=True):
        """
        Scans the led across the lens, while scanning the lens across the led at each position of the led.
        Assumes everything is centered initially.
        """
        if self.GetRotOrLED() == 'rot':
            print('led motor is off. Use SwitchMotor and switch power manually')
            return
        
        dist_move_led = width_led/num_measurements_led
        self.led_motor.MoveMotor(-width_led/2.)
        #self.lens_motor.MoveMotor(-width_lens/2.)
        led_data = []
        for step_led in range(num_measurements_led):
            if print_progress:
                clear_output(wait=True)
                display('LED step: '+str(step_led+1)+"/"+str(num_measurements_led))

            positions_lens, maxes = self.ScanLens(width_lens, num_measurements_lens, print_progress=False)
            led_data.append([positions_lens, maxes, self.led_motor.GetCurrentPosition()])
            self.led_motor.MoveMotor(dist_move_led)
            
        self.led_motor.MoveMotor(-width_led/2.)
        #self.lens_motor.MoveMotor(width_lens/2.)
        
        return led_data
    
    def ScanRotation(self, scan_degrees, num_steps, print_progress=True):
        """
        Measures the SiPM signal across a number of rotation of the lens.
        """
        
        if self.GetRotOrLED() == 'led':
            print('rot motor is off. Use SwitchPower and switch power manually')
            return 
        
        # Round degrees so we take a whole number of steps
        dtheta = ((scan_degrees/num_steps) // self.motor_dtheta) * self.motor_dtheta
        scan_degrees = dtheta * num_steps

        self.rot_motor.Rotate(-scan_degrees/2.)
        rot_data = []
        for step in range(num_steps):
            if print_progress:
                clear_output(wait=True)
                display('Rot step: '+str(step+1)+"/"+str(num_steps))

            rot_data.append([self.rot_motor.GetCurrentNumSteps(), MeasurePeaktoPeak(self.scope, 10)])
            self.rot_motor.Rotate(dtheta)
        self.rot_motor.Rotate(-scan_degrees/2.)
        
        return np.array(rot_data)
    
    def FindSiPMCenter(self, width=20., num_measurements=100):
        """
        Moves the lens away from the center, scans the sipm across
        the led and finds the center position of the SiPM. 
        """
        self.lens_motor.MoveMotor(-40)
        position_led, positions_sipm, maxes = self.ScanMaxes(width, num_measurements)
        self.lens_motor.MoveMotor(40)
        plt.plot(positions_sipm, maxes)
        
        print('Old SiPM center = '+str(self.alignments['sipm_center']))
        self.alignments['sipm_center'] = positions_sipm[np.argmax(np.array(maxes))]
        print('New SiPM center = '+str(self.alignments['sipm_center']))
        
        self.WriteAlignment()
        
        return position_led, positions_sipm, maxes
    
    def FindLensData(self, positions_lens, maxes, width=4, prominence=0.02):
        """
        Finds the negative peaks due to the edges of the mount, 
        calculates the center and diameter of the mount, and 
        returns the data only between the mount edges.
        """
        peaks, _ = signal.find_peaks(np.array(maxes)*-1, width=width, prominence=prominence)
        widths = signal.peak_widths(np.array(maxes)*-1, peaks)
        [print('Mount edges', positions_lens[int(widths[2][peak])], positions_lens[int(widths[3][peak])]) for peak in range(len(peaks))]

        if len(peaks) > 1:
            left_edge = positions_lens[int(widths[3][0])]
            right_edge = positions_lens[int(widths[2][1])]
            self.alignments['mount_left_outer_edge'] = positions_lens[int(widths[2][0])]

        else:
            print('Could not find enough peaks')
            
        self.WriteAlignment()
        
        return positions_lens[int(widths[2][0])+5:int(widths[3][-1])-5], maxes[int(widths[2][0])+5:int(widths[3][-1])-5]
    
    def FindLensCenter(self, lens_data, mount_prominence=0.05, glass_prominence=0.01):
        """
        Finds the center of the lens, by finding the two peaks 
        corresponding to the glass around the edge and of the
        lens and calculating the center. 
        """

        lens_data = np.array(lens_data)
        der = np.diff(lens_data[1]) / np.diff(lens_data[0])
        positions_lens2 = (lens_data[0][:-1] + lens_data[0][1:]) / 2

        peaks, _ = signal.find_peaks(abs(der), prominence=mount_prominence)
        widths = signal.peak_widths(abs(der), peaks)
        if len(peaks) > 0:
            left_edge = positions_lens2[int(widths[2][0])]
            right_edge = positions_lens2[int(widths[2][-1])]
            center_index = int((int(widths[2][0]) + int(widths[2][-1]))/2)

            left_data = lens_data[:,0:center_index-5]
            right_data = lens_data[:,center_index+5:]
        else:
            print('Could not find enough peaks')
            return

        peaks, _ = signal.find_peaks(left_data[1], prominence=glass_prominence)
        widths = signal.peak_widths(left_data[1], peaks)
        if len(peaks) > 0:
            lens_left_edge = left_data[0][int(widths[3][0])]
            self.alignments['mount_left_inner_edge'] = left_data[0][int(widths[2][0])]
        else:
            print('Could not find enough peaks for left edge')
            return

        peaks, _ = signal.find_peaks(right_data[1], prominence=glass_prominence)
        widths = signal.peak_widths(right_data[1], peaks)
        if len(peaks) > 0:
            lens_right_edge = right_data[0][int(widths[2][-1])]
        else:
            print('Could not find enough peaks for right edge')
            return

        lens_center = (lens_left_edge + lens_right_edge) / 2.
        self.alignments['lens_center'] = lens_center

        plt.plot(lens_data[0], lens_data[1], label='data')
        plt.vlines(lens_left_edge, 0,.15, color='r', label='lens edges')
        plt.vlines(lens_right_edge, 0, .15, color='r')
        plt.vlines(lens_center, 0, .15, color='y', label='lens_center')
        plt.xlabel('Lens position [mm]')
        plt.ylabel('SiPM signal [V]')
        plt.legend()
        plt.show()
        
        self.WriteAlignment()

        return 
    
    def FindLEDCenter(self, led_data, prominence=0.02, guess=[5., 163., 180.]):
        """
        Aligns the LED to the center of the lens by finding the left
        edges of the lens at different led positions from led_data,
        fitting a circle and finding the LED center. 

        Input:
            led_data: array of ???
            prominence: prominence of glass peak
            guess: array of guesses for fit 
                [radius, led center position, lens center position]
        """

        lens_edges = []
        led_positions = []
        for step in led_data:
            positions_lens = step[0]
            maxes = step[1]
            led_position = step[2]

            # Find peak
            peaks, _ = signal.find_peaks(np.array(maxes), prominence=prominence)
            widths = signal.peak_widths(np.array(maxes), peaks)

            if len(peaks) > 0:
                lens_edges.append(positions_lens[int(widths[3][0])])
                led_positions.append(led_position)

        def Circle(x, r, a, b):
            return b - np.sqrt(abs(r**2. - (x-a)**2.))

        popt, pcov = curve_fit(Circle, np.array(led_positions), lens_edges, guess)
        x = np.linspace(led_positions[0], led_positions[-1], 10)
        plt.plot(x, Circle(x, *popt), label='fit')      
        plt.plot(led_positions, lens_edges, 'o', label='data')
        plt.legend()
        plt.xlabel('LED position [mm]')
        plt.ylabel('Edge of lens position [mm]')
        plt.show()

        print('LED Center = '+str(popt[1]))
        self.alignments['led_center'] = popt[1]
        
        self.WriteAlignment()
        
        return
    
    def FindLensRotationAlignment(self, rot_data, prominence):
        """
        Calls ScanRotation to rotate the lens, measuring the SiPM signal at each step.
        The signal will dip as the lens rotates so that the edges stick out in front
        of the LED, but will peak again once the lens is rotated enough. This function
        finds the center position of the center peak, corresponding to the edges 
        blocking the LED, and calculates the 0 degree alignment. 
        """
        
        rot_data = np.array(rot_data)
        peaks, _ = signal.find_peaks(rot_data[:,1]*-1, prominence=prominence)
        widths = signal.peak_widths(rot_data[:,1]*-1, peaks)

        step_positions = rot_data[:,0]
        angles = (rot_data[:,0] - rot_data[len(rot_data[:,0])//2,0])*(1.8/8.)
        
        if len(peaks) == 2:
            center_step = int((step_positions[int(widths[3][0])] + step_positions[int(widths[2][1])])/2)
            current_step = self.rot_motor.GetCurrentNumSteps()
            self.rot_motor.MoveSteps(center_step - self.rot_motor.GetCurrentNumSteps())
            self.alignments['rot_center'] = center_step
            print('Rotated '+str((current_step - center_step)*(1.8/8.))+' to align')
        else:
            print("Couldn't find correct peaks")
            return
                  
        self.WriteAlignment()
        plt.plot(angles, rot_data[:,1])
        plt.vlines((center_step - rot_data[len(rot_data[:,0])//2,0])*(1.8/8.), 0, .08, color='r',label='center')
        plt.legend()
        plt.show()

        return
    

    def Align(self, motor='all'):
        """
        Align the sipm, lens, and led to center
        """
        if motor == 'sipm':
            self.sipm_motor.MoveMotor(self.alignments['sipm_center'] - self.sipm_motor.GetCurrentPosition())
        elif motor == 'lens':
            self.lens_motor.MoveMotor(self.alignments['lens_center'] - self.lens_motor.GetCurrentPosition())
        
        elif self.GetRotOrLED() == motor:
            if motor == 'led':
                self.led_motor.MoveMotor(self.alignments['led_center'] - self.led_motor.GetCurrentPosition())
            elif motor == 'rot':
                self.rot_motor.MoveSteps(self.alignments['rot_center'] - self.rot_motor.GetCurrentNumSteps())
                
        elif motor == 'all':
            self.sipm_motor.MoveMotor(self.alignments['sipm_center'] - self.sipm_motor.GetCurrentPosition())
            self.lens_motor.MoveMotor(self.alignments['lens_center'] - self.lens_motor.GetCurrentPosition())
            
            if self.GetRotOrLED() == 'led':
                self.led_motor.MoveMotor(self.alignments['led_center'] - self.led_motor.GetCurrentPosition())
                print('Rotation motor is off. Switch motors to align')
            else:
                self.rot_motor.MoveSteps(self.alignments['rot_center'] - self.rot_motor.GetCurrentNumSteps())
                print('LED motor is off. Switch motors to align')
              
        elif (self.GetRotOrLED() == 'led' and motor == 'rot') or (self.GetRotOrLED() == 'rot' and motor == 'led'):
            print(motor+' motor is off, you must switch motors to align')
        else:
            print('Invalid motor option. Option include sipm, lens, led, rot, and all')

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
    
    def ScanMaxes(self, width=40., num_measurements=200, align_to=None, print_progress=True):
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
            if print_progress:
                clear_output(wait=True)
                display(str(i+1)+"/"+str(num_measurements))
            self.sipm_motor.MoveMotor(distance_to_move)
            maxes.append(MeasurePeaktoPeak(self.scope, self.num_sweeps))
            positions_sipm.append(self.sipm_motor.GetCurrentPosition())
        self.sipm_motor.MoveMotor(-width/2.)
            
        return position_led, positions_sipm, maxes
    
  