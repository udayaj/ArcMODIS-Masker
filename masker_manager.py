from masker import Masker
import arcpy


def main():
    # criteria = [["Condition1", "DQC", "0", "1", "Bit Value", "00"],
    #             ["Condition2", "DQC", "0", "1", "Bit Value", "01"],
    #             ["Condition3", "DQC", "6", "7", "Bit Range", "00,01"]]
    # masking_rule = "Condition1 OR (Condition2 AND Condition3)"

    criteria = [["Condition1", "QC", "5", "7", "Bit Range", "000,001"],
                ["Condition2", "QC", "3", "4", "Bit Value", "00"]]
    masking_rule = "Condition1 AND Condition2"
    target_band_suffixes = "NPP"

    msk = Masker(
        # input_data_dir=r"\\test\Aqua\rawdata",
        # masked_data_dir=r"\\test\Aqua\masked",
        input_data_dir=r"Q:\test\Aqua\rawdata",
        masked_data_dir=r"Q:\test\Aqua\masked",
        mask_criteria=criteria,
        masking_rule=masking_rule,
        target_band_suffixes=target_band_suffixes,
        num_threads=10)

    msk.execute()
    print arcpy.GetMessages()


if __name__ == '__main__':
    main()
