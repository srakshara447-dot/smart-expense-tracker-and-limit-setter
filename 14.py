import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

# Modern color palette - ELEGANT THEME
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#F8F9FA",
    "accent": "#E91E63",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "light": "#ECEFF1",
    "text": "#37474F",
    "soft_blue": "#E3F2FD",
    "soft_green": "#E8F5E9",
    "soft_orange": "#FFF3E0",
    "soft_purple": "#F3E5F5"
}

# Modern fonts
FONTS = {
    "title": ("Helvetica", 24, "bold"),
    "heading": ("Helvetica", 14, "bold"),
    "subheading": ("Helvetica", 12, "bold"),
    "body": ("Helvetica", 10),
    "small": ("Helvetica", 9)
}

# ---------------- FILE STORAGE ---------------- #
DATA_FILE = "expense_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "monthly_limit": 0,
        "daily_limit": 0,
        "expenses": [],
        "streak": 0
    }

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -------- CUSTOM STYLED BUTTON CLASS -------- #
class ModernButton(tk.Button):
    def __init__(self, parent, text, command, bg_color="#3498DB", fg_color="white", width=20, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = self.lighten_color(bg_color)
        
        self.config(
            bg=bg_color,
            fg=fg_color,
            font=("Helvetica", 12, "bold"),
            relief="flat",
            borderwidth=0,
            padx=25,
            pady=15,
            cursor="hand2",
            activebackground=self.hover_color,
            activeforeground=fg_color
        )
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def lighten_color(self, color):
        """Lighten a hex color for hover effect"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        return '#{:02x}{:02x}{:02x}'.format(
            min(int(rgb[0] * 1.15), 255),
            min(int(rgb[1] * 1.15), 255),
            min(int(rgb[2] * 1.15), 255)
        )
    
    def on_enter(self, event):
        self.config(bg=self.hover_color)
    
    def on_leave(self, event):
        self.config(bg=self.bg_color)

# -------- ROUNDED FRAME CLASS -------- #
class RoundedFrame(tk.Frame):
    def __init__(self, parent, bg_color=COLORS["light"], padding=15, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=COLORS["secondary"], highlightthickness=0)
        self.pack_propagate(False)
        
        inner_frame = tk.Frame(self, bg=bg_color)
        inner_frame.pack(fill="both", expand=True, padx=padding, pady=padding)
        self.inner_frame = inner_frame
        return inner_frame

# -------- CUSTOM ENTRY CLASS -------- #
class ModernEntry(tk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            font=FONTS["body"],
            relief="flat",
            borderwidth=1,
            bg=COLORS["light"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"]
        )

# -------- CUSTOM LABEL CLASS -------- #
class ModernLabel(tk.Label):
    def __init__(self, parent, text, weight="normal", size=10, **kwargs):
        font_name = "Helvetica"
        if weight == "bold":
            font_name = f"{font_name} {size} bold"
        else:
            font_name = f"{font_name} {size}"
        
        super().__init__(parent, text=text, font=font_name, **kwargs)



# -------- FUNCTIONS -------- #

def set_limits():
    try:
        data["monthly_limit"] = float(monthly_entry.get())
        data["daily_limit"] = float(daily_entry.get())
        save_data()
        limit_window.destroy()
        update_status()
        messagebox.showinfo("Success 🎉", "Limits Set Successfully!")
    except:
        messagebox.showerror("Error ❌", "Enter valid numbers")

def add_expense():
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            messagebox.showwarning("Invalid Amount", "Amount must be positive!")
            return

        category = category_var.get()
        today = datetime.now().strftime("%Y-%m-%d")

        data["expenses"].append({
            "amount": amount,
            "category": category,
            "date": today
        })

        expense_list.insert("", "end", values=(today, category, f"₹{amount}"))
        amount_entry.delete(0, tk.END)

        save_data()
        update_status()

    except:
        messagebox.showerror("Error ❌", "Enter valid amount")

def get_total():
    return sum(exp["amount"] for exp in data["expenses"])

def get_today_total():
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(exp["amount"] for exp in data["expenses"] if exp["date"] == today)

def update_status():
    total = get_total()
    today_total = get_today_total()

    remaining = max(0, data["monthly_limit"] - total)

    total_label.config(text=f"Monthly Spent: ₹{total}")
    daily_label.config(text=f"Today Spent: ₹{today_total}")

    if total > data["monthly_limit"]:
        remaining_label.config(text="Remaining: ₹0 (Limit Exceeded)")
    else:
        remaining_label.config(text=f"Remaining: ₹{remaining}")

    if data["monthly_limit"] > 0:
        percent = (total / data["monthly_limit"]) * 100
        progress['value'] = min(percent, 100)

        if percent >= 100:
            status_label.config(text="🚨 Monthly Limit Exceeded!", fg="red")
        elif percent >= 80:
            status_label.config(text="⚠️ 80% Budget Used!", fg="orange")
        else:
            status_label.config(text="✅ Within Budget", fg="green")
    else:
        progress['value'] = 0
        status_label.config(text="Set Monthly Limit", fg="black")

    smart_advice()
    update_streak()

def smart_advice():
    category_totals = {}
    for exp in data["expenses"]:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]

    if category_totals:
        highest = max(category_totals, key=category_totals.get)
        advice_label.config(
            text=f"💡 Tip: You spend most on {highest}. Try reducing it!",
            fg="#4b0082"
        )
    else:
        advice_label.config(text="")

def update_streak():
    if data["daily_limit"] > 0 and get_today_total() <= data["daily_limit"]:
        data["streak"] += 1
    else:
        data["streak"] = 0

    streak_label.config(
        text=f"🔥 Smart Saving Streak: {data['streak']} days",
        fg="#008080"
    )

def predict_spending():
    total = get_total()
    day = datetime.now().day
    if day == 0:
        return
    predicted = (total / day) * 30
    messagebox.showinfo(
        "AI Prediction 🤖",
        f"Estimated End-of-Month Spending:\n₹{round(predicted,2)}"
    )

def show_charts():
    if not data["expenses"]:
        messagebox.showinfo("No Data", "No expenses to show!")
        return

    category_totals = {}
    date_totals = {}

    for exp in data["expenses"]:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]
        date_totals[exp["date"]] = date_totals.get(exp["date"], 0) + exp["amount"]

    # Create a new window for charts
    chart_window = tk.Toplevel(root)
    chart_window.title("Expense Analytics")
    chart_window.geometry("1000x600")
    chart_window.config(bg=COLORS["secondary"])

    fig = Figure(figsize=(12, 5.5), dpi=100, facecolor=COLORS["secondary"], edgecolor='none')
    
    # Modern color palette for charts
    chart_colors = [COLORS["accent"], COLORS["success"], COLORS["warning"], 
                   COLORS["danger"], COLORS["soft_purple"]]

    # Pie chart
    ax1 = fig.add_subplot(131)
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())
    wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%',
                                         colors=chart_colors, startangle=90,
                                         textprops={"fontsize": 10, "weight": "bold"})
    ax1.set_title("Category Distribution", fontsize=12, weight="bold", color=COLORS["text"])
    for autotext in autotexts:
        autotext.set_color("white")

    # Bar chart
    ax2 = fig.add_subplot(132)
    bars = ax2.bar(categories, amounts, color=chart_colors, edgecolor=COLORS["text"], linewidth=1.5)
    ax2.set_title("Category Spending", fontsize=12, weight="bold", color=COLORS["text"])
    ax2.tick_params(axis='x', rotation=45, labelsize=9)
    ax2.set_ylabel("Amount (₹)", fontsize=10, weight="bold")
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Trend line chart
    ax3 = fig.add_subplot(133)
    dates = sorted(date_totals.keys())
    date_amounts = [date_totals[d] for d in dates]
    ax3.plot(dates, date_amounts, marker='o', linewidth=2.5, markersize=8, 
             color=COLORS["accent"], markerfacecolor=COLORS["success"], 
             markeredgewidth=2, markeredgecolor=COLORS["accent"])
    ax3.fill_between(range(len(dates)), date_amounts, alpha=0.2, color=COLORS["accent"])
    ax3.set_title("Daily Spending Trend", fontsize=12, weight="bold", color=COLORS["text"])
    ax3.tick_params(axis='x', rotation=45, labelsize=9)
    ax3.set_ylabel("Amount (₹)", fontsize=10, weight="bold")
    ax3.grid(alpha=0.3, linestyle='--')

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    chart_window.config(bg=COLORS["secondary"])

def generate_report():
    total = get_total()
    limit_amt = data["monthly_limit"]

    if limit_amt == 0:
        messagebox.showwarning("Set Limit", "Please set monthly limit first!")
        return

    usage = (total / limit_amt) * 100
    score = max(0, 100 - usage)

    if usage <= 50:
        status = "🏆 Excellent"
    elif usage <= 80:
        status = "👍 Good"
    elif usage <= 100:
        status = "⚠️ Risk Zone"
    else:
        status = "🚨 Critical"

    report_text = f"""
📊 MONTHLY REPORT
-------------------------
Total Spent: ₹{total}
Limit: ₹{limit_amt}
Usage: {round(usage,2)}%

💯 Financial Health Score: {round(score,1)}/100
Status: {status}
"""

    messagebox.showinfo("Monthly Report", report_text)

# 🔄 RESET FUNCTION ADDED
def reset_month():
    confirm = messagebox.askyesno(
        "Reset Confirmation",
        "Are you sure you want to reset everything for a new month?\n\nThis will clear all expenses, limits, and streak."
    )

    if confirm:
        data["monthly_limit"] = 0
        data["daily_limit"] = 0
        data["expenses"] = []
        data["streak"] = 0

        # Clear Treeview items
        for item in expense_list.get_children():
            expense_list.delete(item)
        progress['value'] = 0

        save_data()
        update_status()

        messagebox.showinfo("Reset Done ✅", "New Month Started Successfully!")

# -------- MODERN UI -------- #

root = tk.Tk()
root.title("💰 Smart Expense Tracker PRO")
root.geometry("900x1000")
root.config(bg=COLORS["secondary"])
root.resizable(True, True)

# Create style for ttk widgets
style = ttk.Style()
style.theme_use('clam')
style.configure('TProgressbar', 
                background=COLORS["success"],
                troughcolor=COLORS["light"],
                bordercolor=COLORS["text"],
                lightcolor=COLORS["success"],
                darkcolor=COLORS["success"])

# -------- SETUP LIMITS WINDOW -------- #
def setup_limits():
    global limit_window, monthly_entry, daily_entry
    limit_window = tk.Toplevel(root)
    limit_window.title("Set Your Budget Limits")
    limit_window.geometry("450x450")
    limit_window.config(bg=COLORS["secondary"])
    limit_window.resizable(False, False)

    # Header
    header = tk.Label(limit_window, text="Budget Configuration", 
                     font=("Helvetica", 20, "bold"), bg=COLORS["secondary"],
                     fg=COLORS["primary"])
    header.pack(pady=30)

    # Monthly limit frame
    monthly_frame = tk.Frame(limit_window, bg=COLORS["secondary"])
    monthly_frame.pack(pady=20, padx=40, fill="x")

    tk.Label(monthly_frame, text="Monthly Limit (₹)", font=("Helvetica", 14, "bold"),
            bg=COLORS["secondary"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))
    monthly_entry = tk.Entry(monthly_frame, font=("Helvetica", 16), relief="flat",
                            borderwidth=2, bg=COLORS["light"], fg=COLORS["text"])
    monthly_entry.pack(fill="x", ipady=12)

    # Daily limit frame
    daily_frame = tk.Frame(limit_window, bg=COLORS["secondary"])
    daily_frame.pack(pady=20, padx=40, fill="x")

    tk.Label(daily_frame, text="Daily Limit (₹)", font=("Helvetica", 14, "bold"),
            bg=COLORS["secondary"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))
    daily_entry = tk.Entry(daily_frame, font=("Helvetica", 16), relief="flat",
                          borderwidth=2, bg=COLORS["light"], fg=COLORS["text"])
    daily_entry.pack(fill="x", ipady=12)

    # Save button
    save_btn = ModernButton(limit_window, "✨ Save Limits", command=set_limits,
                           bg_color=COLORS["accent"], width=20)
    save_btn.pack(pady=30, padx=40, fill="x")

    limit_window.grab_set()

# -------- MAIN TITLE -------- #
title_frame = tk.Frame(root, bg=COLORS["primary"])
title_frame.pack(fill="x", padx=0, pady=0)

title = tk.Label(title_frame, text="💰 SMART EXPENSE MANAGER",
                font=FONTS["title"], bg=COLORS["primary"],
                fg=COLORS["light"])
title.pack(pady=20)

subtitle = tk.Label(title_frame, text="Manage Your Budget Intelligently",
                   font=FONTS["small"], bg=COLORS["primary"],
                   fg=COLORS["soft_blue"])
subtitle.pack(pady=(0, 15))

# -------- INPUT SECTION -------- #
input_section = tk.Frame(root, bg=COLORS["secondary"])
input_section.pack(fill="x", padx=20, pady=15)

tk.Label(input_section, text="Add New Expense", font=FONTS["subheading"],
        bg=COLORS["secondary"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))

input_frame = tk.Frame(input_section, bg=COLORS["light"])
input_frame.pack(fill="x", pady=10, padx=10, ipady=10)

# Amount input
amount_label = tk.Label(input_frame, text="Amount (₹)", font=FONTS["body"],
                       bg=COLORS["light"], fg=COLORS["text"])
amount_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

amount_entry = tk.Entry(input_frame, font=FONTS["body"], relief="flat",
                       borderwidth=1, bg="white", fg=COLORS["text"], width=15)
amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Category selection
category_label = tk.Label(input_frame, text="Category", font=FONTS["body"],
                         bg=COLORS["light"], fg=COLORS["text"])
category_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

categories = ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
category_var = tk.StringVar(root)
category_var.set(categories[0])

category_menu = ttk.Combobox(input_frame, textvariable=category_var, 
                            values=categories, state="readonly", width=15, font=FONTS["body"])
category_menu.grid(row=0, column=3, padx=5, pady=5)

# Add button
add_btn = ModernButton(input_frame, "➕ Add", command=add_expense,
                      bg_color=COLORS["accent"], width=8)
add_btn.grid(row=0, column=4, padx=5, pady=5)

input_frame.columnconfigure(1, weight=1)
input_frame.columnconfigure(3, weight=1)

# -------- STATISTICS SECTION -------- #
stats_section = tk.Frame(root, bg=COLORS["secondary"])
stats_section.pack(fill="x", padx=20, pady=15)

tk.Label(stats_section, text="Financial Overview", font=FONTS["subheading"],
        bg=COLORS["secondary"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))

# Stats cards
stats_frame = tk.Frame(stats_section, bg=COLORS["secondary"])
stats_frame.pack(fill="x")

# Total spent card
total_card = tk.Frame(stats_frame, bg=COLORS["light"], relief="flat", borderwidth=0)
total_card.pack(side="left", fill="both", expand=True, padx=5, pady=5, ipady=15, ipadx=15)

tk.Label(total_card, text="📊 Monthly Spent", font=FONTS["body"],
        bg=COLORS["light"], fg=COLORS["text"]).pack(anchor="w")
total_label = tk.Label(total_card, text="₹0", font=("Helvetica", 18, "bold"),
                      bg=COLORS["light"], fg=COLORS["accent"])
total_label.pack(anchor="w", pady=(5, 0))

# Daily spent card
daily_card = tk.Frame(stats_frame, bg=COLORS["soft_green"], relief="flat", borderwidth=0)
daily_card.pack(side="left", fill="both", expand=True, padx=5, pady=5, ipady=15, ipadx=15)

tk.Label(daily_card, text="📅 Today Spent", font=FONTS["body"],
        bg=COLORS["soft_green"], fg=COLORS["text"]).pack(anchor="w")
daily_label = tk.Label(daily_card, text="₹0", font=("Helvetica", 18, "bold"),
                      bg=COLORS["soft_green"], fg=COLORS["success"])
daily_label.pack(anchor="w", pady=(5, 0))

# Remaining card
remaining_card = tk.Frame(stats_frame, bg=COLORS["soft_blue"], relief="flat", borderwidth=0)
remaining_card.pack(side="left", fill="both", expand=True, padx=5, pady=5, ipady=15, ipadx=15)

tk.Label(remaining_card, text="💰 Remaining", font=FONTS["body"],
        bg=COLORS["soft_blue"], fg=COLORS["text"]).pack(anchor="w")
remaining_label = tk.Label(remaining_card, text="₹0", font=("Helvetica", 18, "bold"),
                          bg=COLORS["soft_blue"], fg=COLORS["accent"])
remaining_label.pack(anchor="w", pady=(5, 0))

# -------- STATUS SECTION -------- #
status_section = tk.Frame(root, bg=COLORS["secondary"])
status_section.pack(fill="x", padx=20, pady=15)

status_label = tk.Label(status_section, text="✅ Within Budget", font=FONTS["heading"],
                       bg=COLORS["secondary"], fg=COLORS["success"])
status_label.pack(pady=5)

# Progress bar with styling
progress_section = tk.Frame(status_section, bg=COLORS["secondary"])
progress_section.pack(fill="x", pady=10)

progress = ttk.Progressbar(progress_section, length=500, mode='determinate',
                          style='TProgressbar', value=0)
progress.pack(fill="x", ipady=3)

# -------- MOTIVATIONAL SECTION -------- #
motivation_section = tk.Frame(root, bg=COLORS["secondary"])
motivation_section.pack(fill="x", padx=20, pady=15)

streak_label = tk.Label(motivation_section, text="🔥 Streak: 0 days",
                       font=FONTS["heading"], bg=COLORS["secondary"],
                       fg=COLORS["warning"])
streak_label.pack(pady=5)

advice_label = tk.Label(motivation_section, text="", font=FONTS["small"],
                       bg=COLORS["secondary"], fg=COLORS["text"],
                       wraplength=700, justify="center")
advice_label.pack(pady=5)

# -------- ACTION BUTTONS SECTION -------- #
button_section = tk.Frame(root, bg=COLORS["secondary"])
button_section.pack(fill="x", padx=20, pady=15)

btn_frame_1 = tk.Frame(button_section, bg=COLORS["secondary"])
btn_frame_1.pack(fill="x", pady=5)

predict_btn = ModernButton(btn_frame_1, "🤖 Predict Spending", command=predict_spending,
                          bg_color=COLORS["accent"], width=20)
predict_btn.pack(side="left", padx=5, fill="x", expand=True)

charts_btn = ModernButton(btn_frame_1, "📊 Analytics", command=show_charts,
                         bg_color=COLORS["success"], width=20)
charts_btn.pack(side="left", padx=5, fill="x", expand=True)

btn_frame_2 = tk.Frame(button_section, bg=COLORS["secondary"])
btn_frame_2.pack(fill="x", pady=5)

report_btn = ModernButton(btn_frame_2, "📄 Report", command=generate_report,
                         bg_color=COLORS["warning"], width=20)
report_btn.pack(side="left", padx=5, fill="x", expand=True)

reset_btn = ModernButton(btn_frame_2, "🔄 Reset Month", command=reset_month,
                        bg_color=COLORS["danger"], width=20)
reset_btn.pack(side="left", padx=5, fill="x", expand=True)

# -------- EXPENSE HISTORY SECTION -------- #
history_section = tk.Frame(root, bg=COLORS["secondary"])
history_section.pack(fill="both", expand=True, padx=20, pady=15)

tk.Label(history_section, text="Expense History", font=FONTS["subheading"],
        bg=COLORS["secondary"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))

# Create Treeview for expenses
tree_frame = tk.Frame(history_section, bg=COLORS["light"], relief="flat", borderwidth=0)
tree_frame.pack(fill="both", expand=True)

columns = ("Date", "Category", "Amount")
expense_list = ttk.Treeview(tree_frame, columns=columns, height=10, show="headings",
                           style='Treeview')

expense_list.column("Date", width=100, anchor="center")
expense_list.column("Category", width=150, anchor="w")
expense_list.column("Amount", width=100, anchor="e")

expense_list.heading("Date", text="📅 Date")
expense_list.heading("Category", text="🏷️ Category")
expense_list.heading("Amount", text="💵 Amount")

# Scrollbar
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=expense_list.yview)
expense_list.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
expense_list.pack(fill="both", expand=True)

# Initialize with limit setup
setup_limits()

# Update display
update_status()
root.mainloop()