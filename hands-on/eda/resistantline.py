import numpy as np
import matplotlib.pyplot as plt

def divide_three_batches(x_data, y_data):
  rem = len(x_data) % 3
  quotient = len(x_data) // 3

  # -- first sort x_data and y_data order follow from it.
  y_data = y_data[np.argsort(x_data, kind="stable")]
  x_data = np.sort(x_data, kind="stable")

  batches = {}
  if rem == 0:
    batches[0] = {'x': x_data[:quotient],
                  'y': y_data[:quotient]}
    batches[1] = {'x': x_data[quotient:2*quotient],
                  'y': y_data[quotient:2*quotient]}
    batches[2] = {'x': x_data[2*quotient:],
                  'y': y_data[2*quotient:]}
    assert all([len(batches[i]['x']) == quotient for i in range(3)]
               + [len(batches[i]['y']) == quotient for i in range(3)])
  elif rem == 1:
    batches[0] = {'x': x_data[:quotient],
                  'y': y_data[:quotient]}
    batches[1] = {'x': x_data[quotient:2*quotient+1],
                  'y': y_data[quotient:2*quotient+1]}
    batches[2] = {'x': x_data[2*quotient+1:],
                  'y': y_data[2*quotient+1:]}
    assert all([len(batches[0]['x']) == quotient, 
                len(batches[2]['x']) == quotient, 
                len(batches[1]['x']) == quotient+1,
                len(batches[0]['y']) == quotient,
                len(batches[2]['y']) == quotient,
                len(batches[1]['y']) == quotient+1])
  elif rem == 2:
    batches[0] = {'x': x_data[:quotient+1],
                  'y': y_data[:quotient+1]}
    batches[1] = {'x': x_data[quotient+1: 2*quotient+1],
                  'y': y_data[quotient+1: 2*quotient+1]}
    batches[2] = {'x': x_data[2*quotient+1:],
                  'y': y_data[2*quotient+1:]}
    # batches[0] = {'x': x_data[:quotient-1],
    #               'y': y_data[:quotient-1]}
    # batches[1] = {'x': x_data[quotient-1: 2*quotient+2],
    #               'y': y_data[quotient-1: 2*quotient+2]}
    # batches[2] = {'x': x_data[2*quotient+2:],
    #               'y': y_data[2*quotient+2:]}

    # print(batches)
    # assert all([len(batches[0]['x']) == quotient+1, 
    #             len(batches[2]['x']) == quotient+1, 
    #             len(batches[1]['x']) == quotient,
    #             len(batches[0]['y']) == quotient+1,
    #             len(batches[2]['y']) == quotient+1, 
    #             len(batches[1]['y']) == quotient])
  return batches


