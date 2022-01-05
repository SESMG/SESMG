import tkinter as tk
from program_files.GUI_files.GUI import *
from tkinter import filedialog


class MethodsGUI(tk.Tk):
    """
        class holding the main methods for the Graphical User Interface
        (GUI)

        :param TITLE: defines the TK Frame label
        :type TITLE: str
        :param VERSION: defines the Version of the SESMG
        :type TITLE: str
        :param geometry: defines the geometry of the GUI
        :type geometry: str
    """
    
    @staticmethod
    def create_heading(frame, text, column, row, sticky, bold=False,
                       columnspan=None, rowspan=None):
        """
            creates a tkinter Label

            :param frame: tkinter frame where the heading will be
                included
            :type frame: tk.Frame
            :param text: text of the label to be created
            :type text: str
            :param column: defines in which column the heading will be
                placed
            :type column: int
            :param row: defines in which row the heading will be placed
            :type row: int
            :param sticky: direction in which the heading will be sticky
            :type sticky: str
            :param bold: defines rather the heading will be bold
            :type bold: bool
            :param columnspan: number of column to be spanned
            :type columnspan: int
            :param rowspan: number of rows to be spanned
            :type rowspan: int

        """
        if bold:
            font = 'Helvetica 10 bold'
        else:
            font = 'Helvetica 10'
        if type(text) == str:
            Label(frame, text=text, font=font)\
                .grid(column=column, row=row, sticky=sticky, rowspan=rowspan,
                      columnspan=columnspan)
        else:
            Label(frame, textvariable=text, font=font)\
                .grid(column=column, row=row, sticky=sticky,
                      columnspan=columnspan)
        
    @staticmethod
    def create_option_menu(frame, variable, options, column, row):
        """
            create tkinter optionmenu

            :param frame: tkinter frame where the optionmenu will be
                included
            :type frame: tk.Frame
            :param variable: StringVar holding the chosen option
            :type variable: tk.StringVar
            :param options: list holding the possible options
            :type options: list
            :param column: defines in which column the optionmenu will be
                placed
            :type column: int
            :param row: defines in which row the optionmenu will be
                placed
            :type row: int

        """
        DMenu = OptionMenu(frame, variable, *options)
        DMenu.grid(column=column, row=row)
        
    @staticmethod
    def create_checkbox(frame, variable, column, row):
        """
            creates tkinter checkbox

            :param frame: tkinter frame where the checkbox will be
                included
            :type frame: tk.Frame
            :param variable: BooleanVar holding the checkbox status
            :type variable: tk.BooleanVar
            :param column: defines in which column the checkbox will be
                placed
            :type column: int
            :param row: defines in which row the checkbox will be placed
            :type row: int
        """
        checkbox = Checkbutton(frame, variable=variable)
        checkbox.grid(column=column, row=row)

    @staticmethod
    def create_button(frame, text, command, column, row):
        """
            creates tkinter button

            :param frame: tkinter frame where the button will be
                included
            :type frame: tk.Frame
            :param text: button text
            :type text: str
            :param command: command executed onclick
            :type command:
            :param column: defines in which column the button will be
                placed
            :type column: int
            :param row: defines in which row the button will be placed
            :type row: int

        """
        button = Button(frame, text=text, command=command)
        button.grid(column=column, row=row)
        
    def get_path(self, type: str, store):
        """
            Opens a pop-up window asking the user to select a folder,
            csv-file or xlsx-file.

            :param type: defines rather the pop up for folder,
                xlsx or csv will be shown
            :type type: str
            :param store: StringVar containing the chosen path
            :type store: tk.StringVar
            :return: **path**(tk.StringVar) - chosen path

        """
        if type == "xlsx":
            path = filedialog.askopenfilename(
                    filetypes=(("Spreadsheet Files", "*.xlsx"),
                               ("all files", "*.*")))
        elif type == "folder":
            path = filedialog.askdirectory()
        elif type == "csv":
            path = filedialog.askopenfilename(
                    filetypes=(("Spreadsheet Files", "*.csv"),
                               ("all files", "*.*")))
        else:
            raise ValueError("type not implemented yet")
        if store:
            store.set(path)
            self.update_idletasks()
        else:
            return path
    
    def create_button_lines(self, frame, elements, row, gui_variables):
        """
            creates a tkinter row consisting of a label, a button and
            a optional label

            :param frame: tkinter frame where the button_row will be
                included
            :type frame: tk.Frame
            :param elements: dictionary containing the information of
                several buttons
            :type elements: dict
            :param row: defines in which row the button_row will be
                placed
            :type row: int
            :param gui_variables: dictionary containing the gui
                variables
            :type gui_variables: dict

        """
        for element in elements:
            self.create_heading(frame, element, 0, row, "w")
            self.create_button(frame=frame,
                               text=elements[element][1],
                               command=elements[element][0],
                               column=1, row=row)
            if elements[element][2] != "":
                self.create_heading(frame, gui_variables[elements[element][2]],
                                    2, row, "w", columnspan=6)
            row += 1
        return row

    def create_cb_lines(self, frame, elements, row, gui_variables):
        """
            creates a tkinter row consisting of a label and a checkbox

            :param frame: tkinter frame where the checkbox_row will be
                included
            :type frame: tk.Frame
            :param elements: dictionary containing the information of
                several checkboxes
            :type elements: dict
            :param row: defines in which row the checkbox_row will be
                placed
            :type row: int
            :param gui_variables: dictionary containing the gui
                variables
            :type gui_variables: dict
        """
        for param in elements:
            row += 1
            self.create_heading(frame, param, 0, row, "w")
            self.create_checkbox(
                frame, gui_variables[elements[param]], 1, row)
        return row
            
    def __init__(self, TITLE=None, VERSION=None, geometry=None):
        self.TITLE = TITLE
        self.VERSION = VERSION
        tk.Tk.__init__(self)
        self.title(self.TITLE + ' ' + self.VERSION)
        self.geometry(geometry)
