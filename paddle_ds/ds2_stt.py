"""Evaluation for DeepSpeech2 model."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import functools
import pandas as pd
import numpy as np
import logging
import sys
import pickle
import datetime
import paddle.v2 as paddle

from data_utils.data import DataGenerator
from model_utils.model import DeepSpeech2Model
from utils.error_rate import char_errors, word_errors
from utils.utility import add_arguments, print_arguments
from data_utils.utility import read_manifest
from timeit import default_timer as timer
from custom_utils import pre_process_srt

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
# yapf: disable
add_arg('batch_size',       int,    128,    "Minibatch size.")
add_arg('trainer_count',    int,    8,      "# of Trainers (CPUs or GPUs).")
add_arg('beam_size',        int,    500,    "Beam search width.")
add_arg('num_proc_bsearch', int,    8,      "# of CPUs for beam search.")
add_arg('num_proc_data',    int,    8,      "# of CPUs for data preprocessing.")
add_arg('num_conv_layers',  int,    2,      "# of convolution layers.")
add_arg('num_rnn_layers',   int,    3,      "# of recurrent layers.")
add_arg('rnn_layer_size',   int,    2048,   "# of recurrent cells per layer.")
add_arg('alpha',            float,  2.5,    "Coef of LM for beam search.")
add_arg('beta',             float,  0.3,    "Coef of WC for beam search.")
add_arg('cutoff_prob',      float,  1.0,    "Cutoff probability for pruning.")
add_arg('cutoff_top_n',     int,    40,     "Cutoff number for pruning.")
add_arg('use_gru',          bool,   False,  "Use GRUs instead of simple RNNs.")
add_arg('use_gpu',          bool,   True,   "Use GPU or not.")
add_arg('share_rnn_weights',bool,   True,   "Share input-hidden weights across "
                                            "bi-directional RNNs. Not for GRU.")
add_arg('mean_std_path',    str,
        'data/librispeech/mean_std.npz',
        "Filepath of normalizer's mean & std.")
add_arg('vocab_path',       str,
        'data/librispeech/vocab.txt',
        "Filepath of vocabulary.")
add_arg('model_path',       str,
        './checkpoints/libri/params.latest.tar.gz',
        "If None, the training starts from scratch, "
        "otherwise, it resumes from the pre-trained model.")
add_arg('lang_model_path',  str,
        'models/lm/common_crawl_00.prune01111.trie.klm',
        "Filepath for language model.")
add_arg('decoding_method',  str,
        'ctc_beam_search',
        "Decoding method. Options: ctc_beam_search, ctc_greedy",
        choices = ['ctc_beam_search', 'ctc_greedy'])
add_arg('error_rate_type',  str,
        'wer',
        "Error rate type for evaluation.",
        choices=['wer', 'cer'])
add_arg('specgram_type',    str,
        'linear',
        "Audio feature type. Options: linear, mfcc.",
        choices=['linear', 'mfcc'])
add_arg('src_path',   str,
        'Videos',
        "Filepath of all Videos folder.")
# yapf: disable
args = parser.parse_args()


def evaluate():
    """Evaluate on whole test data for DeepSpeech2."""
    data_generator = DataGenerator(
        vocab_filepath=args.vocab_path,
        mean_std_filepath=args.mean_std_path,
        augmentation_config='{}',
        specgram_type=args.specgram_type,
        num_threads=args.num_proc_data,
        keep_transcription_text=True)

    ds2_model = DeepSpeech2Model(
        vocab_size=data_generator.vocab_size,
        num_conv_layers=args.num_conv_layers,
        num_rnn_layers=args.num_rnn_layers,
        rnn_layer_size=args.rnn_layer_size,
        use_gru=args.use_gru,
        pretrained_model_path=args.model_path,
        share_rnn_weights=args.share_rnn_weights)

    # decoders only accept string encoded in utf-8
    vocab_list = [chars.encode("utf-8") for chars in data_generator.vocab_list]

    if args.decoding_method == "ctc_beam_search":
        ds2_model.init_ext_scorer(args.alpha, args.beta, args.lang_model_path,
                                  vocab_list)
    errors_func = char_errors if args.error_rate_type == 'cer' else word_errors

    # prepare ASR inference handler
    def file_to_transcript(filename):
        feature = data_generator.process_utterance(filename, "")
        probs_split = ds2_model.infer_batch_probs(
            infer_data=[feature],
            feeding_dict=data_generator.feeding)

        if args.decoding_method == "ctc_greedy":
            result_transcript = ds2_model.decode_batch_greedy(
                probs_split=probs_split,
                vocab_list=vocab_list)
        else:
            result_transcript = ds2_model.decode_batch_beam_search(
                probs_split=probs_split,
                beam_alpha=args.alpha,
                beam_beta=args.beta,
                beam_size=args.beam_size,
                cutoff_prob=args.cutoff_prob,
                cutoff_top_n=args.cutoff_top_n,
                vocab_list=vocab_list,
                num_processes=1)
        return result_transcript[0]
    print("Line 121")
    number_of_videos = len(os.listdir(args.src_path))
    for index, dirs in enumerate(os.listdir(args.src_path)):
        print("Line: 124")
        parentdir = os.path.join(args.src_path, dirs)
        if not os.path.isdir(parentdir):
            continue # If its not directory, just continue
        print("Working on {}/{} Video".format(index+1,number_of_videos))
        manifest_path = os.path.join(parentdir, "manifest.txt")
        print(parentdir)
        manifest = read_manifest(
            manifest_path=manifest_path)
        transcripts = []
        for entry in manifest:
            fname = entry["audio_filepath"]
            transcript = file_to_transcript(fname)
            transcripts.append((fname, fname.split("/")[-1], transcript))
            print(transcript)

        df = pd.DataFrame(data=transcripts, columns=["wav_path", "wav_name", "transcripts"])
        df.sort_values("wav_name", inplace=True)
        try:
            with open(os.path.join(parentdir, 'transcripts_list_'+\
                                   datetime.datetime.now().strftime("%H:%M:%S")+".b"), 'wb') as f:
               pickle.dump(transcripts, f)
        except:
            pass
        try:
            with open(os.path.join(parentdir, 'ds2_stt_complete.csv'), 'w') as f:
                df.to_csv(f, index=False)
        except:
            pass    
        try:        
            with open(os.path.join(parentdir, 'ds2_stt.txt'), 'w') as f:
                for trans in df["transcripts"]:
                    f.write(pre_process_srt(trans) + " ")
        except:
            pass
    ds2_model.logger.info("finish evaluation")

def main():
    print_arguments(args)
    paddle.init(use_gpu=args.use_gpu,
                rnn_use_batch=True,
                trainer_count=args.trainer_count)
    evaluate()


if __name__ == '__main__':
    try:
        logs_path = os.path.basename(__file__) + ".logs"
        logging.basicConfig(filename=logs_path,
            filemode='a',
            format='%(asctime)s [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s] #%(lineno)d: %(message)s',
            datefmt='%H:%M:%S',
            level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        print("Logs are in ", os.path.abspath(logs_path), file=sys.stderr)
        print("Run the following command to view logs:\n", file=sys.stderr)
        print("tail -f {}".format(os.path.abspath(logs_path)), file=sys.stderr)
        start_time = timer()
        main()
        total_time = timer() - start_time
        print('Entire program ran in %0.3f minutes.' % (total_time / 60))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)