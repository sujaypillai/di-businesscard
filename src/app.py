import os
import streamlit as st
import pandas as pd

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

st.write("   Upload a business card ...")

uploaded_file = st.file_uploader("Choose your file", type=['png', 'jpg'])

if uploaded_file:
    st.image(image=uploaded_file, caption='Uploaded Image.')

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

def safe_value(val):
    # Convert complex SDK objects to string, leave primitives as is
    if isinstance(val, (str, int, float, type(None))):
        return val
    return str(val)

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.read()
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-businessCard",
        document=bytes_data
    )
    result = poller.result()
    #st.write("Document contains content: ", result.content)

    business_cards_data = []

    for idx, business_card in enumerate(result.documents):
        for field_name, field in business_card.fields.items():
            # Handle list fields (e.g., ContactNames, CompanyNames, etc.)
            if hasattr(field.value, '__iter__') and not isinstance(field.value, str):
                for item in field.value:
                    # For nested fields like ContactNames
                    if hasattr(item, 'value') and isinstance(item.value, dict):
                        for subfield_name, subfield in item.value.items():
                            business_cards_data.append({
                                'Field': f"{field_name}.{subfield_name}",
                                'Value': safe_value(subfield.value if hasattr(subfield, 'value') else None),
                                'Confidence': f"{subfield.confidence * 100:.2f}%" if hasattr(subfield, 'confidence') else None
                            })
                    else:
                        business_cards_data.append({
                            'Field': field_name,
                            'Value': safe_value(getattr(item, 'value', getattr(item, 'content', None))),
                            'Confidence': f"{getattr(item, 'confidence', 0) * 100:.2f}%" if hasattr(item, 'confidence') else None
                        })
            else:
                business_cards_data.append({
                    'Field': field_name,
                    'Value': safe_value(getattr(field, 'value', getattr(field, 'content', None))),
                    'Confidence': f"{getattr(field, 'confidence', 0) * 100:.2f}%" if hasattr(field, 'confidence') else None
                })

    if business_cards_data:
        df_cards = pd.DataFrame(business_cards_data)
        st.write("Extracted Business Card Data:")
        st.dataframe(df_cards)
