import numpy as np
import scipy.stats as sc_stats
import pandas as pd


def get_stem_leaf_datastructure(arr, stem_digit=2):
  """A data structure for plotting stem and leaf display"""
  arr = [str(row) for row in arr] 
  stem_leaf_pair = [[row[:stem_digit], row[stem_digit:]] for row in arr]
  # print(stem_leaf_pair)

  stem_num =[int(pair[0]) for pair in stem_leaf_pair]
  max_stem = max(stem_num)
  min_stem = min(stem_num)
  stem_num_full = [min_stem + idx for idx in range(max_stem - min_stem + 1)]

  y_stem_interval = (max_stem - min_stem)/(len(stem_num_full) - 1)
  y_interval = [stem + idx*y_stem_interval for idx, stem in enumerate(stem_num_full)]

  # -- get leaf data for plotting the histogram based on the oultine of stem 
  #    and leaf display
  stem_leaf_dict = {}
  for stem, leaf in stem_leaf_pair:
    if stem in stem_leaf_dict:
      stem_leaf_dict[stem].append(leaf[0])
    else:
      stem_leaf_dict[stem] = [leaf[0]]
    
  # print(stem_leaf_dict)
  stem_leaf_hist = []
  for stem in stem_num_full:
    leaf = 0
    if f"{stem}" in stem_leaf_dict:
      key_stem = f"{stem}"
      leaf = len(stem_leaf_dict[key_stem])
    
    stem_leaf_hist.append([stem, leaf])

  stem_leaf_hist = np.array(stem_leaf_hist)

  return stem_num_full, stem_leaf_dict, y_interval, stem_leaf_hist


def plot_stem_leaf(stem_num_full, stem_leaf_dict, y_interval, ax, stem_shift=0.005, leaf_shift=0.01, 
          fontsize=16, margin_multiplier=0.05, width=0.1):
  """Make the plot for stem-and-leaf
  stem_shift [float]: the distance between the label of stem and the vertical line
  leaf_shift [float]: the distance between the label of leaf and the vertical line
  fontsize [int]: the font size for the stem and leaf numbers
  margin_multipler [float]: A multiplication factor for the width of the top
    and bottom margi of stem-and-leaf display
  width [float]: the width (along x-axis) of stem-and-leaf plot
  """
  vert_line_xcoord = 1
  
  for stem, stem_y_interval in zip(stem_num_full, y_interval):
    ax.text(vert_line_xcoord - stem_shift, stem_y_interval, f"{stem}", ha="right", va="center", 
            fontdict=dict(fontsize=fontsize))
    if f"{stem}" in stem_leaf_dict:
      key_stem = f"{stem}"
      ax.text(vert_line_xcoord + leaf_shift, stem_y_interval, f"{' '.join(stem_leaf_dict[key_stem])}",
              ha="left", va="center", fontdict=dict(fontsize=fontsize))

  max_y_interval = max(y_interval)
  min_y_interval = min(y_interval)
  margin = margin_multiplier*(max_y_interval - min_y_interval)
  ax.set_ylim([min_y_interval-margin, max_y_interval+margin])

  ax.set_xlim([1-width/2, 1 + 2*width])
  ax.axvline(vert_line_xcoord, linewidth=2)
  ax.invert_yaxis()
  # ax.set_aspect(0.006)
  ax.axis("off")

  return ax 


def get_fitted_count(tick, data, is_width_equal=True, with_drr=True):
  """tick is a one-dimensional integer or label for the value that we want to know
  its frequency.
  data is a one-dimensional numpy arra. This array represents the
  frequency of each tick values. We assume that the width
  is equal. We will implement in the future for non-uniform width"""
  width = tick[1] - tick[0]
  x_arr = np.concatenate([tick, [tick[-1] + width]]) - 0.5

  df_drr = pd.DataFrame()
  df_drr["tick"] = np.concatenate(
    [[tick[0] - width], tick, [tick[-1] + width]])
  df_drr["n"] = np.concatenate([[0], data, [0]])
  df_drr["cumul n"] = np.cumsum(df_drr["n"])
  df_drr["reverse cumul n"] = np.cumsum(df_drr["n"].iloc[::-1])[::-1]

  # -- Compute depth of median and depth of hinge
  N = df_drr["cumul n"].iloc[-1]
  d_M = (N + 1)/2
  d_H = int((int(d_M) + 1)/2)

  # -- find L such that (n_0 + ... + n_{L-1}) <= d(H) < n_L and compute H_L (lower hinge)
  L = 0
  for idx in range(1, len(df_drr)):
    if df_drr["cumul n"].iloc[idx-1] <= d_H < df_drr["cumul n"].iloc[idx]:
      L = idx
      break
  w_L = x_arr[L] - x_arr[L-1]
  H_L = x_arr[L-1] + (d_H - np.sum(df_drr["n"].iloc[:L]) - 0.5)*w_L/df_drr["n"].iloc[L]

  # -- find U such that n_U < d <= n_{U+1} + ... + n_{k+1} and compute H_U (upper hinge)
  U = len(df_drr) - 1
  for idx in range(len(df_drr)-1, 1, -1):
    if df_drr["reverse cumul n"].iloc[idx-1] > d_H >= df_drr["reverse cumul n"].iloc[idx]:
      U = idx-1
      break
  w_U = x_arr[U] - x_arr[U-1]
  H_U = x_arr[U] - (d_H - np.sum(df_drr["n"].iloc[U+1:]) - 0.5)*w_U/df_drr["n"].iloc[U]

  # -- Compute F((x_i - m)/s)
  m_mean = 0.5*(H_L + H_U)
  Delta_z = sc_stats.norm.ppf(.75) - sc_stats.norm.ppf(.25)
  s_std = (H_U - H_L)/Delta_z
  norm_cumul_x_arr = sc_stats.norm.cdf((x_arr - m_mean)/s_std)
  # norm_cumul_x_arr
  # print(H_L, H_U, m_mean, s_std)

  # -- Compute hat{n}_i
  df_drr["fitted n"] = np.concatenate([
    [N*norm_cumul_x_arr[0]],
    [N*(norm_cumul_x_arr[j] - norm_cumul_x_arr[j-1]) for j in range(1, len(norm_cumul_x_arr))],
    [N*(1. - norm_cumul_x_arr[-1])]
  ])

  if with_drr:
  # -- Compute DDR_i
    df_drr["DRR"] = [np.sqrt(2 + 4*df_drr["n"].iloc[j]) - np.sqrt(1 + 4*df_drr["fitted n"].iloc[j]) if np.abs(df_drr["n"].iloc[j]) > 1e-4 
                    else 1 - np.sqrt(1 + 4*df_drr["fitted n"].iloc[j]) 
                        for j in range(len(df_drr))] 

  # print(df_chest["Chest (in.)"].to_numpy())
  return df_drr


