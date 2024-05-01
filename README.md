# noise-intensity
Measure signal noise as a function of laser intensity.

This Python-based software aims to measure the noise in an acquired signal while the laser intensity is varied. The signal comes from a detector such as a photodiode or an ultrafast atomic force microscope. The signal is fed from the detector into a Zurich Instruments device (in this case a UHFLI lock-in amplifier) and the data is acquired via the scope module (see https://docs.zhinst.com/zhinst-toolkit/en/latest/examples/scope_module.html). The laser intensity is varied by turning a half-waveplate in a half-waveplate and polarizer combination. It is turned with a motorized ThorLabs rotation stage (see https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/KCube/KDC101/KDC101_Power_Meter_Insight_Code.py). 

This software can be generalized to control different motorized Thorlabs stages as well as acquire different types of data from a Zurich Instrument.

