import pandas as pd
import os
import re

# function to parse the txt file for relevant data
def parse_usda_file(filepath):
    with open(filepath) as file:
        contents = file.read()

        # extract date
        week_match = re.search(r'WEEK ENDING\s+(\d{2}/\d{2}/\d{4})', contents)
        week_ending_date = week_match.group(1) if week_match else None

        # extract sale data   r'This Week:\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)'
        receipts_match = re.search(r'This Week:?\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', contents, re.IGNORECASE)
        if receipts_match:
            national_auctions = int(receipts_match.group(1).replace(",", ""))
            national_total = int(receipts_match.group(4).replace(",", ""))
        else:
            national_auctions = None
            national_total = None

        # extract block of text after texas
        texas_match = re.search(r'(TEXAS\s+\d+\.?.*?)(?=\n\s*[A-Z]{2,}|$)', contents, re.DOTALL | re.IGNORECASE)
        texas_block = texas_match.group(1) if texas_match else ""

        # normalize whitespace to account for newlines breaking up the reg exps
        texas_block_flat = re.sub(r"\s+", " ", texas_block)
        # print(texas_block_flat)

        # extract steers subsection
        steers_match = re.search(r'Steers:\s+(.*?)(?=Heifers:|$)', texas_block_flat, re.DOTALL | re.IGNORECASE)
        steers_text = steers_match.group(1) if steers_match else ""
        # print(steers_text)

        # extract heifers subsection
        heifers_match = re.search(r'Heifers:\s+(.*)$', texas_block_flat, re.DOTALL | re.IGNORECASE)
        heifers_text = heifers_match.group(1) if heifers_match else ""

        # within steers text, parse "medium and large 1" and "medium large 1-2"
        ml1_pattern = r'Medium\s*and\s*Large\s*1\s+(.*?)(?=Medium\s*and\s*Large\s*1-\s*2|$)'
        ml1_2_pattern = r'Medium\s*and\s*Large\s*1-\s*2\s+(.*)$'

        # steers medium and large 1
        steers_ml1 = re.search(ml1_pattern, steers_text, re.IGNORECASE)
        steers_ml1_text = steers_ml1.group(1) if steers_ml1 else ""
        # print('\n\n' + steers_ml1_text + '\n\n')

        # steers medium and large 1-2
        steers_ml1_2 = re.search(ml1_2_pattern, steers_text, re.IGNORECASE)
        steers_ml1_2_text = steers_ml1_2.group(1) if steers_ml1_2 else ""
        # print(steers_ml1_2_text + '\n\n')

        # heifers medium and large 1
        heifers_ml1 = re.search(ml1_pattern, heifers_text, re.IGNORECASE)
        heifers_ml1_text = heifers_ml1.group(1) if heifers_ml1 else ""
        # print(heifers_ml1_text + '\n\n')

        # heifers medium and large 1-2
        heifers_ml1_2 = re.search(ml1_2_pattern, heifers_text, re.IGNORECASE)
        heifers_ml1_2_text = heifers_ml1_2.group(1) if heifers_ml1_2 else ""
        # print(heifers_ml1_2_text + '\n\n')

        # calculate average prices
        steers_ml1_avg = compute_weighted_avg(steers_ml1_text)
        steers_ml1_2_avg = compute_weighted_avg(steers_ml1_2_text)
        heifers_ml1_avg = compute_weighted_avg(heifers_ml1_text)
        heifers_ml1_2_avg = compute_weighted_avg(heifers_ml1_2_text)

        # print(steers_ml1_avg)
        # print(steers_ml1_2_avg)
        # print(heifers_ml1_avg)
        # print(heifers_ml1_2_avg)

        return {
            'week_ending_date': week_ending_date,
            'national_auctions': national_auctions,
            'national_total': national_total,
            'avg_price_steers_ML1': steers_ml1_avg,
            'avg_price_steers_ML1_2': steers_ml1_2_avg,
            'avg_price_heifers_ML1': heifers_ml1_avg,
            'avg_price_heifers_ML1_2': heifers_ml1_2_avg
        }

# helper function to calculate the weighted average     
def compute_weighted_avg(text_block):
    sale_matches = re.findall(r'\(\s*(\d+)\s*\)\s*([\d]+\.[\d]+)', text_block)
    if not sale_matches:
        return None
    total_head = 0
    total_dollars = 0
    for head_str, price_str in sale_matches:
        total_head += int(head_str)
        total_dollars += int(head_str) * float(price_str)
    return round(total_dollars / total_head, 2)

data_rows = []
data_folder = r'National_Feeder_Stocker_Cattle_Summary'

for file in os.listdir(data_folder):
    # print(os.path.join(data_folder,file))
    parsed = parse_usda_file(os.path.join(data_folder,file))
    data_rows.append(parsed)

# print(data_rows)

# data = parse_usda_file(r'National_Feeder_Stocker_Cattle_Summary\ams_3232_00001.txt')
# print(data)

df = pd.DataFrame(data_rows)
print(df.to_string())