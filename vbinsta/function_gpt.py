import re
import requests
from rich.console import Console
import pyperclip
from typing import List
import base64
import subprocess
import os
from .token_cost_calculations import calculate_image_cost, calculate_input_cost, calculate_output_cost


def encode_image(image_path):
    """
    Encodes the image located at the given image_path into base64 format.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_image_dicts(image_names: List[str]) -> List[dict]:
    """
    Encodes images to base64 and creates a list of dictionaries with image data.

    Args:
        image_names (List[str]): List of image file names.

    Returns:
        List[dict]: List of dictionaries containing base64 encoded image data.
    """
    image_dicts = []
    for image_name in image_names:
        base64_image = encode_image(image_name)
        image_dict = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        }
        image_dicts.append(image_dict)
    return image_dicts


def process_images(image_names: List[str], prompt: str, model: str, api_key: str, max_tokens: int) -> str:
    """
    Processes images using OpenAI's GPT-4 Vision, extracts LaTeX code from the response,
    copies the first match to the clipboard, and prints the message in deep pink color.

    Args:
        image_names (List[str]): List of image file names.
        prompt (str): Prompt for the GPT-4 Vision model.
        api_key (str): OpenAI API key.

    Returns:
        str: First match of the LaTeX code in the response.
    """
    image_dicts = create_image_dicts(image_names)
    title = os.path.basename(image_names[0]).split('.')[0] + ".tex"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    *image_dicts
                ]
            }
        ],
        "max_tokens": max_tokens
    }

    message = ""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        response_json = response.json()

        if 'choices' in response_json and 'message' in response_json["choices"][0]:
            message = response_json["choices"][0]["message"]["content"]

            print(f'\n\tTotal cost: {calculate_image_cost(
                image_names) + calculate_input_cost(prompt) + calculate_output_cost(message):.2f}\n')

        else:
            console = Console()
            console.print(
                "Error: 'choices' or 'message' not found in the API response.", style="bold red")
            return "Error: 'choices' or 'message' not found in the API response."
    else:
        console = Console()
        console.print(
            f"Error: API request failed with status code {response.status_code}.", style="bold red")
        return f"Error: API request failed with status code {response.status_code}."

    pyperclip.copy(message)
    subprocess.Popen(
        f'pbpaste | bat -l txt --file-name "{title}"', shell=True)
    return message
