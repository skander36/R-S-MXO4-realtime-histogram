from RsMxo import *
from RsMxo.enums import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np


mxo = RsMxo('TCPIP::192.168.1.25::hislip0', id_query=False)
mxo.system.display.set_update(True)
mxo.trigger.set_mode(trigger_mode=TriggerMode.AUTO)

ch1 = mxo.channel.clone()
ch1.repcap_channel_set(channel=repcap.Channel.Ch1)
ch1.state.set(True)


m1 = repcap.MeasIndex.Nr1
mxo.measurement.source.set(signal_source=enums.SignalSource.C1, measIndex=m1)
mxo.measurement.main.set(meas_type=MeasType.STDDev, measIndex=m1)
mxo.measurement.enable.set(state=True, measIndex=m1)


data = [] 
max_points = 500
fig, ax = plt.subplots(figsize=(10, 6))

def update(frame):
    try:
        
        mxo.utilities.write("SINGle")
        mxo.utilities.query("*OPC?")
        
       
        std_val = mxo.measurement.result.actual.get(measIndex=m1)
        
        if std_val < 1e10:
            data.append(std_val)
            if len(data) > max_points:
                data.pop(0)
        
        
        if len(data) > 1:
            ax.clear()
            sns.histplot(data, bins=700, kde=False, ax=ax, color='skyblue', edgecolor='black')
            ax.set_title(f"Live Histogram: Standard Deviation\nSamples: {len(data)} | Mean: {np.mean(data):.6f} V")
            ax.set_xlabel("Standard Deviation (V)")
            ax.set_ylabel("Frequency")
            
    except Exception as e:
        print(f"Error: {e}")


ani = FuncAnimation(fig, update, interval=1, cache_frame_data=True)

try:
    plt.show() 
except KeyboardInterrupt:
    pass
finally:
    
    print("Close sesion...")

    mxo.close()

