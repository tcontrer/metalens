"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

This class controls defines the functions avaible
to align the motors in the
metalens black box experiment. 
"""

from motor import Motor
import matplotlib.pyplot as plt
from scipy import signal

MAX_Z = 231. # Mazimum allowable height in mm
GRATING_LED_POSITION = 70. # LED position for alignment with grating
BELOW_GRATING_LED_POSITION = 67 # LED position for alignment below grating
BELOW_MOUNT_LED_POSITION = 45 # LED position for alignment below grating
SIPM_OFFSET = 13.86 #14.355 # Difference in height between SiPM and LeD for direct alignment. LED is lower.
NUM_SWEEPS = 15


def Align(sipm_motor, led_motor, align_to='grating'):
    """
    Moves them to align with the diffraction grating and saves 
    the position in the cvs file, if to_lens=True, else aligns
    the sipm and led away from the diffraction grating.

    inputs
        sipm_motor (Motor class object)
        led_motor (Motor class object)
        align_to (str): Align the LED and sipm to the diffraction
            grating ('grating'), the substrate without the grating 
            ('below_grating'), or below the mount ('below_mount')
    """


    sipm_pos = sipm_motor.GetCurrentPosition()
    led_pos = led_motor.GetCurrentPosition()

    if align_to=='grating':
        led_motor.MoveMotor(GRATING_LED_POSITION-led_pos)
        sipm_motor.MoveMotor(GRATING_LED_POSITION+SIPM_OFFSET-sipm_pos)
    elif align_to=='below_grating':
        led_motor.MoveMotor(BELOW_GRATING_LED_POSITION-led_pos)
        sipm_motor.MoveMotor(BELOW_GRATING_LED_POSITION+SIPM_OFFSET-sipm_pos)
    elif align_to=='below_mount':
        led_motor.MoveMotor(BELOW_MOUNT_LED_POSITION-led_pos)
        sipm_motor.MoveMotor(BELOW_MOUNT_LED_POSITION+SIPM_OFFSET-sipm_pos)
    else:
        print("Incorrect input for align_to (options: 'grating', 'below_grating', 'below_mount')")

    return


def GetAlignment(sipm_motor, led_motor, scope):
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
    sipm_motor.SetToZero()
    led_motor.SetToZero()
    sipm_motor.MoveMotor(BELOW_MOUNT_LED_POSITION)
    led_motor.MoveMotor(BELOW_MOUNT_LED_POSITION)
    distance_to_move = 30.
    distance_per_step = 0.5
    num_steps = int(distance_to_move/distance_per_step)
    maxes = []
    positions = []
    steps = []
    # Measure voltage at each step
    for i in range(num_steps):
        sipm_motor.MoveMotor(distance_per_step)
        max = osc.MeasurePeaktoPeak(scope)
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
    SIPM_OFFSET = abs(NoGrating_peak_pos)
    print(SIPM_OFFSET)
    # Remember to update global variable at the top of the workbook once a new SIPM_OFFSET is measured.
    
    return SIPM_OFFSET

def ResetZero(sipm_motor, led_motor):
    # Unplug motors and move them to bottom first
    sipm_motor.WriteNewNumSteps(0,"sipm")
    led_motor.WriteNewNumSteps(0,"led")
    
    return

