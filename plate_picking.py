import os
import pandas as pd
import streamlit as st
import plotly.figure_factory as ff 
import plotly_express as px
import plotly.offline as pyo
import datetime
#import barcode
from barcode import Code39
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image

def rowIndex(row):
	return row.name


def make_plate_list(df):#Tests if there are more than 96 colonies
	
	if df['No. Colonies'].sum() < 97:
		return [df]	
	else:
		print("Still working on multiple plates")

# Converting links to html tags
def convert_images_html(path_to_image):
	return f'<img src={path_to_image} width = 60 >'

def machine_barcode(human_bc: str):
	image_path = os.getcwd()+'/barcode_images/'+human_bc+'.jpg'
	#code39 = barcode.get_barcode_class('code39')
	my_code39 = Code39(human_bc, writer=ImageWriter())
	img_bytes = BytesIO()
	my_code39.write(img_bytes)
	img = Image.open(img_bytes)
	img.save(image_path, "JPEG")
	return (image_path)


def generate_barcode(df, plate_type):
	
	date_time = datetime.datetime.now()
	str_date_time = date_time.strftime("%d%m%Y%H%M%S")
	barcode = df['Name'].str.split(' ')[0][0][0]+df['Name'].str.split(' ')[1][1][0]+'source'+str_date_time	
	df['Source Barcode'] = barcode
	
	if plate_type == 'petri':
		df['Source Agar Plate No.'] = df.apply(rowIndex, axis=1)+1
	elif plate_type == 'qtrey':
		df['Source Agar Plate No.'] = 1
	
	df['Source Agar Plate No.'] = df['Source Agar Plate No.'].astype(str)
	df['Source Agar Plate Barcode'] = (df['Source Barcode']+df['Source Agar Plate No.']).str.upper() # .apply(lambda x: Code39(x))
	df['Destination 96 Plate Barcode'] = barcode.replace('source', 'dest').upper()
	df_stamp = df.copy()
	df_stamp['Destination 96 Plate Barcode'] = barcode.replace('source', 'stamp').upper()
	df = pd.concat([df, df_stamp], axis = 0, ignore_index=True)
	
	if plate_type == 'petri': 
		df = df[['Name', 'Source Agar Plate Name', 'Source Agar Plate No.', 'No. Colonies', 'Source Agar Plate Barcode', 'Destination 96 Plate Barcode']]  
	elif plate_type == 'qtrey':
		df = df[['Name', 'Source Agar Plate Name', 'Source Agar Plate No.','Source Well', 'No. Colonies', 'Source Agar Plate Barcode', 'Destination 96 Plate Barcode']]
	
	for i in ['Source Agar Plate Barcode', 'Destination 96 Plate Barcode']:	
		d = {}
		d_image = {}
		for human_barcode in df[i].unique().tolist():
			img_path = machine_barcode(human_barcode)
			print(img_path, human_barcode)
			d_image[human_barcode] = img_path
			html_path = convert_images_html(img_path)
			d[human_barcode] = html_path
			print(d)
		df[i+'_image_path'] = df[i].map(d_image)	
		df[i+'_machine'] = df[i].map(d)
	
	return df


def get_table_map(df):
	df['row'] = df['Destination Well'].apply(lambda x: x[0])
	df['col'] = df['Destination Well'].apply(lambda x: x[1:])
	df = df[['Source Barcode', 'Destination Barcode', 'row', 'col']]
	
	d = {}
	for i,j in enumerate(df['Source Barcode'].unique()):
		d[j] = float(i+1)
		df['key'] = df['Source Barcode'].map(d)
	table = pd.pivot_table(df, index = 'row', columns = 'col', values = 'key', aggfunc='median')
	table = table[['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']]
    
	#Make the Plate Map
	fig = px.imshow(table, text_auto=True)
	#Make it look nice.
	for row in [i+0.5 for i,j in enumerate(table.index.to_list())]:
		fig.add_hline(y=row, line_color = 'white')
	for col in [i+0.5 for i,j in enumerate(table.columns.to_list())]:
		fig.add_vline(x=col, line_color = 'white')
	fig = fig.update_xaxes(showgrid=False)
	fig = fig.update_yaxes(showgrid=False)
	
	return fig


