import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from RsMxo import *

class MXO4ExpertConsoleV19(QtWidgets.QWidget):
    def __init__(self, resource_str):
        super().__init__()
        self.resource_str = resource_str
        self.setWindowTitle("R&S MXO4 - FW 2.8.2.0 Optimized V19")
        self.resize(1400, 950)
        
        self.mxo = None
        self.timer = None
        self.hist_data = [] 
        
       
        self.param_list = "HIGH|LOW|AMPLitude|MAXimum|MINimum|PDELta|PEAK|MEAN|RMS|STDDev|CRESt|POVershoot|NOVershoot|AREA|RTIMe|FTIMe|PPULse|NPULse|PERiod|FREQuency|PDCYcle|NDCYcle|CYCarea|CYCMean|CYCRms|CYCStddev|CYCCrest|CAMPlitude|CMAXimum|CMINimum|CPDelta|PULCnt|DELay|PHASe|BWIDth|EDGecount|SETup|HOLD|SHT|SHR|DTOTrigger|SLERising|SLEFalling".split('|')
        
        self.setup_ui()
        QtCore.QTimer.singleShot(500, self.connect_instrument)

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        
       
        left_container = QtWidgets.QWidget()
        l_lay = QtWidgets.QVBoxLayout(left_container)
        
        self.pw_wave = pg.PlotWidget(title="Live Waveform (CH1) - Real-time Sync")
        self.pw_wave.showGrid(x=True, y=True, alpha=0.3)
        self.curve_wave = self.pw_wave.plot(pen=pg.mkPen('#00FF00', width=1.5))
        
        self.pw_wave.setMouseEnabled(x=False, y=False)
        self.pw_wave.enableAutoRange(enable=False)
        l_lay.addWidget(self.pw_wave)
        
        self.pw_hist = pg.PlotWidget(title="Measurement Distribution (Histogram)")
        self.pw_hist.setBackground('k')
        self.hist_curve = self.pw_hist.plot(pen='#55AAFF', brush=(85, 170, 255, 100), fillLevel=0, stepMode="center")
        l_lay.addWidget(self.pw_hist)
        
       
        self.right_panel = QtWidgets.QGroupBox("Instrument Controls")
        self.right_panel.setFixedWidth(350)
        self.m_lay = QtWidgets.QVBoxLayout(self.right_panel)
        
        
        self.lbl_val = QtWidgets.QLabel("--")
        self.lbl_val.setStyleSheet("font-family: 'Consolas'; font-size: 28pt; color: #00FF00; font-weight: bold; background-color: #000; border: 2px solid #333; border-radius: 8px; padding: 15px;")
        self.lbl_val.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.m_lay.addWidget(self.lbl_val)

        # Measurements
        meas_group = QtWidgets.QGroupBox("Measurement")
        meas_lay = QtWidgets.QVBoxLayout(meas_group)
        self.combo_meas = QtWidgets.QComboBox()
        self.combo_meas.addItems(self.param_list)
        self.combo_meas.setCurrentText("FREQuency")
        meas_lay.addWidget(self.combo_meas)
        btn_apply = self.create_styled_button("SET MEASUREMENT", self.update_measurement)
        meas_lay.addWidget(btn_apply)
        self.m_lay.addWidget(meas_group)

        # Positioning (Vertical & Horizontal)
        self.ctrl_group = QtWidgets.QGroupBox("Signal Positioning")
        ctrl_lay = QtWidgets.QVBoxLayout(self.ctrl_group)
        
        # Vertical
        ctrl_lay.addWidget(QtWidgets.QLabel("Vertical Scale & Offset:"))
        v_lay = QtWidgets.QHBoxLayout()
        v_lay.addWidget(self.create_styled_button("V-", lambda: self.adjust_vertical(0.8)))
        v_lay.addWidget(self.create_styled_button("V+", lambda: self.adjust_vertical(1.2)))
        ctrl_lay.addLayout(v_lay)

        vo_lay = QtWidgets.QHBoxLayout()
        vo_lay.addWidget(self.create_styled_button("▼", lambda: self.adjust_vertical_offset(-1)))
        vo_lay.addWidget(self.create_styled_button("0", self.reset_vertical_offset))
        vo_lay.addWidget(self.create_styled_button("▲", lambda: self.adjust_vertical_offset(1)))
        ctrl_lay.addLayout(vo_lay)

        # Horizontal
        ctrl_lay.addWidget(QtWidgets.QLabel("Horizontal Timebase & Position:"))
        h_lay = QtWidgets.QHBoxLayout()
        h_lay.addWidget(self.create_styled_button("T-", lambda: self.adjust_horizontal(0.5)))
        h_lay.addWidget(self.create_styled_button("T+", lambda: self.adjust_horizontal(2.0)))
        ctrl_lay.addLayout(h_lay)

        hp_lay = QtWidgets.QHBoxLayout()
        hp_lay.addWidget(self.create_styled_button("◀", lambda: self.adjust_horizontal_offset(-1)))
        hp_lay.addWidget(self.create_styled_button("0", self.reset_horizontal_offset))
        hp_lay.addWidget(self.create_styled_button("▶", lambda: self.adjust_horizontal_offset(1)))
        ctrl_lay.addLayout(hp_lay)
        
        self.m_lay.addWidget(self.ctrl_group)

        # System Buttons
        self.btn_autoset = self.create_styled_button("AUTOSET", self.run_autoset)
        self.m_lay.addWidget(self.btn_autoset)

        rs_lay = QtWidgets.QHBoxLayout()
        self.btn_run = QtWidgets.QPushButton("RUN")
        self.btn_stop = QtWidgets.QPushButton("STOP")
        self.btn_run.setMinimumHeight(45)
        self.btn_stop.setMinimumHeight(45)
        self.btn_run.clicked.connect(lambda: self.set_acquisition(True))
        self.btn_stop.clicked.connect(lambda: self.set_acquisition(False))
        rs_lay.addWidget(self.btn_run)
        rs_lay.addWidget(self.btn_stop)
        self.m_lay.addLayout(rs_lay)

        self.m_lay.addStretch()
        self.status_led = QtWidgets.QLabel("Status: Offline")
        self.m_lay.addWidget(self.status_led)
        
        main_layout.addWidget(left_container)
        main_layout.addWidget(self.right_panel)

    
    def create_styled_button(self, text, callback):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(35)
        def on_click():
            btn.setStyleSheet("background-color: #00A0FF; color: black; font-weight: bold; border: 1px solid white;")
            QtCore.QTimer.singleShot(150, lambda: btn.setStyleSheet(""))
            callback()
        btn.clicked.connect(on_click)
        return btn

    def set_acquisition(self, state):
        if self.mxo:
            try:
                self.mxo.utilities.write_str("RUN" if state else "STOP")
                if state:
                    self.btn_run.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; border: 2px solid #4CAF50;")
                    self.btn_stop.setStyleSheet("")
                else:
                    self.btn_stop.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; border: 2px solid #FF5252;")
                    self.btn_run.setStyleSheet("")
            except: pass

    
    def connect_instrument(self):
        try:
            self.mxo = RsMxo(self.resource_str, id_query=True)
            self.mxo.utilities.visa_timeout = 2500
            self.status_led.setText(f"🟢 {self.mxo.utilities.idn_string.split(',')[1]}")
            self.set_acquisition(True) 
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_loop)
            self.timer.start(40) # 25 FPS update
        except: self.status_led.setText("🔴 Connection Error")

    def update_measurement(self):
        if self.mxo:
            try:
                sel = self.combo_meas.currentText()
                self.mxo.measurement.main.set(meas_type=getattr(enums.MeasType, sel), measIndex=repcap.MeasIndex.Nr1)
                self.reset_histogram()
            except: pass

    def run_autoset(self):
        if self.mxo: self.mxo.utilities.write_str("AUT")

    def adjust_horizontal(self, factor):
        if self.mxo:
            curr = float(self.mxo.utilities.query_str("TIMebase:SCALe?"))
            self.mxo.utilities.write_str(f"TIMebase:SCALe {curr * factor}")

    def adjust_vertical(self, factor):
        if self.mxo:
            curr = float(self.mxo.utilities.query_str("CHANnel1:SCALe?"))
            self.mxo.utilities.write_str(f"CHANnel1:SCALe {curr * factor}")

    def adjust_vertical_offset(self, direction):
        if self.mxo:
            scale = float(self.mxo.utilities.query_str("CHANnel1:SCALe?"))
            curr = float(self.mxo.utilities.query_str("CHANnel1:OFFSet?"))
            self.mxo.utilities.write_str(f"CHANnel1:OFFSet {curr + (direction * scale)}")

    def reset_vertical_offset(self):
        if self.mxo: self.mxo.utilities.write_str("CHANnel1:OFFSet 0")

    def adjust_horizontal_offset(self, direction):
        if self.mxo:
            scale = float(self.mxo.utilities.query_str("TIMebase:SCALe?"))
            curr = float(self.mxo.utilities.query_str("TIMebase:HORizontal:POSition?"))
            self.mxo.utilities.write_str(f"TIMebase:HORizontal:POSition {curr + (direction * scale)}")

    def reset_horizontal_offset(self):
        if self.mxo: self.mxo.utilities.write_str("TIMebase:HORizontal:POSition 0")

    def reset_histogram(self):
        self.hist_data = []
        self.hist_curve.setData([], [])

    def update_loop(self):
        if not self.mxo: return
        try:
            
            raw = self.mxo.utilities.query_bin_or_ascii_float_list("CHANnel1:DATA?")
            if raw:
                
                v_scale = float(self.mxo.utilities.query_str("CHANnel1:SCALe?"))
                v_offset = float(self.mxo.utilities.query_str("CHANnel1:OFFSet?"))
                h_scale = float(self.mxo.utilities.query_str("TIMebase:SCALe?"))
                h_pos = float(self.mxo.utilities.query_str("TIMebase:HORizontal:POSition?"))

                y_min, y_max = v_offset - (4 * v_scale), v_offset + (4 * v_scale)
                x_min, x_max = h_pos - (5 * h_scale), h_pos + (5 * h_scale)
                
                time_axis = np.linspace(x_min, x_max, len(raw))
                self.curve_wave.setData(time_axis, np.array(raw))
                self.pw_wave.setYRange(y_min, y_max, padding=0)
                self.pw_wave.setXRange(x_min, x_max, padding=0)
            
           
            val = self.mxo.measurement.result.actual.get(measIndex=repcap.MeasIndex.Nr1)
            if val < 1e10:
                formatted_val = f"{val:.6f}".rstrip('0').rstrip('.')
                if abs(val) < 1e-9: formatted_val = "0"
                self.lbl_val.setText(formatted_val)
                
                self.hist_data.append(val)
                if len(self.hist_data) > 1000: self.hist_data.pop(0)
                if len(self.hist_data) > 5:
                    y, x = np.histogram(self.hist_data, bins=40)
                    self.hist_curve.setData(x, y)
        except: pass

    def closeEvent(self, event):
        if self.timer: self.timer.stop()
        if self.mxo:
            self.mxo.utilities.write_str("&GTL")
            self.mxo.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    view = MXO4ExpertConsoleV19('TCPIP::192.168.1.25::hislip0')
    view.show()
    sys.exit(app.exec())