"""Service for processing images using Google Vision API."""
import base64
from typing import Optional, Dict, Any
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)

class ImageProcessingService:
    """Service for extracting text and information from images using Google Vision API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the image processing service.

        Args:
            api_key: Google Vision API key
        """
        self.api_key = api_key
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"

        if not api_key:
            logger.warning("Google Vision API key not provided - image processing will be disabled")
        else:
            logger.info("Image processing service initialized with Google Vision API")

    def extract_text_from_image(self, image_bytes: bytes, file_path: str = "") -> Dict[str, Any]:
        """
        Extract text from an image using Google Vision API.

        Args:
            image_bytes: Raw image bytes
            file_path: Path to the image file (for logging)

        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.api_key:
            logger.warning("Google Vision API key not configured - skipping image processing")
            return {
                "text": "",
                "labels": [],
                "web_entities": [],
                "error": "API key not configured"
            }

        try:
            logger.debug(f"Processing image: {file_path}")

            # Convert image bytes to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Prepare the API request
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {"type": "TEXT_DETECTION"},  # Extract text
                            {"type": "LABEL_DETECTION", "maxResults": 10},  # Image labels
                            {"type": "WEB_DETECTION"}  # Web entities
                        ]
                    }
                ]
            }

            # Make API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            result = response.json()

            if "responses" not in result or len(result["responses"]) == 0:
                logger.warning(f"No response from Vision API for {file_path}")
                return {
                    "text": "",
                    "labels": [],
                    "web_entities": [],
                    "error": "No response from API"
                }

            response_data = result["responses"][0]

            # Extract text
            extracted_text = ""
            if "textAnnotations" in response_data and len(response_data["textAnnotations"]) > 0:
                # First annotation contains all detected text
                extracted_text = response_data["textAnnotations"][0].get("description", "")
                logger.info(f"Extracted {len(extracted_text)} characters of text from {file_path}")
            else:
                logger.debug(f"No text found in image: {file_path}")

            # Extract labels
            labels = []
            if "labelAnnotations" in response_data:
                labels = [
                    {
                        "description": label.get("description", ""),
                        "score": label.get("score", 0.0)
                    }
                    for label in response_data["labelAnnotations"]
                ]
                logger.debug(f"Extracted {len(labels)} labels from {file_path}")

            # Extract web entities
            web_entities = []
            if "webDetection" in response_data and "webEntities" in response_data["webDetection"]:
                web_entities = [
                    {
                        "description": entity.get("description", ""),
                        "score": entity.get("score", 0.0)
                    }
                    for entity in response_data["webDetection"]["webEntities"]
                    if entity.get("description")
                ]
                logger.debug(f"Extracted {len(web_entities)} web entities from {file_path}")

            return {
                "text": extracted_text,
                "labels": labels,
                "web_entities": web_entities,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process image {file_path}: {e}")
            return {
                "text": "",
                "labels": [],
                "web_entities": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error processing image {file_path}: {e}")
            return {
                "text": "",
                "labels": [],
                "web_entities": [],
                "error": str(e)
            }

    def format_image_content(self, vision_result: Dict[str, Any], file_path: str, file_name: str) -> str:
        """
        Format the Vision API results into a text document for embedding.

        Args:
            vision_result: Result from extract_text_from_image
            file_path: Path to the image file
            file_name: Name of the image file

        Returns:
            Formatted text content combining all extracted information
        """
        content_parts = [f"# Image: {file_name}\n"]
        content_parts.append(f"**File Path:** {file_path}\n\n")

        # Add extracted text
        if vision_result.get("text"):
            content_parts.append("## Extracted Text\n")
            content_parts.append(vision_result["text"])
            content_parts.append("\n\n")

        # Add labels
        if vision_result.get("labels"):
            content_parts.append("## Image Labels\n")
            for label in vision_result["labels"][:5]:  # Top 5 labels
                content_parts.append(f"- {label['description']} (confidence: {label['score']:.2f})\n")
            content_parts.append("\n")

        # Add web entities
        if vision_result.get("web_entities"):
            content_parts.append("## Related Concepts\n")
            for entity in vision_result["web_entities"][:5]:  # Top 5 entities
                content_parts.append(f"- {entity['description']}\n")
            content_parts.append("\n")

        return "".join(content_parts)
