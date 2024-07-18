import pyg4ometry
import math
from l200geom import construct
import pyg4ometry.geant4 as g4
import pyg4ometry.gdml as gdml
import pyg4ometry.exceptions
import sys
import os

sys.path.insert(0, "/legend-pygeom-l200/src")  # This line works only in the docker container
import l200geom.core

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

def RenameMaterials(mat, _ren_g4_mats):
    if not isinstance(mat, g4.Material):
        print(f'Material "{mat.name}" is of type "{type(mat)}". Skipping its renaming.')
        return
    
    ren_mats_dict = {}
    obj_name = str(mat.name)  # Only for the warning at the end of the function

    if mat.name[-4:] != '_mat':
        mat.name += '_mat'
        _ren_g4_mats[obj_name] = mat
    else:
        # Material already renamed no need to redo it
        return
    
    if hasattr(mat, 'components'):
        for comp in mat.components:
            if isinstance(comp[0], g4.Material):
                RenameMaterials(comp[0], ren_mats_dict)
    
    for oldname, matobj in ren_mats_dict.items():
        if oldname in _ren_g4_mats.keys():
            print(f'The material with "{oldname}" name was already renamed!')
            if not (_ren_g4_mats[oldname] is matobj):
                print(f'WARNING --> Found multiple instances of material originally named "{oldname}" while processing material "{obj_name}"!')
            print()
        else:
            _ren_g4_mats[oldname] = matobj

def RenameGeomObjects(reg):
    renamed_g4_mats = {}

    # Go through all the materials that have name G4_ and load them properly from the NIST database
    for matkey, matobj in reg.materialDict.items():
        if matobj.name[:3] == 'G4_':
            continue
        RenameMaterials(matobj, renamed_g4_mats)

    print(f'Materials renamed ({len(renamed_g4_mats)}):')
    for k, v in renamed_g4_mats.items():
        print(f'   {k} --> {v}')

    # Clean the registry and then add all the materials
    for matname, _ in renamed_g4_mats.items():
        if matname in reg.materialDict:
            reg.materialDict.pop(matname)
            reg.materialNameCount[matname] -= 1
            if reg.materialNameCount[matname] <= 0:
                reg.materialNameCount.pop(matname)
        if matname in reg.materialUsageCount:
            reg.materialUsageCount.pop(matname)

    # Check which material is still in the registry
    for matname, matobj in renamed_g4_mats.items():
        if matname in reg.materialDict:
            pnt_msg = f'WARNING --> Material {matname} is still in the materials dictionary! '
            if not (matobj is reg.materialDict[matname]):
                pnt_msg += 'The two instances are different!'
            print(pnt_msg, file=sys.stderr)
            print()

    # Now add again the materials with the new name
    for _, matobj in renamed_g4_mats.items():
        reg.materialDict[matobj.name] = matobj
        reg.materialNameCount[matobj.name] += 1

    # Go through all the logical volumes to redefine their names
    renamed_lv = {}
    for lvkey, lvobj in reg.logicalVolumeDict.items():
        if lvobj.name[-3:] != '_LV':
            if lvkey in reg.logicalVolumeNameCount:
                reg.logicalVolumeNameCount.pop(lvkey)
            if lvkey in reg.assemblyVolumeDict:
                reg.assemblyVolumeDict.pop(lvkey)
            if lvkey in reg.assemblyVolumeNameCount:
                reg.assemblyVolumeNameCount.pop(lvkey)
            if lvkey in reg.logicalVolumeUsageCountDict:
                reg.logicalVolumeUsageCountDict.pop(lvkey)
            lvobj.name += '_LV'
            renamed_lv[lvkey] = lvobj

    for lvkey, _ in renamed_lv.items():
        if lvkey in reg.logicalVolumeDict:
            reg.logicalVolumeDict.pop(lvkey)
            reg.volumeTypeCountDict['logicalVolume'] -= 1

    print(f'Logical volumes renamed ({len(renamed_lv)}):')
    for k, v in renamed_lv.items():
        print(f'   {k} --> {v.name}')

    # Register the logical volumes with the new names
    for _, lvobj in renamed_lv.items():
        reg.addLogicalVolume(lvobj)

    # Go through all the physical volumes to redefine their names
    renamed_pv = {}
    for pvkey, pvobj in reg.physicalVolumeDict.items():
        if pvobj.name[-3:] != '_PV':
            if pvkey in reg.physicalVolumeNameCount:
                reg.physicalVolumeNameCount.pop(pvkey)
            pvobj.name += '_PV'
            renamed_pv[pvkey] = pvobj

    for pvkey, _ in renamed_pv.items():
        if pvkey in reg.physicalVolumeDict:
            reg.physicalVolumeDict.pop(pvkey)
            reg.volumeTypeCountDict["physicalVolume"] -= 1

    print(f'Physical volumes renamed ({len(renamed_pv)}):')
    for k, v in renamed_pv.items():
        print(f'   {k} --> {v.name}')

    # Register the physical volumes with the new names
    for _, pvobj in renamed_pv.items():
        reg.addPhysicalVolume(pvobj)

    return reg

reg = construct()
reg = RenameGeomObjects(reg)

lar_LV_list = reg.findLogicalVolumeByName('lar_LV')

