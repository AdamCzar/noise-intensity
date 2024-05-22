# imports for Thorlabs
import time
import clr # need to import pythonnet (can be done from pip)
import zurich_daq as scope
import matplotlib.pyplot as plt



# to access dll namespaces from Thorlabs, we need to first add the references
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.TCube.DCServoCLI.dll")

# import methods/objects from Thorlabs namespaces
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import JogParametersBase
from Thorlabs.MotionControl.TCube.DCServoCLI import *
from System import Decimal # Kinesis libraries use Decimal type for move parameters and stage settings


# Initialize sweep parameters
start_angle = 5
end_angle = 24
step_angle = 0.1

n_records = 3 # number of time traces (aka records) per waveplate step




# Initialize Zurich instrument and subscribe to scope module
scope.initialize()


def sweep(controller, start, end, step, n_records):
    # Initialize data arrays
    voltages = []
    noises = []
    angles = []
    
    print('Moving Motor to start')
    controller.MoveTo(Decimal(start), 60000) # immediately continue
    time.sleep(2)
    
    # Sweep specified range
    n = int((end - start)/step)
    print('Sweeping')
    for i in range(n):
        current_pos = controller.Position.ToString()
        print(current_pos, '\n')
        controller.MoveTo(Decimal(float(current_pos)+float(step)), 60000)
        time.sleep(0.5)
        
        #Obtain data with triggering disabled
        data_no_trig = scope.get_scope_records(scope.scope_module, n_records)
        
        #print(data_no_trig)

        v, n = scope.extract_stats(data_no_trig)
        voltages += v
        noises += n
        
        for i in v:
            angles.append(float(current_pos))
        
        time.sleep(.25)
            
    print('Finished Sweeping \n')
    
    return voltages, noises, angles
    
    
#def main():
serial_num = str('83835052') # use S/N of T Cube controller

DeviceManagerCLI.BuildDeviceList() # load available devices into memory
controller = TCubeDCServo.CreateTCubeDCServo(serial_num) # create controller variable

if not controller == None: # check if connection worked
    controller.Connect(serial_num)
    
    if not controller.IsSettingsInitialized(): # wait for connection and initialization
        controller.WaitForSettingsInitialized(3000) # in units of ms
    
    controller.StartPolling(50) # instruct controller to send updates about position and motor status to PC with update rate of 50ms
    time.sleep(.1) # give controller time to update, good habits to set as twice the duration of polling rate
    controller.EnableDevice()
    time.sleep(.1)
    
    # load parameters for translation stage into the TCube
    config = controller.LoadMotorConfiguration(serial_num, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
    config.DeviceSettingsName = str('PRM1-Z8') # use part number of this stage
    config.UpdateCurrentConfiguration()
    controller.SetSettings(controller.MotorDeviceSettings, True, False)
    info = controller.GetDeviceInfo()
    
    print(f"Controller {serial_num} = {info.Name}")

    #print('Homing Motor')
    #controller.Home(60000) # if command does not complete by the end of this time, it will throw an error
    
    # to change the jog params of the translation stage, first import them with the GetJogParams method and then modify
    jog_params = controller.GetJogParams()
    jog_params.StepSize = Decimal(1) # units of deg
    jog_params.MaxVelocity = Decimal(25) # units in deg/s
    jog_params.JogMode = JogParametersBase.JogModes.SingleStep
    
    # send updated jog params back to the controller
    controller.SetJogParams(jog_params)
    
    #print(controller.Position.ToString())
    
    # Jog motor single step
    #print('Jogging Motor')
    #controller.MoveJog(MotorDirection.Forward, 60000)
    #time.sleep(.25)
    
    #print(controller.Position.ToString())
    
    # Move to user position
    #print('Moving Motor')
    #controller.MoveTo(Decimal(50.3), 60000) # immediately continue
    #time.sleep(2)
    
    print(controller.Position.ToString())

    #sweep(controller, 60, 60.5, 0.1)
    voltages, noises, angles = sweep(controller, start_angle, end_angle, step_angle, n_records)
    
    
    # Close controller
    controller.StopPolling()
    controller.Disconnect(False)
    
    
if len(voltages) > 0:
    # Create a figure and two subplots (axes) that share the same x-axis
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Plot voltages on the first subplot
    ax1.scatter(angles, voltages)  # 'b-' is for blue solid line
    ax1.set_ylabel('Voltage (V)')
    #ax1.set_title('Voltages and Noises vs Angles')

    # Plot noises on the second subplot
    ax2.scatter(angles, noises)  # 'r-' is for red solid line
    ax2.set_ylabel('Voltage STD (V)')
    ax2.set_xlabel('Waveplate Angle (deg)')

    # Display the plots
    plt.tight_layout()
    plt.show()
    
    # save data to text file
    file_name = input('Enter the file name (with extension ie .txt): ')
    data = np.column_stack((np.array(angles), np.array(voltages), np.array(noises)))
    np.savetxt(file_name, data, fmt='%.8f', delimeter = '\t', header = 'Angle (deg)\tVoltage (V)\tVoltage STD (V)')
    
    '''
    plt.scatter(voltages, noises)
    plt.xlabel('Voltage (V)')
    plt.ylabel('Voltage STD (V)')
    #plt.scatter(angles, voltages)
    #plt.xlabel('Angle (deg)')
    #plt.ylabel('Voltage (V)')
    plt.show()
    '''
#main()
    
    