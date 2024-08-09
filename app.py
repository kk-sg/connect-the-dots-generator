import streamlit as st
import os
import datetime
from openai import OpenAI
import requests
from typing import List
import zipfile
import io
from PIL import Image

def get_api_key():
    return st.text_input("Enter your OpenAI API key (don't worry, we won't peek!)", type='password', key="api_key_input")


def generate_themes(client):
    if 'themes' not in st.session_state:
        prompt = "Generate a list of 10 suitable themes for children's connect the dots activity."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        themes = response.choices[0].message.content.strip().split('\n')
        st.session_state.themes = [theme.strip('- ') for theme in themes]
    return st.session_state.themes


def generate_one_liner(client, theme):
    prompt = f"Generate a simple one-liner prompt suitable for a children's connect-the-dots image. The image is to be only a single object in a simple, black and white line art style. The single object is based on the theme: {theme}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_image(client, prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url


def save_image(url, folder_name, image_number):
    os.makedirs(folder_name, exist_ok=True)
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(
            folder_name, f"generated_image_{image_number}.png")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    return None


def create_zip_file(folder_name):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_name):
            for file in files:
                zip_file.write(os.path.join(root, file), file)
    return zip_buffer


def main():
    st.title("🪄 AI Connect-the-Dots Generator 🖍️")

    st.markdown("""
    Step into the realm of dotted delights! This Streamlit app is your enchanted portal to crafting charming connect-the-dots puzzles that will captivate youngsters (and let's face it, grown-ups too) with pure joy!

    ## 🌟 What's This All About?""")
    
    # Load and display the image
    image = Image.open('./images/dino.jpg')
    st.image(image, caption='Complete the cuteness')
    
    st.markdown("""
    Imagine conjuring a parade of delightful dot puzzles with a wave of your digital wand! That's exactly what you can do here! Our app harnesses the magic of AI to whip up custom connect-the-dots pages quicker than you can sharpen your favorite pencil!

    ## 🚀 Features

    - 🖋️ Conjure one-of-a-kind dot puzzles across various motifs
    - 🖼️ Choose how many masterpieces you want to connect (up to 10!)
    - 💾 Save your dot-tastic creations in a neat zip package
    - 🌞 Ideal for lazy Sundays, festive gatherings, or whenever you crave a sprinkle of dot-driven delight

    ## 🔑 Getting Your OpenAI API Key

    Before you can start generating cute images, you'll need an OpenAI API key. Here's how to get one:

    1. Visit [OpenAI's website](https://platform.openai.com/)
    2. Sign up or log in: If you don't have an account, click "Sign up" and create one. If you already have an account, click "Log in".
    3. Navigate to API keys: Once logged in, look for your account name or icon in the top-right corner of the page. Click on it to open a dropdown menu.
    4. Select "Your Profile".
    5. Select "User API keys".
    6. Create a new API key: Look for a button that says "Create new secret key" or "+ New secret key".
    7. Name your key (optional): You may have the option to give your API key a name.
    8. Copy and save your API key: After creating the key, you'll see it displayed once. Make sure to copy it immediately and store it securely, as you won't be able to see it again.
    9. Set up billing: Before you can use your API key, you need to set up billing. Look for a "Billing" or "Payment" section in the account settings or main menu.
    10. Set usage limits (optional): In the billing section, you may be able to set usage limits to control your spending.
    """)

    st.markdown("---")  # This adds a horizontal line for separation

    # Initialize session state for theme if it doesn't exist
    if 'selected_theme' not in st.session_state:
        st.session_state.selected_theme = None

    api_key = get_api_key()
    if api_key:
        client = OpenAI(api_key=api_key)

        # Generate themes only if they don't exist in session state
        if 'themes' not in st.session_state:
            generate_themes(client)

        # Use session state to maintain the selected theme
        selected_theme = st.selectbox("Select a theme", st.session_state.themes, key="theme_selector", index=st.session_state.themes.index(
            st.session_state.selected_theme) if st.session_state.selected_theme in st.session_state.themes else 0)

        # Update session state when a new theme is selected
        if selected_theme != st.session_state.selected_theme:
            st.session_state.selected_theme = selected_theme

        num_images = st.slider("Number of images to generate",
                               min_value=1, max_value=10, value=3, key="num_images_slider")

        st.warning(
            f"You've chosen to generate {num_images} images. Please note that generating more images will increase your API usage and costs.")

        if st.button("Generate Images", key="generate_button"):
            one_liner_theme_prompt = generate_one_liner(
                client, st.session_state.selected_theme)
            st.write(
                f"Creating images based on '{st.session_state.selected_theme}'")

            folder_name = f"{st.session_state.selected_theme.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            generated_file_paths = []

            progress_bar = st.progress(0)
            for i in range(num_images):
                generate_image_prompt = f"""Generate a simple one-liner prompt suitable for a children's connect-the-dots image. The image is to be only a single object in a simple, black and white line art style. 
                The single object theme is '{st.session_state.selected_theme}': {one_liner_theme_prompt}. 
                Ensure the design has clear lines and very simple shapes that will look good when scaled up for printing on A4 paper. 
                Avoid intricate details that may be lost when printed."""

                image_url = generate_image(client, generate_image_prompt)
                file_path = save_image(image_url, folder_name, i + 1)
                generated_file_paths.append(file_path)
                progress_bar.progress((i + 1) / num_images)

            st.write(
                f"Generated {num_images} images for theme: {st.session_state.selected_theme}")
            for file_path in generated_file_paths:
                st.image(file_path)

            zip_buffer = create_zip_file(folder_name)
            st.download_button(
                label="Download Images",
                data=zip_buffer.getvalue(),
                file_name=f"{folder_name}.zip",
                mime="application/zip",
                key="download_button"
            )

            st.info("Note: These images are generated at 1024x1024 pixels. For best print quality on A4 paper, you may need to scale them up slightly using an image editing software.")


if __name__ == "__main__":
    main()
