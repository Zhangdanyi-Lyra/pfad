from diffusers import DiffusionPipeline
import torch

print("开始加载模型...")

model = "runwayml/stable-diffusion-v1-5"

try:
    # Load the model and move it to the GPU if available
    # For Apple Silicon Mac, use float32 instead of float16 for better compatibility
    if torch.backends.mps.is_available():
        print("使用 Apple Silicon MPS 设备")
        pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float32)
        device = "mps"
    else:
        print("使用 CPU 或 CUDA 设备")
        pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16)
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"模型加载完成，使用设备: {device}")
    pipe.to(device)
    print("模型已移动到设备")

    # 生成一张测试图片
    prompt = "a beautiful sunset over mountains"
    print(f"生成图像: '{prompt}'")
    
    images = pipe(prompt, num_inference_steps=20).images
    
    # 保存图像而不是显示（避免显示问题）
    images[0].save("generated_image.png")
    print("✅ 图像已保存为 generated_image.png")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()