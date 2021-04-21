"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

This class defines a run of data taking with the metalens-
black box experiment. 
"""

from motor import Motor
import alignment
import oscilliscope as osc
import time
import csv

def ScanMaxes(sipm_motor, led_motor, scope, width=40., num_measurements=200, align_to='grating', num_sweeps=15):
    """
    Scan the max signal across the sipm with and without
    the diffraction grating and save to a file. 
    """     
    # Align and measure
    alignment.Align(sipm_motor, led_motor, align_to)
    sipm_motor.MoveMotor(-width/2.)
        
    # Measure voltage at each distance
    distance_to_move = width/num_measurements
    maxes = []
    positions_sipm = []
    position_led = led_motor.GetCurrentPosition()
    for i in range(num_measurements):
        clear_output(wait=True)
        display(str(i+1)+"/"+str(num_measurements))
        sipm_motorMoveMotor(distance_to_move)
        maxes.append(osc.MeasurePeaktoPeak(scope, num_sweeps))
        positions_sipm.append(GetCurrentPosition())

    return position_led, positions_sipm, maxes

def Run_Voltage_v_Intensity(sipm_motor, led_motor, scope, dV=0.1, num_sweeps=15):
    """
    A run that increased the voltage by dV (currently must
    be done by hand), and plots led voltage versus
    sipm intensity.
    """
    # Run to check voltage to intensity
    alignment.Align(sipm_motor, led_motor, align='grating')
    num_measurements = 100
    values = []
    for i in range(num_measurements):
        clear_output(wait=True)
        display(str(i+1)+"/"+str(num_measurements))
        values.append(osc.MeasurePeaktoPeak(scope, num_sweeps))
        time.sleep(2)

    plt.plot([dV*(i+1) for i in range(num_measurements)], values)
    plt.xlabel('LED Voltage')
    plt.ylabel('SiPM Max Voltage')
    
    return

def Run(file_name, sipm_motor, led_motor, scope, voltage=5.0, num_sweeps):
    """
    This function takes two data sets, measuring the peak
    intensity of the sipm over a given width centered at 
    the grating and below the grating.
    """
    
    width = 60.0 # mm
    num_measurements = 150 #300 
    # Create the file to hold the array of max signals
    with open(file_name, mode='w') as file:
        writer = csv.writer(file)

        print("With grating")
        position_led_g, positions_sipm_g, maxes_g = ScanMaxes(sipm_motor, led_motor, scope, width, num_measurements, align_to='grating', num_sweeps)
        writer.writerow(['with grating'])
        writer.writerow([position_led_g])
        writer.writerow(positions_sipm_g)
        writer.writerow(maxes_g)

        print('Below grating')
        position_led_bg, positions_sipm_bg, maxes_bg = ScanMaxes(sipm_motor, led_motor, scope, width, num_measurements, align_to='below_grating', num_sweeps)
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
        writer.writerow(['Grating LED Position', GRATING_LED_POSITION])
        writer.writerow(['Below Grating LED Position',BELOW_GRATING_LED_POSITION])
        writer.writerow(['Below Mount LED Position', BELOW_MOUNT_LED_POSITION])
        writer.writerow(['Voltage', voltage])

    halfway = len(positions_sipm_g)//2
    plt.plot(np.array(positions_sipm_bg)-BELOW_GRATING_LED_POSITION, maxes_bg, label='below grating')
    plt.plot(np.array(positions_sipm_g)-GRATING_LED_POSITION, maxes_g, label='with grating')
#     plt.plot(np.array(positions_sipm_bm)-BELOW_MOUNT_LED_POSITION, maxes_bm, label='below mount')
    plt.legend()
    plt.ylabel('Max Voltage [V]')
    plt.xlabel('SiPM Position [mm]')
    
    return