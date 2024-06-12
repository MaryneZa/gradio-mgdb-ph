import gradio as gr
import pandas as pd
from route import insert_data, fetch_data

js_func = """
function refresh() {
    const container = document.getElementById('container');  // Assuming there's a container element
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

def check_inputs(text, phoneme):
    """
    Checks if both the text and phoneme inputs are not empty.

    Args:
        text (str): The input text.
        phoneme (str): The input phoneme.

    Returns:
        bool: True if both text and phoneme inputs are not empty, False otherwise.
    """
    return bool(text.strip()) and bool(phoneme.strip())

def update_button_state(text, phoneme):
    """
    Updates the state of the insert button based on the inputs.

    Args:
        text (str): The input text.
        phoneme (str): The input phoneme.

    Returns:
        gr.Interface: A Gradio Interface object with the interactive state updated.
    """
    if check_inputs(text, phoneme):
        return gr.update(interactive=True)
    else:
        return gr.update(interactive=False)

def update_data_frame(search_query):
    """
    Updates the data frame based on the search query.

    Args:
        search_query (str): The search query input.

    Returns:
        gr.Interface: A Gradio Interface object with the data frame updated.
    """
    df, error_message = fetch_data(search_query)
    if error_message:
        return gr.HTML(value=error_message)
    return gr.DataFrame(value=df)

def update_examples(search_query):
    """
    Updates the examples based on the search query.

    Args:
        search_query (str): The search query input.

    Returns:
        list: A list of examples fetched from the data frame.
    """
    try:
        df, error_message = fetch_data(search_query)
        if error_message:
            print(f"Error fetching data: {error_message}")
            return []
        if df.empty:
            print("DataFrame is empty.")
            return []
        if 'text' in df.columns and 'phoneme' in df.columns:
            examples = []
            for idx in df.index:
                try:
                    text = df.at[idx, 'text']
                    phoneme = df.at[idx, 'phoneme']
                    examples.append([text, phoneme])
                except KeyError as e:
                    print(f"KeyError accessing index {idx}: {e}")
            # print(f"Fetched {len(examples)} examples.")
            return examples
        else:
            print("Columns 'text' or 'phoneme' not found in DataFrame.")
            return []
    except KeyError as e:
        print(f"KeyError in update_examples: {e}")
        return []
    except Exception as e:
        print(f"Exception in update_examples: {e}")
        return []

with gr.Blocks(theme=gr.themes.Monochrome(radius_size="md"), js=js_func, title="PhonoFix") as demo:
    gr.Markdown('## <p style="text-align: center; margin-top: 2em;">PhonoFix</p>')
    tabs = gr.Tabs()
    with tabs:
        with gr.TabItem("Text (add | edit)") as add_text:
            text_input = gr.Textbox(label="Text", value=None, placeholder="ใส่อินพุต")
            phoneme_input = gr.Textbox(label="Phoneme", value=None, placeholder="ใส่|อิน|พุด")
            insert_button = gr.Button("Insert Data", interactive=False)
            insert_output = gr.HTML(label="status")
            text_input.change(fn=update_button_state, inputs=[text_input, phoneme_input], outputs=insert_button)
            phoneme_input.change(fn=update_button_state, inputs=[text_input, phoneme_input], outputs=insert_button)
            insert_button.click(fn=insert_data, inputs=[text_input, phoneme_input], outputs=insert_output)

        with gr.TabItem("Text List") as text_list:
            search_input = gr.Textbox(label="Search", placeholder="Enter search query", value=None)
            
            data, message = fetch_data(None)
            if not message:
                initial_examples = [[data.at[idx, 'text'], data.at[idx, 'phoneme']] for idx in data.index]
                saved_examples = gr.Dataset(components=["text", "text"], samples=initial_examples, label="", samples_per_page=5, headers=["Text", "Phoneme"])

            search_input.change(fn=update_examples, inputs=search_input, outputs=saved_examples)

    text_list.select(fn=update_examples, inputs=search_input, outputs=saved_examples)
    
demo.launch()
