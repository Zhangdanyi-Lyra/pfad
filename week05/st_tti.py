import streamlit as st
from diffusers import DiffusionPipeline
import torch

if "pipeline" not in st.session_state:
    model = "runwayml/stable-diffusion-v1-5"
    st.session_state["pipeline"] = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float32)
    # change to mps if on Mac with Apple Silicon
    device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    st.session_state["pipeline"].to(device)

if prompt := st.text_input("Prompt"):
    with st.spinner("Generating..."):
        img = st.session_state["pipeline"](prompt)
        st.image(img[0], use_container_width=True)