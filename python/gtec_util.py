import time

# According to the labels on cap
CHANNEL_NAMES = {1: 'Cz',
                 2: 'Fp2',
                 3: 'F3',
                 4: 'Fz',
                 5: 'F4',
                 6: 'T7',
                 7: 'C3',
                 8: 'FP1',
                 9: 'C4',
                 10: 'T8',
                 11: 'P3',
                 12: 'Pz',
                 13: 'P4',
                 14: 'PO7',
                 15: 'PO8',
                 16: 'Oz',
                 17: 'acc_x',
                 18: 'acc_y',
                 19: 'acc_z'}
# according to gNautilus_research docs
CHANNEL_NAMES = ['Fp1', 'Fp2', 'F3', 'Fz',
                 'F4', 'T7', 'C3', 'Cz',
                 'C4', 'T8', 'P3', 'Pz',
                 'P4', 'PO7', 'PO8', 'Oz',
                 'acc_x', 'acc_y', 'acc_z']

# according to the Cap
CHANNEL_NAMES = ['Cz', 'Fp2', 'F3', 'Fz', 
                 'F4', 'T7', 'C3', 'Fp1',
                 'C4', 'T8', 'P3', 'Pz',
                 'P4', 'PO7', 'PO8', 'Oz', 
                 'acc_x', 'acc_y', 'acc_z']
#TODO: Check all possible channels and add in the correct order
#TODO: Add channel names dynamically
# Ground and REF not supplied, but physical count are: 
#   17: GND = AFz
#   18: REF


def gtec_to_lsl(device):
    '''
	Retrieves data from the g.Tec Nautilus
	research and sends it to LabStreamingLayer
	indefinetely. Ctrl+C to exit.

	device: object
		pygds.GDS() object, handles the connection
		with the acquisition device.
	
	sample_size: int, default=None
		Defines size of a single scan. If None
		given, the device Sampling Rate is used.

    '''
    ## LSL SETUP
    stream_name = "gtec_outlet"

    # Add header
    info = StreamInfo(stream_name, 'data', device.N_ch_calc(), device.SamplingRate, 'float32', 'gtec_outlet_1')
    info.desc().append_child_value("manufacturer", "gtec")
    channels = info.desc().append_child("channels")
    for ch_idx in range(device.N_ch):
         channels.append_child("channel") \
             .append_child_value("label", CHANNEL_NAMES[ch_idx]) \
             .append_child_value("unit", "microvolts") \
             .append_child_value("type", "EEG")
    outlet = StreamOutlet(info) 

    # function to handle incoming data
    def data_handle(s):
        t = time.time()
        outlet.push_chunk(s.copy())
        print('.', end='', flush=True)
        passed_time = time.time() - t
        if passed_time > 0.1:
            print('Time per loop: {0:.3f}'.format(passed_time), flush=True)
        return True

    # run
    try:
        print('Fs: {} // Sample size: {}'.format(device.SamplingRate, device.NumberOfScans))
        data = device.GetData(device.NumberOfScans, data_handle)
    except Exception as e:
        print(e)
    finally:
        device.Close()
        del device


def run_data_acquisition(device, handle=None, sample_size=None, record_time=None):
    '''
    Retrieves data from the g.Tec Nautilus Research 
    device for a preset amount of time and returns
    the retrieved data.
    Note that a scan is a single sample which is of 
    size [sample_size x chs]

    device: object
        pygds.GDS() object, handles the connection
        with the acquisition device.

    handle: function(scan), default=None
        function with a single scan as input. Supply
        this function to use a scan (for example
        for closed loop applications).

    sample_size: int, default=None
        Defines size of a single scan. If None
        given, the device Sampling Rate is used.

    record_time: int, default=None
        total time to record in seconds. If None
        supplied, measurement will take 60 seconds

    returns: list
        list of all samples.
    '''

    sample_size = device.SamplingRate if sample_size == None else sample_size
    record_time = 60 if record_time == None else record_time
    total_scans = record_time * device.SamplingRate / sample_size
    
    samples = []
    def data_handle(s):
        current_scan = s.copy()
        samples.append(current_scan)
        if handle != None:
            #TODO: include ability to continue/stop data collection
            handle(current_scan)
        # print('.', end='', flush=True)
        # print(current_scan, flush=True)
        return True if len(samples) < total_scans else False

    print('Recording for {}s with sample_size {}, resulting in {} samples'.format(record_time, sample_size, total_scans))

    try:
        data = device.GetData(sample_size, data_handle)    
        print('\n', end='')    
        return samples
    except Exception as e:
        print(e)
    finally:
        device.Close()
        del device



if __name__ == "__main__":
    from pylsl import StreamOutlet, StreamInfo
    import pygds


    # TODO: Move setting config to a more logical place
    device = pygds.GDS()
    config = {
        'AccelerationData': 1, # Adds 3 channels
        'SamplingRate': 500, # 250 or 500
        'CAR': 0, # Don't use CAR on hardware, Noise can spread to other channels and then you render your exp useless
        'NoiseReduction': 0
    }
    
    if config['CAR']:
        for ch_num in range(device.N_electrodes):
            device.Channels[ch_num].UsedForCar = 1
    if config['NoiseReduction']:
        for ch_num in range(device.N_electrodes):
            device.Channels[ch_num].UsedForNoiseReduction = 1

    for attr, val in config.items():
        setattr(device, attr, val)

    device.NumberOfScans_calc()

    device.SetConfiguration()

    gtec_to_lsl(device)