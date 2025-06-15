import keyboard
import time

def press_esc_after_delay(seconds):
    """
    Simulate an "ESC" keypress after the given delay.

    Args:
        seconds (int): Number of seconds to wait before pressing "ESC".
    """
    print(f"Waiting for {seconds} seconds before pressing 'ESC'...")
    time.sleep(seconds)
    keyboard.press_and_release('esc')
    print("ESC key pressed.")

if __name__ == "__main__":
    # Specify the delay in seconds
    delay = int(input("Enter the number of seconds to wait: "))
    press_esc_after_delay(delay)
