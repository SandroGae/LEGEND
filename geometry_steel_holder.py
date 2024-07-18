# This code produces the geometry for the steel holder correctly

import pyg4ometry
import math

# Initialize the registry
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


# Upper Cylinder (Cylinder_2)
inner_radius2 = 0.0  # mm
outer_radius2 = 2.5  # mm
height2 = 8.6  # mm

# Lower Cylinder (Cylinder_1)
inner_radius1 = 0.0  # mm
outer_radius1 = 3.2  # mm
height1 = 9.0  # mm

# Dimensions for the source (cavity)
source_radius = 2.0  # mm
source_height = 4.0  # mm

material = "G4_Galactic"

# Create the solids for the two cylinders
cylinder2_solid = create_cylinder("Cylinder2", inner_radius2, outer_radius2, height2 / 2, 0, 2 * math.pi, reg)
cylinder1_solid = create_cylinder("Cylinder1", inner_radius1, outer_radius1, height1 / 2, 0, 2 * math.pi, reg)

# Create the solid for the cavity
cavity_solid = create_cylinder("Cavity", 0.0, source_radius, source_height / 2, 0, 2 * math.pi, reg)

# Create logical volumes for the two cylinders and the cavity
cylinder_up_lv = create_logical_volume(cylinder2_solid, material, "Cylinder2_LV", reg)
cylinder_down_lv = create_logical_volume(cylinder1_solid, material, "Cylinder1_LV", reg)
cavity_lv = create_logical_volume(cavity_solid, material, "Cavity_LV", reg)

# Create a mother logical volume to contain both cylinders
mother_solid = pyg4ometry.geant4.solid.Box("MotherBox", 20, 20, 40, reg)
mother_lv = create_logical_volume(mother_solid, material, "Mother_LV", reg)

# Place the two cylinders inside the mother logical volume
place_cylinder(cylinder_up_lv, "Cylinder2_PV", mother_lv, [0, 0, -height1/2], reg)
place_cylinder(cylinder_down_lv, "Cylinder1_PV", mother_lv, [0, 0, -height1/2 - height2/2], reg)

# Define the displacement vector for the cavity within the lower cylinder
cavity_position = [0, 0, 0]  # TODO: Find the correct z position, at the moment [0, 0, 0] is the centre of the lower cylinder

# Place the cavity inside the lower cylinder
place_cylinder(cavity_lv, "Cavity_PV", cylinder_down_lv, cavity_position, reg)

# Set the world volume and write to GDML
reg.setWorld("Mother_LV")
visual = pyg4ometry.gdml.Writer()
visual.addDetector(reg)
visual.write('Steel_holder.gdml')