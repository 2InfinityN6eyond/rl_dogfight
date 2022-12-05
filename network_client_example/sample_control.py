import json
import socket_lib

import dogfight_client as df
import time

SERVER_IP = "172.20.80.1"
SERVER_PORT = 50888

def print_fps():
	global t, t0, t1
	t1 = time.time()
	dt = t1 - t0
	t0 = t1
	if dt > 0:
		print(str(1 / dt))

# Enter the IP and port displayed in top-left corner of DogFight screen
df.connect(SERVER_IP, SERVER_PORT)

time.sleep(2)

planes = df.get_planes_list()
print(str(planes))


# Get the id of the plane you want to control
plane_id = planes[0]


# Reset the plane at its start state
df.reset_machine(plane_id)

# Set plane thrust level (0 to 1)
df.set_plane_thrust(plane_id, 1)

# Set client update mode ON: the scene update must be done by client network, calling "update_scene()"
df.set_client_update_mode(True)

i = 0
while True :
    i += 1
    
    df.update_scene()
    
    if i < 2000 :
        df.set_plane_pitch(plane_id=plane_id, level = -0.4)
    else :
        df.set_plane_pitch(plane_id, 0)
    
    print(
        df.get_plane_state(plane_id)["user_pitch_level"]
    )
