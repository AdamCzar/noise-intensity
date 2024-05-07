import waveplate_control as thor
import zurich_daq as scope

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
controller = thor.connect_controller(serial_num)
thor.activate(controller)


# Conduct sweep


# Disconnect Thorlabs stage once sweep is complete
thor.close_controller(controller)