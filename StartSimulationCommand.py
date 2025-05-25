# Этот файл включает: открытие модели, генерацию сетки, настройку ГУ и запуск расчёта
import FreeCAD
from CfdOF import CfdAnalysis, CfdTools, CfdConsoleProcess
from CfdOF.Solve import (CfdPhysicsSelection, CfdFluidMaterial,
                          CfdInitialiseFlowField, CfdSolverFoam, CfdFluidBoundary, CfdRunnableFoam, CfdCaseWriterFoam)
from CfdOF.Mesh import (CfdMesh, CfdMeshRefinement, CfdMeshTools)
import os

class StartSimulationCommand:
    def GetResources(self):
        return {
            "MenuText": "Старт симуляции",
            "ToolTip": "Импорт модели, генерация сетки, запуск решателя",
            "Pixmap": ""# ← сюда можно вставить путь к иконке PNG
        }

    def Activated(self):
        FreeCAD.openDocument("C:/Map/Compute_domain.FCStd")

        analysis = CfdAnalysis.makeCfdAnalysis("CfdAnalysis")
        CfdTools.setActiveAnalysis(analysis)
        analysis.addObject(CfdPhysicsSelection.makeCfdPhysicsSelection())
        analysis.addObject(CfdFluidMaterial.makeCfdFluidMaterial("FluidProperties"))
        analysis.addObject(CfdInitialiseFlowField.makeCfdInitialFlowField())
        analysis.addObject(CfdSolverFoam.makeCfdSolverFoam())

        CfdMesh.makeCfdMesh("XOR_Mesh")
        App.ActiveDocument.ActiveObject.Part = App.ActiveDocument.XOR
        CfdTools.getActiveAnalysis().addObject(App.ActiveDocument.ActiveObject)
        App.ActiveDocument.XOR_Mesh.CharacteristicLengthMax = "18000.0 mm"

        # Refinement zones
        CfdMeshRefinement.makeCfdMeshRefinement(App.ActiveDocument.XOR_Mesh)
        App.ActiveDocument.MeshRefinement.RelativeLength = 0.01
        App.ActiveDocument.MeshRefinement.RefinementThickness = '1.0 mm'
        FreeCAD.ActiveDocument.MeshRefinement.ShapeRefs = [(FreeCAD.ActiveDocument.getObject('Clone001'), ('',))]

        CfdMeshRefinement.makeCfdMeshRefinement(App.ActiveDocument.XOR_Mesh)
        App.ActiveDocument.MeshRefinement001.RelativeLength = 0.05
        App.ActiveDocument.MeshRefinement001.RefinementThickness = '1.0 mm'
        FreeCAD.ActiveDocument.MeshRefinement001.ShapeRefs = [(FreeCAD.ActiveDocument.getObject('Clone002'), ('',))]
        FreeCAD.ActiveDocument.recompute()

        cart_mesh = CfdMeshTools.CfdMeshTools(FreeCAD.ActiveDocument.XOR_Mesh)
        FreeCAD.ActiveDocument.XOR_Mesh.Proxy.cart_mesh = cart_mesh
        cart_mesh.writeMesh()

        cmd = CfdTools.makeRunCommand('Allmesh.bat', source_env=False)
        env_vars = CfdTools.getRunEnvironment()
        mesh_process = CfdConsoleProcess.CfdConsoleProcess()
        mesh_process.start(cmd, env_vars=env_vars, working_dir=cart_mesh.meshCaseDir)
        mesh_process.waitForFinished()

        # Boundary conditions
        inlet = CfdFluidBoundary.makeCfdFluidBoundary(); CfdTools.getActiveAnalysis().addObject(inlet)
        inlet.Label = 'inlet'; inlet.BoundaryType = 'inlet'; inlet.BoundarySubType = 'uniformVelocityInlet'
        inlet.Uy = '250000.0 mm/s'; inlet.ReverseNormal = True; inlet.Temperature = '290.0 K'
        inlet.ShapeRefs = [(FreeCAD.ActiveDocument.getObject('Clone001'), ('Face3',))]

        outlet = CfdFluidBoundary.makeCfdFluidBoundary(); CfdTools.getActiveAnalysis().addObject(outlet)
        outlet.Label = 'outlet'; outlet.BoundaryType = 'outlet'; outlet.BoundarySubType = 'staticPressureOutlet'
        outlet.Temperature = '290.0 K'
        outlet.ShapeRefs = [(FreeCAD.ActiveDocument.getObject('XOR'), ('Face6', 'Face3', 'Face2', 'Face4', 'Face1'))]

        wall = CfdFluidBoundary.makeCfdFluidBoundary(); CfdTools.getActiveAnalysis().addObject(wall)
        wall.Label = 'wall'; wall.Temperature = '290.0 K'
        wall.ShapeRefs = [
            (FreeCAD.ActiveDocument.getObject('Clone001'), ('Face1',)),
            (FreeCAD.ActiveDocument.getObject('XOR'), ('Face5',)),
            (FreeCAD.ActiveDocument.getObject('Clone002'), ('',))]

        App.ActiveDocument.PhysicsModel.Turbulence = 'RANS'
        App.ActiveDocument.PhysicsModel.gy = '-9800.0 mm/s^2'

        App.ActiveDocument.InitialiseFields.PotentialFlow = False
        App.ActiveDocument.InitialiseFields.UseOutletPValue = False
        App.ActiveDocument.InitialiseFields.Temperature = '290.0 K'

        App.ActiveDocument.CfdSolver.MaxIterations = 50

        writer = CfdCaseWriterFoam.CfdCaseWriterFoam(FreeCAD.ActiveDocument.CfdAnalysis)
        FreeCAD.ActiveDocument.CfdSolver.Proxy.case_writer = writer
        writer.writeCase()

        cart_mesh = CfdMeshTools.CfdMeshTools(FreeCAD.ActiveDocument.XOR_Mesh)
        FreeCAD.ActiveDocument.XOR_Mesh.Proxy.cart_mesh = cart_mesh
        cart_mesh.writeMesh()
        mesh_process = CfdConsoleProcess.CfdConsoleProcess()
        mesh_process.start(cmd, env_vars=env_vars, working_dir=cart_mesh.meshCaseDir)
        mesh_process.waitForFinished()

        # Solver
        solver_runner = CfdRunnableFoam.CfdRunnableFoam(App.ActiveDocument.CfdAnalysis, App.ActiveDocument.CfdSolver)
        cmd = solver_runner.getSolverCmd(writer.case_dir)
        env_vars = solver_runner.getRunEnvironment()
        solver_process = CfdConsoleProcess.CfdConsoleProcess(stdout_hook=solver_runner.processOutput)
        solver_process.start(cmd, env_vars=env_vars, working_dir=writer.case_dir)
        solver_process.waitForFinished()

    def IsActive(self):
        return True
