# make sure you're logged in with `huggingface-cli login`
import time
from diffusers import StableDiffusionPipeline


def handle(input_data):
    try:
        prompt = input_data["prompt"]
        device = input_data["device"]
    except Exception as e:
        return {"error": str(e)}

    output_data = run_a_diffuser(prompt=prompt, device=device, is_save=False)
    return output_data


def run_a_diffuser(prompt="a photo of an astronaut riding a horse on mars", device="cpu", is_save=True):
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    pipe = pipe.to(device)

    # Recommended if your computer has < 64 GB of RAM
    pipe.enable_attention_slicing()

    # First-time "warmup" pass (see explanation above)
    start_t = time.time()
    _ = pipe(prompt, num_inference_steps=1)
    end_t = time.time()
    print(f"warmup time: {end_t - start_t}")

    # Results match those from the CPU device after the warmup pass.
    start_t = time.time()
    images = pipe(prompt).images
    end_t = time.time()
    print(f"diffusion time: {end_t - start_t}")
    image = images[0]
    print(type(image))
    if is_save:
        image.save(f"{prompt}.png")
    return image


if __name__ == "__main__":
    # 测量cpu时间
    start = time.time()
    run_a_diffuser(device="cpu")
    end = time.time()
    print(f"cpu time: {end - start}")

    start = time.time()
    run_a_diffuser(device="mps")
    end = time.time()
    print(f"mps time: {end - start}")
