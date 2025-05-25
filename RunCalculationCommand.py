import FreeCAD

class RunCalculationCommand:
    def GetResources(self):
        return {
            "MenuText": "Запуск",
            "ToolTip": "Старт расчёта",
            "Pixmap": "" # ← сюда можно вставить путь к иконке PNG
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Расчёт начат...\n")
        # Здесь будет логика запуска расчёта (опционально вынесена в отдельный модуль)
        FreeCAD.Console.PrintMessage("Расчёт окончен!\n")

    def IsActive(self):
        return True
