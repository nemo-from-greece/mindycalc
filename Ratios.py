class Block:
    def __init__(self, name):
        self.name = name

class Turret(Block):
    def __init__(self, name, reloadTime=0, burst=1, ammoTypes=None, coolant=None, ammoUse=1, power=0, liquidAmmo=None):
        super().__init__(name)
        self.reloadTime = reloadTime  # How long between shots (frames, 60 fps). Int.
        self.burst = burst  # How many bullets fired at once. Int.
        self.ammoTypes = ammoTypes if ammoTypes else {}  # Different ammo types and their reload time multiplier, ammo cost multiplier (how much
        # ammo per item inputted). Dict{Str:List[Float,Int]}.
        self.coolant = coolant if coolant else {}  # Effects of coolants on fire rate and consumption rate. Dict:{Str:List[Float,Float]}.
        self.ammoUse = ammoUse  # How much ammo used per shot. Int.
        self.power = power # Power consumption, while firing/reloading (/sec)
        self.liquidAmmo = liquidAmmo if liquidAmmo else []  # Liquid ammo types and consumption rate. List:[Str]. Fire rate is 60*burst/reloadTime.

class Drill(Block):
    def __init__(self, name, tier, base_time, A, B, boost=None):
        super().__init__(name)
        self.tier = tier  # Drill tier
        self.base_time = base_time  # Base mining time (in frames)
        self.A = A  # Constant A
        self.B = B  # Constant B
        self.boost = boost if boost else {}  # Water consumption for boosting (/sec)

    def mining_speed(self, hardness):
        return 60 / (self.base_time * self.A + self.B * hardness)

class Production(Block):
    def __init__(self, name, recipes = None):
        super().__init__(name)
        self.recipes = recipes if recipes else [{"Input": {}, "Outputs": {}, "Time": 1}] # List:[Dict:{Str:Int}, Dict:{Str:Int}, Float]. Stores the
        # input and output resources. Resources are for one craft, and production time to determine rates.

class Factory(Block):
    def __init__(self, name, power, unit_recipes=None):
        super().__init__(name)
        self.power = power  # Power required per second
        self.unit_recipes = unit_recipes if unit_recipes else {}  # Dict of units and their input costs (total items per recipe, liquids remain per second)

class Reconstructor(Block):
    def __init__(self, name, tier, power, cost, buildTime):
        super().__init__(name)
        self.tier = tier  # The tier this reconstructor upgrades to
        self.power = power  # Power required per second
        self.cost = cost # Production cost
        self.time = buildTime # Time for reconstruction (sec)

class Unit:
    def __init__(self, name, tier, unit_type, colour):
        self.name = name
        self.tier = tier
        self.unit_type = unit_type
        self.colour = colour

