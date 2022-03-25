from tabula import read_pdf
from pathlib import Path
from icalendar import Calendar, Event
from datetime import datetime
from dateutil.relativedelta import relativedelta

pdf_path = Path("pdf")

table_dict = {}

# Create Calendar object
cal = Calendar()

# Load pdfs and extract tables
for i, pdf in enumerate(pdf_path.glob("*.pdf")):
    

    print(f"Extracting table from {pdf}")
    df = (
        read_pdf(pdf, pages='all')[0]
        .dropna() # drop NaNs as they don't have important info
        .drop(['Host'], axis=1, errors='ignore') # Don't need host and it messes up what we're doing
        ) 
    
    df[['dtstart', 'dtend']] = (
        df['TIME'].str.extract(r"([0-9]{1,2}:[0-9]{2})\s*[ap]m\-([0-9]{1,2}:[0-9]{2})\s*[ap]m")
    )
    
    for index, date, _, speaker, school, room, dtstart, dtend in df.itertuples():
        
        # Create event object
        event = Event()
            
        full_date_start = datetime.strptime("2022" + " " + date  + ' ' + dtstart, '%Y %B %d %H:%M')
        full_date_end = datetime.strptime("2022" + " " + date  + ' ' + dtend, '%Y %B %d %H:%M')
        
        # Change to military time
        if full_date_start.hour < 10:
            full_date_start = full_date_start + relativedelta(hours=12)
            
        if full_date_end.hour < 10:
            full_date_end = full_date_end + relativedelta(hours=12) 
            
        event.add('dtstart', full_date_start)
        event.add('dtend', full_date_end)
        event.add('summary', pdf.stem + f': {speaker}, {school}')
        event.add('location', room)
        cal.add_component(event)
    
# save to file
with open("output/cal.ical", 'wb') as f:
    f.write(cal.to_ical())