def get_resistance_line(x_data, y_data, max_iter=10, tol=1e-4, verbose=True):
  batches_dict = {}

  batches = divide_three_batches(x_data, y_data)
  
  boundaries = [np.mean([batches[0]['x'][-1], batches[1]['x'][0]]),
                np.mean([batches[1]['x'][-1], batches[2]['x'][0]])]

  median_batch = [
    [np.median(batches[i]['x']) for i in range(3)],
    [np.median(batches[i]['y']) for i in range(3)]]
  
  batches_dict["boundary"] = boundaries
  batches_dict["batches"] = batches
  batches_dict["median_batch"] = median_batch
  batches_dict["no_runtime"] = True

  slope_b = (median_batch[1][2] - median_batch[1][0]) / (median_batch[0][2] - median_batch[0][0])
  # intercept_a = np.median([y - slope_b*x for x, y in zip(*median_batch)])
  intercept_a = np.mean([y - slope_b*x for x, y in zip(*median_batch)])
  
  for j in range(max_iter):
    residual_batches = {
      k: {'x': v['x'],
          'y': v['y'] - (intercept_a + slope_b*np.array(v['x']))} 
      for k, v in batches.items()}
    
    median_residual_batch = [
      [np.median(residual_batches[i]['x']) for i in range(3)],
      [np.median(residual_batches[i]['y']) for i in range(3)]]

    residual_slope_b = (
      median_residual_batch[1][2] - median_residual_batch[1][0]) \
      / (median_residual_batch[0][2] - median_residual_batch[0][0])
    # residual_intercept_a = np.median([y - residual_slope_b*x 
    #                                   for x, y in zip(*median_residual_batch)])
    residual_intercept_a = np.mean(
      [y - residual_slope_b*x for x, y in zip(*median_residual_batch)])
    
    # if j > 0 and abs(residual_slope_b - batches_dict[j-1]["residual_slope_intercept"][0]) < tol:
    if j > 0 and abs(residual_slope_b) < tol:
      intercept_a += np.mean([y for x, y in zip(*median_residual_batch)]) 

      residual_batches = {
        k: {'x': v['x'],
            'y': v['y'] - (intercept_a + slope_b*np.array(v['x']))} 
        for k, v in batches.items()}
      
      median_residual_batch = [
        [np.median(residual_batches[i]['x']) for i in range(3)],
        [np.median(residual_batches[i]['y']) for i in range(3)]]

      residual_slope_b = (median_residual_batch[1][2] - median_residual_batch[1][0]) \
                          / (median_residual_batch[0][2] - median_residual_batch[0][0])
      # residual_intercept_a = np.median([y - residual_slope_b*x 
      #                                   for x, y in zip(*median_residual_batch)])
      residual_intercept_a = np.mean([y - residual_slope_b*x 
                                    for x, y in zip(*median_residual_batch)])
      
      batches_dict["iter_max"] = j
      if verbose:
        print(j, slope_b, intercept_a, residual_slope_b, residual_intercept_a)
      batches_dict[j] = {
        "slope_intercept": [slope_b, intercept_a],
        "residual_batches": residual_batches,
        "median_residual_batch": median_residual_batch,
        "residual_slope_intercept": [residual_slope_b, residual_intercept_a],
      }
      break

    batches_dict["iter_max"] = j
    if verbose:
      print(j, slope_b, intercept_a, residual_slope_b, residual_intercept_a)
    # print(residual_slope_b, residual_intercept_a)
    batches_dict[j] = {
      "slope_intercept": [slope_b, intercept_a],
      "residual_batches": residual_batches,
      "median_residual_batch": median_residual_batch,
      "residual_slope_intercept": [residual_slope_b, residual_intercept_a],
    }



    # -- update slope_b 
    if j < 2:
      slope_b += residual_slope_b
    else:
      b_nM1 = batches_dict[j-1]["slope_intercept"][0]                 # slope at n-1
      b_res_nM1 = batches_dict[j-1]["residual_slope_intercept"][0]    # residual slope at n-1
      b_nM2 = batches_dict[j-2]["slope_intercept"][0]                 # slope at n-2
      b_res_nM2 = batches_dict[j-2]["residual_slope_intercept"][0]    # residual slope at n-2
      denom = abs(b_res_nM1 - b_res_nM2)
      if denom > 1e-7:
        slope_b = b_nM1 - b_res_nM1*(b_nM1 - b_nM2)/(b_res_nM1 - b_res_nM2)
      else:
        slope_b = b_nM1 + b_res_nM1
    # intercept_a = np.median([y - slope_b*x for x, y in zip(*median_batch)])
    # intercept_a = np.mean([y - slope_b*x for x, y in zip(*median_batch)])


  return batches_dict


