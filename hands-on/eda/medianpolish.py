import numpy as np
import matplotlib.pyplot as plt


def plot_polish(vals_with_margins, row_labels, col_labels, ax, 
                significant_num=10., sweep_flag=None):
  
  """Use this if the input vals_with_margins is replaced by vals without
  margins. When sweep_flag is in default (None), we do not change into
  different layout. What we mean by changing is margin row medians 
  are positioned from left to right, margin column medians are positioned 
  from bottom to top, and bottom right common effect is positioned to 
  top left corner)"""
  if sweep_flag == 0:
    arr_size = np.shape(vals_with_margins)
    arr_with_margins = np.zeros([arr_size[0] + 1, arr_size[1] + 1])
    arr_with_margins[1:, 1:] = vals_with_margins.copy()
    vals_with_margins = arr_with_margins.copy()

  elif sweep_flag == 1:
    arr_size = np.shape(vals_with_margins)
    arr_with_margins = np.zeros([arr_size[0] + 1, arr_size[1]])
    arr_with_margins[1:, 1:] = vals_with_margins[:, :-1]
    arr_with_margins[1:, 0] = vals_with_margins[:, -1]
    vals_with_margins = arr_with_margins.copy()

  elif sweep_flag is not None and sweep_flag >= 2:
    arr_size = np.shape(vals_with_margins)
    arr_with_margins = np.zeros([arr_size[0], arr_size[1]])
    arr_with_margins[1:, 1:] = vals_with_margins[:-1, :-1]
    arr_with_margins[1:, 0] = vals_with_margins[:-1, -1]
    arr_with_margins[0, 1:] = vals_with_margins[-1, :-1]
    arr_with_margins[0, 0] = vals_with_margins[-1, -1]
    vals_with_margins = arr_with_margins.copy()
      
  
  v_range = np.max(np.abs(vals_with_margins))
  v_range = [-v_range, v_range]
  cmap = "RdYlBu_r"
  # cmap = "BrBG"
  # ax.imshow(vals, cmap=cmap, vmin=v_range[0], vmax=v_range[1])
  ax.imshow(vals_with_margins, cmap=cmap, vmin=v_range[0], vmax=v_range[1])

  # -- auxiliary hline and vline for better visualization
  for i in range(len(row_labels)-1):
    ax.axhline(1/2 + (i+1), color="gray", linewidth=2)
  for j in range(len(col_labels)-1):
    ax.axvline(1/2 + (j+1), color="gray", linewidth=2)

  # -- vertical and horizontal lines to separate margins and vals
  ax.axvline(1/2., color="k", linewidth=4)
  ax.axhline(1/2., color="k", linewidth=4)

  # -- set x ticks to the top, set tick positions and tick labels
  ax.xaxis.tick_top()
  ax.set_xticks(np.arange(len(col_labels) + 1), labels=[""] + col_labels)
  ax.set_yticks(np.arange(len(row_labels) + 1), labels=[""] + row_labels)

  # -- add text annotation to the center of vals
  for i in range(len(row_labels)+1):
    for j in range(len(col_labels)+1):
      val = vals_with_margins[i, j]
      if val >= significant_num:
        val_text = f"{val:.4g}"
      else:
        val_text = f"{val:.3g}"
      ax.text(j, i, val_text, ha="center", va="center", color="k")

  # ax.set_aspect("equal")
  return ax


def plot_polish_progress(polish_dict, row_labels, col_labels, max_cols=4, 
                         height=4, sweep_flag=None):
  """To use this function, you have to create another key "vals_with_margins" 
  inside each sweep"""

  N_polish = len(polish_dict)
  if max_cols > N_polish:
    max_cols = N_polish 
  
  fig, axes = plt.subplots(nrows=1, ncols=max_cols, 
                           figsize=(max_cols*height, height), sharey=True)
  
  for ax_idx in range(max_cols):
    # print(ax_idx)
    plot_polish(polish_dict[ax_idx]["vals_with_margins"], row_labels, col_labels, ax=axes[ax_idx],
                sweep_flag=sweep_flag)

  plt.show(fig)


