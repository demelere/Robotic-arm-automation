##################################################
# Set up environment #############################

import os
import requests
from dotenv import load_dotenv
from robodk import robolink
from robodk.robodk import transl
from robodk.robolink import ITEM_TYPE_OBJECT

load_dotenv()  # Initialize Airtable credentials
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
base_id = os.getenv("BASE_ID")
table_name = os.getenv("TABLE_NAME")

##################################################
# Connect to DB ##################################

class AuthenticateDB(requests.auth.AuthBase):
    """
    Authenticates with Airtable DB
    """

    def __init__(self, api_key):
        self.api_key = api_key

    def __call__(self, request):
        auth_token = {"Authorization": f"Bearer {self.api_key}"}
        request.headers.update(auth_token)
        return request


def get_place_positions():
    """
    Retrieves place positions from Airtable DB records
    """

    auth = AuthenticateDB(api_key)
    db_url = f'https://api.airtable.com/v0/{base_id}/{table_name}'

    try:
        response = requests.get(url=db_url, auth=auth, timeout=5)
        if response.status_code == 200:
            print('connected to airtable: ', response.status_code)

    except (requests.ConnectTimeout, requests.HTTPError, requests.ReadTimeout, requests.Timeout, requests.ConnectionError) as error:
        print('error connecting to airtable: ', error)

    airtable_response = response.json()
    airtable_records = airtable_response['records']
    print('number of airtable records:', len(airtable_records))

    for record in airtable_records:  # Convert x/y/z coordinates to a pose matrix
        record['translatedFields'] = transl(
            (record['fields']['x']*90)-300, (record['fields']['y']*90)-250, record['fields']['z']-400)

    return airtable_records

##################################################
# Pick and place objects #########################

def control_robot_arm():
    """
    Controls simulated robot arm
    """

    RDK = robolink.Robolink()  # Connect to RoboDK simulation instance

    robot = RDK.Item('UR10e')  # Set up robot and tool
    tool = RDK.Item('Tool1')
    robot.setTool(tool)

    frame_pick = RDK.Item('frame_pick')  # Set up frames
    frame_place = RDK.Item('frame_place')

    RDK.Render(True)  # Set up view settings
    RDK.setSimulationSpeed(25)

    positions = get_place_positions()
    positions_list = list(positions)

    all_objects = RDK.ItemList(ITEM_TYPE_OBJECT)
    print('number of all_objects: ', len(all_objects))

    for number, _ in enumerate(positions_list):

        robot.setFrame(frame_pick)
        target = RDK.Item(f'ball{number}', ITEM_TYPE_OBJECT)
        # Move pose to location because unable to pass target as an argument to MoveJ()
        approach = target.Pose()

        try:
            # To do: use approach vector to avoid collisions
            robot.MoveJ(approach)
            tool.AttachClosest()
        except:
            print('could not pick from: ', approach)
            raise

        place_pose = positions_list[number]['translatedFields']
        robot.setFrame(frame_place)

        try:
            robot.MoveJ(place_pose)
            tool.DetachAll(0)
        except:
            print('could not place at: ', place_pose)
            raise

    robot.MoveJ([0, 0, 0, 0, 0, 0])

control_robot_arm()
