import detectron2
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
import glob
import cv2
import numpy as np
from detectron2.engine import DefaultPredictor
from detectron2.data.catalog import Metadata
import os
import json

meta = Metadata(evaluator_type='coco',thing_classes=['Building-Roof', 'Building-Roof', 'Commercial-Flat-Roof', 'Commercial-Slope-Roof', 'Construction-Area', 'Flat Roof',
  'Playground', 'Slope-Flat-Roof', 'Slope-Roof', 'Solar-Flat-Roof', 'Solar-Pannel-Ground', 'Solar-Slope-Roof', 'TreeShading-Slope-Roof', 'Unknownshape-Roof'], 
  thing_dataset_id_to_contiguous_id={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13})

cfg = get_cfg()   

cfg.merge_from_file("data/config.yaml")   
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.4   # set the testing threshold for this model
cfg.MODEL.DEVICE = 'cpu'
cfg.MODEL.WEIGHTS = 'data/model_final.pth'

predictor = DefaultPredictor(cfg) 


class Roofsize:
    def get(self,roof_image_path):
        print(roof_image_path)
        im = cv2.imread(roof_image_path)
        outputs = predictor(im)
        v = Visualizer(im[:, :, ::-1], metadata = meta, scale = 1.0)
        class_name = meta.as_dict()['thing_classes'][int(outputs["instances"].to("cpu").pred_classes[0].numpy())]
        print(outputs)
        pixel_area = outputs["instances"].to("cpu").pred_masks.size()[0]
        
        if pixel_area == 0 :
            print('No Segmentation/Classification')
            roof_area = 0.0
        else:
            zoom_level_multiplier = .281
            roof_area = (np.sqrt(outputs["instances"].to("cpu").pred_masks[0].numpy().sum()* zoom_level_multiplier))
            print(f'Segmented Area : {(np.sqrt(outputs["instances"].to("cpu").pred_masks[0].numpy().sum()* zoom_level_multiplier)):.2f} m')
        
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        segmented_img_filepath = "segmented_images/"+os.path.basename(roof_image_path)
        cv2.imwrite(segmented_img_filepath, out.get_image()[:, :, ::-1])
        panel_area =  0

        if 'Solar' in class_name:
            panel_area = 0
        elif 'Slope' in class_name:
            panel_area = roof_area*0.5
        elif 'Flat' in class_name:
            panel_area = roof_area*0.75
        
        number_of_panels =  round(panel_area / 8,0)

        roof_results = {'segmented_image':segmented_img_filepath, 'roof_size': str(round(roof_area,2)), 'roof_type': class_name, 'panel_area': panel_area , 'panel_count': number_of_panels}

        return json.dumps(roof_results)