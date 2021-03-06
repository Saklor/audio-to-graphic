import tkinter as tk
import random
import audioop
import pyaudio
import time

from os import listdir
from os.path import isfile, join
from math import ceil, sin, cos

from audio_transformation import apply_fft

# MODIFICAR ACA SI EL VOLUMEN ESTA BAJO O LOS COLORES APAGADOS

# Este valor indica cual es la sensibilidad del volumen del microfono.
# Si se quiere que las formas sean mas grandes, aumentar este valor (probar con 4 o 6)
MAX_MIC_READING_MODIFIER = 2

# Este valor indica cual es la sensibilidad de las frecuencias
# Si se quiere que las formas tengan colores mas claros aumentar este valor (probar con 6 u 8)
MAX_FFT_READING_MODIFIER = 4


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44000

WIDTH = 1366
HEIGHT = 768

DELETE_SPACING = 50

DRAWING_STEP_DELAY = 10
STATIC_DRAWING_TIME = 5000

p = pyaudio.PyAudio()

MAX_FFT_READING = 8388352/MAX_FFT_READING_MODIFIER
MAX_MIC_READING = 32768/MAX_MIC_READING_MODIFIER
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
        self.shapes = ['circle', 'square']
        self.drawings = {}

        self.color_order = [0,1,2]
        self.shape = self.shapes[0]

        self.lap = 0

        self.drawing_step = 1

        self.stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

        self.unpack_paths(arg)
        self.set_random_variables()
        print ([len(a) for a in self.paths])
        self.after(0, self.draw_on_path)


    def create_circle_centered(self, pos, r, **kwargs):
        x, y = pos
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)


    def create_square_centered_and_rotated(self, pos, size, rotation, **kwargs):
        coords = []
        corner_variation = [
            (-size, -size),
            (-size, size),
            (size, size),
            (size, -size)
        ]

        for corner in [tuple(map(lambda x, y: x + y, elem, pos)) for elem in corner_variation]:
            tempX = corner[0] - pos[0]
            tempY = corner[1] - pos[1]

            rotatedX = tempX*cos(rotation) - tempY*sin(rotation)
            rotatedY = tempX*sin(rotation) + tempY*cos(rotation)

            x = rotatedX + pos[0]
            y = rotatedY + pos[1]
            coords.append((x,y))

        return self.canvas.create_polygon(coords, **kwargs)


    def set_random_variables(self):
        # Random path
        self.path = random.choice(self.paths)
        if (len(self.path) > 5000):
            self.drawing_step = 2
        else:
            self.drawing_step = 1

        # Random color order
        random.shuffle(self.color_order)

        # Random shape
        self.shape = random.choice(self.shapes)


    def unpack_paths(self, dir):
        onlyfiles = [join(dir,f) for f in listdir(dir) if isfile(join(dir, f)) and f.endswith('out')]
        for file in onlyfiles:
            current_file_path = []
            with open(file, 'r') as file:
                for line in file.readlines():
                    current_file_path.append([int(i) for i in line.split(';')])
            self.paths.append(current_file_path)


    def rgb_to_hex(self, rgb):
        r, g, b = rgb
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
        mic_data = self.stream.read(CHUNK, exception_on_overflow = False)
        fft_data = apply_fft(mic_data)



        for index_to_check in range(self.index, self.index + self.drawing_step):
            index_to_delete = ((index_to_check + DELETE_SPACING) % len(self.path))
            if index_to_delete > self.index or self.lap == 0:
                self.delete_index_drawing(index_to_delete)



        self.line_width = min(int((audioop.max(mic_data, 2)/MAX_MIC_READING) * 15), 15)
        rgb = [
            min(255, int(self.max_bass_level(fft_data)/MAX_FFT_READING*255)),
            min(255, int(self.max_harmonics_level(fft_data)/MAX_FFT_READING*255)),
            min(255, int(self.max_high_level(fft_data)/MAX_FFT_READING*255))
        ]
        rgb = [rgb[i] for i in self.color_order]
        self.color = self.rgb_to_hex(rgb)

        if self.line_width > 2:
            if self.shape == 'square':
                self.drawings[self.index] = self.create_square_centered_and_rotated(
                    self.path[self.index],
                    self.line_width,
                    random.randint(0,360),
                    fill=self.color,
                    outline=''
                )
            elif self.shape == 'circle':
                self.drawings[self.index] = self.create_circle_centered(
                    self.path[self.index],
                    self.line_width,
                    fill=self.color,
                    outline=''
                )



        self.index += self.drawing_step
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
            self.set_random_variables()
            self.stream.start_stream()
            self.after(DRAWING_STEP_DELAY, self.draw_on_path)


app = PathDrawing('caminos')
app.mainloop()