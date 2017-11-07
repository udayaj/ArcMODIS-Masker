import arcpy
import os
from arcpy.sa import *
import multiprocessing


class MaskGenerator(object):
    def __init__(self, input_image_dir, output_image_dir, mask_file_suffix, mask_criteria, masking_rule,
                 target_band_names, num_threads=1):
        self.name = "Mask generator"
        self.input_image_dir = input_image_dir
        self.output_image_dir = output_image_dir
        self.mask_file_suffix = mask_file_suffix
        self.mask_criteria = mask_criteria
        self.masking_rule = masking_rule
        self.target_band_names = target_band_names
        self.num_threads = num_threads

    def build_mask(self):

        qa_image_suffixes = set([])
        for row in self.mask_criteria:
            qa_image_suffixes.add(row[1])

        qa_image_suffixes = list(qa_image_suffixes)

        file_list = os.listdir(self.input_image_dir)
        if len(file_list) <= 0:
            arcpy.AddError("No files found !")
            exit(0)

        band_file_count = None
        scene_list = []
        for qa_band_suffix in qa_image_suffixes:

            if len(file_list) <= 0:
                arcpy.AddError("No TIF files found for the {0} band".format(qa_band_suffix))
                exit(0)
            else:
                band_file_list = [f for f in file_list if f.endswith(qa_band_suffix + ".tif")]
                band_file_list.sort()
                if band_file_count is None:
                    band_file_count = len(band_file_list)
                else:
                    if band_file_count != len(band_file_list):
                        arcpy.AddError("Number of files for each quality band are not similar !")
                        exit(0)

                band_file_list = [bfile.replace(qa_band_suffix + ".tif", "") for bfile in band_file_list]
                if len(scene_list) == 0:
                    scene_list = band_file_list
                else:
                    if band_file_list != scene_list:
                        arcpy.AddError(
                            "All quality bands for some images are not available or additional quality images exist !")
                        exit(0)

        arcpy.AddMessage("Ready to build the mask")

        if self.num_threads > 1:
            part_scene_list = self._partition(scene_list, self.num_threads)

            threads = []
            for i in range(self.num_threads):
                worker = multiprocessing.Process(target=self._execute, args=(i, part_scene_list[i],))
                worker.daemon = False
                threads.append(worker)
                worker.start()

            for thread in threads:
                thread.join()
        else:
            # ArcGIS Desktop tool do not work with multi-processing
            self._execute(1, scene_list)

    def _execute(self, thread_id, scene_list):
        arcpy.CheckOutExtension("Spatial")
        print "Thread: {thread_name}".format(thread_name=str(thread_id)) + "\n"

        # loop through all scenes
        for scene in scene_list:

            list_cond_raster = []

            for row in self.mask_criteria:
                # conditon_name = row[0]
                bsuffix = row[1]
                start_bit = int(row[2])
                end_bit = int(row[3])
                value_type = row[4]
                values = [x.strip() for x in row[5].split(",")]
                # bit_field_length = 16 if bsuffix == "QA" else None

                file_path = os.path.join(self.input_image_dir, scene + bsuffix + ".tif")
                raster_band = Raster(file_path)

                cond_raster = None
                cond_string = ""

                # build mask rule
                if value_type == "Bit List":
                    temp1 = raster_band % pow(2, end_bit + 1)
                    temp2 = temp1 >> start_bit

                    cond_string = " | ".join(["(temp2 == {0})".format(str(int(val.strip(), 2))) for val in values])

                elif value_type == "Bit Range":
                    temp1 = raster_band % pow(2, end_bit + 1)
                    temp2 = temp1 >> start_bit
                    cond_string = "(temp2 >= {0}) & (temp2 <= {1})".format(str(int(values[0], 2)),
                                                                           str(int(values[1], 2)))

                elif value_type == "Bit Value":
                    temp1 = raster_band % pow(2, end_bit + 1)
                    temp2 = temp1 >> start_bit
                    cond_string = "(temp2 == {0})".format(str(int(values[0], 2)))

                elif value_type == "Integer List":
                    cond_string = " | ".join(["(raster_band == {0})".format(str(int(val.strip()))) for val in values])

                elif value_type == "Integer Range":
                    cond_string = "(raster_band >= {0}) & (raster_band <= {1})".format(str(int(values[0])),
                                                                                       str(int(values[1])))

                elif value_type == "Integer Value":
                    cond_string = "(raster_band == {0})".format(str(int(values[0])))

                cond_raster = eval(cond_string)
                list_cond_raster.append(cond_raster)

            replace_list = [
                [condition[0], "list_cond_raster[" + str(int(condition[0].replace("Condition", "")) - 1) + "]"] for
                condition in self.mask_criteria]

            m_rule = self.masking_rule
            for ri in replace_list:
                m_rule = m_rule.replace(ri[0], ri[1])

            m_rule = m_rule.replace("AND", "&")
            m_rule = m_rule.replace("OR", "|")
            m_rule = m_rule.replace("XOR", "^")
            m_rule = m_rule.replace("NOT", "~")
            # arcpy.AddMessage(m_rule)

            # build mask
            mask_raster = eval(m_rule)

            ## TODO : comment these lines if you don't need to save the mask files
            ## save mask
            # if self.mask_file_suffix is not None and self.mask_file_suffix != "":
            #     mask_file_path = os.path.join(self.output_image_dir, scene + self.mask_file_suffix + ".tif")
            # else:
            #     mask_file_path = os.path.join(self.output_image_dir, scene + ".tif")
            # mask_raster.save(mask_file_path)

            # ---------------Start mask applying-------------------------
            # get bands to be masked
            target_bands = [b.strip() for b in self.target_band_names.split(",")]

            for tband in target_bands:
                # ex: evi, ndvi
                tband_file_path = os.path.join(self.input_image_dir, scene + tband + ".tif")
                tband_raster = Raster(tband_file_path)

                # do mask
                masked_out_raster = SetNull(mask_raster == 0, tband_raster)
                masked_file_path = os.path.join(self.output_image_dir, scene + tband + ".tif")
                masked_out_raster.save(masked_file_path)

        arcpy.CheckInExtension("Spatial")

    @staticmethod
    def _partition(lst, n):
        return [lst[i::n] for i in range(n)]
