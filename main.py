import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

PRODUCT_FILE = "products.json"
SALES_FILE = "sales.json"


# ---------------- FILE SETUP ---------------- #

def initialize_files():
    if not os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, "w") as f:
            json.dump([], f)


def load_products():
    try:
        with open(PRODUCT_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_products(data):
    with open(PRODUCT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_sales():
    try:
        with open(SALES_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_sales(data):
    with open(SALES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_next_invoice_number():
    sales = load_sales()
    if not sales:
        return 1
    return max(s["invoice_no"] for s in sales) + 1


# ---------------- POS SYSTEM ---------------- #

class StorePOS:

    def __init__(self, root):

        self.root = root
        self.root.title("Bhavin Smart POS")
        self.root.geometry("1400x750")
        self.root.configure(bg="#1e1e2f")

        initialize_files()

        self.bill_data = {}
        self.current_total = 0
        self.invoice_counter = get_next_invoice_number()

        self.create_widgets()
        self.update_stock_status()

    # ---------------- UI ---------------- #

    def create_widgets(self):

        # TOP BAR
        top = tk.Frame(self.root, bg="#2c2c3e", height=60)
        top.pack(fill="x")

        tk.Label(top,
                 text="BHAVIN SELLS",
                 font=("Segoe UI", 20, "bold"),
                 bg="#2c2c3e",
                 fg="white").pack(side="left", padx=20)

        tk.Label(top,
                 text=datetime.now().strftime("%d-%m-%Y"),
                 font=("Segoe UI", 12),
                 bg="#2c2c3e",
                 fg="white").pack(side="right", padx=20)

        # NAVBAR
        nav = tk.Frame(self.root, bg="#141423", height=40)
        nav.pack(fill="x")

        tk.Button(nav, text="Bills",
                  bg="#141423", fg="white", bd=0).pack(side="left", padx=20)

        tk.Button(nav, text="Recent Bills",
                  bg="#141423", fg="white", bd=0,
                  command=self.open_recent_bills_window).pack(side="left", padx=20)

        tk.Button(nav, text="Inventory",
                  bg="#141423", fg="white", bd=0,
                  command=self.inventory_window).pack(side="left", padx=20)

        tk.Button(nav, text="Day Report",
                  bg="#141423", fg="white", bd=0,
                  command=self.open_day_report_window).pack(side="left", padx=20)

        self.stock_status_label = tk.Label(nav,
                                           bg="#141423",
                                           fg="yellow",
                                           font=("Segoe UI", 10, "bold"))
        self.stock_status_label.pack(side="right", padx=20)

        # BODY
        body = tk.Frame(self.root, bg="#1e1e2f")
        body.pack(fill="both", expand=True)

        # BILL PANEL
        left = tk.Frame(body, bg="#2c2c3e")
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        tk.Label(left, text="Customer Bill",
                 font=("Segoe UI", 14, "bold"),
                 bg="#2c2c3e",
                 fg="white").pack(pady=10)

        columns = ("ID", "Name", "Qty", "Price", "Amount")

        self.bill_table = ttk.Treeview(left,
                                       columns=columns,
                                       show="headings",
                                       height=20)

        for col in columns:
            self.bill_table.heading(col, text=col)
            self.bill_table.column(col, width=120, anchor="center")

        self.bill_table.pack(fill="both", expand=True, padx=10)

        self.total_label = tk.Label(left,
                                    text="Total Amount: ₹0",
                                    font=("Segoe UI", 18, "bold"),
                                    bg="#2c2c3e",
                                    fg="red")

        self.total_label.pack(pady=10)

        btn_frame = tk.Frame(left, bg="#2c2c3e")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Remove Item",
                  bg="#f44336", fg="white",
                  command=self.remove_item).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Print Bill",
                  bg="#4CAF50", fg="white",
                  command=self.ask_payment_and_print).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Clear Bill",
                  bg="#FF9800", fg="white",
                  command=self.clear_bill).grid(row=0, column=2, padx=10)

        # PRODUCT PANEL
        right = tk.Frame(body, bg="#2c2c3e")
        right.pack(side="right", fill="both", padx=5, pady=5)

        tk.Label(right, text="Products",
                 font=("Segoe UI", 14, "bold"),
                 bg="#2c2c3e",
                 fg="white").pack(pady=10)

        self.product_frame = tk.Frame(right, bg="#2c2c3e")
        self.product_frame.pack(fill="both", expand=True)

        self.display_products()

    # ---------------- STOCK STATUS ---------------- #

    def update_stock_status(self):

        products = load_products()

        total_products = len(products)
        total_stock = sum(p["qty"] for p in products)

        self.stock_status_label.config(
            text=f"Products: {total_products} | Total Stock: {total_stock}"
        )

    # ---------------- PRODUCTS ---------------- #

    def display_products(self):

        for w in self.product_frame.winfo_children():
            w.destroy()

        products = load_products()

        row = col = 0

        for p in products:

            stock = p["qty"]

            color = "green" if stock > 5 else "orange" if stock > 0 else "gray"

            btn = tk.Button(self.product_frame,
                            text=f"{p['name']}\n₹{p['price']}\nStock:{stock}",
                            width=15,
                            height=4,
                            bg=color,
                            fg="white",
                            command=lambda prod=p: self.add_to_bill(prod))

            btn.grid(row=row, column=col, padx=5, pady=5)

            col += 1

            if col == 4:
                col = 0
                row += 1

    # ---------------- BILL ---------------- #

    def add_to_bill(self, product):

        pid = product["id"]
        stock = product["qty"]

        current_qty = self.bill_data.get(pid, {}).get("qty", 0)

        if current_qty >= stock:
            messagebox.showerror("Stock Limit",
                                 f"Only {stock} items available")
            return

        if pid in self.bill_data:
            self.bill_data[pid]["qty"] += 1
        else:
            self.bill_data[pid] = {
                "name": product["name"],
                "price": product["price"],
                "qty": 1
            }

        self.update_bill_table()

    def update_bill_table(self):

        for row in self.bill_table.get_children():
            self.bill_table.delete(row)

        self.current_total = 0

        for pid, data in self.bill_data.items():

            amount = data["qty"] * data["price"]

            self.current_total += amount

            self.bill_table.insert("", "end",
                                   values=(pid,
                                           data["name"],
                                           data["qty"],
                                           data["price"],
                                           amount))

        self.total_label.config(text=f"Total Amount: ₹{self.current_total}")

    # ---------------- REMOVE ITEM ---------------- #

    def remove_item(self):

        selected = self.bill_table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Select item first")
            return

        item = self.bill_table.item(selected[0])

        pid = item["values"][0]

        if pid in self.bill_data:
            del self.bill_data[pid]

        self.update_bill_table()

    # ---------------- CLEAR BILL ---------------- #

    def clear_bill(self):
        self.bill_data.clear()
        self.update_bill_table()

    # ---------------- PAYMENT ---------------- #

    def ask_payment_and_print(self):

        if not self.bill_data:
            messagebox.showwarning("Warning", "No items in bill")
            return

        pay = tk.Toplevel(self.root)
        pay.title("Payment")
        pay.geometry("300x150")

        tk.Label(pay, text="Payment Method").pack(pady=10)

        pay_var = tk.StringVar(value="Cash")

        ttk.Combobox(pay,
                     textvariable=pay_var,
                     values=["Cash", "Online", "Card"],
                     state="readonly").pack(pady=10)

        tk.Button(pay, text="Confirm",
                  command=lambda: [pay.destroy(),
                                   self.print_bill(pay_var.get())]).pack(pady=10)

    # ---------------- PRINT BILL ---------------- #

    def print_bill(self, payment_method):

        products = load_products()

        for pid, data in self.bill_data.items():
            for p in products:
                if p["id"] == pid:
                    p["qty"] -= data["qty"]

        save_products(products)

        bill = tk.Toplevel(self.root)
        bill.title("Invoice")
        bill.geometry("420x550")

        text = tk.Text(bill,
                       font=("Courier New", 11),
                       padx=10,
                       pady=10)

        text.pack(fill="both", expand=True)

        text.insert(tk.END, "\n")
        text.insert(tk.END, "        BHAVIN SELLS\n")
        text.insert(tk.END, "--------------------------------\n")

        date_time = datetime.now().strftime("%d-%m-%Y %H:%M")

        text.insert(tk.END, f"Invoice : {self.invoice_counter}\n")
        text.insert(tk.END, f"Date    : {date_time}\n")
        text.insert(tk.END, f"Payment : {payment_method}\n")

        text.insert(tk.END, "--------------------------------\n")

        text.insert(tk.END, f"{'Item':<15}{'Qty':<5}{'Price':<8}{'Total'}\n")
        text.insert(tk.END, "--------------------------------\n")

        subtotal = 0

        for pid, data in self.bill_data.items():

            name = data["name"][:14]
            qty = data["qty"]
            price = data["price"]
            total = qty * price

            subtotal += total

            text.insert(tk.END,
                        f"{name:<15}{qty:<5}{price:<8}{total}\n")

        text.insert(tk.END, "--------------------------------\n")

        gst = subtotal * 0.18
        final_total = subtotal + gst

        text.insert(tk.END, f"Subtotal : ₹{subtotal}\n")
        text.insert(tk.END, f"GST 18%  : ₹{gst:.2f}\n")
        text.insert(tk.END, "--------------------------------\n")

        text.insert(tk.END, f"TOTAL    : ₹{final_total:.2f}\n")

        text.insert(tk.END, "--------------------------------\n")
        text.insert(tk.END, "\n        Thank You!\n")

        sales = load_sales()

        sales.append({
            "invoice_no": self.invoice_counter,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": final_total,
            "payment": payment_method
        })

        save_sales(sales)

        self.invoice_counter += 1

        self.clear_bill()
        self.display_products()
        self.update_stock_status()

    # ---------------- INVENTORY ---------------- #

    def inventory_window(self):

        win = tk.Toplevel(self.root)
        win.title("Inventory")
        win.geometry("800x500")

        columns = ("ID", "Name", "Price", "Qty")

        self.inv_table = ttk.Treeview(win,
                                      columns=columns,
                                      show="headings")

        for col in columns:
            self.inv_table.heading(col, text=col)

        self.inv_table.pack(fill="both", expand=True)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product",
                  command=self.add_product_inventory).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Update Price",
                  command=self.update_price_from_inventory).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Update Qty",
                  command=self.update_qty_from_inventory).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete",
                  command=self.delete_product_from_inventory).pack(side="left", padx=5)

        self.load_inventory()

    def load_inventory(self):

        for i in self.inv_table.get_children():
            self.inv_table.delete(i)

        for p in load_products():
            self.inv_table.insert("", "end",
                                  values=(p["id"], p["name"], p["price"], p["qty"]))

    def add_product_inventory(self):

        name = simpledialog.askstring("Product Name", "Enter product name")
        price = simpledialog.askfloat("Price", "Enter price")
        qty = simpledialog.askinteger("Qty", "Enter quantity")

        products = load_products()

        new_id = max([p["id"] for p in products], default=0) + 1

        products.append({
            "id": new_id,
            "name": name,
            "price": price,
            "qty": qty
        })

        save_products(products)

        self.load_inventory()
        self.display_products()
        self.update_stock_status()

    def update_price_from_inventory(self):

        selected = self.inv_table.selection()

        if not selected:
            return

        item = self.inv_table.item(selected[0])
        pid = item["values"][0]

        new_price = simpledialog.askfloat("New Price", "Enter new price")

        products = load_products()

        for p in products:
            if p["id"] == pid:
                p["price"] = new_price

        save_products(products)

        self.load_inventory()
        self.display_products()

    def update_qty_from_inventory(self):

        selected = self.inv_table.selection()

        if not selected:
            return

        item = self.inv_table.item(selected[0])
        pid = item["values"][0]

        new_qty = simpledialog.askinteger("Stock", "Enter new stock")

        products = load_products()

        for p in products:
            if p["id"] == pid:
                p["qty"] = new_qty

        save_products(products)

        self.load_inventory()
        self.display_products()
        self.update_stock_status()

    def delete_product_from_inventory(self):

        selected = self.inv_table.selection()

        if not selected:
            return

        item = self.inv_table.item(selected[0])
        pid = item["values"][0]

        products = [p for p in load_products() if p["id"] != pid]

        save_products(products)

        self.load_inventory()
        self.display_products()
        self.update_stock_status()

    # ---------------- REPORT ---------------- #

    def open_recent_bills_window(self):

        win = tk.Toplevel(self.root)
        win.title("Recent Bills")
        win.geometry("700x400")

        table = ttk.Treeview(win,
                             columns=("Invoice", "Date", "Total", "Payment"),
                             show="headings")

        for col in ("Invoice", "Date", "Total", "Payment"):
            table.heading(col, text=col)

        table.pack(fill="both", expand=True)

        for s in load_sales():
            table.insert("", "end",
                         values=(s["invoice_no"],
                                 s["date"],
                                 s["total"],
                                 s["payment"]))

    def open_day_report_window(self):

        today = datetime.now().strftime("%Y-%m-%d")

        sales = load_sales()

        total = 0
        count = 0

        for s in sales:
            if today in s["date"]:
                total += s["total"]
                count += 1

        messagebox.showinfo("Day Report",
                            f"Today's Bills: {count}\nTotal Sale ₹{total}")


# ---------------- RUN ---------------- #

if __name__ == "__main__":

    root = tk.Tk()
    app = StorePOS(root)
    root.mainloop()