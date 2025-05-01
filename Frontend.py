import math, weakref
import tkinter as tk
from tkinter import font

from Logic import get_block, find_producers, unit_math
from Ratios import units, drillables, blocks, liquids

#%% TODO, 0.3A:
# Implement recursive production finding
# Make buttons for ^^^
#%% TODO, 1.1:
# Add Erekir

#%% TODO, 1.1/2.0:
# Switch to CTk for better-looking UI.
# Possibly rewrite whole program for more efficiency and consistent structuring of elements (blocks vs units in particular).
# Add more input methods, like items/sec; perform math based on that, assuming is limiting resource.
# Add support for domes
#%% UI creation
root = tk.Tk()
root.title("Serpulo Ratio Calculator")
root.configure(bg="#202020")
custom_font = font.Font(family="fontello", size=11)
root.option_add("*Font", custom_font)

class UiTools:
    def __init__(self, uiToolsRoot, main_menu_command):
        self.root = uiToolsRoot
        self.main_menu_command = main_menu_command

    @staticmethod
    def reset_grid():
        UiTools.clear_full()
        prompt = tk.Label(root, text="What do you want to make?")
        prompt.grid(row=0, column=0, columnspan=5)
        prompt.configure(bg="#202020", fg="#ffffff")
        line = tk.Frame(root, height=3, bg="#808080")
        line.grid(row=1, columnspan=5, sticky="ew")

    @staticmethod
    def clear_grid(minRow, maxRow, parent):
        for widget in parent.grid_slaves():
            if minRow < widget.grid_info()['row'] < maxRow:
                widget.destroy()

    @staticmethod
    def clear_full():
        # Clears widgets from the grid except the first two rows.
        for widget in root.grid_slaves():
            widget.destroy()

    @staticmethod
    def hline(row):
        hline = tk.Frame(root, height=3, bg="#404040")
        hline.grid(row=row, column=0, columnspan=5, sticky="ew")

    @staticmethod
    def on_enter(e):
        # Handles mouse enter event for button highlighting.
        e.widget['highlightbackground'] = "#fcd47c"

    @staticmethod
    def on_leave(e):
        # Handles mouse leave event for button highlighting.
        e.widget['highlightbackground'] = "#202020"

    @staticmethod
    def back_button(parent, row, cols, command):
        back_button = tk.Button(parent, image=images["back"], width=32, height=32,
                                borderwidth=0,
                                highlightthickness=2,
                                highlightbackground="#202020",
                                activeforeground="#ffffff",
                                highlightcolor="#fcd47c",
                                bg="#202020",
                                activebackground="#202020",
                                command=command)
        back_button.grid(row=row, column=0, columnspan=cols, pady=10)
        back_button.bind("<Enter>", UiTools.on_enter)
        back_button.bind("<Leave>", UiTools.on_leave)

    @staticmethod
    def standard_button(location, row, col, image, text, height, width, command=None):
        button = tk.Button(
            location,
            image=image,
            text=text,
            fg="#ffffff",
            compound="top",
            borderwidth=0,
            highlightthickness=2,
            highlightbackground="#202020",
            activeforeground="#ffffff",
            highlightcolor="#fcd47c",
            bg="#202020",
            activebackground="#202020",
            padx=0,
            pady=1,
            height=height,
            width=width,
            command=command)
        button.grid(row=row, column=col, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)

    @staticmethod
    def standard_label(parent, row, col, colspan, text, image):
        label = tk.Label(parent, text=text, image=image)
        label.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5)
        label.configure(bg="#202020", fg="#ffffff")

class BaseComponents:
    # A reusable base class for UI components using grid layout.
    def __init__(self, parent):
        self.parent = parent  # Store the parent widget

    def grid(self, row, column, **kwargs):
        # Helper method to place all child widgets in a grid layout.
        for widget in vars(self).values():
            if isinstance(widget, tk.Widget):
                widget.grid(row=row, column=column, **kwargs)

class FancySpinbox(BaseComponents):
    # A Spinbox that enforces value limits but does not perform operations itself.
    def __init__(self, parent, row, column, colspan=1, minVal=0.0, maxVal=100.0, width=5):
        super().__init__(parent)
        self.columnspan = colspan
        self.minVal = minVal
        self.maxVal = maxVal
        self.width = width
        self.observers = weakref.WeakSet()

        # StringVar to hold the Spinbox value
        self.spinboxVar = tk.StringVar(value=str(self.minVal))

        # Create the Spinbox
        self.spinbox = tk.Spinbox(
            parent, from_=self.minVal, to=self.maxVal, textvariable=self.spinboxVar, width=width,
            format="%.2f")
        self.spinbox.grid(row=row, column=column, columnspan=colspan, padx=5, pady=5, sticky="ew")
        self.spinbox.configure(bg="#202020", fg="#ffffff",
                               borderwidth=0, highlightthickness=0,
                               buttonbackground="#202020")

        # Add trace to check input
        self.spinboxVar.trace_add("write", self.validate_input)

    def validate_input(self, *args):
        # Schedules a correction to ensure the input stays valid.
        self.parent.after(1, self.correct_value)  # Delay correction to allow Tkinter update

    def correct_value(self):
        # Ensures input is properly formatted and within bounds.
        try:
            value = float(self.spinboxVar.get())
            if value > self.maxVal:
                self.spinboxVar.set(str(self.maxVal))  # Set to max if too large
            elif value < self.minVal:
                self.spinboxVar.set(str(self.minVal))  # Set to min if too small
        except ValueError:
            if self.spinboxVar.get() == "":
                return  # Allow temporary empty input
            self.spinboxVar.set(str(self.minVal))  # Reset on invalid input

    def get_value(self):
        # Returns the current value of the Spinbox as an integer.
        try:
            return float(self.spinboxVar.get())
        except ValueError:
            return self.minVal  # Return min if invalid

    def set_value(self, newValue):
        """Externally update the Spinbox value, ensuring it's within range, and notify observers."""
        newValue = max(self.minVal, min(self.maxVal, newValue))  # Clamp within bounds
        self.spinboxVar.set(f"{newValue:.2f}")  # Update value formatted to 2 decimals
        self.update_observers()  # Notify observers after setting

    def update_observers(self, *args):
        """Notify all observers that the Spinbox value has changed."""
        for observer in list(self.observers):
            try:
                observer()
            except Exception:
                self.observers.discard(observer)

    def add_observer(self, observerFunction):
        """Allows other objects (like labels) to react to Spinbox value changes."""
        self.observers.add(observerFunction)

