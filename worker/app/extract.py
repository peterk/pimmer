#!/usr/bin/env python
import argparse
import json
import os
import sys
import cv2
import numpy
from image_mining.figure_extraction import FigureExtractor
from image_mining.utils import open_image


def get_enumerated_boxes(image):
    filtered_image = extractor.filter_image(image)
    contours, hierarchy = extractor.find_contours(filtered_image)

    return enumerate(extractor.get_bounding_boxes_from_contours(contours, filtered_image), 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--debug', action="store_true", help="Open debugger for errors")

    parser.add_argument('files', metavar="IMAGE_FILE", nargs="+")

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--interactive', default=False, action="store_true", help="Display visualization windows")
    mode_group.add_argument('--output-directory', default=None, help="Directory to store extracted files")

    parser.add_argument('--save-json', action="store_true", help="Save bounding boxes as JSON files along with extracts")

    extraction_params = parser.add_argument_group("Extraction Parameters")
    extraction_params.add_argument('--canny-threshold', type=int, default=0, help="Canny edge detection threshold (%(type)s, default=%(default)s, 0 to disable)")

    extraction_params.add_argument('--erosion-element', default="rectangle", choices=FigureExtractor.MORPH_TYPE_KEYS, help="Erosion Element (default: %(default)s)")
    extraction_params.add_argument('--erosion-size', type=int, default=0, help="Erosion Size (%(type)s, default=%(default)s, 0 to disable)")

    extraction_params.add_argument('--dilation-element', default="rectangle", choices=FigureExtractor.MORPH_TYPE_KEYS, help="Dilation Element (default: %(default)s)")
    extraction_params.add_argument('--dilation-size', type=int, default=0, help="Dilation Size (%(type)s, default=%(default)s, 0 to disable)")

    args = parser.parse_args()

    if not args.output_directory:
        output_dir = None
    else:
        output_dir = os.path.realpath(args.output_directory)
        if not os.path.isdir(output_dir):
            parser.error("Output directory %s does not exist" % args.output_directory)
        else:
            print("Output will be saved to %s" % output_dir)

    if output_dir is None and not args.interactive:
        parser.error("Either use --interactive or specify an output directory to save results!")

    param_names = [action.dest for action in extraction_params._group_actions]
    params = {k: v for (k, v) in args._get_kwargs() if k in param_names}

    try:
        extractor = FigureExtractor(**params)

        if args.interactive:
            display_images(extractor, args.files)
        else:
            for f in args.files:
                try:
                    base_name, source_image = open_image(f)
                except Exception as e:
                    sys.stderr.write(str(e))
                    continue

                output_base = os.path.join(output_dir, base_name)

                print("Processing %s" % f)

                boxes = []

                for i, bbox in get_enumerated_boxes(source_image):
                    extracted = source_image[bbox.image_slice]
                    extract_filename = os.path.join(output_dir, "%s-%d.jpg" % (output_base, i))
                    print("\tSaving %s" % extract_filename)
                    cv2.imwrite(extract_filename, extracted)

                    boxes.append(bbox.as_dict())

                if args.save_json and boxes:
                    json_data = {"source_image": {"filename": f,
                                                  "dimensions": {"width": source_image.shape[1],
                                                                 "height": source_image.shape[0]}},
                                 "regions": boxes}

                    json_filename = os.path.join(output_dir, "%s.json" % output_base)
                    with open(json_filename, "w", encoding="utf8") as json_f:
                        json.dump(json_data, json_f, allow_nan=False)
                    print("\tSaved extract information to %s" % json_filename)

    except Exception as e:
        if args.debug:
            sys.stderr.write(str(e))
        raise
