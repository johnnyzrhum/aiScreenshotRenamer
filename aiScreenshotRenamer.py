import os
import time  # Added this import
from dotenv import load_dotenv
from google import genai
from PIL import Image
from pillow_heif import register_heif_opener

# Initialize HEIC support and Load .env
register_heif_opener()
load_dotenv()

# Pulls the key from your hidden .env file
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1beta'}
)

def process_batch(directory):
    valid_extensions = ('.png', '.jpg', '.jpeg', '.heic')
    
    # Identify files that need renaming
    files = [f for f in os.listdir(directory) 
             if f.lower().endswith(valid_extensions) and f.startswith(('Screenshot', 'IMG_'))]
    
    print(f"Found {len(files)} new files to process...")

    for filename in files:
        old_path = os.path.join(directory, filename)
        file_ext = os.path.splitext(filename)[1].lower()
        success = False
        
        while not success:
            try:
                img = Image.open(old_path)
                
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=["Describe this image for a filename. 3 words, underscores, no extension.", img]
                )
                
                suggested_name = response.text.strip().lower().replace(" ", "_")
                clean_name = "".join(c for c in suggested_name if c.isalnum() or c == '_')
                
                # Suffix prevents overwriting if Gemini names two files the same thing
                timestamp = int(time.time() % 1000)
                new_name = f"{clean_name}_{timestamp}{file_ext}"
                new_path = os.path.join(directory, new_name)

                os.rename(old_path, new_path)
                print(f"✅ Renamed: {filename} -> {new_name}")
                success = True
                time.sleep(0.5) 

            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "exhausted" in error_msg:
                    print(f"⚠️ Rate limit hit. Waiting 10s...")
                    time.sleep(10)
                else:
                    print(f"❌ Skipping {filename} due to error: {e}")
                    break 

if __name__ == "__main__":
    raw_path = os.getenv("DROPBOX_PATH")
    
    if raw_path:
        # Use abspath + expanduser to be bulletproof against "path doubling"
        target_dir = os.path.abspath(os.path.expanduser(raw_path))
        process_batch(target_dir)
    else:
        print("❌ Error: DROPBOX_PATH not found in .env file.")
