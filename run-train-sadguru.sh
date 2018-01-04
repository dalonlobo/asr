#!/bin/sh
set -xe
if [ ! -f DeepSpeech.py ]; then
    echo "Please make sure you run this from DeepSpeech's top level directory."
    exit 1
fi;

python -u DeepSpeech.py \
  --train_files /home/nvidia/DeepSpeech/data/alfred/train/train.csv \
  --dev_files /home/nvidia/DeepSpeech/data/alfred/dev/dev.csv \
  --test_files /home/nvidia/DeepSpeech/data/alfred/test/test.csv \
  --train_batch_size 80 \
  --dev_batch_size 80 \
  --test_batch_size 40 \
  --n_hidden 375 \
  --epoch 33 \
  --validation_step 1 \
  --early_stop True \
  --earlystop_nsteps 6 \
  --estop_mean_thresh 0.1 \
  --estop_std_thresh 0.1 \
  --dropout_rate 0.22 \
  --learning_rate 0.00095 \
  --report_count 100 \
  --use_seq_length False \
  --export_dir /home/nvidia/DeepSpeech/data/alfred/results/model_export/ \
  --checkpoint_dir /home/nvidia/DeepSpeech/data/alfred/results/checkout/ \
  --decoder_library_path /home/nvidia/tensorflow/bazel-bin/native_client/libctc_decoder_with_kenlm.so \
  --alphabet_config_path /home/nvidia/DeepSpeech/data/alfred/vocabulary.txt \
  --lm_binary_path /home/nvidia/DeepSpeech/data/alfred/lm.binary \
  --lm_trie_path /home/nvidia/DeepSpeech/data/alfred/trie \
  "$@"
