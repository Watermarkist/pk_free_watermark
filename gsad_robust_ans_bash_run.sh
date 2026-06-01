#!/bin/bash
dataset_root="./dataset_GSAD"
org_file="$dataset_root/gsad_std_train.csv"
test_set="$dataset_root/gsad_std_test.csv"
exp_root="./experiments"
exp_tag="gsad_robust_ans_exp"
dataset="gsad"
method="Ours"
column_range="0,127"
wm_params_json="./secret_keys_GSAD/gsad_params_robust_ans_d20.json"
wm_datasets_folder="$exp_root/$exp_tag/$dataset/embed/wm_datasets"

isEmbed=true
num_wm_sets=10
save_bin_info="false"
col_to_embed="0,19"
num_col_to_embed=20
eigenvec_file="$dataset_root/gsad_basis_$num_col_to_embed.npy"
if $isEmbed; then
  python embed.py --org_file "$org_file" --eigenvec_file "$eigenvec_file" --wm_params_json "$wm_params_json"  \
  --exp_root "$exp_root" --exp_tag "$exp_tag" --dataset "$dataset" --col_to_embed "$col_to_embed" \
  --num_wm_sets $num_wm_sets --save_bin_info "$save_bin_info"
fi


isExtract_no_attack=true
if $isExtract_no_attack; then
  python detect.py --exp_root "$exp_root" --exp_tag "$exp_tag" --target_dir "embed" --dataset "$dataset" \
  --attack "watermarked" --add_info "no_attack" --col_to_embed "$col_to_embed"
fi

isNoiseAttack=true
noise_std="0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0"
noise_range="0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0"

isClassify=true
isExtract=true
if $isNoiseAttack; then
#  noise_type_list=("constant" "gaussian" "uniform" )
  noise_type_list=("uniform" "gaussian")
  for noise_type in "${noise_type_list[@]}"
  do
    target_dir_noise="$exp_root/$exp_tag/$dataset/noise/$noise_type"
    if [ "$noise_type" == "gaussian" ]; then
      python attack_channel/noise_attack.py --clean_file "$org_file" --wm_folder "$wm_datasets_folder" \
      --noise_std $noise_std --output_dir "$target_dir_noise" --noise_type "$noise_type" --method "$method" \
      --dataset "$dataset" --column_range "$column_range"
    elif [ "$noise_type" == "uniform" ]; then
      python attack_channel/noise_attack.py --clean_file "$org_file" --wm_folder "$wm_datasets_folder" \
      --noise_range $noise_range --output_dir "$target_dir_noise" --noise_type "$noise_type" --method "$method" \
      --dataset "$dataset" --column_range "$column_range"
    else
      echo "check noise type"
    fi

    if $isExtract; then
      python detect.py --exp_root "$exp_root" --exp_tag "$exp_tag" --dataset "$dataset" --attack "noise" \
      --add_info "$noise_type" --target_dir "$target_dir_noise" --col_to_embed "$col_to_embed"
    fi

    rm -r "$target_dir_noise"
  done
fi


row_del_atk=true
delete_ratio="0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 0.91 0.92 0.93 0.94 0.95 0.96 0.97 0.98 0.99"

if $row_del_atk; then
  delete_type="row"
  target_dir_delete="$exp_root/$exp_tag/$dataset/delete/$delete_type"
  python attack_channel/delete_attack.py --clean_file "$org_file" --wm_folder "$wm_datasets_folder" --output_dir "$target_dir_delete" --delete_type "$delete_type" --method "$method" --dataset "$dataset" --alpha_list $delete_ratio

  python detect.py --exp_root "$exp_root" --exp_tag "$exp_tag" --dataset "$dataset" --attack "delete" --add_info "$delete_type" --target_dir "$target_dir_delete" --ori_file "$org_file" --col_to_embed "$col_to_embed"

  rm -r "$target_dir_delete"
fi

isInsertAttack=true
insert_ratio="0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0"

if $isInsertAttack; then
#  insert_type_list=("replicate" "concatenate" "generate")
  insert_type_list=("generate")
  for insert_type in "${insert_type_list[@]}"
  do
    target_dir_insert="$exp_root/$exp_tag/$dataset/insert/$insert_type"
    python attack_channel/insert_attack.py --clean_file "$org_file" --wm_folder "$wm_datasets_folder" --remain_file "" --output_dir "$target_dir_insert" --insert_type "$insert_type" --method "$method" --dataset "$dataset" --alpha_list $insert_ratio --column_range "$column_range"

    if $isExtract; then
      python detect.py --exp_root "$exp_root" --exp_tag "$exp_tag" --dataset "$dataset" --attack "insert" --add_info "$insert_type" --target_dir "$target_dir_insert" --ori_file "$org_file" --col_to_embed "$col_to_embed"
    fi
    rm -r "$target_dir_insert"
  done
fi
