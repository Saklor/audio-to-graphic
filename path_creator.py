import tkinter as tk

WIDTH = 1366
HEIGHT = 768

class PathCreator(tk.Tk):
    """
    Objeto TK para crear un camino y exportarlo a un archivo.
    El archivo despues puede levantarse con el programa principal para usarlo
    como recorrido.
    """
    def __init__(self):
        super(PathCreator, self).__init__()
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="black", cursor="cross")
        self.canvas.pack(fill="both", expand=True)

        self.save_button = tk.Button(self, text="Guardar camino", command=self.save_path)
        self.save_button.place(x=int(WIDTH/2),y=100)

        self.del_button = tk.Button(self, text="Borrar", command=self.delete_last_line)
        self.del_button.place(x=int(WIDTH/2),y=50)

        self.previous_pos = [(-1, -1)]
        self.path = []
        self.index = 1
        self.lines = []
        self.canvas.bind('<B1-Motion>', self.draw_path)



    def draw_path(self, event):
        event_pos = (event.x, event.y)
        if self.previous_pos[-1][0] != -1 and event_pos != self.previous_pos[-1]:
            self.path.append(event_pos)
            self.lines.append(
                self.canvas.create_line(self.previous_pos[-1], event_pos, fill = "yellow")
            )

        self.previous_pos.append(event_pos)


    def delete_last_line(self):
        self.canvas.delete(self.lines[-1])
        del (self.lines[-1])
        if len(self.previous_pos) > 1:
            del (self.previous_pos[-1])


    def save_path(self):
        with open('output_' + str(self.index) + '.out', 'w+') as file:
            for pos in self.path:
                file.write(';'.join([str(pos[0]), str(pos[1])]) + '\n')

        # self.destroy()
        self.index += 1
        self.previous_pos = [(-1, -1)]
        self.path = []
        self.lines = []
        self.canvas.delete('all')


root = PathCreator()
root.mainloop()