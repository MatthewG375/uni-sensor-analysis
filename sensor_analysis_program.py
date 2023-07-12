import numpy as np
import os
import pandas as pd
import tkinter as tk

from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog as fd

# b9031670 - Matthew Gibson


def line_colourmap(current_ax, lower_line_value, x, y, colour_1, colour_2, colour_3=None, upper_line_value=None):
    # Credit, edited from: 
    # https://stackoverflow.com/questions/30121773/is-it-possible-to-change-line-color-in-a-plot-if-exceeds-a-specific-range

    # Create a colormap for red, green and blue and a norm to color
    # f' < -0.5 red, f' > 0.5 blue, and the rest green
    if colour_3 is not None and upper_line_value is not None:
        cmap = ListedColormap([colour_1, colour_2, colour_3])
        norm = BoundaryNorm([np.min(y), lower_line_value, upper_line_value, np.max(y)], cmap.N)
    else:
        cmap = ListedColormap([colour_1, colour_2])
        norm = BoundaryNorm([np.min(y), lower_line_value, np.max(y)], cmap.N)

    # Create a set of line segments so that we can color them individually
    # This creates the points as an N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line collection
    # needs to be number of lines x points per line x 2 (x and y)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create the line collection object, setting the colour-mapping parameters.
    # Have to set the actual values used for colour-mapping separately.
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(y)

    # print(current_ax.axes.lines[-1])
    current_ax.add_collection(lc)
    current_ax.axes.lines[0].set_gid('main_line')


def remove_old_lines(current_ax):
    for z in current_ax.axes.lines:
        if z.get_gid() == 'low_lim':
            z.remove()
        if z.get_gid() == 'up_lim':
            z.remove()
        if z.get_gid() == 'marker' or z.get_gid() == 'big_marker':
            z.remove()


def do_nothing():
    pass


def line_value_get(line_value):
    try:
        lv = int(line_value.get())
    except tk.TclError:
        lv = None
    except ValueError:
        lv = None
    return lv


