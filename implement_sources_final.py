import pyg4ometry
import pyg4ometry.geant4 as g4
import pyg4ometry.gdml as gdml
import pyg4ometry.exceptions
from Extrapolation import current_mass_list

from l200geom import construct

import math
import sympy as sp

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
height_list = [height_1, height_2, height_3, height_4]

# Upper Cylinder of steel holder (the capsule)
capsule_radius_up = 6.38  # mm
capsule_height_up = 11  # mm

# Lower Cylinder of steel holder (the M4 screw)
capsule_radius_low = 3.98  # mm
capsule_height_low = 8.2  # mm

# Dimensions for the cavity of the upper cylinder
capsule_cavity_radius = 4.12  # mm
capsule_cavity_height = 10.13  # mm

# Dimensions for the source (inner radius first needs to be calculated)
source_outer_radius = 0.2  # cm
source_height = 0.4  # cm
density_thorium = 11.72  # density of thorium-228 in g/cm^3
source_volume_list = []
source_inner_radius_list = []
for i in range(0,len(current_mass_list),1):
    source_volume_list.append(current_mass_list[i]/density_thorium)
    source_inner_radius = (source_outer_radius**2-(source_volume_list[i]/(source_height*math.pi)))**(1/2) # in cm
    source_inner_radius_list.append(source_inner_radius * 10) # in mm
#print(source_inner_radius_list)

#Converting from cm to mm
source_outer_radius = 10 * source_outer_radius  # mm
source_height = 10 * source_height  # mm

absorber_radius = 16  # mm
absorber_height = 37.5  # mm

# Dimensions of steel band
band_length_list = []
for n in range(0,4,1):
    band_length_list.append((1700-height_list[n]-absorber_height/2.0)) # mm
#print(band_length_list)
band_width = 13 # mm
band_thickness = 0.1 # mm

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
band_solid_list = []
band_lv_list = []

for k in range(0, 4):
    band_solid = create_cuboid(f"Band_solid_{k+1}", band_width, band_thickness, band_length_list[k], registry=reg)
    band_lv = create_logical_volume(band_solid, material="metal_steel_mat", name=f"Band_LV_{k+1}", registry=reg)
    band_solid_list.append(band_solid)
    band_lv_list.append(band_lv)


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


# Define the source cylinder with all the correct masses
source_solid_list = []
source_lv_list = []
for number in range(len(current_mass_list)):
    source_solid_list.append(create_cylinder(
                                  name=f"Source_{number}",
                                  inner_radius=source_inner_radius_list[number],
                                  outer_radius=source_outer_radius,
                                  height=source_height / 2.0,
                                  start_angle=0,
                                  end_angle=2 * math.pi,
                                  registry=reg))

    source_lv_list.append(create_logical_volume(
                                     solid=source_solid_list[number],
                                     material="G4_Galactic",
                                     name=f"Source_LV_{number}",
                                     registry=reg))


# Place cylinders in the world where the middle of the absorber is set to be 0
source_counter = 0
for iString in range(1, 5):  # Iteration over the strings
    # Place the absorber
    g4.PhysicalVolume(rotation=[0, 0, 0],
                      position=[base_positions[iString][0], base_positions[iString][1], base_positions[iString][2] - (absorber_height + capsule_height_up) / 2.0],
                      logicalVolume=absorber_lv,
                      name=f"Absorber_{iString}_PV",
                      motherVolume=mother_LV,
                      registry=reg,
                      copyNumber=iString
                      )
    for iSource in range(4):
        source_counter += 1  # Increment the source counter
        # Get the correct logical volume for this source
        current_source_lv = source_lv_list[source_counter - 1]
        
        # Place the capsule
    
        g4.PhysicalVolume(rotation=[0, 0, 0],
                          position=[base_positions[iString][0], base_positions[iString][1],
                                    base_positions[iString][2] + iSource * 100.0], # 100mm being the height difference between the sources
                          logicalVolume=capsule_lv,
                          name=f"Source_Capsule_{iString}_{iSource + 1}_PV",
                          motherVolume=mother_LV,
                          registry=reg,
                          copyNumber=source_counter
                          )

        # Place the source
        g4.PhysicalVolume(rotation=[0, 0, 0],
                          position=[base_positions[iString][0], base_positions[iString][1],
                                    base_positions[iString][2] + iSource * 100.0],
                          logicalVolume=current_source_lv,
                          name=f"Source_{iString}_{iSource + 1}_PV",
                          motherVolume=mother_LV,
                          registry=reg,
                          copyNumber=source_counter
                          )
        
# Position of the steel bands as close to the sources in x,y direction and as close the absorbers in z direction as possible
# The idea is to position the steelband between the sources and the detectors, without touching the steel capsules
steel_band_positions = {
    1: [144.2840 + (capsule_radius_up + 0.01), 56.6315, height_1 + (absorber_height + band_length_list[0])/ 2.0 + 0.01],
    2: [-23.0977, 153.2694 + (capsule_radius_up + 0.01), height_2 + (absorber_height + band_length_list[1])/ 2.0 + 0.01],
    3: [-144.2840 - (capsule_radius_up + 0.01), -56.6315, height_3 + (absorber_height + band_length_list[2])/ 2.0 + 0.01],
    4: [23.0977, -153.2694 - (capsule_radius_up + 0.01), height_4 + (absorber_height + band_length_list[3])/ 2.0 + 0.01]
}

        

# Place the steel bands as close to the sources in x,y direction and as close the absorbers in z direction as possible
band_rotation_list = [[0, 0, 0], [0, 0, math.pi / 2.0], [0, 0, 0], [0, 0, math.pi / 2.0]]
for iString in range(1, 5):
    g4.PhysicalVolume(rotation=band_rotation_list[iString - 1],
                      position=steel_band_positions[iString],
                      logicalVolume=band_lv_list[iString - 1],
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