# ArcMODIS-Masker
Masks clouds, water, snow etc. polluted bad quality pixels for large MODIS science datasets using quality assurance data and user defined rules. User has total control over defining the masking criteria.

## Summary
ArcMODIS-Masker was developed with four primary goals.
* A masking tool that works for all MODIS products
* A masking tool that supports bulk MODIS image masking tasks (across multiple MODIS grid cells)
* A tool that does not depend on MODIS product changes
* A simpler masking GUI tool for ArcMap users

A bulk image masking scripting tool and a simpler GUI tool were developed to satisfy those requirements.

## Bulk ArcMODIS-Masker Scripting Tool

This tool can process data across multiple MODIS grid cells (ex: h12v05, h12v04). Each gird cell can contain any number of GeoTiFF (.tif extension) files representing the temporal dimension of data. User can develop the masking rule using the quality bands. Bit encoded quality data fields can be specified using the bit position indices. Complex masking rules can be developed by combining primary rules using AND, OR, XOR, and NOT operations.

Example: This example is for MOD17A3H (v6) Net Primary Production (NPP) dataset.

masker_manager.py script is used to run the ArcMODIS-Masker tool.

Prerequisites:

* Data for each MODIS grid cell should contain within a separate directory (ex: h12v05) and all necessary quality bands and the band to be masked should contain within that directory.
* Each band should have identical suffix for its file name.
  ex: 'QC' for a quality band and 'NPP' for the NPP band. File names will look like 20130101_QC.tif and 20130101_NPP.tif
* Currently support only for GeoTIFF files with 'tif' extension.

Then use the MODIS product's user guide to identify the quality criteria you need. For MOD17A3H, Quality Control (QC) band is chosen for defining masking criteria and two primary rules were identified.

| Filed Name  | Band suffix | Bits | Data Type |Rule |
| ------------- | ------------- |------------- |------------- |------------- |
| Field 1  | QC  | 5 - 7  |Bit Range  |Value in range (000,001)  |
| Field 2  | QC  | 3 - 4  |Bit Value  |Value == 00 |

A suitable data type can be chosen from 'Bit List', 'Bit Range', 'Bit Value', 'Integer List', 'Integer Range', or 'Integer Value'. If you choose bit values, you have provide bit values in the rule. Otherwise convert the bit values you need into base10 integers.

### How to specify bit or integer values in rules:
ex: 

Bit Value -> 101<br/>
Bit List -> 00,01,11<br/>
Bit Range -> 000, 101

Integer Value -> 5<br/>
Integer List -> 0,1,3<br/>
Integer Range -> 0, 5

Rules:

```Python
    criteria = [["Condition1", "QC", "5", "7", "Bit Range", "000,001"],
                ["Condition2", "QC", "3", "4", "Bit Value", "00"]]
```

Final criteria is made combining two rules with a logical operator, "AND" in this case.

```Python
    masking_rule = "Condition1 AND Condition2"
```

Then specify the band to be masked using the file suffix for that band, here it is 'NPP'

```Python
    target_band_suffixes = "NPP"
```

Final code:

```Python
    criteria = [["Condition1", "QC", "5", "7", "Bit Range", "000,001"],
                ["Condition2", "QC", "3", "4", "Bit Value", "00"]]
    masking_rule = "Condition1 AND Condition2"
    target_band_suffixes = "NPP"
    
    msk = Masker(       
        input_data_dir=r"\\<parent dir path>\rawdata",
        masked_data_dir=r"\\<parent dir path>\masked",
        mask_criteria=criteria,
        masking_rule=masking_rule,
        target_band_suffixes=target_band_suffixes,
        num_threads=10)
```

* You can specify any directory for 'masked_data_dir' or the output directory.
* If you choose to go for Python multi-processing, use the `num_threads` for specifying number of processes.

Running the masker:

```Python
    msk.execute()
    print arcpy.GetMessages()
```


## Simple ArcMODIS-Masker GUI Tool for ArcGIS Desktop

This is a simplified GUI tool for masking MODIS images. A single directory containing any number of MODIS images can be processed with this tool. All data and quality bands should be directly under that input directory. You can mix up images from multiple MODIS grid cells in this case, but then you would need to re-organize images into multiple grid cells after processing.

* Follow the tool help messages to understand how to enter your inputs.

* Final rule can be customized using "AND", "OR", "XOR" and "NOT" operators and brackets ("(" and ")").


![Alt text](MaskBuilder_screen1.PNG?raw=true "ArcMODIS Masker Tool")

## Important Information
* [MODIS product table](https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table) - See all the available MODIS products
* [MODIS data download](https://e4ftl01.cr.usgs.gov/) - Download data from the Data pool (go to MOTA, MOLA and MOLT for Terra, Aqua and Combined products). You need a NASA Earth Data account for downloading data.
* [MODIS grid and sinusoidal projection](modis_grid.zip) - Download the MODIS grid (in sinusoidal projection) and sinusoidal projection. You can use this to identify grid cells (tiles) you need to download.
* [MODIS data pre-processing tool](https://github.com/udayaj/ArcMODIS-Prepro) - Use ArcMODIS-Prepro to pre-process downloaded large MODIS datasets. Band subsetting, projection, value scale correction and GeoTIFF conversion functions are available under this tool.
