from mask_gen import MaskGenerator
import arcpy
import os
import glob


class Toolbox(object):
    def __init__(self):
        self.label = "MODIS Tools"
        self.alias = ""
        self.tools = [MaskBuilder]


class MaskBuilder(object):
    def __init__(self):
        self.label = "MODIS Mask Builder"
        self.description = "Builds masks for MODIS datasets using quality assurance data and user specified rules."
        self.category = "MODIS"
        self.canRunInBackground = True

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName="MODIS Input Data Directory",
            name="input_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Output Directory (masked data)",
            name="output_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Mask File Suffix",
            name="mask_suffix",
            datatype="String",
            parameterType="Optional",
            direction="Input")
        param2.value = "_masked"

        param3 = arcpy.Parameter(
            displayName='Masking Condition(s)',
            name='mask_conditions',
            datatype='GPValueTable',
            parameterType='Required',
            direction='Input')

        param3.columns = [['String', 'Condition'], ['String', 'Band Suffix'], ['String', 'Starting Bit'],
                          ['String', 'Ending Bit'], ['String', 'Value Type'], ['String', 'Value(s)']]
        param3.filters[0].type = 'ValueList'
        param3.filters[0].list = ['Condition1', 'Condition2', 'Condition3', 'Condition4', 'Condition5', 'Condition6',
                                  'Condition7', 'Condition8', 'Condition9', 'Condition10']

        param3.filters[2].type = "ValueList"
        param3.filters[2].list = ["Whole Band", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

        param3.filters[3].type = "ValueList"
        param3.filters[3].list = ["Whole Band", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

        param3.filters[4].type = "String"
        param3.filters[4].list = ['Bit List', 'Bit Range', 'Bit Value', 'Integer List', 'Integer Range',
                                  'Integer Value']

        param3.values = [["Condition1", "QC", "5", "7", "Bit Range", "000,001"],
                         ["Condition2", "QC", "3", "4", "Bit Value", "00"]]

        param4 = arcpy.Parameter(
            displayName="Default Conditional Operator",
            name="default_conditional_operator",
            datatype="String",
            parameterType="Required",
            direction="Input")

        param4.filter.type = "ValueList"
        param4.filter.list = ["AND", "OR", "XOR", "NOT", "Custom"]
        param4.value = "AND"

        param5 = arcpy.Parameter(
            displayName="Masking Rule",
            name="mask_rule",
            datatype="String",
            parameterType="Required",
            direction="Input")
        param5.value = "Condition1 AND Condition2"

        param6 = arcpy.Parameter(
            displayName="Masking Band Name Suffixes",
            name="bands_masked",
            datatype="String",
            parameterType="Required",
            direction="Input")
        param6.value = "NPP"

        params = [param0, param1, param2, param3, param4, param5, param6]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        if parameters[3].altered:
            if parameters[3].values is None:
                parameters[5].value = ""

        if (parameters[4].altered is True) and (parameters[5].altered is not True):
            if parameters[3].values is not None:
                table = parameters[3].values
                list_conditions = []

                for row in table:
                    condition = row[0]
                    list_conditions.append(row[0])
                    bsuffix = row[1]
                    sbit = row[2]
                    ebit = row[3]
                    condition_type = row[4]
                    value_string = row[5]

                str_logical_operator = " X " if parameters[4].value == "Custom" else " " + parameters[4].value + " "
                masking_rule = str_logical_operator.join(list_conditions)
                parameters[5].value = masking_rule

        return

    def updateMessages(self, parameters):
        if parameters[6].altered and (parameters[6].value is not None):
            data_dir = parameters[0].value.value  # unicode(parameters[0].value).encode('unicode-escape')

            band_names = [b.strip() for b in parameters[6].value.split(",")]
            band_names.sort()

            if band_names[0] == "":
                parameters[6].setErrorMessage("Blank band suffix found")

            invalid_bands = []

            for band in band_names:
                search_path = os.path.join(data_dir, "*" + band + ".tif")
                files_found = glob.glob(search_path)
                if (files_found is None) or (len(files_found) == 0):
                    invalid_bands.append(band)

            if len(invalid_bands) > 0:
                str_invalid_bands = " , ".join(invalid_bands)
                parameters[6].setErrorMessage("No bands exist for {0} band suffix(es)".format(str_invalid_bands))

        return

    def execute(self, parameters, messages):
        table = parameters[3].values

        data_dir = parameters[0].value.value  # unicode(parameters[0].value).encode('unicode-escape')
        output_dir = parameters[1].value.value  # unicode(parameters[1].value).encode('unicode-escape')
        arcpy.AddMessage(
            "P0: {0}, P1: {1}, P2: {2}, P4: {3}, P5: {4}, P6: {5}".format(data_dir, output_dir, parameters[2].value,
                                                                          parameters[4].value, parameters[5].value,
                                                                          parameters[6].value))

        maskgen = MaskGenerator(data_dir, output_dir, parameters[2].value, table, parameters[5].value,
                                parameters[6].value, 1)
        maskgen.build_mask()
        return
