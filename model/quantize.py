"""Dynamic int8 quantization of the exported ONNX seq2seq graphs.

Shrinks the model roughly 4x (~300MB fp32 -> ~80MB int8) so it downloads once and
runs in the browser. Quantizes each ONNX file in the export dir (encoder, decoder,
decoder-with-past).

    python model/quantize.py --onnx ./onnx --out ./onnx-int8
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil

from optimum.onnxruntime import ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True, help="dir from export_onnx.py")
    ap.add_argument("--out", default="./onnx-int8")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # Copy tokenizer/config so the output dir is a complete, loadable model.
    for f in glob.glob(os.path.join(args.onnx, "*")):
        if not f.endswith(".onnx"):
            shutil.copy(f, args.out)

    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=False)
    for onnx_file in glob.glob(os.path.join(args.onnx, "*.onnx")):
        name = os.path.basename(onnx_file)
        quantizer = ORTQuantizer.from_pretrained(args.onnx, file_name=name)
        quantizer.quantize(save_dir=args.out, quantization_config=qconfig)
        print(f"quantized {name}")
    print(f"int8 model in {args.out}")


if __name__ == "__main__":
    main()
