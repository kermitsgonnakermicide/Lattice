# Lattice
![keyboard](Assets/keyboard_front.png)
> a 60% mechanical keyboard with magnetically attached modules

# what even is Lattice?
Lattice is a modular 60% mechanical keyboard, with the main keyboard featuring:
- cherry mx black switches
- a raspberry pi pico 2
- an EC11 encoder
- 6 expansion ports(two 2.54 inch female headers and 4 4 pin magnetic pogo connectors)
- absolutely NO RGB(in the keyboard itself skdsks)

Lattice also comes with three modules(as of now), which are:
- a 16 key macropad with an OLED
![macropad](Assets/just_macropad_render.png)
- a 3 slider, two encoder module i'm calling the sliderpad
![sliderpad](Assets/just_sliderpad.png)
- a 32x4 RGB LED(specifically the WS2812B-2020) matrix that slides in the empty top bit of the keyboard(connected by 2.54 mm pins because I didnt trust the current limits of the magnetic connectors)
![matrix](Assets/matrix_3D.png)

Each module features a xiao rp2040 to run everything else on it because its so smol and cute :3</br>

The macropad and the sliderpad connect with magnetic pogo pins and use I2C to communicate with the main board, while the matrix does the same thing but just connects with normal pin headers and sockets. </br>

# why did you even build this?(and many other whys)
I lowkenuinely just needed a keyboard pretty desperately - i've been using my crusty musty dusty redragon k552 for almost 5 years now and I need to switch it out :cryin:
additionally, I wanted a keyboard that I could actually take places, so things like a detachable cable(made possible by the pico 2) and a small form factor without compromising on key count was pretty important to me(hence the modules)

**Q: why xiao rp2040s on each board????**<br>
A: I can get them for hella cheap, they're really well documented, i've worked with them before and they're really small(works well for my purposes)

**Q: why not integrate a microcontroller on your board**<br>
A: while I would love to not use a module and put the straight microcontroller on this board, money is a problem here and I want to try and minimize costs where I can - a PCBA costs a crazy amount of money and with customs and shipping, this project aint covering it :cryin:

**Q: why not RGB?? are you not gamer???**<br>
A: i dont like RGB on the keeb - its annoying to work with, solder and must I remind you - **expensive** - to satiate the thirst for RGB i'm instead just slapping a giant matrix on the top empty bit of the board(hopefully playing snek on it soon)

# images
<details>
<summary> Schematics </summary>

![keyboard schematic](Assets/keyboard_schematic.png)
> main keyboard

![macropad_schematic](Assets/macropad_schematic.png)
>macropad 

![sliderpad schematic](Assets/matrix_schematic.png)
> sliderpad

![matrix_schematic](Assets/matrix_schematic.png)
> matrix

</details>

<details>

<summary> PCBs </summary>

![keyboard pcb](Assets/keyboard_PCB.png)
> main keyboard

![macropad pcb](Assets/macropad_PCB.png)
> macropad

![sliderpad PCB](Assets/sliderpad_PCB.png)
> sliderpad

![matrix_pcb](Assets/matrix_PCB.png)
> LED matrix

</details>

<details>

<summary> 3D models </summary>

![keyboard pcb](Assets/keyboard_3D.png)
> main keyboard

![macropad pcb](Assets/macropad_3D.png)
> macropad

![sliderpad PCB](Assets/sliderpad_3D.png)
> sliderpad

![matrix_pcb](Assets/matrix_3D.png)
> LED matrix

</details>

<details>

<summary> CAD renders </summary>

![keyboard pcb](Assets/justkeeb.png)
> main keyboard

![macropad pcb](Assets/just_macropad_render.png)
> macropad

![sliderpad PCB](Assets/just_sliderpad.png)
> sliderpad

![whole thing together](Assets/keyboard_front.png)
![another angle](Assets/keyboard_side.png)
> the assembled keyboard!

</details>

# Zine

![zine](Zine.png)