#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Rtty Demod
# Generated: Sun May 28 09:23:19 2017
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import radioteletype
import sip
import sys
from gnuradio import qtgui


class rtty_demod(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Rtty Demod")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Rtty Demod")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "rtty_demod")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.spacing = spacing = 170
        self.mark = mark = 2000+spacing/2
        self.space = space = mark-spacing/2
        self.samp_rate = samp_rate = 8000
        self.decimation = decimation = 22
        self.baud = baud = 45.45

        ##################################################
        # Blocks
        ##################################################
        self.radioteletype_rtty_demod_cb_0 = radioteletype.rtty_demod_cb(
            alpha=0.35,
            baud=baud,
            decimation=1,
            mark_freq=mark,
            samp_rate=samp_rate,
            space_freq=space,
        )
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	samp_rate, #bw
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)

        if not True:
          self.qtgui_freq_sink_x_0.disable_legend()

        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_0.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.hilbert_fc_0 = filter.hilbert_fc(65, firdes.WIN_HAMMING, 6.76)
        self.gr_wavfile_source_0 = blocks.wavfile_source('./rtty.wav', True)
        self.gr_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/dev/stdout', True)
        self.gr_file_sink_0.set_unbuffered(True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.radioteletype_rtty_demod_cb_0, 0))
        self.connect((self.gr_wavfile_source_0, 0), (self.hilbert_fc_0, 0))
        self.connect((self.hilbert_fc_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.radioteletype_rtty_demod_cb_0, 0), (self.gr_file_sink_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rtty_demod")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_spacing(self):
        return self.spacing

    def set_spacing(self, spacing):
        self.spacing = spacing
        self.set_space(self.mark-self.spacing/2)
        self.set_mark(2000+self.spacing/2)

    def get_mark(self):
        return self.mark

    def set_mark(self, mark):
        self.mark = mark
        self.set_space(self.mark-self.spacing/2)
        self.radioteletype_rtty_demod_cb_0.set_mark_freq(self.mark)

    def get_space(self):
        return self.space

    def set_space(self, space):
        self.space = space
        self.radioteletype_rtty_demod_cb_0.set_space_freq(self.space)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.radioteletype_rtty_demod_cb_0.set_samp_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_baud(self):
        return self.baud

    def set_baud(self, baud):
        self.baud = baud
        self.radioteletype_rtty_demod_cb_0.set_baud(self.baud)


def main(top_block_cls=rtty_demod, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
