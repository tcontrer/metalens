import pyfirmata
import time
import csv

MAX_D = 231. # Maximum distance (length of rod) in mm

class Motor:
    """
    Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)
    Date: 2021

    This class controls defines the functions avaible
    to control a single motor in the
    metalens black box experiment. 
    """

    
    def __init__(self, board, step_pin, dir_pin, name, button_pin=0):
        self.board = board
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.button_pin = button_pin
        self.name = name
        
        self.ignore_button = True
        if button_pin != 0:
            # Setup the button pin to take input from button
            self.ignore_button = False
            #board.digital[button_pin].mode = pyfirmata.INPUT
            
            
    def PrintInfo(self):
        print('Motor name: '+self.name)
        print('    Step pin: '+str(self.step_pin))
        print('    Dir pin: '+str(self.dir_pin))
        print('    Button pin: '+str(self.button_pin))
    
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
    
    def MoveSteps(self, num_steps, ignore_button=False):
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

        # Step the motor
        for i in range(abs(num_steps)):
            if not ignore_button and not self.ignore_button:
                push_button = self.board.digital[self.button_pin].read()
                #print(push_button)
                if push_button:
                    self.AlertAtEdge(num_steps//abs(num_steps))
                    break
            self.step(motor_direction)

        current_num_steps = self.GetCurrentNumSteps()
        self.WriteNewNumSteps(current_num_steps+num_steps)

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
    
    def Rotate(self, degrees):
        """
        Moves the motor a number of degrees clockwise
        or counterclockwise. Minimum degree is 1.8/8.
        1600 steps in one full rotation.
        
        Inputs:
            degrees (float): degrees to rotate
        """
        steps = int(degrees / (1.8/8.))
        if abs(steps) < 1:
            print('Minimum rotation is 1.8 degrees')
            
        self.MoveSteps(steps, ignore_button=True)
        
        return
        

    def SetToZero(self):
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        self.SetSteps(0)
        return

    def SetToTop(self):
        """
        Set motor to zero steps.

        Inputs:
            steps (int): steps value to move to
        """
        self.MoveMotor(MAX_D-position-5)

    def SetSteps(self, steps):
        """
        Sets the motor a certain number of steps.

        Inputs:
            steps (int): steps value to move to
        """
        current_steps = self.GetCurrentNumSteps()
        steps_to_move = steps - current_steps
        self.MoveSteps(steps_to_move)

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
            
    def AlertAtEdge(self, original_dir):
        """
        Alerts the user that the motor has reached the edge of its movement
        and moves it 10 steps in the oposite direction.
        
        Inputs:
            original_dir (-1 or 1): The original direction of movement
        """
        current_pos = self.GetCurrentPosition()
        print('--------------------WARNING!---------------------')
        print(str(self.name)+' motor has reached edge')
        self.MoveSteps(-1*original_dir*1000, ignore_button=True)
        print('Moved away from edge, new positions is '+str(self.GetCurrentPosition())+' mm')
        print('-------------------------------------------------')
        return