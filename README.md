### To replicate:
1. Start virtual environment
2. From project directory root run `pip install -r /path/to/requirements.txt`
3. Create a `.env` file based off of `.env.template` and add Airtable config variables
4. Download the `.rdk` station file and open it in RoboDK
5. From project directory root run `python3 pick_and_place_balls.py`

### Updates and notes:
#### 12/8/22
* This simulation environment would be a good candidate for deep reinforcement learning.  

#### 11/7/22
Refactored a couple small details and updated the scaling to show the full pattern while accounting for ball diameter. To do:
* Refactor functions into a class that could be called from another script
* Load station file from script

#### 10/30/22
At the moment I'm ignoring potential real-world constraints/collisions with the x-axis surface.  To do:
* My next step would be to refactor this by finding a safe intermediate pose/approach from above frame_pick.  This may involve defining another reference frame called ‘table’.
* Another approach would be to constrain the joints for the space we’re not using.  This would help with safety, and would speed up collision checking by reducing the amount of detail and triangles in the 3D models.
* Another approach would be to add larger offsets
* If it's possible, I would also look into moving the robot base