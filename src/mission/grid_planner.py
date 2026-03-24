from math import ceil
from typing import List, Tuple

class GridMission:
    """
    Generates grid pattern waypoints for rectangular area coverage.
    
    Coordinate system: NED (North-East-Down)
    - X axis: North (positive = north)
    - Y axis: East (positive = east)
    - Z axis: Down (negative = altitude up)
    """
    
    def __init__(self, center: Tuple[float, float], 
                 width: float, length: float, altitude: float,
                 spacing: float, overlap: float = 0.3):
        """
        Initialize grid mission over rectangular area.
        
        Args:
            center: (north, east) center point in meters
            width: Area width in meters (East-West dimension)
            length: Area length in meters (North-South dimension)
            altitude: Flight altitude in meters (positive = up from ground)
            spacing: Track spacing in meters
            overlap: Track overlap fraction (0.0 to 1.0)
            
        Example:
            # Cover 20m × 15m roof at 15m altitude
            grid = GridMission(
                center=(0, 0),
                width=20,    # 20m East-West
                length=15,   # 15m North-South
                altitude=15, # 15m above ground
                spacing=5    # 5m between tracks
            )
        """
        self.center = center
        self.width = width          # East-West
        self.length = length        # North-South (was "height")
        self.altitude = altitude    # Up from ground
        self.spacing = spacing
        self.overlap = overlap
        
        self.waypoints = []
    
    def _calculate_tracks(self) -> List[float]:
        """
        Calculate Y (East-West) positions for each parallel track.
    
        Returns:
        List of Y coordinates for each track
        """
        num_tracks=ceil(self.width/self.spacing) + 1
        
        print(f'Number tracks {num_tracks}')
    
        _, cy = self.center
        start_y = cy - self.width / 2
        track_position = [start_y + i * self.spacing for i in range(num_tracks)]
        return track_position
    
    def _create_waypoints(self, track_positions: List[float]) -> List[Tuple[float, float, float]]:
        waypoints = []
        cx, _ = self.center
        z = -self.altitude
    
        for i, y in enumerate(track_positions):
            x_south = cx - self.length / 2
            x_north = cx + self.length / 2
        
            if i % 2 == 0:
                waypoints.append((x_south, y, z))
                waypoints.append((x_north, y, z))
            else:
                waypoints.append((x_north, y, z))
                waypoints.append((x_south, y, z))
    
        return waypoints

    def generate(self) -> List[Tuple[float, float, float]]:
        """
        Generate complete grid mission waypoints.
    
         This is the main entry point for creating a grid mission.
    
        Returns:
            List of (x, y, z) waypoints in NED frame
        
        Example:
            grid = GridMission(center=(0,0), width=20, length=20, 
                          altitude=15, spacing=5)
            waypoints = grid.generate()
            # Returns 10 waypoints covering 20x20m area
        """
        # Step 1: Calculate where tracks should be positioned
        track_positions = self._calculate_tracks()
    
        # Step 2: Create waypoints along those tracks
        self.waypoints = self._create_waypoints(track_positions)
    
        # Step 3: Return the waypoints
        return self.waypoints


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Grid Mission Generator")
    print("=" * 60)
    
    # Create a grid mission
    grid = GridMission(
        center=(0, 0),
        width=20,
        length=20,
        altitude=15,
        spacing=5
    )
    
    # Generate waypoints
    waypoints = grid.generate()
    
    # Display results
    print("\nMission Parameters:")
    print(f"  Area: {grid.width}m × {grid.length}m")
    print(f"  Altitude: {grid.altitude}m")
    print(f"  Track spacing: {grid.spacing}m")
    
    print(f"\nGenerated {len(waypoints)} waypoints:")
    print("\n  WP#   X (N)    Y (E)    Z (D)   | Description")
    print("  " + "-" * 50)
    
    for i, (x, y, z) in enumerate(waypoints):
        track_num = i // 2
        position = "Start" if i % 2 == 0 else "End"
        print(f"  {i:2d}   {x:6.1f}   {y:6.1f}   {z:6.1f}   | Track {track_num} {position}")
    
    # Calculate statistics
    total_distance = 0
    for i in range(len(waypoints) - 1):
        x1, y1, z1 = waypoints[i]
        x2, y2, z2 = waypoints[i + 1]
        distance = ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5
        total_distance += distance
    
    print(f"\n" + "=" * 60)
    print("Mission Statistics:")
    print(f"  Total distance: {total_distance:.1f}m")
    print(f"  Estimated time: {total_distance / 1.0:.1f}s @ 1m/s")
    print(f"  Area covered: {grid.width * grid.length:.0f} m²")
    print("=" * 60)