import tkinter as tk
from tkinter import messagebox, font

def calculate_bmr(age, weight, height, gender):
    if gender == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == 'female':
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_calories_needed(bmr, activity_factor):
    return bmr * activity_factor

def submit():
    try:
        age = int(age_entry.get())
        weight = float(weight_entry.get())
        height = float(height_entry.get())
        gender = gender_var.get()
        activity_factor = float(activity_levels[activity_var.get()][1])

        if age < 13 or age > 100 or weight < 30 or weight > 300 or height < 100 or height > 250:
            raise ValueError("Input out of range")

        bmr = calculate_bmr(age, weight, height, gender)
        calories_needed = calculate_calories_needed(bmr, activity_factor)
        messagebox.showinfo("Calorie Needs", f"Your estimated daily calorie need is: {calories_needed:.2f} calories")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

root = tk.Tk()
root.title("Calorie Calculator")
app_font = font.Font(family="Helvetica", size=12)

# Frame for entries
entry_frame = tk.Frame(root, padx=10, pady=10)
entry_frame.grid(row=0, column=0, sticky="ew")

# Entries and labels
labels = ["Age (13-100):", "Weight in kg (30-300):", "Height in cm (100-250):", "Gender:", "Activity Level:"]
entries = [tk.Entry(entry_frame, font=app_font) for _ in labels[:-2]]
age_entry, weight_entry, height_entry = entries

# Layout entries and labels
for idx, text in enumerate(labels[:-2]):
    tk.Label(entry_frame, text=text, font=app_font).grid(row=idx, column=0, sticky="w")
    entries[idx].grid(row=idx, column=1, pady=5, padx=5, sticky="ew")

# Gender selection
gender_var = tk.StringVar(value="male")
tk.Radiobutton(entry_frame, text="Male", variable=gender_var, value="male", font=app_font).grid(row=3, column=1)
tk.Radiobutton(entry_frame, text="Female", variable=gender_var, value="female", font=app_font).grid(row=3, column=2)

# Activity level selection
activity_var = tk.StringVar(value='1')
activity_levels = {
    'Sedentary': ('sedentary', 1.2),
    'Lightly active': ('lightly active', 1.375),
    'Moderately active': ('moderately active', 1.55),
    'Very active': ('very active', 1.725),
    'Hyper active': ('hyper active', 1.9)
}
tk.Label(entry_frame, text="Activity Level:", font=app_font).grid(row=4, column=0, sticky="w")
activity_menu = tk.OptionMenu(entry_frame, activity_var, *activity_levels.keys())
activity_menu.config(font=app_font)  # Set font for the dropdown
activity_menu.grid(row=4, column=1, sticky="ew")

# Submit button
submit_button = tk.Button(entry_frame, text="Calculate", command=submit, font=app_font)
submit_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()