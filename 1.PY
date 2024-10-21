import pygame
import math
import sys

# Initializes Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple PFD Visualization")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
BROWN = (160, 82, 45)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 128)

# Font
font = pygame.font.SysFont("Arial", 20)

# State variables
pitch = 0       # Pitch (degrees)
bank = 0        # Roll (degrees)
airspeed = 120  # Airspeed (knots)
altitude = 5000 # Altitude (ft)
fpv_pitch = 0   # Flight Path Vector pitch
throttle = 0.0  # Engine power (-1 to 1)
heading = 0     # Aircraft heading (degrees)
angle_of_attack = 0  # Angle of attack
rudder = 0      # Rudder control
wind_force = 20  # Wind effect on airspeed

# Axis mapping
control_mapping = {
    "Pitch": None,
    "Roll": None,
    "Throttle": None,
    "Rudder": None
}

# Available axes
axis_options = ["Axis 0", "Axis 1", "Axis 2", "Axis 3"]
selected_axis_index = 0  # Currently selected axis index
selected_control = "Pitch"  # Control initially selected

# Joystick setup
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Function to draw the artificial horizon
def draw_horizon(pitch, bank):
    # Limit pitch to 90 degrees
    pitch = max(-90, min(90, pitch))
    
    # Draw sky and ground
    horizon_y = HEIGHT // 2 + pitch * 5
    pygame.draw.rect(screen, BROWN, (0, horizon_y, WIDTH, HEIGHT - horizon_y))  # Ground
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, horizon_y))  # Sky

    # Horizon line
    pygame.draw.line(screen, WHITE, (0, horizon_y), (WIDTH, horizon_y), 4)

    # Add angle marks on the horizon from -90 to 90 degrees
    for angle in range(-90, 91, 5):
        angle_y = horizon_y - angle * 5
        if angle % 10 == 0:
            pygame.draw.line(screen, WHITE, (WIDTH // 2 - 10, angle_y), (WIDTH // 2 + 10, angle_y), 2)
        else:
            pygame.draw.line(screen, WHITE, (WIDTH // 2 - 5, angle_y), (WIDTH // 2 + 5, angle_y), 1)

    # Rotate the horizon based on bank angle
    horizon_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    horizon_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(horizon_surface, BLUE, (0, 0, WIDTH, horizon_y))  # Sky
    pygame.draw.rect(horizon_surface, BROWN, (0, horizon_y, WIDTH, HEIGHT - horizon_y))  # Ground
    rotated_horizon = pygame.transform.rotate(horizon_surface, -bank)
    screen.blit(rotated_horizon, (WIDTH // 2 - rotated_horizon.get_width() // 2, HEIGHT // 2 - rotated_horizon.get_height() // 2))

# Function to draw the airplane reference
def draw_airplane_reference():
    pygame.draw.line(screen, YELLOW, (WIDTH // 2 - 20, HEIGHT // 2), (WIDTH // 2 + 20, HEIGHT // 2), 5)  # Horizontal line
    pygame.draw.line(screen, YELLOW, (WIDTH // 2, HEIGHT // 2 - 10), (WIDTH // 2, HEIGHT // 2 + 10), 5)  # Vertical line

# Function to draw the FPV (Flight Path Vector)
def draw_fpv(fpv_pitch):
    fpv_x = WIDTH // 2
    fpv_y = HEIGHT // 2 - fpv_pitch * 5
    pygame.draw.circle(screen, GREEN, (fpv_x, fpv_y), 10, 2)  # Circle
    pygame.draw.line(screen, GREEN, (fpv_x - 20, fpv_y), (fpv_x - 10, fpv_y), 2)
    pygame.draw.line(screen, GREEN, (fpv_x + 10, fpv_y), (fpv_x + 20, fpv_y), 2)

# Function to draw the compass
def draw_compass(heading):
    center_x = WIDTH // 2
    center_y = HEIGHT - 100
    radius = 50

    # Compass circle
    pygame.draw.circle(screen, WHITE, (center_x, center_y), radius, 2)

    # Drawing wind indicator
    wind_indicator_length = radius * 0.7
    wind_angle_rad = math.radians(heading + 90)  # Adjust wind direction
    wind_x = center_x + wind_indicator_length * math.cos(wind_angle_rad)
    wind_y = center_y + wind_indicator_length * math.sin(wind_angle_rad)
    pygame.draw.line(screen, YELLOW, (center_x, center_y), (wind_x, wind_y), 3)

    # Draw wind direction arrows
    pygame.draw.polygon(screen, YELLOW, [(center_x, center_y), (wind_x, wind_y), (wind_x - 5, wind_y - 5), (wind_x + 5, wind_y - 5)])

    # Drawing the compass rose
    for angle in range(0, 360, 30):
        angle_rad = math.radians(angle)
        x_start = center_x + radius * math.cos(angle_rad)
        y_start = center_y + radius * math.sin(angle_rad)
        x_end = center_x + (radius + 10) * math.cos(angle_rad)
        y_end = center_y + (radius + 10) * math.sin(angle_rad)
        pygame.draw.line(screen, WHITE, (x_start, y_start), (x_end, y_end), 2)

    # Drawing the aircraft direction with fixed needle
    needle_length = radius * 0.9
    heading_rad = math.radians(heading)
    arrow_x = center_x + needle_length * math.cos(heading_rad)
    arrow_y = center_y + needle_length * math.sin(heading_rad)
    pygame.draw.line(screen, GREEN, (center_x, center_y), (arrow_x, arrow_y), 4)

    # Compass text
    compass_text = font.render(f"Heading: {heading:.1f}°", True, WHITE)
    screen.blit(compass_text, (center_x - 40, center_y + 20))

# Function to draw the airspeed indicator
def draw_airspeed_indicator(airspeed):
    airspeed_text = font.render(f"Airspeed: {airspeed:.1f} KT", True, WHITE)
    screen.blit(airspeed_text, (50, 100))
    pygame.draw.rect(screen, WHITE, (30, 90, 150, 30), 2)

# Function to draw the altimeter
def draw_altimeter(altitude):
    altitude_text = font.render(f"Altitude: {altitude} FT", True, WHITE)
    screen.blit(altitude_text, (700, 100))
    pygame.draw.rect(screen, WHITE, (680, 90, 170, 30), 2)

# Function to draw the angle of attack
def draw_angle_of_attack(angle_of_attack):
    angle_text = font.render(f"AoA: {angle_of_attack:.1f}°", True, WHITE)
    screen.blit(angle_text, (700, 130))
    pygame.draw.rect(screen, WHITE, (680, 120, 100, 30), 2)

# Function to draw the throttle
def draw_throttle(throttle):
    throttle_percentage = (throttle * 100)  # Convert to percentage
    throttle_text = font.render(f"Throttle: {throttle_percentage:.1f}%", True, WHITE)
    screen.blit(throttle_text, (50, 130))
    pygame.draw.rect(screen, WHITE, (30, 120, 150, 30), 2)

# Function to draw the rudder indicator
def draw_rudder(rudder):
    rudder_text = font.render(f"Rudder: {rudder:.1f}", True, WHITE)
    screen.blit(rudder_text, (50, 160))
    pygame.draw.rect(screen, WHITE, (30, 150, 150, 30), 2)

# Function to draw the axis selection screen
def draw_axis_selection(selected_control):
    screen.fill(BLACK)
    
    # Display axis selection
    controls_list = list(control_mapping.keys())
    y_offset = 50
    for control in controls_list:
        color = WHITE if control == selected_control else (100, 100, 100)
        control_text = font.render(control, True, color)
        screen.blit(control_text, (WIDTH // 2 - 50, y_offset))
        y_offset += 30

    # Display current selection
    axis_text = font.render("Selected Axis: " + axis_options[selected_axis_index], True, WHITE)
    screen.blit(axis_text, (WIDTH // 2 - 100, y_offset))
    y_offset += 30

    # Display instructions
    instructions = font.render("Use UP/DOWN to change axis, ENTER to confirm", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - 220, y_offset))

    pygame.display.flip()

# Function to handle axis selection
def handle_axis_selection(event, selected_control):
    global selected_axis_index
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_axis_index = (selected_axis_index - 1) % len(axis_options)
        elif event.key == pygame.K_DOWN:
            selected_axis_index = (selected_axis_index + 1) % len(axis_options)
        elif event.key == pygame.K_RETURN:
            control_mapping[selected_control] = axis_options[selected_axis_index]
            return None  # Exit axis selection
    return selected_control

# Main function
def main():
    global pitch, bank, throttle, altitude, heading, angle_of_attack, rudder, airspeed, fpv_pitch, selected_control

    selected_control = "Pitch"  # Ensure selected_control is defined

    is_axis_selection = False  # State to determine if we are in axis selection menu

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if is_axis_selection:
                new_selected_control = handle_axis_selection(event, selected_control)
                if new_selected_control is not None:
                    selected_control = new_selected_control
                else:
                    is_axis_selection = False  # Return to PFD

            else:  # We are in the PFD
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Key to access the axis selection menu
                        is_axis_selection = True

                # Update simulation (simulating joystick inputs)
                if joystick:
                    throttle = joystick.get_axis(3)  # Throttle
                    pitch_input = joystick.get_axis(1) * 1  # Pitch (inverted)
                    bank_input = joystick.get_axis(0) * 1  # Roll (inverted)
                    rudder = joystick.get_axis(2)  # Rudder

                    # Apply input to pitch and roll with reduced sensitivity
                    pitch += pitch_input * 0.5
                    bank += bank_input * 0.5
                    
                    # Clamp values to limit range
                    pitch = max(-90, min(90, pitch))
                    bank = max(-90, min(90, bank))

                    # Update altitude and FPV with wind effect
                    altitude += (math.sin(math.radians(fpv_pitch)) * 0.5)
                    wind_effect = wind_force * 0.1  # Calculate wind effect
                    altitude += wind_effect

                    # Calculate airspeed increase based on throttle
                    airspeed += throttle * 5  # Increase airspeed proportionally to throttle

                    # Exponential airspeed decrease/increase based on pitch
                    if pitch > 0:  # Nose up
                        airspeed *= (1 - (pitch / 90) ** 2)  # Decrease airspeed exponentially as pitch approaches 90
                    elif pitch < 0:  # Nose down
                        airspeed *= (1 + (-pitch / 90) ** 2)  # Increase airspeed exponentially as pitch approaches -90

                    # Limit airspeed
                    airspeed = max(0, min(airspeed, 200))

                    # Update heading based on rudder
                    heading += rudder * 2  # Rudder influences heading
                    heading = heading % 360  # Keep heading within 0-360 degrees

                    # Update angle of attack
                    angle_of_attack = pitch - bank  # Simple calculation for angle of attack

                    # Adjust FPV less responsive than pitch
                    fpv_pitch += (pitch - fpv_pitch) * 0.05  # FPV follows pitch with reduced sensitivity

        # Update the PFD or axis selection screen
        if is_axis_selection:
            draw_axis_selection(selected_control)
        else:
            screen.fill(BLACK)
            draw_horizon(pitch, bank)
            draw_airplane_reference()
            draw_fpv(fpv_pitch)
            draw_compass(heading)
            draw_airspeed_indicator(airspeed)
            draw_altimeter(altitude)
            draw_angle_of_attack(angle_of_attack)
            draw_throttle(throttle)
            draw_rudder(rudder)

            # Instructions to access the selection menu
            access_menu_text = font.render("Press 'S' to access axis selection", True, WHITE)
            screen.blit(access_menu_text, (50, 300))

            pygame.display.flip()

    pygame.quit()
    sys.exit()

# Run the program
main()