if isinstance(lar_LV_list, list):
    for lv in lar_LV_list:
        place_cylinder(sourceLV, 'Source_PV', lv, position, reg)
else:
    place_cylinder(sourceLV, 'Source_PV', lar_LV_list, position, reg)
         
         
print(f"Found logical volume 'lar_LV': {lar_LV_list}")

# Find out volume:
for lv in reg.logicalVolumeDict:
    print("Logische Volumen:",lv)

# Set the world as the root volume
reg.setWorld("world_LV")


# Volume where the sources are placed
mother_LV = reg.findLogicalVolumeByName('lar_LV')  # TODO: is lar_LV the correct one?
print(type(mother_LV))

# Parameters for cylinders
height_1 = -300  # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_2 = -200  # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_3 = -100  # TODO: choose height which is defined as the centre of the absorber at the moment (z position)
height_4 = 0  # TODO: choose height which is defined as the centre of the absorber at the moment (z position)

# Upper Cylinder of steel holder
steel_radius_up = 2.5  # mm
steel_height_up = 8.6  # mm
# Lower Cylinder of steel holder
steel_radius_down = 3.2  # mm
steel_height_down = 9.0  # mm
# Dimensions for the source (cavity)
steel_cavity_radius = 2.0  # mm
steel_cavity_height = 4.0  # mm

source_inner_radius = 1.9  # mm
source_outer_radius = 2  # mm
source_height = 4  # mm

absorber_radius = 16 # mm
absorber_height = 37.5 # mm

material = "G4_Galactic"

# Generating the steel holder
steel_cylinder_up_solid = create_cylinder("Steel_Cylinder_up", 0, steel_radius_up, steel_height_up / 2, 0, 2 * math.pi, reg)
steel_cylinder_down_solid = create_cylinder("Steel_Cylinder_down", 0, steel_radius_down, steel_height_down / 2, 0, 2 * math.pi, reg)
steel_cavity_solid = create_cylinder("Steel_Cavity", 0.0, steel_cavity_radius, steel_cavity_height / 2, 0, 2 * math.pi, reg)
steel_cylinder_up_lv = create_logical_volume(steel_cylinder_up_solid, "metal_steel_mat", "Steel_Cylinder_up_LV", reg)
steel_cylinder_down_lv = create_logical_volume(steel_cylinder_down_solid, "metal_steel_mat", "Steel_Cylinder_down_LV", reg)
steel_cavity_lv = create_logical_volume(steel_cavity_solid, material, "Steel_Cavity_LV", reg)

# Place the two cylinders
place_cylinder(steel_cylinder_up_lv, "Steel_Cylinder_up_PV", mother_LV, [0, 0, -steel_height_down/2], reg)
place_cylinder(steel_cylinder_down_lv, "Steel_Cylinder_down_PV", mother_LV, [0, 0, -steel_height_down/2 - steel_height_up/2], reg)

# Define the displacement vector for the cavity within the lower cylinder
cavity_position = [0, 0, 0]  # TODO: Find the correct z position, at the moment [0, 0, 0] is the centre of the lower cylinder

# Place the cavity inside the lower cylinder
place_cylinder(steel_cavity_lv, "Steel_Cavity_PV", steel_cylinder_down_lv, cavity_position, reg)

# Generating the Thorium source
source_solid = create_cylinder("Source", source_inner_radius, source_outer_radius, source_height, 0, 2 * math.pi, reg)
source_lv = create_logical_volume(source_solid, material, name="Source_LV", registry=reg)

# Generating the Tantulum Absorbers
absorber_solid = create_cylinder("Absorber", 0, absorber_radius, absorber_height, 0, 2 * math.pi, reg)
absorber_lv = create_logical_volume(absorber_solid, material, name="Absorber_LV", registry = reg)

# Define the z position for the lowest sample and the x,y position as well according to l200
base_position1 = [121.472, -96.277,height_1 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position2 = [-120.9667, -96.9126,height_2 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position3 = [-121.304, 96.48977,height_3 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]
base_position4 = [121.135, 96.70,height_4 + 1/2 * absorber_height + 42 + 71 + 1.2 + 1/2 * source_height]

# Place cylinders in the world where the middle of the absorber is set to be 0
for i in range(1, 5, 1):
    source_1_PV = place_cylinder(source_lv, f'Lowest_Source_PV{i}', mother_LV, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2]], reg)
    source_2_PV = place_cylinder(source_lv, f'Second_Lowest_Source_PV{i}', mother_LV, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 100], reg)
    source_3_PV = place_cylinder(source_lv, f'Second_Highest_Source_PV{i}', mother_LV, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 200], reg)
    source_4_PV = place_cylinder(source_lv, f'Highest_Source_PV{i}', mother_LV, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'base_position{i}'][2] + 300], reg)
    absorber_PV = place_cylinder(absorber_lv, f'Absorber_PV{i}', mother_LV, [globals()[f'base_position{i}'][0], globals()[f'base_position{i}'][1], globals()[f'height_{i}']], reg)

# Write the geometries to a GDML file
visual = pyg4ometry.gdml.Writer()
file_path = os.path.abspath('Implemented_sources.gdml') 
visual.addDetector(reg)
visual.write(file_path)
print(f"Full path to the GDML file: {file_path}")