blocks = {
    "turrets": {
        "Duo": Turret("Duo",
                      20,
                      1,
                      {"Copper": [1.0, 2], "Graphite": [0.6, 4], "Silicon": [1.5, 5]},
                      {"Water": [6.0, 1.2], "Cryofluid": [6.0, 1.45]}),
        "Scatter": Turret("Scatter",
                          18,
                          2,
                          {"Scrap": [0.5, 5], "Lead": [1.0, 4], "Metaglass": [0.8, 5]},
                          {"Water": [12.0, 1.4], "Cryofluid": [12.0, 1.9]}),
        "Scorch": Turret("Scorch",
                         6,
                         1,
                         {"Coal": [1.0, 3], "Pyratite": [1.0, 6]},
                         {"Water": [6.0, 1.06], "Cryofluid": [6.0, 1.135]}),
        "Hail": Turret("Hail",
                       60,
                       1,
                       {"Graphite": [1.0, 2], "Silicon": [1.2, 3], "Pyratite": [1.0, 4]},
                       {"Water": [6.0, 1.2], "Cryofluid": [6.0, 1.45]}),
        "Wave": Turret("Wave",
                       3,
                       1,
                       liquidAmmo=["Water", "Cryofluid", "Oil", "Slag"]),
        "Lancer": Turret("Lancer",
                         80,
                         1,
                         coolant={"Water": [12.0, 1.4], "Cryofluid": [12.0, 1.9]},
                         power=360),
        "Arc": Turret("Arc",
                      35,
                      1,
                      coolant={"Water": [6.0, 1.2], "Cryofluid": [6.0, 1.45]},
                      power=198),
        "Parallax": Turret("Parallax",
                           power=198),
        "Swarmer": Turret("Swarmer",
                          30,
                          4,
                          {"Blast compound": [1.0, 5], "Pyratite": [1.0, 5], "Surge alloy": [1.0, 4]},
                          {"Water": [18.0, 1.6], "Cryofluid": [18.0, 2.35]}),
        "Salvo": Turret("Salvo",
                        31,
                        4,
                        {"Copper": [1.0, 2], "Graphite": [0.6, 4], "Pyratite": [1.0, 5], "Silicon": [1.5, 5], "Thorium": [1.0, 4]},
                        {"Water": [12.0, 1.4], "Cryofluid": [12.0, 1.9]}),
        "Segment": Turret("Segment",
                          8,
                          1,
                          power=480),
        "Tsunami": Turret("Tsunami",
                          3,
                          2,
                          liquidAmmo=["Water", "Cryofluid", "Oil", "Slag"]),
        "Fuse": Turret("Fuse",
                       35,
                       3,
                       {"Titanium": [1.3, 4], "Thorium": [1.0, 5]},
                       {"Water": [18.0, 1.6], "Cryofluid": [18.0, 2.35]}),
        "Ripple": Turret("Ripple",
                         60,
                         4,
                         {"Graphite": [1.0, 2], "Silicon": [1.2, 3], "Pyratite": [1.0, 4], "Blast compound": [1.0, 4], "Plastanium": [1.0, 2]},
                         {"Water": [18.0, 1.6], "Cryofluid": [18.0, 2.35]}),
        "Cyclone": Turret("Cyclone",
                          8,
                          1,
                          {"Metaglass": [0.8, 2], "Blast compound": [1.0, 5], "Plastanium": [1.0, 4], "Surge alloy": [1.0, 5]},
                          {"Water": [18.0, 1.6], "Cryofluid": [18.0, 2.35]}),
        "Foreshadow": Turret("Foreshadow",
                             200,
                             1,
                             {"Surge Alloy": [1.0, 1]},
                             {"Water": [60.0, 1.16], "Cryofluid": [60.0, 1.36]},
                             5,
                             600),
        "Spectre": Turret("Spectre",
                          7,
                          1,
                          {"Graphite": [1.7, 4], "Thorium": [1.0, 2], "Pyratite": [1.0, 3]},
                          {"Water": [60.0, 1.2], "Cryofluid": [60.0, 1.45]}),
        "Meltdown": Turret("Meltdown",
                           90,
                           coolant={"Water": [30.0, 1.0], "Cryofluid": [30.0, 2.25]},
                           power=1020),
    },
    "drills": {
        "Mechanical drill": Drill("Mechanical drill", tier=2, base_time=600, A=1.000, B=0.088, boost={"Water": 3}),
        "Pneumatic drill": Drill("Pneumatic drill", tier=3, base_time=400, A=1.000, B=0.132, boost={"Water": 3.6}),
        "Laser drill": Drill("Laser drill", tier=4, base_time=240, A=1.168, B=0.208, boost={"Water": 4.8}),
        "Airblast drill": Drill("Airblast drill", tier=5, base_time=240, A=1.168, B=0.208, boost={"Water": 6}),
    },
    "unit factories": {
        "Ground factory": Factory("Ground factory", power=72, unit_recipes={
            "Dagger": {
                "Input": {"Lead": 10, "Silicon": 10},
                "time": 15
            },
            "Nova": {
                "Input": {"Lead": 20, "Silicon": 30, "Titanium": 20},
                "time": 40
            },
            "Crawler": {
                "Input": {"Coal": 10, "Silicon": 8},
                "time": 10
            }
        }),
        "Air factory": Factory("Air factory", power=72, unit_recipes={
            "Flare": {
                "Input": {"Silicon": 15},
                "time": 15
            },
            "Mono": {
                "Input": {"Lead": 15, "Silicon": 30},
                "time": 35
            }
        }),
        "Naval factory": Factory("Naval factory", power=72, unit_recipes={
            "Risso": {
                "Input": {"Silicon": 20, "Metaglass": 35},
                "time": 45
            },
            "Retusa": {
                "Input": {"Silicon": 15, "Metaglass": 25, "Titanium": 20},
                "time": 50
            }
        })
    },
    "reconstructors": {
        "Additive reconstructor": Reconstructor("Additive reconstructor", 2, 180, {"Silicon": 40, "Graphite": 40}, 10),
        "Multiplicative reconstructor": Reconstructor("Multiplicative reconstructor", 3, 360,
                                                      {"Silicon": 130, "Titanium": 80, "Metaglass": 40}, 30),
        "Exponential reconstructor": Reconstructor("Exponential reconstructor", 4, 780,
                                                   {"Silicon": 850, "Titanium": 750, "Plastanium": 650, "Cryofluid": 60}, 90),
        "Tetrative reconstructor": Reconstructor("Tetrative reconstructor", 5, 1500,
                                                 {"Silicon": 1000,"Plastanium": 600, "Surge Alloy": 500, "Phase Fabric": 350, "Cryofluid": 180},
                                                 240)
    },
    "other": {
        "Water extractor": Production("Water extractor",
                                      {"Input": {"Power": 90}, "Outputs": {"Water": 6.6}, "Time": 1}),
        "Cultivator": Production("Cultivator",
                                 {"Input": {"Water": 18,"Power": 80}, "Outputs": {"Spore pod": 1}, "Time": 1.66}),
        "Oil extractor": Production("Oil extractor",
                                    {"Input": {"Sand": 1, "Water": 9}, "Outputs": {"Oil": 15}, "Time": 1}),
        "Mechanical pump": Production("Mechanical pump",
                                      [{"Input": {}, "Outputs": {"Water": 7}, "Time": 1},
                                              {"Input": {}, "Outputs": {"Cryofluid": 7}, "Time": 1},
                                              {"Input": {}, "Outputs": {"Slag", 7}, "Time": 1},
                                              {"Input": {}, "Outputs": {"Oil", 7}, "Time": 1}]),
        "Rotary pump": Production("Rotary pump",
                                  [{"Input": {"Power": 18}, "Outputs": {"Water": 48}, "Time": 1},
                                          {"Input": {"Power": 18}, "Outputs": {"Cryofluid": 48}, "Time": 1},
                                          {"Input": {"Power": 18}, "Outputs": {"Slag", 48}, "Time": 1},
                                          {"Input": {"Power": 18}, "Outputs": {"Oil", 48}, "Time": 1}]),
        "Impulse pump": Production("Impulse pump",
                                   [{"Input": {"Power": 78}, "Outputs": {"Water": 118.7}, "Time": 1},
                                           {"Input": {"Power": 78}, "Outputs": {"Cryofluid": 118.7}, "Time": 1},
                                           {"Input": {"Power": 78}, "Outputs": {"Slag", 118.7}, "Time": 1},
                                           {"Input": {"Power": 78}, "Outputs": {"Oil", 118.7}, "Time": 1}]),
        "Combustion generator": Production("Combustion generator",
                                           [{"Input": {"Coal": 1}, "Outputs": {"Power": 60}, "Time": 2},
                                                   {"Input": {"Spore pod": 1}, "Outputs": {"Power": round(60*1.15)}, "Time": 2},
                                                   {"Input": {"Pyratite": 1}, "Outputs": {"Power": round(60*1.4)}, "Time": 2},
                                                   {"Input": {"Blast Compound": 1}, "Outputs": {"Power": round(60*0.4)}, "Time": 2}]),
        "Steam generator": Production("Steam generator",
                                      [{"Input": {"Coal": 1}, "Outputs": {"Power": 330}, "Time": 1.5},
                                              {"Input": {"Spore pod": 1}, "Outputs": {"Power": round(330*1.15,1)}, "Time": 1.5},
                                              {"Input": {"Pyratite": 1}, "Outputs": {"Power": round(330*1.4)}, "Time": 1.5},
                                              {"Input": {"Blast Compound": 1}, "Outputs": {"Power": round(330*0.4)}, "Time": 1.5}]),
        "Differential generator": Production("Differential generator",
                                             {"Input": {"Pyratite": 1, "Cryofluid": 6}, "Outputs": {"Power": 1080}, "Time": 22/6}),
        "RTG generator": Production("RTG generator",
                                    [{"Input": {"Thorium": 1}, "Outputs": {"Power": 270}, "Time": 14},
                                                  {"Input": {"Phase fabric": 1}, "Outputs": {"Power": round(270*0.6)}, "Time": 14}]),
        "Thorium reactor": Production("Thorium reactor",
                                      {"Input": {"Thorium": 1, "Cryofluid": 2.4}, "Outputs": {"Power": 900}, "Time": 6}),
        "Impact reactor": Production("Impact reactor",
                                     {"Input": {"Blast compound": 1, "Cryofluid": 15, "Power": 1500}, "Outputs": {"Power": 7800}, "Time": 13/6}),
        "Graphite press": Production("Graphite press",
                                     {"Input": {"Coal": 2}, "Outputs": {"Graphite": 1}, "Time": 1.5}),
        "Multi press": Production("Multi press",
                                  {"Input": {"Coal": 3, "Water": 6, "Power": 108}, "Outputs": {"Graphite": 2}, "Time": 0.5}),
        "Silicon smelter": Production("Silicon smelter",
                                      {"Input": {"Coal": 1, "Sand": 2, "Power": 30}, "Outputs": {"Silicon": 1}, "Time": 2/3}),
        "Silicon crucible": Production("Silicon crucible",
                                       {"Input": {"Sand": 6, "Coal": 4, "Pyratite": 1, "Power": 240}, "Outputs": {"Silicon": 8}, "Time": 1.5}),
        "Kiln": Production("Kiln",
                           {"Input": {"Sand": 1, "Lead": 1, "Power": 36}, "Outputs": {"Metaglass": 1}, "Time": 0.5}),
        "Plastanium compressor": Production("Plastanium compressor",
                                            {"Input": {"Titanium": 2, "Oil": 15, "Power": 180}, "Outputs": {"Plastanium": 1}, "Time": 1}),
        "Phase weaver": Production("Phase weaver",
                                   {"Input": {"Sand": 10, "Thorium": 4, "Power": 600}, "Outputs": {"Phase fabric": 1}, "Time": 2}),
        "Surge smelter": Production("Surge smelter",
                                    {"Input": {"Copper": 3, "Lead": 4, "Titanium": 2, "Silicon": 3, "Power": 240}, "Outputs": {"Surge alloy": 1},
                                     "Time": 1.25}),
        "Cryofluid mixer": Production("Cryofluid mixer",
                                      {"Input": {"Titanium": 1, "Water": 12, "Power": 60}, "Outputs": {"Cryofluid": 12}, "Time": 0}),
        "Pyratite mixer": Production("Pyratite mixer",
                                     {"Input": {"Sand": 2, "Lead": 2, "Coal": 1, "Power": 12}, "Outputs": {"Pyratite": 1}, "Time": 0}),
        "Blast mixer": Production("Blast mixer",
                                  {"Input": {"Pyratite": 1, "Spore pod": 1, "Power": 24}, "Outputs": {"Blast compound": 1}, "Time": 0}),
        "Melter": Production("Melter",
                             {"Input": {"Scrap": 1, "Power": 60}, "Outputs": {"Slag": 12}, "Time": 0}),
        "Separator": Production("Separator",
                                {"Input": {"Slag": 4.1, "Power": 60}, "Outputs": {"Copper": 0.416, "Lead": 0.25, "Graphite": 0.166, "Titanium": 0.166}, "Time": 0}),
        "Disassembler": Production("Disassembler",
                                   {"Input": {"Slag": 7.2, "Scrap": 1, "Power": 240}, "Outputs": {"Sand": 0.4, "Graphite": 0.2, "Titanium": 0.2, "Thorium": 0.2}, "Time": 0}),
        "Spore press": Production("Spore press",
                                  {"Input": {"Spore pod": 1, "Power": 42}, "Outputs": {"Oil": 18}, "Time": 0}),
        "Pulverizer": Production("Pulverizer",
                                 {"Input": {"Scrap": 1, "Power": 30}, "Outputs": {"Sand": 1}, "Time": 0}),
        "Coal centrifuge": Production("Coal centrifuge",
                                      {"Input": {"Oil": 6, "Power": 42}, "Outputs": {"Coal": 1}, "Time": 0.5})
    }
} # Done

