# -*- coding: utf-8 -*-

import arcpy
import os
import sys
import datetime

contador = 0
gdb_salida = ""
PROYECCION = "PROJCS['MAGNA_Colombia_Bogota',GEOGCS['GCS_MAGNA',DATUM['D_MAGNA',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1000000.0],PARAMETER['False_Northing',1000000.0],PARAMETER['Central_Meridian',-74.07750791666666],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',4.596200416666666],UNIT['Meter',1.0]];-4623200 -9510300 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;IsHighPrecision"

contador = 0
gdb_salida = ""

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
        self.label = "Calidad Polígonos"
        self.description = "Herramienta para el control de calidad de capas vectoriales con geometría de tipo polígono"
        self.canRunInBackground = False
        self.conteo_validador = 0
       

    def getParameterInfo(self):
        """Define parameter definitions"""
       # Define el parámetro de capa de entrada
        capaEntrada = arcpy.Parameter(
        displayName ="Capa de entrada",
        name = "capa_entrada",
        datatype = ["GPFeatureLayer","DEFeatureClass","DETable","GPTableView"],
        parameterType = "Required",
        direction = "Input")

        # Define el parámetro de la ruta del reporte
        folderEntrada = arcpy.Parameter(
        displayName = "Ruta reporte",
        name = "folder_reporte",
        datatype = "DEWorkspace",
        parameterType = "Required",
        direction = "Input")

        # Define el parámetro de la validación de Geometrías Z y M
        geomZM = arcpy.Parameter(
        displayName = "Validar geometrías Z y M ",
        name = "geomZM",
        datatype = "GPBoolean",
        parameterType = "Optional",
        direction = "Input")

        # # Define el parámetro de la validación de topología 
        evalTop = arcpy.Parameter(
        displayName ="Validar Topología",
        name="evalTop",
        datatype = "GPBoolean",
        parameterType = "Optional",
        direction="Input")

        # # Define el tipo de regla de la validación de topología 
        reglaTop = arcpy.Parameter(
        displayName="Reglas Topología",
        name = "reglaTop",
        datatype = "GPString",
        parameterType = "Optional",
        direction = "Input")
        
        reglaTop.type = 'ValueList'
        reglaTop.filter.list = ["Huecos y sobreposición", "Huecos", "Sobreposición"]
        reglaTop.value = "Huecos y sobreposición"
        

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
        name ="capaEvaluada",
        datatype=["GPFeatureLayer","DEFeatureClass","DETable","GPTableView"],
        parameterType="Derived",
        direction="Output")

        capaEvaluada.parameterDependencies = [capaEntrada.name]
        capaEvaluada.schema.clone = True


        parameters  = [capaEntrada, folderEntrada, geomZM, evalTop, reglaTop, capaEvaluada]
        return parameters 

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        paramEvalTopologia = [param for param in parameters if param.name == "evalTop"][0]
        paramReglaTopologia = [param for param in parameters if param.name == "reglaTop"][0]

        if paramEvalTopologia.value:
            paramReglaTopologia.enabled = True
        else:
            paramReglaTopologia.enabled = False

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
        
        archivo =r"%s\RCAL_%s_%s.txt"%(folderEntrada.value,arcpy.Describe(capaEntrada.value).name[:5], fecha)
        reporte = open(archivo,"w")
        reporte.write("Fecha: %s\n"%(fecha))
        reporte.write("Usuario: %s\n"%(usuario))
        reporte.write("Capa evaluada: %s\n"%(str(arcpy.Describe(capaEntrada.value).name)))
        reporte.write("Ruta de la capa: %s\n"%(str(arcpy.Describe(capaEntrada.value).catalogpath)))

        self.evaluarParametros(reporte,parameters)

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
        global contador
        global gdb_salida
        contador = 0
        paramCapaEntrada = [param for param in parameters if param.name == "capa_entrada"][0]
        paramCapaEntrada = [param for param in parameters if param.name == "capa_entrada"][0]
        paramFolder_reporte = [param for param in parameters if param.name == "folder_reporte"][0]
        paramval_zm = [param for param in parameters if param.name == "geomZM"][0]
        paramEvalTop = [param for param in parameters if param.name == "evalTop"][0]
        paramReglaTop = [param for param in parameters if param.name == "reglaTop"][0]


        ##################### VALIDACION Z Y M ##########################
        if paramval_zm.value is True:
            arcpy.AddMessage("Validacion ZM \n")
            reporte.write("###### Validación de geometrias Z y M ######")
            reporte.write('\n')
            if self.tiene_m(paramCapaEntrada.value) or self.tiene_z(paramCapaEntrada.value):
                if self.tiene_m(paramCapaEntrada.value):
                    reporte.write("La capa tiene M en su geometría" + " \n")
                    self.conteo_validador+=1
                if self.tiene_z(paramCapaEntrada.value):
                    reporte.write("La capa tiene Z en su geometría" + " \n")
                    self.conteo_validador+=1
                reporte.write('\n')
            else:
                reporte.write("La capa no tiene ni Z ni M en su geometría" + " \n")
        ####################################################################

        ##################### VALIDACION topología ##########################
        if paramEvalTop.value is True:
            arcpy.AddMessage("Validacion de topología \n")
            reporte.write("###### Validación de topología ######")
            reporte.write('\n')

            nombre_gdb = f"topo_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}"
            nombre_gdb = nombre_gdb.replace(".", "")
            gdb_salida = f"{paramFolder_reporte.value}/{nombre_gdb}.gdb"
            nombre_dataset = "dt_topologia"

            if not arcpy.Exists(gdb_salida):
                arcpy.management.CreateFileGDB(paramFolder_reporte.value, nombre_gdb)

            arcpy.env.workspace = gdb_salida
            nombre_capa = arcpy.Describe(paramCapaEntrada.value).name

            arcpy.management.CreateFeatureDataset(gdb_salida, nombre_dataset, PROYECCION)
            path_dataset = os.path.join(gdb_salida, nombre_dataset)    

            arcpy.conversion.FeatureClassToFeatureClass(paramCapaEntrada.value, path_dataset, nombre_capa)
            path_Feature = os.path.join(path_dataset, nombre_capa)

            capa_topologia = f"topo_capa_{nombre_capa}"
            arcpy.management.CreateTopology(path_dataset, capa_topologia, "")
            path_topology = os.path.join(path_dataset, capa_topologia)

            arcpy.management.AddFeatureClassToTopology(path_topology, path_Feature, "1", "1")
            ErroresTopologia =""
            if paramReglaTop.value == "Huecos y sobreposición":
                arcpy.management.AddRuleToTopology(path_topology, "Must Not Overlap (Area)", path_Feature, "", "", "")
                arcpy.management.AddRuleToTopology(path_topology, "Must Not Have Gaps (Area)", path_Feature, "", "", "")
                arcpy.management.ValidateTopology(path_topology, "Full_Extent")
                arcpy.management.ExportTopologyErrors(path_topology, path_dataset, "Errores")

                ErroresTopologia = f"#####Validación de topología (Huecos - Sobreposición) ######\n"
                for fc in arcpy.ListFeatureClasses(feature_dataset=nombre_dataset):
                    path = os.path.join(arcpy.env.workspace, nombre_dataset, fc)
                    if "Errores" in arcpy.Describe(path).name:
                        Ctd_contar = arcpy.management.GetCount(path)
                        Ctd = int(Ctd_contar.getOutput(0))
                        if Ctd > 0:
                            if "line" in str(arcpy.Describe(path).name):
                                if Ctd > 1:
                                    contador += 1
                                    ErroresTopologia += f"La capa presenta {Ctd} casos de huecos.\n"
                            elif "poly" in str(arcpy.Describe(path).name):
                                contador += 1
                                ErroresTopologia += f"La capa presenta {Ctd} casos de sobreposición.\n"

                                oid_campo = [f.name for f in arcpy.Describe(path_Feature).fields if f.type == "OID"][0]
                                arreglo = []
                                with arcpy.da.SearchCursor(path, ["OID@", "OriginObjectID", "DestinationObjectID", "RuleDescription"]) as cursor:
                                    for fila in cursor:
                                        if "Larger Than" in fila[3]:
                                            pass
                                        else:
                                            arreglo.append(fila[1])
                                            arreglo.append(fila[2])
                                if len(arreglo) > 0:
                                    if len(arreglo) == 1:
                                        ErroresTopologia += f"Los siguientes OID presentan sobreposición {oid_campo} in {str(tuple(list(set(arreglo)))).replace(',', '')}\n"
                                    else:
                                        ErroresTopologia += f"Los siguientes OID presentan sobreposición {oid_campo} in {str(tuple(list(set(arreglo))))}\n"

                ErroresTopologia += f"Para validar los errores topológicos por favor consulte el siguiente dataset {path_dataset}"
            elif paramReglaTop.value == "Huecos":
                arcpy.management.AddRuleToTopology(path_topology, "Must Not Have Gaps (Area)", path_Feature, "", "", "")
                arcpy.management.ValidateTopology(path_topology, "Full_Extent")
                arcpy.management.ExportTopologyErrors(path_topology, path_dataset, "Errores")

                ErroresTopologia = f"#####Validación de topología (Huecos) ######\n"
                for fc in arcpy.ListFeatureClasses(feature_dataset=nombre_dataset):
                    path = os.path.join(arcpy.env.workspace, nombre_dataset, fc)
                    if "Errores" in arcpy.Describe(path).name:
                        Ctd_contar = arcpy.management.GetCount(path)
                        Ctd = int(Ctd_contar.getOutput(0))
                        if Ctd > 1:
                            if "line" in str(arcpy.Describe(path).name):
                                contador += 1
                                ErroresTopologia += f"La capa presenta {Ctd} casos de huecos.\n"

            
            
            
            arcpy.AddWarning(ErroresTopologia)
         ####################################################################
       