def plot_resistance_line(x_data, y_data, final_intercept, final_slope, reg_line=None,
                         figsize=(4, 4), x_label="$x$", y_label="$y$"):
  fig, ax = plt.subplots(figsize=figsize)

  batches = divide_three_batches(x_data, y_data)

  for i in range(3):
    ax.plot(batches[i]['x'], batches[i]['y'], marker='o', linestyle="None", markersize=8,
            markerfacecolor="gray", markeredgecolor="k", alpha=.5)

  # -- vertical lines for dividing each batch
  boundary1 = np.mean([batches[0]['x'][-1], batches[1]['x'][0]])
  boundary2 = np.mean([batches[1]['x'][-1], batches[2]['x'][0]])

  ax.axvline(boundary1, linestyle='--', linewidth=1, color='gray', alpha=0.5)
  ax.axvline(boundary2, linestyle='--', linewidth=1, color='gray', alpha=0.5)

  # -- add medians for each batch
  median_each_batch = [
    [np.median(batches[i]['x']) for i in range(3)],
    [np.median(batches[i]['y']) for i in range(3)]]
  ax.plot(median_each_batch[0], median_each_batch[1], marker='o', 
          linestyle="None", markersize=10, markerfacecolor="red", alpha=0.5,
          markeredgecolor="k")

  xlim = ax.get_xlim()
  ylim = ax.get_ylim()

  x_fit = np.array([np.min(batches[0]['x']), np.max(batches[2]['x'])])
  x_fit[0] -= 0.5*(x_fit[1] - x_fit[0])
  x_fit[1] += 0.5*(x_fit[1] - x_fit[0])
  y_fit = final_intercept + final_slope*x_fit 
  ax.plot(x_fit, y_fit, color='r', alpha=1, linewidth=1.5)
  
  if reg_line is not None:
    y_reg_line = reg_line[1] + reg_line[0]*x_fit
    ax.plot(x_fit, y_reg_line, color="k", linestyle="--", linewidth=1.5)

  ax.set_title(f"$y = {final_intercept:.6f} + ({final_slope:.6f})x$", fontsize=12)
  ax.set_xlim(xlim)
  ax.set_ylim(ylim)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)

  plt.show(fig)


def plot_3points(x_data, y_data, figsize=(4, 4), x_label="$x$", y_label="$y$"):
  fig, ax = plt.subplots(figsize=figsize)

  batches = divide_three_batches(x_data, y_data)

  for i in range(3):
    ax.plot(batches[i]['x'], batches[i]['y'], marker='o', linestyle="None", markersize=8,
            markerfacecolor="gray", markeredgecolor="k", alpha=.5)

  # -- vertical lines for dividing each batch
  boundary1 = np.mean([batches[0]['x'][-1], batches[1]['x'][0]])
  boundary2 = np.mean([batches[1]['x'][-1], batches[2]['x'][0]])

  ax.axvline(boundary1, linestyle='--', linewidth=1, color='gray', alpha=0.5)
  ax.axvline(boundary2, linestyle='--', linewidth=1, color='gray', alpha=0.5)

  # -- add medians for each batch
  median_each_batch = [
    [np.median(batches[i]['x']) for i in range(3)],
    [np.median(batches[i]['y']) for i in range(3)]]
  ax.plot(median_each_batch[0], median_each_batch[1], marker='o', 
          linestyle="None", markersize=10, markerfacecolor="red", alpha=0.5,
          markeredgecolor="k", zorder=2)

  # -- a line connecting left and middle median
  x_fit = np.array([np.min(batches[0]['x']), median_each_batch[0][1]])
  slope_left_middle = (median_each_batch[1][1] - median_each_batch[1][0])\
    /(median_each_batch[0][1] - median_each_batch[0][0])
  y_fit = median_each_batch[1][0] + slope_left_middle*(x_fit - median_each_batch[0][0])
  ax.plot(x_fit, y_fit, color='r', alpha=1, linewidth=1.5, zorder=1)

  # --  a line connecting middle and right median
  x_fit = np.array([median_each_batch[0][1], np.max(batches[2]['x'])])
  slope_middle_right = (median_each_batch[1][2] - median_each_batch[1][1])\
    /(median_each_batch[0][2] - median_each_batch[0][1])
  y_fit = median_each_batch[1][1] + slope_middle_right*(x_fit - median_each_batch[0][1])
  ax.plot(x_fit, y_fit, color='r', alpha=1, linewidth=1.5, zorder=1)
  
  # -- a line connecting left and right median
  ax.plot([median_each_batch[0][0], median_each_batch[0][2]],
          [median_each_batch[1][0], median_each_batch[1][2]], color='k', alpha=1, 
          linewidth=1.5, zorder=1)
  
  # ax.set_xlim(xlim)
  # ax.set_ylim(ylim)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)

  plt.show(fig)

