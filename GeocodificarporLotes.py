#-------------------------------------------------------------------------------
# Name:        Geocodificar por lotes
# Purpose:
#
# Author:      jescudero
#
# Created:     13/10/2016
# Copyright:   (c) jescudero 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
arcpy.env.overwriteOutput = 1

"""Divide una lista de valores en varias sublistas de un tamaño específico """
def splitList(table, fieldName, size):
    pList = [row[0] for row in arcpy.da.SearchCursor(table, [fieldName])]
    length = len(pList)
    return [pList[i*length/size:(i+1)*length/size] for i in range(size)]

"""Crea una lista de expresiones SQL a partir de una lista de valores y un campo"""
def createExpresions(blocks, fieldName):
    return ["%s >= %s AND %s <= %s" % (fieldName, min(block) , fieldName, max(block) ) for block in blocks]

"""Carga los registros de una tabla a otra usando cursores"""
def insertToTable(inputFC, targetFC, fields):
    insertor = arcpy.da.InsertCursor(targetFC, fields)
    with arcpy.da.SearchCursor(inputFC, fields) as cursor:
        for row in cursor:
            insertor.insertRow(row)
    del insertor

table = r"C:\Users\jescudero\jescudero\Proyectos\EXPERIAN\PruebaConcepto.gdb\ClientesTabla"
clientes = r"C:\Users\jescudero\jescudero\Proyectos\EXPERIAN\PruebaConcepto.gdb\Clientes"
locator = r"\\ecetina\Users\ECETINA\Documents\jescudero\ColombiaHERE_FGDB_2016_Q3.gdb\Compuesto_FGDB_2016_Q3"

def main():

    # Divide la tabla usando el OBJECTID en paquetes de 5 registros
    blocks = splitList(table, "OBJECTID", 5)

    # Crea múltiples expresiones SQL a partir de los bloques generados
    expresions = createExpresions(blocks, "OBJECTID")

    for expresion in expresions:

        # Crea una subtabla temporal aplicando un filtro con la expresion
        tempTable = arcpy.TableToTable_conversion(table, "in_memory", "tempTable", expresion)

        # Geocodifica la subtabla
        tempClientes = arcpy.GeocodeAddresses_geocoding(tempTable, locator, "Street Direccion VISIBLE NONE;Zone Municipio VISIBLE NONE", "in_memory/geocodedAddresses")

        # Carga el resultado en la capa de destino usando cursores
        insertToTable(tempClientes, clientes, ["Direccion", "Municipio", "SHAPE@"])

if __name__ == '__main__':
    main()
