import pyfirmata
import time
import csv

MAX_Z = 231. # Mazimum allowable height in mm
GRATING_LED_POSITION = 70. # LED position for alignment with grating
BELOW_GRATING_LED_POSITION = 67 # LED position for alignment below grating
BELOW_MOUNT_LED_POSITION = 45 # LED position for alignment below grating
SIPM_OFFSET = 13.86 #14.355 # Difference in height between SiPM and LeD for direct alignment. LED is lower.
NUM_SWEEPS = 15

class Motor:
    """
    Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

    This class controls defines the functions avaible
    to control a single motor in the
    metalens black box experiment. 
    """

    
    def __init__(self, board, step_pin, dir_pin, name):
        self.board = board
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.name = name
    
    def step(self, direction=0):
        """
        Moves the stepper motor one microstep.

        Inputs:
            direction (0 or 1): direction motor will move when stepped
        """
        self.board.digital[self.dir_pin].write(direction) # direction pin
        self.board.digital[self.step_pin].write(1)
        #time.sleep(.01) # lowest windows can get is 10ms, motor runs faster if we remove the time delay 
        self.board.digital[self.step_pin].write(0)
        #time.sleep(.01)
        return

    def MoveMotor(self, distance, ignore_limits=False):
        """
        Moves either motor certain distance up or down.

        Inputs:
            distance (float): the distance to move the device, in mm
            ignore_limits (True/False):
        """

        # Calculate number of steps needed
        dx_per_step = .005 # mm
        num_steps = int(distance // dx_per_step)
        self.MoveSteps(num_steps, ignore_limits)

        return

    def SetToZero(self):
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        self.SetSteps(0)

    def SetToTop(self):
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        self.MoveMotor(MAX_Z-position-5)

    def SetSteps(self, steps):
        """
        Sets the motor a certain number of steps.

        Inputs:
            steps (int): steps value to move to
        """
        current_steps = self.GetCurrentNumSteps()
        steps_to_move = steps - current_steps
        self.MoveSteps(steps_to_move)

    def MoveSteps(self, num_steps, ignore_limits=False):
        """
        Moves the motor a certain number of steps.

        Inputs:
            num_steps (int): number of steps to move the device (positive = up, negative = down)
            ignor_limits (True/False): 
        """
        num_steps = int(num_steps)
        if num_steps == 0: return

        dx_per_step = .005 # mm

        if num_steps < 0:
            motor_direction = 0
        else:
            motor_direction = 1

        current_num_steps = self.GetCurrentNumSteps()
        new_position = (current_num_steps+num_steps)*dx_per_step
        if not ignore_limits and (new_position > MAX_Z or new_position < 0.0):
            print('Warning: too large of distance to move motor')
            return

        # Step the motor
        for i in range(abs(num_steps)):
            self.step(motor_direction)
            #time.sleep(0.01)

        self.WriteNewNumSteps(current_num_steps+num_steps)

        return

    def GetCurrentNumSteps(self):
        """
        Reads the text file that stores the current number of step the sipm and motor
        have moved and returns the position based on the motor input in mm
        """
        rows = []
        with open('position_'+self.name+'.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)

        return int(rows[0][0])

    def GetCurrentPosition(self):
        """
        Reads the text file that stores the current position of the motor
        and returns the position based on the motor input in mm
        """
        dx_per_step = .005 # mm
        rows = []
        with open('position_'+self.name+'.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                rows.append(row)
        
        return int(rows[0][0])*dx_per_step

    def WriteNewNumSteps(self, position):
        """
        Writes to the text file the new number of steps of the device from the bottom 
        """
        
        with open('position_'+str(self.name)+'.csv', 'w', newline='') as file:
            file.truncate()
            writer = csv.writer(file)
            
            writer.writerow([position])

        return

    def CreatePositionFile(self):
        """
        Creates the file to hold the position of the motor, set the motor
        at zero. 
        """
        with open('position_'+self.name+'.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow([0])



