import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from utils import database_file, fetch_clients, create_connection, set_database_dir, get_database_dir, set_database_file, get_database_file
import pyautogui
from sqlite3 import IntegrityError

class TinFrame(ttk.Frame):
    
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.row = 0
        self.n_clients = 0
            
    def init_entries(self) -> None:
        self.tin1 = tk.Entry(self, width=4)
        self.tin2 = tk.Entry(self, width=4)
        self.tin3 = tk.Entry(self, width=4)
        self.tin4 = tk.Entry(self, width=4)

    def automate(self, event) -> None:
        self.widget_info = event.widget.grid_info()
        pyautogui.leftClick(293, 187, duration=0.8)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.sleep(0.5)

        for widget in self.grid_slaves(self.widget_info["row"])[::-1]:

            if isinstance(widget, tk.Entry):
                pyautogui.typewrite(widget.get(), interval=0.3)
                pyautogui.press("tab")
                pyautogui.sleep(0.5)

    def map_widgets(self) -> None:
        with create_connection(database_file()) as conn:
            self.clients = fetch_clients(conn, client_name=self.master.picked.get())

        self.tins = []
        for i in self.clients:
            for tin in i[0].split("-"):
                self.tins.append(tin)
            self.init_entries()

        self.entries = [entry_widget for entry_widget in self.winfo_children() if isinstance(entry_widget, tk.Entry)]

        for col, entr in enumerate(self.entries):
            column = col%4+col%4
            entr.grid(row=self.row, column=column, sticky="ew", pady=(10, 5), padx=(5, 1))
            self.cpy_btn = tk.Button(self, text="Copy", command=lambda e=entr:self.clipboard_clear() or self.clipboard_append(e.get())).grid(row=self.row+1, column=column, sticky="ew", padx=(5, 1))

            entr.insert(tk.END, self.tins[col])
            entr.config(state="disabled")

            if column == 6:
                self.auto_btn = tk.Button(self, text="Auto")
                self.auto_btn.grid(row=self.row, column=column+1, sticky="ew", padx=5, rowspan=2)
                self.auto_btn.bind("<Button>", self.automate)
                self.row += 2
            else:
                tk.Label(self, text="-").grid(row=self.row, column=column+1, sticky="ew")

        self.grid(row=1, column=0, sticky="we", padx=5, pady=5)

        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i, weight=1)

        for slave in self.grid_slaves(row=self.row-1):
            slave.grid_configure(pady=(1, 10))
    
    def grid_remove(self) -> None:
        super().grid_remove()
        for slave in self.grid_slaves():
            slave.destroy()

