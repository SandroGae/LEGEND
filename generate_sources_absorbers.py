import pyg4ometry
import math
#import Extrapolation

reg = pyg4ometry.geant4.Registry()

# Function to create a cylindrical solid
def create_cylinder(name, inner_radius, outer_radius, height, start_angle, end_angle, registry):
    """Create a cylindrical solid with specified parameters."""
    return pyg4ometry.geant4.solid.Tubs(name, inner_radius, outer_radius, height, start_angle, end_angle, registry=registry)

# Function to create a logical volume
def create_logical_volume(solid, material, name, registry):
    """Create a logical volume from a given solid."""
    return pyg4ometry.geant4.LogicalVolume(solid, material, name, registry)

# Function to create and place a physical volume
def place_cylinder(lv, name, mother_volume, position, registry, rotation=[0, 0, 0]):
    """Place a cylinder in the simulation world."""
    return pyg4ometry.geant4.PhysicalVolume(rotation, position, lv, name=name, motherVolume=mother_volume, registry=registry)


# Parameters for height of absorbers
height_1 = -300 # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_2 = -200 # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_3 = -100 # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_4 = 0 # TODO: choose height which is defined as the centre of the absorber at the moment (z position)

inner_radius_source = 1.9  # mm
source_radius = 2  # mm
source_height = 4  # mm
absorber_radius = 16
absorber_height = 37.5
material = "G4_Galactic"

# Create the world volume
world_solid = pyg4ometry.geant4.solid.Box("WorldBox", 1000, 1000, 1000, reg)
world_lv = create_logical_volume(world_solid, material, "WorldLV", reg)

# Create cylinders
sourceLV = create_logical_volume(create_cylinder("Sample LV", inner_radius_source, source_radius, source_height, 0, 2 * math.pi, reg), material, "SourceLV", reg)
absorberLV = create_logical_volume(create_cylinder("Absorber LV", 0, absorber_radius, absorber_height, 0, 2 * math.pi, reg), material, "AbsorberLV", reg)

# Define the z position for the lowest sample and the x,y position as well according to l200
base_position1 = [121.472, -96.277,height_1 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position2 = [-120.9667, -96.9126,height_2 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position3 = [-121.304, 96.48977,height_3 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position4 = [121.135, 96.70,height_4 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]

# Place cylinders in the world where the middle of the absorber is set to be 0
for i in range(1, 5, 1):
    place_cylinder(sourceLV, f'Lowest Source PV{i}', world_lv, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2]], reg)
    place_cylinder(sourceLV, f'Second Lowest Source PV{i}', world_lv, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 100], reg)
    place_cylinder(sourceLV, f'Second Highest Source PV{i}', world_lv, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 200], reg)
    place_cylinder(sourceLV, f'Highest Source PV{i}', world_lv, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 300], reg)
    place_cylinder(absorberLV, f'Absorber PV{i}', world_lv, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'height_{i}']], reg)


# Set the world as the root volume
reg.setWorld("WorldLV")

# Write the geometries to a GDML file
visual = pyg4ometry.gdml.Writer()
visual.addDetector(reg)
visual.write('geometry_Source.gdml')