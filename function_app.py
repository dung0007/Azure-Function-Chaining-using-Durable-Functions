from PIL import Image
import azure.functions as func
import azure.durable_functions as df
import logging
import io

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="orchestrator_function", methods=["POST"])
def orchestrator_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function - Orchestrator Function processed a request.')

    try:
        req_body = req.get_json()
        image_data = req_body.get('image_data')
        watermark_text = req_body.get('watermark_text')

        # Call activity functions in sequence
        resized_image_data = resize_image(image_data)
        grayscale_image_data = grayscale_image(resized_image_data)
        watermarked_image_data = watermark_image(grayscale_image_data, watermark_text)

        return func.HttpResponse(body=watermarked_image_data, status_code=200, mimetype="image/jpeg")

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

def resize_image(image_data: bytes) -> bytes:
    logging.info('Resizing image...')
    image = Image.open(io.BytesIO(image_data))
    resized_image = image.resize((1024, 768))  # Resize to 1024x768 pixels

    output_buffer = io.BytesIO()
    resized_image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    return output_buffer.read()

def grayscale_image(image_data: bytes) -> bytes:
    logging.info('Converting image to grayscale...')
    image = Image.open(io.BytesIO(image_data)).convert("L")  # Convert to grayscale

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    return output_buffer.read()

def watermark_image(image_data: bytes, watermark_text: str) -> bytes:
    logging.info('Adding watermark to image...')
    image = Image.open(io.BytesIO(image_data))

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), watermark_text, fill="white", font=font)

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    return output_buffer.read()
