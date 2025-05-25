import FreeCAD
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class SettingsCommand:
    def GetResources(self):
        return {
            "MenuText": "Настройки",
            "ToolTip": "Параметры сети",
            "Pixmap": "" # ← сюда можно вставить путь к иконке PNG
        }

    def Activated(self):
        dlg = SettingsDialog()
        if dlg.exec_():
            FreeCAD.Console.PrintMessage(f"Сетка={dlg.lineMeshSize.text()}, Итерации={dlg.lineIterations.text()}\n")

    def IsActive(self):
        return True


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки расчёта")

        l1 = QLabel("Размер сетки:")
        l2 = QLabel("Итераций:")

        self.lineMeshSize = QLineEdit("10")
        self.lineIterations = QLineEdit("100")

        ok = QPushButton("OK")
        cancel = QPushButton("Отмена")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        lay = QVBoxLayout()
        r1 = QHBoxLayout(); r1.addWidget(l1); r1.addWidget(self.lineMeshSize)
        r2 = QHBoxLayout(); r2.addWidget(l2); r2.addWidget(self.lineIterations)
        rb = QHBoxLayout(); rb.addWidget(ok); rb.addWidget(cancel)

        lay.addLayout(r1)
        lay.addLayout(r2)
        lay.addLayout(rb)

        self.setLayout(lay)
