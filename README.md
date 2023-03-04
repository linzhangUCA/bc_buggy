# bc_buggy
The bc_buggy project provide a method to train a neural network powered 
autopilot using human driver's experience.
## Usage

### Collect Data (on RaspberryPi)
1. Connect a wireless Xbox joypad to RPi.
2. Run following command 
```console
cd <path to this repo>
python drive/collect_data.py
```
> The data logger will be ready after the prompt.
3. Press "A" button to toggle data recording.

### Train an Autopilot (on Linux host machine)
1. Transfer collected data via rsync.
```console
rsync -rv --partial <rpi user>@<rpi ip address>:<path to repo on rpi>/learn/data/<data dir> <path to repo on host>/learn/data/
```
> Feel free to rename the data directory to make it more descriptive.
2. Update `learn/behavioral_clone.py`. 
    - line 33: `data_dir` 
    - line 149: `epochs`
    - line 174: `model_name`
> You can check the learning curve in `learn/models/`
3. Train autopilot.
```console
cd <path to repo on host>
python learn/behavioral_clone.py
```
4. Transfer trained autopilot back to RPi. 
```console
rsync -rv --partial <path to repo on host>/learn/models/ <rpi user>@<rpi ip address>:<path to repo on rpi>/drive/models/
```

### Run Autopilot (on RaspberryPi)
1. Make sure engine threshold and steering offset in `drive/autopilot.py` are identical to `drive/collect_data.py`
2. Update `drive/autopilot.py` at line 80: `model_path`
3. Run autopilot
```console
cd <path to repo on rpi>
python drive/autopilot.py
```

# TODO
## Software
- [ ] Use start button to toggle data recording.
- [ ] Add legend to and fix x, y range for training curve.
- [ ] Use arguments to specify model and data.
- [ ] Learn steering only.
- [ ] Create model for stacked images.
- [ ] Use button to delete previous data.
## Hardware
- [ ] Design camera holder.
## Document
- [x] Update README with usage.
- [ ] Update wiki page.
