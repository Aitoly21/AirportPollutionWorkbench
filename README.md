# Airport Pollution Workbench for FreeCAD

Проект представляет собой пользовательский модуль для **FreeCAD**, предназначенный для моделирования загрязняющих выбросов в районе аэропортов с использованием **OpenFOAM** и визуализацией в **ParaView**. Разработка выполнена в рамках магистерской выпускной квалификационной работы.

##  Состав комплекса

- **FreeCAD** + Workbench `Airport Pollution`
- **OpenStreetMap (OSM)** — источник геоданных
- **OpenFOAM** — CFD-расчёты загрязнений
- **ParaView** — визуализация результатов
- **Python + osmnx + geopandas** — автоматизация и геообработка

##  Установка

### 1. Установка FreeCAD

Скачайте и установите последнюю стабильную версию FreeCAD:

- [https://www.freecad.org/downloads.php](https://www.freecad.org/downloads.php)

> Рекомендуется использовать FreeCAD 0.21 или новее.

### 2. Установка OpenFOAM (для Windows)

Рекомендуется использовать сборку от BlueCFD:

- [https://bluecfd.github.io/Core/](https://bluecfd.github.io/Core/)

После установки убедитесь, что переменные среды OpenFOAM корректно настроены.

> Пример: проверьте, работает ли команда `simpleFoam` в командной строке BlueCFD.

### 3. Установка ParaView

Скачайте последнюю версию с официального сайта:

- [https://www.paraview.org/download/](https://www.paraview.org/download/)

> После расчёта результат можно открыть через `paraFoam` или вручную в ParaView.

### 4. Установка Python и библиотек

Рекомендуется использовать **Anaconda**:

- [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)

Создайте новое окружение:

```
conda create -n airport python=3.8
conda activate airport
conda install -c conda-forge osmnx geopandas matplotlib pandas
```

> Python 3.8 необходим для совместимости с ядром FreeCAD и OSM-обработкой.

##  Структура проекта

```
AirportPollutionWorkbench/
├── __init__.py
├── ImportGeometryCommand.py
├── SettingsCommand.py
├── RunCalculationCommand.py
├── StartSimulationCommand.py
├── VisualizeResultsCommand.py
├── requirements.txt
├── .gitignore
├── README.md
├── examples/
│   ├── SWO.FCStd            # Пример геометрии Шереметьево
│   ├── Dmdv.FCStd           # Пример геометрии Домодедово
│   └── example_run.md       # Инструкция по запуску

##  Как использовать

1. Скопируйте папку `AirportPollutionWorkbench` в директорию FreeCAD:
   
   ```
   # Пример для Windows:
   C:/Users/<ВАШ_ПОЛЬЗОВАТЕЛЬ>/AppData/Roaming/FreeCAD/Mod/
   ```

2. Запустите FreeCAD → выберите Workbench "Airport Pollution"

3. Доступны кнопки:

   - **Импорт геометрии** — загрузка OSM по координатам
   - **Настройки** — параметры сетки и итераций
   - **Запуск** — генерация анализа, сетки, граничных условий и старт расчёта
   - **Визуализация** — вывод результатов (можно открыть в ParaView)

4. Результаты моделирования сохраняются в формате, совместимом с OpenFOAM. Используйте `paraFoam` или вручную импортируйте папку `case` в ParaView для анализа.

##  Дополнительно можно добавить:

- `Makefile` или `.bat`-скрипты для автоматического запуска `blockMesh`, `Allrun`, `paraFoam`
- Примеры моделей `*.FCStd` для Шереметьево и Домодедово (в папке `examples/`)
- `requirements.txt` с зависимостями Python
- `.gitignore` с исключениями для кэша, временных файлов и логов

