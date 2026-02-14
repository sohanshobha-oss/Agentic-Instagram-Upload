import os
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from replicate.client import Client

llm=ChatGroq(model_name="openai/gpt-oss-20b", temperature=0.2)



prompt_template = PromptTemplate.from_template("""
You are an expert Stable Diffusion prompt engineer.

Rewrite the input into a single, cohesive Stable Diffusion prompt.

Requirements:
- Photorealistic
- Cinematic lighting
- DSLR photography style
- Ultra-detailed, high resolution
- Natural skin tones and realistic textures
- Shallow depth of field (bokeh)
- Professional composition

Text in Image:
- Headline should be elegant, relevant to given context, and aesthetically pleasing
- Add ONE short, impactful headline text inside the image near the bottom center.
- Dont include any colour as background or blurry background.
- Typography should feel cinematic, refined, and naturally embedded into the photograph.
- Text colors should blend with image
- Headline must NOT overpower the image

Output Rules:
- Return ONLY the final Stable Diffusion prompt
- No explanations
- No bullet points
- Single paragraph

Input:
{user_prompt}
""")

def refine_prompt(user_prompt: str) -> str:
    return llm.invoke(
        prompt_template.format(user_prompt=user_prompt)
    ).content



def generate_image(prompt: str):
    client = Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

    output = client.run(
        "google/imagen-4",
        input={
            "prompt": prompt,
            "guidance_scale": 7.5,
            "num_inference_steps": 40,
            "width": 1024,
            "height": 1024
        }
    )

    with open("output.png", "wb") as f:
        f.write(output.read())

    return "output.png"


def replicate(user_prompt):

    refined = refine_prompt(user_prompt)
    print("Refined Prompt:\n", refined)

    image_url = generate_image(refined)
    print("Image URL:\n", image_url)