class Calculator(ttk.Frame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.paddingy = (1,10)
        self.paddingx = (5,5)
        self.btn_width = 10
        self.entr_width = 12
        self.entr_stky = "ew"

        self.percentages = ["1.0%", "5.0%", "10.0%"]

        self.title = tk.Label(self, text="CALCULATOR").grid(row=0, column=0, sticky="ew", padx=5, pady=(10,5), columnspan=2)

        self.amount_tax = tk.DoubleVar(value=0.00)
        self.entr_tax = tk.Entry(self, textvariable=self.amount_tax, width=self.entr_width).grid(row=1, column=0, sticky=self.entr_stky, padx=self.paddingx, pady=self.paddingy)
        self.cal_btn = tk.Button(self, text="Calculate", command=self.calculate, width=self.btn_width).grid(row=1, column=1, sticky="ew", padx=self.paddingx, pady=self.paddingy)

        self.n_cols = self.grid_size()[0]
        self.n_rows = self.grid_size()[1]

    def calculate(self):
        self.conversion = {"1.0%":0.01, "5.0%":0.05, "10.0%":0.1}
        self.amount = tk.DoubleVar()
        self.amount.set(self.amount_tax.get() * 3)
        self.entr_amount = tk.Entry(self, textvariable=self.amount, state="readonly", width=self.entr_width).grid(row=2, column=0, sticky=self.entr_stky, padx=self.paddingx, pady=self.paddingy)

        self.percent = tk.StringVar()
        self.percent.set("-")
        self.dropdown = ttk.Combobox(self, textvariable=self.percent, values=self.percentages, state="readonly", width=self.btn_width)
        self.dropdown.grid(row=2, column=1, sticky="ew", pady=self.paddingy, padx=self.paddingx)

        def show_amnt(e):
            self.total_var = tk.DoubleVar(value=(self.amount.get()/self.conversion[self.percent.get()]))
            self.total = tk.Entry(self, textvariable=self.total_var, state="readonly", width=self.entr_width).grid(row=3, column=0, sticky=self.entr_stky, padx=self.paddingx, pady=self.paddingy)
            self.cal_btn = tk.Button(self, text="Copy", command=lambda e=self.total_var: self.clipboard_clear() or self.clipboard_append(e.get()), width=self.btn_width).grid(row=3, column=1, sticky="ew", padx=self.paddingx, pady=(1,10), columnspan=2)

        self.bs = self.dropdown.bind("<<ComboboxSelected>>", show_amnt)

    def show(self):

        for i in range(self.n_cols-1):
            self.grid_columnconfigure(i, weight=1)
            
        self.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

class BottomFrame(ttk.Frame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.add_client_frame = AddClientFrame(master=self.master.toplevelwindow)
        self.remove_client_frame = RemoveClientFrame(master=self.master.toplevelwindow)

        self.add_button = tk.Button(self, text="Add Client", command=self.add_client_frame.show)
        self.remove_button = tk.Button(self, text="Remove Client", command=self.remove_client_frame.show)

    def show(self):
        self.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        self.add_button.grid(row=1, column=0, sticky="ew")
        self.remove_button.grid(row=2, column=0, sticky="ew")

class ClientManagerFrame(ttk.Frame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.col = 0

        self.str_tin1 = tk.StringVar()
        self.tin1 = tk.Entry(self, textvariable=self.str_tin1, width=4)

        self.str_tin2 = tk.StringVar()
        self.tin2 = tk.Entry(self, textvariable=self.str_tin2, width=4)

        self.str_tin3 = tk.StringVar()
        self.tin3 = tk.Entry(self, textvariable=self.str_tin3, width=4)

        self.str_tin4 = tk.StringVar()
        self.tin4 = tk.Entry(self, textvariable=self.str_tin4, width=4)

        for child in self.winfo_children():   
            if isinstance(child, tk.Entry):
                child.grid(row=1, column=self.col, sticky="ew", pady=(10,5), padx=5)
                self.reg = self.register(self.filter)
                child.config(validate="key", validatecommand=(self.reg, '%P'))
                self.col += 2
        else:
            for index in range(3):
                tk.Label(self, text="-").grid(row=1, column=index+index+1, sticky="ew")

        self.type = tk.StringVar()
        self.type.set("-")
        self.dropdown = ttk.Combobox(self, textvariable=self.type, values=["Individual", "Organization"], state="readonly", width=1)
        self.dropdown.grid(row=2, column=2, pady=5, sticky="we", columnspan=3)
        self.dropdown.bind('<<ComboboxSelected>>', self.dropdown_event)

        self.l_nm = tk.StringVar()
        self.l_name = tk.Entry(self, textvariable=self.l_nm, width=1)

        self.f_nm = tk.StringVar()
        self.f_name = tk.Entry(self, textvariable=self.f_nm)

        self.org_nm = tk.StringVar()
        self.org_name = tk.Entry(self, textvariable=self.org_nm)

        self.button = tk.Button(self)

        self.n_cols = self.grid_size()[0]
        self.n_rows = self.grid_size()[1]

    def validate(self, *args: tuple) -> bool:
        """
        Usage:
            Class.valid( (condition, title, message) )

        Desc:
             Returns False and show a warning box with a title and message if the 
            condition is False, otherwise it returns True.

        Args:
            (tuple): 
                    condition: 
                        Statements that evaluates to either true or false.
                    title: 
                        The title for your warning window.
                    message:
                        The message that is prompted to the window.

        Returns:
            bool: True | False
        """

        for condition, title, message in args:
            if not condition:
                messagebox.showwarning(title, message)
                return False

        return True
    
    def confirmation(self, title:str, message:str):
        self.con_choice = messagebox.askyesno(title, message)

        return self.con_choice
    
    def clear_entries(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def dropdown_event(self, event):

        for slave in self.grid_slaves(3):
            slave.grid_remove()

        if self.type.get() == "Individual":
            self.l_name.grid(row=3, column=0, pady=5, padx=5, sticky="ew", columnspan=2)

            self.f_name.grid(row=3, column=2, pady=5, padx=5, sticky="ew", columnspan=5)
        
        elif self.type.get() == "Organization":
            self.org_name.grid(row=3, column=0, pady=5, padx=5, sticky="ew", columnspan=7)

        self.button.grid(row=4, column=2, pady=5, padx=5, sticky="ew", columnspan=3)

    def filter(self, key):
        if key.isdigit() and len(key) <= 3:
            return True
                            
        elif key is "":
            return True
    
        else:
            return False

    def show(self):
        self.master.deiconify()
        self.master.grab_set()
        self.master.title(self.title.cget("text"))
        self.grid(row=0, column=0, sticky="sew", padx=5, pady=5)

        for i in range(self.n_cols):
            self.grid_columnconfigure(i, weight=1)

    def grid_remove(self) -> None:
        super().grid_remove()
        self.clear_entries()
        for child in self.winfo_children():
            if child in [*self.grid_slaves(2), *self.grid_slaves(3), *self.grid_slaves(4)]:
            
                if isinstance(child, ttk.Combobox):
                    child.set("-")
                else:
                    child.grid_remove()

class RemoveClientFrame(ClientManagerFrame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.title = tk.Label(self, text="REMOVE CLIENT")
        self.title.grid(row=0, column=0, sticky="ew", padx=5, pady=(10,5), columnspan=7)

        self.button = tk.Button(master=self, text="Remove", command=self.remove_client)

    def remove_client(self):
        self.entry_widgets = [ widget.get() for widget in self.winfo_children() if (isinstance(widget, tk.Entry)) and widget.winfo_ismapped() ] # All Entry Widget in this frame
        self.tin_widgets = [ widget if len(widget.get()) == 3 else False for widget in self.grid_slaves(1) if (isinstance(widget, tk.Entry)) ] # All Entry Widget that represents the TIN of a Client
        self.valid = self.validate((all(self.tin_widgets), "Incomplete", "Incomplete Tin"),(all(self.entry_widgets), "Incomplete", "Incomplete Client Information"))

        if not self.valid:
            return

        self.tin = ""
        for index, tins in enumerate(self.tin_widgets[::-1]):
            self.tin += tins.get()
            
            if index == len(self.tin_widgets)-1:
                break
            self.tin += "-"

        if self.type.get() == "Individual":
            self.client = f"{self.l_nm.get()}, {self.f_nm.get()}"

        elif self.type.get() == "Organization":
            self.client = self.org_nm.get()

        with create_connection(database_file()) as con:
            self.cursor = con.cursor()

            try:
                if self.confirmation("Deletion", "Are you sure you want to delete?"):
                    self.cursor.execute(
                        """ DELETE FROM clients WHERE tin=? AND name=? """, (self.tin, self.client.upper()))
                    con.commit()

            except IntegrityError as e:
                messagebox.showerror("Duplicate client information detected.",
                                     "Please provide a unique information to avoid conflicts.")

        self.clear_entries()

class AddClientFrame(ClientManagerFrame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.title = tk.Label(self, text="ADD CLIENT")
        self.title.grid(row=0, column=0, sticky="ew", padx=5, pady=(10,5), columnspan=7)

        self.button = tk.Button(master=self, text="Add", command=self.add_client)

    def add_client(self):       
        self.entry_widgets = [ widget.get() for widget in self.winfo_children() if (isinstance(widget, tk.Entry)) and widget.winfo_ismapped() ] # All Entry Widget in this frame
        self.tin_widgets = [ widget if len(widget.get()) == 3 else False for widget in self.grid_slaves(1) if (isinstance(widget, tk.Entry)) ] # All Entry Widget that represents the TIN of a Client
        self.valid = self.validate((all(self.tin_widgets), "Incomplete", "Incomplete Tin"),(all(self.entry_widgets), "Incomplete", "Incomplete Client Information"))

        if not self.valid:
            return
        
        self.tin = ""
        for index, tins in enumerate(self.tin_widgets[::-1]):
            self.tin += tins.get()
            
            if index == len(self.tin_widgets)-1:
                break
            self.tin += "-"

        if self.type.get() == "Individual":
            self.client = f"{self.l_nm.get()}, {self.f_nm.get()}"
        
        elif self.type.get() == "Organization":
            self.client = self.org_nm.get()
    
        with create_connection(database_file()) as con:
            self.cursor = con.cursor()

            try:
                self.cursor.execute(""" INSERT INTO clients (tin, name) VALUES (?, ?) """, (self.tin.upper(), self.client.upper()))
                con.commit()

            except IntegrityError as e:
                messagebox.showerror("Duplicate client information detected.", "Please provide a unique information to avoid conflicts.")

        self.clear_entries()

class Menu(tk.Menu):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.options = tk.Menu(master=self.master, tearoff=0)
        self.options.add_command(label="Change Database Location", command=self.change_location)
        self.options.add_separator()
        self.options.add_command(label="Load Database", command=self.load)
        self.options.add_command(label="Move Database")
        self.options.add_separator()
        self.options.add_command(label="Import From Excel")
        self.options.add_command(label="Export To Excel")
        self.options.add_separator()
        self.options.add_checkbutton(label="Resizable")
        self.add_cascade(label="Options", menu=self.options)

    def change_location(self):
        self.directory = filedialog.askdirectory(initialdir=get_database_dir())
        if self.directory == "":
            return
            
        set_database_dir(self.directory)
        self.master.reset_ui()
        self.master.picked.set("Client Name")

    def load(self):
        self.file = filedialog.askopenfilename(filetypes=[("Text files", "*.db")])
        if self.file == "":
            return 

        set_database_file(self.file)
        self.master.reset_ui()
        self.master.picked.set("Client Name")

    def move(self):
        pass

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.SCR_WIDTH= self.winfo_screenwidth()
        self.SCR_HEIGHT= self.winfo_screenheight()
        self.WINDOW_WIDTH = 300
        self.geometry(f"290x{self.SCR_HEIGHT-50}+{int(self.SCR_WIDTH-300)}+0")
        self.maxsize(self.WINDOW_WIDTH,self.SCR_HEIGHT)
        self.minsize(self.WINDOW_WIDTH,150)
        self.title("Tin Getter")
        self.wm_attributes("-topmost", 1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.toplevelwindow = tk.Toplevel(master=self)
        self.toplevelwindow.geometry(f"325x200")
        self.toplevelwindow.protocol("WM_DELETE_WINDOW", self.reset_top_level_window)
        self.toplevelwindow.wm_attributes("-topmost", 1)
        self.toplevelwindow.resizable(False, False)
        self.toplevelwindow.withdraw()
        self.toplevelwindow.grid_columnconfigure(0, weight=1)

        self.menu = Menu(master=self)
        self.config(menu=self.menu)

        self.picked = tk.StringVar()
        self.picked.set("Client Name")
        self.dropdown = ttk.Combobox(self, textvariable=self.picked, state="readonly", postcommand=self.on_expand_dropdown)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_select_dropdown)
        self.dropdown.grid(row=0, column=0, pady=1, sticky="nsew")
        self.show_bt = tk.Button(self, text="Show", command=self.create_frames)

        self.tin_frame = TinFrame(master=self, relief="groove")
        self.calc_frame = Calculator(master=self, relief="groove")

        self.bottom_frame = BottomFrame(master=self, relief="groove")
        self.bottom_frame.show()

    def reset_top_level_window(self):
        if self.tin_frame.winfo_ismapped() and self.calc_frame.winfo_ismapped():
            self.create_frames()

        self.toplevelwindow.withdraw()
        self.toplevelwindow.grab_release()

        for widget in self.toplevelwindow.winfo_children():
            widget.grid_remove()
        
        self.update_options()
        if self.picked.get() not in self.options:
            self.reset_ui()
            self.picked.set("Client Name")

    def create_frames(self):
        self.reset_ui()
        self.tin_frame.map_widgets()
        self.calc_frame.show()

    def get_clients(self):
        try:
            with create_connection(database_file()) as conn:
                self.clients = fetch_clients(conn)
        except Exception as e:
            print(f"Error: {e}")
        
        self.client_info = {}

        for client in self.clients:
            self.tin, self.name =  client
            
            self.client_info[self.tin] = self.name

        return self.client_info

    def reset_ui(self):
        for child in self.winfo_children():
            if not isinstance(child, ttk.Combobox) and child.winfo_name() != "!bottomframe" and not isinstance(child, tk.Toplevel):
                child.grid_remove()

    def on_select_dropdown(self, _):
        if self.prev_selection != self.dropdown.get():
            self.reset_ui()
            self.show_bt.grid(row=1, column=0, sticky="new")

    def update_options(self):
        self.clients = self.get_clients()
        self.options = [ name for name in set(self.clients.values()) ]
        self.options.sort()
        self.dropdown['values'] = self.options

    def on_expand_dropdown(self):
        self.update_options()
        self.prev_selection = self.picked.get()

if __name__ == "__main__":
    app = App()
    app.mainloop()