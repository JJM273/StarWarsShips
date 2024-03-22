"""
Gui for selecting ships to compare and displaying radar charts of stats
"""

# Standard Imports
from collections import deque
import tkinter as tk
from typing import Any, Callable, Tuple
# Third Party Imports
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from customtkinter.windows.widgets.core_widget_classes import DropdownMenu
import pandas

# Local Imports

class Plot(ctk.CTkFrame):
    def __init__(self, 
                 master, 
                 width: int = 200, 
                 height: int = 200, 
                 corner_radius: int | str | None = None, 
                 border_width: int | str | None = None, 
                 bg_color: str | Tuple[str, str] = "transparent", 
                 fg_color: str | Tuple[str, str] | None = None, 
                 border_color: str | Tuple[str, str] | None = None, 
                 background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, 
                 overwrite_preferred_drawing_method: str | None = None, 
                 **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)

        #self.canvas = FigureCanvasTkAgg(self.figure, self) 

def test_figure():
    fig = plt.Figure(figsize = (5, 5), 
                 dpi = 100) 
    # list of squares 
    y = [i**2 for i in range(101)] 
    # adding the subplot 
    plot1 = fig.add_subplot(111) 
    # plotting the graph 
    plot1.plot(y) 
    return fig

def test_data() -> pandas.DataFrame:
    data = {
    'A': ['A1', 'A2', 'A3', 'A4', 'A5'],
    'B': ['B1', 'B2', 'B3', 'B4', 'B4'],
    'C': ['C1', 'C2', 'C3', 'C3', 'C3'],
    'D': ['D1', 'D2', 'D2', 'D2', 'D2'],
    'E': ['E1', 'E1', 'E1', 'E1', 'E1']}
    return pandas.DataFrame(data)

class BaseButton(ctk.CTkButton):
    def __init__(self, master,*args,**kwargs):
        super().__init__(master,*args,**kwargs)
        self.configure(
        corner_radius = 20,
        # border_width = None,
        # font: Tuple | ctk.CTkFont | None = None,
        border_spacing = 2
        )

class StdBtn(BaseButton):
    def __init__(self, master,text: str="StdBtn",command: Callable = None):
        super().__init__(master, text=text,command=command)
        self.configure(
            width=100,
            height=28,
            bg_color = "transparent",
            fg_color = 'red',
            hover_color= 'dark red'
        )

class FilterMenu(ctk.CTkOptionMenu):
    def __init__(self,master,name,col,*args,values:list[str]=[],**kwargs):
        self.col_name = name
        super().__init__(master,*args,**kwargs)
        self.set_options(values)
        self.grid(row=0,column=col, padx=5)

    def filter_action(self,name,value):
        print(f"{name},{value}")
        ...

    def _dropdown_callback(self, value: str):
        """overwriting to pass name and value to command"""
        self._current_value = value
        self._text_label.configure(text=self._current_value)

        if self._variable is not None:
            self._variable_callback_blocked = True
            self._variable.set(self._current_value)
            self._variable_callback_blocked = False

        if self._command is not None:
            self._command(self.col_name,self._current_value)

    def set_options(self, values: list[str],include_all:bool=True):
        """set the options displayed in dropdown, include an "ALL" by default"""
        if include_all:
            vals = deque(values)
            vals.appendleft("ALL")
            values = list(vals)
        self.configure(values=values)
        self.reset_selection()

    def reset_selection(self):
        if self._current_value not in set(self._values):
            self.set(self._values[0])

class Filters(ctk.CTkFrame):
    """
    using Pandas provide UI filter element and filtering functionality
    this will create a set of connected dropdown filters that filter the provided data
    and repopulate the option values
    """
    def __init__(self, master,*args,width,height,orientation: str='row',data: pandas.DataFrame=None,filter_list:list[str], **kwargs):
        """
        Positional Arguments:
        :param master: -- TKinter widgit for the filters to belong to
        :param *args: -- any positional args for CTkFrame
        Keyword Arguments:
        :param width: -- Total width (px) for the filter element
        :param height: -- Total height (px) for the filter element
        :param orientation: -- {'row' | 'col'} how should the individual filter dropdowns be arranged
        :param data: -- DataFrame with the data to be interactivly filtered
        :param filter_list: -- list of column names from data to be filtered on
        """
        self._data = data
        self.working_data = data
        self._orientation = orientation
        super().__init__(master,width,height,*args,**kwargs)
        self._size = len(filter_list)
        #get individual button size and check they will all fit
        button_width = (width/self._size)-4 if orientation == 'row' else width
        button_height = (height/self._size)-4 if orientation == 'col' else height
        if button_width < 100 or button_height < 25:
            raise ValueError(f"""Provided frame size (w/h:{width}/{height}) cannot accomodate {self._size} filters.
                              This would result in buttons of {button_width}/{button_height}""")

        #check that filter_list contains valid columns
        if data is not None: #DEV remove when data becomes mandatory param
            diff = set(filter_list).difference(set(data.columns))
            if len(diff) > 0:
                raise ValueError(f"column(s) {diff} not found in data")

        #dynamically create filters from the list provided
        self.filters = [FilterMenu(self,filter,col=i,command=self.update_filters) for i, filter in enumerate(filter_list)]
        self.set_filter_options()
        
    def update_filters(self,col_name,value) -> pandas.DataFrame:
        """update the filter dropdowns based on selected values and return filtered data"""
        q_list: list[str] = []
        update_list: list[FilterMenu] = list()
        for filter in self.filters:
            if filter.get() == "ALL":
                update_list.append(filter)
            else:
                q_list.append(f'{filter.col_name} == "{filter.get()}"')
                filter.set_options([filter.get()])
        if len(q_list) > 0:
            query = " and ".join(q_list)
            self.working_data = self._data.query(query)
        else:
            self.working_data = self._data
        self.set_filter_options(update_list)
        return self.working_data
    
    def set_filter_options(self, to_set:list[FilterMenu] = None):
        """sets filter options based on working data"""
        if to_set is None:
            to_set = self.filters
        if len(to_set) < 1:
            return
        for filter in to_set:
            filter.set_options(self.working_data[filter.col_name].unique())



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.button = StdBtn(self, text="my button", command=self.button_callbck)
        self.button.pack(padx=20, pady=20)
        # adding matplotlib canvas
        self.figure = test_figure()
        self.data = test_data()
        self.canvas = FigureCanvasTkAgg(self.figure, self) # connect figure and ctk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self) # connect toolbar to canvas and ctk

        optionmenu_var = ctk.StringVar(value="option 2")
        self.optionmenu = ctk.CTkOptionMenu(self,values=["option 1", "option 2"],
                                         command=self.optionmenu_callback,
                                         variable=optionmenu_var)
        self.optionmenu.pack()
        self.filters = Filters(self,width=500,height=28,data=self.data,filter_list=["A","C","D"])
        self.filters.pack()

    def optionmenu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)
        self.optionmenu.configure(values=["option 1", "option 2","option 3"])
        
    def button_callbck(self):
        self.canvas.get_tk_widget().pack() 
        # self.figure.canvas.draw()
        print("button clicked")

if __name__ == '__main__':
    ctk.set_appearance_mode('dark')
    app = App()
    app.mainloop()
    input()