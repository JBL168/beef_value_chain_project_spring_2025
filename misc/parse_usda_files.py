import pandas as pd
import os
import regex as re

# function to parse the txt file for relevant data
def parse_usda_file(filepath):
    with open(filepath, 'r', encoding = 'utf-8') as file:
        contents = file.read()

        # extract date
        week_match = re.search(r'WEEK\s*ENDING\s*.*?(\d{2}/\d{2}/\d{4})', contents)
        week_ending_date = week_match.group(1) if week_match else None

        # extract sale data   r'This Week:\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)'
        receipts_match = re.search(r'This Week:?\s+(?:\*+\s*)?([\d,\.]+)(?:\s*\*+)?\s+(?:\*+\s*)?([\d,\.]+)(?:\s*\*+)?\s+(?:\*+\s*)?([\d,\.]+)(?:\s*\*+)?\s+(?:\*+\s*)?([\d,\.]+)(?:\s*\*+)?', contents, re.IGNORECASE)
        # print(receipts_match)
        if receipts_match:
            try:
                national_auctions = int(receipts_match.group(1).replace(',', '').replace('*', ''))
                national_total = int(receipts_match.group(4).replace(',', '').replace('*', ''))
            except:
                print(filepath)
                exit()
        else:
            national_auctions = None
            national_total = None

        # isolate the auction data from the direct receipt data
        split1 = contents.split("Auction Receipts:", 1)[1] if len(contents.split("Auction Receipts:", 1)) == 2 else contents.split("Auction Receipts:", 1)[0]
        # if(len())
        text_no_direct = split1.split("Direct Receipts:", 1)[0]

        # within auction data, search for texas block
        texas_match = re.search(r'(?s)(?i)(?m)(^[ \t]*TEXAS\b.*?)(?=^[ \t]*[^\w]*OKLAHOMA|KANSAS|MISSOURI|IOWA|SOUTH DAKOTA|NORTH DAKOTA|MONTANA|NEBRASKA|COLORADO|WYOMING|VIRGINIA|WASHINGTON|ARKANSAS|TENNESSEE|FLORIDA|GEORGIA|MISSISSIPPI|ALABAMA|NEW MEXICO|NORTH CAROLINA|SOUTH CAROLINA\b)', text_no_direct)
        texas_block = texas_match.group(0) if texas_match else "fail"
        # print(texas_block)

        # normalize whitespace to account for newlines breaking up the reg exps
        texas_block_flat = re.sub(r'\s+', ' ', texas_block)
        # print(texas_block_flat)

        # extract texas auctions
        texas_auctions = re.search(r'\bTEXAS\s+([\d,\.]+)', texas_block_flat, re.DOTALL | re.IGNORECASE)
        try:
            texas_auctions = int(texas_auctions.group(1).replace(',', '').replace('.', '')) if texas_auctions else None
        except:
            print(len(split1))
            # print(texas_block_flat)
            print(filepath)
            exit()

        # extract steers subsection
        steers_match = re.search(r'Steers:\s+(.*?)(?=Heifers:|$)', texas_block_flat, re.DOTALL | re.IGNORECASE)
        steers_text = steers_match.group(1) if steers_match else ""
        # print(steers_text)

        # extract heifers subsection
        heifers_match = re.search(r'Heifers:\s+(.*)$', texas_block_flat, re.DOTALL | re.IGNORECASE)
        heifers_text = heifers_match.group(1) if heifers_match else ""

        # within steers text, parse "medium and large 1" and "medium large 1-2"
        ml1_pattern = r'Medium\s*and\s*Large\s*1(?!\s*[-–—]\s*2)\s+(.*?)(?=Medium\s*and\s*Large\s*1\s*[-–—]\s*2|$)'
        ml1_2_pattern = r'Medium\s*and\s*Large\s*1\s*[-–—]?\s*2\s+(.*)$'


        # steers medium and large 1
        steers_ml1 = re.search(ml1_pattern, steers_text, re.IGNORECASE)
        steers_ml1_text = steers_ml1.group(1) if steers_ml1 else ""
        # print(compute_avg(steers_ml1_text))
        # print(steers_ml1_text + '\n\n')

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
        steers_ml1_avg = compute_avg(steers_ml1_text)
        steers_ml1_2_avg = compute_avg(steers_ml1_2_text)
        heifers_ml1_avg = compute_avg(heifers_ml1_text)
        heifers_ml1_2_avg = compute_avg(heifers_ml1_2_text)

        # print(steers_ml1_avg)
        # print(steers_ml1_2_avg)
        # print(heifers_ml1_avg)
        # print(heifers_ml1_2_avg)

        return {
            'week_ending_date': week_ending_date,
            'national_auctions': national_auctions,
            'national_total': national_total,
            'texas_auctions': texas_auctions,
            'avg_price_steers_ML1': steers_ml1_avg,
            'avg_price_steers_ML1_2': steers_ml1_2_avg,
            'avg_price_heifers_ML1': heifers_ml1_avg,
            'avg_price_heifers_ML1_2': heifers_ml1_2_avg
        }

# helper function to calculate the weighted average     
def compute_avg(text_block):
    sale_matches = re.findall(r'\b\d+\.\d+\b', text_block)
    # print(text_block + '\n')
    if not sale_matches:
        return None
    sale_matches = [float(price_str) for price_str in sale_matches]
    return round(sum(sale_matches)/len(sale_matches), 2)

data_rows = []
data_folder = r'National_Feeder_Stocker_Cattle_Summary'

for file in os.listdir(data_folder):
    # print(os.path.join(data_folder,file))
    parsed = parse_usda_file(os.path.join(data_folder,file))
    data_rows.append(parsed)

df = pd.DataFrame(data_rows)
print(df.to_string())
# print(df.head())


# data = parse_usda_file(r'National_Feeder_Stocker_Cattle_Summary\ams_3232_00219_01.txt')
# print(data)

df.to_csv('stocker_data.csv', index=False)