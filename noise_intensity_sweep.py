import waveplate_control as thor
import zurich_daq as scope

# imports for Thorlabs
import time
import clr # need to import pythonnet (can be done from pip)


# to access dll namespaces from Thorlabs, we need to first add the references
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.TCube.DCServoCLI.dll")

# import methods/objects from Thorlabs namespaces
#import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
from Thorlabs.MotionControl.DeviceManagerCLI import *
#import Thorlabs.MotionControl.GenericMotorCLI as GenericMotorCLI
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import JogParametersBase
#import Thorlabs.MotionControl.TCube.DCServoCLI as DCServoCLI
from Thorlabs.MotionControl.TCube.DCServoCLI import *
from System import Decimal # Kinesis libraries use Decimal type for move parameters and stage settings


# Initialize sweep parameters
start_angle = 50.3
end_angle = 50.5
step_angle = 0.01

n_records = 5 # number of time traces (aka records) per waveplate step

# Initialize data arrays
voltages = []
noises = []


# Initialize Zurich instrument and subscribe to scope module
scope.initialize()


# Initialize Thorlabs rotation stage and connect
thor.configure_Thorlabs()

serial_num = str('83835052') # use S/N of T Cube controller
#controller = thor.connect_controller(serial_num)

thor.DeviceManagerCLI.BuildDeviceList() # load available devices into memory
controller = thor.TCubeDCServo.CreateTCubeDCServo(serial_num) # create controller variable

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
    config.DeviceSettingsName = str('MTS50-Z8') # use part number of this stage
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

    print(controller.Position.ToString())

    # Conduct sweep
    print('Moving Motor to start')
    #controller.MoveTo(Decimal(start), 60000) # immediately continue
    thor.move(controller, float(start_angle))
    time.sleep(2)

    # Sweep specified range
    n = int((end_angle - start_angle)/step_angle)
    print('Sweeping')
    for i in range(n):
        #current_pos = controller.Position.ToString()
        #controller.MoveTo(Decimal(current_pos) + Decimal(step), 60000)
        thor.step(controller, step_angle)
        #time.sleep(0.25)

        #Obtain data with triggering disabled
        data_no_trig = scope.get_scope_records(scope.scope_module, n_records)

        v, n = scope.extract_stats(data_no_trig)
        voltages.append(v)
        noises.append(n)


    print('Finished Sweeping')


    # Disconnect Thorlabs stage once sweep is complete
    thor.close_controller(controller)

plt.scatter(voltages, noises)
plt.xlabel('Voltage (V)')
plt.ylabel('Voltage STD (V)')
plt.show()