class OperationLabel(BaseComponents):
    # A label that updates dynamically based on a given Spinbox value.
    def __init__(self, parent, row, column, spinbox, operation, labelText):
        super().__init__(parent)
        self.spinbox = spinbox  # Reference to the spinbox instance
        self.operation = operation  # Function to apply to spinbox value
        self.labelText = labelText

        # Create label for static text (label_text)
        self.staticLabel = tk.Label(parent, text=self.labelText)
        self.staticLabel.grid(row=row, column=column, padx=5, pady=5)
        self.staticLabel.configure(bg="#202020", fg="#ffffff", )

        # Create label for dynamic result
        self.resultLabel = tk.Label(parent, text=f"{self.operation(self.spinbox.get_value()):.2f}")
        self.resultLabel.grid(row=row, column=column + 1, padx=5, pady=5)
        self.resultLabel.configure(bg="#202020", fg="#ffffff", )

        # Update the dynamic result when spinbox value changes
        self.spinbox.spinboxVar.trace_add("write", self.update_label)

    def update_label(self, *args):
        # Only update if the resultLabel widget still exists.
        if not self.resultLabel.winfo_exists():
            return
        try:
            value = self.operation(self.spinbox.get_value())
            self.resultLabel.config(text=f"{value:.2f}")
        except Exception as e:
            # Optionally log or handle exceptions
            pass

class ToggleButton(BaseComponents):
    def __init__(self, parent, image_on, image_off, state_on="on", state_off="off", command=None):
        super().__init__(parent)

        # Load images
        self.image_on = image_on
        self.image_off = image_off

        # State tracking
        self.state_on = state_on
        self.state_off = state_off
        self.state = state_off  # Start with 'off' state

        # Button widget
        self.button = tk.Button(
            parent,
            image=self.image_off,
            borderwidth=0,
            highlightthickness=2,
            highlightbackground="#202020",
            activeforeground="#ffffff",
            highlightcolor="#fcd47c",
            bg="#202020",
            activebackground="#202020",
            command=self.toggle
        )
        self.command = command  # External function
        self.group = None  # Will be set when added to a ToggleGroup

    def toggle(self):
        """Toggles the button state and updates the image."""
        if self.state == self.state_off:
            self.state = self.state_on
            self.button.config(image=self.image_on)
            if self.group:
                self.group.update_exclusive(self)  # Notify group to turn other buttons off
        else:
            self.state = self.state_off
            self.button.config(image=self.image_off)

        # Call external function if provided
        if self.command:
            self.command()

    def get_state(self):
        """Returns the current state of the toggle button."""
        return self.state

class ToggleGroup:
    def __init__(self):
        self.buttons = []

    def add_button(self, button):
        """Registers a ToggleButton and links it to this group."""
        self.buttons.append(button)
        button.group = self  # Assign the group reference

    def update_exclusive(self, active_button):
        """Ensure that only one button is 'on' at any time."""
        # If a button is turned 'on', make sure all others are turned off.
        for button in self.buttons:
            if button is not active_button and button.state == button.state_on:
                button.state = button.state_off  # Set 'off'
                button.button.config(image=button.image_off)  # Update UI

def reformat_entry(text):
    text = text.lower()
    if "_" in text:
        textPieces = text.split("_")
    elif " " in text:
        textPieces = text.split(" ")
    else:
        textPieces = [text]
    for i in range(len(textPieces)):
        if i > 0:
            text += textPieces[i].capitalize()
        else:
            text = textPieces[i]
    return text

def main_menu():
    UiTools.reset_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (image, text, command) in enumerate(mainMenuButtons):
        UiTools.standard_button(frame, 0, idx, image, text, 50, 90, command)

