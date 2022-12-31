import re
import yaml
from torch.utils.data import Subset
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

re_reference_remove = re.compile(r'\[([0-9])+\]|\[([0-9])+,([0-9])+\]')

def webgpt_return_format(row):
    if row['score_0'] >= row['score_1']:
        # remove this to prevent information leak, since we are not using reference
        return {
                'question': row['question']['full_text'],
                     'pos': re_reference_remove.sub('', row['answer_0']),
                     'neg': re_reference_remove.sub('', row['answer_1'])
                }

    return {
            'question': row['question']['full_text'],
                 'pos': re_reference_remove.sub('', row['answer_1']),
                 'neg': re_reference_remove.sub('', row['answer_0'])
            }


def get_tokenizer(tokenizer_name):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if 'galactica' in tokenizer_name:
        tokenizer.add_special_tokens({'pad_token':'<pad>', 'eos_token': '</s>' })

    return tokenizer



def train_val_dataset(dataset, val_split=0.2):
    train_idx, val_idx = train_test_split(list(range(len(dataset))), 
        test_size=val_split, random_state=666, shuffle=True)
    # [3879, 11479, 8341, 9177, 10798, 18177, 5735, 15669, 4837, 2760]
    print(val_idx[:10])
    # [13582, 5919, 11875, 7373, 19135, 13706, 8555, 15788, 15005, 15209]
    print(train_idx[:10])
    return Subset(dataset, train_idx), Subset(dataset, val_idx)

def freeze_top_n_layers(model, target_layers):
    for name, param in model.name_parameters():
        if 'embed' in name:
            param.requires_grad = False
        elif 'layer' in name:
            tokens = name.split('.')
            idx = 0
            for token in tokens:
                if 'layer' in token:
                    break
                idx += 1

            layer_ = int(tokens[idx+1])
            if layer_ < target_layers:
                param.requires_grad = False
    return model


def argument_parsing(parser):
    default_params = {
        'num_train_epochs': 4,
        'learning_rate': 3e-5,
        'eval_steps': 500,
        'loss': 'rank',
        'max_length': 440,
        'per_device_train_batch_size': 8,
        'gradient_accumulation_steps': 8,
        'gradient_checkpointing': False,
        'datasets': ['webgpt']
    }
    args = parser.parse_args()
    with open(args.config, 'r', encoding='utf-8') as f:
        training_conf = yaml.safe_load(f.read())

    params = { **default_params, **training_conf }
    params['gradient_accumulation_steps'] = int(params['gradient_accumulation_steps'])
    params['num_train_epochs'] = int(params['num_train_epochs'])
    params['per_device_train_batch_size'] = int(params['per_device_train_batch_size'])
    params['learning_rate'] = float(params['learning_rate'])
    return params

