"""
Written by: Taylor Contreras (taylorcontreras@g.harvard.edu)

This code holds the function to run the motors and oscilliscope
in the metalens black box experiment. 
"""
import pyvisa
import numpy as np

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

def MeasureIntegral(scope, num_sweeps):
    """
    Measures the integral of the sipm waveform coming from the oscilliscope and
    returns an array of the maxes for a given number of aquisitions.
    """
    force_trigger_rate = 0.003 # s
    trigger_level = 0.890 # V
    
    # Set up aquisition by stopping trigger 
    scope.write(r"""vbs 'app.acquisition.triggermode = "stopped" ' """)
    # Set up trigger (in this case we trigger on the C2 which has the trigger for the input waveform to the LED)
    scope.write(r"""vbs 'app.acquisition.trigger.edge.source = "C2" ' '""")
    scope.write(r"""vbs 'app.acquisition.trigger.C2level = %f ' """ % trigger_level)
    scope.write(r"""vbs 'app.acquisition.triggermode = "single" ' """)
    scope.write(r"""vbs 'app.acquisition.horizontal.maximize = "FixedSampleRate" ' """)

    # Set up Measurements, clearing previous measurements
    scope.write(r"""vbs 'app.clearsweeps ' """)
    scope.write(r"""vbs 'app.measure.clearall ' """)
    scope.write(r"""vbs 'app.measure.clearsweeps ' """)

    # Setup averaging waveform
    scope.write(r"""vbs 'app.math.f1.operator1 = "intg" ' """)
    scope.write(r"""vbs 'app.math.f1.source1 = "C1" ' """)

    # Setup measurement of peak to peak voltage based on average waveform
    scope.write(r"""vbs 'app.measure.showmeasure = true ' """)
    scope.write(r"""vbs 'app.measure.statson = true ' """)
    scope.write(r"""vbs 'app.measure.p1.view = true ' """)
    scope.write(r"""vbs 'app.measure.p1.paramengine = "maximum" ' """ )
    scope.write(r"""vbs 'app.measure.p1.source1 = "F1" ' """)

    # Sweep
    integrals = []
    for i in range(0,num_sweeps):
        r = scope.query(r"""vbs? 'return=app.acquisition.acquire( %f , True ) ' """ %force_trigger_rate)
        r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(0.03)' """)
        integral = scope.query(r"""vbs? 'return=app.measure.p1.out.result.value' """)
        integrals.append(integral)
        if r==0:
            print("Time out from WaitUntilIdle, return = {0}".format(r))

    integrals = np.array([ConvertToFloat(integral) for integral in integrals])
    print(integrals)
    
    return np.mean(integrals)


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