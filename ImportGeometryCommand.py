import FreeCAD, FreeCADGui
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
import osmnx as ox
import geopandas as gpd
import traceback
import Part, Draft
from BOPTools import SplitFeatures

ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"

def safe_features_from_point(center, tags, dist):
    try:
        return ox.features_from_point(center, tags=tags, dist=dist)
    except Exception:
        FreeCAD.Console.PrintError("\u274c Ошибка при запросе к OpenStreetMap:\n" + traceback.format_exc() + "\n")
        return gpd.GeoDataFrame()


class ImportGeometryCommand:
    def GetResources(self):
        return {
            "MenuText": "Импорт геометрии",
            "ToolTip": "Импорт геометрии из OpenStreetMap",
            "Pixmap": ""# ← сюда можно вставить путь к иконке PNG
        }

    def Activated(self):
        dlg = ImportGeometryDialog()
        if not dlg.exec_():
            return
        try:
            lat = float(dlg.lineEditLat.text().strip())
            lon = float(dlg.lineEditLon.text().strip())
        except:
            FreeCAD.Console.PrintError("\u274c Введите корректные координаты!\n")
            return

        center = (lat, lon)
        dist, extension, scale = 1500, 200, 1/65.0
        bdf = safe_features_from_point(center, {'building': True}, dist)
        if bdf.empty:
            FreeCAD.Console.PrintError("\u2757 Ничего не найдено в OSM.\n")
            return

        polys = bdf[bdf.geometry.type=='Polygon'].to_crs(epsg=3857)
        minx, miny, maxx, maxy = polys.total_bounds
        width, height, depth = maxx+extension-minx, maxy+extension-miny, 100000*scale

        doc = FreeCAD.newDocument()
        cube = Part.makeBox(width+extension, height+extension, depth)
        cube.Placement.Base = FreeCAD.Vector(minx-extension, miny-extension, 0)
        cube_obj = doc.addObject("Part::Feature", "Cube"); cube_obj.Shape = cube

        r1, h1 = 100*scale, 500*scale
        cyl1 = Part.makeCylinder(r1, h1)
        cyl1_obj = doc.addObject("Part::Feature", "Cylinder"); cyl1_obj.Shape = cyl1
        cyl1_obj.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 90)
        cyl1_obj.Placement.Base = FreeCAD.Vector(minx+(width-extension)/2, miny-extension+h1, 2000*scale+r1)

        cx = cube_obj.Placement.Base.x+(width+extension)/2
        cy = cube_obj.Placement.Base.y+(height+extension)/2
        r2, h2 = 50*scale, 200*scale
        cyl2 = Part.makeCylinder(r2, h2)
        cyl2_obj = doc.addObject("Part::Feature", "CenterCylinder"); cyl2_obj.Shape = cyl2
        cyl2_obj.Placement.Base = FreeCAD.Vector(cx-r2, cy-r2, 0)

        buildings = []
        for i, row in enumerate(polys.itertuples(), start=1):
            coords = [(x,y,0) for x,y in row.geometry.exterior.coords]
            face = Part.Face(Part.makePolygon(coords))
            height_b = max(row.geometry.area/2000, 20)
            bobj = doc.addObject("Part::Feature", f"Building_{i}")
            bobj.Shape = face.extrude(FreeCAD.Vector(0,0,height_b))
            buildings.append(bobj)

        frag = SplitFeatures.makeBooleanFragments(name='Buildings')
        frag.Objects, frag.Mode = buildings, 'Standard'
        frag.Proxy.execute(frag); frag.purgeTouched()
        for ch in frag.ViewObject.Proxy.claimChildren(): ch.ViewObject.hide()
        doc.recompute()

        edges = cube_obj.Shape.Edges
        if len(edges) > 8:
            e = edges[8]; clones = []
            for src in ("Cube","Cylinder","CenterCylinder","Buildings"):
                o = doc.getObject(src)
                if o: clones.append(Draft.make_clone([o], forcedraft=True))
            for clone in clones:
                clone.Scale = FreeCAD.Vector(65,65,65)
                base_pt = FreeCAD.Vector(e.Vertexes[0].X, e.Vertexes[0].Y, e.Vertexes[0].Z)
                diff = base_pt.sub(clone.Placement.Base)
                corr = FreeCAD.Vector(diff.x*-64, diff.y*-64, diff.z*-64)
                clone.Placement.move(corr)
        doc.recompute()

        xor = SplitFeatures.makeXOR(name='XOR')
        xor.Objects = [doc.getObject(n) for n in ("Clone","Clone001","Clone002") if doc.getObject(n)]
        xor.Proxy.execute(xor); xor.purgeTouched()
        for ch in xor.ViewObject.Proxy.claimChildren(): ch.ViewObject.hide()

        to_del = ['Cube','Cylinder','CenterCylinder','Buildings'] + [f'Building_{i}' for i in range(1,len(buildings)+1)]
        for name in to_del:
            if doc.getObject(name): doc.removeObject(name)
        doc.recompute()

        FreeCAD.Gui.ActiveDocument.ActiveView.fitAll()
        FreeCAD.Gui.activeDocument().activeView().viewAxometric()
        path = "C:/Map/Compute_domain.FCStd"
        doc.saveAs(path)
        FreeCAD.Console.PrintMessage(f"\u2705 Модель сохранена: {path}\n")

    def IsActive(self): return True


class ImportGeometryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт геометрии (OSM)")
        self.setMinimumWidth(300)
        l1, l2 = QLabel("Широта (Lat):"), QLabel("Долгота (Lon):")
        self.lineEditLat, self.lineEditLon = QLineEdit(), QLineEdit()
        self.lineEditLat.setMinimumWidth(200); self.lineEditLon.setMinimumWidth(200)
        ok, cancel = QPushButton("OK"), QPushButton("Отмена")
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        lay = QVBoxLayout()
        for lbl, line in ((l1, self.lineEditLat), (l2, self.lineEditLon)):
            row = QHBoxLayout(); row.addWidget(lbl); row.addWidget(line); lay.addLayout(row)
        rb = QHBoxLayout(); rb.addWidget(ok); rb.addWidget(cancel)
        lay.addLayout(rb); self.setLayout(lay)
