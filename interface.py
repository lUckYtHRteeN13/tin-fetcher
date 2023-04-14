import tkinter as tk
from tkinter import ttk, messagebox
from utils import database_file, fetch_clients, create_connection
import pyautogui
from sqlite3 import IntegrityError

class TinFrame(ttk.Frame):
    
    def __init__(self, master, **options):
        super().__init__(master, **options)

        with create_connection(database_file()) as conn:
            self.clients = fetch_clients(conn, client_name=master.picked.get())

        self.row = 1

        for tin, _ in self.clients:

            self.digits = tin.split("-")
            self.col = 0

            for index, digit in enumerate(self.digits):

                self.entr = tk.Entry(self, width=4)
                self.entr.grid(row=self.row, column=self.col, sticky="ew", pady=(10,5), padx=(5,1))
                self.cpy_btn = tk.Button(self, text="Copy", command=lambda e=self.entr: self.clipboard_clear() or self.clipboard_append(e.get())).grid(row=self.row+1, column=self.col, sticky="ew", padx=(5, 1))
                
                self.entr.insert(0, digit)
                self.entr.config(state="disabled")
                self.col += 2

                if index == len(self.digits) - 1:
                    break

                tk.Label(self, text="-").grid(row=self.row, column=self.col-1, sticky="ew")

            self.auto_btn = tk.Button(self, text="Auto")
            self.auto_btn.grid(row=self.row, column=self.col-1, sticky="ew", padx=5, rowspan=2)
            self.auto_btn.bind("<Button>", lambda e=self.auto_btn: self.automate(e))
            self.row += 2

        else:
            for slave in self.grid_slaves(row=self.row-1):
                slave.grid_configure(pady=(1,10))
            
        self.n_cols = self.grid_size()[0]
        self.n_rows = self.grid_size()[1]


    def automate(self, event):
        self.widget_info = event.widget.grid_info()
        pyautogui.leftClick(293, 187, duration=0.8)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.sleep(0.5)

        for widget in self.grid_slaves(self.widget_info["row"])[::-1]:

            if isinstance(widget, tk.Entry):
                pyautogui.typewrite(widget.get(), interval=0.3)
                pyautogui.press("tab")
                pyautogui.sleep(0.5)

    def show(self):
        self.grid(row=1, column=0, sticky="we", padx=5, pady=5)

        for i in range(self.n_cols):
            self.grid_columnconfigure(i, weight=1)

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

class AddClientFrame(ttk.Frame):
    def __init__(self, master, **options):
        super().__init__(master, **options)

        self.title = tk.Label(self, text="ADD CLIENT").grid(row=0, column=0, sticky="ew", padx=5, pady=(10,5), columnspan=7)
        
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

        self.add_btn = tk.Button(self, text="Add", command=self.add_client)

        self.n_cols = self.grid_size()[0]
        self.n_rows = self.grid_size()[1]


    def add_client(self):       
        self.filled_inputs = all([ widget.get() for widget in self.winfo_children() if (isinstance(widget, tk.Entry)) and widget.winfo_ismapped() ])
        self.correct_fields = [ widget if len(widget.get()) == 3 else False for widget in self.grid_slaves(1) if (isinstance(widget, tk.Entry)) ]

        if not all(self.correct_fields):
            messagebox.showwarning("Incomplete", "Incomplete Tin")
            return

        elif not self.filled_inputs:
            messagebox.showwarning("Incomplete", "Incomplete Client Information")
            return
        
        self.tin = ""
        for index, tins in enumerate(self.correct_fields[::-1]):
            self.tin += tins.get()
            
            if index == len(self.correct_fields)-1:
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

        self.add_btn.grid(row=4, column=2, pady=5, padx=5, sticky="ew", columnspan=3)

    def filter(self, key):
        if key.isdigit() and len(key) <= 3:
            return True
                            
        elif key is "":
            return True
    
        else:
            return False
            
    def show(self):
        self.grid(row=3, column=0, sticky="sew", padx=5, pady=5)

        for i in range(self.n_cols):
            self.grid_columnconfigure(i, weight=1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.SCR_WIDTH= self.winfo_screenwidth()
        self.SCR_HEIGHT= self.winfo_screenheight()
        self.WINDOW_WIDTH = 300

        self.geometry(f"300x{self.SCR_HEIGHT}+{int(self.SCR_WIDTH-300)}+0")
        self.maxsize(self.WINDOW_WIDTH,self.SCR_HEIGHT)
        self.minsize(self.WINDOW_WIDTH,150)
        self.title("Tin Getter")

        self.wm_attributes("-topmost", 1)

        self.grid_columnconfigure(0, weight=1)

        self.picked = tk.StringVar()
        self.picked.set("Client Name")
        self.clients = self.get_clients()

        self.options = [name for name in set(self.clients.values())]
        self.options.sort()

        self.dropdown = ttk.Combobox(self, textvariable=self.picked, values=self.options, state="readonly")
        self.dropdown.grid(row=0, column=0, pady=1, sticky="nsew")
        self.dropdown.bind('<<ComboboxSelected>>', self.OptionMenu_CheckButton)
        self.show_bt = tk.Button(self, text="Show", command=self.create_frames)


        self.add_client_frame = AddClientFrame(master=self, relief="groove")
        self.add_client_frame.show()

    def create_frames(self):
        self.reset_ui()
        self.tin_frame = TinFrame(master=self, relief="groove")
        self.calc_frame = Calculator(master=self, relief="groove")
        self.tin_frame.show()
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
            if not isinstance(child, tk.Entry) and child.winfo_name() != "!addclientframe":
                child.grid_remove()

    def OptionMenu_CheckButton(self, event):
        self.reset_ui()
        self.show_bt.grid(row=1, column=0, sticky="new")

if __name__ == "__main__":
    app = App()
    app.mainloop()