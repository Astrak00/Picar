from picarx import Picarx
import time

def main():
    try:
        px = Picarx()
        # px = Picarx(ultrasonic_pins=['D2','D3']) # tring, echo
       
        while True:
            distance = round(px.ultrasonic.read(), 2)
            print("distance: ",distance)

    finally:
        px.forward(0)


if __name__ == "__main__":
    main()
