import time
import vision
from vimbot import Vimbot
from sys import argv


def main(site, task, is_groundtruth):
    print("Initializing the Vimbot driver...")
    driver = Vimbot(is_groundtruth=is_groundtruth)

    print(f"Navigating to {site}...")
    driver.navigate(f"http://{site}")
    objective = f"Do the following task: {task}"
    print(objective)

    while True:
        time.sleep(1)
        print("Capturing the screen...")
        screenshot = driver.capture()

        # print("Getting actions for the given objective...")
        action = vision.get_actions(screenshot, objective)
        print(f"JSON Response: {action}")

        if driver.perform_action(action):  # returns True if done
            break


if __name__ == "__main__":
    site, task, is_groundtruth = argv[1], argv[2], argv[3].lower() == "true"
    try:
        main(site, task, is_groundtruth)
    except KeyboardInterrupt:
        print("Exiting...")
