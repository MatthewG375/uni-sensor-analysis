# uni-sensor-analysis

My university dissertation project, an application to monitor the data output by environmental sensor boxes, and to help ensure sensor integrity.

## Installation
The application is opened by running a .py file, and to run the application all modules used in the program must be installed on the user’s machine, along with a Python 3 install. The requirements.txt file contains the non-standard Python modules needed for this project

## Main App
Upon opening the program, the user is greeted with the main screen, without a graph but with the buttons to select graphs on the left and the empty list box on the right.

The user can click any of the available buttons to load a graph, with each button showing a different graph corresponding to the data in the default .csv file.

From here, the user can enter limit lines, to define a valid or acceptable range of data. They can enter an upper line, lower line, or both at the same time, and clicking the ‘Show Lines’ button will display these lines.

As can be seen on the right, the list of Invalid Values may have been populated. These values lie outside the limit lines, and correspond to the data points which have been highlighted on the graph. The user can click one of the data points in this list, to highlight it on the graph.

This enables the user to easily identify erroneous data points just by clicking the list. Clicking another point will remove the highlight from the initial point, returning it to the original size and colour, and highlight the new point by increasing the size of the point and changing the colour. The list of points doesn’t persist between graphs, and switching to a new graph will wipe the list of invalid values. Switching back doesn’t switch the list of invalid values back, but the graph with points remains the same, so the user can easily re-enter their limits and click ‘Show Line’ again. 

In the top left, the user can click File > Choose .csv file. This will open a file selection prompt, where the user can navigate their system to choose a file they wish to open. Clicking cancel returns to the program and keeps the current .csv file but choosing a new file will load a new dataset into the program.

Once a new dataset has been imported, the program will update the list of buttons to match the new data, and each button will correspond to a new graph.
