"""
Simple test for TelemetryLogger.
Connects to drone and logs telemetry for 10 seconds.
"""

from telemetry_logging import TelemetryLogger  # ← Changed
from first_flight import connect_to_vehicle    # ← Changed
import constants as c                           # ← Changed
from time import sleep


def main():
    print("="*60)
    print("Testing TelemetryLogger")
    print("="*60)
    
    # 1. Create logger
    logger = TelemetryLogger()
    
    # 2. Connect to drone
    print("\nConnecting to drone...")
    connection = connect_to_vehicle(c.CONNECTION_STRING)
    
    # 3. Start logging
    print("\nStarting telemetry logging for 10 seconds...")
    logger.start_logging(connection)
    
    # 4. Simulate waypoint changes
    for i in range(5):
        logger.set_waypoint(i)
        logger.set_target(i * 5, i * 5, -10)
        print(f"  Waypoint {i}: Target set to ({i*5}, {i*5}, -10)")
        sleep(2)  # Log for 2 seconds at each "waypoint"
    
    # 5. Stop logging
    print("\nStopping logger...")
    logger.stop_logging()
    
    # 6. Save to CSV
    print("\nSaving to CSV...")
    logger.save_to_csv()
    
    # 7. Report
    print("\n" + "="*60)
    print("Test complete!")
    print(f"Total readings captured: {len(logger.telemetry_log)}")
    print(f"CSV file saved to: {logger.file_path}")
    print("="*60)
    
    # 8. Show first few readings
    if logger.telemetry_log:
        print("\nFirst 3 readings:")
        for i, reading in enumerate(logger.telemetry_log[:3]):
            print(f"  {i}: timestamp={reading['timestamp']:.2f}s, "
                  f"x={reading['x']:.2f}, y={reading['y']:.2f}, "
                  f"waypoint={reading['waypoint']}")
    
    connection.close()


if __name__ == "__main__":
    main()