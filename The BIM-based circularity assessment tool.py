from __future__ import print_function

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import ifcopenshell
import ifcopenshell.geom
import math

settings = ifcopenshell.geom.settings()
settings.set(settings.USE_PYTHON_OPENCASCADE, True)

import OCC
from OCC.Display.backend import load_backend

load_backend("qt-pyqt5")
from OCC.Display.SimpleGui import *
from OCC.Core.gp import *
from OCC.Core import Bnd
import OCC.Core.Bnd, OCC.Core.BRepBndLib
from OCC.Display.qtDisplay import qtViewer3d

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.container import BarContainer
import mplcursors

style.use('seaborn')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
from matplotlib.patches import ConnectionPatch
import pandas as pd
import numpy as np

NLSfB_Table3 = pd.read_excel("External database.xlsx", sheet_name="NL-SfB_Tabel 3")
NLSfB_Table1 = pd.read_excel("External database.xlsx", sheet_name="NL-SfB_Tabel 1")
NAAKT_Table = pd.read_excel("External database.xlsx", sheet_name="NAA.K.T")

class IFCInput:
    def __init__(self, ifc_file):
        self.ifc_file = ifc_file

        # Extract status information from IFC file

    def product_status(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        status = []

        for product in products:
            flag = 0
            if product.IsDefinedBy:
                definitions = product.IsDefinedBy
                for definition in definitions:
                    try:
                        if definition.RelatingPropertyDefinition:
                            property_definition = definition.RelatingPropertyDefinition
                            for value in property_definition.HasProperties:
                                if value.Name == "EC_EF000124_Status":
                                    for status_value in value.NominalValue:
                                        status.append(status_value)
                                        flag +=1

                    except:
                        continue
                if flag == 0:
                    for definition in definitions:
                        try:
                            if definition.RelatingPropertyDefinition:
                                property_definition = definition.RelatingPropertyDefinition
                                for value in property_definition.HasProperties:
                                    if value.Name == "Status":
                                        for status_value in value.NominalValue:
                                            status.append(status_value)
                                            flag +=1
                        except:
                            continue
                if flag == 0:
                    status.append("0")
        return status

    # Extract information of connection type from IFC file
    def connection_type(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        connection_type = []

        for product in products:
            flag = 0
            if product.IsDefinedBy:
                definitions = product.IsDefinedBy
                for definition in definitions:
                    try:
                        if definition.RelatingPropertyDefinition:
                            property_definition = definition.RelatingPropertyDefinition
                            for value in property_definition.HasProperties:
                                if value.Name == "EC_EF000124_Connection type":
                                    for connection_value in value.NominalValue:
                                        connection_type.append(connection_value)
                                        flag +=1

                    except:
                        continue
            if flag == 0:
                connection_type.append("Unknown")

        return connection_type

    # Extract information of accessibility level from IFC file
    def accessibility_level(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        accessibility_type = []

        for product in products:
            flag = 0
            if product.IsDefinedBy:
                definitions = product.IsDefinedBy
                for definition in definitions:
                    try:
                        if definition.RelatingPropertyDefinition:
                            property_definition = definition.RelatingPropertyDefinition
                            for value in property_definition.HasProperties:
                                if value.Name == "EC_EFXXXXXX_Accessibility":
                                    for accessibility_value in value.NominalValue:
                                        accessibility_type.append(accessibility_value)
                                        flag +=1

                    except:
                        continue
            if flag == 0:
                accessibility_type.append("Unknown")

        return accessibility_type

    def recycled_percentage(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        recycled_percentage = []

        for product in products:
            flag_1 = 0
            if product.IsDefinedBy:
                definitions = product.IsDefinedBy
                for definition in definitions:
                    try:
                        if definition.RelatingPropertyDefinition:
                            property_definition = definition.RelatingPropertyDefinition
                            for value in property_definition.HasProperties:
                                if value.Name == "EC_EF017158_Percentage recycled material":
                                    for recycled_value in value.NominalValue:
                                        recycled_percentage.append(recycled_value )
                                        flag_1 +=1

                    except:
                        continue
            if flag_1 == 0:
                recycled_percentage.append("0")

        for i in recycled_percentage:
            recycled_percentage = [float(i) for i in recycled_percentage]


        '''
        recycled_value = []
        for value in recycled_percentage:

            value_1  = value.split("_")
            for i in value_1:
                recycled_value.append(float(i))
        '''


        return recycled_percentage

    # Extract quantity information from IFC file
    def product_quantity(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        software = self.ifc_file.by_type("IfcApplication")
        volume = []
        area = []

        for application in software:
            name = application.ApplicationFullName
            if "Revit" in name:
                for product in products:
                    if product.IsDefinedBy:
                        flag = 0
                        flag_1 = 0
                        definitions = product.IsDefinedBy
                        for definition in definitions:
                            try:
                                if definition.RelatingPropertyDefinition:
                                    property_definition = definition.RelatingPropertyDefinition
                                    if property_definition.is_a("IfcElementQuantity"):
                                        for quantity in property_definition.Quantities:
                                            if quantity.is_a("IfcQuantityVolume"):
                                                if quantity.Name == "NetVolume":
                                                    flag = flag + 1
                                                    volume.append(quantity.VolumeValue)
                                                    break
                            except:
                                continue

        for application in software:
            name = application.ApplicationFullName
            if "Revit" in name:
                for product in products:
                    if product.IsDefinedBy:
                        flag_1 = 0
                        definitions = product.IsDefinedBy
                        for definition in definitions:
                            try:
                                if definition.RelatingPropertyDefinition:
                                    property_definition = definition.RelatingPropertyDefinition
                                    if property_definition.is_a("IfcElementQuantity"):
                                        for quantity in property_definition.Quantities:
                                            if quantity.is_a("IfcQuantityArea"):
                                                if quantity.Name == "NetSideArea" or quantity.Name == "NetArea" \
                                                        or quantity.Name == "CrossSectionArea":
                                                    flag_1 = flag_1 + 1
                                                    area.append(quantity.AreaValue)
                                                    break
                            except:
                                continue


                        if flag == 0:
                            volume.append(0)
                        if flag_1 == 0:
                            area.append(0)

            elif "SketchUp" or "sketchup" in name:
                for product in products:
                    if product.IsDefinedBy:
                        flag = 0

                        definitions = product.IsDefinedBy
                        for definition in definitions:
                            try:
                                if definition.RelatingPropertyDefinition:
                                    property_definition = definition.RelatingPropertyDefinition
                                    if 'IfcPropertySet' == property_definition.is_a():
                                        for quantity in property_definition.HasProperties:
                                            if 'IfcPropertySingleValue' == quantity.is_a():
                                                if quantity.Name == 'NetVolume':
                                                    flag += 1
                                                    volume.append(quantity.NominalValue.wrappedValue)


                                                    break
                            except:
                                continue
                        if flag == 0:
                            volume.append(0)

        return volume, area

    def product_guids(self):
        guids = []
        products = self.ifc_file.by_type("IfcBuildingElement")
        for product in products:
            guids.append(str(product.GlobalId))
        return guids

    def product_weight(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        # a list to hold areas information of all building elements

        product_mass = []
        # a list to hold material name information of all material
        materialss = []

        ETIM_weight_total = []
        ETIM_material_total = []


        # first try to extract weight information which is stored based on ETIM standard
        for product in products:
            flag = 0
            if product.IsDefinedBy:
                definitions = product.IsDefinedBy
                for definition in definitions:
                    # first extract information based on ETIM standard
                    try:
                        if definition.RelatingPropertyDefinition:
                            property_definition = definition.RelatingPropertyDefinition
                            for value in property_definition.HasProperties:
                                if value.Name == "EC_EF000167_Weight":
                                    for weight_value in value.NominalValue:
                                        ETIM_weight = []
                                        ETIM_weight.append(weight_value)
                                        for weight in ETIM_weight:
                                            product_mass.append(weight)
                                            flag += 1
                    except:
                        continue
                if flag == 0:
                    product_weight = 0
                    for definition in definitions:
                        try:
                            if definition.RelatingPropertyDefinition:
                                property_definition = definition.RelatingPropertyDefinition
                                if property_definition.is_a("IfcElementQuantity"):
                                    for quantity in property_definition.Quantities:
                                        try:
                                            if quantity.is_a("IfcQuantityArea"):
                                                if quantity.Name == "NetSideArea" or quantity.Name == "NetArea" \
                                                        or quantity.Name == "CrossSectionArea":
                                                    area = []
                                                    area.append(quantity.AreaValue)
                                                    if product.HasAssociations:
                                                        associations = product.HasAssociations
                                                        for association in associations:
                                                            if association.is_a(
                                                                    "IfcRelAssociatesMaterial"):
                                                                associatesmaterial = association.RelatingMaterial
                                                                try:
                                                                    if associatesmaterial.is_a(
                                                                            "IfcMaterialLayerSetUsage"):
                                                                        materiallayers = associatesmaterial.ForLayerSet
                                                                        if materiallayers.is_a(
                                                                                "IfcMaterialLayerSet"):
                                                                            if materiallayers.MaterialLayers:
                                                                                for layer in materiallayers.MaterialLayers:
                                                                                    tickness = []
                                                                                    tickness.append(
                                                                                        layer.LayerThickness)
                                                                                    for material in layer.Material:
                                                                                        density= []
                                                                                        code = (material.split('_',2))[1]
                                                                                        code = code.lower()
                                                                                        material_density = \
                                                                                            NLSfB_Table3.loc[
                                                                                                NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                                                                                        if math.isnan(
                                                                                                material_density) == True:
                                                                                            material_density = 1000
                                                                                        density.append(material_density)
                                                                                        for area_1 in area:
                                                                                            for tickness_1 in tickness:
                                                                                                for density_1 in density:
                                                                                                    material_weight = (area_1 * tickness_1*density_1) / 1000
                                                                                                    product_weight+= material_weight



                                                                except:
                                                                    continue


                                        except:
                                            continue

                        except:
                            continue
                    if product_weight != 0:
                        product_mass.append(product_weight)
                    else:
                        for definition in definitions:
                            flag_1 = 0
                            try:
                                if definition.RelatingPropertyDefinition:
                                    property_definition = definition.RelatingPropertyDefinition
                                    if property_definition.is_a("IfcElementQuantity"):
                                        for quantity in property_definition.Quantities:
                                            try:
                                                if quantity.is_a(
                                                        "IfcQuantityVolume"):
                                                    if quantity.Name == "NetVolume":
                                                        entityvolume = []
                                                        entityvolume.append(
                                                            quantity.VolumeValue)

                                                        if product.HasAssociations:
                                                            associations = product.HasAssociations
                                                            for association in associations:
                                                                if association.is_a(
                                                                        "IfcRelAssociatesMaterial"):
                                                                    associatesmaterial = association.RelatingMaterial
                                                                    try:
                                                                        if associatesmaterial.is_a(
                                                                                "IfcMaterial"):
                                                                            material = associatesmaterial.Name
                                                                            density = []
                                                                            code = (material.split('_', 2))[1]
                                                                            code = code.lower()
                                                                            material_density = \
                                                                                NLSfB_Table3.loc[
                                                                                    NLSfB_Table3[
                                                                                        'Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[
                                                                                    0]
                                                                            if math.isnan(
                                                                                    material_density) == True:
                                                                                material_density = 1000
                                                                            density.append(material_density)
                                                                            for volume in entityvolume:
                                                                                for density_1 in density:
                                                                                    product_weight = volume * density_1
                                                                                    flag_1 +=1



                                                                    except:
                                                                        continue
                                            except:
                                                continue
                            except:
                                continue
                        product_mass.append(product_weight)

        for i in product_mass:
            product_mass = [float(i) for i in product_mass]


        return   product_mass

    def materials(self):
        materials = []
        #IfcProduct include IfcBuilding, IfcSite and etc.
        products = self.ifc_file.by_type("IfcBuildingElement")
        for product in products:
            flag = 0
            try:
                if product.IsDefinedBy:
                    definitions = product.IsDefinedBy
                    for definition in definitions:
                        # first extract information based on ETIM standard
                        try:
                            if definition.RelatingPropertyDefinition:
                                property_definition = definition.RelatingPropertyDefinition
                                for value in property_definition.HasProperties:
                                    if value.Name == "EC_EF002169_Material":
                                        for material_value in value.NominalValue:
                                            materials.append(material_value)
                                            flag += 1

                        except:
                            continue
            except:
                continue
            if flag == 0:
                try:
                    if product.HasAssociations:
                        associations = product.HasAssociations
                        for association in associations:
                            if association.is_a("IfcRelAssociatesMaterial"):
                                associatesmaterial = association.RelatingMaterial
                                try:
                                    if associatesmaterial.is_a("IfcMaterialLayerSetUsage"):
                                        materiallayers = associatesmaterial.ForLayerSet
                                        if materiallayers.is_a(
                                                "IfcMaterialLayerSet"):
                                            if materiallayers.MaterialLayers:
                                                for layer in materiallayers.MaterialLayers:
                                                    for material in layer.Material:
                                                        materials.append(material)
                                                        flag += 1
                                except:
                                    continue
                except:
                    continue
                if flag == 0:
                    try:
                        if product.HasAssociations:
                            associations = product.HasAssociations
                            for association in associations:
                                if association.is_a("IfcRelAssociatesMaterial"):
                                    associatesmaterial = association.RelatingMaterial
                                    try:
                                        if associatesmaterial.is_a("IfcMaterial"):
                                            material_name = associatesmaterial.Name
                                            materials.append(material_name)
                                            flag += 1
                                    except:
                                        continue
                    except:
                        continue
                if flag == 0:
                    materials.append("Unknown")

        return materials

    def material_properties(self):
        products = self.ifc_file.by_type("IfcBuildingElement")
        # a list to hold areas information of all building elements
        areas = []
        # a list to hold volumes information of all building elements
        volumes = []
        # a list to hold material name information of all material
        materialss = []
        # a list to hold status information of all materials
        statuss = []
        # a list to hold guid infomration of all materials. For example, the same guid of a wall will be extracted twice if
        # the wall involve two different materials
        guidss = []
        # a list to hold assembly code (NL-SfB Table 1) of all materials
        assembly_codes = []
        weights = []

        ETIM_guid_total = []
        ETIM_status_total = []
        ETIM_weight_total = []
        ETIM_material_total = []
        ETIM_code_total = []

        # first try to extract information which based on ETIM Standard

        for product in products:
            guids = []
            guids.append(str(product.GlobalId))
            for rel in product.HasAssociations:
                if rel.is_a("IfcRelAssociatesClassification"):
                    codes = []
                    codes.append(rel.RelatingClassification.ItemReference)
                    if product.IsDefinedBy:
                        definitions = product.IsDefinedBy
                        for definition in definitions:
                            try:
                                if definition.RelatingPropertyDefinition:
                                    property_definition = definition.RelatingPropertyDefinition
                                    for value in property_definition.HasProperties:
                                        if value.Name == "Status":
                                            for status_value in value.NominalValue:
                                                status_ETIM = []
                                                status_ETIM.append(status_value)
                                                # print(ETIM_status)
                                                if definition.RelatingPropertyDefinition:
                                                    property_definition = definition.RelatingPropertyDefinition
                                                    for value in property_definition.HasProperties:
                                                        if value.Name == "EC_EF000167_Weight":
                                                            for weight_value in value.NominalValue:
                                                                ETIM_weight = []
                                                                ETIM_weight.append(weight_value)
                                                                if definition.RelatingPropertyDefinition:
                                                                    property_definition = definition.RelatingPropertyDefinition
                                                                    for value in property_definition.HasProperties:
                                                                        if value.Name == "EC_EF002169_Material":
                                                                            for material_value in value.NominalValue:
                                                                                ETIM_material = []
                                                                                ETIM_material.append(material_value)
                                                                                for value in status_ETIM:
                                                                                    ETIM_status_total.append(value)
                                                                                for weight in ETIM_weight:
                                                                                    ETIM_weight_total.append(weight)
                                                                                for guid in guids:
                                                                                    ETIM_guid_total.append(guid)
                                                                                for material in ETIM_material:
                                                                                    ETIM_material_total.append(material)
                                                                                for code in codes:
                                                                                    ETIM_code_total.append (code)
                                                                                break
                            # if a object is not apply for ETIM standard, the program will try to extract information based on normal revit standard (normally in design phases)
                            except:
                                try:
                                    if definition.RelatingPropertyDefinition:
                                        property_definition = definition.RelatingPropertyDefinition
                                        if property_definition.is_a("IfcElementQuantity"):
                                            for quantity in property_definition.Quantities:
                                                try:
                                                    if quantity.is_a("IfcQuantityArea"):
                                                        if quantity.Name == "NetSideArea" or quantity.Name == "NetArea" \
                                                                or quantity.Name == "CrossSectionArea":
                                                            area = []
                                                            area.append(quantity.AreaValue)
                                                            if product.IsDefinedBy:
                                                                definitions = product.IsDefinedBy
                                                                for definition in definitions:
                                                                    try:
                                                                        if definition.RelatingPropertyDefinition:
                                                                            property_definition = definition.RelatingPropertyDefinition
                                                                            if property_definition.is_a(
                                                                                    "IfcElementQuantity"):
                                                                                for quantity in property_definition.Quantities:
                                                                                    try:
                                                                                        if quantity.is_a(
                                                                                                "IfcQuantityVolume"):
                                                                                            if quantity.Name == "NetVolume":
                                                                                                entityvolume = []
                                                                                                entityvolume.append(
                                                                                                    quantity.VolumeValue)
                                                                                                if product.IsDefinedBy:
                                                                                                    definitions = product.IsDefinedBy
                                                                                                    for definition in definitions:
                                                                                                        try:
                                                                                                            if definition.RelatingPropertyDefinition:
                                                                                                                property_definition = definition.RelatingPropertyDefinition
                                                                                                                for value in property_definition.HasProperties:
                                                                                                                    if value.Name == "Status":
                                                                                                                        for status_value in value.NominalValue:
                                                                                                                            status = []
                                                                                                                            status.append(
                                                                                                                                status_value)
                                                                                                                            if product.HasAssociations:
                                                                                                                                associations = product.HasAssociations
                                                                                                                                for association in associations:
                                                                                                                                    if association.is_a(
                                                                                                                                            "IfcRelAssociatesMaterial"):
                                                                                                                                        associatesmaterial = association.RelatingMaterial
                                                                                                                                        try:
                                                                                                                                            if associatesmaterial.is_a(
                                                                                                                                                    "IfcMaterialLayerSetUsage"):
                                                                                                                                                materiallayers = associatesmaterial.ForLayerSet
                                                                                                                                                if materiallayers.is_a(
                                                                                                                                                        "IfcMaterialLayerSet"):
                                                                                                                                                    if materiallayers.MaterialLayers:
                                                                                                                                                        for layer in materiallayers.MaterialLayers:
                                                                                                                                                            tickness = []
                                                                                                                                                            tickness.append(
                                                                                                                                                                layer.LayerThickness)
                                                                                                                                                            for material in layer.Material:
                                                                                                                                                                materialss.append(
                                                                                                                                                                    material)
                                                                                                                                                            for area_1 in area:
                                                                                                                                                                areas.append(
                                                                                                                                                                    area_1)
                                                                                                                                                                for tickness_1 in tickness:
                                                                                                                                                                    volume = (
                                                                                                                                                                                     area_1 * tickness_1) / 1000
                                                                                                                                                                    volumes.append(
                                                                                                                                                                        volume)
                                                                                                                                                            for status_1 in status:
                                                                                                                                                                statuss.append(
                                                                                                                                                                    (
                                                                                                                                                                        status_1))
                                                                                                                                                            for guid in guids:
                                                                                                                                                                guidss.append(
                                                                                                                                                                    guid)
                                                                                                                                                            for code in codes:
                                                                                                                                                                assembly_codes.append(
                                                                                                                                                                    code)

                                                                                                                                                        continue

                                                                                                                                            if associatesmaterial.is_a(
                                                                                                                                                    "IfcMaterial"):
                                                                                                                                                material = associatesmaterial.Name
                                                                                                                                                materialss.append(
                                                                                                                                                    material)
                                                                                                                                                for volume in entityvolume:
                                                                                                                                                    volumes.append(
                                                                                                                                                        volume)
                                                                                                                                                for status_1 in status:
                                                                                                                                                    statuss.append(
                                                                                                                                                        (
                                                                                                                                                            status_1))
                                                                                                                                                for guid in guids:
                                                                                                                                                    guidss.append(
                                                                                                                                                        guid)
                                                                                                                                                for code in codes:
                                                                                                                                                    assembly_codes.append(
                                                                                                                                                        code)
                                                                                                                                                for area_1 in area:
                                                                                                                                                    areas.append(
                                                                                                                                                        area_1)
                                                                                                                                                break

                                                                                                                                        except:
                                                                                                                                            continue

                                                                                                        except:
                                                                                                            continue
                                                                                    except:
                                                                                        continue
                                                                    except:
                                                                        continue


                                                except:
                                                    continue

                                except:
                                    continue

        for i in ETIM_weight_total:
            ETIM_weight_total = [float(i) for i in ETIM_weight_total]

        return materialss, volumes, statuss, guidss, assembly_codes, areas, ETIM_status_total, ETIM_guid_total, ETIM_weight_total, ETIM_material_total, ETIM_code_total

guid_selection = None

class ProductViewer(qtViewer3d):
    def __init__(self, *args):
        qtViewer3d.__init__(self, *args)
        self.objects = {}

    @staticmethod
    def Hash(shape):
        return shape.HashCode(1 << 30)

    displayed_shapes = {}

    def Show(self, key, shape, color=None):
        r = float(100) / 255
        g = float(100) / 255
        b = float(100) / 255
        self.objects[ProductViewer.Hash(shape)] = key
        qclr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais = self._display.DisplayColoredShape(shape, qclr)
        self.displayed_shapes[key] = ais
        self._display.FitAll()

    def non_color(self, key):
        r = float(100) / 255
        g = float(100) / 255
        b = float(100) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def clr_Arrow4(self, key):
        # r = float(86) / 255
        r = float(41) / 255
        # g = float(110) / 255
        g = float(77) / 255
        # b = float(61) / 255
        b = float(50) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def clr_Arrow3(self, key):
        r = float(88) / 255
        g = float(164) / 255
        b = float(176) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def clr_Arrow5(self, key):
        r = float(108) / 255
        g = float(105) / 255
        b = float(141) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def clr_Arrow1(self, key):
        # r = float(227) / 255
        r = float(190) / 255
        # g = float(150) / 255
        g = float(100) / 255
        # b = float(149) / 255
        b = float(100) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def clr_Arrow2(self, key):
        r = float(110) / 255
        #r = float(148) / 255
        #g = float(41) / 255
        g = float(25) / 255
        #b = float(17) / 255
        b = float(17) / 255
        ais = self.displayed_shapes[key]
        clr = OCC.Core.Quantity.Quantity_Color(r, g, b, OCC.Core.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)

    def erase_shape(self):
        self._display.EraseAll()

    # *args: no fixed input
    def mouseReleaseEvent(self, *args):
        # Process selection by parent class
        qtViewer3d.mouseReleaseEvent(self, *args)
        if self._display.selected_shapes:
            global guid_selection
            global selected_shapes
            selected_shapes = self._display.selected_shapes

            for x in self._display.selected_shapes:
                guid_selection = self.objects[ProductViewer.Hash(x)]

class Ui_Login(QtWidgets.QMainWindow):
    switch_window1 = QtCore.pyqtSignal()
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self):
        super(Ui_Login, self).__init__()
        loadUi("loginin.ui", self)
        self.renovated.clicked.connect(self.gotorenovatedscreen)
        self.New_demolished.clicked.connect(self.gotonewscreen)

        png1 = QPixmap("Univeristy of Twente")
        self.label_2.setPixmap(png1)
        self.label_2.setScaledContents(True)

        png2 = QPixmap("digiGO.jpg")
        self.label_3.setPixmap(png2)
        self.label_3.setScaledContents(True)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        self.widget10.setLayout(layout)
        layout.addWidget(self.canvas)

        style_new = "Simple, tail_width={}, head_width={}, head_length={}".format(10, 20, 10)

        kw_new = dict(arrowstyle=style_new, color=[float(227) / 255, float(150) / 255, float(149) / 255])
        a1 = patches.FancyArrowPatch((0.5, 1), (0.5, 0.75), **kw_new)

        # draw arrow 4

        style_reused = "Simple, tail_width={}, head_width={}, head_length={}".format(10, 20, 10)

        kw_reused = dict(arrowstyle=style_reused, color=[float(86) / 255, float(110) / 255, float(61) / 255])
        a4 = patches.FancyArrowPatch((0.45, 0.41), (0.45, 0.59), connectionstyle="arc3,rad=1", **kw_reused)

        # draw arrow 2

        style_demolished = "Simple, tail_width={}, head_width={}, head_length={}".format(10, 20, 10)

        kw_demolished = dict(arrowstyle=style_demolished, color=[float(148) / 255, float(41) / 255, float(17) / 255])
        a2 = patches.FancyArrowPatch((0.5, 0.3), (0.5, 0.05), **kw_demolished)

        # draw arrow 3

        style_reuse = "Simple, tail_width={}, head_width={}, head_length={}".format(10, 20, 10)

        kw_reused_old = dict(arrowstyle=style_reuse, color=[float(88) / 255, float(164) / 255, float(176) / 255])
        a3 = patches.FancyArrowPatch((0.05, 0.5), (0.3, 0.5), **kw_reused_old)

        # draw arrow 5

        style_recovery = "Simple, tail_width={}, head_width={}, head_length={}".format(10, 20, 10)

        kw_recovery_in_another_building = dict(arrowstyle=style_recovery,
                                               color=[float(108) / 255, float(105) / 255, float(141) / 255])
        a5 = patches.FancyArrowPatch((0.7, 0.5), (0.95, 0.5), **kw_recovery_in_another_building)

        plt.gca().add_patch(a1)
        plt.gca().add_patch(a2)
        plt.gca().add_patch(a4)
        plt.gca().add_patch(a3)
        plt.gca().add_patch(a5)
        plt.axis('off')
        plt.tight_layout()
        plt.plot([0.35, 0.65, 0.65, 0.5, 0.35, 0.35], [0.35, 0.35, 0.55, 0.7, 0.55, 0.35], linewidth=1, color="k")
        plt.close()

    def gotorenovatedscreen(self):
        self.switch_window1.emit()

    def gotonewscreen(self):
        self.switch_window2.emit()

# creat a function for preseneting material's subcategory of each category
def materialdetails(materialdic):
    text_sum = ""
    value_sum = 0
    for value in materialdic.values():
        value_sum += value
    for key, value in materialdic.items():
        text = str(key) + ":" + str((format(value / value_sum, ".2%")))
        text_sum = text_sum + "\n" + text

    return text_sum

def draw_five_arrows(New_value, Existing_value, Demolished_value, Reuse_from_old_building,
                     Recovery_in_another_building):
    width_new = (New_value / (
            New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building)) * 30
    width_reused = (Existing_value / (
            New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building)) * 30
    width_demolished = (Demolished_value / (
            New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building)) * 30
    width_reused_old_building = (Reuse_from_old_building / (
            New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building)) * 30

    width_recovery_another_building = (Recovery_in_another_building / (
            New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building)) * 30

    head_width_new = width_new * 3
    head_width_reused = width_reused * 3
    head_width_demolished = width_demolished * 3
    head_width_reused_old = width_reused_old_building * 3
    head_width_recovery_another = width_recovery_another_building * 3

    head_length = 20
    plt.xlim((0, 1))
    plt.ylim((0, 1))

    ######################
    # if the value of one arrow is zero, will not draw it and present its precentage of bio/techinical materials
    # draw arrow 1
    if New_value <= 0:
        style_new = "Simple, tail_width={}, head_width={}, head_length={}".format(0, 0, 0)
    else:
        style_new = "Simple, tail_width={}, head_width={}, head_length={}".format(width_new, head_width_new,
                                                                                  head_length)

    kw_new = dict(arrowstyle=style_new, color=[float(227) / 255, float(150) / 255, float(149) / 255])
    a1 = patches.FancyArrowPatch((0.5, 1), (0.5, 0.75), **kw_new)

    # draw arrow 4
    if Existing_value <= 0:
        style_reused = "Simple, tail_width={}, head_width={}, head_length={}".format(0, 0, 0)
    else:
        style_reused = "Simple, tail_width={}, head_width={}, head_length={}".format(width_reused,
                                                                                     head_width_reused,
                                                                                     head_length)

    kw_reused = dict(arrowstyle=style_reused, color=[float(86) / 255, float(110) / 255, float(61) / 255])
    a4 = patches.FancyArrowPatch((0.45, 0.41), (0.45, 0.59), connectionstyle="arc3,rad=1", **kw_reused)

    # draw arrow 2
    if Demolished_value <= 0:
        style_demolished = "Simple, tail_width={}, head_width={}, head_length={}".format(0, 0, 0)
    else:
        style_demolished = "Simple, tail_width={}, head_width={}, head_length={}".format(width_demolished,
                                                                                         head_width_demolished,
                                                                                         head_length)

    kw_demolished = dict(arrowstyle=style_demolished, color=[float(148) / 255, float(41) / 255, float(17) / 255])
    a2 = patches.FancyArrowPatch((0.5, 0.3), (0.5, 0.05), **kw_demolished)

    # draw arrow 3
    if Reuse_from_old_building <= 0:
        style_reuse = "Simple, tail_width={}, head_width={}, head_length={}".format(0, 0, 0)
    else:
        style_reuse = "Simple, tail_width={}, head_width={}, head_length={}".format(width_reused_old_building,
                                                                                    head_width_reused_old,
                                                                                    head_length)

    kw_reused_old = dict(arrowstyle=style_reuse, color=[float(88) / 255, float(164) / 255, float(176) / 255])
    a3 = patches.FancyArrowPatch((0.05, 0.5), (0.3, 0.5), **kw_reused_old)

    # draw arrow 5
    if Recovery_in_another_building <= 0:
        style_recovery = "Simple, tail_width={}, head_width={}, head_length={}".format(0, 0, 0)
    else:
        style_recovery = "Simple, tail_width={}, head_width={}, head_length={}".format(
            width_recovery_another_building,
            head_width_recovery_another,
            head_length)

    kw_recovery_in_another_building = dict(arrowstyle=style_recovery,
                                           color=[float(108) / 255, float(105) / 255, float(141) / 255])
    a5 = patches.FancyArrowPatch((0.7, 0.5), (0.95, 0.5), **kw_recovery_in_another_building)

    plt.gca().add_patch(a1)
    plt.gca().add_patch(a2)
    plt.gca().add_patch(a4)
    plt.gca().add_patch(a3)
    plt.gca().add_patch(a5)
    plt.axis('off')
    plt.tight_layout()
    plt.plot([0.35, 0.65, 0.65, 0.5, 0.35, 0.35], [0.35, 0.35, 0.55, 0.7, 0.55, 0.35], linewidth=1, color="k")
    plt.close()
    # plt.text(0.5,0.5,"100%",fontdict=None)


class Ui_New_demolihsed(QtWidgets.QMainWindow):
    pass

class Ui_Renovation(QtWidgets.QMainWindow):
    switch_window4 = QtCore.pyqtSignal()
    switch_window5 = QtCore.pyqtSignal()

    def __init__(self):

        super(Ui_Renovation, self).__init__()
        loadUi("Circularity assessment with disassembility potential.ui", self)
        self.setWindowTitle("Circularity Assessment for renovation project")
        self.showMaximized()

        self.materialwindow_NLSfB = Ui_Material_window_NLSfB()
        self.materialwindow_NAAKT = Ui_Material_window_NAAKT()

        # configure "OpenIFCFile" functionality
        self.OpenIFCFile.triggered.connect(self.open_IFC)


        # configure "OpenIFCFile_Existing" functionality
        self.OpenIFCFile_1.triggered.connect(self.open_IFC_1)

        # configure "Help"functionality
        self.menuHelp.triggered.connect(self.help)

        # configure "Exit" functionality
        self.Exit.triggered.connect(self.close_application)

        # configure "Save" functionality
        self.Save.triggered.connect(self.save_plots)

        png1 = QPixmap("Univeristy of Twente")
        self.ImageLabel2.setPixmap(png1)
        self.ImageLabel2.setScaledContents(True)
        # attch pictures of material type (eight in total)


        png2 = QPixmap("DP potential.jpg")
        self.ImageLabel3.setPixmap(png2)
        self.ImageLabel3.setScaledContents(True)

        # configure back button functionability
        self.back.clicked.connect(self.backtomainwindow)
        self.Material_analysis.clicked.connect(self.materialperformance)
        # self.Material_analysis.clicked.connect(self.materialoverview)
        # self.Material_analysis.clicked.connect(self.entityperformance)

        # configure "Viewer" functionality

        self.canvas1 = ProductViewer(self)
        layout1 = QVBoxLayout()
        layout1.setContentsMargins(0, 0, 0, 0)
        layout1.addWidget(self.canvas1)
        self.widgetViewer.setLayout(layout1)

        self.canvas10 = ProductViewer(self)
        layout2 = QVBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget(self.canvas10)
        self.widgetViewer_2.setLayout(layout2)

        # configure arrow functionability
        # configure arrow filter
        self.pushButton_1.clicked.connect(self.new_materials)
        self.pushButton_2.clicked.connect(self.waste)
        self.pushButton_3.clicked.connect(self.reused_oldbuilding)
        self.pushButton_4.clicked.connect(self.reused_samebuilding)
        self.pushButton_5.clicked.connect(self.recovery_anotherbuilding)
        self.showproperties.clicked.connect(self.getProperties)

    def backtomainwindow(self):
        self.switch_window4.emit()

    def getProperties(self):
        ifc_file = ifcopenshell.open((self.file_path)[0])
        product_weight = IFCInput(ifc_file).product_weight()
        guid_identical = IFCInput(ifc_file).product_guids()

        status = IFCInput(ifc_file).product_status()
        status = list(map(lambda x: x.replace('EV000001_New', '1'), status))
        status = list(map(lambda x: x.replace('EV000004_Reused in the same building', '4'), status))

        materials = IFCInput(ifc_file).material_properties()[0]

        volumes = IFCInput(ifc_file).product_quantity()[0]
        guids = IFCInput(ifc_file).material_properties()[3]

        materials_ETIM = IFCInput(ifc_file).material_properties()[9]
        guid_ETIM = IFCInput(ifc_file).material_properties()[7]

        materials_total = materials + materials_ETIM
        guid_total = guids + guid_ETIM

        ifc_file_existing = ifcopenshell.open((self.file_path_1)[0])
        weight_existing = IFCInput(ifc_file_existing).product_weight()
        materials_existing = IFCInput(ifc_file_existing).material_properties()[0]
        status_existing = IFCInput(ifc_file_existing).product_status()
        guids_existing = IFCInput(ifc_file_existing).material_properties()[3]
        guid_identical_existing = IFCInput(ifc_file_existing).product_guids()
        volumes_existing = IFCInput(ifc_file_existing).product_quantity()[0]

        material_standard = self.standard.currentText()


        def showproperties(guid_material, guid_material_existing):
            status = IFCInput(ifc_file).product_status()
            connection_type = IFCInput(ifc_file).connection_type()
            accessibility_level = IFCInput(ifc_file).accessibility_level()
            recycled_value = IFCInput(ifc_file).recycled_percentage()

            connection_type_existing = IFCInput(ifc_file_existing).connection_type()
            accessibility_level_existing = IFCInput(ifc_file_existing).accessibility_level()
            # create dictionary of holding the information of guid and its volume in two IFC files (new and existing)
            guid_quantity = {}
            if all (value == 0 for value in product_weight):
                for key, value in zip(guid_identical, volumes):
                    guid_quantity[key] = str(round(value, 2)) + ' m3'
            else:
                for key, value in zip(guid_identical, product_weight):
                    guid_quantity[key] = str(round(value, 2)) + ' Kg'


            guid_quantity_existing = {}
            if all (value == 0 for value in weight_existing):
                for key, value in zip(guid_identical_existing, volumes_existing):
                    guid_quantity_existing[key] = str(round(value, 2)) + ' m3'
            else:
                for key, value in zip(guid_identical_existing, weight_existing):
                    guid_quantity_existing[key] = str(round(value, 2)) + ' Kg'

            guid_connection_type = {}
            for key, value in zip(guid_identical, connection_type):
                #value = value.split('_', 2)[1]
                guid_connection_type[key] = value


            guid_accessibility_type = {}
            for key, value in zip (guid_identical, accessibility_level):
                #value = value.split('_', 2)[1]
                guid_accessibility_type[key] = value

            guid_recycled = {}
            for key, value in zip (guid_identical, recycled_value):
                #value = value.split('_', 2)[1]
                guid_recycled[key] = value

            # create dictionary of holding the information of guid and its status in two IFC files (new and existing)
            guid_status = {}
            for key, value in zip(guid_identical, status):
                if value == "1":
                    guid_status[key] = "New"
                if value == "2":
                    guid_status[key] = "Waste"
                if value == "3":
                    guid_status[key] = "Reused from an old building"
                if value == "4":
                    guid_status[key] = "Reuse in the same building"
                if value == "5":
                    guid_status[key] = "Recovery in another building"

            guid_status_existing = {}
            for key, value in zip(guid_identical_existing, status_existing):
                if value == "1":
                    guid_status_existing[key] = "New"
                if value == "2":
                    guid_status_existing[key] = "Waste"
                if value == "3":
                    guid_status_existing[key] = "Reused from an old building"
                if value == "4":
                    guid_status_existing[key] = "Reuse in the same building"
                if value == "5":
                    guid_status_existing[key] = "Recovery in another building"


            # comparing guid of the selected component first with new ifc file, and if not same guid is found, change to existing ifc file. otherwise, set "unknown"
            try:
                material = guid_material[guid_selection]
            except:
                try:
                    material = guid_material_existing[guid_selection]
                except:
                    material = "Unknown"


            try:
                connection = guid_connection_type[guid_selection]
            except:
                connection = "Unknown"

            try:
                accessibility = guid_accessibility_type[guid_selection]
            except:
                accessibility = "Unknown"


            try:
                weight = guid_quantity[guid_selection]

            except:
                try:
                    weight = guid_quantity_existing[guid_selection]

                except:
                    weight = "Unknown"


            try:
                status = guid_status[guid_selection]
            except:
                try:
                    status = guid_status_existing[guid_selection]
                except:
                    status = "Unknown"

            try:
                recycled_value_1 = guid_recycled[guid_selection]
            except:
                recycled_value_1 = "Unknown"

            if all (i == 0.0 for i in recycled_value):
                recycled_value_1 = "Unknown"

            self.Circular_materials.setText("%s" % str(recycled_value_1))

            self.Global_ID.setText("%s" % guid_selection)

            self.Material.setText("%s" % (material))

            self.volume.setText("%s" % (str(weight)))

            self.status.setText("%s" % (str(status)))

            self.Connection_type.setText(("%s" % connection))

            self.Accessibility_level.setText("%s" % accessibility)

            # plus renewable materials later

            if connection == "EV003046_Glue" or connection == "EV001391 _cast-in-situ concrete":
                connection_score = 0.1
            elif connection == "EV020482_Bolt and Nut Connection":
                connection_score = 0.8
            elif connection == 'Unknown':
                connection_score = 0.1
            else:
                connection_score = 0.1

            if accessibility == "EVXXXXX2_Accessible with additional actions that do not cause damage":
                accessibility_score = 0.8
            elif accessibility == "EVXXXXX3_Accessible with additional actions with fully repairable damage":
                accessibility_score = 0.6
            elif accessibility == 'Unknown':
                accessibility_score = 0.1
            else:
                accessibility_score = 0.1


            if all (value == "Unknown" for value in connection_type) and all (value == "Unknown" for value in accessibility_level):
                disassembility_potential = "Unknown"
            else:
                disassembility_potential = round(2/(1/connection_score + 1/accessibility_score),2)

            self.Disassembility_potential_2.setText("%s" % str(disassembility_potential))

            if status == "New":
                try:
                    material_score = recycled_value_1 * 0.25
                except:
                    material_score = 0
            elif status == "Waste":
                material_score = 0
            elif status == "Reused from an old building":
                material_score = 0.5
            elif status == "Reuse in the same building":
                material_score = 1
            elif status == "Recovery in another building":
                material_score = 0.5
            else:
                material_score = "Unknown"


            if all (value == "Unknown" for value in connection_type) and all (value == "Unknown" for value in accessibility_level):
                try:
                    total_value = round(material_score , 2)
                except:
                    total_value = "Unknown"
            else:
                try:
                    total_value = round((0.5 * material_score + 0.5 * disassembility_potential), 2)
                except:
                    total_value = "Unknown"

            self.Material_Circularity.setText("%s" % str(material_score))

            self.Overall_value_3.setText("%s" % str(total_value))



        if material_standard == "NL-SfB Table 3":
            material_category = []
            for i in materials_total:
                try:
                    code = (i.split('_', 2))[1]
                    code = code.lower()
                    material_subcategory = \
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'text_NL-SfB_en'].iloc[0]
                    material_category.append(material_subcategory)
                except:
                    material_category.append(" ")


            material_category_existing = []
            for i in materials_existing:
                try:
                    code = (i.split('_', 2))[1]
                    code = code.lower()
                    material_subcategory = \
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'text_NL-SfB_en'].iloc[0]
                    material_category_existing.append(material_subcategory)
                except:
                    material_category_existing.append(" ")

            # create dictionary of holding the information of guid and its materials in two IFC files (new and existing)
            guid_material = {}
            for key, value1, value2 in zip(guid_total, materials_total, material_category):
                if key in guid_material:
                    guid_material[key] = guid_material[key] + '\n' + str(value1) + ' (' + str(value2) + ')'
                else:
                    guid_material[key] = str(value1) + ' (' + str(value2) + ')'


            guid_material_existing = {}
            for key, value1, value2 in zip(guids_existing, materials_existing, material_category_existing):
                if key in guid_material_existing:
                    guid_material_existing[key] = guid_material_existing[key] + '\n' + str(value1) + ' (' + str(
                        value2) + ')'
                else:
                    guid_material_existing[key] = str(value1) + ' (' + str(value2) + ')'


            showproperties(guid_material, guid_material_existing)


        else:
            # create dictionary of holding the information of guid and its materials in two IFC files (new and existing)
            guid_material = {}
            for key, value1 in zip(guid_total, materials_total):
                if key in guid_material:
                    guid_material[key] = guid_material[key] + '\n' + str(value1)
                else:
                    guid_material[key] = str(value1)

            guid_material_existing = {}
            for key, value1 in zip(guids_existing, materials_existing):
                if key in guid_material_existing:
                    guid_material_existing[key] = guid_material_existing[key] + '\n' + str(value1)
                else:
                    guid_material_existing[key] = str(value1)

            showproperties(guid_material, guid_material_existing)

    def materialperformance(self):
        material_standard = self.standard.currentText()

        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            materials = IFCInput(ifc_file).material_properties()[0]
            volumes = IFCInput(ifc_file).material_properties()[1]
            status = IFCInput(ifc_file).material_properties()[2]

            ifc_file_existing = ifcopenshell.open((self.file_path_1)[0])
            materials_existing = IFCInput(ifc_file_existing).material_properties()[0]
            volumes_existing = IFCInput(ifc_file_existing).material_properties()[1]
            status_existing = IFCInput(ifc_file_existing).material_properties()[2]

            materials_ETIM = IFCInput(ifc_file).material_properties()[9]
            mass_ETIM = IFCInput(ifc_file).material_properties()[8]
            status_ETIM = IFCInput(ifc_file).material_properties()[6]
            #status_ETIM = list(map(lambda x: x.replace('EV000001_New', '1'), status_ETIM))
            #status_ETIM = list(map(lambda x: x.replace('EV000004_Reused in the same building', '4'), status_ETIM))


            mass = []
            for material, volume in zip(materials, volumes):
                try:
                    code = (material.split('_', 2))[1]
                    code = code.lower()
                    material_density = \
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                    mass.append(material_density * volume)
                except:
                    # put an average idensity for unknown materials
                    mass.append(1000 * volume)
            material_total = materials + materials_ETIM
            status_total = status + status_ETIM
            mass_total = mass + mass_ETIM


            mass_exiting = []
            for material, volume in zip(materials_existing, volumes_existing):
                try:
                    code = (material.split('_', 2))[1]
                    code = code.lower()
                    material_density = \
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                    mass_exiting.append(material_density * volume)
                except:
                    mass_exiting.append(1000 * volume)

            if len(material_total) == 0 or len(materials_existing) == 0:
                QtWidgets.QMessageBox.warning(self, "Material standard checking",
                                              "Please assign material information based on standards")
            else:
                if material_standard == "NL-SfB Table 3":
                    self.materialwindow_NLSfB.figure = plt.figure()
                    self.materialwindow_NLSfB.canvas2 = FigureCanvas(self.materialwindow_NLSfB.figure)
                    layout = QVBoxLayout()
                    self.materialwindow_NLSfB.widget10.setLayout(layout)
                    layout.addWidget(self.materialwindow_NLSfB.canvas2)

                    NL_SfB_File = pd.read_excel("External database.xlsx", sheet_name="NL-SfB_Tabel 3")
                    # extract NL-sfb (table 3) from the material name (located between the first undersocre and the second undersocre)
                    # link external excel file to check corresponding material categroy (e.g., f2 is the precase concrete)
                    # sum the quantities with the same material category
                    materialcode = {}

                    # a list to hold the information of material cateogry of each material
                    category = []
                    sub_category = []


                    for key, value in zip(material_total, mass_total):
                        try:
                            code = (key.split('_', 2))[1]
                            code = code.lower()
                            material_category = \
                            NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Category'].iloc[
                                0]
                            material_subcategory = \
                                NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'text_NL-SfB_en'].iloc[0]
                            category.append(material_category)
                            sub_category.append(material_subcategory)
                            if material_category in materialcode:
                                materialcode[material_category] += value
                            else:
                                materialcode[material_category] = value
                        except:
                                try:
                                    code = (key.split('_', 2))[0]
                                    material_category = \
                                        NLSfB_Table3.loc[NLSfB_Table3['ETIM Standard'] == code, 'Category'].iloc[0]
                                    material_subcategory = \
                                        NLSfB_Table3.loc[
                                            NLSfB_Table3['ETIM Standard'] == code, 'ETIM Standard Name'].iloc[0]

                                    category.append(material_category)
                                    sub_category.append((material_subcategory))
                                    if material_category in materialcode:
                                        materialcode[material_category] += value
                                    else:
                                        materialcode[material_category] = value
                                except:
                                    category.append("Unknown")
                                    sub_category.append("Unknown")
                                    if "Unknown" in materialcode:
                                        materialcode["Unknown"] += value
                                    else:
                                        materialcode["Unknown"] = value

                    materialcode_existing = {}
                    category_existing = []
                    subcategory_existing = []
                    for key, value in zip(materials_existing, mass_exiting):
                        try:
                            code = (key.split('_', 2))[1]
                            code = code.lower()
                            material_category = \
                                NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Category'].iloc[
                                    0]
                            material_subcategory = \
                                NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'text_NL-SfB_en'].iloc[0]
                            category_existing.append(material_category)
                            subcategory_existing.append(material_subcategory)
                            if material_category in materialcode_existing:
                                materialcode_existing[material_category] += value
                            else:
                                materialcode_existing[material_category] = value
                        except:
                            try:
                                code = (key.split('_', 2))[0]
                                material_category = \
                                    NLSfB_Table3.loc[NLSfB_Table3['ETIM Standard'] == code, 'Category'].iloc[0]
                                material_subcategory = \
                                    NLSfB_Table3.loc[
                                        NLSfB_Table3['ETIM Standard'] == code, 'ETIM Standard Name'].iloc[0]
                                category_existing.append(material_category)
                                subcategory_existing.append((material_subcategory))
                                if material_category in materialcode_existing:
                                    materialcode_existing[material_category] += value
                                else:
                                    materialcode_existing[material_category] = value
                            except:
                                category_existing.append("Unknown")
                                subcategory_existing.append("Unknown")
                                if "Unknown" in materialcode:
                                    materialcode_existing["Unknown"] += value
                                else:
                                    materialcode_existing["Unknown"] = value

                    # sum volume based on its material type and status; for exmaple, the reused concrete is seperated from new concrete
                    cat_sta_mass_sum = {}
                    for key1, key2, value in zip(category, status_total, mass_total):
                        if (key1, key2) in cat_sta_mass_sum:
                            cat_sta_mass_sum[(key1, key2)] += value
                        else:
                            cat_sta_mass_sum[(key1, key2)] = value

                    cat_sta_mass_existing_sum = {}
                    for key1, key2, value in zip(category_existing, status_existing, mass_exiting):
                        if (key1, key2) in cat_sta_mass_existing_sum:
                            cat_sta_mass_existing_sum[(key1, key2)] += value
                        else:
                            cat_sta_mass_existing_sum[(key1, key2)] = value

                    project_material_status = {}
                    for (key1, key2), value in cat_sta_mass_existing_sum.items():
                        for (key3, key4), value1 in cat_sta_mass_sum.items():
                            if key2 == "4":
                                project_material_status[(key1, key2)] = value
                            if key2 == "2":
                                project_material_status[(key1, key2)] = value
                            if key2 == "5":
                                project_material_status[(key1, key2)] = value
                            if key4 == "1":
                                project_material_status[(key3, key4)] = value1
                            if key4 == "3":
                                project_material_status[(key3, key4)] = value1

                    project_material = {}
                    for (key1, key2), value in project_material_status.items():
                        if key1 in project_material:
                            project_material[key1] += value
                        else:
                            project_material[key1] = value

                    arrow_1 = {}
                    arrow_2 = {}
                    arrow_3 = {}
                    arrow_4 = {}
                    arrow_5 = {}

                    new_material = []
                    reused = []
                    waste = []
                    reused_from_oldbuilding = []
                    recovery_in_anotherbuilding = []

                    # for each material category (e.g., precast concrete), sum its volume based on its status
                    # for the material which did not contribute the volume of a status, for example, if no concrete is new, put volume value as zero
                    for (key1, key2), value in project_material_status.items():
                        for key in project_material.keys():
                            if key1 == key and key2 == "4":
                                arrow_4[key] = value
                            if key not in arrow_4:
                                arrow_4[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "1":
                                arrow_1[key] = value
                            if key not in arrow_1:
                                arrow_1[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "3":
                                arrow_3[key] = value
                            if key not in arrow_3:
                                arrow_3[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "2":
                                arrow_2[key] = value
                            if key not in arrow_2:
                                arrow_2[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "5":
                                arrow_5[key] = value
                            if key not in arrow_5:
                                arrow_5[key] = 0

                    # extract volume based on material sequence
                    for value in arrow_1.values():
                        new_material.append(round(value / 1000, 2))
                    for value in arrow_2.values():
                        waste.append(round(value / 1000, 2))
                    for value in arrow_3.values():
                        reused_from_oldbuilding.append(round(value / 1000, 2))
                    for value in arrow_4.values():
                        reused.append(round(value / 1000, 2))
                    for value in arrow_5.values():
                        recovery_in_anotherbuilding.append(round(value / 1000, 2))

                    data = [new_material,
                            waste,
                            reused_from_oldbuilding,
                            reused,
                            recovery_in_anotherbuilding]

                    data_array = np.array(data)

                    # calculating the circularity value of each material category and put these values in a list
                    circularity_value = []
                    for i in range(0, (len(project_material.values()))):
                        array = data_array[:, i]
                        sum = np.sum(array)
                        factor_sum = array[0] * 0 + array[1] * 0 + array[2] * 0.5 + array[3] * 1 + array[4] * 0.5
                        value = round(factor_sum / sum, 2)
                        circularity_value.append(value)

                    data_new = [new_material,
                                waste,
                                reused_from_oldbuilding,
                                reused,
                                recovery_in_anotherbuilding, circularity_value]

                    columns = tuple(project_material.keys())
                    rows = ["New material/products / 1000Kg", "Unrecoverable waste / 1000Kg",
                            "Reused products from an old building/ 1000Kg",
                            "Reused products in the same building / 1000Kg",
                            "Reuse products in another building / 1000Kg", "Circularity Value"]

                    # Get some pastel shades for the colors
                    colors = [[float(227) / 255, float(150) / 255, float(149) / 255],
                              [float(148) / 255, float(41) / 255, float(17) / 255],
                              [float(88) / 255, float(164) / 255, float(176) / 255],
                              [float(86) / 255, float(110) / 255, float(61) / 255],
                              [float(108) / 255, float(105) / 255, float(141) / 255],
                              [1, 1, 1]]

                    colors = np.array(colors)

                    n_rows = len(data_new)
                    index = np.arange(len(columns)) + 0.3
                    bar_width = 0.4

                    # Initialize the vertical-offset for the stacked bar chart.
                    y_offset = np.zeros(len(columns))

                    # Plot bars and create text labels for the table

                    for row in range(n_rows):
                        plt.bar(index, data_new[row], bar_width, bottom=y_offset, color=colors[row])
                        y_offset = y_offset + data_new[row]

                    # Add a table at the bottom of the axes
                    the_table = plt.table(cellText=data_new,
                                          rowLabels=rows,
                                          rowColours=colors,
                                          colLabels=columns,
                                          loc='bottom')
                    the_table.auto_set_font_size(False)
                    the_table.set_fontsize(9)

                    # set the text color ("Arrow 1" to “Arrow 6") as white
                    cell_lists = []
                    for i in range(1, 7):
                        cell = the_table[i, -1]
                        cell.get_text().set_fontweight("bold")

                    for i in range(1, 6):
                        cell = the_table[i, -1]
                        cell.get_text().set_color('white')

                    for i in range(0, len(project_material)):
                        cell = the_table[0, i]
                        cell.get_text().set_fontweight("bold")

                    # Adjust layout to make room for the table:
                    plt.subplots_adjust(left=0.2, bottom=0.2)
                    plt.xticks([])
                    self.materialwindow_NLSfB.canvas2.draw()
                    plt.close()

                    # show the details of materials (detailed category)
                    ##############################################
                    ###############################################
                    ##################################################

                    # sum volume based on its material type,sub material type and status
                    category_subcategory = {}
                    for key1, key2, key3, value in zip(category, sub_category, status_total, mass_total):
                        if (key1, key2, key3) in category_subcategory:
                            category_subcategory[(key1, key2, key3)] += value
                        else:
                            category_subcategory[(key1, key2, key3)] = value

                    category_subcategory_existing = {}
                    for key1, key2, key3, value in zip(category_existing, subcategory_existing, status_existing,
                                                       mass_exiting):
                        if (key1, key2, key3) in category_subcategory_existing:
                            category_subcategory_existing[(key1, key2, key3)] += value
                        else:
                            category_subcategory_existing[(key1, key2, key3)] = value

                    # combine information from two ifc files, getting "4", "2", "5" from the new building and the rest from old
                    # avoid double counting for those "reused in the same building (4), choosing the information in old building as reference

                    project_subcategory_status_mass = {}
                    for (key1, key2, key3), value in category_subcategory_existing.items():
                        for (key4, key5, key6), value1 in category_subcategory.items():
                            if key3 == "4":
                                project_subcategory_status_mass[(key1, key2, key3)] = value
                            if key3 == "2":
                                project_subcategory_status_mass[(key1, key2, key3)] = value
                            if key3 == "5":
                                project_subcategory_status_mass[(key1, key2, key3)] = value
                            if key6 == "1":
                                project_subcategory_status_mass[(key4, key5, key6)] = value1
                            if key6 == "3":
                                project_subcategory_status_mass[(key4, key5, key6)] = value1

                    # sum the volume of the same subcategory for each category
                    project_subcategory_mass = {}
                    for (key1, key2, key3), value in project_subcategory_status_mass.items():
                        if (key1, key2) in project_subcategory_mass:
                            project_subcategory_mass[(key1, key2)] += value
                        else:
                            project_subcategory_mass[(key1, key2)] = value

                    Stone = {}
                    Clay_Lime_Cement_Concrete = {}
                    Metal = {}
                    Wood_Organic_material = {}
                    Fiber_Rubbers_Plastic = {}
                    Glass = {}
                    Aggregates_Loosefills = {}
                    Others = {}

                    for (key1, key2), value in project_subcategory_mass.items():
                        if key1 == "Clay/Concrete":
                            Clay_Lime_Cement_Concrete[key2] = value
                        if key1 == "Stone":
                            Stone[key2] = value
                        if key1 == "Metal":
                            Metal[key2] = value
                        if key1 == "Organic Materials":
                            Wood_Organic_material[key2] = value
                        if key1 == "Inorganic Materials":
                            Fiber_Rubbers_Plastic[key2] = value
                        if key1 == "Glass":
                            Glass[key2] = value
                        if key1 == "Others":
                            Others[key2] = value
                        if key1 == "Aggregates":
                            Aggregates_Loosefills[key2] = value

                        concrete_text = materialdetails(Clay_Lime_Cement_Concrete)
                        self.materialwindow_NLSfB.concrete_details.setText(concrete_text)

                        stone_text = materialdetails(Stone)
                        self.materialwindow_NLSfB.stone_details.setText(stone_text)

                        metal_text = materialdetails(Metal)
                        self.materialwindow_NLSfB.metal_details.setText(metal_text)

                        wood_text = materialdetails(Wood_Organic_material)
                        self.materialwindow_NLSfB.wood_details.setText(wood_text)

                        fiber_text = materialdetails(Fiber_Rubbers_Plastic)
                        self.materialwindow_NLSfB.fiber_details.setText(fiber_text)

                        fills_text = materialdetails(Aggregates_Loosefills)
                        self.materialwindow_NLSfB.fills_details.setText(fills_text)

                        glass_text = materialdetails(Glass)
                        self.materialwindow_NLSfB.glass_details.setText(glass_text)

                        others_text = materialdetails(Others)
                        self.materialwindow_NLSfB.others_details.setText(others_text)

                    self.materialwindow_NLSfB.display_materialinfo()

                if material_standard == "NAA.K.T":
                    self.materialwindow_NAAKT.figure = plt.figure()
                    self.materialwindow_NAAKT.canvas2 = FigureCanvas(self.materialwindow_NAAKT.figure)
                    layout = QVBoxLayout()
                    self.materialwindow_NAAKT.material_window.setLayout(layout)
                    layout.addWidget(self.materialwindow_NAAKT.canvas2)

                    materialcode = {}
                    # a list to hold the information of material cateogry of each material
                    category = []
                    for key, value in zip(materials, mass):
                        try:
                            code = (key.split('_', 2))[0]
                            category.append(code)
                            if code in materialcode:
                                materialcode[code] += value
                            else:
                                materialcode[code] = value
                        except:
                            category.append("Unknown")
                            if "Unknown" in materialcode:
                                materialcode["Unknown"] += value
                            else:
                                materialcode["Unknown"] = value

                    materialcode_existing = {}
                    category_existing = []
                    for key, value in zip(materials_existing, mass_exiting):
                        try:
                            code = (key.split('_', 2))[0]
                            category_existing.append(code)
                            if code in materialcode_existing:
                                materialcode_existing[code] += value
                            else:
                                materialcode_existing[code] = value
                        except:
                            category_existing.append("Unknown")
                            if "Unknown" in materialcode:
                                materialcode_existing["Unknown"] += value
                            else:
                                materialcode_existing["Unknown"] = value

                    # sum volume based on its material type and status; for exmaple, the reused concrete is seperated from new concrete
                    cat_sta_mass_sum = {}
                    for key1, key2, value in zip(category, status, mass):
                        if (key1, key2) in cat_sta_mass_sum:
                            cat_sta_mass_sum[(key1, key2)] += value
                        else:
                            cat_sta_mass_sum[(key1, key2)] = value

                    cat_sta_mass_existing_sum = {}
                    for key1, key2, value in zip(category_existing, status_existing, mass_exiting):
                        if (key1, key2) in cat_sta_mass_existing_sum:
                            cat_sta_mass_existing_sum[(key1, key2)] += value
                        else:
                            cat_sta_mass_existing_sum[(key1, key2)] = value

                    project_material_status = {}
                    for (key1, key2), value in cat_sta_mass_existing_sum.items():
                        for (key3, key4), value1 in cat_sta_mass_sum.items():
                            if key2 == "4":
                                project_material_status[(key1, key2)] = value
                            if key2 == "2":
                                project_material_status[(key1, key2)] = value
                            if key2 == "5":
                                project_material_status[(key1, key2)] = value
                            if key4 == "1":
                                project_material_status[(key3, key4)] = value1
                            if key4 == "3":
                                project_material_status[(key3, key4)] = value1

                    project_material = {}
                    for (key1, key2), value in project_material_status.items():
                        if key1 in project_material:
                            project_material[key1] += value
                        else:
                            project_material[key1] = value

                    arrow_1 = {}
                    arrow_2 = {}
                    arrow_3 = {}
                    arrow_4 = {}
                    arrow_5 = {}

                    new_material = []
                    reused = []
                    waste = []
                    reused_from_oldbuilding = []
                    recovery_in_anotherbuilding = []

                    # for each material category (e.g., precast concrete), sum its volume based on its status
                    # for the material which did not contribute the volume of a status, for example, if no concrete is new, put volume value as zero
                    for (key1, key2), value in project_material_status.items():
                        for key in project_material.keys():
                            if key1 == key and key2 == "4":
                                arrow_4[key] = value
                            if key not in arrow_4:
                                arrow_4[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "1":
                                arrow_1[key] = value
                            if key not in arrow_1:
                                arrow_1[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "3":
                                arrow_3[key] = value
                            if key not in arrow_3:
                                arrow_3[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "2":
                                arrow_2[key] = value
                            if key not in arrow_2:
                                arrow_2[key] = 0

                        for key in project_material.keys():
                            if key1 == key and key2 == "5":
                                arrow_5[key] = value
                            if key not in arrow_5:
                                arrow_5[key] = 0

                    # extract volume based on material sequence
                    for value in arrow_1.values():
                        new_material.append(round(value / 1000, 2))
                    for value in arrow_2.values():
                        waste.append(round(value / 1000, 2))
                    for value in arrow_3.values():
                        reused_from_oldbuilding.append(round(value / 1000, 2))
                    for value in arrow_4.values():
                        reused.append(round(value / 1000, 2))
                    for value in arrow_5.values():
                        recovery_in_anotherbuilding.append(round(value / 1000, 2))

                    data = [new_material,
                            waste,
                            reused_from_oldbuilding,
                            reused,
                            recovery_in_anotherbuilding]

                    data_array = np.array(data)

                    # calculating the circularity value of each material category and put these values in a list
                    circularity_value = []
                    for i in range(0, (len(project_material.values()))):
                        array = data_array[:, i]
                        sum = np.sum(array)
                        factor_sum = array[0] * 0 + array[1] * 0 + array[2] * 0.5 + array[3] * 1 + array[4] * 0.5
                        value = round(factor_sum / sum, 2)
                        circularity_value.append(value)

                    data_new = [new_material,
                                waste,
                                reused_from_oldbuilding,
                                reused,
                                recovery_in_anotherbuilding, circularity_value]

                    columns = tuple(project_material.keys())
                    rows = ["New material / 1000Kg", "Unrecoverable waste / 1000Kg",
                            "Reused materials from an old building/ 1000Kg",
                            "Recovery and reuse in the same building / 1000Kg",
                            "Recovery and reuse in another building / 1000Kg", "Circularity Value"]

                    # Get some pastel shades for the colors
                    colors = [[float(227) / 255, float(150) / 255, float(149) / 255],
                              [float(148) / 255, float(41) / 255, float(17) / 255],
                              [float(88) / 255, float(164) / 255, float(176) / 255],
                              [float(86) / 255, float(110) / 255, float(61) / 255],
                              [float(108) / 255, float(105) / 255, float(141) / 255],
                              [1, 1, 1]]

                    colors = np.array(colors)

                    n_rows = len(data_new)
                    index = np.arange(len(columns)) + 0.3
                    bar_width = 0.4

                    # Initialize the vertical-offset for the stacked bar chart.
                    y_offset = np.zeros(len(columns))

                    # Plot bars and create text labels for the table

                    for row in range(n_rows):
                        plt.bar(index, data_new[row], bar_width, bottom=y_offset, color=colors[row])
                        y_offset = y_offset + data_new[row]

                    # Add a table at the bottom of the axes
                    the_table = plt.table(cellText=data_new,
                                          rowLabels=rows,
                                          rowColours=colors,
                                          colLabels=columns,
                                          loc='bottom')
                    the_table.auto_set_font_size(False)
                    the_table.set_fontsize(10)

                    # set the text color ("Arrow 1" to “Arrow 6") as white
                    cell_lists = []
                    for i in range(1, 7):
                        cell = the_table[i, -1]
                        cell.get_text().set_fontweight("bold")

                    for i in range(1, 6):
                        cell = the_table[i, -1]
                        cell.get_text().set_color('white')

                    for i in range(0, len(project_material)):
                        cell = the_table[0, i]
                        cell.get_text().set_fontweight("bold")

                    # Adjust layout to make room for the table:
                    plt.subplots_adjust(left=0.2, bottom=0.2)
                    plt.xticks([])
                    self.materialwindow_NAAKT.canvas2.draw()
                    plt.close()

                    # presenting the precenatge of biological and technical materials in each arrow
                    arrow1_B = bio_technimaterial_NAAKT(arrow_1)[0]
                    arrow1_T = bio_technimaterial_NAAKT(arrow_1)[1]
                    self.BT1.setText("(T:{:.0%}".format(arrow1_T) + " " + "B:{:.0%})".format(arrow1_B))

                    arrow2_B = bio_technimaterial_NAAKT(arrow_2)[0]
                    arrow2_T = bio_technimaterial_NAAKT(arrow_2)[1]
                    self.BT2.setText("(T:{:.0%}".format(arrow2_T) + " " + "B:{:.0%})".format(arrow2_B))

                    arrow3_B = bio_technimaterial_NAAKT(arrow_3)[0]
                    arrow3_T = bio_technimaterial_NAAKT(arrow_3)[1]
                    self.BT3.setText("(T:{:.0%}".format(arrow3_T) + " " + "B:{:.0%})".format(arrow3_B))

                    arrow4_B = bio_technimaterial_NAAKT(arrow_4)[0]
                    arrow4_T = bio_technimaterial_NAAKT(arrow_4)[1]
                    self.BT4.setText("(T:{:.0%}".format(arrow4_T) + " " + "B:{:.0%})".format(arrow4_B))

                    arrow5_B = bio_technimaterial_NAAKT(arrow_5)[0]
                    arrow5_T = bio_technimaterial_NAAKT(arrow_5)[1]
                    self.BT5.setText("(T:{:.0%}".format(arrow5_T) + " " + "B:{:.0%})".format(arrow5_B))
                    self.materialwindow_NAAKT.display_materialinfo()

                self.entityperformance()
                self.materialoverview()
        except:
            choice = QtWidgets.QMessageBox.warning(self, "Material analysis fail",
                                                   "No deeper material insights can be found",
                                                   QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Close)
            if choice == QtWidgets.QMessageBox.Close:
                sys.exit()
            else:
                return

    def materialoverview(self):
        ifc_file = ifcopenshell.open((self.file_path)[0])
        ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])

        status_new = IFCInput(ifc_file).product_status()
        weight_new = IFCInput(ifc_file).product_weight()

        recycled_value = IFCInput(ifc_file).recycled_percentage()

        status_existing = IFCInput(ifc_file_1).product_status()
        weight_existing = IFCInput(ifc_file_1).product_weight()

        materialss = IFCInput(ifc_file).material_properties()[0]
        volumes = IFCInput(ifc_file).material_properties()[1]
        statuss = IFCInput(ifc_file).material_properties()[2]

        materials_ETIM = IFCInput(ifc_file).material_properties()[9]
        mass_ETIM = IFCInput(ifc_file).material_properties()[8]
        status_ETIM = IFCInput(ifc_file).material_properties()[6]
        #status_ETIM = list(map(lambda x: x.replace('EV000001_New', '1'), status_ETIM))
        #status_ETIM = list(map(lambda x: x.replace('EV000004_Reused in the same building', '4'), status_ETIM))

        materialss_existing = IFCInput(ifc_file_1).material_properties()[0]
        volumes_existing = IFCInput(ifc_file_1).material_properties()[1]
        statuss_existing = IFCInput(ifc_file_1).material_properties()[2]

        mass = []
        for material, volume in zip(materialss, volumes):
            try:
                code = (material.split('_', 2))[1]
                code = code.lower()
                material_density = \
                    NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                mass.append(material_density * volume)
            except:
                # put an average idensity for unknown materials
                mass.append(1000 * volume)

        mass_existing = []
        for material, volume in zip(materialss_existing, volumes_existing):
            try:
                code = (material.split('_', 2))[1]
                code = code.lower()
                material_density = \
                    NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                mass_existing.append(material_density * volume)
            except:
                # put an average idensity for unknown materials
                mass_existing.append(1000 * volume)

        mass_total = mass + mass_ETIM
        materials_total = materialss + materials_ETIM
        status_total = statuss + status_ETIM

        New_value = 0
        Existing_value = 0
        Demolished_value = 0
        Reuse_from_old_building = 0
        Recovery_in_another_building = 0
        for key, value in zip(status_new, weight_new):
            if key == "1":
                New_value = New_value + value
            if key == "3":
                Reuse_from_old_building = Reuse_from_old_building + value

        for key, value in zip(status_existing, weight_existing):
            if key == "2":
                Demolished_value = Demolished_value + value
            if key == "5":
                Recovery_in_another_building = Recovery_in_another_building + value
            if key == "4":
                Existing_value = Existing_value + value

        width_new = (New_value / (
                New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building))
        width_reused = (Existing_value / (
                New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building))
        width_demolished = (Demolished_value / (
                New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building))
        width_reused_old_building = (Reuse_from_old_building / (
                New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building))
        width_recovery_another_building = (Recovery_in_another_building / (
                New_value + Existing_value + Demolished_value + Reuse_from_old_building + Recovery_in_another_building))

        ratios = [width_new, width_reused, width_demolished, width_reused_old_building, width_recovery_another_building]
        labels = [("New materials/products: %.2f%%" % (width_new * 100)),
                  ("Reused products in the same building: %.2f%%" % (width_reused * 100)),
                  ("Waste:%.2f%%" % (width_demolished * 100)),
                  ("Reused products from an old building:%.2f%%" % (width_reused_old_building * 100)),
                  ("Reuse products in another building: %.2f%%" % (width_recovery_another_building * 100))]
        colors = [[float(227) / 255, float(150) / 255, float(149) / 255],
                  [float(86) / 255, float(110) / 255, float(61) / 255],
                  [float(148) / 255, float(41) / 255, float(17) / 255],
                  [float(88) / 255, float(164) / 255, float(176) / 255],
                  [float(108) / 255, float(105) / 255, float(141) / 255],
                  ]

        material_standard = self.standard.currentText()

        if material_standard == "NL-SfB Table 3":
            self.materialwindow_NLSfB.figure, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 10))
            self.materialwindow_NLSfB.canvas3 = FigureCanvas(self.materialwindow_NLSfB.figure)
            layout = QVBoxLayout()
            self.materialwindow_NLSfB.material_overview.setLayout(layout)
            layout.addWidget(self.materialwindow_NLSfB.canvas3)

            # rotate so that first wedge is split by the x-axis
            angle = -180 * ratios[0]
            ax2.pie(ratios, startangle=angle, colors=colors, wedgeprops={'alpha': 0.93})
            ax2.legend(labels, bbox_to_anchor=(1, -0.3), loc='lower right')


            material_status_volume = {}
            for key1, key2, value in zip(materials_total, status_total, mass_total):
                if (key1, key2) in material_status_volume:
                    material_status_volume[(key1, key2)] += value
                else:
                    material_status_volume[(key1, key2)] = value

            # etract the volume information of each new material (status=1) and translate the code to real material name
            new_material_volume = {}
            for (key1, key2), value in material_status_volume.items():
                if key2 == "1":
                    NL_SfB_File = pd.read_excel("External database.xlsx", sheet_name="NL-SfB_Tabel 3")
                    try:
                        code = (key1.split('_', 2))[1]
                        code = code.lower()
                        material_category = \
                            NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Category'].iloc[0]
                        if key1 not in new_material_volume:
                            new_material_volume[(material_category)] = (value)
                        else:
                            new_material_volume[(material_category)] += (value)
                    except:
                        try:
                            code = (key1.split('_', 2))[0]
                            material_category = \
                                NL_SfB_File.loc[NL_SfB_File['ETIM Standard'] == code, 'Category'].iloc[0]
                            new_material_volume[(material_category)] = value
                        except:
                            material_category = "Unknown"
                            new_material_volume[(material_category)] = (value)

            biomaterials = 0

            for key, value in new_material_volume.items():
                if key == "Organic Materials":
                    biomaterials += value

            if width_new != 0:
                if all(value == "Unknown" for value in recycled_value) or all(value == 0 for value in recycled_value):
                    #ax3.axis('off')

                    Circular_material_percentage = biomaterials / New_value
                    Non_circular_material = (New_value - biomaterials) / New_value

                else:
                    # the information of new materials (arrow 1) is stored in the IFC file of new building
                    # calculate the weight of recycled materials from new materials
                    weight_recycled_status = {}

                    for key1, key2, value in zip(weight_new, recycled_value, status_new):
                        weight_recycled_status[(key1, key2)] = value

                    recycled_weight = 0
                    for (key1, key2), value in weight_recycled_status.items():
                        if value == "1":
                            recycled_weight += key1 * key2

                    # calculate the weight of bio-based materials from new materials

                    if biomaterials >= recycled_weight:
                        circular_materials = biomaterials
                    else:
                        circular_materials = recycled_weight

                    Circular_material_percentage = circular_materials/New_value
                    Non_circular_material = (New_value-circular_materials)/New_value

                # creating a bar chart to distinguish bio/tech materials
                xpos = 0
                bottom = 0
                ratios = [Circular_material_percentage, Non_circular_material]
                width = .2
                colors = [[float(227) / 255, float(150) / 255, float(140) / 255],
                          [float(227) / 255, float(150) / 255, float(200) / 255],]

                for j in range(len(ratios)):
                    height = ratios[j]
                    ax3.bar(xpos, height, width, bottom=bottom, color=colors[j])
                    # ypos = bottom + ax3.patches[j].get_height() / 2
                    bottom += height
                    # ax3.text(xpos, ypos, "%d%%" % (ax3.patches[j].get_height() * 100),
                    # ha='center')

                ax3.set_title('New materials')
                if all(value == "Unknown" for value in recycled_value) or  all(value == 0 for value in recycled_value):
                    ax3.legend([("Renewable materials: %.2f%%" % (Circular_material_percentage * 100)),
                                ("Non-Renewable primary materials: %.2f%%" % (Non_circular_material * 100))],
                               bbox_to_anchor=(1.45, 0), loc='lower right')
                else:
                    ax3.legend([("Recycled or/and Renewable materials: %.2f%%" % (Circular_material_percentage * 100)),
                                ("Non-renewable primary materials: %.2f%%" % (Non_circular_material * 100))],
                               bbox_to_anchor=(1.45, 0), loc='lower right')

                ax3.axis('off')
                ax3.set_xlim(- 2.5 * width, 2.5 * width)

                # use ConnectionPatch to draw lines between the two plots
                # get the wedge data
                theta1, theta2 = ax2.patches[0].theta1, ax2.patches[0].theta2
                center, r = ax2.patches[0].center, ax2.patches[0].r
                bar_height = sum([item.get_height() for item in ax3.patches])

                # draw top connecting line
                x = r * np.cos(np.pi / 180 * theta2) + center[0]
                y = r * np.sin(np.pi / 180 * theta2) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax3.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                con.set_linewidth(1)
                ax3.add_artist(con)

                # draw bottom connecting line
                x = r * np.cos(np.pi / 180 * theta1) + center[0]
                y = r * np.sin(np.pi / 180 * theta1) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax3.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                ax3.add_artist(con)
                con.set_linewidth(1)

            else:
                ax3.axis('off')

            if width_demolished != 0:
                # extract the percentage of EoL scenairos of each watse material, and calculate the total recycling rate, landfill rate and energy recovery rate
                # the waste information is extracted from the ifc file of existing one
                material_status_volume = {}
                for key1, key2, value in zip(materialss_existing, statuss_existing, mass_existing):
                    if (key1, key2) in material_status_volume:
                        material_status_volume[(key1, key2)] += value
                    else:
                        material_status_volume[(key1, key2)] = value

                waste_volume = {}
                for (key1, key2), value in material_status_volume.items():
                    if key2 == "2":
                        waste_volume[key1] = value

                NL_SfB_File = pd.read_excel("External database.xlsx", sheet_name="NL-SfB_Tabel 3")
                waste_EoL = {}
                total_waste_volume = 0
                for key1, value in waste_volume.items():
                    total_waste_volume += value
                    try:
                        code = (key1.split('_', 2))[1]
                        code = code.lower()
                    except:
                        code = "Unknown"
                    try:
                        recycling_rate = \
                            NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Recycling/Reuse (%)'].iloc[
                                0]
                        lanfill_rate = \
                        NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Landfill (%)'].iloc[
                            0]
                        energy_rate = \
                            NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Energy recovery (%)'].iloc[
                                0]
                        waste_EoL[code] = (value, recycling_rate, lanfill_rate, energy_rate)
                    except:
                        pass

                recycling_volume = 0
                landfill_volume = 0
                enegry_volume = 0
                for code, (volume, recycling, landfill, enegry) in waste_EoL.items():
                    recycling_volume += volume * recycling * 0.01
                    landfill_volume += volume * landfill * 0.01
                    enegry_volume += volume * enegry * 0.01

                unknown = total_waste_volume - recycling_volume - landfill_volume - enegry_volume

                reycling_fraction = round(recycling_volume / total_waste_volume, 2)
                landfill_fraction = round(landfill_volume / total_waste_volume, 2)
                enegry_fraction = round(enegry_volume / total_waste_volume, 2)
                unknown_fraction = round((unknown / total_waste_volume), 2)

                # create a bar chart presenting the precentage of waste going to recycling, landfill or energy recovery
                xpos = 0
                bottom = 0
                ratios = [landfill_fraction, enegry_fraction, reycling_fraction, unknown_fraction]
                width = .2
                colors = ([float(210) / 255, 0, 0],
                          [float(150) / 255, 0, 0],
                          [float(100) / 255, 0, 0],
                          [0, 0, 0])

                for j in range(len(ratios)):
                    height = ratios[j]
                    ax1.bar(xpos, height, width, bottom=bottom, color=colors[j])
                    # ypos = bottom + ax1.patches[j].get_height() / 2
                    bottom += height
                    # ax1.text(xpos, ypos, "%d%%" % (ax1.patches[j].get_height() * 100),
                    # ha='center')

                ax1.set_title('Waste')
                ax1.legend([("Landfill: %.2f%%" % (landfill_fraction * 100)),
                            ("Energy recovery: %.2f%%" % (enegry_fraction * 100)),
                            ("Recycling/reuse: %.2f%%" % (reycling_fraction * 100)),
                            ("Unknown: %.2f%%" % (unknown_fraction * 100))],
                           bbox_to_anchor=(-0.25, 0.0), loc='lower left')
                ax1.axis('off')
                ax1.set_xlim(- 2.5 * width, 2.5 * width)

                # use ConnectionPatch to draw lines between the two plots
                # get the wedge data
                theta1, theta2 = ax2.patches[2].theta1, ax2.patches[2].theta2
                center, r = ax2.patches[2].center, ax2.patches[2].r
                bar_height = sum([item.get_height() for item in ax1.patches])

                # draw top connecting line
                x = r * np.cos(np.pi / 180 * theta1) + center[0]
                y = r * np.sin(np.pi / 180 * theta1) + center[1]
                con = ConnectionPatch(xyA=(width / 2, bar_height), coordsA=ax1.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                con.set_linewidth(1)
                ax1.add_artist(con)

                # draw bottom connecting line
                x = r * np.cos(np.pi / 180 * theta2) + center[0]
                y = r * np.sin(np.pi / 180 * theta2) + center[1]
                con = ConnectionPatch(xyA=(width / 2, 0), coordsA=ax1.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                ax1.add_artist(con)
                con.set_linewidth(1)
            else:
                ax1.axis('off')

            self.materialwindow_NLSfB.canvas3.draw()
            plt.close()
        else:
            self.materialwindow_NAAKT.figure, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 10))
            self.materialwindow_NAAKT.canvas3 = FigureCanvas(self.materialwindow_NAAKT.figure)
            layout = QVBoxLayout()
            self.materialwindow_NAAKT.material_overview.setLayout(layout)
            layout.addWidget(self.materialwindow_NAAKT.canvas3)

            # rotate so that first wedge is split by the x-axis
            angle = -180 * ratios[0]
            ax2.pie(ratios, startangle=angle, colors=colors)
            ax2.legend(labels, bbox_to_anchor=(1, -0.3), loc='lower right')

            if width_new != 0:
                # creating a dic to sum the volume of material with different status
                material_status_volume = {}
                for key1, key2, value in zip(materialss, statuss, volumes):
                    if (key1, key2) in material_status_volume:
                        material_status_volume[(key1, key2)] += value
                    else:
                        material_status_volume[(key1, key2)] = value

                # etract the volume information of each new material (status=1) and translate the code to real material name
                new_material_volume = {}
                for (key1, key2), value in material_status_volume.items():
                    if key2 == "1":
                        # extract the material name in the first location based on NAA.KT
                        try:
                            name = (key1.split('_', 2))[0]
                            new_material_volume[name] = value
                        except:
                            name = "Unknown"
                            new_material_volume[(name)] = value

                New_biomaterial = bio_technimaterial_NAAKT(new_material_volume)[0]
                New_technimaterial = bio_technimaterial_NAAKT(new_material_volume)[1]
                Recycled_biomaterial = 0
                Recycled_technimaterial = 0

                # creating a bar chart to distinguish bio/tech materials
                xpos = 0
                bottom = 0
                ratios = [New_technimaterial, New_biomaterial, Recycled_biomaterial, Recycled_technimaterial]
                width = .2
                colors = [[float(227) / 255, float(150) / 255, float(140) / 255],
                          [float(227) / 255, float(150) / 255, float(170) / 255],
                          [float(227) / 255, float(150) / 255, float(200) / 255],
                          [float(227) / 255, float(150) / 255, float(230) / 255]]

                for j in range(len(ratios)):
                    height = ratios[j]
                    ax3.bar(xpos, height, width, bottom=bottom, color=colors[j])
                    bottom += height

                ax3.set_title('New materials')
                ax3.legend([("Non-renewable new materials: %.2f%%" % (New_technimaterial * 100)),
                            ("Renewable new materials: %.2f%%" % (New_biomaterial * 100)),
                            ("Non-renewable recycled materials: %.2f%%" % (Recycled_technimaterial * 100)),
                            ("Renewable recycled materials: %.2f%%" % (Recycled_biomaterial * 100))],
                           bbox_to_anchor=(1.50, 0), loc='lower right')

                ax3.axis('off')
                ax3.set_xlim(- 2.5 * width, 2.5 * width)

                # use ConnectionPatch to draw lines between the two plots
                # get the wedge data
                theta1, theta2 = ax2.patches[0].theta1, ax2.patches[0].theta2
                center, r = ax2.patches[0].center, ax2.patches[0].r
                bar_height = sum([item.get_height() for item in ax3.patches])

                # draw top connecting line
                x = r * np.cos(np.pi / 180 * theta2) + center[0]
                y = r * np.sin(np.pi / 180 * theta2) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax3.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                con.set_linewidth(1)
                ax3.add_artist(con)

                # draw bottom connecting line
                x = r * np.cos(np.pi / 180 * theta1) + center[0]
                y = r * np.sin(np.pi / 180 * theta1) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax3.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                ax3.add_artist(con)
                con.set_linewidth(1)

            else:
                ax3.axis('off')

            if width_demolished != 0:
                # extract the percentage of EoL scenairos of each watse material, and calculate the total recycling rate, landfill rate and energy recovery rate
                material_status_volume = {}
                for key1, key2, value in zip(materialss_existing, statuss_existing, volumes_existing):
                    if (key1, key2) in material_status_volume:
                        material_status_volume[(key1, key2)] += value
                    else:
                        material_status_volume[(key1, key2)] = value

                waste_volume = {}
                for (key1, key2), value in material_status_volume.items():
                    if key2 == "2":
                        waste_volume[key1] = value

                NL_SfB_File = pd.read_excel("External database.xlsx", sheet_name="NAA.K.T")
                waste_EoL = {}
                total_waste_volume = 0
                for key1, value in waste_volume.items():
                    total_waste_volume += value
                    try:
                        recycling_rate = \
                            NL_SfB_File.loc[
                                NL_SfB_File['NAA.KT'] == key1, 'Recycling/Reuse (%)'].iloc[0]
                        lanfill_rate = \
                            NL_SfB_File.loc[NL_SfB_File['NAA.KT'] == key1, 'Landfill (%)'].iloc[
                                0]
                        energy_rate = \
                            NL_SfB_File.loc[
                                NL_SfB_File['NAA.KT'] == key1, 'Energy recovery (%)'].iloc[0]
                        waste_EoL[key1] = (value, recycling_rate, lanfill_rate, energy_rate)
                    except:
                        pass

                recycling_volume = 0
                landfill_volume = 0
                enegry_volume = 0
                for name, (volume, recycling, landfill, energy) in waste_EoL.items():
                    recycling_volume += volume * recycling * 0.01
                    landfill_volume += volume * landfill * 0.01
                    enegry_volume += volume * energy * 0.01
                    unknown = total_waste_volume - recycling_volume - landfill_volume - enegry_volume

                reycling_fraction = round(recycling_volume / total_waste_volume, 2)
                landfill_fraction = round(landfill_volume / total_waste_volume, 2)
                enegry_fraction = round(enegry_volume / total_waste_volume, 2)
                unknown_fraction = round((unknown / total_waste_volume), 2)

                # create a bar chart presenting the precentage of waste going to recycling, landfill or energy recovery
                xpos = 0
                bottom = 0
                ratios = [landfill_fraction, enegry_fraction, reycling_fraction, unknown_fraction]
                width = .2
                colors = ([float(100) / 255, float(41) / 255, float(17) / 255],
                          [float(130) / 255, float(41) / 255, float(17) / 255],
                          [float(180) / 255, float(41) / 255, float(17) / 255],
                          [0, 0, 0])

                for j in range(len(ratios)):
                    height = ratios[j]
                    ax1.bar(xpos, height, width, bottom=bottom, color=colors[j])
                    bottom += height

                ax1.set_title('Waste')
                ax1.legend([("Landfill: %.2f%%" % (landfill_fraction * 100)),
                            ("Energy recovery: %.2f%%" % (enegry_fraction * 100)),
                            ("Recycling/reuse: %.2f%%" % (reycling_fraction * 100)),
                            ("Unknown: %.2f%%" % (unknown_fraction * 100))],
                           bbox_to_anchor=(-0.25, 0.0), loc='lower left')
                ax1.axis('off')
                ax1.set_xlim(- 2.5 * width, 2.5 * width)

                # use ConnectionPatch to draw lines between the two plots
                # get the wedge data
                theta1, theta2 = ax2.patches[1].theta1, ax2.patches[1].theta2
                center, r = ax2.patches[1].center, ax2.patches[1].r
                bar_height = sum([item.get_height() for item in ax1.patches])

                # draw top connecting line
                x = r * np.cos(np.pi / 180 * theta1) + center[0]
                y = r * np.sin(np.pi / 180 * theta1) + center[1]
                con = ConnectionPatch(xyA=(width / 2, bar_height), coordsA=ax1.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                con.set_linewidth(1)
                ax1.add_artist(con)

                # draw bottom connecting line
                x = r * np.cos(np.pi / 180 * theta2) + center[0]
                y = r * np.sin(np.pi / 180 * theta2) + center[1]
                con = ConnectionPatch(xyA=(width / 2, 0), coordsA=ax1.transData,
                                      xyB=(x, y), coordsB=ax2.transData)
                con.set_color([0, 0, 0])
                ax1.add_artist(con)
                con.set_linewidth(1)
            else:
                ax1.axis('off')

            self.materialwindow_NAAKT.canvas3.draw()
            plt.close()
            return

        # update the circularity value with the improved circularity project model
        # self.Value.setFrameShape(QFrame.HLine)
        # self.updated_value.setText("0.43")

    def entityperformance(self):
        ifc_file = ifcopenshell.open((self.file_path)[0])
        ifc_file_existing = ifcopenshell.open((self.file_path_1)[0])

        materials = IFCInput(ifc_file).material_properties()[0]
        volumes = IFCInput(ifc_file).material_properties()[1]
        status = IFCInput(ifc_file).material_properties()[2]
        codes = IFCInput(ifc_file).material_properties()[4]

        materials_ETIM = IFCInput(ifc_file).material_properties()[9]
        mass_ETIM = IFCInput(ifc_file).material_properties()[8]
        code_ETIM = IFCInput(ifc_file).material_properties()[10]
        status_ETIM = IFCInput(ifc_file).material_properties()[6]
        status_ETIM = list(map(lambda x: x.replace('EV000001_New', '1'), status_ETIM))
        status_ETIM = list(map(lambda x: x.replace('EV000004_Reused in the same building', '4'), status_ETIM))

        materials_existing = IFCInput(ifc_file_existing).material_properties()[0]
        volumes_existing = IFCInput(ifc_file_existing).material_properties()[1]
        status_existing = IFCInput(ifc_file_existing).material_properties()[2]
        codes_existing = IFCInput(ifc_file_existing).material_properties()[4]

        mass = []
        for material, volume in zip(materials, volumes):
            try:
                code = (material.split('_', 2))[1]
                code = code.lower()
                material_density = \
                    NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]

                mass.append((material_density * volume))
            except:
                # assign an average density for unknown materials
                mass.append((1000 * volume))

        mass_total = mass + mass_ETIM
        materials_total = materials + materials_ETIM
        status_total = status + status_ETIM
        codes_total = codes + code_ETIM

        mass_exiting = []
        for material, volume in zip(materials_existing, volumes_existing):
            try:
                code = (material.split('_', 2))[1]
                code = code.lower()
                material_density = \
                    NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                mass_exiting.append(material_density * volume)
            except:
                mass_exiting.append((1000 * volume))

        material_standard = self.standard.currentText()

        entity_category = []
        for code in codes_total:
            try:
                entity_category.append(NLSfB_Table1.loc[NLSfB_Table1['Class-codenotatie'] == code, 'Category'].iloc[0])
            except:
                entity_category.append("Unknown")


        entity_category_eixsting = []
        for code_existing in codes_existing:
            try:
                entity_category_eixsting.append(
                    NLSfB_Table1.loc[NLSfB_Table1['Class-codenotatie'] == code_existing, 'Category'].iloc[0])
            except:
                entity_category_eixsting.append("Unknown")

        def materials_in_entity_analysis(code_vol, code_sta_vol, entity_material_status_volume):
            arrow_1 = {}
            arrow_2 = {}
            arrow_3 = {}
            arrow_4 = {}
            arrow_5 = {}

            new_material = []
            reused = []
            waste = []
            reused_from_oldbuilding = []
            recovery_in_anotherbuilding = []

            # for each material category (e.g., precast concrete), sum its volume based on its status
            # for the material which did not contribute the volume of a status, for example, if no concrete is new, put volume value as zero
            for (key1, key2), value in code_sta_vol.items():
                for key in code_vol.keys():
                    if key1 == key and key2 == "4":
                        arrow_4[key] = value
                    if key not in arrow_4:
                        arrow_4[key] = 0

                    if key1 == key and key2 == "2":
                        arrow_2[key] = value
                    if key not in arrow_2:
                        arrow_2[key] = 0

                    if key1 == key and key2 == "1":
                        arrow_1[key] = value
                    if key not in arrow_1:
                        arrow_1[key] = 0

                    if key1 == key and key2 == "3":
                        arrow_3[key] = value
                    if key not in arrow_3:
                        arrow_3[key] = 0

                    if key1 == key and key2 == "5":
                        arrow_5[key] = value
                    if key not in arrow_5:
                        arrow_5[key] = 0

            # extract volume based on material sequence
            for value in arrow_1.values():
                new_material.append(round(value / 1000, 2))
            for value in arrow_2.values():
                waste.append(round(value / 1000, 2))
            for value in arrow_3.values():
                reused_from_oldbuilding.append(round(value / 1000, 2))
            for value in arrow_4.values():
                reused.append(round(value / 1000, 2))
            for value in arrow_5.values():
                recovery_in_anotherbuilding.append(round(value / 1000, 2))

            data = [new_material,
                    waste,
                    reused_from_oldbuilding,
                    reused,
                    recovery_in_anotherbuilding]

            data_array = np.array(data)

            # calculating the circularity value of each material category and put these values in a list
            circularity_value = []
            for i in range(0, (len(code_vol.values()))):
                array = data_array[:, i]
                sum = np.sum(array)
                factor_sum = array[0] * 0 + array[1] * 0 + array[2] * 0.5 + array[3] * 1 + array[4] * 0.5
                value = round(factor_sum / sum, 2)
                circularity_value.append(value)

            data_new = [new_material,
                        waste,
                        reused_from_oldbuilding,
                        reused,
                        recovery_in_anotherbuilding, circularity_value]

            columns = tuple(code_vol)
            rows = ["New materials/products / 1000Kg", "Unrecoverable waste / 1000Kg",
                    "Reused products from an old building/ 1000Kg", "Reused products in the same building / 1000Kg",
                    "Reuse products in another building / 1000Kg", "Circularity Value"]

            # Get some pastel shades for the colors
            colors = [[float(227) / 255, float(150) / 255, float(149) / 255],
                      [float(148) / 255, float(41) / 255, float(17) / 255],
                      [float(88) / 255, float(164) / 255, float(176) / 255],
                      [float(86) / 255, float(110) / 255, float(61) / 255],
                      [float(108) / 255, float(105) / 255, float(141) / 255],
                      [1, 1, 1]]

            colors = np.array(colors)

            n_rows = len(data_new)
            index = np.arange(len(columns)) + 0.3

            bar_width = 0.4

            # Initialize the vertical-offset for the stacked bar chart.
            y_offset = np.zeros(len(columns))

            # Plot bars and create text labels for the table
            for row in range(n_rows):
                plt.bar(index, data_new[row], bar_width, bottom=y_offset, color=colors[row])
                y_offset = y_offset + data_new[row]

            # Add a table at the bottom of the axes
            the_table = plt.table(cellText=data_new,
                                  rowLabels=rows,
                                  rowColours=colors,
                                  colLabels=columns,
                                  loc='bottom',
                                  )
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(9)

            # change the text color (Arrow 1 ~ Arrow 5) as white
            cell_lists = []
            for i in range(1, 7):
                cell = the_table[i, -1]
                cell.get_text().set_fontweight("bold")

            for i in range(1, 6):
                cell = the_table[i, -1]
                cell.get_text().set_color('white')

            for i in range(0, len(code_vol)):
                cell = the_table[0, i]
                cell.get_text().set_fontweight("bold")

            # Adjust layout to make room for the table:
            plt.subplots_adjust(left=0.2, bottom=0.2)
            plt.xticks([])

            # extract the percentage of EoL scenairos of each watse material, and calculate the total recycling rate, landfill rate and energy recovery rate
            def show_annotation_materials(sel):
                material_information = ""
                entity_information = ""
                if type(sel.artist) == BarContainer:
                    bar = sel.artist[sel.target.index]
                    if sel.artist.get_label() == "_container3":
                        for (code, material, status), volume in entity_material_status_volume.items():
                            if str(columns[sel.index]) == str(code) and status == '4':
                                entity_information = "{} Kg materials in the {} are reused in the same building (arrow 4)," \
                                                     " including:".format(round(bar.get_height() * 1000, 2),
                                                                          str(columns[sel.index]))
                                material_information = material_information + "\n" + material + ":" + str(
                                    round(volume, 2)) + " Kg"
                    if sel.artist.get_label() == "_container1":
                        for (code, material, status), volume in entity_material_status_volume.items():
                            if str(columns[sel.index]) == str(code) and status == '2':
                                entity_information = "{} Kg materials in the {} become waste after demolition (arrow 2)," \
                                                     " including:".format(round(bar.get_height() * 1000, 2),
                                                                          str(columns[sel.index]))
                                material_information = material_information + "\n" + material + ":" + str(
                                    round(volume, 2)) + " Kg"
                    if sel.artist.get_label() == "_container2":
                        for (code, material, status), volume in entity_material_status_volume.items():
                            if str(columns[sel.index]) == str(code) and status == '3':
                                entity_information = "{} Kg materials in the {} are reused materials collected from an old project (arrow 3)," \
                                                     " including:".format(round(bar.get_height() * 100, 2),
                                                                          str(columns[sel.index]))
                                material_information = material_information + "\n" + material + ":" + str(
                                    round(volume, 2)) + " Kg"
                    if sel.artist.get_label() == "_container4":
                        for (code, material, status), volume in entity_material_status_volume.items():
                            if str(columns[sel.index]) == str(code) and status == '5':
                                entity_information = "{} Kg materials in the {} are recovered and reused in another building (arrow 5)," \
                                                     " including:".format(round(bar.get_height() * 100, 2),
                                                                          str(columns[sel.index]))
                                material_information = material_information + "\n" + material + ":" + str(
                                    round(volume, 2)) + " Kg"
                    if sel.artist.get_label() == "_container0":
                        for (code, material, status), volume in entity_material_status_volume.items():
                            if str(columns[sel.index]) == str(code) and status == '1':
                                entity_information = "{} Kg materials in the {} are new materials (arrow 1)," \
                                                     " including:".format(round(bar.get_height() * 100, 2),
                                                                          str(columns[sel.index]))
                                material_information = material_information + "\n" + material + ":" + str(
                                    round(volume, 2)) + " Kg"
                    sel.annotation.set_text("")

                    if material_standard == "NL-SfB Table 3":
                        self.materialwindow_NLSfB.material_details.setText(
                            entity_information + '\n' + material_information)
                    else:
                        self.materialwindow_NAAKT.material_details.setText(
                            entity_information + '\n' + material_information)

                    sel.annotation.xy = (bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2)
                    sel.annotation.get_bbox_patch().set_alpha(0.8)

            cursor = mplcursors.cursor(hover=True)

            cursor.connect('add', show_annotation_materials)

        if material_standard == "NL-SfB Table 3":
            self.materialwindow_NLSfB.figure = plt.figure()
            self.materialwindow_NLSfB.canvas = FigureCanvas(self.materialwindow_NLSfB.figure)
            layout = QVBoxLayout()
            self.materialwindow_NLSfB.enity_circularity.setLayout(layout)
            layout.addWidget(self.materialwindow_NLSfB.canvas)
            material_category_NLSfB = []
            for material in materials_total:
                try:
                    material = (material.split('_', 2))[1]
                    material = material.lower()
                    material_category_NLSfB.append(
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == material, 'Category'].iloc[0])
                except:
                    try:
                        material = (material.split('_', 2))[0]
                        material_category_NLSfB.append(
                            NLSfB_Table3.loc[NLSfB_Table3['ETIM Standard'] == material, 'Category'].iloc[0])
                    except:
                        material_category_NLSfB.append("Unknown")

            material_category_NLSfB_existing = []
            for material_existing in materials_existing:
                try:
                    material_existing = (material_existing.split('_', 2))[1]
                    material_existing = material_existing.lower()
                    material_category_NLSfB_existing.append(
                        NLSfB_Table3.loc[NLSfB_Table3['Class-tekstcodenotatie'] == material_existing, 'Category'].iloc[
                            0])
                except:
                    material_category_NLSfB_existing.append("Unknown")

            entity_material_status_volume = {}
            entity_material_status_area = {}
            code_sta_vol = {}
            code_vol = {}
            entity_material_status_volume_area = {}

            for entity_existing, material_existing, status_existing,  quantity_existing in zip(
                    entity_category_eixsting, material_category_NLSfB_existing, status_existing,
                     mass_exiting):
                if status_existing == "4" or status_existing == "2":
                    if (entity_existing, status_existing) in code_sta_vol:
                        code_sta_vol[(entity_existing, status_existing)] += quantity_existing

                    else:
                        code_sta_vol[(entity_existing, status_existing)] = quantity_existing

                    if entity_existing in code_vol:
                        code_vol[entity_existing] += quantity_existing
                    else:
                        code_vol[entity_existing] = quantity_existing

                    if (
                            entity_existing, material_existing, status_existing) in entity_material_status_volume:
                        entity_material_status_volume[
                            (entity_existing, material_existing, status_existing)] += quantity_existing
                    else:
                        entity_material_status_volume[
                            (entity_existing, material_existing, status_existing)] = quantity_existing



            for entity, material, status,  quantity in zip(entity_category, material_category_NLSfB, status_total,
                                                                  mass_total):
                if status == "1" or status == "3":
                    if (entity, status) in code_sta_vol:
                        code_sta_vol[(entity, status)] += quantity
                    else:
                        code_sta_vol[(entity, status)] = quantity

                    if entity in code_vol:
                        code_vol[entity] += quantity
                    else:
                        code_vol[entity] = quantity

                    if (entity, material, status) in entity_material_status_volume:
                        entity_material_status_volume[(entity, material, status)] += quantity
                    else:
                        entity_material_status_volume[(entity, material, status)] = quantity




            materials_in_entity_analysis(code_vol, code_sta_vol, entity_material_status_volume)
            self.materialwindow_NLSfB.canvas.draw()
            plt.close()

        else:
            self.materialwindow_NAAKT.figure = plt.figure()
            self.materialwindow_NAAKT.canvas = FigureCanvas(self.materialwindow_NAAKT.figure)
            layout = QVBoxLayout()
            self.materialwindow_NAAKT.enity_circularity.setLayout(layout)
            layout.addWidget(self.materialwindow_NAAKT.canvas)

            material_category_NAAKT = []
            for material in materials:
                try:
                    material = (material.split('_', 2))[0]
                    material_category_NAAKT.append(
                        material)
                except:
                    material_category_NAAKT.append("Unknown")

            material_category_NAAKT_existing = []
            for material_existing in materials_existing:
                try:
                    material_existing = (material_existing.split('_', 2))[0]
                    material_category_NAAKT_existing.append(
                        material_existing)
                except:
                    material_category_NAAKT_existing.append("Unknown")

            entity_material_status_volume = {}
            entity_material_status_area = {}
            code_sta_vol = {}
            code_vol = {}
            entity_material_status_volume_area = {}

            for entity_existing, material_existing, status_existing, volume_existing, quantity_existing in zip(
                    entity_category_eixsting, material_category_NAAKT_existing, status_existing,
                    volumes_existing, mass_exiting):
                if status_existing == "4" or status_existing == "2":
                    if (entity_existing, status_existing) in code_sta_vol:
                        code_sta_vol[(entity_existing, status_existing)] += quantity_existing

                    else:
                        code_sta_vol[(entity_existing, status_existing)] = quantity_existing

                    if entity_existing in code_vol:
                        code_vol[entity_existing] += quantity_existing
                    else:
                        code_vol[entity_existing] = quantity_existing

                    if (
                            entity_existing, material_existing, status_existing) in entity_material_status_volume:
                        entity_material_status_volume[
                            (entity_existing, material_existing, status_existing)] += quantity_existing
                    else:
                        entity_material_status_volume[
                            (entity_existing, material_existing, status_existing)] = quantity_existing

                    if (
                            entity_existing, material_existing, status_existing) in entity_material_status_area:
                        entity_material_status_area[
                            (entity_existing, material_existing, status_existing)] += volume_existing
                    else:
                        entity_material_status_area[
                            (entity_existing, material_existing, status_existing)] = volume_existing

            for entity, material, status, volume, quantity in zip(entity_category, material_category_NAAKT, status,
                                                                  volumes, mass):
                if status == "1" or status == "3":
                    if (entity, status) in code_sta_vol:
                        code_sta_vol[(entity, status)] += quantity
                    else:
                        code_sta_vol[(entity, status)] = quantity

                    if entity in code_vol:
                        code_vol[entity] += quantity
                    else:
                        code_vol[entity] = quantity

                    if (entity, material, status) in entity_material_status_volume:
                        entity_material_status_volume[(entity, material, status)] += quantity
                    else:
                        entity_material_status_volume[(entity, material, status)] = quantity

                    if (entity, material, status) in entity_material_status_area:
                        entity_material_status_area[(entity, material, status)] += volume
                    else:
                        entity_material_status_area[(entity, material, status)] = volume
            for (entity, material, status), quantity1 in entity_material_status_volume.items():
                for (entity_1, material_1, status_1), volume1 in entity_material_status_area.items():
                    if entity == entity_1 and material == material_1 and status == status_1:
                        entity_material_status_volume_area[(entity, material, status)] = (quantity1, volume1)

            materials_in_entity_analysis(code_vol, code_sta_vol, entity_material_status_volume_area)

            self.materialwindow_NAAKT.canvas.draw()
            plt.close()

    def help(self):
        self.switch_window5.emit()

    def open_IFC(self):

        # open a file path
        ifc_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open IFC file', '',
                                                         'Industry Foundation Classes(*.ifc)')
        self.file_path = ifc_path
        # Display the name of the uploaded IFC file
        self.IFCFilePath.setText(os.path.basename(ifc_path[0]))

        try:
            self.canvas1.InitDriver()
            ifc_file = ifcopenshell.open((self.file_path_1)[0])
            ifc_file_1 = ifcopenshell.open((self.file_path)[0])


            products = ifc_file.by_type("IfcBuildingElement")
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow1 = []
            lst_Arrow2 = []
            lst_Arrow3 = []
            lst_Arrow4 = []
            lst_Arrow5 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "2":
                    lst_Arrow2.append(guid)
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)
                if status == "3":
                    lst_Arrow3.append(guid)
                if status == "4":
                    lst_Arrow4.append(guid)
                if status == "5":
                    lst_Arrow5.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "2":
                    lst_Arrow2.append(guid)
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)
                if status == "3":
                    lst_Arrow3.append(guid)
                if status == "4":
                    lst_Arrow4.append(guid)
                if status == "5":
                    lst_Arrow5.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)

            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)
            self.instruction.setText("*Press 'W' for setting wireframe mode; Press 'S' for setting shaded mode")
            self.arrow_tab()


            self.disassmebly_3D()


        except:
            pass
            '''
            connection = IFCInput(ifc_file_1).connection_type()
            accessibility = IFCInput(ifc_file_1).accessibility_level()

            if not all (value == "Unknown" for value in connection) and all (value == "Unknown" for value in accessibility):

                self.canvas10.InitDriver()
                connection = list(map(lambda x: x.replace('EV003046_Glue', '0.1'), connection))
                connection = list(map(lambda x: x.replace('EV001391 _cast-in-situ concrete', '0.1'), connection))
                connection = list(map(lambda x: x.replace('EV020482_Bolt and Nut Connection', '0.8'), connection))
                connection = list(map(lambda x: x.replace('Unknown', '0.1'), connection))
                accessibility = list(
                    map(lambda x: x.replace('EVXXXXX2_Accessible with additional actions that do not cause damage', '0.8'),
                        accessibility))
                accessibility = list(map(lambda x: x.replace('EVXXXXX5_Not accessible', '0.1'), accessibility))
                #accessibility = list(map(lambda x: x.replace('EVXXXXXX_Not accessible', '0.1'), accessibility))
                accessibility = list(
                    map(lambda x: x.replace('EVXXXXX3_Accessible with additional actions with fully repairable damage',
                                            '0.6'),
                        accessibility))
                accessibility = list(map(lambda x: x.replace('Unknown', '0.1'), accessibility))

                product_disassembly = []
                for connection_1, accessibility_1 in zip(connection, accessibility):
                    try:
                        # try to calcualte the disassemly value when both values of connection and accessibility are valid (a number)
                        # otherwise (unknown), use the worse score (0.1)
                        disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / float(accessibility_1)))
                    except:
                        try:
                            disassembly_1 = 2 / ((1 / 0.1) + (1 / float(accessibility_1)))
                        except:
                            try:
                                disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / 0.1))
                            except:
                                disassembly_1 = 0.1
                    product_disassembly.append((round(disassembly_1, 2)))


                disassembly_level_1 = []
                disassembly_level_2 = []
                disassembly_level_3 = []
                disassembly_level_4 = []
                disassembly_level_5 = []

                for guid, disassembly in zip(guids_products_1, product_disassembly):
                    if 0 < disassembly < 0.2:
                        disassembly_level_1.append(guid)
                    if 0.2 <= disassembly < 0.4:
                        disassembly_level_2.append(guid)
                    if 0.4 <= disassembly < 0.6:
                        disassembly_level_3.append(guid)
                    if 0.6 <= disassembly < 0.8:
                        disassembly_level_4.append(guid)
                    if 0.8 <= disassembly <= 1:
                        disassembly_level_5.append(guid)

                for product_1 in products_1:
                    if product_1.Representation:
                        shape = ifcopenshell.geom.create_shape(settings, product_1).geometry
                        self.canvas10.Show(product_1.GlobalId, shape, None)
                        if product_1.GlobalId in disassembly_level_2:
                            self.canvas10.clr_Arrow2(product_1.GlobalId)
                        if product_1.GlobalId in disassembly_level_1:
                            self.canvas10.clr_Arrow1(product_1.GlobalId)
                        if product_1.GlobalId in disassembly_level_4:
                            self.canvas10.clr_Arrow4(product_1.GlobalId)
                        if product_1.GlobalId in disassembly_level_5:
                            self.canvas10.clr_Arrow5(product_1.GlobalId)
                        if product_1.GlobalId in disassembly_level_3:
                            self.canvas10.clr_Arrow3(product_1.GlobalId)
                '''

    def open_IFC_1(self):
        ifc_path_1 = QtWidgets.QFileDialog.getOpenFileName(self, 'Open IFC file', '',
                                                           'Industry Foundation Classes(*.ifc)')
        self.file_path_1 = ifc_path_1
        self.IFCFilePath_1.setText(os.path.basename(ifc_path_1[0]))


        try:
            self.canvas1.InitDriver()
            ifc_file = ifcopenshell.open((self.file_path)[0])
            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])

            products = ifc_file.by_type("IfcBuildingElement")
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow1 = []
            lst_Arrow2 = []
            lst_Arrow3 = []
            lst_Arrow4 = []
            lst_Arrow5 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "2":
                    lst_Arrow2.append(guid)
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)
                if status == "3":
                    lst_Arrow3.append(guid)
                if status == "4":
                    lst_Arrow4.append(guid)
                if status == "5":
                    lst_Arrow5.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "2":
                    lst_Arrow2.append(guid)
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)
                if status == "3":
                    lst_Arrow3.append(guid)
                if status == "4":
                    lst_Arrow4.append(guid)
                if status == "5":
                    lst_Arrow5.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)

            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)


            self.instruction.setText( "*Press 'W' for setting wireframe mode; Press 'S' for setting shaded mode")
            self.arrow_tab()
            self.disassmebly_3D()

        except:
            return

    def disassmebly_3D(self):

        ifc_file = ifcopenshell.open((self.file_path)[0])

        products = ifc_file.by_type("IfcBuildingElement")
        connection = IFCInput(ifc_file).connection_type()
        accessibility = IFCInput(ifc_file).accessibility_level()
        guids_products = IFCInput(ifc_file).product_guids()
        self.canvas10.InitDriver()
        if all(value == "Unknown" for value in connection) and all(value == "Unknown" for value in accessibility):
            pass
        else:
            connection = list(map(lambda x: x.replace('EV003046_Glue', '0.1'), connection))
            connection = list(map(lambda x: x.replace('EV001391 _cast-in-situ concrete', '0.1'), connection))
            connection = list(map(lambda x: x.replace('EV020482_Bolt and Nut Connection', '0.8'), connection))
            connection = list(map(lambda x: x.replace('Unknown', '0.1'), connection))
            accessibility = list(
                map(lambda x: x.replace('EVXXXXX2_Accessible with additional actions that do not cause damage',
                                        '0.8'),
                    accessibility))
            accessibility = list(map(lambda x: x.replace('EVXXXXX5_Not accessible', '0.1'), accessibility))
            # accessibility = list(map(lambda x: x.replace('EVXXXXXX_Not accessible', '0.1'), accessibility))
            accessibility = list(
                map(lambda x: x.replace('EVXXXXX3_Accessible with additional actions with fully repairable damage',
                                        '0.6'),
                    accessibility))
            accessibility = list(map(lambda x: x.replace('Unknown', '0.1'), accessibility))


            product_disassembly = []
            for connection_1, accessibility_1 in zip(connection, accessibility):
                try:
                    # try to calcualte the disassemly value when both values of connection and accessibility are valid (a number)
                    # otherwise (unknown), use the worse score (0.1)
                    disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / float(accessibility_1)))
                except:
                    try:
                        disassembly_1 = 2 / ((1 / 0.1) + (1 / float(accessibility_1)))
                    except:
                        try:
                            disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / 0.1))
                        except:
                            disassembly_1 = 0.1
                product_disassembly.append((round(disassembly_1, 2)))

            disassembly_level_1 = []
            disassembly_level_2 = []
            disassembly_level_3 = []
            disassembly_level_4 = []
            disassembly_level_5 = []

            for guid, disassembly in zip(guids_products, product_disassembly):
                if 0 < disassembly < 0.2:
                    disassembly_level_1.append(guid)
                if 0.2 <= disassembly < 0.4:
                    disassembly_level_2.append(guid)
                if 0.4 <= disassembly < 0.6:
                    disassembly_level_3.append(guid)
                if 0.6 <= disassembly < 0.8:
                    disassembly_level_4.append(guid)
                if 0.8 <= disassembly <= 1:
                    disassembly_level_5.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas10.Show(product.GlobalId, shape, None)
                    if product.GlobalId in disassembly_level_2:
                        self.canvas10.clr_Arrow2(product.GlobalId)
                    if product.GlobalId in disassembly_level_1:
                        self.canvas10.clr_Arrow1(product.GlobalId)
                    if product.GlobalId in disassembly_level_4:
                        self.canvas10.clr_Arrow4(product.GlobalId)
                    if product.GlobalId in disassembly_level_5:
                        self.canvas10.clr_Arrow5(product.GlobalId)
                    if product.GlobalId in disassembly_level_3:
                        self.canvas10.clr_Arrow3(product.GlobalId)

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, "Exit CircularityAssessmentTool", "Are you sure to exit?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    # filter new materials in 3D model, where new materials are colored with red, and the rest of products are non-colored
    def new_materials(self):
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow1 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "1" or status == "EV000001_New":
                    lst_Arrow1.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow1:
                        self.canvas1.clr_Arrow1(product.GlobalId)
        except:
            return

    def reused_samebuilding(self):
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow4 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "4":
                    lst_Arrow4.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "4":
                    lst_Arrow4.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow4:
                        self.canvas1.clr_Arrow4(product.GlobalId)
        except:
            return

    def waste(self):
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow2 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "2":
                    lst_Arrow2.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "2":
                    lst_Arrow2.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow2:
                        self.canvas1.clr_Arrow2(product.GlobalId)
        except:
            return

    def reused_oldbuilding(self):
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow3 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "3":
                    lst_Arrow3.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "3":
                    lst_Arrow3.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)
            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow3:
                        self.canvas1.clr_Arrow3(product.GlobalId)
        except:
            return

        '''
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow3 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()
            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "3":
                    lst_Arrow3.append(guid)
                    for product in products:
                        if product.Representation:
                            for x in lst_Arrow3:
                                self.canvas1.clr_Arrow3(x)
                else:
                    for product in products:
                        if product.Representation:
                            self.canvas1.non_color(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "3":
                    lst_Arrow3.append(guid)
                    for product in products_1:
                        if product.Representation:
                            for x in lst_Arrow3:
                                self.canvas1.clr_Arrow3(x)
                else:
                    for product in products_1:
                        if product.Representation:
                            self.canvas1.non_color(guid)

        except:
            return
        '''

    def recovery_anotherbuilding(self):
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            products = ifc_file.by_type("IfcBuildingElement")

            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products_1 = ifc_file_1.by_type("IfcBuildingElement")

            lst_Arrow5 = []

            guids_products = IFCInput(ifc_file).product_guids()
            status_products = IFCInput(ifc_file).product_status()

            guids_products_1 = IFCInput(ifc_file_1).product_guids()
            status_products_1 = IFCInput(ifc_file_1).product_status()

            for guid, status in zip(guids_products, status_products):
                if status == "5":
                    lst_Arrow5.append(guid)

            for guid, status in zip(guids_products_1, status_products_1):
                if status == "5":
                    lst_Arrow5.append(guid)

            for product in products:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
            for product in products_1:
                if product.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, product).geometry
                    self.canvas1.Show(product.GlobalId, shape, None)
                    if product.GlobalId in lst_Arrow5:
                        self.canvas1.clr_Arrow5(product.GlobalId)
        except:
            return

    def arrow_tab(self):
        material_standard = self.standard.currentText()
        self.figure = plt.figure()
        self.canvas3 = FigureCanvas(self.figure)
        layout3 = QVBoxLayout()
        self.widget10.setLayout(layout3)
        layout3.addWidget(self.canvas3)
        try:
            ifc_file = ifcopenshell.open((self.file_path)[0])
            ifc_file_1 = ifcopenshell.open((self.file_path_1)[0])
            products = ifc_file.by_type("IfcBuildingElement")
            products_existing = ifc_file_1.by_type(("IfcBuildingElement"))

            status = IFCInput(ifc_file).product_status()
            #status= list(map(lambda x: x.replace('EV000001_New', '1'), status))
            status_existing = IFCInput(ifc_file_1).product_status()

            recycled_value = IFCInput(ifc_file).recycled_percentage()

            volumes = IFCInput(ifc_file).product_quantity()[0]
            volumes_existing = IFCInput(ifc_file_1).product_quantity()[0]

            mass = IFCInput(ifc_file).product_weight()
            mass_existing = IFCInput(ifc_file_1).product_weight()

            materials = IFCInput(ifc_file).material_properties()[0]
            materials_ETIM = IFCInput(ifc_file).material_properties()[9]

            mass_ETIM = IFCInput(ifc_file).material_properties()[8]
            materials_volumes = IFCInput(ifc_file).material_properties()[1]

            material_status = IFCInput(ifc_file).material_properties()[2]
            status_ETIM = IFCInput(ifc_file).material_properties()[6]
            #status_ETIM = list(map(lambda x: x.replace('EV000001_New', '1'), status_ETIM))

            # for LOD<200, when only volume information is available without materials information (no density or mass)
            sta_volume_sum = {}
            for key1, value in zip(status, volumes):
                if key1 in sta_volume_sum:
                    sta_volume_sum[key1] += value
                else:
                    sta_volume_sum[key1] = value

            sta_volume_existing_sum = {}
            for key, value1 in zip(status_existing, volumes_existing):
                if key in sta_volume_existing_sum:
                    sta_volume_existing_sum[key] += value1
                else:
                    sta_volume_existing_sum[key] = value1

            project_volume_status = {}
            for key1, value in sta_volume_existing_sum.items():
                for key2, value1 in sta_volume_sum.items():
                    if key1 == "4":
                        project_volume_status[key1] = value
                    if key1 == "2":
                        project_volume_status[key1] = value
                    if key1 == "5":
                        project_volume_status[key1] = value
                    if key2 == "1":
                        project_volume_status[key2] = value1
                    if key2 == "3":
                        project_volume_status[key2] = value1


            # for LOD>200, when mass information is available

            sta_mass_sum = {}
            for key1, value in zip(status, mass):
                if key1 in sta_mass_sum:
                    sta_mass_sum[key1] += value
                else:
                    sta_mass_sum[key1] = value


            sta_mass_existing_sum = {}
            for key1, value in zip(status_existing, mass_existing):
                if key1 in sta_mass_existing_sum:
                    sta_mass_existing_sum[key1] += value
                else:
                    sta_mass_existing_sum[key1] = value


            project_material_status = {}
            for key1, value in sta_mass_existing_sum.items():
                for key2, value1 in sta_mass_sum.items():
                    if key1 == "4":
                        project_material_status[key2] = value1
                    if key1 == "2":
                        project_material_status[key1] = value
                    if key1 == "5":
                        project_material_status[key1] = value
                    if key2 == "1":
                        project_material_status[key2] = value1
                    if key2 == "3":
                        project_material_status[key2] = value1

            project_material_status_volume = {}
            for key1, value in sta_mass_existing_sum.items():
                for key2, value1 in sta_mass_sum.items():
                    if key1 == "4":
                        project_material_status_volume [key2] = value1
                    if key1 == "2":
                        project_material_status_volume [key1] = value
                    if key1 == "5":
                        project_material_status_volume [key1] = value
                    if key2 == "1":
                        project_material_status_volume [key2] = value1
                    if key2 == "3":
                        project_material_status_volume [key2] = value1

            New_value = 0
            Existing_value = 0
            Demolished_value = 0
            Reuse_from_old_building = 0
            Recovery_in_another_building = 0

            # check if the mass of materials are available, if not, calculate the circularity performance based on volume

            if all (value == 0 for value in mass):
                for key, value in project_volume_status.items():
                    if key == '1':
                        New_value += value
                    if key == '2':
                        Demolished_value += value
                    if key == '3':
                        Reuse_from_old_building += value
                    if key == '4':
                        Existing_value += value
                    if key == '5':
                        Recovery_in_another_building += value

            else:
                for key, value in project_material_status.items():
                    if key == '1':
                        New_value += value
                    if key == '2':
                        Demolished_value += value
                    if key == '3':
                        Reuse_from_old_building += value
                    if key == '4':
                        Existing_value += value
                    if key == '5':
                        Recovery_in_another_building += value


            draw_five_arrows(New_value, Existing_value, Demolished_value, Reuse_from_old_building,
                             Recovery_in_another_building)
            self.canvas3.draw()
            plt.close()

            '''
            # calculate the volume/mass of each arrow
            New_value_volume = 0
            Existing_value_volume = 0
            Demolished_value_volume = 0
            Reuse_from_old_building_volume = 0
            Recovery_in_another_building_volume = 0


            if all (value == 0 for value in mass):
                for key, value in zip(status, volumes):
                    if key == "1":
                        New_value_volume = New_value_volume + value
                    if key == "3":
                        Reuse_from_old_building_volume = Reuse_from_old_building_volume + value
                    if key == "2":
                        Demolished_value_volume = Demolished_value_volume + value
                    if key == "5":
                        Recovery_in_another_building_volume = Recovery_in_another_building_volume + value


                for key, value in zip(status_existing, volumes_existing):
                    if key == "2":
                        Demolished_value_volume = Demolished_value_volume + value
                    if key == "5":
                        Recovery_in_another_building_volume = Recovery_in_another_building_volume + value
                    if key == "4":
                        Existing_value_volume = Existing_value_volume + value
                    if key == "1":
                        New_value_volume = New_value_volume + value
                    if key == "3":
                        Reuse_from_old_building_volume = Reuse_from_old_building_volume + value
            else:
                for key, value in zip(status, mass):
                    if key == "1":
                        New_value_volume = New_value_volume + value
                    if key == "3":
                        Reuse_from_old_building_volume = Reuse_from_old_building_volume + value
                    if key == "2":
                        Demolished_value_volume = Demolished_value_volume + value
                    if key == "5":
                        Recovery_in_another_building_volume = Recovery_in_another_building_volume + value

                for key, value in zip(status_existing, mass_existing):
                    if key == "2":
                        Demolished_value_volume = Demolished_value_volume + value
                    if key == "5":
                        Recovery_in_another_building_volume = Recovery_in_another_building_volume + value
                    if key == "4":
                        Existing_value_volume = Existing_value_volume + value
                    if key == "1":
                        New_value_volume = New_value_volume + value
                    if key == "3":
                        Reuse_from_old_building_volume = Reuse_from_old_building_volume + value
            '''

            # presenting the quantity (mass and volume) of each arrow
            # volume information is accurate based on BIM model
            # mass information may be samller, because some of components did not assign with correct/standard material information and the density of materials is also a rough data
            if all (value == 0 for value in mass):
                self.arrow_1.setText(str("%.2f m3" % (New_value)))
                self.arrow_2.setText(str("%.2f m3" % (Demolished_value)))
                self.arrow_3.setText(str("%.2f m3" % (Reuse_from_old_building)))
                self.arrow_4.setText(str("%.2f m3" % (Existing_value)))
                self.arrow_5.setText(str("%.2f m3" % (Recovery_in_another_building)))
            else:
                self.arrow_1.setText(str("%.2f t" % (New_value/1000)))
                self.arrow_2.setText(str("%.2f t" % (Demolished_value/1000)))
                self.arrow_3.setText(str("%.2f t" % (Reuse_from_old_building/1000)))
                self.arrow_4.setText(str("%.2f t" % (Existing_value/1000)))
                self.arrow_5.setText(str("%.2f t" % (Recovery_in_another_building/1000)))

            # calculate the circularity value
            #calculate circularity performance based on volume during the stage of early design with LOD < 200
            if len(materials) == 0 and len(materials_ETIM) == 0:
                circularity_value = (
                                            Existing_value * 1
                                            + Reuse_from_old_building * 0.5 + Recovery_in_another_building * 0.5) / (
                                            New_value + Demolished_value +
                                            Existing_value + Reuse_from_old_building
                                            + Recovery_in_another_building)
            else:
                if material_standard == "NL-SfB Table 3":
                    material_mass = []
                    for material, volume in zip(materials, materials_volumes):
                        try:
                            code = (material.split('_', 2))[1]
                            code = code.lower()
                            material_density = \
                                NLSfB_Table3.loc[
                                    NLSfB_Table3['Class-tekstcodenotatie'] == code, 'Density (kg/m3)'].iloc[0]
                            material_mass.append((material_density * volume))
                        except:
                            material_mass.append((1000 * volume))

                    status_total = material_status+ status_ETIM
                    mass_total = material_mass + mass_ETIM
                    material_total = materials + materials_ETIM


                    if New_value != 0:
                        # creating a dic to sum the volume of material with different status
                        material_status_volume = {}
                        for key1, key2, value in zip(material_total, status_total, mass_total):
                            if (key1, key2) in material_status_volume:
                                material_status_volume[(key1, key2)] += value
                            else:
                                material_status_volume[(key1, key2)] = value


                        # etract the volume information of each new material (status=1) and translate the code to real material name

                        new_material_volume = {}
                        for (key1, key2), value in material_status_volume.items():
                            if key2 == "1":
                                NL_SfB_File = pd.read_excel("External database.xlsx",
                                                            sheet_name="NL-SfB_Tabel 3")
                                try:
                                    code = (key1.split('_', 2))[1]
                                    code = code.lower()
                                    material_category = \
                                        NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Category'].iloc[0]
                                    new_material_volume[(material_category)] = float(value)
                                except:
                                    try:
                                        code = (key1.split('_', 2))[0]
                                        material_category = \
                                            NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'ETIM Standard'].iloc[0]
                                        new_material_volume[(material_category)] = float(value)
                                    except:
                                        material_category = "Unknown"
                                        new_material_volume[(material_category)] = float(value)


                        weight_recycled_status = {}

                        for key1, key2, value in zip(mass, recycled_value, status):
                            weight_recycled_status[(key1, key2)] = value

                        recycled_weight = 0
                        for (key1, key2), value in weight_recycled_status.items():
                            if value == "1":
                                recycled_weight += key1 * key2

                        # calculate the weight of bio-based materials from new materials
                        material_status_volume = {}
                        for key1, key2, value in zip(material_total, status_total, mass_total):
                            if (key1, key2) in material_status_volume:
                                material_status_volume[(key1, key2)] += value
                            else:
                                material_status_volume[(key1, key2)] = value

                        # etract the volume information of each new material (status=1) and translate the code to real material name
                        new_material_volume = {}
                        for (key1, key2), value in material_status_volume.items():
                            if key2 == "1":
                                NL_SfB_File = pd.read_excel("External database.xlsx",
                                                            sheet_name="NL-SfB_Tabel 3")
                                try:
                                    code = (key1.split('_', 2))[1]
                                    code = code.lower()
                                    material_category = \
                                        NL_SfB_File.loc[NL_SfB_File['Class-tekstcodenotatie'] == code, 'Category'].iloc[
                                            0]
                                    if key1 not in new_material_volume:
                                        new_material_volume[(material_category)] = (value)
                                    else:
                                        new_material_volume[(material_category)] += (value)
                                except:
                                    try:
                                        code = (key1.split('_', 2))[0]
                                        material_category = \
                                            NL_SfB_File.loc[NL_SfB_File['ETIM Standard'] == code, 'Category'].iloc[0]
                                        new_material_volume[(material_category)] = value
                                    except:
                                        material_category = "Unknown"
                                        new_material_volume[(material_category)] = (value)

                        biomaterials = 0

                        for key, value in new_material_volume.items():
                            if key == "Organic Materials":
                                biomaterials += value

                        if biomaterials >= recycled_weight:
                            circular_materials = biomaterials
                        else:
                            circular_materials = recycled_weight


                if material_standard == "NAA.K.T":

                    material_mass = []
                    for material, volume in zip(materials, materials_volumes):
                        try:
                            material_density = \
                                NLSfB_Table3.loc[
                                    NLSfB_Table3['Class-tekstcodenotatie'] == material, 'Density (kg/m3)'].iloc[0]
                            material_mass.append((material_density * volume))
                        except:
                            # assign an average density for unknown materials
                            material_mass.append((1000 * volume))

                    if New_value != 0:
                        # creating a dic to sum the volume of material with different status
                        material_status_volume = {}
                        for key1, key2, value in zip(materials, material_status, material_mass):
                            if (key1, key2) in material_status_volume:
                                material_status_volume[(key1, key2)] += value
                            else:
                                material_status_volume[(key1, key2)] = value

                        # etract the volume information of each new material (status=1) and translate the code to real material name
                        new_material_volume = {}
                        for (key1, key2), value in material_status_volume.items():
                            if key2 == "1":
                                # extract the material name in the first location based on NAA.KT
                                try:
                                    name = (key1.split('_', 2))[0]
                                    new_material_volume[name] = value
                                except:
                                    name = "Unknown"
                                    new_material_volume[(name)] = value

                        New_biomaterial = bio_technimaterial_NAAKT(new_material_volume)[0]
                        New_technimaterial = bio_technimaterial_NAAKT(new_material_volume)[1]
                        Recycled_biomaterial = 0
                        Recycled_technimaterial = 0
                    else:
                        New_biomaterial = 0
                        New_technimaterial = 0
                        Recycled_biomaterial = 0
                        Recycled_technimaterial = 0


                circularity_value = (
                                            circular_materials*0.25 +  Existing_value* 1
                                            + Reuse_from_old_building * 0.5 + Recovery_in_another_building * 0.5) / (
                                            New_value + Demolished_value +
                                            Existing_value + Reuse_from_old_building
                                            + Recovery_in_another_building)


                #self.horizontalSlider.setValue(float(circularity_value * 100))

            self.Value.setText(str("%.3f" % circularity_value))




        except:
            QtWidgets.QMessageBox.warning(self, "Circularity Assessment Fail",
                                          "Please go to [File] <- [Open] <-[IFCfile_New]/[IFCfile_Existing]"
                                          " to upload IFC files\n"
                                          '\n'
                                          "Check [Help] about IFC guidelines")
        try:
            #disassembility assessment only need to do for the new building
            connection = IFCInput(ifc_file).connection_type()
            accessibility = IFCInput(ifc_file).accessibility_level()
            weight = IFCInput(ifc_file).product_weight()

            if all(value == "Unknown" for value in connection) and all(value == "Unknown" for value in accessibility):
                self.Disassembility_potential.setText("Unknown")
            else:
                connection = list(map(lambda x: x.replace('EV003046_Glue', '0.1'), connection))
                connection = list(map(lambda x: x.replace('EV001391 _cast-in-situ concrete', '0.1'), connection))
                connection = list(map(lambda x: x.replace('EV020482_Bolt and Nut Connection', '0.8'), connection))
                checking = all (item == "Unknown" for item in connection)
                if checking is True:
                    pass
                else:
                    connection = list(map(lambda x: x.replace('Unknown', '0.1'), connection))

                accessibility = list(
                    map(lambda x: x.replace('EVXXXXX2_Accessible with additional actions that do not casue damage',
                                            '0.8'),
                        accessibility))
                accessibility = list(map(lambda x: x.replace('EVXXXXX5_Not accessible', '0.1'), accessibility))
                accessibility = list(
                    map(lambda x: x.replace('EVXXXXX3_Accessible with additional actions with fully repairable damage',
                                            '0.6'),
                        accessibility))
                accessibility = list(map(lambda x: x.replace('Unknown', '0.1'), accessibility))

                product_disassembly = []
                for connection_1, accessibility_1 in zip(connection, accessibility):
                    try:
                        # try to calcualte the disassemly value when both values of connection and accessibility are valid (a number)
                        # otherwise (unknown), use the worse score (0.1)
                        disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / float(accessibility_1)))
                    except:
                        try:
                            disassembly_1 = 2 / ((1 / 0.1) + (1 / float(accessibility_1)))
                        except:
                            try:
                                disassembly_1 = 2 / ((1 / float(connection_1)) + (1 / 0.1))
                            except:
                                disassembly_1 = 0.1
                    product_disassembly.append((round(disassembly_1, 2)))


                disassembly_level = 0


                for disassembly_1, weight_1 in zip(product_disassembly, weight):
                    disassembly_level += disassembly_1 * weight_1

                disassembly_level_overall = round(disassembly_level / sum(weight), 3)
                self.Disassembility_potential.setText(str("%.2f" % disassembly_level_overall))
        except:
            self.Disassembility_potential.setText("Unknown")


        try:
            # for each product, its material circularity and disassmeblity potential should be assessed repsectively



            self.Overall_value.setText(str("%.3f" % (0.5*circularity_value + 0.5*disassembly_level_overall)))
        except:
            self.Overall_value.setText(str("%.3f" % (circularity_value)))

    # Stores the plots in a .png or .pdf file.
    def save_plots(self):
        '''
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        else:
        '''
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, 0, 0, 1381, 1006)
        screenshot.save("circularity results.png")

