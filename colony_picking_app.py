import pandas as pd
import streamlit as st
import plotly_express as px
import datetime
from barcode import Code39
import os
import sys
from io import BytesIO
from PIL import Image

#import path
#PATH = os.getcwd()+'/pages'
#sys.path.append(PATH)
#Import modules
from plate_picking import make_plate_list, generate_barcode, machine_barcode, get_table_map, convert_images_html
from streamlit_helper_functions import convert_df

#Global Variables. Will import these properly when I have time.
#For dict below key is qpix and value is human
QPIX_DICT_90 = {'A1': 'A1','B1': 'A2','C1': 'A3','D1': 'A4','E1': 'A5','F1': 'A6',
 	     'A2': 'B1', 'B2': 'B2', 'C2': 'B3', 'D2': 'B4', 'E2': 'B5', 'F2': 'B6',
 	     'A3': 'C1', 'B3': 'C2', 'C3': 'C3', 'D3': 'C4', 'E3': 'C5', 'F3': 'C6',
 	     'A4': 'D1', 'B4': 'D2', 'C4': 'D3', 'D4': 'D4', 'E4': 'D5', 'F4': 'D6',
 	     'A5': 'E1', 'B5': 'E2', 'C5': 'E3', 'D5': 'E4', 'E5': 'E5', 'F5': 'E6',
 	     'A6': 'F1', 'B6': 'F2', 'C6': 'F3', 'D6': 'F4', 'E6': 'F5', 'F6': 'F6',
	     'A7': 'G1', 'B7': 'G2', 'C7': 'G3', 'D7': 'G4', 'E7': 'G5', 'F7': 'G6',
             'A8': 'H1', 'B8': 'H2', 'C8': 'H3', 'D8': 'H4', 'E8': 'H5', 'F8': 'H6'
	    }

QPIX_DICT_180 = {'H6': 'A1', 'H5': 'A2', 'H4': 'A3', 'H3': 'A4', 'H2': 'A5', 'H1': 'A6', 
		'G6': 'B1', 'G5': 'B2', 'G4': 'B3', 'G3': 'B4', 'G2': 'B5', 'G1': 'B6',
 		'F6': 'C1', 'F5': 'C2', 'F4': 'C3', 'F3': 'C4', 'F2': 'C5', 'F1': 'C6', 
		'E6': 'D1', 'E5': 'D2', 'E4': 'D3', 'E3': 'D4', 'E2': 'D5', 'E1': 'D6', 
		'D6': 'E1', 'D5': 'E2', 'D4': 'E3', 'D3': 'E4', 'D2': 'E5', 'D1': 'E6', 
		'C6': 'F1', 'C5': 'F2', 'C4': 'F3', 'C3': 'F4', 'C2': 'F5', 'C1': 'F6', 
		'B6': 'G1', 'B5': 'G2', 'B4': 'G3', 'B3': 'G4', 'B2': 'G5', 'B1': 'G6', 
		'A6': 'H1', 'A5': 'H2', 'A4': 'H3', 'A3': 'H4', 'A2': 'H5', 'A1': 'H6'
}	

 
def convert_qpix_wells(df, qpix_rot_dict):
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
				df2_html = df2.to_html(escape=False, formatters = {'Source Agar Plate Barcode_machine':convert_images_html})
				st.write(df2_html, unsafe_allow_html=True)
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

		upload_file2 = st.file_uploader(label="Please Upload Qpix qtrey picking output", key=3)
		if upload_file2 is not None:
			df3 = pd.read_csv(upload_file2, header=6)
			df3 = convert_qpix_wells(df3, QPIX_DICT_180)
			st.write(df3)

			st.download_button(
			label = "Downlaod qtrey output as CSV",
			data = convert_df(df3),
			file_name = 'qtrey_output.csv',
			mime = "text/csv",
			)		
if __name__ == "__main__":
    main()
