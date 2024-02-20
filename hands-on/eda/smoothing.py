import numpy as np
import pandas as pd

def get_evs(data, smooth, end="start"):

  if end == "start":
    y_end = data[0]
    y_smoothed_next_to_end = smooth[1]
    y_smoothed_next_to_end_but_one = smooth[2]
  elif end == "end":
    y_end = data[-1]
    y_smoothed_next_to_end = smooth[-2]
    y_smoothed_next_to_end_but_one = smooth[-3]

  change_start = abs(y_smoothed_next_to_end - y_smoothed_next_to_end_but_one)

  if change_start > 1e-4:
    max_change = 2.*change_start
    y_change_min = y_smoothed_next_to_end - max_change
    y_change_max = y_smoothed_next_to_end + max_change
    
    # -- case 02
    if y_change_min <= y_end <= y_change_max:
      y_smoothed_end = y_end

    # -- case 01
    else:
      distance_to_y_change_min = abs(y_end - y_change_min)
      distance_to_y_change_max = abs(y_end - y_change_max)

      if distance_to_y_change_max < distance_to_y_change_min:
        y_smoothed_end = y_change_max
      else:
        y_smoothed_end = y_change_min

  else:
    y_smoothed_end = y_smoothed_next_to_end

  return y_smoothed_end


def apply_evs(data, smooth):
  y_smoothed_start = get_evs(data, smooth, end="start")
  y_smoothed_end = get_evs(data, smooth, end="end")

  smooth_with_evs = smooth.copy()
  smooth_with_evs[0] = y_smoothed_start
  smooth_with_evs[-1] = y_smoothed_end
  return smooth_with_evs


def apply_3(data):
  """data must have a numpy ndarrray data type"""
  data_update = data.copy()
  smooth3 = (pd.Series(
    [np.nan, *list(data_update), np.nan])
      .rolling(window=3, center=True).median().iloc[1:-1]
    ).to_list() 
  smooth3 = apply_evs(data_update, smooth3)
  return smooth3


def apply_3R(data, tol=1e-4, max_iter=100, verbose=False):
  """
  data must have a numpy ndarray data type
  """
  data_update = data.copy()

  for i in range(max_iter):
    smooth3 = apply_3(data_update)

    residual = np.abs(np.array(data_update) - np.array(smooth3))
    is_no_change = np.all(residual < tol)
    
    if verbose:
      print(f"{i+1} {residual}")
    
    if is_no_change:
      # print(i)
      break 
    else:
      data_update = smooth3.copy()
  
  return i+1, smooth3
  

def scan_peak_or_valley(data, separate=False):
  """We use four windows scanning. We have a 2-high peak, if the second and
  third element are the same value, and the first and fourth elements
  are lower than the second element"""

  idx_peak = []
  idx_valley = []
  idx_split = []
  N = len(data)

  if separate:
    for i in range(N-3):
      first_element = data[i]
      second_element = data[i+1]
      third_element = data[i+2]
      fourth_element = data[i+3]

      if second_element == third_element:
        if first_element < second_element and fourth_element < second_element:
          idx_peak.append(i+2)

        elif first_element > second_element and fourth_element > second_element:
          idx_valley.append(i+2)
    return {"peak": idx_peak, "valley": idx_valley} 

  else:
    for i in range(N-3):
      first_element = data[i]
      second_element = data[i+1]
      third_element = data[i+2]
      fourth_element = data[i+3]

      if second_element == third_element:
        if first_element < second_element and fourth_element < second_element:
          idx_split.append(i+2)

        elif first_element > second_element and fourth_element > second_element:
          idx_split.append(i+2)

    return {"both": idx_split}


def apply_evs_in_split(smooth_left, smooth_right):
  y_smoothed_end = get_evs(smooth_left, smooth_left, end="end")
  y_smoothed_start = get_evs(smooth_right, smooth_right, end="start")

  smooth = np.concatenate([smooth_left, smooth_right])
  smooth[len(smooth_left)-1] = y_smoothed_end
  smooth[len(smooth_left)] = y_smoothed_start

  return smooth


def apply_S(data):
  smooth = data.copy()
  # peak_and_valley_dict = scan_peak_or_valley(smooth)
  # print(smooth)
  
  # -- fix peak
  # for peak in peak_valley_dict["peak"]:
  #   # print(f"peak: {peak}")
  #   smooth = apply_evs_in_split(smooth[:peak], smooth[peak:])

  # # -- fix valley
  # for valley in peak_and_valley_dict["valley"]:
  #   # print(f"valley: {valley}")
  #   smooth = apply_evs_in_split(smooth[:valley], smooth[valley:])
  # print(type(smooth), smooth)

  
  peak_and_valley_dict = scan_peak_or_valley(smooth)
  for split in peak_and_valley_dict["both"]:
    smooth = apply_evs_in_split(smooth[:split], smooth[split:])
    # smooth = np.array(apply_3R(smooth)[1])
    
  return smooth


def apply_H(data):
  if type(data) == pd.core.series.Series:
    new_data = data.copy().to_list()
  elif type(data) == np.ndarray:
    new_data = data.copy()
  new_data = [new_data[0], *new_data, new_data[-1]]
  return (pd.Series(new_data).rolling(window=3, center=True).apply(
    lambda s: 0.25*s.iloc[0] + 0.5*s.iloc[1] + 0.25*s.iloc[2]).iloc[1:-1]).to_numpy()  


def apply_5(data):
  data_update = data.copy()
  smooth5 = pd.Series(data_update).rolling(window=5, center=True).median()

  # -- fill in next-to-end data
  smooth5.iloc[1] = np.median(data_update[:3])
  smooth5.iloc[-2] = np.median(data_update[-3:])

  # -- fill in end-value
  left_evs = 3.*smooth5.iloc[1] - 2.*smooth5.iloc[2]
  right_evs = 3.*smooth5.iloc[-2] + 2.*smooth5.iloc[-3]
  smooth5.iloc[0] = np.median([left_evs, data_update[0], smooth5.iloc[1]])
  smooth5.iloc[-1] = np.median([smooth5.iloc[-2], data_update[-1], right_evs])
  
  return smooth5.to_numpy()


def apply_42(data):
  data_update = data.copy()
  smooth42 = pd.Series(data_update).rolling(window=4, center=True)\
    .median().iloc[1:].to_list()

  # -- fill in next-to-end data
  smooth42[0] = np.median(data[:2])
  smooth42[-1] = np.median(data[-2:])

  # -- recentering with median of 2
  # because pd.Series.rolling won't centere the result to the middle
  # index, we remove a first point from smooth42.
  smooth42 = pd.Series(smooth42).rolling(window=2, center=True)\
    .median().to_list()
  smooth42 = [data_update[0], *smooth42[1:], data_update[-1]]
  
  return np.array(smooth42)


def apply_twice(data, smooth, seq):
  rough = data - smooth

  for smoother in seq.split("_"):
    if smoother == "3R":
      rough = apply_3R(rough)[1]
    elif smoother == "S":
      rough = apply_S(rough)
    elif smoother == "H":
      rough = apply_H(rough)

  return smooth + rough
