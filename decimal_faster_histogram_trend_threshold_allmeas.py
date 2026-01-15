from RsMxo import *
from RsMxo.enums import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RadioButtons, Button, TextBox
from matplotlib.ticker import ScalarFormatter # Import pentru formatarea axelor
import numpy as np

# 1. INITIALIZARE OSCILOSCOP
mxo = RsMxo('TCPIP::192.168.1.25::hislip0', id_query=False)
mxo.system.display.set_update(True)
mxo.trigger.set_mode(trigger_mode=TriggerMode.AUTO)
mxo.utilities.write("RUN") 

m1 = repcap.MeasIndex.Nr1
mxo.measurement.source.set(signal_source=enums.SignalSource.C1, measIndex=m1)
mxo.measurement.main.set(meas_type=MeasType.FREQuency, measIndex=m1)
mxo.measurement.enable.set(state=True, measIndex=m1)

# 2. PARAMETRI ANALIZĂ
data = [] 
std_history = []
max_points = 1000   
window_size = 50    
threshold_value = 0.5
current_meas_type = "FREQuency"

params_str = "HIGH|LOW|AMPLitude|MAXimum|MINimum|PDELta|MEAN|RMS|STDDev|CRESt|POVershoot|NOVershoot|AREA|RTIMe|FTIMe|PPULse|NPULse|PERiod|FREQuency|PDCYcle|NDCYcle|CYCarea|CYCMean|CYCRms|CYCStddev|CYCCrest|CAMPlitude|CMAXimum|CMINimum|CPDelta|PULCnt|DELay|PHASe|BWIDth|EDGecount|SETup|HOLD|SHT|SHR|DTOTrigger|SLERising|SLEFalling"
param_list = params_str.split('|')

# 3. UI SETUP
fig, (ax_hist, ax_trend) = plt.subplots(2, 1, figsize=(14, 9))
plt.subplots_adjust(left=0.3, hspace=0.45)

# Configurare formatare axe (Zecimal Plain)
decimal_formatter = ScalarFormatter(useOffset=False)
decimal_formatter.set_scientific(False)

# Widget-uri UI
ax_menu = plt.axes([0.02, 0.25, 0.18, 0.65], facecolor='#f0f0f0')
radio = RadioButtons(ax_menu, param_list, active=param_list.index("FREQuency"))

ax_box = plt.axes([0.1, 0.18, 0.1, 0.04])
text_box = TextBox(ax_box, 'Prag Alertă: ', initial=str(threshold_value))

ax_btn_update = plt.axes([0.05, 0.10, 0.15, 0.05])
btn_update = Button(ax_btn_update, 'Actualizează Parametru', color='lightgreen', hovercolor='green')

ax_btn_reset = plt.axes([0.05, 0.03, 0.15, 0.05])
btn_reset = Button(ax_btn_reset, 'Resetare Statistică', color='#ffcc66', hovercolor='#ff9933')

# --- FUNCTII DE CONTROL ---
def update_threshold(text):
    global threshold_value
    try:
        threshold_value = float(text)
    except ValueError: pass

text_box.on_submit(update_threshold)

def reset_stats(event):
    global data, std_history
    data, std_history = [], []

btn_reset.on_clicked(reset_stats)

def update_measurement(event):
    global current_meas_type
    selected = radio.value_selected
    current_meas_type = selected
    try:
        new_type = getattr(MeasType, selected)
        mxo.measurement.main.set(meas_type=new_type, measIndex=m1)
        reset_stats(None)
    except Exception as e: print(f"Eroare: {e}")

btn_update.on_clicked(update_measurement)

# --- LOOP-UL DE UPDATE ---
def update(frame):
    try:
        val = mxo.measurement.result.actual.get(measIndex=m1)
        
        if val < 1e10:
            data.append(val)
            if len(data) > max_points: data.pop(0)
            
            if len(data) >= window_size:
                std_history.append(np.std(data[-window_size:]))
                if len(std_history) > max_points: std_history.pop(0)

        if frame % 2 == 0 and len(data) > 1:
            # Update Histogramă
            ax_hist.clear()
            ax_hist.hist(data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
            ax_hist.set_title(f"Parameter: {current_meas_type}\n"
                             f"Min: {np.min(data):.9f} | Mean: {np.mean(data):.9f} | Max: {np.max(data):.9f}")
            
            # Aplicare format zecimal pe axa X a histogramei
            ax_hist.xaxis.set_major_formatter(decimal_formatter)
            
            # Update Trend
            if len(std_history) > 0:
                ax_trend.clear()
                last_std = std_history[-1]
                ax_trend.plot(std_history, color='red', linewidth=1.2)
                ax_trend.axhline(y=threshold_value, color='black', linestyle='--', linewidth=2)
                
                # Aplicare format zecimal pe axa Y a trendului
                ax_trend.yaxis.set_major_formatter(decimal_formatter)
                
                if last_std > threshold_value:
                    ax_trend.set_facecolor('#ffcccc')
                    #ax_trend.set_title(f"⚠️ OverLine!: {last_std:.4f}", color='darkred', fontweight='bold')
                    ax_trend.set_title(f"Track {current_meas_type} ({last_std:.4f})")
                else:
                    ax_trend.set_facecolor('#f9f9f9')
                    ax_trend.set_title(f"Track {current_meas_type} ({last_std:.4f})")

                ax_trend.set_ylim(0, max(threshold_value * 1.2, max(std_history) * 1.1) if std_history else 1)
                ax_trend.grid(True, linestyle=':', alpha=0.0000005)
                
    except Exception: pass
    return []

ani = FuncAnimation(fig, update, interval=1, cache_frame_data=False)
plt.show()
mxo.close()
