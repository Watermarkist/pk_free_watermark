import pandas as pd
import random
import json


def random_delete_columns(input_file, output_file, start_index, end_index, k):
    """
    Randomly delete k columns from a CSV file within a specified range of column indices.

    Args:
    - input_file (str): The input CSV file name.
    - output_file (str): The output CSV file name after deleting columns.
    - start_index (int): The starting index of the range of columns (inclusive).
    - end_index (int): The ending index of the range of columns (inclusive).
    - k (int): The number of columns to randomly delete.

    Returns:
    - deleted_columns (list): List of indices of the deleted columns.
    """

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(input_file)

    # Get a list of column indices within the specified range
    column_indices = list(range(start_index, end_index + 1))

    # Randomly shuffle the column indices
    random.shuffle(column_indices)

    # Select the first k indices for deletion
    deleted_columns = column_indices[:k]

    # Drop the selected columns
    df.drop(df.columns[deleted_columns], axis=1, inplace=True)

    # Save the modified DataFrame to the output file
    df.to_csv(output_file, index=False)

    return deleted_columns


def get_del_col_name(json_file, num_col_del):
    # Load the sorted dictionary from the JSON file
    with open(json_file, 'r') as json_file:
        sorted_dict = json.load(json_file)

    # Get the last 'num_col_del' keys from the sorted dictionary
    last_keys = list(sorted_dict.keys())[-num_col_del:]

    return last_keys


def delete_columns(input_file, output_file, columns_to_delete):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    for col_name in columns_to_delete:
        # Delete the specified columns
        print('col', col_name)
        df.drop(columns=col_name, inplace=True)

    # Save the modified DataFrame to a new CSV file
    df.to_csv(output_file, index=False)


# Example usage:
json_file = '/home/celia/PycharmProjects/watermark_proj/dataset_higgs/feat_rank.json'
input_file = '/home/celia/PycharmProjects/watermark_proj/dataset_higgs/higgs_std_train.csv'
output_file = '/home/celia/PycharmProjects/watermark_proj/dataset_higgs/output_after_deletion.csv'
start_index = 1  # Replace with your desired starting index
end_index = 29  # Replace with your desired ending index
k = 10  # Replace with the number of columns to randomly delete

# deleted_columns = random_delete_columns(input_file, output_file, start_index, end_index, k)
# print(f"Deleted columns: {deleted_columns}")
columns_to_delete = get_del_col_name(json_file, k)
print('del', columns_to_delete)
delete_columns(input_file, output_file, columns_to_delete)
