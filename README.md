# Calibration Implementation

This project contains scripts for generating and implementing geometries related to the calibration of steel bands with sources and absorbers. Below is an overview of each script and its functionality.

## Contents

- `generate_sources_absorbers.py`: Generates the geometry for the 4 calibration steel bands, each with 4 sources and one absorber. This is placed within an empty volume, and the height of the 4 steel bands is adjustable.
- `geometry_steel_holder.py`: Approximates the steel holder using 3 cylinders and places it to form the desired shape. Again in an empty volume that is generated.
- `implement_sources_in_code.py`: Incorporates the geometries of the 4 steel bands with their respective 4 sources and absorbers, including the steel holders for each source, into the existing volume from the GitHub repository: `lar_LV`.

## Additional Files

- `geometry_Source.gdml`: Geometry description file for the sources.
- `Steel_holder.gdml`: Geometry description file for the steel holder.

## Ignored Test Files

- `implement_sources_test.py`
- `Test.py`

These files are used for testing purposes and are not essential for the main functionality of the project.

## Getting Started

1. **generate_sources_absorbers.py**: Run this script to generate the initial geometries for the calibration steel bands.
2. **geometry_steel_holder.py**: Execute this script to create the approximated steel holder geometry.
3. **implement_sources_in_code.py**: Use this script to integrate all generated geometries into the existing volume from the `lar_LV` repository