class Ui_Material_window_NLSfB(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_Material_window_NLSfB, self).__init__()
        loadUi("Material level analysis (NL-SfB).ui", self)
        self.setWindowTitle("Material level analysis (NL-SfB)")

        # attch pictures of material type (eight in total)
        concrete = QPixmap("precast concrete.png")
        self.concrete.setPixmap(concrete)
        self.concrete.setScaledContents(True)

        stone = QPixmap("stone.png")
        self.stone.setPixmap(stone)
        self.stone.setScaledContents(True)

        metal = QPixmap("iron-bar.png")
        self.metal.setPixmap(metal)
        self.metal.setScaledContents(True)

        wood = QPixmap("wood.png")
        self.wood.setPixmap(wood)
        self.wood.setScaledContents(True)

        fiber = QPixmap("Fiber.png")
        self.fiber.setPixmap(fiber)
        self.fiber.setScaledContents(True)

        loose_fill = QPixmap("Loose_fills.png")
        self.loose_fills.setPixmap(loose_fill)
        self.loose_fills.setScaledContents(True)

        glass = QPixmap("glass.png")
        self.glass.setPixmap(glass)
        self.glass.setScaledContents(True)

        others = QPixmap("Other_materials.png")
        self.others.setPixmap(others)
        self.others.setScaledContents(True)

    def display_materialinfo(self):
        self.show()

class Ui_Material_window_NAAKT(QtWidgets.QMainWindow):
    pass

class Controller:
    def __init__(self):
        pass

    def show_login(self):
        self.login = Ui_Login()
        self.login.switch_window1.connect(self.show_renovated)
        self.login.switch_window2.connect(self.show_new_demolished)
        self.login.show()

    def show_renovated(self):
        self.renovated = Ui_Renovation()
        self.renovated.switch_window4.connect(self.back_2)
        self.login.close()
        self.renovated.show()

    def show_new_demolished(self):
        pass

    def back_1(self):
        self.login = Ui_Login()
        self.login.switch_window1.connect(self.show_renovated)
        self.login.switch_window2.connect(self.show_new_demolished)
        self.new_demolished.close()
        self.login.show()

    def back_2(self):
        self.login = Ui_Login()
        self.login.switch_window1.connect(self.show_renovated)
        self.login.switch_window2.connect(self.show_new_demolished)
        self.renovated.close()
        self.login.show()

app = QApplication(sys.argv)
controller = Controller()
controller.show_login()

sys.exit(app.exec())






















