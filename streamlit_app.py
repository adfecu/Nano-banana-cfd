

import streamlit as st
from io import BytesIO
from google import genai
from google.genai import types
from utils import get_image_pairs


st.title("🍌 Nano Banana CFD")
st.write("Generate high-resolution images of airfoils with smooth airflow lines using Nano Banana")

# Add X profile link
st.markdown('[Follow me on X](https://x.com/afernandezc146)', unsafe_allow_html=True)

# Create two columns
col1, col2 = st.columns(2)

prompt = "Generate a high-resolution image of an airfoil with smooth airflow lines around it. The streamlines CANNOT intersect or overlap, and they should clearly show the airflow pattern around the airfoil."

# Prepare all three input/output image pairs as a single list alternating input/output
image_pairs = get_image_pairs()

example_parts = []
for input_path, output_path in image_pairs:
	with open(input_path, 'rb') as f_in:
		img_in_bytes = f_in.read()
	with open(output_path, 'rb') as f_out:
		img_out_bytes = f_out.read()
	example_parts.append(types.Part.from_bytes(
		data=img_in_bytes,
		mime_type='image/png'
	))
	example_parts.append(types.Part.from_bytes(
		data=img_out_bytes,
		mime_type='image/png'
	))

# Input column
with col1:
	st.header("Input")
	
	uploaded_file = st.file_uploader("Upload an image of your airfoil", type=["png", "jpg", "jpeg"])
	if uploaded_file:
		st.image(uploaded_file)

# Output column
with col2:
	st.header("Output")
	if uploaded_file:
				if st.button("Generate Image"):
					with st.spinner("Generating..."):
						client = genai.Client()
						image_bytes = uploaded_file.read()
						image_part = types.Part.from_bytes(
							data=image_bytes,
							mime_type=uploaded_file.type or "image/jpeg",
						)
						response = client.models.generate_content(
							model="gemini-2.5-flash-image-preview",
							contents=[prompt] + example_parts + [image_part],
							config=types.GenerateContentConfig(
								temperature=0.05
							)
						)
						output_image = None
						for part in response.candidates[0].content.parts:
							if part.inline_data is not None:
								output_image = BytesIO(part.inline_data.data)
								st.image(output_image)
						# Second call: classify flow condition
						if output_image is not None:
							classify_prompt = (
								"Based on this airfoil image, is the flow Normal, is there Flow Separation, or is there a Stall condition? "
								"Respond with only one of: Normal flow, Flow Separation, Stall condition."
							)
							output_image.seek(0)
							output_part = types.Part.from_bytes(
								data=output_image.read(),
								mime_type="image/png",
							)
							classify_response = client.models.generate_content(
								model="gemini-2.5-flash-image-preview",
								contents=[classify_prompt, output_part],
							)
							# Extract and display the classification result
							try:
								classification = classify_response.candidates[0].content.parts[0].text.strip()
							except Exception:
								classification = "Unable to determine flow condition."
							st.markdown(f"**Flow Condition:** {classification}")

