from pymavlink import mavutil
from time import sleep

GPS_RAW_INT = "GPS_RAW_INT"
SYS_STATUS = "SYS_STATUS"
VFR_HUD = "VFR_HUD"
GPS_GRAD = 1e7
THOUSD = 1000
        

def main():
    connection = mavutil.mavlink_connection("udp:127.0.0.1:14550")
    connection.wait_heartbeat()
    print("Heartbeat from system (system %u component %u flight mode %s)" % (connection.target_system, connection.target_component, connection.flightmode))
    for i in range(1,2):
        # gps messages
        gps_messages = connection.recv_match(type=GPS_RAW_INT, blocking=True)
        if not gps_messages:
            return

        print(f'{i} -> GPS Position: Lat={float(gps_messages.lat)/GPS_GRAD}, Lon = {float(gps_messages.lon)/GPS_GRAD}, Alt = {float(gps_messages.alt)/THOUSD}meter')
        
        # sys status messages
        sys_status_msg = connection.recv_match(type = SYS_STATUS, blocking=True)
        if not sys_status_msg:
            return
        print(f'{i} -> SYS Battery:{float(sys_status_msg.voltage_battery) / THOUSD} V')
        
        # vfr_hud messages
        vfr_hud_msg = connection.recv_match(type = VFR_HUD, blocking=True)
        if not vfr_hud_msg:
            return
        print(f'{i} -> VFR_HUD Altitude:{vfr_hud_msg.alt} m')
        print(f'{i} -> VFR_HUD GroundSpeed:{vfr_hud_msg.groundspeed} m/s')
        
        # flight mode messages
        print(f'{i} -> Flight Mode :{connection.flightmode}')
        print("")
               
    sleep(3)
    connection.close()
    print(f'Connection is closed {connection.check_condition}')



if __name__=="__main__":
    main()
        