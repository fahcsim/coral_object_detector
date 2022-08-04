import os
def reset_directories(directory):
  if not os.path.exists(directory):
    os.mkdir(directory)
  if not os.path.exists(f"{directory}tmp"):
    os.mkdir(f"{directory}tmp")
  elif os.path.exists(f"{directory}tmp"):
    # remove tmp directory and its contents, then recreate it
    shutil.rmtree(f"{directory}tmp")
    os.mkdir(f"{directory}tmp")