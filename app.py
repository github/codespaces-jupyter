import gradio as gr
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from agent import app as agent_app
from langchain_core.messages import HumanMessage
import os

API_URL = os.getenv("ENGINE_API_URL", "http://localhost:8080/simulate")

def get_plot(beta, lambda_cosmo):
    payload = {
        "beta": beta,
        "kappa": 0.1,
        "lambda_cosmo": lambda_cosmo,
        "num_states": 4,
        "lyapunov_threshold": 4.20,
        "lambda_meta": 0.05
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            history = data["history"]
            
            norms = [h["norm"] for h in history]
            lyapunovs = [h["lyapunov"] for h in history]
            
            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax2 = ax1.twinx()
            
            ax1.plot(norms, color='cyan', label='Hilbert Norm')
            ax2.plot(lyapunovs, color='magenta', label='Lyapunov')
            
            ax1.set_xlabel('Recent Time Steps')
            ax1.set_ylabel('Norm', color='cyan')
            ax2.set_ylabel('Lyapunov', color='magenta')
            plt.title(f"Phase-Space Stability (Beta={beta}, Lambda={lambda_cosmo})")
            plt.grid(alpha=0.2)
            
            return fig
        else:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, f"API Error: {response.status_code}", ha='center')
            return fig
    except Exception as e:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"Connection Error: {str(e)}", ha='center')
        return fig

def chat_response(message, history, beta, lambda_cosmo):
    full_message = f"{message} (Current Engine Context: beta={beta}, lambda={lambda_cosmo})"
    
    inputs = {"messages": [HumanMessage(content=full_message)]}
    response = ""
    
    try:
        # LangGraph can have multiple steps (agent -> tools -> agent)
        for output in agent_app.stream(inputs):
            for node, value in output.items():
                if node == "agent":
                    # Capture the latest AI message from the agent node
                    last_msg = value["messages"][-1]
                    if isinstance(last_msg, AIMessage) and last_msg.content:
                        response = last_msg.content
    except Exception as e:
        response = f"Error in agent execution: {str(e)}"
    
    return response if response else "The physicist is calculating the tensors... please wait."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌌 Quantum-Relativistic Financial Agent")
    gr.Markdown("Integration of Einstein Field Equations and Hilbert Space dynamics for BTC-USD forecasting.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Engine Parameters")
            beta_slider = gr.Slider(0.001, 0.1, value=0.01, label="Relativistic Self-Interaction (β)")
            lambda_slider = gr.Slider(0.01, 0.5, value=0.1, label="Cosmological Constant (Λ)")
            
            plot_output = gr.Plot(label="Phase-Space Analysis")
            update_btn = gr.Button("Re-Simulate Engine", variant="primary")
            
            update_btn.click(get_plot, inputs=[beta_slider, lambda_slider], outputs=plot_output)

        with gr.Column(scale=2):
            gr.Markdown("### 🤖 Physicist Chatbot")
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(placeholder="Ask the Physicist about market stability or request a prediction...")
            
            def user(user_message, history):
                return "", history + [[user_message, None]]

            def bot(history, beta, lambda_cosmo):
                user_message = history[-1][0]
                bot_message = chat_response(user_message, history, beta, lambda_cosmo)
                history[-1][1] = bot_message
                return history

            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, [chatbot, beta_slider, lambda_slider], chatbot
            )

    demo.load(get_plot, inputs=[beta_slider, lambda_slider], outputs=plot_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