units = {
    "Dagger": Unit("Dagger", 1, "Ground", "Orange"),
    "Mace": Unit("Mace", 2, "Ground", "Orange"),
    "Fortress": Unit("Fortress", 3, "Ground", "Orange"),
    "Scepter": Unit("Scepter", 4, "Ground", "Orange"),
    "Reign": Unit("Reign", 5, "Ground", "Orange"),
    "Nova": Unit("Nova", 1, "Ground", "Green"),
    "Pulsar": Unit("Pulsar", 2, "Ground", "Green"),
    "Quasar": Unit("Quasar", 3, "Ground", "Green"),
    "Vela": Unit("Vela", 4, "Ground", "Green"),
    "Corvus": Unit("Corvus", 5, "Ground", "Green"),
    "Crawler": Unit("Crawler", 1, "Ground", "Purple"),
    "Atrax": Unit("Atrax", 2, "Ground", "Purple"),
    "Spiroct": Unit("Spiroct", 3, "Ground", "Purple"),
    "Arkyid": Unit("Arkyid", 4, "Ground", "Purple"),
    "Toxopid": Unit("Toxopid", 5, "Ground", "Purple"),
    "Flare": Unit("Flare", 1, "Air", "Orange"),
    "Horizon": Unit("Horizon", 2, "Air", "Orange"),
    "Zenith": Unit("Zenith", 3, "Air", "Orange"),
    "Antumbra": Unit("Antumbra", 4, "Air", "Orange"),
    "Eclipse": Unit("Eclipse", 5, "Air", "Orange"),
    "Mono": Unit("Mono", 1, "Air", "Green"),
    "Poly": Unit("Poly", 2, "Air", "Green"),
    "Mega": Unit("Mega", 3, "Air", "Green"),
    "Quad": Unit("Quad", 4, "Air", "Green"),
    "Oct": Unit("Oct", 5, "Air", "Green"),
    "Risso": Unit("Risso", 1, "Naval", "Orange"),
    "Minke": Unit("Minke", 2, "Naval", "Orange"),
    "Bryde": Unit("Bryde", 3, "Naval", "Orange"),
    "Sei": Unit("Sei", 4, "Naval", "Orange"),
    "Omura": Unit("Omura", 5, "Naval", "Orange"),
    "Retusa": Unit("Retusa", 1, "Naval", "Green"),
    "Oxynoe": Unit("Oxynoe", 2, "Naval", "Green"),
    "Cyerce": Unit("Cyerce", 3, "Naval", "Green"),
    "Aegires": Unit("Aegires", 4, "Naval", "Green"),
    "Navanax": Unit("Navanax", 5, "Naval", "Green")
} # Done

drillables = {
    "Copper": 1,
    "Lead": 1,
    "Sand": 0,
    "Scrap": 0,
    "Coal": 2,
    "Titanium": 3,
    "Thorium": 4
} # Material: hardness
