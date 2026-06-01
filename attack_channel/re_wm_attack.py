import sys
import os
import numpy as np
from collections import Counter
import pandas as pd
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the utils directory
utils_dir = os.path.join(current_dir, '..', 'utils')

# Add the utils directory to the sys.path
sys.path.append(utils_dir)

from load_wm_params import load_wm_params, load_eigenvectors
from dataset_utils import load_data, load_storedkey, save_data


def embed_watermark(data, wm_params, storedkey_file, save_bin_info=False):
    X_wm = data.dot(wm_params['p_vec_x'])
    X_wm_hash = X_wm.copy()

    X_wm_hash = np.asarray(X_wm_hash, dtype=np.float64)
    bin_vals = np.floor(X_wm_hash / wm_params['bin_width'])
    bin_vals_dict = dict(Counter(bin_vals))
    num_bins = len(bin_vals_dict)
    # print(f'average #points in each bin {calculate_average(bin_vals_dict)}')

    # record bin info
    if save_bin_info:
        bin_info_file = storedkey_file.replace("_keys.csv", "_bin_info.txt")
        with open(bin_info_file, 'w') as file:
            for key, value in bin_vals_dict.items():
                file.write(str(key) + ': ' + str(value) + '\n')


    X_wm_hash = np.floor(X_wm_hash / wm_params['bin_width']) / wm_params['resolution']
    Y_wm = wm_params['ampt'] * np.sin(wm_params['theta'] * 2 * np.pi * X_wm_hash)


    mat2add_wm = np.tile(wm_params['p_vec_y'].reshape(1, -1), (data.shape[0], 1)) * Y_wm.reshape(-1, 1)

    max_abs_val = np.max(np.abs(mat2add_wm))
    wm_params['max_abs'] = max_abs_val
    wm_params['num_bins'] = num_bins

    df = pd.DataFrame.from_dict(wm_params, orient='index', columns=['value'])
    df.to_csv(storedkey_file, header=False)
    # print(f'save secret key at {storedkey_file}')

    data_wm = data + mat2add_wm

    return data_wm


def re_wm_atk(wm_data_file, column_range, alpha, atk_keys_file, eigenvec_file, dataset):
    feat_to_emb = load_data(wm_data_file, column_range)
    # load data and params
    eigenvectors = load_eigenvectors(feat_to_emb, eigenvec_file)
    atk_keys = load_wm_params(atk_keys_file, '1', eigenvectors)
    # print(atk_keys)
    atk_keys['ampt'] = alpha
    # print('updated', atk_keys)

    # embed
    keys_save_path = f"/home/celia/PycharmProjects/watermark_proj/experiments/{dataset}_params_res_grid_search/{dataset}/rewm/keys"
    if not os.path.exists(keys_save_path):
        os.makedirs(keys_save_path)
    storedfile = os.path.basename(wm_data_file)[:-4] + '_rw' + '_keys.csv'
    data_wm = embed_watermark(feat_to_emb, atk_keys, os.path.join(keys_save_path, storedfile), False)

    wm_file = os.path.basename(wm_data_file)[:-4] + '_wm.csv'

    wm_save_path = f"/home/celia/PycharmProjects/watermark_proj/experiments/{dataset}_params_res_grid_search/{dataset}/rewm/datasets"
    if not os.path.exists(wm_save_path):
        os.makedirs(wm_save_path)
    save_data(wm_data_file, data_wm, os.path.join(wm_save_path, wm_file), column_range)

    return os.path.join(wm_save_path, wm_file)



if __name__ == "__main__":
    wm_data_file = "/home/celia/PycharmProjects/watermark_proj/experiments/covtype_params_res_grid_search/covtype/embed/wm_datasets/covtype_std_train_keyid1_wm.csv"
    # wm_data_file2 = "experiments/gas_params_res_grid_search/gas/embed/wm_datasets/gas_std_train_keyid1_wm.csv"
    dataset = wm_data_file.split('/')[-4]
    print('dataset', dataset)
    if dataset == 'covtype':
        column_range = [0, 53]
        num_col_to_embed = 54
        alpha_list = [2]
        eigenvec_file = f"/home/celia/PycharmProjects/watermark_proj/dataset_covtype_params/covtype_basis_{num_col_to_embed}.npy"
        atk_keys_file = f"/home/celia/PycharmProjects/watermark_proj/dataset_covtype_params/re_wm_atk_params.json"
    elif dataset == 'gas':
        column_range = [0, 127]
        num_col_to_embed = 128
        alpha_list = [20, 30, 40]
        eigenvec_file = f"/home/celia/PycharmProjects/watermark_proj/dataset_gas/gas_basis_{num_col_to_embed}.npy"
        atk_keys_file = f"/home/celia/PycharmProjects/watermark_proj/dataset_gas/re_wm_atk_params.json"
    else:
        print('check dataset')
        exit()


    for alpha in alpha_list:
        re_wm_data_file = re_wm_atk(wm_data_file, column_range, alpha, atk_keys_file, eigenvec_file, dataset)

        # mlu

