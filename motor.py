import pyfirmata
import time
import csv

class Motor:
    """
    Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

    This class controls defines the functions avaible
    to control a single motor in the
    metalens black box experiment. 
    """
    
    def __init__(self, board, step_pin, dir_pin, name):
        self.board = board
        self.step_pin
        self.dir_pin
        self.name = name
    
    def step(direction=0):
        """
        Moves the stepper motor one microstep.

        Inputs:
            direction (0 or 1): direction motor will move when stepped
        """
        board.digital[self.dir_pin].write(direction) # direction pin
        board.digital[self.step_pin].write(1)
        #time.sleep(.01) # lowest windows can get is 10ms, motor runs faster if we remove the time delay 
        board.digital[self.step_pin].write(0)
        #time.sleep(.01)
        return

    def MoveMotor(distance, ignore_limits=False):
        """
        Moves either motor certain distance up or down.

        Inputs:
            distance (float): the distance to move the device, in mm
            ignore_limits (True/False):
        """

        # Calculate number of steps needed
        dx_per_step = .005 # mm
        num_steps = int(distance // dx_per_step)
        MoveSteps(num_steps, ignore_limits)

        return

    def SetToZero():
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        SetSteps(0)

    def SetToTop():
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        for motor in ["led","sipm"]:
            position = GetCurrentPosition(motor)
            MoveMotor(board, MAX_Z-position-5, motor)

    def SetSteps(steps):
        """
        Sets the motor a certain number of steps.

        Inputs:
            steps (int): steps value to move to
        """
        current_steps = GetCurrentNumSteps()
        steps_to_move = steps - current_steps
        MoveSteps(steps_to_move)

    def MoveSteps(num_steps, ignore_limits=False):
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

        current_num_steps = GetCurrentNumSteps()
        new_position = (current_num_steps+num_steps)*dx_per_step
        if not ignore_limits and (new_position > MAX_Z or new_position < 0.0):
            print('Warning: too large of distance to move motor')
            return

        # Step the motor
        for i in range(abs(num_steps)):
            step(motor_direction)
            #time.sleep(0.01)

        WriteNewNumSteps(current_num_steps+num_steps)

        return

    def GetCurrentNumSteps():
        """
        Reads the text file that stores the current number of step the sipm and motor
        have moved and returns the position based on the motor input in mm
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

    def GetCurrentPosition():
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

    def WriteNewNumSteps(position):
        """
        Writes to the text file the new number of steps of the device from the bottom 
        """
        
        pos = GetCurrentNumSteps()

        with open('positions.csv', 'w', newline='') as file:
            file.truncate()
            writer = csv.writer(file)
            
            writer.writerow([pos])

        return




