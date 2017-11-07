from mask_gen import MaskGenerator
import os
import glob
import shutil
import arcpy
from arcpy import env


class Masker(object):
    def __init__(self, input_data_dir, masked_data_dir, mask_criteria, masking_rule, target_band_suffixes,
                 num_threads=5):
        self.input_data_dir = input_data_dir
        self.masked_data_dir = masked_data_dir

        self.mask_criteria = mask_criteria
        self.masking_rule = masking_rule
        self.target_band_suffixes = target_band_suffixes

        self.num_threads = num_threads
        self.temp_dir = os.path.join(self.input_data_dir, "..", "temp")
        self.temp_masked_dir_name = "masked"

    def execute(self):
        self._create_temp_directory()
        self._create_output_directory()

        env.workspace = self.masked_data_dir + os.path.sep
        env.overwriteOutput = True

        tile_paths = self._get_tile_path_list()

        for tile_path in tile_paths:
            self._create_temp_sub_directories()

            temp_output_dir = os.path.join(self.temp_dir, self.temp_masked_dir_name)

            maskgen = MaskGenerator(tile_path, temp_output_dir, "_mask", self.mask_criteria, self.masking_rule,
                                    self.target_band_suffixes, self.num_threads)
            maskgen.build_mask()

            print  "Tile: {tpath} masking finished!".format(tpath=tile_path)
            self._move_to_pro_directory(os.path.basename(os.path.normpath(tile_path)))

    def _get_tile_path_list(self):
        temp_path = os.path.join(self.input_data_dir, "*")

        return glob.glob(temp_path)

    def _create_output_directory(self):
        try:
            if os.path.exists(self.masked_data_dir):
                shutil.rmtree(self.masked_data_dir)

            os.mkdir(self.masked_data_dir)
        except:
            print "Could not create pst directory"

    def _create_temp_directory(self):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            os.mkdir(self.temp_dir)
        except:
            print "Could not create Temp directory"

    def _create_temp_sub_directories(self):

        temp_masked_dir = os.path.join(self.temp_dir, self.temp_masked_dir_name)
        os.mkdir(temp_masked_dir)

    def _move_to_pro_directory(self, tile):
        # create tile dir within the masked dir
        # move data from Temp
        temp_masked_dir = os.path.join(self.temp_dir, self.temp_masked_dir_name)
        temp_tile_dir = os.path.join(self.temp_dir, tile)
        os.rename(temp_masked_dir, temp_tile_dir)

        masked_tile_dir = os.path.join(self.masked_data_dir, tile)
        shutil.move(temp_tile_dir, masked_tile_dir)

        for temp_dir in glob.glob(os.path.join(self.temp_dir, "*")):
            shutil.rmtree(temp_dir)
