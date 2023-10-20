import pandas as pd
import streamlit as st
import plotly_express as px
import datetime
from barcode import Code39
import os
import sys
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
#import path
#PATH = os.getcwd()+'/pages'
#sys.path.append(PATH)
#Import modules
from plate_picking import make_plate_list, generate_barcode, machine_barcode, get_table_map, convert_images_html
from streamlit_helper_functions import convert_df

#Global Variables. 
load_dotenv()
QTREY_ROT_90 = os.getenv("QTREY_ROT_90")
QTREY_ROT_180 = os.getenv("QTREY_ROT_180")



def convert_qpix_wells(df, qpix_rot_dict:
	print(df.columns)
	df = df.rename(columns={'Source Region': 'Qpix Source Well'})
	df['Human Source Well'] = df['Qpix Source Well'].map(qpix_rot_dict)
	df = df[['Source Barcode', 'Destination Barcode', 'Qpix Source Well', 'Human Source Well', 'Destination Well']]
	return df

st.title("Colony Picking Dashboard.")
def main():
    
	option = st.selectbox(
	label = "Please select whether picking from petri plates or 48-well Qtreys :sunglasses:",
	options = ('Petri Plates', '48-well Qtrey'),
	index=None)
	st.write('You selected:', option)
    
	if option == 'Petri Plates':
		upload_file = st.file_uploader(label="Please Upload Petri dish colony picking submission form")
		if upload_file is not None:
			df = pd.read_csv(upload_file, delimiter=',')
			df_list = make_plate_list(df)
			for dframe in df_list:
				df2 = generate_barcode(dframe, plate_type='petri')
				st.write(df2)
			st.download_button(
                        label = "Download as CSV",
                        data = convert_df(df2),
                        file_name = 'petri_plate_input.csv',
                        mime = "text/csv",
                        )

		upload_file2 = st.file_uploader(label="Please Upload QPIX output", key=2)
		if upload_file2 is not None:
			df_fig = pd.read_csv(upload_file2, header=11)
			fig = get_table_map(df_fig)
			st.plotly_chart(fig, use_container_width=True)                   	

	elif option == '48-well Qtrey':
		st.write('Go Time!')
		upload_file = st.file_uploader(label="Please Upload 48-well Qtrey colony picking submission form")
		if upload_file is not None:
			df = pd.read_csv(upload_file, delimiter=",")
			df_list = make_plate_list(df)
			for dframe in df_list:
				df2 = generate_barcode(dframe, plate_type = 'qtrey')
				df2_html = df2.to_html(escape=False, formatters = {'Source Agar Plate Barcode_image_path':convert_images_html})
				columns = ['Name', 'Source Agar Plate Name', 'Source Agar Plate No.', 'Source Well', 'No. Colonies', 
					'Source Agar Plate Barcode', 'Destination 96 Plate Barcode'
					]
				df2_view = df2[columns]
				st.write(df2_view)
				#st.markdown(df2_html, unsafe_allow_html=True)
			st.download_button(
			label = "Download qtrey input as CSV",
			data = convert_df(df2),
			file_name = 'qtrey_input.csv',
			mime = "text/csv",
			)

			unique_source_barcodes = df2['Source Agar Plate Barcode_image_path'].unique().tolist()
			unique_destination_barcodes = df2['Destination 96 Plate Barcode_image_path'].unique().tolist()
			print(unique_source_barcodes)
			
			for i in unique_source_barcodes:
				st.image(i, caption='Source Agar Plate Barcode')
				with open(i, "rb") as file:
					btn = st.download_button(
							'Download plate barcode',
							data=file,
							file_name='Source Barcode', 
							key=i, 
							mime="image/jpeg")
			for i in unique_destination_barcodes:
				st.image(i, caption='Destination Plate Barcode')
				st.download_button('Download plate barcode',i, key=i, mime="image/jpeg") 

		
		qpix_orientation = st.selectbox(
			"Please Select QTrey plate orientation. Please do not change from ROT_90 unless you know what you are doing ",
			("ROT_90", "ROT_180"),
			key = 'qtrey orientation')
		orientation = QTREY_ROT_90				 
		if qpix_orientation == "ROT_180":
			orientation = QTREY_ROT_180
		
		upload_file2 = st.file_uploader(label="Please Upload Qpix qtrey picking output", key=3)
		if upload_file2 is not None:
			df3 = pd.read_csv(upload_file2, header=6)
			df3 = convert_qpix_wells(df3, orientation)
			st.write(df3)

			st.download_button(
			label = "Downlaod qtrey output as CSV",
			data = convert_df(df3),
			file_name = 'qtrey_output.csv',
			mime = "text/csv",
			)		
if __name__ == "__main__":
    main()
