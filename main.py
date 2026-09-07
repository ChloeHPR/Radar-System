from speed_mode import acquisition_treatment

def main():
    # path to the file for speed mode processing
    radar_file = "/Acquisition/acquistion_aller_retour_pause(2).wav" #
    acquisition_treatment(radar_file)

if __name__ == "__main__":
    main()
