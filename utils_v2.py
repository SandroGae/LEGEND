import pyg4ometry
import pyg4ometry.geant4 as g4
import pyg4ometry.gdml as gdml
import pyg4ometry.exceptions


# Function to create a cylindrical solid
def create_cylinder(number, name, inner_radius, outer_radius, height, start_angle, end_angle, registry): #number choosed correct mass for each source
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