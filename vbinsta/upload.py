import click
from instagrapi.exceptions import PhotoNotUpload
from rich.console import Console
import os
from .functions import upload_single_image, upload_carousel
from .function_gpt import process_images
from .choice_option import ChoiceOption
from .login import LOGIN, RELOGIN


USERNAME = os.getenv('INSTA_USERNAME')
PASSWORD = os.getenv('INSTA_PASSWORD')

SESSION_FILE = os.path.expanduser("~/.vbinsta_session.json")


@click.command()
@click.option(
    '--image',
    '-i',
    required=True,
    type=click.Path(exists=True),
    multiple=True,
    help='Path to the image file to upload.'
)
@click.option(
    "-p",
    "--prompt",
    cls=ChoiceOption,
    type=click.Choice(
        [
            "Analyse this image it contains a physics problem, describe the problem and discuss the solution approach, in caption format for insta in simple text, don't format for web page",
            "Analyse this image and write an instagram caption with few hashtags, keep it under 1500 characters and conceptual.",
            "prompt",
        ],
        case_sensitive=False),
    prompt=True,
    default=1,
    show_default=True,
    help="Prompt to use for the completion",
)
@click.option(
    "-m",
    "--model",
    cls=ChoiceOption,
    type=click.Choice(
        [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-vision-preview",
        ],
        case_sensitive=False),
    prompt=True,
    default=1,
    show_default=True,
    help="Prompt to use for the completion",
)
def upload(image, prompt, model):
    try:
        client = LOGIN()
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if prompt == "prompt":
        prompt = click.prompt("Enter the prompt: ")

    # Verify if the login was successful
    if client.user_id:
        print("Login successful!: @10xphysics\n")
        with Console().status("Processing images...", spinner="dots"):
            caption = process_images(
                image[0:1],
                prompt,
                model,
                os.getenv('OPENAI_API_KEY'),
                1500
            )
        try:
            if len(image) == 1:
                with Console().status("Uploading image...", spinner="dots"):
                    upload_single_image(
                        client, image[0], caption + "\n\n Captions generated using gpt-4o!")
            if len(image) > 1:
                with Console().status("Uploading carousel...", spinner="dots"):
                    upload_carousel(client, image, caption +
                                    "\n\n Captions generated using gpt-4o!")
        except PhotoNotUpload:
            print("Upload failed. Re-authenticating...")
            try:
                client = RELOGIN()
                # Retry upload after re-authentication
                if len(image) == 1:
                    with Console().status("Uploading image...", spinner="dots"):
                        upload_single_image(
                            client, image[0], caption + "\n\n Captions generated using gpt-4o!")
                if len(image) > 1:
                    with Console().status("Uploading carousel...", spinner="dots"):
                        upload_carousel(client, image, caption +
                                        "\n\n Captions generated using gpt-4o!")
            except Exception as e:
                print(f"Re-authentication failed: {e}")
    else:
        print("Login failed.")
