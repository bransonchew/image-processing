import argparse
import sys

from img.controller import Controller
from img.webcam import WebcamController


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Face tracking and recognition publishing script")

    # Optional argument
    parser.add_argument('-a', '--assets', type=str, default="assets", help="Assets path")

    # Boolean flags
    parser.add_argument('--webcam', action='store_true', help="Enable webcam mode")
    parser.add_argument('--takeoff', action='store_true', help="Enable drone takeoff")
    parser.add_argument('--export', action='store_true', help="Enable results export")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose mode")

    # Parse the arguments
    args = parser.parse_args()

    # Check for conflicting flags
    if args.webcam and args.takeoff:
        print("Error: --webcam and --takeoff flags cannot be used together.", file=sys.stderr)
        sys.exit(1)

    # Initialize controller and start system
    if args.webcam:
        controller = WebcamController(assets_path=args.assets,
                                      verbose=args.verbose)  # use webcam
        controller.start(export=args.export)
    else:
        controller = Controller(assets_path=args.assets,
                                verbose=args.verbose)  # use drone
        controller.start(takeoff=args.takeoff, export=args.export)


if __name__ == '__main__':
    main()
