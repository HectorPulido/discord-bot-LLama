# LLAMA - Discord Chatbot
This repo is an implementartion of [LLAMA/ALPACA](https://github.com/tloen/alpaca-lora/). It's a chatbot made with Python that simulates natural conversation with users. The chatbot is designed to be used in the **Discord** platform, providing an interactive experience for the users. LLAMA can run in user hardware or in colab.

![image demo of the game](/img/example.png)<br/>

# Installation
The following instructions will help you install LLAMA on your machine or in colab.

## In your computer
To use LLAMA, you need to have Python 3 installed on your machine. You can download Python 3 from the official website at https://www.python.org/downloads/

After installing Python 3, you can follow the instructions:

1. Clone the repository to your local machine.
2. Install the required Python packages by running ```pip install -r requirements.txt``` in your terminal.
3. Create a new Discord bot account and invite it to your server.
4. Create a file with the name ```.env``` and fill it with your token, use the ```.env.example``` file as a template.
5. Run the main.py file in your terminal, using ```python main.py```.

## For ARM
[Follow this instructions](https://github.com/nomic-ai/gpt4all/issues/553#issuecomment-1584167667)

## In colab
To use LLAMA in colab, 
1. you need to have a google account. 
2. Open [colaboratory](https://colab.research.google.com/) in your browser. 
3. Import the ```to_upload_to_colab.ipynb``` file to your colab.
4. Run the cells in order.

# License
This project is licensed under the MIT License. See the LICENSE file for details.
