#!/bin/sh
set -eu

url="https://huggingface.co/$HF_REPO_ID/resolve/main"
model_dir=/models/classification_model
mkdir -p "$model_dir"
for file in model.json opchain.json; do
  curl -fsSL -H "Authorization: Bearer $HF_TOKEN" "$url/$file?download=true" -o "$model_dir/$file"
done
model_file="$(sed -n 's/.*"modelFile": "\([^"]*\)".*/\1/p' "$model_dir/model.json")"
test -n "$model_file"
curl -fsSL -H "Authorization: Bearer $HF_TOKEN" "$url/$model_file?download=true" -o "$model_dir/$model_file"