def turret_selection():
    UiTools.reset_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(turretsMenuButtons):
        UiTools.standard_button(frame, idx // 4, idx % 4, image, text, 50, 100, command)
    UiTools.back_button(root, 3, 4, lambda: main_menu())

def power_selection():
    UiTools.reset_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image) in enumerate(powerMenuButtons):
        word1, word2 = text.split()
        text1 = f"{word1}\n{word2}"
        UiTools.standard_button(frame, idx // 3, idx % 3, image, text1, 65, 90, lambda name=text: power_window(name))
    UiTools.back_button(root, 3, 4, lambda: main_menu())

def units_selection():
    UiTools.reset_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(unitsMenuButtons):
        UiTools.standard_button(frame, idx % 5, idx // 5, image, text, 50, 90, command)
    UiTools.back_button(root, 3, 4, lambda: main_menu())

def materials_selection():
    UiTools.reset_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(materialsMenuButtons):
        UiTools.standard_button(frame, idx // 4, idx % 4, image, text, 50, 95, command)
    UiTools.back_button(root, 3, 4, lambda: main_menu())

def turrets_window(name):
    def item_bullets():
        maxRow = 0
        if block.get('power'):
            for widget in outputFrame.grid_slaves():
                if int(widget.grid_info()['row']) > maxRow:
                    maxRow = widget.grid_info()['row']
        else:
            maxRow = float("inf")
        for widget in outputFrame.grid_slaves():
            if int(widget.grid_info()['row']) < maxRow:
                widget.destroy()
        if coolantWater.get_state() == "water":
            coolantMulti = block.get('coolant')['Water'][1]
        elif coolantCryo.get_state() == "cryofluid":
            coolantMulti = block.get('coolant')['Cryofluid'][1]
        else:
            coolantMulti = 1
        if block.get('ammoTypes') or block.get('liquidAmmo'):
            UiTools.standard_label(outputFrame, 0, 0, 1, "Ammo type", None)
            UiTools.standard_label(outputFrame, 0, 1, 1, "Feed rate", None)
        for i, (ammo, modifiers) in enumerate(block.get('ammoTypes').items()):
            fireRate = 60 * block.get('burst') * block.get('ammoUse') * (coolantMulti + modifiers[0] - 1) / (modifiers[1] * block.get('reloadTime'))
            OperationLabel(outputFrame, i + 1, 0, gunCount, lambda x, rate=fireRate: x * rate, "")
            UiTools.standard_button(outputFrame, i + 1, 0, images[ammo.lower()], None, 32, 32, lambda name=ammo, rate=fireRate,
                                                                                                    count=gunCount.get_value(): materials_window(name, rate * count))
        root.update()

    def liquid_bullets():
        maxRow = 0
        if block.get('power'):
            for widget in outputFrame.grid_slaves():
                if int(widget.grid_info()['row']) > maxRow:
                    maxRow = widget.grid_info()['row']
        else:
            maxRow = float("inf")
        for widget in outputFrame.grid_slaves():
            if int(widget.grid_info()['row']) < maxRow:
                widget.destroy()
        UiTools.standard_label(outputFrame, 0, 0, 1, "Ammo type", None)
        UiTools.standard_label(outputFrame, 0, 1, 1, "Feed rate", None)
        if not block.get('consumptionRate'): return None
        for i, ammo in enumerate(block.get('liquidAmmo')):
            OperationLabel(outputFrame, i + 1, 0, gunCount, lambda x, rate=block.get('consumptionRate'): x * rate, "")
            UiTools.standard_label(outputFrame, i + 1, 0, 1, None, images[ammo.lower()])
        root.update()

    UiTools.clear_full()
    block = get_block(name)
    UiTools.standard_label(root, 0, 0, 1, name, None)
    UiTools.standard_label(root, 0, 1, 2, None, images[name.lower()])
    UiTools.standard_label(root, 1, 0, 1, "How many guns?", None)
    gunCount = FancySpinbox(root, 1, 1, 2, 1, 1000, 4)
    UiTools.hline(2)
    coolants = []
    coolantGroup = ToggleGroup()
    if "Water" in block.get('coolant'):
        coolants.append("Water")
    if "Cryofluid" in block.get('coolant'):
        coolants.append("Cryofluid")
    UiTools.standard_label(root, 3, 0, 1, "Coolant:", None)
    if "Water" in coolants:
        coolantWater = ToggleButton(root, images["water toggle"], images["water"], "water", "none", lambda: item_bullets())
        coolantGroup.add_button(coolantWater)
        coolantWater.grid(row=3, column=1, padx=5, pady=5)
    else:
        UiTools.standard_label(root, 3, 1, 1, None, images["water != coolant"])
    if "Cryofluid" in coolants:
        coolantCryo = ToggleButton(root, images["cryofluid toggle"], images["cryofluid"], "cryofluid", "none", lambda: item_bullets())
        coolantGroup.add_button(coolantCryo)
        coolantCryo.grid(row=3, column=2, padx=5, pady=5)
    else:
        UiTools.standard_label(root, 3, 2, 1, None, images["cryofluid != coolant"])
    UiTools.hline(4)
    outputFrame = tk.Frame(root, bg="#202020")
    outputFrame.grid(row=5, column=0, columnspan=3)
    if len(block.get('ammoTypes')):
        item_bullets()
    elif len(block.get('liquidAmmo')):
        liquid_bullets()
    if block.get('power'):
        if len(block.get('ammoTypes')):
            row = len(block.get('ammoTypes')) + 1
        elif len(block.get('liquidAmmo')):
            row = 5
        else:
            row = 1
        OperationLabel(outputFrame, row, 0, gunCount, lambda x, power=block.get("power"): x * power, "")
        UiTools.standard_button(outputFrame, row, 0, images['power'], None, 32, 32, command=lambda power=block.get("power"): power_submenu(
            gunCount.get_value() * power))
    UiTools.back_button(root, 6, 4, lambda: turret_selection())

def power_window(name):
    def update_ui():
        for widget in inputElements.grid_slaves():
            widget.destroy()
        spinboxRefs = {}  # Store references to sync spinboxes in the same column

        def sync_spinboxes(var, column):
            """Updates all spinboxes in the same column when one changes."""
            new_value = var.get()
            for row_spinvar in spinboxRefs.get(column, []):
                if row_spinvar is not var:
                    row_spinvar.set(new_value)

        def handle_item_input(row):
            column = 0 if (toggleState if toggleState else selection.get_state()) == "power" else 3  # Choose column dynamically
            if row < len(spinboxRefs[column]):  # Ensure row index is valid
                value = float(spinboxRefs[column][row].get())  # Get numeric value
                if column:
                    rate = value * list(ratios[0].values())[0] / ratios[2]
                else:
                    rate = (math.ceil(value / (ratios[1]['Power'] - ratios[0]['Power'] if ratios[0]['Power'] else 0)) * list(ratios[0].values())[0]
                            / ratios[2])
                return rate

        # Iterate over all recipes and create UI elements dynamically
        for i, ratios in enumerate(recipes):
            imageColumn = 1 if (toggleState if toggleState else selection.get_state()) == "power" else 2
            UiTools.standard_label(inputElements, i, imageColumn, 1, None, images[list(ratios[0].keys())[0].lower()])
            UiTools.standard_button(inputElements, i, imageColumn, images[list(ratios[0].keys())[0].lower()], "", 32, 32,
                                    command=lambda itemName=list(ratios[0].keys())[0], row=i: materials_window(itemName,
                                                                                                               handle_item_input(
                                                                                                                   row)))

            if (toggleState if toggleState else selection.get_state()) == "power":
                # Power is input, Generators are calculated
                column = 0
                inputSpinbox = FancySpinbox(inputElements, i, column, minVal=0, maxVal=1000 * ratios[1]['Power'], width=4)
                spinVar = inputSpinbox.spinboxVar
                spinVar.trace_add("write", lambda *args, var=spinVar: sync_spinboxes(var, column))

                if column not in spinboxRefs:
                    spinboxRefs[column] = []
                spinboxRefs[column].append(spinVar)
                OperationLabel(inputElements, i, 2, inputSpinbox, lambda value, rate=ratios[1]["Power"]: value / rate, "Generators:")

            else:
                # Generators are input, Power is calculated
                column = 3
                inputSpinbox = FancySpinbox(inputElements, i, column, minVal=0.0, maxVal=1000, width=4)
                spinVar = inputSpinbox.spinboxVar
                spinVar.trace_add("write", lambda *args, var=spinVar: sync_spinboxes(var, column))

                if column not in spinboxRefs:
                    spinboxRefs[column] = []
                spinboxRefs[column].append(spinVar)

                OperationLabel(inputElements, i, 0, inputSpinbox, lambda value, rate=ratios[1]["Power"]: value * rate, "Power/sec:")

        root.update()

    UiTools.clear_full()
    block = get_block(name)
    UiTools.standard_label(root, 0, 0, 2, block['name'], None)
    UiTools.standard_label(root, 0, 2, 1, None, images[reformat_entry(name)])
    UiTools.standard_label(root, 1, 0, 3, "Select input method:", None)
    UiTools.standard_label(root, 2, 0, 1, "Power output", None)
    UiTools.standard_label(root, 2, 2, 1, "Generator count", None)
    selection = ToggleButton(root, images['left toggle'], images['right toggle'], "power", "count", command=lambda: update_ui())
    toggleState = None
    selection.grid(row=2, column=1, padx=5, pady=5)
    recipes = []
    if isinstance(block['recipes'], list):
        for recipe in block['recipes']:
            tempList = list(recipe.values())
            recipes.append(tempList)
    else:
        recipes.append(list(block['recipes'].values()))
    UiTools.hline(3)

    inputElements = tk.Frame(root, bg="#202020")
    inputElements.grid(row=4, column=0, columnspan=3)

    update_ui()
    UiTools.back_button(root, 5, 4, lambda: power_selection())

def units_window(name):
    def handle_item_input(rate):
        return float(entrySpinBox.get_value()) * rate

    UiTools.clear_full()
    unit = units.get(name)
    UiTools.standard_label(root, 0, 0, 1, unit.name, None)
    UiTools.standard_label(root, 0, 1, 1, None, images[unit.name.lower()])
    UiTools.standard_label(root, 1, 0, 1, 'How many to\nproduce/min?', None)
    entrySpinBox = FancySpinbox(root, 1, 1, minVal=1, maxVal=1000)
    UiTools.hline(2)
    for i, (key, value) in enumerate(unit_math(name).items()):
        if key == "Output":
            break
        elif key == 'Power':
            OperationLabel(root, i + 3, 0, entrySpinBox, lambda x, amount=value: x * amount, "")
            UiTools.standard_button(root, i + 3, 0, images[key.lower()], None, 32, 32,
                                    command=lambda amount=value: power_submenu(handle_item_input(amount)))
        else:
            OperationLabel(root, i + 3, 0, entrySpinBox, lambda x, amount=value: x * amount, "")
            UiTools.standard_button(root, i + 3, 0, images[key.lower()], None, 32, 32, command=lambda name=key, amount=value: materials_window(name, handle_item_input(amount)))
    OperationLabel(root, len(unit_math(name)) + 3, 0, entrySpinBox, lambda x, rate=unit_math(name)["Output"]: x * rate, "Factories\nrequired")
    UiTools.back_button(root, len(unit_math(name)) + 4, 4, lambda: units_selection())

def materials_window(name, rate=0.0):
    UiTools.clear_full()
    producers = find_producers(name)
    UiTools.standard_label(root, 0, 0, 1, name, None)
    UiTools.standard_label(root, 0, 1, 1, None, images[name.lower()])
    UiTools.standard_label(root, 1, 0, 1, "How much to\nmake/sec?" if rate != 0 else "How much to\nmake/sec:", None)

    # Always create the spinbox, but only show it when rate == 0
    entrySpinBox = FancySpinbox(root, 1, 1, minVal=0.0, maxVal=10000.0, width=6)
    entrySpinBox.grid(row=1, column=1, padx=5, pady=5)
    entrySpinBox.set_value(rate)

    # Create label to display fixed rate if provided
    rateLabel = tk.Label(root, text=round(rate, 2), bg='#202020', fg="#ffffff")

    if rate:
        rateLabel.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    UiTools.hline(2)

    # Producer Selection UI
    selectionFrame = tk.Frame(root, bg="#202020")
    selectionFrame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    for i, producer in enumerate(producers):
        producer = get_block(producer)
        productionRate = None
        if "recipes" in producer:
            for recipe in producer["recipes"]:
                if name in recipe["Outputs"].keys() and name in liquids:
                    productionRate = recipe["Outputs"][name]
                    break
                elif name in recipe["Outputs"].keys():
                    productionRate = recipe["Outputs"][name] / recipe["Time"]
                    break
            OperationLabel(selectionFrame, i, 1, entrySpinBox, lambda x, value=productionRate: x / value, "Required:")
        else:
            producerAmount = tk.Frame(selectionFrame, bg="#202020")
            producerAmount.grid(row=i, column=1, columnspan=2, padx=5, pady=5)
            drillSpeed = 60 / (producer["base_time"] * (producer["A"] + producer["B"] * drillables[name]))
            OperationLabel(producerAmount, 0, 0, entrySpinBox, lambda x, value=drillSpeed: math.ceil(x / value), "Tiles to cover:")
            OperationLabel(producerAmount, 1, 0, entrySpinBox, lambda x, value=producer["size"] ** 2 * drillSpeed: x / value,
                           "Minimum number of drills:")

        UiTools.standard_button(selectionFrame, i, 0, images[reformat_entry(producer["name"])], "", 32, 32, lambda name=producer['name'],
                                rate=productionRate if productionRate else producer["size"] ** 2 * drillSpeed:
                                process_submenu(name, entrySpinBox.get_value() / rate))

    UiTools.back_button(root, 4 + len(producers), 4, lambda: materials_selection())

def process_submenu(name, count):
    UiTools.clear_full()
    block = get_block(name)
    UiTools.standard_label(root, 0, 0, 1, name, None)
    UiTools.standard_label(root, 0, 1, 1, None, images[reformat_entry(name)])
    UiTools.standard_label(root, 1, 0, 1, 'Count', None)
    UiTools.standard_label(root, 1, 1, 1, f'{count:.2f}', None)
    UiTools.hline(2)
    if block.get('type') == 'Drill':
        if block.get('power'):
            UiTools.standard_label(root, 3, 1, 1, f"{block.get('power') * count:.2f}", None)
            UiTools.standard_button(root, 3, 0, images['power'], None, 32, 32, command=lambda:
                                                                                                         power_submenu(count * block.get('power')))
        else:
            UiTools.standard_label(root, 3, 0, 2, "No inputs required,\nexcept possibly coolant.", None)
    else:
        inputs = {}
        for recipe in block.get('recipes', []):
            for key, value in recipe.get('Input', {}).items():
                if key in inputs:
                    pass
                else:
                    inputs[key] = value / recipe['Time'] if key.lower() != 'power' else value
        inputsFrame = tk.Frame(root, bg="#202020")
        inputsFrame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        if inputs != {}:
            for i, (key, value) in enumerate(inputs.items()):
                if key == 'Power':
                    UiTools.standard_label(inputsFrame, i, 1, 1, f"{value * count:.2f}", None)
                    UiTools.standard_button(inputsFrame, i, 0, images[key.lower()], None, 32, 32, lambda rate=count * value:
                    power_submenu(rate))
                else:
                    UiTools.standard_label(inputsFrame, i, 1, 1, f"{value * count:.2f}", None)
                    UiTools.standard_button(inputsFrame, i, 0, images[key.lower()], None, 32, 32, lambda name=key, rate=count * value: materials_window(name, rate))
        else:
            UiTools.standard_label(root, 3, 0, 2, "No inputs required.", None)
    UiTools.back_button(root, 4, 4, lambda: materials_selection())

def power_submenu(amount):
    UiTools.clear_full()
    UiTools.standard_label(root, 0, 0, 1, 'Power', None)
    UiTools.standard_label(root, 0, 1, 1, None, images['power'])
    UiTools.standard_label(root, 1, 0, 1, 'How much\nto produce:', None)
    UiTools.standard_label(root, 1, 1, 1, f'{amount:.0f}', None)
    UiTools.hline(2)
    row = 3
    for key, value in blocks['other'].items():
        if any(word in key for word in ['reactor', 'generator']):
            if isinstance(value.recipes, list):
                for i in value.recipes:
                    count = round(amount / i['Outputs']['Power'], 6)
                    UiTools.standard_button(root, row, 0, images[reformat_entry(key + " " + list(i['Input'].keys())[0])], None, 32, 32,
                                            lambda rate=count * list(i['Input'].values())[0] / i['Time'], item=list(i['Input'].keys())[0]:
                                            materials_window(item, rate))
                    UiTools.standard_label(root, row, 1, 1, f"{count:.2f}", None)
                    row += 1
            elif isinstance(value.recipes, dict):
                count = round(amount / value.recipes['Outputs']['Power'], 6)
                UiTools.standard_button(root, row, 0, images[reformat_entry(key)], None, 32, 32,
                                        lambda rate=count * list(value.recipes['Input'].values())[0] / value.recipes['Time'],
                                               item=list(value.recipes['Input'].keys())[0]: materials_window(item, rate))
                UiTools.standard_label(root, row, 1, 1, f"{count:.2f}", None)
                row += 1
    UiTools.back_button(root, row, 4, lambda: materials_selection())

#%% Image manipulation (the bit that makes the UI even prettier: with pictures)
# Images are imported as tk.PhotoImages in images, then paired with functions and text for the main menu selection levels of the UI.

images = {
    "left toggle": tk.PhotoImage(file="Images/left.png"),
    "right toggle": tk.PhotoImage(file="Images/right.png"),
    "water toggle": tk.PhotoImage(file="Images/Items/water-toggle.png"),
    "cryofluid toggle": tk.PhotoImage(file="Images/Items/cryofluid-toggle.png"),
    "water != coolant": tk.PhotoImage(file="Images/Items/no-water.png"),
    "cryofluid != coolant": tk.PhotoImage(file="Images/Items/no-cryofluid.png"),
    "bullets": tk.PhotoImage(file="Images/turret.png"),
    "power": tk.PhotoImage(file="Images/power.png"),
    "unitsIcon": tk.PhotoImage(file="Images/units.png"),
    "items": tk.PhotoImage(file="Images/production.png"),
    "back": tk.PhotoImage(file="Images/Back.png"),
    "duo": tk.PhotoImage(file="Images/Blocks/Turrets/Duo.png"),
    "scatter": tk.PhotoImage(file="Images/Blocks/Turrets/Scatter.png"),
    "scorch": tk.PhotoImage(file="Images/Blocks/Turrets/Scorch.png"),
    "hail": tk.PhotoImage(file="Images/Blocks/Turrets/Hail.png"),
    "wave": tk.PhotoImage(file="Images/Blocks/Turrets/Wave.png"),
    "lancer": tk.PhotoImage(file="Images/Blocks/Turrets/Lancer.png"),
    "arc": tk.PhotoImage(file="Images/Blocks/Turrets/Arc.png"),
    "parallax": tk.PhotoImage(file="Images/Blocks/Turrets/Parallax.png"),
    "swarmer": tk.PhotoImage(file="Images/Blocks/Turrets/Swarmer.png"),
    "salvo": tk.PhotoImage(file="Images/Blocks/Turrets/Salvo.png"),
    "segment": tk.PhotoImage(file="Images/Blocks/Turrets/Segment.png"),
    "tsunami": tk.PhotoImage(file="Images/Blocks/Turrets/Tsunami.png"),
    "fuse": tk.PhotoImage(file="Images/Blocks/Turrets/Fuse.png"),
    "ripple": tk.PhotoImage(file="Images/Blocks/Turrets/Ripple.png"),
    "cyclone": tk.PhotoImage(file="Images/Blocks/Turrets/Cyclone.png"),
    "foreshadow": tk.PhotoImage(file="Images/Blocks/Turrets/Foreshadow.png"),
    "spectre": tk.PhotoImage(file="Images/Blocks/Turrets/Spectre.png"),
    "meltdown": tk.PhotoImage(file="Images/Blocks/Turrets/Meltdown.png"),
    "combustionGenerator": tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator.png"),
    "combustionGeneratorCoal": tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator_Coal.png"),
    "combustionGeneratorPyratite": tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator_Pyratite.png"),
    "combustionGeneratorBlastCompound": tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator_Blast.png"),
    "combustionGeneratorSporePod": tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator_Spore.png"),
    "steamGenerator": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator.png"),
    "steamGeneratorCoal": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator_Coal.png"),
    "steamGeneratorPyratite": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator_Pyratite.png"),
    "steamGeneratorBlastCompound": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator_Blast.png"),
    "steamGeneratorSporePod": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator_Spore.png"),
    "differentialGenerator": tk.PhotoImage(file="Images/Blocks/Generators/Differential_Generator.png"),
    "rtgGenerator": tk.PhotoImage(file="Images/Blocks/Generators/RTG_Generator.png"),
    "rtgGeneratorThorium": tk.PhotoImage(file="Images/Blocks/Generators/RTG_Generator_Thorium.png"),
    "rtgGeneratorPhaseFabric": tk.PhotoImage(file="Images/Blocks/Generators/RTG_Generator_Phase.png"),
    "thoriumReactor": tk.PhotoImage(file="Images/Blocks/Generators/Thorium_Reactor.png"),
    "impactReactor": tk.PhotoImage(file="Images/Blocks/Generators/Impact_Reactor.png"),
    "dagger": tk.PhotoImage(file="Images/Units/Dagger.png"),
    "mace": tk.PhotoImage(file="Images/Units/Mace.png"),
    "fortress": tk.PhotoImage(file="Images/Units/Fortress.png"),
    "scepter": tk.PhotoImage(file="Images/Units/Scepter.png"),
    "reign": tk.PhotoImage(file="Images/Units/Reign.png"),
    "nova": tk.PhotoImage(file="Images/Units/Nova.png"),
    "pulsar": tk.PhotoImage(file="Images/Units/Pulsar.png"),
    "quasar": tk.PhotoImage(file="Images/Units/Quasar.png"),
    "vela": tk.PhotoImage(file="Images/Units/Vela.png"),
    "corvus": tk.PhotoImage(file="Images/Units/Corvus.png"),
    "crawler": tk.PhotoImage(file="Images/Units/Crawler.png"),
    "atrax": tk.PhotoImage(file="Images/Units/Atrax.png"),
    "spiroct": tk.PhotoImage(file="Images/Units/Spiroct.png"),
    "arkyid": tk.PhotoImage(file="Images/Units/Arkyid.png"),
    "toxopid": tk.PhotoImage(file="Images/Units/Toxopid.png"),
    "flare": tk.PhotoImage(file="Images/Units/Flare.png"),
    "horizon": tk.PhotoImage(file="Images/Units/Horizon.png"),
    "zenith": tk.PhotoImage(file="Images/Units/Zenith.png"),
    "antumbra": tk.PhotoImage(file="Images/Units/Antumbra.png"),
    "eclipse": tk.PhotoImage(file="Images/Units/Eclipse.png"),
    "mono": tk.PhotoImage(file="Images/Units/Mono.png"),
    "poly": tk.PhotoImage(file="Images/Units/Poly.png"),
    "mega": tk.PhotoImage(file="Images/Units/Mega.png"),
    "quad": tk.PhotoImage(file="Images/Units/Quad.png"),
    "oct": tk.PhotoImage(file="Images/Units/Oct.png"),
    "risso": tk.PhotoImage(file="Images/Units/Risso.png"),
    "minke": tk.PhotoImage(file="Images/Units/Minke.png"),
    "bryde": tk.PhotoImage(file="Images/Units/Bryde.png"),
    "sei": tk.PhotoImage(file="Images/Units/Sei.png"),
    "omura": tk.PhotoImage(file="Images/Units/Omura.png"),
    "retusa": tk.PhotoImage(file="Images/Units/Retusa.png"),
    "oxynoe": tk.PhotoImage(file="Images/Units/Oxynoe.png"),
    "cyerce": tk.PhotoImage(file="Images/Units/Cyerce.png"),
    "aegires": tk.PhotoImage(file="Images/Units/Aegires.png"),
    "navanax": tk.PhotoImage(file="Images/Units/Navanax.png"),
    "copper": tk.PhotoImage(file="Images/Items/item-copper.png"),
    "lead": tk.PhotoImage(file="Images/Items/item-lead.png"),
    "metaglass": tk.PhotoImage(file="Images/Items/item-metaglass.png"),
    "graphite": tk.PhotoImage(file="Images/Items/item-graphite.png"),
    "sand": tk.PhotoImage(file="Images/Items/item-sand.png"),
    "coal": tk.PhotoImage(file="Images/Items/item-coal.png"),
    "titanium": tk.PhotoImage(file="Images/Items/item-titanium.png"),
    "thorium": tk.PhotoImage(file="Images/Items/item-thorium.png"),
    "scrap": tk.PhotoImage(file="Images/Items/item-scrap.png"),
    "silicon": tk.PhotoImage(file="Images/Items/item-silicon.png"),
    "plastanium": tk.PhotoImage(file="Images/Items/item-plastanium.png"),
    "phase fabric": tk.PhotoImage(file="Images/Items/item-phase-fabric.png"),
    "surge alloy": tk.PhotoImage(file="Images/Items/item-surge-alloy.png"),
    "spore pod": tk.PhotoImage(file="Images/Items/item-spore-pod.png"),
    "blast compound": tk.PhotoImage(file="Images/Items/item-blast-compound.png"),
    "pyratite": tk.PhotoImage(file="Images/Items/item-pyratite.png"),
    "water": tk.PhotoImage(file="Images/Items/liquid-water.png"),
    "cryofluid": tk.PhotoImage(file="Images/Items/liquid-cryofluid.png"),
    "slag": tk.PhotoImage(file="Images/Items/liquid-slag.png"),
    "oil": tk.PhotoImage(file="Images/Items/liquid-oil.png"),
    "airblastDrill": tk.PhotoImage(file="Images/Blocks/Extractors/Airblast_Drill.png"),
    "impulsePump": tk.PhotoImage(file="Images/Blocks/Extractors/Impulse_Pump.png"),
    "laserDrill": tk.PhotoImage(file="Images/Blocks/Extractors/Laser_Drill.png"),
    "mechanicalDrill": tk.PhotoImage(file="Images/Blocks/Extractors/Mechanical_Drill.png"),
    "mechanicalPump": tk.PhotoImage(file="Images/Blocks/Extractors/Mechanical_Pump.png"),
    "pneumaticDrill": tk.PhotoImage(file="Images/Blocks/Extractors/Pneumatic_Drill.png"),
    "rotaryPump": tk.PhotoImage(file="Images/Blocks/Extractors/Rotary_Pump.png"),
    "waterExtractor": tk.PhotoImage(file="Images/Blocks/Extractors/Water_Extractor.png"),
    "blastMixer": tk.PhotoImage(file="Images/Blocks/Item production/Blast_Mixer.png"),
    "coalCentrifuge": tk.PhotoImage(file="Images/Blocks/Item production/Coal_Centrifuge.png"),
    "cryofluidMixer": tk.PhotoImage(file="Images/Blocks/Item production/Cryofluid_Mixer.png"),
    "cultivator": tk.PhotoImage(file="Images/Blocks/Item production/Cultivator.png"),
    "disassembler": tk.PhotoImage(file="Images/Blocks/Item production/Disassembler.png"),
    "graphitePress": tk.PhotoImage(file="Images/Blocks/Item production/Graphite_Press.png"),
    "kiln": tk.PhotoImage(file="Images/Blocks/Item production/Kiln.png"),
    "melter": tk.PhotoImage(file="Images/Blocks/Item production/Melter.png"),
    "multiPress": tk.PhotoImage(file="Images/Blocks/Item production/Multi-Press.png"),
    "oilExtractor": tk.PhotoImage(file="Images/Blocks/Item production/Oil_Extractor.png"),
    "phaseWeaver": tk.PhotoImage(file="Images/Blocks/Item production/Phase_Weaver.png"),
    "plastaniumCompressor": tk.PhotoImage(file="Images/Blocks/Item production/Plastanium_Compressor.png"),
    "pulverizer": tk.PhotoImage(file="Images/Blocks/Item production/Pulverizer.png"),
    "pyratiteMixer": tk.PhotoImage(file="Images/Blocks/Item production/Pyratite_Mixer.png"),
    "separator": tk.PhotoImage(file="Images/Blocks/Item production/Separator.png"),
    "siliconCrucible": tk.PhotoImage(file="Images/Blocks/Item production/Silicon_Crucible.png"),
    "siliconSmelter": tk.PhotoImage(file="Images/Blocks/Item production/Silicon_Smelter.png"),
    "sporePress": tk.PhotoImage(file="Images/Blocks/Item production/Spore_Press.png"),
    "surgeSmelter": tk.PhotoImage(file="Images/Blocks/Item production/Surge_Smelter.png")
}

mainMenuButtons = [
    (images["bullets"], "Turrets", turret_selection),
    (images["power"], "Power", power_selection),
    (images["unitsIcon"], "Units", units_selection),
    (images["items"], "Resources", materials_selection),
]
turretsMenuButtons = [
    ("Duo", images["duo"], lambda: turrets_window("Duo")),
    ("Scatter", images["scatter"], lambda: turrets_window("Scatter")),
    ("Scorch", images["scorch"], lambda: turrets_window("Scorch")),
    ("Hail", images["hail"], lambda: turrets_window("Hail")),
    ("Wave", images["wave"], lambda: turrets_window("Wave")),
    ("Lancer", images["lancer"], lambda: turrets_window("Lancer")),
    ("Arc", images["arc"], lambda: turrets_window("Arc")),
    ("Parallax", images["parallax"], lambda: turrets_window("Parallax")),
    ("Swarmer", images["swarmer"], lambda: turrets_window("Swarmer")),
    ("Salvo", images["salvo"], lambda: turrets_window("Salvo")),
    ("Segment", images["segment"], lambda: turrets_window("Segment")),
    ("Tsunami", images["tsunami"], lambda: turrets_window("Tsunami")),
    ("Fuse", images["fuse"], lambda: turrets_window("Fuse")),
    ("Ripple", images["ripple"], lambda: turrets_window("Ripple")),
    ("Cyclone", images["cyclone"], lambda: turrets_window("Cyclone")),
    ("Foreshadow", images["foreshadow"], lambda: turrets_window("Foreshadow")),
    ("Spectre", images["spectre"], lambda: turrets_window("Spectre")),
    ("Meltdown", images["meltdown"], lambda: turrets_window("Meltdown"))
]
powerMenuButtons = [
    ("Combustion generator", images["combustionGenerator"]),
    ("Steam generator", images["steamGenerator"]),
    ("Differential generator", images["differentialGenerator"]),
    ("RTG generator", images["rtgGenerator"]),
    ("Thorium reactor", images["thoriumReactor"]),
    ("Impact reactor", images["impactReactor"]),
]
unitsMenuButtons = [
    ("Dagger", images["dagger"], lambda: units_window("Dagger")),
    ("Mace", images["mace"], lambda: units_window("Mace")),
    ("Fortress", images["fortress"], lambda: units_window("Fortress")),
    ("Scepter", images["scepter"], lambda: units_window("Scepter")),
    ("Reign", images["reign"], lambda: units_window("Reign")),
    ("Nova", images["nova"], lambda: units_window("Nova")),
    ("Pulsar", images["pulsar"], lambda: units_window("Pulsar")),
    ("Quasar", images["quasar"], lambda: units_window("Quasar")),
    ("Vela", images["vela"], lambda: units_window("Vela")),
    ("Corvus", images["corvus"], lambda: units_window("Corvus")),
    ("Crawler", images["crawler"], lambda: units_window("Crawler")),
    ("Atrax", images["atrax"], lambda: units_window("Atrax")),
    ("Spiroct", images["spiroct"], lambda: units_window("Spiroct")),
    ("Arkyid", images["arkyid"], lambda: units_window("Arkyid")),
    ("Toxopid", images["toxopid"], lambda: units_window("Toxopid")),
    ("Flare", images["flare"], lambda: units_window("Flare")),
    ("Horizon", images["horizon"], lambda: units_window("Horizon")),
    ("Zenith", images["zenith"], lambda: units_window("Zenith")),
    ("Antumbra", images["antumbra"], lambda: units_window("Antumbra")),
    ("Eclipse", images["eclipse"], lambda: units_window("Eclipse")),
    ("Mono", images["mono"], lambda: units_window("Mono")),
    ("Poly", images["poly"], lambda: units_window("Poly")),
    ("Mega", images["mega"], lambda: units_window("Mega")),
    ("Quad", images["quad"], lambda: units_window("Quad")),
    ("Oct", images["oct"], lambda: units_window("Oct")),
    ("Risso", images["risso"], lambda: units_window("Risso")),
    ("Minke", images["minke"], lambda: units_window("Minke")),
    ("Bryde", images["bryde"], lambda: units_window("Bryde")),
    ("Sei", images["sei"], lambda: units_window("Sei")),
    ("Omura", images["omura"], lambda: units_window("Omura")),
    ("Retusa", images["retusa"], lambda: units_window("Retusa")),
    ("Oxynoe", images["oxynoe"], lambda: units_window("Oxynoe")),
    ("Cyerce", images["cyerce"], lambda: units_window("Cyerce")),
    ("Aegires", images["aegires"], lambda: units_window("Aegires")),
    ("Navanax", images["navanax"], lambda: units_window("Navanax")),
]
materialsMenuButtons = [
    ("Copper", images["copper"], lambda: materials_window("Copper")),
    ("Lead", images["lead"], lambda: materials_window("Lead")),
    ("Glass", images["metaglass"], lambda: materials_window("Metaglass")),
    ("Graphite", images["graphite"], lambda: materials_window("Graphite")),
    ("Sand", images["sand"], lambda: materials_window("Sand")),
    ("Coal", images["coal"], lambda: materials_window("Coal")),
    ("Titanium", images["titanium"], lambda: materials_window("Titanium")),
    ("Thorium", images["thorium"], lambda: materials_window("Thorium")),
    ("Scrap", images["scrap"], lambda: materials_window("Scrap")),
    ("Silicon", images["silicon"], lambda: materials_window("Silicon")),
    ("Plastanium", images["plastanium"], lambda: materials_window("Plastanium")),
    ("Phase", images["phase fabric"], lambda: materials_window("Phase fabric")),
    ("Surge", images["surge alloy"], lambda: materials_window("Surge alloy")),
    ("Spore Pods", images["spore pod"], lambda: materials_window("Spore pod")),
    ("Blast", images["blast compound"], lambda: materials_window("Blast compound")),
    ("Pyratite", images["pyratite"], lambda: materials_window("Pyratite")),
    ("Water", images["water"], lambda: materials_window("Water")),
    ("Cryofluid", images["cryofluid"], lambda: materials_window("Cryofluid")),
    ("Slag", images["slag"], lambda: materials_window("Slag")),
    ("Oil", images["oil"], lambda: materials_window("Oil")),
]

if __name__ == "__main__":
    main_menu()
    root.mainloop()
