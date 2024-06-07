import gradio as gr
from route import insert_data, fetch_data

js_func = """
function refresh() {
    const container = document.getElementById('container');  // Assuming there's a container element
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }
}
"""

def check_inputs(text, phoneme):
    """
    Check if both text and phoneme inputs are not empty.

    Args:
        text (str): The input text.
        phoneme (str): The input phoneme.

    Returns:
        bool: True if both text and phoneme inputs are not empty, False otherwise.
    """
    return bool(text.strip()) and bool(phoneme.strip())

def update_button_state(text, phoneme):
    """
    Update the state of the insert button based on the inputs.

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
    Update the data frame based on the search query.

    Args:
        search_query (str): The search query input.

    Returns:
        gr.Interface: A Gradio Interface object with the data frame updated.
    """
    df, error_message = fetch_data(search_query)
    if error_message:
        return gr.HTML(value=error_message)
    return gr.DataFrame(value=df)


with gr.Blocks(theme=gr.themes.Monochrome(radius_size="md"), js=js_func, title="PhonoFix") as demo:
    gr.Markdown('## <p style="text-align: center; margin-top: 2em;">PhonoFix</p>')
    tabs = gr.Tabs()
    with tabs:
        with gr.TabItem("Text (add | edit)") as add_text:
            # with gr.Column(elem_id="container"):
            text_input = gr.Textbox(label="Text", value=None, placeholder="ใส่อินพุต")
            phoneme_input = gr.Textbox(label="Phoneme", value=None, placeholder="ใส่|อิน|พุด")
            insert_button = gr.Button("Insert Data", interactive=False)
            insert_output = gr.HTML(label="status")
            text_input.change(fn=update_button_state, inputs=[text_input, phoneme_input], outputs=insert_button)
            phoneme_input.change(fn=update_button_state, inputs=[text_input, phoneme_input], outputs=insert_button)
            insert_button.click(fn=insert_data, inputs=[text_input, phoneme_input], outputs=insert_output)

        with gr.TabItem("Text List") as text_list:
            search_input = gr.Textbox(label="Search", placeholder="Enter search query", value=None)
            data_frame = gr.DataFrame()
            # Use the search_input's value to fetch data
            search_input.change(fn=update_data_frame, inputs=search_input, outputs=data_frame)
    
    text_list.select(update_data_frame, search_input, data_frame)

demo.launch()