class GraphManager:
    def __init__(self, root):
        self.root = root
        self.figures = []  # List to store the different graphs
        self.current_figure_index = None
        self.graph_titles = []  # List to store the titles of the graphs
        self.data_file = 'FILE001.csv'

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.LEFT, padx=10)

        self.upper_line_value = tk.StringVar()  # Variable to store the upper line value entered by the user
        self.lower_line_value = tk.StringVar()  # Variable to store the lower line value entered by the user

        self.canvas = None
        self.create_graphs()
        self.show_current_graph()

        self.entry_frame = tk.Frame(self.root)
        self.entry_frame.pack(anchor='w', side=tk.BOTTOM, padx=10, pady=10)

        # Upper Limit Line Buttons
        self.entry_label = tk.Label(self.entry_frame, text="Upper Line Value:")
        self.entry_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(self.entry_frame, textvariable=self.upper_line_value)
        self.entry.pack(side=tk.LEFT)

        # Lower Limit Line Buttons
        self.entry_label = tk.Label(self.entry_frame, text="Lower Line Value:")
        self.entry_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(self.entry_frame, textvariable=self.lower_line_value)
        self.entry.pack(side=tk.LEFT)

        self.line_button = tk.Button(self.entry_frame, text="Show Lines", command=self.show_lines_button)
        self.line_button.pack(pady=10, side=tk.LEFT)

        # Menu Bar
        self.menubar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Choose .csv file", command=self.select_file)
        self.menubar.add_cascade(label="File", menu=self.file_menu, underline=0)
        self.root.config(menu=self.menubar)

        # Listbox values, including scrollbar
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(side=tk.RIGHT, padx=10)

        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.listbox_label = tk.Label(self.list_frame, text="Invalid Values")
        self.listbox_label.pack(padx=10)

        self.listbox = tk.Listbox(self.list_frame, selectmode=tk.SINGLE, height=40, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        self.scrollbar.config(command=self.listbox.yview)

    def button_create(self):
        for item in self.button_frame.winfo_children():
            item.destroy()

        for i, title in enumerate(self.graph_titles):
            button = tk.Button(self.button_frame, text=title,
                               command=lambda index=i: self.switch_graph(index))
            button.pack(pady=10)

    def select_file(self):
        filetypes = (('CSV files', '*.csv'), ('All files', '*.*'))
        prov_data_file = fd.askopenfilename(title='Open a file', initialdir=os.getcwd(), filetypes=filetypes)

        # Test to see if the file was selected, if cancelled keep original self.data_file
        if not prov_data_file:
            pass
        else:
            self.data_file = prov_data_file

        self.create_graphs()

    def create_graphs(self):
        self.figures = []  # Reset figures
        self.graph_titles = []  # Reset graph titles
        data = pd.read_csv(self.data_file)

        # Create the figures and add them to the list
        for column in data.columns:
            fig = Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)

            x = list(range(1, len(data) + 1))
            y = data[column].tolist()
            ax.set_gid("base")
            ax.plot(x, y)

            fig.suptitle(column)
            # get the string from the title, from one space before the open bracket
            ax.set_ylabel(column[(int(column.find('('))-1):])
            ax.set_xlabel('Sensor Reading Count')

            self.figures.append(fig)
            self.graph_titles.append(column)

        self.button_create()
        self.current_figure_index = None
        self.show_current_graph()

    def show_current_graph(self):
        if self.current_figure_index is not None:
            # Remove the previous canvas if it exists
            if self.canvas is not None:
                self.canvas.get_tk_widget().pack_forget()

            # Get the current figure and create a new canvas for it
            current_figure = self.figures[self.current_figure_index]
            self.canvas = FigureCanvasTkAgg(current_figure, master=self.root)
            self.canvas.draw()

            # Place the canvas in the center of the window
            self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.clear_listbox()

    def switch_graph(self, index):
        self.current_figure_index = index
        self.show_current_graph()

    def show_upper_line(self):
        upper_line_value = int(self.upper_line_value.get())

        if self.current_figure_index is not None and upper_line_value is not None:
            current_figure = self.figures[self.current_figure_index]
            current_ax = current_figure.get_axes()[0]

            line = current_ax.lines[0]
            x = line.get_xdata()
            y = line.get_ydata()

            if upper_line_value <= np.max(y):
                line_colourmap(current_ax, upper_line_value, x, y, 'blue', 'red')

            elif upper_line_value > np.max(y):
                for g in current_ax.axes.lines:
                    # print(g.get_gid())
                    if g.get_gid() == 'main_line':
                        g.remove()
                current_ax.plot(x, y, gid='main_line', color='blue')

            remove_old_lines(current_ax)

            current_ax.axhline(upper_line_value, color='red', gid='up_lim')
            self.canvas.draw()

    def show_lower_line(self):
        lower_line_value = int(self.lower_line_value.get())

        if self.current_figure_index is not None and lower_line_value is not None:
            current_figure = self.figures[self.current_figure_index]
            current_ax = current_figure.get_axes()[0]

            line = current_ax.lines[0]
            x = line.get_xdata()
            y = line.get_ydata()

            if lower_line_value >= np.min(y):
                line_colourmap(current_ax, lower_line_value, x, y, 'green', 'blue')

            elif lower_line_value < np.min(y):
                for g in current_ax.axes.lines:
                    # print(g.get_gid())
                    if g.get_gid() == 'main_line':
                        g.remove()
                current_ax.plot(x, y, gid='main_line', color='blue')

            remove_old_lines(current_ax)

            current_ax.axhline(lower_line_value, color='green', gid='low_lim')

            self.canvas.draw()

    def show_line_colours(self):
        upper_line_value = line_value_get(self.upper_line_value)
        lower_line_value = line_value_get(self.lower_line_value)

        if self.current_figure_index is not None and lower_line_value is not None and upper_line_value is None:
            self.show_lower_line()

        elif self.current_figure_index is not None and upper_line_value is not None and lower_line_value is None:
            self.show_upper_line()

        elif self.current_figure_index is not None and lower_line_value is not None and upper_line_value is not None:
            current_figure = self.figures[self.current_figure_index]
            current_ax = current_figure.get_axes()[0]

            line = current_ax.lines[0]
            x = line.get_xdata()
            y = line.get_ydata()

            if lower_line_value >= np.min(y):
                line_colourmap(current_ax, lower_line_value, x, y, 'green', 'blue',
                               colour_3='red', upper_line_value=upper_line_value)

            elif lower_line_value < np.min(y):
                for g in current_ax.axes.lines:
                    # print(g.get_gid())
                    if g.get_gid() == 'main_line':
                        g.remove()
                current_ax.plot(x, y, gid='main_line', color='blue')

            elif lower_line_value > np.min(y):
                for g in current_ax.axes.lines:
                    # print(g.get_gid())
                    if g.get_gid() == 'main_line':
                        g.remove()
                current_ax.plot(x, y, gid='main_line', color='green')

            # Add new line
            remove_old_lines(current_ax)

            current_ax.axhline(lower_line_value, color='green', gid='low_lim')
            current_ax.axhline(upper_line_value, color='red', gid='up_lim')

            self.canvas.draw()

    def show_lines_button(self):
        self.show_line_colours()
        self.clear_listbox()
        self.add_to_listbox()

    def add_to_listbox(self):
        # check that a graph is selected
        if self.current_figure_index is not None:
            # get local copies of all important class variables
            upper_line_value = line_value_get(self.upper_line_value)
            lower_line_value = line_value_get(self.lower_line_value)

            current_figure = self.figures[self.current_figure_index]
            current_ax = current_figure.get_axes()[0]

            # get x and y data of main graph
            line = current_ax.lines[0]
            x = line.get_xdata()
            y = line.get_ydata()

            values_to_listbox = []

            # add values outside of limits to values_to_listbox
            if upper_line_value is not None:
                for val_x, val_y in zip(x, y):
                    if val_y > upper_line_value:
                        values_to_listbox.append([val_x, val_y, 0])

            if lower_line_value is not None:
                for val_x, val_y in zip(x, y):
                    if val_y < lower_line_value:
                        values_to_listbox.append([val_x, val_y, 1])

            # sort the list in order of the points, and add them to the listbox
            values_to_listbox = sorted(values_to_listbox, key=lambda k: k[0])
            for val in values_to_listbox:
                p = str(str(val[0]) + ": " + str(val[1]))
                self.listbox.insert('end', p)

                if int(val[2]) == 0:
                    face_col, edge_col = 'green', 'red'
                else:
                    face_col, edge_col = 'red', 'green'

                current_ax.plot(val[0], val[1], gid='marker', marker='o', markersize=5,
                                markerfacecolor=face_col, markeredgecolor=edge_col)
                current_ax.axes.lines[-1].set_gid('marker')

            self.canvas.draw()

    def on_listbox_select(self, event):
        # get local copies of all important class variables
        current_figure = self.figures[self.current_figure_index]
        current_ax = current_figure.get_axes()[0]
        ulv = line_value_get(self.upper_line_value)

        # if an item in the listbox has been selected
        selection = event.widget.curselection()
        if selection:
            sel_index = event.widget.get(selection[0]).split(':')

            # for every line/marker on the graph
            for line in current_ax.axes.lines:

                # if the selected line is a marker
                if line.get_gid() == 'marker':
                    cur_line = line.get_data()

                    if int(cur_line[0]) == int(sel_index[0]):
                        line.remove()
                        current_ax.plot(int(cur_line[0]), cur_line[1], gid='marker', marker='o', markersize=10,
                                        markerfacecolor="yellow", markeredgecolor='orange')
                        current_ax.axes.lines[-1].set_gid('big_marker')
                        self.canvas.draw()

                # if the selected line is a big marker
                elif line.get_gid() == 'big_marker':
                    cur_line = line.get_data()
                    line.remove()

                    # marker colour changes depending on if above or below limit line
                    if cur_line[1] > int(ulv):
                        face, outline = 'red', 'green'
                    else:
                        face, outline = 'green', 'red'

                    current_ax.plot(int(cur_line[0]), cur_line[1], gid='marker', marker='o', markersize=5,
                                    markerfacecolor=face, markeredgecolor=outline)
                    current_ax.axes.lines[-1].set_gid('marker')
                    self.canvas.draw()

    def clear_listbox(self):
        self.listbox.delete(0, 'end')


# Create the Tkinter window
root_tk = tk.Tk()
root_tk.geometry("1600x900")
root_tk.title('Sensor Box Management')
root_tk.iconbitmap("myIcon.ico")

# Create the GraphManager instance
graph_manager = GraphManager(root_tk)

# Start the Tkinter event loop
root_tk.mainloop()
