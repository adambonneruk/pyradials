'''loads a .csv file with gps coordinates in a given format'''
import csv

# Function to group and average data
def load_and_average_gps_csv_file(filename):
    # Dictionary to store data grouped by keys
    data_dict = {}

    # Open the CSV file
    with open(filename, newline='') as csv_file:
        # Create a CSV reader object
        csv_reader = csv.reader(csv_file, delimiter=',')

        # Iterate through each row in the CSV
        for row in csv_reader:
            # Extract the grouping key from the first column
            key = row[0].split('.')[0]  # Grouping key

            # Check if the key is already in the dictionary
            if key not in data_dict:
                data_dict[key] = []  # Initialize list for the group

            # Append values of columns 2, 3, and 4 as floats to the group
            data_dict[key].append([float(row[1]), float(row[2]), float(row[3])])

    # List to store the averages for each group
    averages = []

    # Calculate averages for each group
    for key, values in data_dict.items():
        # Calculate the average for each column and round to 3 decimal places
        avg = [round(sum(col) / len(values), 3) for col in zip(*values)]
        # Append the key and averages to the result list
        averages.append([key] + avg)

    return averages

# Main block to execute if the script is run directly
if __name__ == "__main__":
    filename = 'data/SROAD.csv'  # Replace 'data.csv' with your file name
    result = load_and_average_gps_csv_file(filename)
    print(result)
