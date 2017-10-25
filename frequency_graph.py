import tkinter as tk
import random
import alsaaudio, audioop
import time
from audio_transformation import apply_fft
import math
import pyaudio


# inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)

# inp.setchannels(1)
# inp.setrate(8000)
# inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# inp.setperiodsize(160)
p = pyaudio.PyAudio()



CHUNK = 511
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

WIDTH = 1366
HEIGHT = 768

DELAY = 10
STEP = 1

class FrequencyDrawing(tk.Tk):
    def __init__(self):
        super(FrequencyDrawing, self).__init__()
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="black", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.index = 1
        self.path = []
        self.line_width = 1
        self.mic_data = []

        self.drawings = {}
        # self.after(0, self.read_mic_data)
        self.after(10, self.draw_frequencies)


    def create_circle_centered(self, pos, r, **kwargs):
        x, y = pos
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)


    def create_rectangle_at_angle(self, pos, angle, height, **kwargs):
        x, y = pos
        rads = math.radians(angle)

        self.canvas.create_rectangle(
            x,
            y,
            x + (height*math.sin(rads)),
            y + (height*math.cos(rads)),
            **kwargs
        )


    def unpack_path(self, file):
        with open(file, 'r') as file:
            for line in file.readlines():
                self.path.append([int(i) for i in line.split(';')])


    def read_mic_data(self):
        self.mic_data = stream.read(CHUNK)
        self.after(10, self.read_mic_data)


    def draw_frequencies(self):
        self.mic_data = stream.read(CHUNK)
        # self.after(10, self.read_mic_data)        

        self.canvas.delete('all')

        center = (int(WIDTH/2), int(HEIGHT/2))

        frequencies = apply_fft(self.mic_data)
        x_step = int(WIDTH / len(frequencies))
        # lows_top = 10
        # mids_top = (len(frequencies) - lows_top)
        # highs_top = len(frequencies)

        # lows_val = min(int(WIDTH/2), (sum(frequencies[1:lows_top])/lows_top))
        # red_value = int((lows_val*(255))/(WIDTH/2))
        # self.create_circle_centered(
        #     center,
        #     lows_val,
        #     fill='#%02x%02x%02x' % (red_value, max(0, 100-red_value), max(0, 100-red_value))
        # )

        # for index in range(lows_top, mids_top):
        #     angle = (index*360)/(mids_top-lows_top)
        #     self.create_rectangle_at_angle(
        #         center,
        #         angle,
        #         frequencies[index],
        #         fill='white'
        #     )
        # for index in range(mids_top, highs_top):

        print(max(frequencies))
        for index in range(1, len(frequencies)):
            x0 = index*x_step
            x1 = (index+1)*x_step
            height = (frequencies[index]/16776704)*255*2
            try:
                self.canvas.create_rectangle(x0, 0, x1, height, fill='white')
            except:
                pass

        # start = time.time()
        self.after(DELAY, self.draw_frequencies)


app = FrequencyDrawing()
app.mainloop()
