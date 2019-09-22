from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from cubemap2fisheye import *


class CubeMapConverter:

    def __init__(self, master):
        self.master = master
        self.cube_map_image = None
        self.output_image = None
        master.title("Cube map converter")
        master.geometry("300x700")
        master.resizable(FALSE, FALSE)
        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        ttk.Label(self.mainframe, text="1. Select the desired projection", font='bold', justify="left").grid(column=0, row=1,
                                                                                                        columnspan=2,
                                                                                                        pady=10,
                                                                                                        padx=20,
                                                                                                        sticky="we")
        self.current_projection = StringVar()
        self.combobox_projection = ttk.Combobox(self.mainframe, textvariable=self.current_projection, state="readonly")
        self.combobox_projection['values'] = ("Fisheye Equisolid", "Equirectangular")
        self.combobox_projection.grid(column=0, columnspan=2, row=2, pady=10, padx=20)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=3, sticky="we", pady=10)

        ttk.Label(self.mainframe, text="2. Load cube map image", font='bold', justify="left").grid(column=0, columnspan=2,
                                                                                              row=4, pady=10, padx=20,
                                                                                              sticky="we")
        self.button_select_cube_map = ttk.Button(self.mainframe, text="Select cube map...", command=self.choose_cube_map)
        self.button_select_cube_map.grid(column=0, columnspan=2, row=5, ipady=10, ipadx=15)
        self.button_select_cube_map['state'] = 'disabled'
        self.combobox_projection.bind("<<ComboboxSelected>>", self.combobox_updated)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=6, sticky="we", pady=10)

        ttk.Label(self.mainframe, text="3. Provide required information", font='bold', justify="left").grid(column=0,
                                                                                                       columnspan=2,
                                                                                                       row=7, pady=10,
                                                                                                       padx=20,
                                                                                                       sticky="we")
        ttk.Label(self.mainframe, text="FOV (deg)", justify="left").grid(column=0, row=8, pady=10, padx=20, sticky="w")
        self.field_of_view = StringVar()
        self.entry_fov = ttk.Entry(self.mainframe, textvariable=self.field_of_view, width=10)
        self.entry_fov.grid(column=1, row=8, pady=10, sticky="w")
        ttk.Label(self.mainframe, text="Size of output square image", wraplength=100, justify="left").grid(column=0, row=9,
                                                                                                      pady=10, padx=20,
                                                                                                      sticky="w")
        self.size_output_image = StringVar()
        self.entry_size_output_image = ttk.Entry(self.mainframe, textvariable=self.size_output_image, width=10)
        self.entry_size_output_image.grid(column=1, row=9, pady=10, sticky="w")

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=10, sticky="we", pady=10)

        ttk.Label(self.mainframe, text="4. Generate the image!", font='bold', justify="left").grid(column=0, columnspan=2,
                                                                                              row=11, pady=10, padx=20,
                                                                                              sticky="we")
        self.button_generate_output_image = ttk.Button(self.mainframe, text="Generate image!", command=self.create_output_image)
        self.button_generate_output_image.grid(column=0, columnspan=2, row=12, ipady=10, ipadx=15)
        self.button_generate_output_image['state'] = 'disabled'
        self.style = ttk.Style(root)
        self.style.layout('text.Horizontal.TProgressbar',
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar',
                                      {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                      ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.progress_var = DoubleVar()
        self.progressbar = ttk.Progressbar(self.mainframe, style='text.Horizontal.TProgressbar', variable=self.progress_var, orient=HORIZONTAL, length=200, mode='determinate', maximum=100)
        self.progressbar.grid(column=0, columnspan=2, row=14, pady=15, ipadx=10)

        ttk.Separator(self.mainframe, orient=HORIZONTAL).grid(column=0, columnspan=2, row=15, sticky="we", pady=10)

        self.button_save_image = ttk.Button(self.mainframe, text="Save image", command=self.save_image)
        self.button_save_image.grid(column=0, columnspan=2, row=16, ipady=10, ipadx=15)
        self.button_save_image['state'] = 'disabled'
        self.button_exit = ttk.Button(self.mainframe, text="Exit", command=self.exit_app)
        self.button_exit.grid(column=0, columnspan=2, row=17, ipady=10, ipadx=15, pady=10)
        web_page = "Visit www.miguelangelbueno.me"
        ttk.Label(self.mainframe, text=web_page, justify="center").grid(column=0, columnspan=2, row=18, pady=10, padx=20,
                                                                   sticky="s")

    def combobox_updated(self, *args):
        if not self.current_projection.get():
            self.button_select_cube_map['state'] = 'disabled'
        else:
            self.button_select_cube_map['state'] = 'enabled'

    def choose_cube_map(self):
        types = [('PNG image', '*.png'), ('BMP image', '*.bmp'), ('JPEG image', '*.jpeg'), ('All files', '*')]
        filename = filedialog.askopenfilename(filetypes=types)
        if self.cube_map_image is not None or not filename == "":
            self.cube_map_image = Image.open(filename)
            self.button_generate_output_image['state'] = 'enabled'
        filename == ""

    def create_output_image(self):
        self.button_save_image['state'] = 'disable'
        if self.current_projection.get() == "Fisheye Equisolid":
            self.cube_map_image = np.array(self.cube_map_image)
            try:
                self.output_image = self.cubemap_to_fisheye(self.cube_map_image, float(self.field_of_view.get()), int(self.size_output_image.get()))
                self.output_image = Image.fromarray(self.output_image.astype('uint8'))
                self.output_image.show()
                self.button_save_image['state'] = 'enable'
            except ValueError:
                messagebox.showinfo(message='Please, provide required information', icon='error')
        elif self.current_projection.get() == "Equirectangular":
            pass

    def cubemap_to_fisheye(self, cube_map, fov, output_image_height):

        output_image = np.zeros((output_image_height, output_image_height, 3))
        field_of_view = fov * np.pi / 180
        face_size = int(cube_map.shape[1]/4)
        print(face_size)
        r, phi = get_spherical_coordinates(output_image_height, output_image_height)
        x, y, z = spherical_to_cartesian(r, phi, field_of_view)

        for row in range(0, output_image_height):
            for column in range(0, output_image_height):
                if np.isnan(r[row, column]):
                    output_image[row, column, 0] = 0
                    output_image[row, column, 1] = 0
                    output_image[row, column, 2] = 0
                else:
                    face = get_face(x[row, column], y[row, column], z[row, column])
                    u, v = raw_face_coordinates(face, x[row, column], y[row, column], z[row, column])
                    xn, yn = normalized_coordinates(face, u, v, face_size)

                    output_image[row, column, 0] = cube_map[yn, xn, 0]
                    output_image[row, column, 1] = cube_map[yn, xn, 1]
                    output_image[row, column, 2] = cube_map[yn, xn, 2]
            self.progress_var.set((row/output_image_height)*100)
            self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(self.progress_var.get()))
            self.progressbar.update()
        self.style.configure('text.Horizontal.TProgressbar', text='{:.2f} %'.format(100))
        return output_image

    def save_image(self):
        filename = filedialog.asksaveasfilename()
        self.output_image.save(str(filename))

    def exit_app(self):
        self.master.destroy()


root = Tk()
app = CubeMapConverter(root)
root.mainloop()
