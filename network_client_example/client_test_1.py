import dogfight_client as df
import time

SERVER_IP = "192.168.219.101"
SERVER_PORT = 50888


def print_fps():
	global t, t0, t1
	t1 = time.time()
	dt = t1 - t0
	t0 = t1
	if dt > 0:
		print(str(1 / dt))


df.connect(SERVER_IP, SERVER_PORT)


time.sleep(2)

planes = df.get_planes_list()

print(planes)


df.set_client_update_mode(True)

df.fire_missile(planes[0], 0)


while True :
    df.update_scene()