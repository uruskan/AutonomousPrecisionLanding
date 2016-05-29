from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
from pymavlink import mavutil
import argparse  

parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

#Start SITL if no connection string specified
if not args.connect:
    print "Starting copter simulator (SITL)"
    from dronekit_sitl import SITL
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353']
    sitl.launch(sitl_args, await_ready=True, restart=True)
    connection_string = 'tcp:127.0.0.1:5760'


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True)

def download_mission():
    """
    Download the current mission from the vehicle.
    """
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() # wait until download is complete.


from flightAssist import get_location_metres
def adds_square_mission(aLocation, aSize):
    
    #Adds a takeoff command and four waypoint commands to the current mission. 
    #The waypoints are positioned to form a square of side length 2*aSize around the specified LocationGlobal (aLocation).

    #The function assumes vehicle.commands matches the vehicle mission state 
    #(you must have called download at least once in the session and after clearing the mission)
    	

    cmds = vehicle.commands

    print " Clear any existing commands"
    cmds.clear() 
    
    print " Define/add new commands."
    # Add new commands. The meaning/order of the parameters is documented in the Command class. 
     
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))

    #Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
    point1 = get_location_metres(vehicle, aLocation, aSize, -aSize)
    point2 = get_location_metres(vehicle, aLocation, aSize, aSize)
    point3 = get_location_metres(vehicle, aLocation, -aSize, aSize)
    point4 = get_location_metres(vehicle, aLocation, -aSize, -aSize)
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point1.lat, point1.lon, 11))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point2.lat, point2.lon, 12))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point3.lat, point3.lon, 13))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point4.lat, point4.lon, 14))
    #add dummy waypoint "5" at point 4 (lets us know when have reached destination)
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point4.lat, point4.lon, 14))    

    print " Upload new commands to vehicle"
    cmds.upload()

from flightAssist import get_distance_metres
def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle, vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint



#initial location of target 
initial_location = vehicle.location.global_frame

#adding mission to move in a square path
adds_square_mission(initial_location, 2.5)

from flightAssist import arm_and_takeoff
arm_and_takeoff(vehicle, 5)

vehicle.commands.next = 0
vehicle.mode = VehicleMode("AUTO")

start_time = time.time()

while True:
	nextWayPoint = vehicle.commands.next
	print "Distance to next waypoint: ", distance_to_current_waypoint()
	
	if nextWayPoint == 3:
		vehicle.commands.next = 5
	elif nextWayPoint == 5:
		vehicle.commands.next = 0

	if time.time()-start_time > 1000:
		break

	time.sleep(2)

print "Mission completed" 
vehicle.mode = VehicleMode("RTL")

while True:
	h = vehicle.location.global_frame.alt
	print "Landing...."
	print "Altitude: ", h
	
	if h<0.1:
		print "Landed"
		break

print "Closing vehicle"
vehicle.close()
sitl.close()

	

			
	
	

	
