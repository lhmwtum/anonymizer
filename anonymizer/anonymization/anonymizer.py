import json
from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm

from anonymizer.detection import Detector
from anonymizer.obfuscation import Obfuscator


def load_np_image(image_path):
    image = Image.open(image_path).convert("RGB")
    np_image = np.array(image)
    return np_image


def save_np_image(image, image_path):
    pil_image = Image.fromarray((image).astype(np.uint8), mode="RGB")
    pil_image.save(image_path)


def save_detections(detections, detections_path):
    json_output = []
    for box in detections:
        json_output.append(
            {
                "y_min": box.y_min,
                "x_min": box.x_min,
                "y_max": box.y_max,
                "x_max": box.x_max,
                "score": box.score,
                "kind": box.kind,
            }
        )

    with open(detections_path, "w") as output_file:
        json.dump(json_output, output_file, indent=2)


# ------------------------------------------------------------------------------
class Anonymizer:
    def __init__(
        self,
        obfuscator: Obfuscator,
        detectors: dict[str, Detector],
        detection_thresholds: dict[str, float],
    ):
        self._obfuscator = obfuscator
        self._detectors = detectors
        self._detection_thresholds = detection_thresholds

    # ----------------
    def anonymize_image(self, image):
        assert set(self._detectors.keys()) == set(
            self._detection_thresholds.keys()
        ), "Detector names must match detection threshold names"

        detected_boxes = []

        for kind, detector in self._detectors.items():
            new_boxes = detector.detect(
                image, detection_threshold=self._detection_thresholds[kind]
            )
            detected_boxes.extend(new_boxes)

        return self._obfuscator.obfuscate(image, detected_boxes), detected_boxes

    # ----------------
    def anonymize_images(
        self,
        input_path,
        output_path,
        file_types,
        write_json,
    ):
        print(
            f"Anonymizing images in {input_path} and saving the anonymized"
            f" images to {output_path}..."
        )

        Path(output_path).mkdir(exist_ok=True)
        assert Path(output_path).is_dir(), "Output path must be a directory"

        files = []
        for file_type in file_types:
            files.extend(list(Path(input_path).glob(f"**/*.{file_type}")))

        for input_image_path in tqdm(files):
            # Create output directory
            relative_path = input_image_path.relative_to(input_path)
            (Path(output_path) / relative_path.parent).mkdir(
                exist_ok=True, parents=True
            )
            output_image_path = Path(output_path) / relative_path
            output_detections_path = (
                Path(output_path) / relative_path
            ).with_suffix(".json")

            # Anonymize image
            image = load_np_image(input_image_path)
            anonymized_image, detections = self.anonymize_image(image=image)
            save_np_image(image=anonymized_image, image_path=output_image_path)

            if write_json:
                save_detections(
                    detections=detections,
                    detections_path=output_detections_path,
                )
