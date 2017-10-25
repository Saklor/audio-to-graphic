import tkinter as tk
import random
import audioop
import pyaudio
import time

from os import listdir
from os.path import isfile, join
from math import ceil

from audio_transformation import apply_fft

p = pyaudio.PyAudio()



CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44000

WIDTH = 1366
HEIGHT = 768

DELETE_SPACING = 50

DRAWING_STEP_DELAY = 10
STATIC_DRAWING_TIME = 5000

MAX_FFT_READING = 8388352/2
FFT_BIN_FREQ_RANGE = int(RATE/ceil(CHUNK/2)) #Freq range of each bin


class PathDrawing(tk.Tk):
    def __init__(self, arg):
        super(PathDrawing, self).__init__()
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="white", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.index = 0
        self.line_width = 1
        self.color = 'white'
        
        self.path = []
        self.paths = []
        self.drawings = {}

        self.lap = 0


        self.stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

        self.unpack_paths(arg)
        self.path = random.choice(self.paths)
        print ([len(a) for a in self.paths])
        self.after(0, self.draw_on_path)


    def create_circle_centered(self, pos, r, **kwargs):
        x, y = pos
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)


    def unpack_paths(self, dir):
        onlyfiles = [join(dir,f) for f in listdir(dir) if isfile(join(dir, f)) and f.endswith('out')]
        for file in onlyfiles:
            current_file_path = []
            with open(file, 'r') as file:
                for line in file.readlines():
                    current_file_path.append([int(i) for i in line.split(';')])
            self.paths.append(current_file_path)


    def rgb_to_hex(self, r, g, b):
        return '#%02x%02x%02x' % (r, g, b)


    def max_bass_level(self, fft_data):
        return max(fft_data[:(int(2000/FFT_BIN_FREQ_RANGE))])

    def max_harmonics_level(self, fft_data):
        return max(fft_data[(int(2000/FFT_BIN_FREQ_RANGE)):(int(8000/FFT_BIN_FREQ_RANGE))])

    def max_high_level(self, fft_data):
        return max(fft_data[(int(8000/FFT_BIN_FREQ_RANGE)):(int(17000/FFT_BIN_FREQ_RANGE))])


    def delete_index_drawing(self, index):
        if index in self.drawings:
            self.canvas.delete(self.drawings[index])
            del(self.drawings[index])


    def draw_on_path(self):
        mic_data = self.stream.read(CHUNK)
        fft_data = apply_fft(mic_data)


        index_to_delete = ((self.index + DELETE_SPACING) % len(self.path))
        if index_to_delete > self.index or self.lap == 0:
            self.delete_index_drawing(index_to_delete)



        self.line_width = int((audioop.max(mic_data, 2)/32768) * 15)
        self.color = self.rgb_to_hex(
            min(255, int(self.max_bass_level(fft_data)/MAX_FFT_READING*255)),
            min(255, int(self.max_harmonics_level(fft_data)/MAX_FFT_READING*255)),
            min(255, int(self.max_high_level(fft_data)/MAX_FFT_READING*255))
        )

        if self.line_width > 2:
            self.drawings[self.index] = self.create_circle_centered(self.path[self.index], self.line_width, fill=self.color, outline='')



        self.index += 1
        if self.index >= len(self.path):
            self.lap += 1
            self.index = self.index % len(self.path)

        if self.lap > 1:
            self.index = 0
            self.stream.stop_stream()
            self.after(STATIC_DRAWING_TIME, self.delete_drawings)
        else:
            self.after(DRAWING_STEP_DELAY, self.draw_on_path)


    def delete_drawings(self):
        self.delete_index_drawing(self.index)

        self.index += 1
        if self.index < len(self.path):
            self.after(1, self.delete_drawings)
        else:
            self.index = 0
            self.lap = 0
            self.path = random.choice(self.paths)
            self.stream.start_stream()
            self.after(DRAWING_STEP_DELAY, self.draw_on_path)


app = PathDrawing('caminos')
app.mainloop()