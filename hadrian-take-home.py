# to replicate:
# start virtual environment
# from project directory root: `pip install -r /path/to/requirements.txt``
# from project directory root: `python3 hadrian-take-home.py`

##################################################
# Set up environment #############################

import requests, os
from dotenv import load_dotenv
from robodk import robolink
from robodk.robodk import transl
from robodk.robolink import ITEM_TYPE_OBJECT

load_dotenv() # Initialize Airtable credentials
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
base_id = os.getenv("BASE_ID")
table_name = os.getenv("TABLE_NAME")

RDK = robolink.Robolink() # Connect to RoboDK simulation instance

##################################################
# Connect to the Airtable database ###############

class AirtableAuth(requests.auth.AuthBase):
    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, request):
        auth_token = {"Authorization": "Bearer {}".format(self.api_key)}
        request.headers.update(auth_token)
        return request
        
def get_place_positions():
    auth = AirtableAuth(api_key)
    response = requests.get(f'https://api.airtable.com/v0/{base_id}/{table_name}', auth=auth)
    print('status code from airtable:', response.status_code)
    airtable_response = response.json()
    
    global airtable_records # Share variable with frame_place without using class
    airtable_records = airtable_response['records']
    print('length of airtable records:', len(airtable_records))

    for record in airtable_records: # Convert Z/Y/Z coordinates to a pose matrix
        record['translatedFields'] = transl(record['fields']['x']*100, record['fields']['y']*100, record['fields']['z']*100) # To do: use Scale method instead

##################################################
# Control simulated robot ########################

def move_robot():
    robot = RDK.Item('UR10e') # Set up robot
    tool = RDK.Item('Tool1')
    robot.setTool(tool)
    frame_pick = RDK.Item('frame_pick') # Set up frames
    frame_place = RDK.Item('frame_place')
    RDK.Render(True) # Set up view settings
    RDK.setSimulationSpeed(50)
    
    get_place_positions() 
    positionList = list(airtable_records)
    
    all_objects = RDK.ItemList(ITEM_TYPE_OBJECT)
    print('length of all_objects: ', len(all_objects))
    
    for number, obj in enumerate(all_objects): 

        robot.setFrame(frame_pick)
        target = RDK.Item(f'ball{number}', ITEM_TYPE_OBJECT)
        approach = target.Pose()

        try: 
            robot.MoveJ(approach) # To do: use approach vector to avoid collisions
            tool.AttachClosest()
        except:
            print('could not pick ')
    
        placePose = positionList[number]['translatedFields']
        robot.setFrame(frame_place)

        try:
            robot.MoveJ(placePose)
            tool.DetachAll(0)
        except:
            print('could not place')

move_robot()