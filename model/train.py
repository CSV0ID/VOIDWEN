"""Fine-tune Helsinki-NLP/opus-mt-zh-en on the wenyan -> English corpus.

Transfer learning, not from scratch: the base model already handles modern Chinese
-> English. Runs on a Colab free T4. Config from VOIDWEN master plan section 8.2.
Resume across sessions with --resume (checkpoints go to --output_dir, point that at
Google Drive on Colab so they survive the 12h session limit).

    pip install -r model/requirements.txt
    python model/train.py --output_dir /content/drive/MyDrive/voidwen/ckpt --resume
"""
from __future__ import annotations

import argparse

from datasets import load_dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

BASE_MODEL = "Helsinki-NLP/opus-mt-zh-en"
DATASET = "CSV0ID/voidwen-wenyan-en"
MAX_SRC_LEN, MAX_TGT_LEN = 128, 256


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output_dir", default="./checkpoints/voidwen")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)
    ds = load_dataset(args.dataset)

    def preprocess(batch):
        model_inputs = tokenizer(batch["source"], max_length=MAX_SRC_LEN, truncation=True)
        labels = tokenizer(text_target=batch["target"], max_length=MAX_TGT_LEN, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = ds.map(preprocess, batched=True, remove_columns=ds["train"].column_names)

    targs = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        learning_rate=5e-5,
        warmup_steps=500,
        fp16=True,          # T4 supports fp16, ~2x throughput
        eval_strategy="steps",
        eval_steps=500,
        save_steps=1000,
        save_total_limit=2,
        predict_with_generate=True,
        logging_steps=100,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=targs,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized.get("eval") or tokenized.get("validation"),
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )
    trainer.train(resume_from_checkpoint=args.resume)
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"saved fine-tuned model to {args.output_dir}")


if __name__ == "__main__":
    main()
