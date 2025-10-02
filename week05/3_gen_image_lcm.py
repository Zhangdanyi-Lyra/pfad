from diffusers import AutoPipelineForText2Image, LCMScheduler
import torch

model = 'lykon/dreamshaper-8-lcm'

# For Apple Silicon Mac, use float32 and MPS device
if torch.backends.mps.is_available():
    pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float32)
    device = "mps"
    print("Using Apple Silicon MPS device")
else:
    pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float16)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

pipe.to(device)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)

while True:
    prompt = input("Type a prompt and press enter to generate an image:\n>>> ")
    images = pipe(prompt, num_inference_steps=4, guidance_scale=1.5).images
    images[0].show()
