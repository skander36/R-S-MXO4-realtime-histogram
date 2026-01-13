from RsMxo import *
from RsMxo.enums import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns
import numpy as np

# 1. INITIALIZARE (Codul tău original)
mxo = RsMxo('TCPIP::192.168.1.25::hislip0', id_query=False)
mxo.system.display.set_update(True)
mxo.trigger.set_mode(trigger_mode=TriggerMode.AUTO)

ch1 = mxo.channel.clone()
ch1.repcap_channel_set(channel=repcap.Channel.Ch1)
ch1.state.set(True)

# 2. CONFIGURARE MASURATOARE (Rămâne fixă)
m1 = repcap.MeasIndex.Nr1
mxo.measurement.source.set(signal_source=enums.SignalSource.C1, measIndex=m1)
mxo.measurement.main.set(meas_type=MeasType.STDDev, measIndex=m1)
mxo.measurement.enable.set(state=True, measIndex=m1)

# 3. PREGATIRE LIVE PLOT
data = [] 
max_points = 500
fig, ax = plt.subplots(figsize=(10, 6))

def update(frame):
    try:
        # Executăm achiziția și așteptăm sincronizarea
        mxo.utilities.write("SINGle")
        mxo.utilities.query("*OPC?")
        
        # Citim valoarea
        std_val = mxo.measurement.result.actual.get(measIndex=m1)
        
        if std_val < 1e10:
            data.append(std_val)
            if len(data) > max_points:
                data.pop(0)
        
        # Desenăm histograma
        if len(data) > 1:
            ax.clear()
            sns.histplot(data, bins=100, kde=False, ax=ax, color='blue', edgecolor='black')
            ax.set_title(f"Live Histogram: Standard Deviation\nSamples: {len(data)} | Mean: {np.mean(data):.6f} V")
            ax.set_xlabel("Standard Deviation (V)")
            ax.set_ylabel("Frequency")
            
    except Exception as e:
        print(f"Eroare: {e}")

# 4. LANSARE ANIMATIE
# 'ani' trebuie definit pentru a menține animația activă
ani = FuncAnimation(fig, update, interval=1, cache_frame_data=True)

try:
    plt.show() # Această linie blochează execuția până închizi fereastra
except KeyboardInterrupt:
    pass
finally:
    # 5. CURATENIE (Se execută la închiderea ferestrei sau oprire)
    print("Închidere sesiune...")
    mxo.close()