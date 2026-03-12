from datetime import datetime
from time import time, sleep
import csv
import os
import threading
from missions.first_flight import get_current_position, horizontal_distance, print_timestamped
import missions.constants as c


class TelemetryLogger:
    
    def __init__(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        os.makedirs("logs", exist_ok=True)
        
        self.file_path = os.path.join('logs', f'flight_{timestamp}.csv')
        self.fieldnames = [
            'timestamp', 'x', 'y', 'z', 'altitude',
            'vx', 'vy', 'vz', 'ground_speed', 'vertical_speed',
            'waypoint', 'battery', 'distance_to_target'
        ]
        
        self.telemetry_log = []
        self.mission_start_time = None
        self.current_waypoint = 0
        self.target_position = (0, 0, 0)
        self.logging_active = False
        self.logging_thread = None
        
        print_timestamped(f"[TelemetryLogger] Will save to: {self.file_path}")
    
    def start_logging(self, connection):
        """Start background logging thread."""
        self.mission_start_time = time()
        self.logging_active = True
        
        self.logging_thread = threading.Thread(
            target=self._logging_loop,
            args=(connection,),
            daemon=True
        )
        self.logging_thread.start()
        print_timestamped("[TelemetryLogger] Started")
    
    def stop_logging(self):
        """Stop background logging thread."""
        self.logging_active = False
        if self.logging_thread:
            self.logging_thread.join(timeout=2.0)
        print_timestamped("[TelemetryLogger] Stopped")
    
    def _logging_loop(self, connection):
        """Background thread - captures telemetry every 0.5s."""
        while self.logging_active:
            try:
                elapsed = time() - self.mission_start_time
                
                # Get position
                pos = get_current_position(connection, timeout=0.5)
                if not pos:
                    continue
                
                # Get battery
                sys_msg = connection.recv_match(type=c.MSG_SYS, blocking=False)
                battery = sys_msg.battery_remaining if sys_msg else -1
                
                # Calculate distance to target
                current = {'x': pos['x'], 'y': pos['y']}
                target = {'x': self.target_position[0], 'y': self.target_position[1]}
                distance = horizontal_distance(current, target)
                
                # Create reading
                reading = {
                    'timestamp': elapsed,
                    'x': pos['x'],
                    'y': pos['y'],
                    'z': pos['z'],
                    'altitude': pos['altitude'],
                    'vx': pos['vx'],
                    'vy': pos['vy'],
                    'vz': pos['vz'],
                    'ground_speed': pos['ground_speed'],
                    'vertical_speed': pos['vertical_speed'],
                    'waypoint': self.current_waypoint,
                    'battery': battery,
                    'distance_to_target': distance
                }
                
                self.telemetry_log.append(reading)
                
            except Exception as e:
                print_timestamped(f"[TelemetryLogger] Error: {e}")
            
            sleep(0.5)
    
    def set_waypoint(self, waypoint_num):
        """Update current waypoint number."""
        self.current_waypoint = waypoint_num
    
    def set_target(self, x, y, z):
        """Update target position."""
        self.target_position = (x, y, z)
    
    def save_to_csv(self):
        """Write telemetry log to CSV file."""
        if not self.telemetry_log:
            print_timestamped("[TelemetryLogger] No data to save")
            return
        
        with open(self.file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.telemetry_log)
        
        print_timestamped(f"[TelemetryLogger] Saved {len(self.telemetry_log)} readings to {self.file_path}")