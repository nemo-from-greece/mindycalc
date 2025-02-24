from Ratios import units, blocks, drillables, Turret, Drill, Production, Factory, Reconstructor

def get_block(name, default=None):
	# Iterate through each category in the blocks dictionary
	for category in blocks.values():
		# Iterate through each block in the category
		for blockName, blockData in category.items():

			# Check if the block name matches
			if blockName == name:
				# Determine the block's class and return relevant information
				if isinstance(blockData, Turret):
					return {
						"type": "Turret",
						"name": blockData.name,
						"reloadTime": blockData.reloadTime,
						"burst": blockData.burst,
						"ammoTypes": blockData.ammoTypes,
						"coolant": blockData.coolant,
						"ammoUse": blockData.ammoUse,
						"power": blockData.power,
						"liquidAmmo": blockData.liquidAmmo,
					}
				elif isinstance(blockData, Drill):
					return {
						"type": "Drill",
						"name": blockData.name,
						"tier": blockData.tier,
						"base_time": blockData.base_time,
						"A": blockData.A,
						"B": blockData.B,
						"boost": blockData.boost,
					}
				elif isinstance(blockData, Production):
					return {
						"type": "Production",
						"name": blockData.name,
						"recipes": blockData.recipes,
					}
				elif isinstance(blockData, Factory):
					return {
						"type": "Factory",
						"name": blockData.name,
						"power": blockData.power,
						"unit_recipes": blockData.unit_recipes,
					}
				elif isinstance(blockData, Reconstructor):
					return {
						"type": "Reconstructor",
						"name": blockData.name,
						"tier": blockData.tier,
						"power": blockData.power,
						"cost": blockData.cost,
						"time": blockData.time,
					}
				else:
					# Default case for generic Block
					return {
						"type": "Block",
						"name": blockData.name,
					}

	# Return the default value if the block is not found
	return default

def get_unit(name):
	# Iterate through the units dictionary
	for unitName, unitData in units.items():
		# Check if the unit name matches
		if unitName == name:
			# Return the unit data as a dictionary
			unit_info = {
				"name": unitData.name,
				"tier": unitData.tier,
				"type": unitData.unit_type,
				"colour": unitData.colour,  # Include the colour attribute
			}
			# Add unit_type only for tier 1 units
			if unitData.tier == 1:
				unit_info["unit_type"] = unitData.unit_type
			return unit_info

def find_upgrade_path(unitName):
	# Get the unit data
	unitData = units.get(unitName)

	# Initialize the upgrade path
	upgrade_path = {
		"target_unit": unitName,
		"tier": unitData.tier,
		"colour": unitData.colour,
		"unit_type": unitData.unit_type
	}

	# If the unit is tier 1, it is produced by a factory
	if unitData.tier == 1:
		# Determine the factory based on the unit_type
		if unitData.unit_type == "Ground":
			upgrade_path["produced_by"] = "Ground factory"
		elif unitData.unit_type == "Air":
			upgrade_path["produced_by"] = "Air factory"
		elif unitData.unit_type == "Naval":
			upgrade_path["produced_by"] = "Naval factory"
		return upgrade_path

	# If the unit is tier 2 or higher, find the reconstructor and the previous tier unit
	if unitData.tier > 1:
		# Find the reconstructor for the current tier
		reconstructor = next(
			(name for name, data in blocks.get("reconstructors", {}).items()
			 if isinstance(data, Reconstructor) and data.tier == unitData.tier),
			None
		)

		# Find the unit in the previous tier with the same colour and unit_type
		previous_tier = unitData.tier - 1
		previous_unit = next(
			(name for name, data in units.items()
			 if data.tier == previous_tier
			 and data.colour == unitData.colour
			 and data.unit_type == unitData.unit_type),  # Ensure unit_type matches
			None
		)

		# Add the reconstructor and previous unit to the upgrade path
		upgrade_path["upgrades"] = {
			"tier": unitData.tier,
			"reconstructor": reconstructor,
			"previous_unit": previous_unit,
		}

	return upgrade_path

def find_producers(material):
	producers = []

	# Check if the material is drillable
	if material in drillables:
		hardness = drillables[material]
		# Search for drills that can mine the material
		for category in blocks.values():
			for block_name, block_data in category.items():
				if isinstance(block_data, Drill):
					# Check if the drill's tier is sufficient for the material's hardness
					if block_data.tier >= hardness:
						producers.append(block_name)

	# Search blocks (e.g., Production blocks)
	for category in blocks.values():
		for block_name, block_data in category.items():
			if isinstance(block_data, Production):
				if isinstance(block_data.recipes, dict):
					if material in block_data.recipes.get("Outputs", {}):
						producers.append(block_name)
				elif isinstance(block_data.recipes, list):
					for recipe in block_data.recipes:
						if isinstance(recipe, dict) and material in recipe.get("Outputs", {}):
							producers.append(block_name)
							break

	return producers
