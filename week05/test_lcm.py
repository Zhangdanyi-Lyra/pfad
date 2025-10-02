from diffusers import AutoPipelineForText2Image, LCMScheduler
import torch

print("开始加载 LCM 模型...")

model = 'lykon/dreamshaper-8-lcm'

try:
    # For Apple Silicon Mac, use float32 and MPS device
    if torch.backends.mps.is_available():
        pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float32)
        device = "mps"
        print("使用 Apple Silicon MPS 设备")
    else:
        pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float16)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用设备: {device}")

    pipe.to(device)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    print("模型加载完成！")
    
    # 生成测试图片
    prompt = "a cute cat sitting on a chair, photorealistic"
    print(f"生成图像: '{prompt}'")
    print("LCM 模型只需要 4 步推理，速度很快...")
    
    images = pipe(prompt, num_inference_steps=4, guidance_scale=1.5).images
    
    # 保存图像
    images[0].save("lcm_generated_image.png")
    print("✅ LCM 图像已保存为 lcm_generated_image.png")
    
    # 如果想要交互模式，可以取消下面的注释
    # while True:
    #     prompt = input("Type a prompt and press enter to generate an image:\n>>> ")
    #     images = pipe(prompt, num_inference_steps=4, guidance_scale=1.5).images
    #     images[0].show()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()