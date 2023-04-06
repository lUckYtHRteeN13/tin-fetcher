import tkinter as tk
from working import database_file, fetch_clients, create_connection


root = tk.Tk()

SCR_WIDTH= root.winfo_screenwidth()
SCR_HEIGHT= root.winfo_screenheight()

root.geometry(f"300x150+{int((SCR_WIDTH/5)-(300/2))}+{int((SCR_HEIGHT/5)-(150/2))}")
root.maxsize(300,SCR_HEIGHT)
root.minsize(300,150)
root.title("Tin Getter")

root.wm_attributes("-topmost", 1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_columnconfigure(6, weight=1)
# root.grid_rowconfigure(1, weight=1)

def reset_ui():
    for child in root.winfo_children():
        if child.winfo_class() != "Menubutton":
            child.destroy()

def OptionMenu_CheckButton(event):

    reset_ui()

    root.show_bt = tk.Button(root, text="Show", command=get_tin)
    root.show_bt.grid(row=1, column=0, columnspan=7 ,sticky="new")

def get_tin():

    with create_connection(database_file()) as conn:
        clients = fetch_clients(conn, client_name=clicked.get())

    reset_ui()
    row = 1

    for tin, _ in clients:

        digits = tin.split("-")
        col = 0

        for index, digit in enumerate(digits):

            entr = tk.Entry(root, width=4)
            entr.grid(row=row, column=col, columnspan=1)
            cpy_btn = tk.Button(root, text="Copy", command=lambda e=entr: root.clipboard_clear(
            ) or root.clipboard_append(e.get())).grid(row=row+1, column=col)

            entr.insert(0, digit)
            entr.config(state="disabled")
            col += 2

            if index == len(digits) - 1:
                break

            tk.Label(root, text="-").grid(row=row, column=col-1)

        row += 2

clicked = tk.StringVar()
clicked.set("Client Name")

with create_connection(database_file()) as conn:
    clients = fetch_clients(conn)

client_info = {}

for client in clients:
    tin, name =  client
    
    client_info[tin] = name

options = [name for name in set(client_info.values())]
options.sort()

dropdown = tk.OptionMenu(root, clicked, *options, command=OptionMenu_CheckButton)
dropdown.grid(row=0, column=0, columnspan=7, sticky="nsew")

root.mainloop()