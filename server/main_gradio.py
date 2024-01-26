import gradio as gr
from gemini import GeminiAI


def random_response(message, history):
    print(history)
    history_as_gemini = []
    for section in history:
        history_as_gemini.append({
            'role': 'user',
            'message': section[0]
        })
        history_as_gemini.append({
            'role': 'model',
            'message': section[1]
        })

    history_as_gemini.append({
        'role': 'user',
        'message': message
    })

    ai = GeminiAI()
    res = ai.get_anything_chat(history_as_gemini)
    res = res.replace('•', '  *')
    return res


demo = gr.ChatInterface(random_response)

if __name__ == "__main__":
    demo.launch(
        share=True
    )
