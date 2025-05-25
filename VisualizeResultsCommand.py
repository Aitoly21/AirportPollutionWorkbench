import FreeCAD

class VisualizeResultsCommand:
    def GetResources(self):
        return {
            "MenuText": "Визуализация",
            "ToolTip": "Показ результатов",
            "Pixmap": "" # ← сюда можно вставить путь к иконке PNG
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Показываем результаты...\n")

    def IsActive(self):
        return True
