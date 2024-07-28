import pyg4ometry
import pyg4ometry.geant4 as g4
import pyg4ometry.gdml as gdml
import pyg4ometry.exceptions

from l200geom import construct

import math

import sys
import os
from utils import *


reg = construct()
reg = RenameGeomObjects(reg)

lar_LV_list = reg.findLogicalVolumeByName('lar_LV')

# Set the world as the root volume
reg.setWorld("world_LV")


# Volume where the sources are placed
try:
    mother_LV = reg.findLogicalVolumeByName('lar_LV')[0]
except Exception as err:
    print(f'Could not find the "lar_LV" volume for placing the sources. Error message: {err}.')
    sys.exit()

# Parameters for cylinders
height_1 = 1000
height_2 = 700
height_3 = 1000
height_4 = 700

# Upper Cylinder of steel holder (the capsule)
capsule_radius_up = 3.2  # mm
capsule_height_up = 9.0  # mm

# Lower Cylinder of steel holder (the M4 screw)
capsule_radius_low = 2.5  # mm
capsule_height_low = 8.6  # mm

# Dimensions for the source (cavity)
capsule_cavity_radius = 2.0  # mm
capsule_cavity_height = 4.0  # mm

source_inner_radius = 1  # mm
source_outer_radius = 2  # mm
source_height = 4  # mm

absorber_radius = 16  # mm
absorber_height = 37.5  # mm

# Dimensions of steel band
# TODO: measure the dimensions, current dimensions are just place holders
band_length = 100 # mm
band_width = 10 # mm
band_thickness = 1 # mm

material = "G4_Galactic"

# Upper capsule cylinder
capsule_cylinder_up_solid = create_cylinder(name="Capsule_Cylinder_up",
                                            inner_radius=0,
                                            outer_radius=capsule_radius_up,
                                            height=capsule_height_up / 2.0,
                                            start_angle=0,
                                            end_angle=2 * math.pi,
                                            registry=reg)

# Lower capsule cylinder (the M4 screw)
capsule_cylinder_low_solid = create_cylinder(name="Capsule_Cylinder_low",
                                             inner_radius=0.0,
                                             outer_radius=capsule_radius_low,
                                             height=capsule_height_low / 2.0,
                                             start_angle=0,
                                             end_angle=2 * math.pi,
                                             registry=reg)


capsule_union_solid = g4.solid.Union(name="capsule_union_solid",
                                    obj1=capsule_cylinder_up_solid,
                                    obj2=capsule_cylinder_low_solid,
                                    tra2=[[0,0,0], [0,0,-(capsule_height_up+capsule_height_low)/2.0]],
                                    registry=reg)

# From here the capsule has the origin of axis in the middle of the lower volume
capsule_lv = g4.LogicalVolume(solid=capsule_union_solid,
                              material="metal_steel_mat",
                              name="source_capsule_LV",
                              registry=reg)

capsule_cavity_solid = create_cylinder(name="Source_capsule_Cavity",
                                       inner_radius=0.0,
                                       outer_radius=capsule_cavity_radius,
                                       height=capsule_cavity_height / 2.0,
                                       start_angle=0,
                                       end_angle=2.0 * math.pi,
                                       registry=reg)

capsule_cavity_lv = create_logical_volume(solid=capsule_cavity_solid,
                                          material="G4_Galactic",
                                          name="Source_capsule_Cavity_LV",
                                          registry=reg)

# Place the cavity inside the capsule (the lower cylinder)
cavity_position = [0, 0, 0]
cavity_rotation = [0, 0, 0]
capsule_cavity_pv = g4.PhysicalVolume(rotation=cavity_rotation,
                                      position=cavity_position,
                                      logicalVolume=capsule_cavity_lv,
                                      name="Source_capsule_Cavity_PV",
                                      motherVolume=capsule_lv,
                                      registry=reg
                                      )

# Generating the Tantulum Absorbers
absorber_body_solid = create_cylinder("Absorber_body", 0, absorber_radius, absorber_height, 0, 2 * math.pi, reg)

# The absorber has a hole at its top to fasten the source in
absorber_hole_radius = (1.001 * capsule_radius_low)
absorber_hole_height = (1.001 * capsule_height_low)

absorber_hole_solid = g4.solid.Tubs(name="Absorber_hole",
                                    pRMin=0,
                                    pRMax=absorber_hole_radius,
                                    pDz=absorber_hole_height / 2.0,
                                    pSPhi=0.0,
                                    pDPhi=2.0 * math.pi,
                                    registry=reg
                                    )

absorber_solid = g4.solid.Subtraction(name="absorber_solid",
                                      obj1=absorber_body_solid,
                                      obj2=absorber_hole_solid,
                                      tra2=[[0, 0, 0], [0, 0, (absorber_height - absorber_hole_height) / 2]],
                                      registry=reg)

absorber_lv = create_logical_volume(absorber_solid, material, name="Absorber_LV", registry=reg)




