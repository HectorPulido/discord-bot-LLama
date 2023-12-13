# LLAMA - Discord Chatbot
This repo is an implementartion of LLAMA 2. It's a chatbot made with Python that simulates natural conversation with users. The chatbot is designed to be used in the **Discord** platform, providing an interactive experience for the users. LLAMA can run in user hardware or in colab.

![image demo of the game](/img/example.png)<br/>

## Create the bot account
1. Make sure you’re logged on to the [Discord website](https://discord.com/).
2. Navigate to the [Applications](https://discord.com/developers/applications).
3. Click on the “New Application” button.
4. Give the application a name and click “Create”.
5. Navigate to the “Bot” tab to configure it.
6. Make sure that Public Bot is ticked if you want others to invite your bot.
7. Copy the token using the “Copy” button. **do not share this token.**
8. Go to the “OAuth2 > URL Generator” tab.
9. Tick the “bot” checkbox under “scopes”.
10. Tick the permissions required for your bot to function under “Bot Permissions”.
11. Now the resulting URL can be used to add your bot to a server. Copy and paste the URL into your browser, choose a server to invite the bot to, and click “Authorize”

## Installation
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

## In colab
To use LLAMA in colab, 
1. you need to have a google account. 
2. Open [colaboratory](https://colab.research.google.com/) in your browser. 
3. Import the ```to_upload_to_colab.ipynb``` file to your colab.
4. Run the cells in order.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
<hr>

<div align="center">
<h3 align="center">Let's connect 😋</h3>
</div>
<p align="center">
<a href="https://www.linkedin.com/in/hector-pulido-17547369/" target="blank">
<img align="center" width="30px" alt="Hector's LinkedIn" src="https://www.vectorlogo.zone/logos/linkedin/linkedin-icon.svg"/></a> &nbsp; &nbsp;
<a href="https://twitter.com/Hector_Pulido_" target="blank">
<img align="center" width="30px" alt="Hector's Twitter" src="https://www.vectorlogo.zone/logos/twitter/twitter-official.svg"/></a> &nbsp; &nbsp;
<a href="https://www.twitch.tv/hector_pulido_" target="blank">
<img align="center" width="30px" alt="Hector's Twitch" src="https://www.vectorlogo.zone/logos/twitch/twitch-icon.svg"/></a> &nbsp; &nbsp;
<a href="https://www.youtube.com/channel/UCS_iMeH0P0nsIDPvBaJckOw" target="blank">
<img align="center" width="30px" alt="Hector's Youtube" src="https://www.vectorlogo.zone/logos/youtube/youtube-icon.svg"/></a> &nbsp; &nbsp;
<a href="https://pequesoft.net/" target="blank">
<img align="center" width="30px" alt="Pequesoft website" src="https://github.com/HectorPulido/HectorPulido/blob/master/img/pequesoft-favicon.png?raw=true"/></a> &nbsp; &nbsp;

