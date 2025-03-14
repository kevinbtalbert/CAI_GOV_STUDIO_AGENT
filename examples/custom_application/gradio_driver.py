import gradio as gr
import time
import os 

from studio.sdk.workflows import run_workflow, get_workflow_status


# This is the name of the workflow in Agent Studio. This workflow
# is a deployed workflow, and the agent studio SDK methods will
# perform proper discovery on the workflow's endpoints.
WORKFLOW_NAME = "Chatbot"


def respond(user_message, chat_history, context):

    chat_history.append([user_message, None])

    context.append({"role": "User", "content": user_message})

    run_id = run_workflow("Chatbot", inputs={
        "user_input": user_message,
        "context": context,
    })

    workflow_status = {}
    while not workflow_status.get("complete"):
        time.sleep(1)
        workflow_status = get_workflow_status(run_id)

    agent_reply = workflow_status["output"]

    chat_history[-1][1] = agent_reply
    context.append({"role": "Assistant", "content": agent_reply})

    return chat_history, context


with gr.Blocks() as demo:
    gr.Markdown("## Simple Agent Studio Chatbot")

    chatbot = gr.Chatbot(
        label="Conversation",
        elem_id="chatbot"
    )

    txt = gr.Textbox(
        label="Your Message",
        placeholder="Type a message and press Enter...",
    )

    context_state = gr.State([])

    txt.submit(
        fn=respond,
        inputs=[txt, chatbot, context_state],
        outputs=[chatbot, context_state]
    )


demo.queue().launch(server_port=int(os.getenv("CDSW_APP_PORT")))
