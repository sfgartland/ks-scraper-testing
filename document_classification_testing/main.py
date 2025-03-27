import os
import pdfplumber
import torch
from transformers import (
    AutoProcessor,
    AutoModelForSequenceClassification,
    AutoTokenizer,
)
from pdf2image import convert_from_path

# Define directories
pdf_dir = "../data/FoU/000024"
# model_name = 'path/to/your/layoutlmv3-model'
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print("Loading models....")

# Load pre-trained model and processor

# processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
# processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base")
# model = AutoModelForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base")


# Use trained model
processor = AutoProcessor.from_pretrained("nielsr/layoutlmv3-finetuned-funsd")
model = AutoModelForSequenceClassification.from_pretrained("nielsr/layoutlmv3-finetuned-funsd")

def extract_text_and_boxes(pdf_path):
    """Extract text and bounding boxes from a PDF file using pdfplumber."""
    text = []
    boxes = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extract and iterate over the words and their properties
            for word in page.extract_words():
                text.append(word["text"])
                # Translate keys to match the actual structure of the word dictionary
                bbox = [word["x0"], word["top"], word["x1"], word["bottom"]]
                boxes.append(bbox)
    return text, boxes


def convert_pdf_to_images(file_path):
    """Convert PDF pages to images using pdf2image."""
    print("Converting PDF to images...")
    images = convert_from_path(file_path, last_page=1)  # TODO Change
    return images


def classify_pdf_old(text, boxes, images):
    """Classify PDF text using LayoutLMv3."""
    chunk_size = 512  # Adjust as needed, ensuring it fits the model's capability
    num_chunks = len(text) // chunk_size + (1 if len(text) % chunk_size else 0)

    logits_sum = torch.zeros((model.num_labels,))

    for i in range(num_chunks):
        text_chunk = text[i * chunk_size : (i + 1) * chunk_size]
        boxes_chunk = boxes[i * chunk_size : (i + 1) * chunk_size]

        inputs = processor(
            images=images, text=text_chunk, boxes=boxes_chunk, return_tensors="pt"
        )

        # Forward pass to get logits for the chunk
        with torch.no_grad():
            outputs = model(**inputs)

        # Add up logits for a holistic view across chunks
        logits_sum += outputs.logits[0]

    # Decide class based on cumulative logits
    predicted_class = torch.argmax(logits_sum, dim=-1).item()
    return predicted_class


def classify_pdf_images_only(images):
    """Classify PDF text using LayoutLMv3."""
    print("Encoding....")
    encoding = processor(images=images, return_tensors="pt", padding=True, truncation=True)
    sequence_label = torch.tensor([1])
    print("Computing....")
    outputs = model(**encoding, labels=sequence_label)
    loss = outputs.loss
    logits = outputs.logits
    print("Logits")
    print(logits)
    print("Loss")
    print(loss)
    probabilities = torch.nn.functional.softmax(logits, dim=1)
    print("Probabilities:", probabilities)
    predicted_label = model.config.id2label[torch.argmax(logits, dim=1).item()]
    print("Predicted Label:", predicted_label)


def classify_pdf(text, boxes, images):
    """Classify PDF text using LayoutLMv3."""
    encoding = processor(images, text, boxes=boxes, return_tensors="pt")
    sequence_label = torch.tensor([1])
    outputs = model(**encoding, labels=sequence_label)
    loss = outputs.loss
    logits = outputs.logits
    print(logits)
    print(loss)


def main():
    print("Classifying PDF files...")
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        file_path = os.path.join(pdf_dir, pdf_file)
        text, boxes = extract_text_and_boxes(file_path)
        images = convert_pdf_to_images(file_path)
        # predicted_class = classify_pdf(text, boxes, images)
        predicted_class = classify_pdf_images_only(images)
        print(f"File: {pdf_file} - Classified as class: {predicted_class}")


if __name__ == "__main__":
    main()
