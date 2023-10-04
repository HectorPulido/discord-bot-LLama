# LLAMA - Discord Chatbot
This repo is an implementartion of [LLAMA/ALPACA](https://github.com/tloen/alpaca-lora/). It's a chatbot made with Python that simulates natural conversation with users. The chatbot is designed to be used in the **Discord** platform, providing an interactive experience for the users. LLAMA can run in user hardware or in colab.

![image demo of the game](/img/example.png)<br/>

# Installation
The following instructions will help you install LLAMA on your machine or in colab.

## In your computer
To use LLAMA, you need to have Python 3 installed on your machine. You can download Python 3 from the official website at https://www.python.org/downloads/

After installing Python 3, you can follow the instructions:

1. Clone the repository to your local machine.
2. Excecute ```pip install fabric``` if you don't have it already and only first time
3. ```fab start-bot``` to start the discor bot

## Build GPT4ALL For ARM
You have to Build the library GPT4ALL, you can follow this step by step
[Follow this instructions](https://github.com/nomic-ai/gpt4all/blob/main/gpt4all-bindings/python/README.md)

If you get problems with vulkan you will need to follow this steps:

### Prerequisites
* git
* curl
* cmake

### Process
Once you have downloaded the repository you have to enter to the `source` folder and create your virtual env, usually with:
```
python3 -m venv venv
source venv/bin/activate
```

Then download and build the `GPT4ALL` library
```
git clone --recurse-submodules https://github.com/nomic-ai/gpt4all.git
cd gpt4all/gpt4all-backend/
```
Now the important part, you have to downgrade the library changing the commit
```
git checkout fd419caa551bd5e72d7e6b21bc9d9bda6500dc16
cd gpt4all-backend/gpt4all-backend/
git checkout ba4e85a8339b9dd7cdffad31838235f2fe45a8ea
cd ..
```
Then you have to make some changes to the code with your favorite code editor:

1. File: `llama.cpp-mainline/ggml.c`
2. Change this line: `#ifdef __ARM_NEON` is the line 181 aprox.
3. for this: `#if defined(__ARM_FEATURE_SIMD32) || defined(__ARM_NEON)`

Then you can make your build, from the `gpt4all-backend` folder do this

```
mkdir build && cd build
cmake ..
cmake --build . --parallel  # optionally append: --config Release
cd ../../gpt4all-bindings/python
pip3 install -e .
```

Voila, now you have the correct GPT4ALL version for Raspberry Pi, Orange Pi, Android, etc.

[Follow this instructions](https://github.com/nomic-ai/gpt4all/issues/553#issuecomment-1584167667)
If you get problems with vulkan, downgrade your version to the commit `d3ba1295a764d1803746a2340024c1f7379f06a1`

## In colab
To use LLAMA in colab, 
1. you need to have a google account. 
2. Open [colaboratory](https://colab.research.google.com/) in your browser. 
3. Import the ```to_upload_to_colab.ipynb``` file to your colab.
4. Run the cells in order.

# License
This project is licensed under the MIT License. See the LICENSE file for details.
