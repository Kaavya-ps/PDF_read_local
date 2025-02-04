# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 11:09:57 2025

@author: ts235
"""

import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Retrieve the API key from Streamlit secrets
api_key = st.secrets["API_KEY"]

# Configure API key
genai.configure(api_key=api_key)

# Create GenerativeModel instance
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Streamlit app
st.title('ServiceNow Tickets PDF Assistant')

# Upload PDF file
pdf_path = st.file_uploader("Upload a PDF file", type="pdf")

if pdf_path:
    pdf_reader = PdfReader(pdf_path)

    # Extract "Short Description" and "Resolution" from each page
    descriptions = []
    resolutions = []
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        description_start = page_text.find("Short Description:")
        if description_start != -1:
            description_start += len("Short Description:")
            description_end = page_text.find("Resolution:")
            descriptions.append(page_text[description_start:description_end].strip())

        resolution_start = page_text.find("Resolution:")
        if resolution_start != -1:
            resolution_start += len("Resolution:")
            resolutions.append(page_text[resolution_start:].strip())

    pdf_content = {"descriptions": descriptions, "resolutions": resolutions}

# User input for questions
user_input = st.text_input("Ask a question about the PDF:")
submit_button = st.button("Submit")

if submit_button and user_input:
    # Construct a refined prompt
    prompt = f"""
    **Question:** {user_input}

    **Context:** 
    This PDF contains information about Service Now tickets, including "Short Description" and "Resolution" for each ticket.

    **Instructions:**
    1. If the "Resolution" has multiple steps, give the exact answer present in the "Resolution".
    2. For all the queries being asked from the "Short Description", display all the steps from the "Resolution".
    3. If the question can be answered directly from the "Short Description" of any ticket, answer based on that.
    4. If the question requires information from the "Resolution" of any ticket to be answered correctly, use the "Resolution" information.
    5. If the answer cannot be found in either "Short Description" or "Resolution", state "Answer not found in the provided PDF."
    6. If the input is a common greeting, respond with an appropriate greeting message.

    **Data:**
    * **Short Descriptions:** {pdf_content["descriptions"]}
    * **Resolutions:** {pdf_content["resolutions"]}

    Answer the question wordly and accurately based on the provided data and instructions.
    """

    # Generate answer using the Gemini model
    response = model.generate_content(contents=[prompt])
    st.write(f"MES Bot: {response.text}")