def median_polish_velleman(arr_2d, iteration=1, tol=1e-4, sort_median=False,
                           x_label=None, y_label=None, all_output=False):
  if all_output:
    all_arr = {}

  """arr_2d is the values of the given table"""
  # -- sweep 1
  sweep1_part = np.median(arr_2d, axis=1)

  arr_clean_sweep1 = np.column_stack([arr_2d - sweep1_part[:, np.newaxis],
                                      sweep1_part])

  # -- sweep 2
  sweep2_part = np.median(arr_clean_sweep1, axis=0)
  arr_clean_sweep2 = np.row_stack([arr_clean_sweep1 - sweep2_part[np.newaxis, :],
                                   [sweep2_part]])
  
  # print(arr_clean_sweep2)
  
  # -- sweep 3
  median_sweep3 = np.median(arr_clean_sweep2[:, :-1], axis=1)
  sweep3_part = median_sweep3 + arr_clean_sweep2[:, -1]
  arr_clean_sweep3 = np.column_stack([
    arr_clean_sweep2[:, :-1] - median_sweep3[:, np.newaxis],
    sweep3_part[:, np.newaxis]])
  
  # -- sweep 4
  median_sweep4 = np.median(arr_clean_sweep3[:-1, :], axis=0)
  sweep4_part = median_sweep4 + arr_clean_sweep3[-1, :]
  arr_clean_sweep4 = np.row_stack([
    arr_clean_sweep3[:-1, :] - median_sweep4[np.newaxis, :],
    sweep4_part[np.newaxis, :]])

  if all_output:
    all_arr[1] = arr_clean_sweep1
    all_arr[2] = arr_clean_sweep2
    all_arr[3] = arr_clean_sweep3
    all_arr[4] = arr_clean_sweep4

  # add iteration
  sweep4_flatten = arr_clean_sweep4.flatten() 
  for idx in range(iteration-1):
    print(f"iteration: {idx+1}")
    arr_clean_sweep2 = arr_clean_sweep4.copy()
    # -- sweep 3
    median_sweep3 = np.median(arr_clean_sweep2[:, :-1], axis=1)
    sweep3_part = median_sweep3 + arr_clean_sweep2[:, -1]
    arr_clean_sweep3 = np.column_stack([
      arr_clean_sweep2[:, :-1] - median_sweep3[:, np.newaxis],
      sweep3_part[:, np.newaxis]])
    
    
    # -- sweep 4
    median_sweep4 = np.median(arr_clean_sweep3[:-1, :], axis=0)
    sweep4_part = median_sweep4 + arr_clean_sweep3[-1, :]
    arr_clean_sweep4 = np.row_stack([
      arr_clean_sweep3[:-1, :] - median_sweep4[np.newaxis, :],
      sweep4_part[np.newaxis, :]])
    
    if all_output:
      all_arr[4+1 + 2*idx] = arr_clean_sweep3
      all_arr[4+1 + 2*idx+1] = arr_clean_sweep4

    new_sweep4_flatten = arr_clean_sweep4.flatten()
    if np.all(abs(sweep4_flatten - new_sweep4_flatten) < tol):
      break
  
  if sort_median:
    row_median_sort_idx = np.argsort(arr_clean_sweep4[:-1, -1])
    final_sweep_sort_row_median = arr_clean_sweep4[list(row_median_sort_idx) + [-1], :]
    x_label_sort = x_label[row_median_sort_idx]

    col_row_median_sort_idx = np.argsort(final_sweep_sort_row_median[-1, :-1])
    final_sweep_sort_col_row_median = final_sweep_sort_row_median[
      :, list(col_row_median_sort_idx) + [-1]]
    y_label_sort = y_label[col_row_median_sort_idx]
    return final_sweep_sort_col_row_median, x_label_sort, y_label_sort
  else:
    if all_output:
      return all_arr
    else:
      return arr_clean_sweep4


def median_polish_gimond(vals, max_iter=4, agg=np.median, tol=1e-4):
    """vals is the values in the given table (without margin -- median row and cols)"""
    vals_with_margins = np.zeros(np.array(np.shape(vals)) + 1)
    vals_with_margins[1:, 1:] = vals

    polish_dict = {0: 
      {"vals_with_margins": vals_with_margins.copy()}}
    # -- compute overal median
    vals_with_margins[0, 0] = agg(vals_with_margins[1:, 1:])
    # -- compute residual table
    vals_with_margins[1:, 1:] -= vals_with_margins[0, 0]
    
    for i in range(max_iter):
      # print(f"  i = {i}")
      # -- compute the row medians (margin left is not included)
      # print(np.median(vals_with_margins[:, 1:], axis=1))
      row_medians = np.median(vals_with_margins[:, 1:], axis=1)
      vals_with_margins[:, 0] += row_medians
    
      # -- compute residual table from the row medians
      vals_with_margins[:, 1:] -= row_medians[:, np.newaxis]
      # print("row_medians", row_medians)
      # print(vals_with_margins)
    
      # -- compute the column median (margin top is not included)
      # print(np.median(vals_with_margins[1:, :], axis=0))
      column_medians = np.median(vals_with_margins[1:, :], axis=0)
      vals_with_margins[0, :] += column_medians

      # -- compute residual table from the col medians
      vals_with_margins[1:,:] -= column_medians[np.newaxis, :]
      # print("column_medians", column_medians)
      # print(vals_with_margins)
    
      polish_dict[i+1] = {
        "vals_with_margins": vals_with_margins.copy(),
        "row_medians": row_medians,
        "col_medians": column_medians
      }

      
      if np.all(row_medians < tol) and np.all(column_medians < tol):
        break

    polish_dict["max_iter"] = i+1
    return polish_dict