"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

This code holds the function to run the motors and oscilliscope
in the metalens black box experiment. 
"""

import pyvisa
import pyfirmata
import time
import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy import signal
from IPython.display import display, clear_output

def MeasurePeaktoPeak(scope, num_sweeps):
    """
    Measures the peak to peak voltage coming from the oscilliscope and
    returns an array of the maxes for a given number of aquisitions.
    """
    force_trigger_rate = 0.1 # s
    trigger_level = 0.890 # V
    
    # Waits 5 seconds after oscilliscope is idle before 
    # setting up new acquisition
    scope.timeout = 5000
    scope.clear()
    r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(.0003)' """)
    
    # Set up aquisition by stopping trigger 
    scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
    # Set up trigger (in this case we trigger on the C2 which has the trigger for the input waveform to the LED)
    scope.write(r"""vbs 'app.acquisition.trigger.C2level = %f ' """ % trigger_level)
    scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
    scope.write(r"""vbs 'app.acquisition.horizontal.maximize = "FixedSampleRate" ' """)

    # Set up Measurements, clearing previous measurements
    scope.write(r"""vbs 'app.clearsweeps ' """)
    scope.write(r"""vbs 'app.measure.clearall ' """)
    scope.write(r"""vbs 'app.measure.clearsweeps ' """)

    # Setup averaging waveform
    scope.write(r"""vbs 'app.math.f1.operator1 = "average" ' """)
    scope.write(r"""vbs 'app.math.f1.source1 = "C1" ' """)
    
    for i in range(0, num_sweeps):
        r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.0003 , True ) ' """)
        r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(.0003)' """)
        if r==0:
            print("Time out from WaitUntilIdle, return = {0}".format(r))


    # Setup measurement of peak to peak voltage based on average waveform
    scope.write(r"""vbs 'app.measure.showmeasure = true ' """)
    scope.write(r"""vbs 'app.measure.statson = true ' """)
    scope.write(r"""vbs 'app.measure.p1.view = true ' """)
    scope.write(r"""vbs 'app.measure.p1.paramengine = "pkpk" ' """ ) 
    scope.write(r"""vbs 'app.measure.p1.source1 = "F1" ' """)
    r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.003 , True ) ' """)
    r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(.003)' """)

    # Read back Measurement Results
    pkpk = scope.query(r"""vbs? 'return=app.measure.p1.out.result.value' """)

    return ConvertToFloat(pkpk)

def step(board, step_pin=9, dir_pin=8, direction=0):
    """
    Moves the stepper motor one microstep.
    
    Inputs:
        step_pin (int): pin on arduino to control stepping
        dir_pin (int): pin on arduino to control direction
        direction (0 or 1): direction motor will move when stepped
    """
    board.digital[dir_pin].write(direction) # direction pin
    board.digital[step_pin].write(1)
    #time.sleep(.01) # lowest windows can get is 10ms, motor runs faster if we remove the time delay 
    board.digital[step_pin].write(0)
    #time.sleep(.01)
    return

