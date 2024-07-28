import pyg4ometry
import pyg4ometry.geant4 as g4
from pyg4ometry import visualisation

def _color_recursive(lv: g4.LogicalVolume, viewer: visualisation.ViewerBase) -> None:
    if hasattr(lv, "pygeom_color_rgba"):
        for vis in viewer.instanceVisOptions[lv.name]:
            if lv.pygeom_color_rgba is False:
                vis.alpha = 0
                vis.visible = False
            else:
                vis.colour = lv.pygeom_color_rgba[0:3]
                vis.alpha = lv.pygeom_color_rgba[3]
                vis.visible = vis.alpha > 0

r = pyg4ometry.gdml.Reader("Implemented_sources.gdml")
l = r.getRegistry().getWorldVolume()
v = pyg4ometry.visualisation.VtkViewerColouredNew()
v.addLogicalVolume(l)
_color_recursive(l, v)

v.buildPipelinesAppend()
v.addAxes(length=5000)

v.view()
