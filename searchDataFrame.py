import pandas as pd

# Assuming you have a DataFrame named 'response_df' already loaded

# Function to perform search within the DataFrame
def search_in_document(input_text, dataframe):
    # Search for the input text in the DataFrame
    result = dataframe[dataframe['column_name'].str.contains(input_text, case=False, na=False)]
    return result

# Replace 'column_name' with the actual column name you want to search in

# Example DataFrame creation (Replace this with your actual DataFrame loading)
data = {
    'column_name': ['Lorem ipsum dolor sit amet', 'consectetur adipiscing elit', 'sed do eiusmod tempor']
}
response_df = pd.DataFrame(data)

# Taking input from the user
search_input = input("Enter text to search: ")

# Performing the search
search_result = search_in_document(search_input, response_df)

# Displaying the search result
print("Search Result:")
print(search_result)
