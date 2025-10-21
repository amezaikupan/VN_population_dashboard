def format_number(num):
    actual_num = num * 1000  # Convert back to real numbers

    if abs(actual_num) > 1000000:
        if not actual_num % 1000000:
            return f'{actual_num // 1000000} M'
        return f'{round(actual_num / 1000000, 1)} M'
    return f'{round(actual_num // 1000, 1)} K'

def calculate_population_difference(input_df, input_year):
    data_selected_year = input_df[input_df['Year'] == input_year].reset_index()
    data_previous_year =  input_df[input_df['Year'] == input_year - 1].reset_index()
    data_selected_year['Population_difference'] = data_selected_year['Population'] - data_previous_year['Population']
    return data_selected_year[['Province', 'Population', 'Population_difference']].sort_values(by="Population_difference", ascending=False)
