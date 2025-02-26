from Logic import get_block, find_producers, unit_math
from Ratios import units
import tkinter as tk
from tkinter import font
#%% TODO, V2:
# Make logic
#%% TODO, V3:
# Implement recursive production finding
# Make buttons for ^^^
#%% TODO, V4:
# Add Erekir

#%% UI creation
root = tk.Tk()
root.title("Serpulo Ratio Calculator")
root.configure(bg="#202020")
custom_font = font.Font(family="fontello", size=11) # In theory, should make tkinter use mindustry font.
root.option_add("*Font", custom_font)

# Simple routines used at all levels of the UI
class UiTools:
    def __init__(self, uiToolsRoot, main_menu_command):
        self.root = uiToolsRoot
        self.main_menu_command = main_menu_command

    @staticmethod
    def clear_grid():
        UiTools.clear_full()
        prompt = tk.Label(root, text="What do you want to make?")
        prompt.grid(row=0, column=0, columnspan=5)
        prompt.configure(bg="#202020", fg="#ffffff")
        line = tk.Frame(root, height=3, bg="#808080")
        line.grid(row=1, columnspan=5, sticky="ew")

    @staticmethod
    def clear_full():
        # Clears widgets from the grid except the first two rows.
        for widget in root.grid_slaves():
            widget.destroy()

    @staticmethod
    def on_enter(e):
        # Handles mouse enter event for button highlighting.
        e.widget['highlightbackground'] = "#fcd47c"

    @staticmethod
    def on_leave(e):
        # Handles mouse leave event for button highlighting.
        e.widget['highlightbackground'] = "#202020"

    def create_grid(self, button_texts, rows, cols, empty_cells=None):
        # Creates a grid of buttons with specified empty cells and a back button.
        empty_cells = empty_cells or []
        frame = tk.Frame(self.root, bg="#202020")
        frame.grid(row=2, column=0, columnspan=cols, padx=5, pady=5)

        # Create grid buttons
        for r in range(rows):
            for c in range(cols):
                if (r, c) in empty_cells:
                    continue
                btn = tk.Button(
                    frame,
                    text=button_texts[r][c],
                    width=10, height=2,
                    fg="#ffffff", bg="#404040",
                    activebackground="#606060",
                    borderwidth=1, relief="raised"
                )
                btn.grid(row=r, column=c, padx=5, pady=5)

        # Back button configuration
        self.back_button(self.root,rows, cols, self.main_menu_command)

    @staticmethod
    def back_button(root, row, cols, command):
        back_button = tk.Button(root, image=images["back"], width=32, height=32,
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

class BaseComponents:
    # A reusable base class for UI components using grid layout.
    def __init__(self, parent):
        self.parent = parent  # Store the parent widget

    def grid(self, row, column, **kwargs):
        # Helper method to place all child widgets in a grid layout.
        for widget in vars(self).values():
            if isinstance(widget, tk.Widget):
                widget.grid(row=row, column=column, **kwargs)

class FancySpinbox:
    # A Spinbox that enforces value limits but does not perform operations itself.
    def __init__(self, parent, row, column, minVal=0.0, maxVal=100.0, width=5):
        self.parent = parent
        self.minVal = minVal
        self.maxVal = maxVal
        self.width = width

        # StringVar to hold the Spinbox value
        self.spinboxVar = tk.StringVar(value=str(self.minVal))

        # Create the Spinbox
        self.spinbox = tk.Spinbox(
            parent, from_=self.minVal, to=self.maxVal, textvariable=self.spinboxVar, width=width,
            format="%.2f")
        self.spinbox.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
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
        self.staticLabel.configure(bg="#202020", fg="#ffffff",)

        # Create label for dynamic result
        self.resultLabel = tk.Label(parent, text=f"{self.operation(self.spinbox.get_value()):.2f}")
        self.resultLabel.grid(row=row, column=column + 1, padx=5, pady=5)
        self.resultLabel.configure(bg="#202020", fg="#ffffff",)

        # Update the dynamic result when spinbox value changes
        self.spinbox.spinboxVar.trace_add("write", self.update_label)

    def update_label(self, *args):
        # Updates the label with the dynamic result based on the spinbox value.
        self.resultLabel.config(text=f"{self.operation(self.spinbox.get_value()):.2f}")

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
# Main selection menu for Serpulo
def main_menu():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (image, text, command) in enumerate(mainMenuButtons):
        button = tk.Button(
            frame,
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
            height=50,
            width=90,
            command=command)
        button.grid(row=0, column=idx, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)
# Serpulo turret selection menu
def turret_selection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(turretsMenuButtons):
        button = tk.Button(
            frame,
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
            height=50,
            width=100,
            command=command)
        button.grid(row=idx//4, column=idx%4, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)
    UiTools.back_button(root,3,4,lambda: main_menu())
# Serpulo power selection menu
def power_selection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(powerMenuButtons):
        word1,word2 = text.split()
        text = f"{word1}\n{word2}"
        button = tk.Button(
            frame,
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
            height=65,
            width=90,
            command=command)
        button.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)
    UiTools.back_button(root,3,4,lambda: main_menu())
# Serpulo unit selection menu
def units_selection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(unitsMenuButtons):
        button = tk.Button(
            frame,
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
            height=50,
            width=90,
            command=command)
        button.grid(row=idx % 5, column=idx // 5, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)
    UiTools.back_button(root,3,4,lambda: main_menu())
# Serpulo material selection menu
def materials_selection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(bg="#202020")
    for idx, (text, image, command) in enumerate(materialsMenuButtons):
        button = tk.Button(
            frame,
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
            height=50,
            width=95,
            command=command)
        button.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
        button.bind("<Enter>", UiTools.on_enter)
        button.bind("<Leave>", UiTools.on_leave)
    UiTools.back_button(root, 3, 4, lambda: main_menu())

def turrets_window(name):
    UiTools.clear_full()
    block = get_block(name)
    # Extract relevant information
    text = (
        f"Name: {block['name']}\n"
        f"Reload Time: {block.get('reloadTime', 'N/A')}\n"
        f"Burst: {block.get('burst', 'N/A')}\n"
        f"Ammo Types: {block.get('ammoTypes', 'N/A')}\n"
        f"Coolant: {block.get('coolant', 'N/A')}\n"
        f"Ammo Use: {block.get('ammoUse', 'N/A')}\n"
        f"Power use while firing/reloading: {block.get('power', 'N/A')}\n"
        f"Liquid Ammo: {block.get('liquidAmmo', 'N/A')}"
    )
    turret = tk.Label(root, text=text)
    turret.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    turret.configure(bg="#202020", fg="#ffffff")
    UiTools.back_button(root, 3, 4, lambda: turret_selection())

def power_window(name):
    UiTools.clear_full()
    block = get_block(name)
    if isinstance(block['recipes'], dict):  # Check if it's a dictionary
        text = (
            f"Name: {block['name']}\n"
            f"Inputs: {block['recipes']['Input']}\n"
            f"Outputs: {block['recipes']['Outputs']}\n"
            f"Production time: {round(block['recipes']['Time'],2)} s"
        )
    else:
        text = (
            f"Name: {block['name']}\n"
            f"Inputs: {block['recipes'][0]['Input']}\n"
            f"Outputs: {block['recipes'][0]['Outputs']}\n"
            f"Production time: {round(block['recipes'][0]['Time'],2)} s"
        )
    powerElement = tk.Label(root, text=text)
    powerElement.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    powerElement.configure(bg="#202020", fg="#ffffff")
    UiTools.back_button(root, 3, 4, lambda: power_selection())

def units_window(name):
    UiTools.clear_full()
    unit = units.get(name)
    windowTitle = tk.Label(root, text=unit.name)
    windowTitle.grid(row=0, column=0, padx=5, pady=5)
    windowTitle.configure(bg="#202020", fg="#ffffff")
    windowImage = tk.Label(root, image=images[unit.name.lower()])
    windowImage.grid(row=0, column=1, padx=5, pady=5)
    windowImage.configure(bg="#202020")
    entryPrompt = tk.Label(root, text="How many to\nproduce/min:")
    entryPrompt.grid(row=1, column=0, padx=5, pady=5)
    entryPrompt.configure(bg="#202020", fg="#ffffff")
    entrySpinBox = FancySpinbox(root,1,1,1,1000)
    hline = tk.Frame(root, height=3, bg="#404040")
    hline.grid(row=2, column=0, columnspan=5, sticky="ew")
    for i, (key, value) in enumerate(unit_math(name).items()):
        if key == "Output":
            break
        OperationLabel(root, i+3, 0, entrySpinBox, lambda x, value=value: x * value, key+"/sec")
        pass
    OperationLabel(root, i+3, 0, entrySpinBox, lambda x, value=unit_math(name)["Output"]: x * value, "Factories\nrequired")
    UiTools.back_button(root, i + 4, 4, lambda: units_selection())

def materials_window(name):
    UiTools.clear_full()
    producers = find_producers(name)
    windowTitle = tk.Label(root, text=name)
    windowTitle.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    windowTitle.configure(bg="#202020", fg="#ffffff")
    entryPrompt = tk.Label(root, text="How much to make/sec:")
    entryPrompt.grid(row=3, column=0, padx=5, pady=5)
    entryPrompt.configure(bg="#202020", fg="#ffffff")
    entrySpinBox = tk.Spinbox(root, from_=0, to=100000, increment=1, width=6)
    entrySpinBox.grid(row=3, column=1, padx=5, pady=5)

    for i, producer in enumerate(producers):
        producerLabel = tk.Label(root, text=f"{producer}")
        producerLabel.grid(row=4+i, column=0, padx=5, pady=5)
        producerLabel.configure(bg="#202020", fg="#ffffff")
        producerButton = tk.Button(root,
                                   image=images[reformat_entry(producer)],
                                   fg="#ffffff",
                                   compound="top",
                                   borderwidth=0,
                                   highlightthickness=2,
                                   highlightbackground="#202020",
                                   activeforeground="#ffffff",
                                   highlightcolor="#fcd47c",
                                   bg="#202020",
                                   activebackground="#202020",
                                   height=32,
                                   width=32)
        producerButton.grid(row=4+i, column=1, padx=5, pady=5)
        producerButton.bind("<Enter>", UiTools.on_enter)
        producerButton.bind("<Leave>", UiTools.on_leave)
    UiTools.back_button(root, 5 + len(producers), 4, lambda: materials_selection())

#%% Image manipulation - Explanation
# Apart from the last two lines, this entire section is importing images into variables tkinter can work with, then pairing each of the images with
# some text and a command, for use above as buttons.

#%% Image manipulation (the bit that makes the UI even prettier: with pictures)

images = {
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
    "steamGenerator": tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator.png"),
    "differentialGenerator": tk.PhotoImage(file="Images/Blocks/Generators/Differential_Generator.png"),
    "rtgGenerator": tk.PhotoImage(file="Images/Blocks/Generators/RTG_Generator.png"),
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
    "glass": tk.PhotoImage(file="Images/Items/item-metaglass.png"),
    "graphite": tk.PhotoImage(file="Images/Items/item-graphite.png"),
    "sand": tk.PhotoImage(file="Images/Items/item-sand.png"),
    "coal": tk.PhotoImage(file="Images/Items/item-coal.png"),
    "titanium": tk.PhotoImage(file="Images/Items/item-titanium.png"),
    "thorium": tk.PhotoImage(file="Images/Items/item-thorium.png"),
    "scrap": tk.PhotoImage(file="Images/Items/item-scrap.png"),
    "silicon": tk.PhotoImage(file="Images/Items/item-silicon.png"),
    "plast": tk.PhotoImage(file="Images/Items/item-plastanium.png"),
    "phase": tk.PhotoImage(file="Images/Items/item-phase-fabric.png"),
    "surge": tk.PhotoImage(file="Images/Items/item-surge-alloy.png"),
    "pods": tk.PhotoImage(file="Images/Items/item-spore-pod.png"),
    "blast": tk.PhotoImage(file="Images/Items/item-blast-compound.png"),
    "pyra": tk.PhotoImage(file="Images/Items/item-pyratite.png"),
    "water": tk.PhotoImage(file="Images/Items/liquid-water.png"),
    "cryo": tk.PhotoImage(file="Images/Items/liquid-cryofluid.png"),
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
    ("Combustion generator", images["combustionGenerator"], lambda: power_window("Combustion generator")),
    ("Steam generator", images["steamGenerator"], lambda: power_window("Steam generator")),
    ("Differential generator", images["differentialGenerator"], lambda: power_window("Differential generator")),
    ("RTG generator", images["rtgGenerator"], lambda: power_window("RTG generator")),
    ("Thorium reactor", images["thoriumReactor"], lambda: power_window("Thorium reactor")),
    ("Impact reactor", images["impactReactor"], lambda: power_window("Impact reactor")),
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
    ("Glass", images["glass"], lambda: materials_window("Metaglass")),
    ("Graphite", images["graphite"], lambda: materials_window("Graphite")),
    ("Sand", images["sand"], lambda: materials_window("Sand")),
    ("Coal", images["coal"], lambda: materials_window("Coal")),
    ("Titanium", images["titanium"], lambda: materials_window("Titanium")),
    ("Thorium", images["thorium"], lambda: materials_window("Thorium")),
    ("Scrap", images["scrap"], lambda: materials_window("Scrap")),
    ("Silicon", images["silicon"], lambda: materials_window("Silicon")),
    ("Plastanium", images["plast"], lambda: materials_window("Plastanium")),
    ("Phase", images["phase"], lambda: materials_window("Phase fabric")),
    ("Surge", images["surge"], lambda: materials_window("Surge alloy")),
    ("Spore Pods", images["pods"], lambda: materials_window("Spore pod")),
    ("Blast", images["blast"], lambda: materials_window("Blast compound")),
    ("Pyratite", images["pyra"], lambda: materials_window("Pyratite")),
    ("Water", images["water"], lambda: materials_window("Water")),
    ("Cryofluid", images["cryo"], lambda: materials_window("Cryofluid")),
    ("Slag", images["slag"], lambda: materials_window("Slag")),
    ("Oil", images["oil"], lambda: materials_window("Oil")),
]

main_menu()
root.mainloop()
