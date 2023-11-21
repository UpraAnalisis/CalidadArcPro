# -*- coding: utf-8 -*-

import arcpy
import os
import sys
import datetime

class Toolbox(object):
    
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CalPol]
    
    


class CalPol(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Polígonos"
        self.description = "Herramienta para el control de calidad de capas vectoriales con geometría de tipo polígono"
        self.canRunInBackground = False
        self.conteo_validador = 0
       

    def getParameterInfo(self):
        """Define parameter definitions"""
       # Define el parámetro de capa de entrada
        capaEntrada = arcpy.Parameter(
        displayName="Capa de entrada",
        name="capa_entrada",
        datatype=["GPFeatureLayer","DEFeatureClass","DETable","GPTableView"],
        parameterType="Required",
        direction="Input")

        # Define el parámetro de la ruta del reporte
        folderEntrada = arcpy.Parameter(
        displayName="Ruta reporte",
        name="ruta_reporte",
        datatype=["DEWorkspace"],
        parameterType="Required",
        direction="Input")

        # Define el parámetro de la validación de Geometrías Z y M
        geomZM = arcpy.Parameter(
        displayName="Validar geometrías Z y M ",
        name="geomZM",
        datatype=["GPBoolean"],
        parameterType="Optional",
        direction="Input")

        # # Define el parámetro de la validación de validación de geometria
        # geomVal = arcpy.Parameter(
        # displayName="Validar Errores geométricos",
        # name="geomVal",
        # datatype=["GPBoolean"],
        # parameterType="Optional",
        # direction="Input")

        # # Define el parámetro de la validación de geometrias multipart
        # multipartVal = arcpy.Parameter(
        # displayName="Validar geometrías multipart",
        # name="multipartVal",
        # datatype=["GPBoolean"],
        # parameterType="Optional",
        # direction="Input")

        # # Define el parámetro de la validación de elementos duplicados
        # duplicadosVal = arcpy.Parameter(
        # displayName="Validar elementos duplicados",
        # name="duplicadosVal",
        # datatype=["GPBoolean"],
        # parameterType="Optional",
        # direction="Input")

        # # Define el parámetro de la validación topológica
        # topologiaVal = arcpy.Parameter(
        # displayName="Validar topología",
        # name="topologiaVal",
        # datatype=["GPBoolean"],
        # parameterType="Optional",
        # direction="Input")


        # # Define el parámetro de la validación del sistema de referencia
        # sisRefVal = arcpy.Parameter(
        # displayName="Validar sistema de referencia",
        # name="sisRefVal",
        # datatype=["GPBoolean"],
        # parameterType="Optional",
        # direction="Input")

        # Define el parámetro de capa de salida
        capaEvaluada = arcpy.Parameter(
        displayName="Capa de salida",
        name="capaEvaluada",
        datatype=["GPFeatureLayer","DEFeatureClass","DETable","GPTableView"],
        parameterType="Derived",
        direction="Output")

        capaEvaluada.parameterDependencies = [capaEntrada.name]
        capaEvaluada.schema.clone = True


        parameters  = [capaEntrada,folderEntrada,geomZM,capaEvaluada]
        return parameters 

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        usuario = self.obtenerUsuario()
        fecha = self.obtenerFecha()
        capaEntrada = parameters[0]
        folderEntrada = parameters[1]
        
        archivo =r"%s\RCAL_%s_%s.txt"%(folderEntrada.value,arcpy.Describe(capaEntrada.value).name, fecha)
        reporte = open(archivo,"w")
        reporte.write("Fecha: %s\n"%(fecha))
        reporte.write("Usuario: %s\n"%(usuario))
        reporte.write("Capa evaluada: %s\n"%(str(arcpy.Describe(capaEntrada.value).name)))
        reporte.write("Ruta de la capa: %s\n"%(str(arcpy.Describe(capaEntrada.value).catalogpath)))

        self.evaluarParametros(reporte,parameters)

        #arcpy.SetParameterAsText(len(parameters)-1, capaEntrada)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

    def obtenerUsuario(self):
        """Devuelve el usuario activo en la ejecución de la herramienta"""
        usuario = os.getenv("USERNAME")
        return (usuario)

    def obtenerFecha(self):
        """ Retorna la fecha en formato texto inlcuyendo la hora"""
        fecha = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S").replace(".","") # se le remplaza el punto porque a veces genera errores con los puntos
        return (fecha)
    
    def tiene_z(self, capa):
        return arcpy.Describe(capa).hasZ

    def tiene_m(self, capa):
        return arcpy.Describe(capa).hasM

    
    def evaluarParametros(self,reporte,parameters):
        capaEntrada = parameters[0].value
        val_zm = parameters[2].value

        ##################### VALIDACION Z Y M ##########################
        if val_zm is True:
            arcpy.AddMessage("Validacion ZM \n")
            reporte.write("###### Validación de geometrias Z y M ######")
            reporte.write('\n')
            if self.tiene_m(capaEntrada) or self.tiene_z(capaEntrada):
                if self.tiene_m(capaEntrada):
                    reporte.write("La capa tiene M en su geometría" + " \n")
                    self.conteo_validador+=1
                if self.tiene_z(capaEntrada):
                    reporte.write("La capa tiene Z en su geometría" + " \n")
                    self.conteo_validador+=1
                reporte.write('\n')
            else:
                reporte.write("La capa no tiene ni Z ni M en su geometría" + " \n")
        ####################################################################
       