def plot_rootogram(tick, count, fitted_count, ax, xlabel="category",
              ylabel=r"$\sqrt{count}$", ylim=None, with_residual=True):
  residual_curve = np.sqrt(count) - np.sqrt(fitted_count)
  width = tick[1] - tick[0]
  ax.bar(tick, np.sqrt(count), bottom=-residual_curve, 
          width=width, linewidth=1, edgecolor="k")

  # x_gauss = np.linspace(-5*sigma+mu, mu+5*sigma, 100)
  # y_gauss = len(data_chest)*sc_stats.norm.pdf((x_gauss - mu)/sigma)/sigma
  # ax.plot(x_gauss, np.sqrt(y_gauss), linewidth=1.5, color="tab:orange",
  #         label="normal pdf")


  ax.plot(tick, np.sqrt(fitted_count), label="fitted $n$", 
          color="tab:green")

  ax.axhline(0, color="k", alpha=0.5, linestyle="--")
  # ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
  ax.set_ylim(ylim)
  ax.set_xlabel(xlabel)
  ax.set_ylabel(ylabel)

  ax.legend(loc="best")
  return None


def plot_suspended_rootogram(tick, count, fitted_count, ax, xlabel="category",
                              ylabel=r"$\sqrt{count}$", ylim=None):

  residual_curve = np.sqrt(count) - np.sqrt(fitted_count)
  width = tick[1] - tick[0]
  ax.bar(tick, np.sqrt(count), bottom=-residual_curve, width=width, 
          linewidth=1, edgecolor="k")

  # x_gauss = np.linspace(-5*sigma+mu, mu+5*sigma, 100)
  # y_gauss = len(data_chest)*sc_stats.norm.pdf((x_gauss - mu)/sigma)/sigma
  # ax.plot(x_gauss, np.sqrt(y_gauss), linewidth=1.5, color="tab:orange",
  #         label="normal pdf")

  ax.plot(tick, np.sqrt(fitted_count), label="fitted $n$", 
          color="tab:green")

  ax.axhline(0, color="k", alpha=0.5, linestyle="--")
  ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
  ax.set_ylim(ylim)
  ax.set_xlabel(xlabel)
  ax.set_ylabel(ylabel)
  ax.xaxis.set_label_position('top') 

  ax.invert_yaxis()

  # ax.legend(loc="best")
  return None


def plot_suspended_rootogram_res(tick, count, fitted_count, ax, 
                                  xlabel="category", 
                                  ylabel=r"$\sqrt{d_i} - \sqrt{\hat{d}_i}$", 
                                  ylim=None, xticks=None):

  w_arr = tick[1] - tick[0]
  x_arr = np.concatenate([tick, [tick[-1] + w_arr]]) - 0.5

  # -- (sqrt(n) - sqrt(fitted n)
  residual_curve = np.sqrt(count) - np.sqrt(fitted_count)
  ax.stairs(residual_curve, x_arr, linewidth=1.5, label=None)
  ax.axhline(0, color="k", linestyle="--", linewidth=1, alpha=0.5, label=None)

  # confidence interval
  ax.axhline(1./np.sqrt(w_arr), color="k", linestyle="--", linewidth=1, alpha=0.5, label="conf. interv.")
  ax.axhline(-1./np.sqrt(w_arr), color="k", linestyle="--", linewidth=1, alpha=0.5, label=None)

  ax.set_ylim(ylim)
  ax.set_ylabel(ylabel)
  ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
  ax.set_xlabel(xlabel)
  ax.xaxis.set_label_position('top') 
  
  if xticks is not None:
    ax.set_xticks(xticks)

  ax.legend(loc="best")

  return None