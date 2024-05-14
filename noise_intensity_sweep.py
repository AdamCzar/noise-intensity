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

if not controller == None: # check if connection worked
    controller.Connect(serial_num)

    if not controller.IsSettingsInitialized(): # wait for connection and initialization
        controller.WaitForSettingsInitialized(3000) # in units of ms

    thor.activate(controller, serial_num)


    # Conduct sweep
    print('Moving Motor to start')
    #controller.MoveTo(Decimal(start), 60000) # immediately continue
    thor.move(controller, start_angle)
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