# Generating the steel band logical volume
band_solid = create_cuboid('Band_solid', band_width, band_thickness, band_length, registry = reg)

band_lv = create_logical_volume(band_solid, material="metal_steel_mat", name="Band_LV", registry=reg)


# Define the z position for the lowest sample and the x,y position as well according to photo of Gloria (25.07)
base_positions = {
    1: [144.2840, 56.6315, height_1 + (absorber_height + capsule_height_up) / 2.0],
    2: [-23.0977, 153.2694, height_2 + (absorber_height + capsule_height_up) / 2.0],
    3: [-144.2840, -56.6315, height_3 + (absorber_height + capsule_height_up) / 2.0],
    4: [23.0977, -153.2694, height_4 + (absorber_height + capsule_height_up) / 2.0]
}
    # keeping the old numbers just in case:
'''
    1: [121.472, -96.277, height_1 + (absorber_height + capsule_height_up) / 2.0],
    2: [-120.9667, -96.9126, height_1 + (absorber_height + capsule_height_up) / 2.0],
    3: [-121.304, 96.48977, height_1 + (absorber_height + capsule_height_up) / 2.0],
    4: [121.135, 96.70, height_1 + (absorber_height + capsule_height_up) / 2.0]
'''


# Place cylinders in the world where the middle of the absorber is set to be 0
source_counter = 0
for iString in range(1, 5, 1):  # Iteration over the strings

    g4.PhysicalVolume(rotation=[0, 0, 0],
                      position=[base_positions[iString][0], base_positions[iString][1], height_1],
                      logicalVolume=absorber_lv,
                      name=f"Absorber_{iString}_PV",
                      motherVolume=mother_LV,
                      registry=reg,
                      copyNumber=iString
                      )
    for iSource in range(4):
        source_counter += 1  # In this way the copy number start from 1
        g4.PhysicalVolume(rotation=[0, 0, 0],
                          position=[base_positions[iString][0], base_positions[iString][1],
                                    base_positions[iString][2] + iSource * 100.0],
                          logicalVolume=capsule_lv,
                          name=f"Source_Capsule_{iString}_{iSource + 1}_PV",
                          motherVolume=mother_LV,
                          registry=reg,
                          copyNumber=source_counter
                          )

# Define the source cylinder
source_solid = create_cylinder(name="Source",
                               inner_radius=source_inner_radius,
                               outer_radius=source_outer_radius,
                               height=source_height / 2.0,
                               start_angle=0,
                               end_angle=2 * math.pi,
                               registry=reg)

source_lv = create_logical_volume(solid=source_solid,
                                  material="G4_Galactic",
                                  name="Source_LV",
                                  registry=reg)

# Place the source cylinder at the center of each cavity
for iString in range(1, 5, 1):
    for iSource in range(4):
        g4.PhysicalVolume(rotation=[0, 0, 0],
                          position=[base_positions[iString][0], base_positions[iString][1],
                                    base_positions[iString][2] + iSource * 100.0],
                          logicalVolume=source_lv,
                          name=f"Source_{iString}_{iSource + 1}_PV",
                          motherVolume=capsule_cavity_lv,
                          registry=reg,
                          copyNumber=source_counter
                          )
        
# Position of the steel bands as close to the sources in x,y direction and as close the absorbers in z direction as possible
# The idea is to position the steelband between the sources and the detectors, without touching the steel capsules
steel_band_positions = {
    1: [144.2840 + (capsule_radius_up + 0.01), 56.6315, height_1 + (absorber_height + band_length/ 2.0) + 0.01],
    2: [-23.0977, 153.2694 + (capsule_radius_up + 0.01), height_2 + (absorber_height + band_length/ 2.0) + 0.01],
    3: [-144.2840 - (capsule_radius_up + 0.01), -56.6315, height_3 + (absorber_height + band_length/ 2.0) + 0.01],
    4: [23.0977, -153.2694 - (capsule_radius_up + 0.01), height_4 + (absorber_height + band_length/ 2.0) + 0.01]
}

        
# Place the steel bands as close to the sources in x,y direction and as close the absorbers in z direction as possible
# TODO: does this rotation make sense?
band_rotation_list = [[0,0,0], [0,0,math.pi / 2.0], [0,0,0], [0,0,math.pi / 2.0]] # I wanted to rotate all of them outward, which results in the band being in the way of the radiation before it hits the detectors
for iString in range(1, 5, 1):
    g4.PhysicalVolume(rotation=[0, 0, 0],
                      position=steel_band_positions[iString],
                      logicalVolume=band_lv,
                      name=f"Steel_Band_{iString}_PV",
                      motherVolume=mother_LV,
                      registry=reg,
                      copyNumber=iString)

# Write the geometries to a GDML file
writer = pyg4ometry.gdml.Writer()
file_path = os.path.abspath('Implemented_sources.gdml')
writer.addDetector(reg)
writer.write(file_path)
print(f"Full path to the GDML file: {file_path}")