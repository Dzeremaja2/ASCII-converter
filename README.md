# ASCII-converter
## Overview
This repository contains code (python) driven primitive 2D image and video editor, algorithm I developed for basic conversion to ASCII stylized art. It also contains HLSL (.fx) code ready to be imported in ReShade and tested on games for ASCII stylization. This project is directly inspired by Acerola's ASCII shader. 

## Detailed overview and backstory
This is now the detailed story of this project. So let's start at the beggining. I will say it right here: this project couldn't be possible if there was no **Acerola's video on ASCII shader** (https://www.youtube.com/watch?v=gg40RWiaHRY&t=1s). It was inspirational and that video got me interested in computer graphics thru coding. Fast forward couple of months and I am choosing thesis for my high-school graduation paper. Immediately I started thinking about this video and how could I make it myself. I download Cyberpunk 2077, which I wanted to play for a long time and this was the excuse, and started vibe coding the idea into existance guided by Acerola's video. That is the part I am least proud of, and it is the fact that the majority of the code is written by Google's Gemini LLM... but I think it is reasonable to use tool of that kind since I had vary limited expirience in computer graphics to begin with. <br/>
Firstly I started expirementing with 2D images and created something I call **"Tilemap editor"** which I can describe as a code driven image editor based on python. Detailed explanation on how to use are below. For now, I will countinue on the story I started. After I proved the concept I turned to editing the game's visual feedback thru **ReShade** and it's programming language called HLSL by creating simple .fx file. After some trial and error I got something that looks nice.<br/> 
I also wrote entire Thesis paper (since my graduation paper needs to be in physical form) on this topic that goes over in detail on how I achieved this look which will also be placed here. <br/>

**EDIT: current version of thesis paper is not complete but once I am done it will be published fully.**

## HOW TO USE 
Let's firstly start with 2D tilemap engine. In the folder **PythonCode** you will find base for my Tilemap Engine written as "ascii_studioV.2.py" and **algorithm for ASCII conversion** named "ASCII algorithm PY". Before running the pythone script ***YOU WILL NEED TO INSTALL CUSTOMKTINKER LIBRARY FOR TILEMAP ENGINE TO WORK***. <br/>
After you installed all necessery libraries you can run the code and I encourage you to take a look at the thesis paper and get more familiar with the UI. 
1. You load wanted image into the right top window;
2. Paste the ASCII algorithm PY
3. **Load ASCII atlas texture** that is provided in "Textures" folder (choose one named only "ASCII")
   - Now you are supposed to see something in the result window on the right side. If there is nothing to show, press the Force refresh button. You should see black and white image with outlines. These are here to help you dial the looks of edge engine by sliding the Sigma_1 and Sigma_2 sliders (you can also tweak the settings with threshold and gain sliders. Once you are happy, check the "use Atlas" box and start creating!)
4. Click save results and determine the path.
If you want to edit the video files, select "load video" in the editor and proceed with same methode I gone over just now.

## ReShade and HLSL
Applying our effect to games is a little bit more problematic but using ReShade makes things a lot simpler. 
1. Firstly install ReShade from their website (https://reshade.me/)
2. Install ReShade on the game you want to play.
3. This step can vary but I did it this way.
   - Installation:
      - Directly in the folder where the game files are sitting create another folder called "reshade-shaders". Inside create two new folders called "Shaders" and "Textures". 
      - In first folder (Shaders) copy files "ASCII.fx" and "ReShade.fsh" that are in the "HLSL code for ReShade" folder.
      - In the second one (Textures) copy "ascii.png" I provided in the "Textures" folder here.
   - In Game
      - Now in the game press the Home (or Pos1) key to open the ReShade overlay.
      - If you don't see your shader in the list, click the Reload button at the bottom of the overlay.
      - Check the box next to the shader name to enable it.
   - Checking the Depth Buffers
      - Go to the Add-ons tab (in newer ReShade versions) or the API tab (DX9DX11Vulkan). Look at the list of Depth Buffers.
      - How to identify the right one. Resolution It must match your game resolution (e.g., 1920x1080). Draw Calls  Vertices Look for the buffer with the highest number of Draw Calls or Vertices. This usually indicates the main scene geometry.
      - Check the box next to that buffer to force ReShade to use it.

**Enjoy and create awesome art.**
 
