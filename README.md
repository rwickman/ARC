# ARC
#### *Autonomous R/C Car*
## What is it?
It is an autonomous vehicle that utilizes behavior cloning and object recognition to navigate around a track! It is also able to perform customized actions based upon the object that it detects.
## How we built it
We used a handful of libraries ranging from Tensorflow to RPIO.gpio to handle training our neural network and gauging the distance between the car and objects around it. We utilized the TensorFlow library to detect objects around the car and act accordingly.
## How to make updates
Currently to reflect the changes in this repository to the donkeycar library, you have to copy/replace the files over to the /home/pi/env/lib/python3.5/site-packages/donkeycar directory(this will be fixed in the future).
## Resources
To handle the behavior cloning and PID controller, we used a library called Donkeycar. Donkeycar is an open source hardware and software platform to build a small scale self driving cars. A link to the Donkeycar repository can be found [here](https://github.com/autorope/donkeycar).
