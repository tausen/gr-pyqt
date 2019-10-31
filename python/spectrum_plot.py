#!/usr/bin/env python
#
# Copyright 2014 Tim O'Shea
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
from plotter_base import *
class spectrum_plot(plotter_base):
    def __init__(self, label="", nsteps=1, *args):
        plotter_base.__init__(self, blkname="spectrum_plot", label=label, *args)
        self.message_port_register_in(pmt.intern("pdus"));
        self.set_msg_handler(pmt.intern("pdus"), self.handler);

        self.setCanvasBackground(Qt.Qt.white)

        # set up curves
        cd = []
        for i in range(nsteps):
            curve = Qwt.QwtPlotCurve("X{}(n)".format(i));
            curve.attach(self);
            self.curves.append(curve);
            curve.setPen( Qt.QPen(Qt.Qt.blue) )
            cd.append(([],[]))

        # enable axes
        self.toggle_axes()
        self.toggle_grid()
        
        self.curve_data = cd
        self.reset_freqs()

    def reset_freqs(self):
        self.f_to_idx = {}
        self.max_cidx = 0

    def handler(self, msg):

        # get input
        meta = pmt.to_python(pmt.car(msg));
        samples = pmt.cdr(msg);
        x = pmt.to_python(pmt.cdr(msg))

        k = str(meta["f"])
        if k in self.f_to_idx.keys():
            cidx = self.f_to_idx[k]
        else:
            if self.max_cidx  >= len(self.curve_data):
                # nsteps not high enough, config probably changed - reset
                self.reset_freqs()

            cidx = self.max_cidx
            self.max_cidx += 1
            self.f_to_idx[k] = cidx

        # pass data
        dom = numpy.array(numpy.fft.fftshift(numpy.fft.fftfreq(len(x), d=1.0/meta["fs"]))+meta["f"], dtype=numpy.float32)
        self.curve_data[cidx] = (dom, x)

        # trigger update
        self.emit(QtCore.SIGNAL("updatePlot(int)"), 0)
    


