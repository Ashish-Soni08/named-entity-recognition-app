import gradio as gr
import spaces
from transformers import pipeline
from typing import List, Dict, Any

def merge_tokens(tokens: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Merges tokens that belong to the same entity into a single token.

    Args:
        tokens (List[Dict[str, any]]): A list of token dictionaries, each containing information about 
                                       the entity, word, start, end, and score.

    Returns:
        List[Dict[str, any]]: A list of merged token dictionaries, where tokens that are part of the 
                              same entity are combined into a single token with updated word, end, 
                              and score values.
    """
    merged_tokens = []
    for token in tokens:
        if merged_tokens and token['entity'].startswith('I-') and merged_tokens[-1]['entity'].endswith(token['entity'][2:]):
            # If the current token continues the entity of the last one, merge them
            last_token = merged_tokens[-1]
            last_token['word'] += token['word'].replace('##', '')
            last_token['end'] = token['end']
            last_token['score'] = (last_token['score'] + token['score']) / 2
        else:
            # Otherwise, add the token to the list
            merged_tokens.append(token)

    return merged_tokens

# Initialize Model
get_completion = pipeline("ner", model="dslim/bert-base-NER", device=0)

@spaces.GPU(duration=120)
def ner(input: str) -> Dict[str, Any]:
    """
    Performs Named Entity Recognition (NER) on the given input text and merges tokens that belong 
    to the same entity into a single entity.

    Args:
        input (str): The input text to analyze for named entities.

    Returns:
        Dict[str, Any]: A dictionary containing the original text and a list of identified entities 
                        with merged tokens.
                        - "text": The original input text.
                        - "entities": A list of dictionaries, where each dictionary contains information 
                          about a recognized entity, including the word, entity type, score, and positions.
    """
    output = get_completion(input)
    merged_tokens = merge_tokens(output)
    return {"text": input, "entities": merged_tokens}

####### GRADIO APP #######
title = """<h1 id="title"> Named Entity Recognition </h1>"""

description = """
- The model used for Recognizing entities [BERT-BASE-NER](https://huggingface.co/dslim/bert-base-NER).
"""

css = '''
h1#title {
  text-align: center;
}
'''

theme = gr.themes.Soft()
demo = gr.Blocks(css=css, theme=theme)

with demo:
  gr.Markdown(title)
  gr.Markdown(description)
  interface = gr.Interface(fn=ner,
                    inputs=[gr.Textbox(label="Text to find entities", lines=10)],
                    outputs=[gr.HighlightedText(label="Text with entities")],
                    allow_flagging="never",
                    examples=["My name is Andrew, I'm building DeeplearningAI and I live in California", "My name is Poli, I live in Vienna and work at HuggingFace"])

demo.launch()