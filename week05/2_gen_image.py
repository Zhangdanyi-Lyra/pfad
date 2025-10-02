from diffusers import DiffusionPipeline


import torch

model = "runwayml/stable-diffusion-v1-5"

# Load the model and move it to the GPU if available
# For Apple Silicon Mac, use float32 instead of float16 for better compatibility
if torch.backends.mps.is_available():
    pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float32)
    device = "mps"
else:
    pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16)
    device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")
pipe.to(device)

while True:
    prompt = input("Type a prompt and press enter to generate an image:\n>>> ")
    
    # Generate the image, for options see:
    # https://huggingface.co/docs/diffusers/en/api/pipelines/stable_diffusion/text2img
    images = pipe(prompt, num_inference_steps=20).images
    
    images[0].show()
