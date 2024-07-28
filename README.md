# Calibration Implementation

This project contains scripts for generating and implementing geometries related to the calibration of steel bands with sources and absorbers. Below is an overview of each script and its functionality.

## Contents

- `Extrapolation.py`: Calculates the amount of Thorium 228 each source contains at the current time.
- `generate_sources_absorbers.py`: Generates the geometry for the absorbers and sources and places them in an empty volume.
- `geometry_steel_holder.py`: Generates the geometry for the steel holders that contain the sources.
- `implement_sources_band.py`: Implements sources, absorbers, steel holders, and steel bands in the l200 geometry.
- `implement_sources_fra.py`: Francesco improved my code for implementing the geometries (except for the steel band) in l200. This was used as the basis for all subsequent codes.
- `implement_sources_glo.py`: Implements the geometries (except for the steel band) in l200, with some corrections added to visualize and simulate the code.
- `implement_sources_glo_v2.py`: Same code as `implement_sources_glo.py`, but here the extrapolated masses from `Extrapolate.py` were imported and the sizes of all sources were adjusted.
- `Test.py`: Code for testing various functionalities.
- `utils.py`: Contains functions needed to generate cylinders for various codes and other utilities.
- `utils_v2.py`: Same as `utils.py`, but with additional functions required for `implement_sources_glo_v2.py` including the steel band.

## Additional Files

- `geometry_Source.gdml`: Geometry description file for the sources.
- `Steel_holder.gdml`: Geometry description file for the steel holder.
- `Implemented_sources.gdml`: The generated geometry for the implemented sources.

## Ignored Test Files

- `implement_sources_test.py`
- `Test.py`

These files are used for testing purposes and are not essential for the main functionality of the project.

## Getting Started

1. **generate_sources_absorbers.py**: Run this script to generate the initial geometries for the calibration steel bands.
2. **geometry_steel_holder.py**: Execute this script to create the approximated steel holder geometry.
3. **implement_sources.py**: Use this script to integrate all generated geometries into the existing volume from the `lar_LV` repository.