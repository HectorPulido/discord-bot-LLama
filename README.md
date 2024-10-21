# LLAMA - Discord Chatbot
This repo is an implementartion of [LLAMA/ALPACA](https://github.com/tloen/alpaca-lora/). It's a chatbot made with Python that simulates natural conversation with users. The chatbot is designed to be used in the **Discord** platform, providing an interactive experience for the users.

![image demo of the game](/img/example.png)<br/>

# Installation
The following instructions will help you install LLAMA on your machine through the docker

## Prerequisites
- Docker
- Docker Compose
- Discord Token


## Create the bot account and get the token
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
1. Clone the repository
```bash
git clone https://github.com/HectorPulido/discord-bot-LLama.git
```

2. Create a `.env` file in the root directory of the project with the following content:
```bash
TOKEN_DISCORD='<FILL THIS WITH YOUR DISCORD TOKEN>'
CHAT_CHANNELS='<YOUR SERVER>:*' # <- This can be a channel or all the server
EMOJI_ONLY_CHANNELS='406975052286787585:944410045871947797' # This is a feature to only allow emojis in some channels

MEMORY_SIZE=4 # This is the memory size of the chatbot
TRANSLATOR=FALSE # This is a feature to translate the messages to english (if your server is in spanish)

MODEL_NAME='gemma:7b' # This is the model name of the chatbot
OLLAMA_URL='ollama' # This is the url of the chatbot, set it to 'ollama' if you are using the docker-compose file
```

3. Build the docker image
```bash
docker-compose build
```

4. Run the docker container
```bash
docker-compose up
```

5. Invite the bot to your server using the URL generated in the previous steps

6. Enjoy the bot! :tada:

### If you need to run the bot on a Orange Pi 5 or some ARM device 
You can check the previous version of this bot and follow the instructions in the following link:
https://github.com/HectorPulido/discord-bot-LLama/tree/6c79b3bf2d3956617f6789934320352ae776adc2

### GPU Support - Only tested on Ubuntu and Nvidia
1. Follow the instructions for the use of the container-toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
2. It's worth to check the docker-compose.gpu.yml file and adapt it to your needs
3. Run the docker container with the following command
```bash
docker compose -f docker-compose.gpu.yml up --build --remove-orphans
```
4. Suffer for CUDA out of memory errors :sweat_smile:

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

