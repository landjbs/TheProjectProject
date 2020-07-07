from pyo import *
from time import time, sleep


WAVEFORM_IDX = {0 : Sine,
                1 : SuperSaw}
                # 2 : Pulse,
                # 3 : Square}


class Oscillator(object):
    def __init__(self, freq, waveform):
        self.env = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=0.5, mul=.5)
        # self.osc = WAVEFORM_IDX[0](mul=self.env)
        self.osc = WAVEFORM_IDX[waveform](freq, 0, 0.1)

    def set_env(self, a=None, d=None, s=None, r=None):
        if a:
            self.env.attack = a
        if d:
            self.env.decay = d
        if s:
            self.env.sustain = s
        if r:
            self.env.release = r

    def play(self):
        self.osc.out()


class Synth(object):
    def __init__(self):
        self.server = Server().boot()
        self.osc_1 = Oscillator(440, 0)
        self.osc_2 = Oscillator(440, 0)

    def modify_params(self):
        pass

    def play(self):
        self.server.start()
        sleep(10)
        self.server.stop()

    def play_to_wav(self, outpath, dur=1):
        self.server.recordOptions(dur=dur, filename=outpath,
                                  fileformat=0, sampletype=1)
        self.server.start()
        self.server.recstart()
        sleep(dur)
        self.server.stop()


    def launch_gui(self):
        sc = Scope([self.osc_1.osc, self.osc_2.osc])
        self.server.gui(locals())


x = Synth()
x.play_to_wav('test_sine.wav')

# from pyo import *
# from time import time, sleep
# import numpy as np
# import matplotlib.pyplot as plt
#
# s = Server().boot()
# bs = s.getBufferSize()
#
# # Create a table of length `buffer size` and read it in loop.
# t = DataTable(size=bs)
# osc = TableRead(t, freq=t.getRate(), loop=True, mul=0.1).out()
#
# # Share the table's memory with a numpy array.
# arr = np.asarray(t.getBuffer())
#
# def process():
#     "Fill the array (so the table) with white noise."
#     arr[:] = np.random.uniform(0.0, 0.0, size=bs)
#
# # Register the `process` function to be called at the beginning
# # of every processing loop.
# s.setCallback(process)
#
# s.start()
# s = time()
# while time()-s < 3:
#     sleep(0.1)
#
# plt.plot(t)
# plt.show()
#
#
# # plt.plot(arr)
# # plt.show()
#
# s.end()
# # s.gui(locals())
