#Luke Torry 400368090

import numpy as np
import streamlit as st

from starter import COSTS, TIME_BLOCKS, ZONES, delivery_times


def calculate_late_cost(costs_dict):
  direct_refund = costs_dict["refund"]
  lost_profit = costs_dict["churn_orders"] * costs_dict["margin"]
  return direct_refund + lost_profit


def get_best_promise(zone, promises, time_block, costs_dict):
  cost_per_late_order = calculate_late_cost(costs_dict)
  profit_margin = costs_dict["margin"]

  best_promise = None
  max_net_profit = -float("inf")

  for promise in promises:
    times = delivery_times(zone, time_block, promise)
    total_orders = len(times)
    late_orders = (times > promise).sum()
    total_profit_collected = total_orders * profit_margin
    total_late_costs = late_orders * cost_per_late_order
    net_profit = total_profit_collected - total_late_costs

    if net_profit > max_net_profit:
      max_net_profit = net_profit
      best_promise = promise

  return best_promise, max_net_profit


st.set_page_config(page_title="Delivery Promise Optimizer", page_icon="📦")
st.title("Delivery Promise Optimizer")
st.write("Find the promised delivery time with the highest estimated net profit.")

zone = st.selectbox("Zone", ZONES)
time_block = st.selectbox("Time block", TIME_BLOCKS)

st.subheader("Promised-time range")
range_columns = st.columns(3)
with range_columns[0]:
  promise_start = st.number_input("Start", min_value=0.01, value=5.0, step=1.0)
with range_columns[1]:
  promise_end = st.number_input("End", value=60.0, step=1.0)
with range_columns[2]:
  promise_step = st.number_input("Step", min_value=0.01, value=5.0, step=1.0)

st.subheader("Cost assumptions")
cost_columns = st.columns(3)
with cost_columns[0]:
  margin = st.number_input(
    "Profit margin per order", min_value=0.0, value=float(COSTS["margin"]), step=1.0
  )
with cost_columns[1]:
  churn_orders = st.number_input(
    "Estimated churn orders", min_value=0.0, value=float(COSTS["churn_orders"]), step=0.1
  )
with cost_columns[2]:
  refund = st.number_input(
    "Refund cost per late order", min_value=0.0, value=float(COSTS["refund"]), step=1.0
  )

if st.button("Find best promised time", type="primary"):
  if promise_end < promise_start:
    st.error("End must be greater than or equal to start.")
  else:
    promise_count = int(np.floor((promise_end - promise_start) / promise_step + 1e-12)) + 1
    promises = promise_start + np.arange(promise_count) * promise_step
    costs = {"margin": margin, "churn_orders": churn_orders, "refund": refund}
    best_promise, net_profit = get_best_promise(zone, promises, time_block, costs)

    if best_promise is None:
      st.warning("No promised times could be evaluated for this selection.")
    else:
      st.success(f"Recommended promised time: {best_promise:g}")
      st.metric("Estimated net profit", f"${net_profit:,.2f}")