def MoveMotor(board, distance, motor='sipm', ignore_limits=False):
    """
    Moves either the sipm or the LED a certain distance up or down.
    
    Inputs:
        distance (float): the distance to move the device, in mm
        motor ('sipm' or 'led'): specifies which device to move
        ignore_limits (True/False):
    """
    
    # Calculate number of steps needed
    dx_per_step = .005 # mm
    num_steps = int(distance // dx_per_step)
    MoveSteps(board, num_steps, motor, ignore_limits)
       
    return

def SetToZero(board):
    """
    Setboth motors to zero steps.
    
    Inputs:
        steps (int): steps value to move to
        motor ('sipm' or 'led'): specifies which device to move
    """
    SetSteps(board, 0, "sipm")
    SetSteps(board, 0, "led")

def SetToTop(board):
    """
    Set both motors to zero steps.
    
    Inputs:
        steps (int): steps value to move to
        motor ('sipm' or 'led'): specifies which device to move
    """
    for motor in ["led","sipm"]:
        position = GetCurrentPosition(motor)
        MoveMotor(board, MAX_Z-position-5, motor)
    
def SetSteps(board, steps, motor="sipm"):
    """
    Sets either the sipm or the LED tp a certain number of steps.
    
    Inputs:
        steps (int): steps value to move to
        motor ('sipm' or 'led'): specifies which device to move
    """
    current_steps = GetCurrentNumSteps(motor)
    steps_to_move = steps - current_steps
    MoveSteps(board, steps_to_move, motor)

def MoveSteps(board, num_steps, motor='sipm', ignore_limits=False):
    """
    Moves either the sipm or the LED a certain number of steps.
    
    Inputs:
        num_steps (int): number of steps to move the device (positive = up, negative = down)
        motor ('sipm' or 'led'): specifies which device to move
        ignor_limits (True/False): 
    """
    num_steps = int(num_steps)
    if num_steps == 0: return
    
    dx_per_step = .005 # mm
    
    # Specify stepper motor inputs
    if motor == 'sipm':
        step_pin = 8
        dir_pin = 9
    elif motor == 'led':
        step_pin = 10
        dir_pin = 11
    else:
        print('Not a valid motor option')
        return
       
    if num_steps < 0:
        motor_direction = 0
    else:
        motor_direction = 1
    
    current_num_steps = GetCurrentNumSteps(motor)
    new_position = (current_num_steps+num_steps)*dx_per_step
    if not ignore_limits and (new_position > MAX_Z or new_position < 0.0):
        print('Warning: too large of distance to move motor')
        return
    
    # Step the motor
    for i in range(abs(num_steps)):
        step(board, step_pin, dir_pin, motor_direction)
        #time.sleep(0.01)
        
    WriteNewNumSteps(current_num_steps+num_steps, motor)
    
    return

def GetCurrentNumSteps(motor='sipm'):
    """
    Reads the text file that stores the current number of step the sipm and motor
    have moved and returns the position based on the motor input in mm
    
    Inputs:
        motor (str): 'sipm' or 'led'
    """
    rows = []
    with open('positions.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
        
    if motor=='sipm':
        return int(rows[0][0])
    elif motor=='led':
        return int(rows[0][1])
    else:
        print('Not a valid input')
        return
    
def GetCurrentPosition(motor='sipm'):
    """
    Reads the text file that stores the current position of the sipm and motor
    and returns the position based on the motor input in mm
    
    Inputs:
        motor (str): 'sipm' or 'led'
    """
    dx_per_step = .005 # mm
    rows = []
    with open('positions.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
        
    if motor=='sipm':
        return int(rows[0][0])*dx_per_step
    elif motor=='led':
        return int(rows[0][1])*dx_per_step
    else:
        print('Not a valid input')
        return

def WriteNewNumSteps(position, motor='sipm'):
    """
    Writes to the text file the new number of steps of the device from the bottom 
    
    Inputs:
        motor (str): 'sipm' or 'led'
    """
    if motor != "sipm" and motor != "led":
        print('Not a valid input')
        return
        
    sipm_pos = GetCurrentNumSteps('sipm')
    led_pos = GetCurrentNumSteps('led')
    
    with open('positions.csv', 'w', newline='') as file:
        file.truncate()
        writer = csv.writer(file)

        if motor=='sipm':
            writer.writerow([position,led_pos])
            return
        else:
            writer.writerow([sipm_pos,position])
            return
        
def Align(board, align_to='grating'):
    """
    Moves them to align with the diffraction grating and saves 
    the position in the cvs file, if to_lens=True, else aligns
    the sipm and led away from the diffraction grating.
    
    inputs
        align_to (str): Align the LED and sipm to the diffraction
            grating ('grating'), the substrate without the grating 
            ('below_grating'), or below the mount ('below_mount')
    """
    
    
    sipm_pos = GetCurrentPosition(motor='sipm')
    led_pos = GetCurrentPosition(motor='led')
    
    if align_to=='grating':
        MoveMotor(board, GRATING_LED_POSITION-led_pos, "led")
        MoveMotor(board, GRATING_LED_POSITION+SIPM_OFFSET-sipm_pos, "sipm")
    elif align_to=='below_grating':
        MoveMotor(board, BELOW_GRATING_LED_POSITION-led_pos, "led")
        MoveMotor(board, BELOW_GRATING_LED_POSITION+SIPM_OFFSET-sipm_pos, "sipm")
    elif align_to=='below_mount':
        MoveMotor(board, BELOW_MOUNT_LED_POSITION-led_pos, "led")
        MoveMotor(board, BELOW_MOUNT_LED_POSITION+SIPM_OFFSET-sipm_pos, "sipm")
    else:
        print("Incorrect input for align_to (options: 'grating', 'below_grating', 'below_mount')")
    
    return

def ConvertToFloat(val):
    """
    Extracts a float from a complex string
    """
    for token in val.split():
        floatval = ''
        try:
           floatval = float(token)
        except ValueError:
            continue
        if type(floatval)==float:
            return floatval
    return np.nan
