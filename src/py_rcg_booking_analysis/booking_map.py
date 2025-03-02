import pandas as pd
import numpy as np

# from plotly.express import density_mapbox

# postcode_lookup = pd.read_csv('open_postcode_geo.csv', names=[ 'status', 'type','easting', 'northing', 'id','country', 'latitude', 'longitude', 'postcode','postcode-7', 'postcode-8','postcode area', 'postcode district', 'postcode sector', 'incode', 'outcode' ])

def clean_postcode(value: str):
    cleaned = value.replace(' ', '').upper()
    if cleaned[:2] == 'P0':
        cleaned = 'PO' + cleaned[2:]
    return f'{cleaned[:-3]} {cleaned[-3:]}'

def postcode_extract(postcode:str):
    extraction = postcode_lookup.loc[postcode]
    return np.float64(extraction.longitude), np.float64(extraction.latitude)

if __name__ == '__main__':

    data = pd.read_csv('data.csv', names=['Postcode'], converters={'Postcode': clean_postcode})
    summary = data.groupby(['Postcode']).value_counts()
    summary = summary.to_frame('Count')
    summary['Longitude'], summary['Latitude'] = zip(*summary.index.map(postcode_extract))
    summary.dropna(inplace=True)

    fig = density_mapbox(data_frame=summary, lat='Latitude', lon='Longitude',
                         mapbox_style='open-street-map', radius=20, z='Count',
                         title='Repair Cafe Gosport\nGuest Locations')