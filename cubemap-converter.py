from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np
import math
import cubemap2fisheye as fisheye
import cube2equi as equi


class CubeMapConverter:

    def __init__(self, master):
        self.master = master
        self.cube_map_image = None
        self.output_image = None

        master.title("Cube map converter")
        master.geometry("320x700")
        master.resizable(FALSE, FALSE)

        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        ttk.Label(self.mainframe, text="1. Select the desired projection", font='bold', justify="left").grid(column=0,
                                                                                                        row=1,
                                                                                                        columnspan=2,
                                                                                                        pady=10,
                                                                                                        padx=20,
                                                                                                        sticky=(W, E))
        self.current_projection = StringVar()
        self.combobox_projection = ttk.Combobox(self.mainframe, state='readonly')
        self.combobox_projection['textvariable'] = self.current_projection
        self.combobox_projection['values'] = ("Fisheye Equisolid", "Equirectangular")
        self.combobox_projection.grid(column=0, columnspan=2, row=2, pady=10, padx=20)
        self.combobox_projection.bind("<<ComboboxSelected>>", self.combobox_updated)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=3, sticky=(W, E), pady=10)

        ttk.Label(self.mainframe, text="2. Load cube map image", font='bold', justify="left").grid(column=0,
                                                                                                   columnspan=2,
                                                                                                   row=4,
                                                                                                   pady=10,
                                                                                                   padx=20,
                                                                                                   sticky=(W, E))
        self.button_select_cube_map = ttk.Button(self.mainframe, text="Select cube map...")
        self.button_select_cube_map['command'] = self.choose_cube_map
        self.button_select_cube_map['state'] = 'disabled'
        self.button_select_cube_map.grid(column=0, columnspan=2, row=5, ipady=10, ipadx=15)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=6, sticky=(W, E), pady=10)

        ttk.Label(self.mainframe, text="3. Provide required information", font='bold', justify="left").grid(column=0,
                                                                                                       columnspan=2,
                                                                                                       row=7,
                                                                                                       pady=10,
                                                                                                       padx=20,
                                                                                                       sticky=(W, E))
        ttk.Label(self.mainframe, text="FOV (deg)", justify="left").grid(column=0, row=8, pady=10, padx=20, sticky=W)

        self.field_of_view = StringVar()
        self.entry_fov = ttk.Entry(self.mainframe, textvariable=self.field_of_view, width=10)
        self.entry_fov.grid(column=1, row=8, pady=10, sticky=W)

        ttk.Label(self.mainframe, text="Size of output square image", wraplength=100, justify="left").grid(column=0,
                                                                                                           row=9,
                                                                                                           pady=10,
                                                                                                           padx=20,
                                                                                                           sticky=W)
        self.size_output_image = StringVar()
        self.entry_size_output_image = ttk.Entry(self.mainframe, textvariable=self.size_output_image, width=10)
        self.entry_size_output_image.grid(column=1, row=9, pady=10, sticky=W)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=10, sticky=(W, E), pady=10)

        ttk.Label(self.mainframe, text="4. Generate the image!", font='bold', justify="left").grid(column=0,
                                                                                                   columnspan=2,
                                                                                                   row=11,
                                                                                                   pady=10,
                                                                                                   padx=20,
                                                                                                   sticky=(W, E))
        self.button_generate_output_image = ttk.Button(self.mainframe, text="Generate image!")
        self.button_generate_output_image['command'] = self.create_output_image
        self.button_generate_output_image['state'] = 'disabled'
        self.button_generate_output_image.grid(column=0, columnspan=2, row=12, ipady=10, ipadx=15)

        self.style = ttk.Style(root)
        self.style.layout('text.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                      ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.progress_var = DoubleVar()
        self.progressbar = ttk.Progressbar(self.mainframe, mode='determinate')
        self.progressbar['style'] = 'text.Horizontal.TProgressbar'
        self.progressbar['variable'] = self.progress_var
        self.progressbar['length'] = 200
        self.progressbar['maximum'] = 100
        self.progressbar.grid(column=0, columnspan=2, row=14, pady=15, ipadx=10)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=15, sticky=(W, E), pady=10)

        self.button_save_image = ttk.Button(self.mainframe, text="Save image")
        self.button_save_image['command'] = self.save_image
        self.button_save_image['state'] = 'disabled'
        self.button_save_image.grid(column=0, columnspan=2, row=16, ipady=10, ipadx=15)

        self.button_exit = ttk.Button(self.mainframe, text="Exit")
        self.button_exit['command'] = self.exit_app
        self.button_exit.grid(column=0, columnspan=2, row=17, ipady=10, ipadx=15, pady=10)

        web_page = "Visit www.miguelangelbueno.me"
        ttk.Label(self.mainframe, text=web_page, justify="center").grid(column=0, columnspan=2, row=18,
                                                                        pady=10, padx=20, sticky=S)

    def combobox_updated(self, *args):
        if not self.current_projection.get():
            self.button_select_cube_map['state'] = 'disabled'
        else:
            self.button_select_cube_map['state'] = 'enabled'
            if self.current_projection.get() == "Equirectangular":
                self.entry_fov['state'] = 'disabled'
                self.entry_size_output_image['state'] = 'disabled'
            else:
                self.entry_fov['state'] = 'enable'
                self.entry_size_output_image['state'] = 'enable'

    def choose_cube_map(self):
        types = [('PNG image', '*.png'), ('BMP image', '*.bmp'), ('JPEG image', '*.jpeg'), ('All files', '*')]
        filename = filedialog.askopenfilename(filetypes=types)
        if not filename == "":
            self.cube_map_image = Image.open(filename)
            self.button_generate_output_image['state'] = 'enabled'
        filename == ""

    def create_output_image(self):
        self.button_save_image['state'] = 'disable'
        self.combobox_projection['state'] = 'disable'
        self.button_select_cube_map['state'] = 'disable'
        self.button_generate_output_image['state'] = 'disable'
        self.cube_map_image = np.array(self.cube_map_image)
        if self.current_projection.get() == "Fisheye Equisolid":
            try:
                self.output_image = self.cubemap_to_fisheye(self.cube_map_image, float(self.field_of_view.get()), int(self.size_output_image.get()))
                self.output_image = Image.fromarray(self.output_image.astype('uint8'))
                self.output_image.show()
            except ValueError:
                messagebox.showinfo(message='Please, provide required information', icon='error')
        elif self.current_projection.get() == "Equirectangular":
            self.output_image = self.cubemap_to_equirectangular(Image.fromarray(self.cube_map_image.astype('uint8')))
            self.output_image.show()
        self.button_select_cube_map['state'] = 'enable'
        self.button_save_image['state'] = 'enable'
        self.combobox_projection['state'] = 'enable'
        self.button_generate_output_image['state'] = 'enable'

    def cubemap_to_fisheye(self, cube_map, fov, output_image_height):

        output_image = np.zeros((output_image_height, output_image_height, 3))
        field_of_view = fov * np.pi / 180
        face_size = int(cube_map.shape[1]/4)
        r, phi = fisheye.get_spherical_coordinates(output_image_height, output_image_height)
        x, y, z = fisheye.spherical_to_cartesian(r, phi, field_of_view)

        for row in range(0, output_image_height):
            for column in range(0, output_image_height):
                if np.isnan(r[row, column]):
                    output_image[row, column, 0] = 0
                    output_image[row, column, 1] = 0
                    output_image[row, column, 2] = 0
                else:
                    face = fisheye.get_face(x[row, column], y[row, column], z[row, column])
                    u, v = fisheye.raw_face_coordinates(face, x[row, column], y[row, column], z[row, column])
                    xn, yn = fisheye.normalized_coordinates(face, u, v, face_size)

                    output_image[row, column, 0] = cube_map[yn, xn, 0]
                    output_image[row, column, 1] = cube_map[yn, xn, 1]
                    output_image[row, column, 2] = cube_map[yn, xn, 2]
            self.progress_var.set((row/output_image_height)*100)
            self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(self.progress_var.get()))
            self.progressbar.update()
        self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(100))
        return output_image

    def cubemap_to_equirectangular(self, cube_map):

        output_height = math.floor(cube_map.size[0] / 3)
        output_width = 2 * output_height
        n = math.floor(cube_map.size[1] / 3)

        output_img = Image.new('RGB', (output_width, output_height))

        for ycoord in range(0, output_height):
            for xcoord in range(0, output_width):
                corrx, corry, face = equi.cubemap_to_equirectangular(xcoord,
                                                                     ycoord,
                                                                     output_width,
                                                                     output_height,
                                                                     n)
                output_img.putpixel((xcoord, ycoord), cube_map.getpixel((corrx, corry)))
            self.progress_var.set((ycoord / output_height) * 100)
            self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(self.progress_var.get()))
            self.progressbar.update()
        self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(100))
        return output_img

    def save_image(self):
        filename = filedialog.asksaveasfilename()
        if not filename == "":
            self.output_image.save(str(filename))

    def exit_app(self):
        self.master.destroy()


root = Tk()
app = CubeMapConverter(root)
root.mainloop()
