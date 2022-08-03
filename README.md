# coral_object_detector
The goal of this is to use a Google Coral m.2 accelerator to provide an identical json output to what deepstack provides, so that it can be used interchangeably with my [object detector project](https://github.com/fahcsim/detector)
## vars.yaml example:
api_key: bP86G5m1xG2Ldfgdfg8x0hnefgdfKc3ip4 # shinobi api key \
directory: ./photos/         # directory to store photos in \
user_id: QI6r6Bsh08          # shinobi user id \
group_key: admin             # shinobi group key \
camera_friendly: front_door  # human friendly name for the camera \
camera_id: zuErUXTCyk        # shinobi camera ID \
shinobi_ip: 10.0.0.12:8080   # shinobi ip/port \
object: person               # object to look for \
interval: 5                  # how often to scan \
log: info                    # logging level

## Running with Docker
1. Create a valid vars.yaml file
2. Build the container `docker build -t coral_object_detector .`
3. Run the container `sudo docker run --device /dev/apex_0:/dev/apex_0 -v /home/yourname/coral_object_detector:/python -it coral_object_detector`
