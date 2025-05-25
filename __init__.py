import FreeCADGui
from .ImportGeometryCommand import ImportGeometryCommand
from .SettingsCommand import SettingsCommand
from .RunCalculationCommand import RunCalculationCommand
from .VisualizeResultsCommand import VisualizeResultsCommand
# Дополнительно
from .StartSimulationCommand import StartSimulationCommand

class AirportPollutionWorkbench(FreeCADGui.Workbench):
    MenuText = "Airport Pollution"
    ToolTip  = "Воркбенч моделирования загрязнений"
    Icon     = ""  # ← сюда можно вставить путь к иконке PNG

    def Initialize(self):
        FreeCADGui.addCommand("ImportGeometry", ImportGeometryCommand())
        FreeCADGui.addCommand("Settings", SettingsCommand())
        FreeCADGui.addCommand("RunCalculation", RunCalculationCommand())
        FreeCADGui.addCommand("VisualizeResults", VisualizeResultsCommand())
        FreeCADGui.addCommand("StartSimulation", StartSimulationCommand())
        # Панель инструментов
        mw = FreeCADGui.getMainWindow()
        tb = mw.findChild(QToolBar, "Airport Pollution Tools")
        if not tb:
            tb = QToolBar("Airport Pollution Tools", mw)
            mw.addToolBar(tb)
        for txt, cmd in [("Импорт геометрии", "ImportGeometry"),
                         ("Настройки", "Settings"),
                         ("Запуск", "StartSimulation"),
                         ("Визуализация", "VisualizeResults")]:
            act = QAction(txt, tb)
            act.triggered.connect(lambda _, c=cmd: FreeCADGui.runCommand(c, 0))
            tb.addAction(act)

    def Activated(self):
        FreeCAD.Console.PrintMessage("Airport Pollution активирован.\n")

    def Deactivated(self):
        FreeCAD.Console.PrintMessage("Airport Pollution деактивирован.\n")

try:
    FreeCADGui.addWorkbench(AirportPollutionWorkbench())
except Exception:
    pass
