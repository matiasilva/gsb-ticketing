import time
import tkinter as tk

import psycopg2


class App:
    def __init__(self, master):
        self.master = master
        self.label = tk.Label(self.master, text="ticket monitor")
        self.label.pack()
        self.get_data()

    def get_data(self):
        conn = psycopg2.connect(
            database="gsb23_tickets",
            user="matias",
            password="",
            host="localhost",
            port="5432",
        )
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM scanner_attendance")
        result = cur.fetchone()[0]
        self.label.configure(text=result)
        self.master.after(1000, self.get_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
