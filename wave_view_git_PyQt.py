import sys
import numpy as np
import pyqtgraph as pg
import datetime
from pyqtgraph.Qt import QtCore, QtWidgets
from RsMxo import *

class MXO4CompleteConsole(QtWidgets.QWidget):
    def __init__(self, resource_str):
        super().__init__()
        self.resource_str = resource_str
        self.setWindowTitle("R&S MXO4 - Basic Remote Console")
        self.resize(1400, 900)
        
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
        
        self.pw_wave = pg.PlotWidget(title="Live Waveform (CH1)")
        self.curve_wave = self.pw_wave.plot(pen=pg.mkPen('#00FF00', width=1.5))
        l_lay.addWidget(self.pw_wave)
        
        self.pw_hist = pg.PlotWidget(title="Measurement Distribution (Histogram)")
        self.pw_hist.setBackground('k')
        self.hist_curve = self.pw_hist.plot(pen='#55AAFF', brush=(85, 170, 255, 100), fillLevel=0, stepMode="center")
        l_lay.addWidget(self.pw_hist)
        
        self.right_panel = QtWidgets.QGroupBox("Instrument Controls")
        self.right_panel.setFixedWidth(330)
        self.m_lay = QtWidgets.QVBoxLayout(self.right_panel)
        
        
        self.lbl_val = QtWidgets.QLabel("--")
        self.lbl_val.setStyleSheet("font-family: 'Consolas'; font-size: 24pt; color: #00FF00; font-weight: bold; margin-bottom: 5px;")
        self.lbl_val.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.m_lay.addWidget(self.lbl_val)

        
        self.meas_group = QtWidgets.QGroupBox("Measurements")
        meas_lay = QtWidgets.QVBoxLayout(self.meas_group)
        self.combo_meas = QtWidgets.QComboBox()
        self.combo_meas.addItems(self.param_list)
        self.combo_meas.setCurrentText("STDDev")
        meas_lay.addWidget(self.combo_meas)
        
        self.btn_apply = QtWidgets.QPushButton("APPLY MEASUREMENT")
        self.btn_apply.setStyleSheet("font-weight: bold; min-height: 30px;")
        self.btn_apply.clicked.connect(self.update_measurement)
        meas_lay.addWidget(self.btn_apply)
        self.m_lay.addWidget(self.meas_group)

        
        self.btn_autoset = QtWidgets.QPushButton("AUTOSET")
        self.btn_autoset.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; min-height: 40px;")
        self.btn_autoset.clicked.connect(self.run_autoset)
        self.m_lay.addWidget(self.btn_autoset)

        
        self.scale_group = QtWidgets.QGroupBox("Scales")
        scale_lay = QtWidgets.QVBoxLayout(self.scale_group)
        
        
        scale_lay.addWidget(QtWidgets.QLabel("Vertical (V/div):"))
        v_lay = QtWidgets.QHBoxLayout()
        btn_v_dn = QtWidgets.QPushButton("V-")
        btn_v_up = QtWidgets.QPushButton("V+")
        btn_v_dn.clicked.connect(lambda: self.adjust_vertical(0.8))
        btn_v_up.clicked.connect(lambda: self.adjust_vertical(1.2))
        v_lay.addWidget(btn_v_dn); v_lay.addWidget(btn_v_up)
        scale_lay.addLayout(v_lay)
        
        
        scale_lay.addWidget(QtWidgets.QLabel("Horizontal (Time/div):"))
        h_lay = QtWidgets.QHBoxLayout()
        btn_h_dn = QtWidgets.QPushButton("T-")
        btn_h_up = QtWidgets.QPushButton("T+")
        btn_h_dn.clicked.connect(lambda: self.adjust_horizontal(0.5))
        btn_h_up.clicked.connect(lambda: self.adjust_horizontal(2.0))
        h_lay.addWidget(btn_h_dn); h_lay.addWidget(btn_h_up)
        scale_lay.addLayout(h_lay)
        
        self.m_lay.addWidget(self.scale_group)

       
        rs_lay = QtWidgets.QHBoxLayout()
        btn_run = QtWidgets.QPushButton("RUN")
        btn_run.clicked.connect(lambda: self.set_acquisition(True))
        btn_stop = QtWidgets.QPushButton("STOP")
        btn_stop.clicked.connect(lambda: self.set_acquisition(False))
        rs_lay.addWidget(btn_run); rs_lay.addWidget(btn_stop)
        self.m_lay.addLayout(rs_lay)

        self.btn_reset_h = QtWidgets.QPushButton("RESET HISTOGRAM")
        self.btn_reset_h.clicked.connect(self.reset_histogram)
        self.m_lay.addWidget(self.btn_reset_h)

        self.m_lay.addStretch()
        self.status_led = QtWidgets.QLabel("Status: Offline")
        self.m_lay.addWidget(self.status_led)
        
        main_layout.addWidget(left_container)
        main_layout.addWidget(self.right_panel)

    def connect_instrument(self):
        try:
            self.mxo = RsMxo(self.resource_str, id_query=False)
            self.mxo.utilities.visa_timeout = 2500
            m1 = repcap.MeasIndex.Nr1
            self.mxo.measurement.source.set(signal_source=enums.SignalSource.C1, measIndex=m1)
            self.mxo.measurement.enable.set(state=True, measIndex=m1)
            self.status_led.setText("🟢 Online")
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_loop)
            self.timer.start(40)
        except Exception as e:
            self.status_led.setText("🔴 Error")

    def update_measurement(self):
        if self.mxo:
            try:
                selected = self.combo_meas.currentText()
                new_type = getattr(enums.MeasType, selected)
                self.mxo.measurement.main.set(meas_type=new_type, measIndex=repcap.MeasIndex.Nr1)
                self.reset_histogram()
            except: pass

    def run_autoset(self):
        if self.mxo: self.mxo.utilities.write_str("AUT")

    def set_acquisition(self, state):
        if self.mxo: self.mxo.utilities.write_str("RUN" if state else "STOP")

    def adjust_horizontal(self, factor):
        if self.mxo:
            try:
                curr = float(self.mxo.utilities.query_str("TIM:SCAL?"))
                self.mxo.utilities.write_str(f"TIM:SCAL {curr * factor}")
            except: pass

    def adjust_vertical(self, factor):
        if self.mxo:
            try:
                curr = float(self.mxo.utilities.query_str("CHAN1:SCAL?"))
                self.mxo.utilities.write_str(f"CHAN1:SCAL {curr * factor}")
            except: pass

    def reset_histogram(self):
        self.hist_data = []
        self.hist_curve.setData([], [])

    def update_loop(self):
        if not self.mxo: return
        try:
            # Waveform
            raw = self.mxo.utilities.query_bin_or_ascii_float_list("CHAN1:DATA?")
            if raw: self.curve_wave.setData(np.array(raw))
            # Meas & Hist
            val = self.mxo.measurement.result.actual.get(measIndex=repcap.MeasIndex.Nr1)
            if val < 1e10:
                self.lbl_val.setText(f"{val:.4e}")
                self.hist_data.append(val)
                if len(self.hist_data) > 1000: self.hist_data.pop(0)
                if len(self.hist_data) > 5:
                    y, x = np.histogram(self.hist_data, bins=100)
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
    view = MXO4CompleteConsole('TCPIP::192.168.1.25::hislip0')
    view.show()
    sys.exit(app.exec())