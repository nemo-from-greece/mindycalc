from Logic import get_block, get_unit, find_producers, find_upgrade_path
import tkinter as tk
from tkinter import font
#%% TODO, V2:
# Make logic
# Implement recursive production finding
# Make buttons for ^^^
#%% TODO, V3:
# Add Erekir

#%% UI creation
root = tk.Tk()
root.title("Serpulo Ratio Calculator")
root.configure(background="#202020")
custom_font = font.Font(family="fontello", size=11)
root.option_add("*Font", custom_font)

prompt = tk.Label(root, text="What do you want to make?")
prompt.grid(row=0, column=0, columnspan=5)
prompt.configure(background="#202020", foreground="#ffffff")
line = tk.Frame(root, height=3, background="#808080")
line.grid(row=1, columnspan=5, sticky="ew")

# Simple routines used at all levels of the UI
class UiTools:
    def __init__(self, uiToolsRoot, main_menu_command):
        self.root = uiToolsRoot
        self.main_menu_command = main_menu_command

    @staticmethod
    def clear_grid():
        """Clears widgets from the grid except the first two rows."""
        for widget in root.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.destroy()

    @staticmethod
    def clear_full():
        """Clears widgets from the grid except the first two rows."""
        for widget in root.grid_slaves():
            widget.destroy()

    @staticmethod
    def on_enter(e):
        """Handles mouse enter event for button highlighting."""
        e.widget['highlightbackground'] = "#fcd47c"

    @staticmethod
    def on_leave(e):
        """Handles mouse leave event for button highlighting."""
        e.widget['highlightbackground'] = "#202020"

    def create_grid(self, button_texts, rows, cols, empty_cells=None):
        """Creates a grid of buttons with specified empty cells and a back button."""
        empty_cells = empty_cells or []
        frame = tk.Frame(self.root, background="#202020")
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
        back_button = tk.Button(root, image=back, width=32, height=32,
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

# Main selection menu for Serpulo
def main_menu():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(background="#202020")
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
def turretsSelection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(background="#202020")
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
def powerSelection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(background="#202020")
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
def unitsSelection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(background="#202020")
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
def materialsSelection():
    UiTools.clear_grid()
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
    frame.configure(background="#202020")
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

def turretsWindow(name):
    UiTools.clear_full()
    block = get_block(name)
    if block:
        # Extract relevant information
        text = (
            f"Name: {block['name']}\n"
            f"Reload Time: {block.get('reloadTime', 'N/A')}\n"
            f"Burst: {block.get('burst', 'N/A')}\n"
            f"Ammo Types: {block.get('ammoTypes', 'N/A')}\n"
            f"Coolant: {block.get('coolant', 'N/A')}\n"
            f"Ammo Use: {block.get('ammoUse', 'N/A')}\n"
            f"Power: {block.get('power', 'N/A')}\n"
            f"Liquid Ammo: {block.get('liquidAmmo', 'N/A')}"
        )
        turret = tk.Label(root, text=text)
        turret.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        turret.configure(background="#202020", fg="#ffffff")
    else:
        # Handle case where block is not found
        error_label = tk.Label(root, text=f"Turret '{name}' not found.")
        error_label.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        error_label.configure(background="#202020", fg="#ffffff")
    UiTools.back_button(root,3,4,lambda: turretsSelection())

def powerWindow(name):
    UiTools.clear_full()
    block = get_block(name)
    if block:
        if isinstance(block['recipes'], dict):  # Check if it's a dictionary
            text = (
                f"Name: {block['name']}\n"
                f"Inputs: {block['recipes']['Input']}\n"
                f"Outputs: {block['recipes']['Outputs']}\n"
                f"Production time: {block['recipes']['Time']} s"
            )
        else:
            text = (
                f"Name: {block['name']}\n"
                f"Inputs: {block['recipes'][0]['Input']}\n"
                f"Outputs: {block['recipes'][0]['Outputs']}\n"
                f"Production time: {block['recipes'][0]['Time']} s"
            )
        powerElement = tk.Label(root, text=text)
        powerElement.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        powerElement.configure(background="#202020", fg="#ffffff")
    UiTools.back_button(root,3,4,lambda: powerSelection())

def unitsWindow(name):
    UiTools.clear_full()
    unit = get_unit(name)
    print(unit)
    if unit:
        print(find_upgrade_path(name))
        # Extract relevant information
        text = (
            f"Name: {unit['name']}\n"
            f"Tier: {unit['tier']}\n"
            f"Type: {unit['type']}\n"
            f"Colour: {unit['colour']}\n"
            f"Upgraded from {find_upgrade_path(name)['upgrades']['previous_unit']} in {find_upgrade_path(name)['upgrades']['reconstructor']}"
        )
        unit_label = tk.Label(root, text=text)
        unit_label.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        unit_label.configure(background="#202020", fg="#ffffff")
    else:
        # Handle case where unit is not found
        error_label = tk.Label(root, text=f"Unit '{name}' not found.")
        error_label.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        error_label.configure(background="#202020", fg="#ffffff")
    UiTools.back_button(root,3,4,lambda: unitsSelection())

def materialsWindow(name):
    UiTools.clear_full()
    producers = find_producers(name)
    if producers:
        # Display each producer
        for i, producer in enumerate(producers):
            producer_label = tk.Label(root, text=f"Producer {i+1}: {producer}")
            producer_label.grid(row=2+i, column=0, columnspan=4, padx=5, pady=5)
            producer_label.configure(background="#202020", fg="#ffffff")
        UiTools.back_button(root,3+len(producers),4,lambda: materialsSelection())
    else:
        # Handle case where no producers are found
        error_label = tk.Label(root, text=f"No producers found for '{name}'.")
        error_label.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        error_label.configure(background="#202020", fg="#ffffff")
        UiTools.back_button(root,3,4,lambda: materialsSelection())

#%% Image manipulation - Explanation
# Apart from the last two lines, this entire section is importing images into variables tkinter can work with, then pairing each of the images with
# some text and a command, for use above as buttons.

#%% Image manipulation (the bit that makes the UI even prettier: with pictures)
bullets = tk.PhotoImage(file="Images/turret.png")
power = tk.PhotoImage(file="Images/power.png")
unitsIcon = tk.PhotoImage(file="Images/units.png")
items = tk.PhotoImage(file="Images/production.png")
back = tk.PhotoImage(file="Images/Back.png")

mainMenuButtons = [
    (bullets, "Turrets", turretsSelection),
    (power, "Power", powerSelection),
    (unitsIcon, "Units", unitsSelection),
    (items, "Resources", materialsSelection),
]

duo = tk.PhotoImage(file="Images/Blocks/Turrets/Duo.png")
scatter = tk.PhotoImage(file="Images/Blocks/Turrets/Scatter.png")
scorch = tk.PhotoImage(file="Images/Blocks/Turrets/Scorch.png")
hail = tk.PhotoImage(file="Images/Blocks/Turrets/Hail.png")
wave = tk.PhotoImage(file="Images/Blocks/Turrets/Wave.png")
lancer = tk.PhotoImage(file="Images/Blocks/Turrets/Lancer.png")
arc = tk.PhotoImage(file="Images/Blocks/Turrets/Arc.png")
parallax = tk.PhotoImage(file="Images/Blocks/Turrets/Parallax.png")
swarmer = tk.PhotoImage(file="Images/Blocks/Turrets/Swarmer.png")
salvo = tk.PhotoImage(file="Images/Blocks/Turrets/Salvo.png")
segment = tk.PhotoImage(file="Images/Blocks/Turrets/Segment.png")
tsunami = tk.PhotoImage(file="Images/Blocks/Turrets/Tsunami.png")
fuse = tk.PhotoImage(file="Images/Blocks/Turrets/Fuse.png")
ripple = tk.PhotoImage(file="Images/Blocks/Turrets/Ripple.png")
cyclone = tk.PhotoImage(file="Images/Blocks/Turrets/Cyclone.png")
foreshadow = tk.PhotoImage(file="Images/Blocks/Turrets/Foreshadow.png")
spectre = tk.PhotoImage(file="Images/Blocks/Turrets/Spectre.png")
meltdown = tk.PhotoImage(file="Images/Blocks/Turrets/Meltdown.png")

turretsMenuButtons = [
    ("Duo", duo, lambda: turretsWindow("Duo")),
    ("Scatter", scatter, lambda: turretsWindow("Scatter")),
    ("Scorch", scorch, lambda: turretsWindow("Scorch")),
    ("Hail", hail, lambda: turretsWindow("Hail")),
    ("Wave", wave, lambda: turretsWindow("Wave")),
    ("Lancer", lancer, lambda: turretsWindow("Lancer")),
    ("Arc", arc, lambda: turretsWindow("Arc")),
    ("Parallax", parallax, lambda: turretsWindow("Parallax")),
    ("Swarmer", swarmer, lambda: turretsWindow("Swarmer")),
    ("Salvo", salvo, lambda: turretsWindow("Salvo")),
    ("Segment", segment, lambda: turretsWindow("Segment")),
    ("Tsunami", tsunami, lambda: turretsWindow("Tsunami")),
    ("Fuse", fuse, lambda: turretsWindow("Fuse")),
    ("Ripple", ripple, lambda: turretsWindow("Ripple")),
    ("Cyclone", cyclone, lambda: turretsWindow("Cyclone")),
    ("Foreshadow", foreshadow, lambda: turretsWindow("Foreshadow")),
    ("Spectre", spectre, lambda: turretsWindow("Spectre")),
    ("Meltdown", meltdown, lambda: turretsWindow("Meltdown"))
]

combustion_generator = tk.PhotoImage(file="Images/Blocks/Generators/Combustion_Generator.png")
steam_generator = tk.PhotoImage(file="Images/Blocks/Generators/Steam_Generator.png")
differential_generator = tk.PhotoImage(file="Images/Blocks/Generators/Differential_Generator.png")
RTG_generator = tk.PhotoImage(file="Images/Blocks/Generators/RTG_Generator.png")
thorium_reactor = tk.PhotoImage(file="Images/Blocks/Generators/Thorium_Reactor.png")
impact_reactor = tk.PhotoImage(file="Images/Blocks/Generators/Impact_Reactor.png")

powerMenuButtons = [
    ("Combustion generator", combustion_generator, lambda: powerWindow("Combustion generator")),
    ("Steam generator", steam_generator, lambda: powerWindow("Steam generator")),
    ("Differential generator", differential_generator, lambda: powerWindow("Differential generator")),
    ("RTG generator", RTG_generator, lambda: powerWindow("RTG generator")),
    ("Thorium reactor", thorium_reactor, lambda: powerWindow("Thorium reactor")),
    ("Impact reactor", impact_reactor, lambda: powerWindow("Impact reactor")),
]

dagger = tk.PhotoImage(file="Images/Units/Dagger.png")
mace = tk.PhotoImage(file="Images/Units/Mace.png")
fortress = tk.PhotoImage(file="Images/Units/Fortress.png")
scepter = tk.PhotoImage(file="Images/Units/Scepter.png")
reign = tk.PhotoImage(file="Images/Units/Reign.png")
nova = tk.PhotoImage(file="Images/Units/Nova.png")
pulsar = tk.PhotoImage(file="Images/Units/Pulsar.png")
quasar = tk.PhotoImage(file="Images/Units/Quasar.png")
vela = tk.PhotoImage(file="Images/Units/Vela.png")
corvus = tk.PhotoImage(file="Images/Units/Corvus.png")
crawler = tk.PhotoImage(file="Images/Units/Crawler.png")
atrax = tk.PhotoImage(file="Images/Units/Atrax.png")
spiroct = tk.PhotoImage(file="Images/Units/Spiroct.png")
arkyid = tk.PhotoImage(file="Images/Units/Arkyid.png")
toxopid = tk.PhotoImage(file="Images/Units/Toxopid.png")
flare = tk.PhotoImage(file="Images/Units/Flare.png")
horizon = tk.PhotoImage(file="Images/Units/Horizon.png")
zenith = tk.PhotoImage(file="Images/Units/Zenith.png")
antumbra = tk.PhotoImage(file="Images/Units/Antumbra.png")
eclipse = tk.PhotoImage(file="Images/Units/Eclipse.png")
mono = tk.PhotoImage(file="Images/Units/Mono.png")
poly = tk.PhotoImage(file="Images/Units/Poly.png")
mega = tk.PhotoImage(file="Images/Units/Mega.png")
quad = tk.PhotoImage(file="Images/Units/Quad.png")
oct = tk.PhotoImage(file="Images/Units/Oct.png")
risso = tk.PhotoImage(file="Images/Units/Risso.png")
minke = tk.PhotoImage(file="Images/Units/Minke.png")
bryde = tk.PhotoImage(file="Images/Units/Bryde.png")
sei = tk.PhotoImage(file="Images/Units/Sei.png")
omura = tk.PhotoImage(file="Images/Units/Omura.png")
retusa = tk.PhotoImage(file="Images/Units/Retusa.png")
oxynoe = tk.PhotoImage(file="Images/Units/Oxynoe.png")
cyerce = tk.PhotoImage(file="Images/Units/Cyerce.png")
aegires = tk.PhotoImage(file="Images/Units/Aegires.png")
navanax = tk.PhotoImage(file="Images/Units/Navanax.png")

unitsMenuButtons = [
    ("Dagger", dagger, lambda: unitsWindow("Dagger")),
    ("Mace", mace, lambda: unitsWindow("Mace")),
    ("Fortress", fortress, lambda: unitsWindow("Fortress")),
    ("Scepter", scepter, lambda: unitsWindow("Scepter")),
    ("Reign", reign, lambda: unitsWindow("Reign")),
    ("Nova", nova, lambda: unitsWindow("Nova")),
    ("Pulsar", pulsar, lambda: unitsWindow("Pulsar")),
    ("Quasar", quasar, lambda: unitsWindow("Quasar")),
    ("Vela", vela, lambda: unitsWindow("Vela")),
    ("Corvus", corvus, lambda: unitsWindow("Corvus")),
    ("Crawler", crawler, lambda: unitsWindow("Crawler")),
    ("Atrax", atrax, lambda: unitsWindow("Atrax")),
    ("Spiroct", spiroct, lambda: unitsWindow("Spiroct")),
    ("Arkyid", arkyid, lambda: unitsWindow("Arkyid")),
    ("Toxopid", toxopid, lambda: unitsWindow("Toxopid")),
    ("Flare", flare, lambda: unitsWindow("Flare")),
    ("Horizon", horizon, lambda: unitsWindow("Horizon")),
    ("Zenith", zenith, lambda: unitsWindow("Zenith")),
    ("Antumbra", antumbra, lambda: unitsWindow("Antumbra")),
    ("Eclipse", eclipse, lambda: unitsWindow("Eclipse")),
    ("Mono", mono, lambda: unitsWindow("Mono")),
    ("Poly", poly, lambda: unitsWindow("Poly")),
    ("Mega", mega, lambda: unitsWindow("Mega")),
    ("Quad", quad, lambda: unitsWindow("Quad")),
    ("Oct", oct, lambda: unitsWindow("Oct")),
    ("Risso", risso, lambda: unitsWindow("Risso")),
    ("Minke", minke, lambda: unitsWindow("Minke")),
    ("Bryde", bryde, lambda: unitsWindow("Bryde")),
    ("Sei", sei, lambda: unitsWindow("Sei")),
    ("Omura", omura, lambda: unitsWindow("Omura")),
    ("Retusa", retusa, lambda: unitsWindow("Retusa")),
    ("Oxynoe", oct, lambda: unitsWindow("Oxynoe")),
    ("Cyerce", cyerce, lambda: unitsWindow("Cyerce")),
    ("Aegires", aegires, lambda: unitsWindow("Aegires")),
    ("Navanax", navanax, lambda: unitsWindow("Navanax")),
]

copper = tk.PhotoImage(file="Images/Items/item-copper.png")
lead = tk.PhotoImage(file="Images/Items/item-lead.png")
glass = tk.PhotoImage(file="Images/Items/item-metaglass.png")
graphite = tk.PhotoImage(file="Images/Items/item-graphite.png")
sand = tk.PhotoImage(file="Images/Items/item-sand.png")
coal = tk.PhotoImage(file="Images/Items/item-coal.png")
titanium = tk.PhotoImage(file="Images/Items/item-titanium.png")
thorium = tk.PhotoImage(file="Images/Items/item-thorium.png")
scrap = tk.PhotoImage(file="Images/Items/item-scrap.png")
silicon = tk.PhotoImage(file="Images/Items/item-silicon.png")
plast = tk.PhotoImage(file="Images/Items/item-plastanium.png")
phase = tk.PhotoImage(file="Images/Items/item-phase-fabric.png")
surge = tk.PhotoImage(file="Images/Items/item-surge-alloy.png")
pods = tk.PhotoImage(file="Images/Items/item-spore-pod.png")
blast = tk.PhotoImage(file="Images/Items/item-blast-compound.png")
pyra = tk.PhotoImage(file="Images/Items/item-pyratite.png")
water = tk.PhotoImage(file="Images/Items/liquid-water.png")
cryo = tk.PhotoImage(file="Images/Items/liquid-cryofluid.png")
slag = tk.PhotoImage(file="Images/Items/liquid-slag.png")
oil = tk.PhotoImage(file="Images/Items/liquid-oil.png")

materialsMenuButtons = [
    ("Copper", copper, lambda: materialsWindow("Copper")),
    ("Lead", lead, lambda: materialsWindow("Lead")),
    ("Glass", glass, lambda: materialsWindow("Metaglass")),
    ("Graphite", graphite, lambda: materialsWindow("Graphite")),
    ("Sand", sand, lambda: materialsWindow("Sand")),
    ("Coal", coal, lambda: materialsWindow("Coal")),
    ("Titanium", titanium, lambda: materialsWindow("Titanium")),
    ("Thorium", thorium, lambda: materialsWindow("Thorium")),
    ("Scrap", scrap, lambda: materialsWindow("Scrap")),
    ("Silicon", silicon, lambda: materialsWindow("Silicon")),
    ("Plastanium", plast, lambda: materialsWindow("Plastanium")),
    ("Phase", phase, lambda: materialsWindow("Phase fabric")),
    ("Surge", surge, lambda: materialsWindow("Surge alloy")),
    ("Spore Pods", pods, lambda: materialsWindow("Spore pod")),
    ("Blast", blast, lambda: materialsWindow("Blast compound")),
    ("Pyratite", pyra, lambda: materialsWindow("Pyratite")),
    ("Water", water, lambda: materialsWindow("Water")),
    ("Cryofluid", cryo, lambda: materialsWindow("Cryofluid")),
    ("Slag", slag, lambda: materialsWindow("Slag")),
    ("Oil", oil, lambda: materialsWindow("Oil")),
]

airblastDrill = tk.PhotoImage(file="Images/Blocks/Extractors/Airblast_Drill.png")
impulsePump = tk.PhotoImage(file="Images/Blocks/Extractors/Impulse_Pump.png")
laserDrill = tk.PhotoImage(file="Images/Blocks/Extractors/Laser_Drill.png")
mechanicalDrill = tk.PhotoImage(file="Images/Blocks/Extractors/Mechanical_Drill.png")
mechanicalPump = tk.PhotoImage(file="Images/Blocks/Extractors/Mechanical_Pump.png")
pneumaticDrill = tk.PhotoImage(file="Images/Blocks/Extractors/Pneumatic_Drill.png")
rotaryPump = tk.PhotoImage(file="Images/Blocks/Extractors/Rotary_Pump.png")
waterExtractor = tk.PhotoImage(file="Images/Blocks/Extractors/Water_Extractor.png")

blastMixer = tk.PhotoImage(file="Images/Blocks/Item production/Blast_Mixer.png")
coalCentrifuge = tk.PhotoImage(file="Images/Blocks/Item production/Coal_Centrifuge.png")
cryoMixer = tk.PhotoImage(file="Images/Blocks/Item production/Cryofluid_Mixer.png")
cultivator = tk.PhotoImage(file="Images/Blocks/Item production/Cultivator.png")
disassembler = tk.PhotoImage(file="Images/Blocks/Item production/Disassembler.png")
graphitePress = tk.PhotoImage(file="Images/Blocks/Item production/Graphite_Press.png")
kiln = tk.PhotoImage(file="Images/Blocks/Item production/Kiln.png")
melter = tk.PhotoImage(file="Images/Blocks/Item production/Melter.png")
multiPress = tk.PhotoImage(file="Images/Blocks/Item production/Multi-Press.png")
oilExtractor = tk.PhotoImage(file="Images/Blocks/Item production/Oil_Extractor.png")
phaseWeaver = tk.PhotoImage(file="Images/Blocks/Item production/Phase_Weaver.png")
plastCompressor = tk.PhotoImage(file="Images/Blocks/Item production/Plastanium_Compressor.png")
pulverizer = tk.PhotoImage(file="Images/Blocks/Item production/Pulverizer.png")
pyraMixer = tk.PhotoImage(file="Images/Blocks/Item production/Pyratite_Mixer.png")
separator = tk.PhotoImage(file="Images/Blocks/Item production/Separator.png")
siliconCrucible = tk.PhotoImage(file="Images/Blocks/Item production/Silicon_Crucible.png")
siliconSmelter = tk.PhotoImage(file="Images/Blocks/Item production/Silicon_Smelter.png")
sporePress = tk.PhotoImage(file="Images/Blocks/Item production/Spore_Press.png")
surgeSmelter = tk.PhotoImage(file="Images/Blocks/Item production/Surge_Smelter.png")

main_menu()
root.mainloop()
