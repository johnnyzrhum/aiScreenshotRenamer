# AI Screenshot & PDF Renamer - Version 1.1

import os
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image
import fitz  # PyMuPDF
from pillow_heif import register_heif_opener

# Initialize HEIC support and Load .env
register_heif_opener()
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def processBatch(directory):
    validExtensions = ('.png', '.jpg', '.jpeg', '.heic', '.pdf')
    filesToProcess = [f for f in os.listdir(directory) if f.lower().endswith(validExtensions)]
    
    print(f"Found {len(filesToProcess)} new files to process...")

    for fileName in filesToProcess:
        oldPath = os.path.join(directory, fileName)
        fileExt = os.path.splitext(fileName)[1].lower()
        success = False

        while not success:
            try:
                modelName = "gemini-3.1-flash-lite-preview"

                if fileExt == '.pdf':
                    with open(oldPath, "rb") as f:
                        docData = f.read()
                    response = client.models.generate_content(
                        model=modelName,
                        contents=[
                            "Describe this document for a filename. 3 words, underscores, no extension.",
                            {"inline_data": {"mime_type": "application/pdf", "data": docData}}
                        ]
                    )
                else:
                    img = Image.open(oldPath)
                    response = client.models.generate_content(
                        model=modelName,
                        contents=["Describe this image for a filename. 3 words, underscores, no extension.", img]
                    )

                suggestedName = response.text.strip().lower().replace(" ", "_")
                cleanName = "".join(c for c in suggestedName if c.isalnum() or c == '_')
                
                timeStamp = int(time.time() % 1000)
                newName = f"{cleanName}_{timeStamp}{fileExt}"
                newPath = os.path.join(directory, newName)
                
                os.rename(oldPath, newPath)
                print(f"✅ Renamed: {fileName} -> {newName}")
                success = True

            except Exception as e:
                errorMsg = str(e).lower()
                if "429" in errorMsg or "exhausted" in errorMsg:
                    print("⚠️ Rate limit hit. Waiting 10s...")
                    time.sleep(10)
                else:
                    print(f"❌ Skipping {fileName} due to error: {e}")
                    break

if __name__ == "__main__":
    rawPath = os.getenv("DROPBOX_PATH")
    if rawPath:
        targetDir = os.path.abspath(os.path.expanduser(rawPath))
        processBatch(targetDir)
    else:
        print("❌ Error: DROPBOX_PATH not found in .env file.")
