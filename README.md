import gradio as gr

def calculate(num1, num2, operation):
    try:
        num1 = float(num1)
        num2 = float(num2)

        if operation == "Add":
            return num1 + num2
        elif operation == "Subtract":
            return num1 - num2
        elif operation == "Multiply":
            return num1 * num2
        elif operation == "Divide":
            if num2 == 0:
                return "Error: Division by zero"
            return num1 / num2
        else:
            return "Invalid operation"

    except ValueError:
        return "Error: Please enter valid numbers"


with gr.Blocks() as demo:
    gr.Markdown("# 🧮 Simple Calculator")

    with gr.Row():
        num1 = gr.Textbox(label="First Number")
        num2 = gr.Textbox(label="Second Number")

    operation = gr.Dropdown(
        ["Add", "Subtract", "Multiply", "Divide"],
        label="Operation"
    )

    result = gr.Textbox(label="Result")

    btn = gr.Button("Calculate")

    btn.click(
        fn=calculate,
        inputs=[num1, num2, operation],
        outputs=result
    )

if __name__ == "__main__":
    demo.launch()
