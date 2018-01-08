#!/bin/sh
set -xe
if [ ! -f DeepSpeech.py ]; then
    echo "Please make sure you run this from DeepSpeech's top level directory."
    exit 1
fi;

python -u DeepSpeech.py \
  --train_files /datadrive/speechexperiments/datasets/video_datasets/sadguru-other-train.csv \
  --dev_files /datadrive/speechexperiments/datasets/video_datasets/sadguru-other-dev.csv \
  --test_files /datadrive/speechexperiments/datasets/video_datasets/sadguru-other-test.csv \
  --train_batch_size 1 \
  --dev_batch_size 1 \
  --test_batch_size 1 \
  --validation_step 1 \
  --n_hidden 494 \
  --epoch 50 \
  --checkpoint_dir /datadrive/speechexperiments/datasets/video_datasets/checkpoint/ \
  --export_dir /datadrive/speechexperiments/datasets/video_datasets/model_export/ \
  --decoder_library_path /datadrive/speechexperiments/DeepSpeech/native_client/libctc_decoder_with_kenlm.so \
  --alphabet_config_path /datadrive/speechexperiments/models/alphabet.txt \
  --lm_binary_path /datadrive/speechexperiments/datasets/lm_models/ds_full_lm_o5.binary \
  --lm_trie_path /datadrive/speechexperiments/datasets/lm_models/ds_full_lm_trie \
  "$@"
#  --early_stop True \
#  --earlystop_nsteps 6 \
#  --estop_mean_thresh 0.1 \
#  --estop_std_thresh 0.1 \
#  --dropout_rate 0.22 \
#  --learning_rate 0.00095 \
#  --report_count 100 \
#  --use_seq_length False \
# "$@"
