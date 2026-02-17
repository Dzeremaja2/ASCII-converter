# ASCII-converter
## Overview
This repository contains code (python) driven primitive 2D image and video editor, algorithm I developed for basic conversion to ASCII stylized art. It also contains HLSL (.fx) code ready to be imported in ReShade and tested on games for ASCII stylization. This project is directly inspired by Acerola's ASCII shader. 

## Detailed overview and backstory
This is now the detailed story of this project. So let's start at the beggining. I will say it right here: this project couldn't be possible if there was no **Acerola's video on ASCII shader** (https://www.youtube.com/watch?v=gg40RWiaHRY&t=1s). It was inspirational and that video got me interested in computer graphics thru coding. Fast forward couple of months and I am choosing thesis for my high-school graduation paper. Immediately I started thinking about this video and how could I make it myself. I download Cyberpunk 2077, which I wanted to play for a long time and this was the excuse, and started vibe coding the idea into existance guided by Acerola's video. That is the part I am least proud of, and it is the fact that the majority of the code is written by Google's Gemini LLM... but I think it is reasonable to use tool of that kind since I had vary limited expirience in computer graphics to begin with. <br/>
Firstly I started expirementing with 2D images and created something I call **"Tilemap editor"** which I can describe as a code driven image editor based on python. Detailed explanation on how to use are below. For now, I will countinue on the story I started. After I proved the concept I turned to editing the game's visual feedback thru **ReShade** and it's programming language called HLSL by creating simple .fx file. After some trial and error I got something that looks nice.<br/> 
I also wrote entire Thesis paper (since my graduation paper needs to be in physical form) on this topic that goes over in detail on how I achieved this look which will also be placed here. <br/>

**EDIT: current version of thesis paper is not complete but once I am done it will be published fully.**

## HOW TO USE 
Let's firstly start with 2D tilemap engine. In the folder (docs/PythonCode) you will find
