#!/usr/bin/env python3
"""
Generate visualizations for ReliQuary benchmark results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Read the benchmark data
with open('sequential_benchmark_results.json', 'r') as f:
    sequential_data = json.load(f)

with open('concurrent_benchmark_results.json', 'r') as f:
    concurrent_data = json.load(f)

# Extract data for plotting
endpoints = list(sequential_data.keys())
sequential_avg_times = [sequential_data[ep]['avg_response_time'] for ep in endpoints]
concurrent_avg_times = [concurrent_data[ep]['avg_response_time'] for ep in endpoints]
success_rates = [sequential_data[ep]['success_rate'] for ep in endpoints]

# Filter out endpoints with 0% success rate
valid_endpoints = [ep for ep, rate in zip(endpoints, success_rates) if rate > 0]
valid_sequential_times = [time for ep, time in zip(endpoints, sequential_avg_times) if sequential_data[ep]['success_rate'] > 0]
valid_concurrent_times = [time for ep, time in zip(endpoints, concurrent_avg_times) if sequential_data[ep]['success_rate'] > 0]

# Create comparison bar chart
plt.figure(figsize=(12, 6))
x = np.arange(len(valid_endpoints))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, valid_sequential_times, width, label='Sequential', alpha=0.8)
bars2 = ax.bar(x + width/2, valid_concurrent_times, width, label='Concurrent', alpha=0.8)

ax.set_xlabel('Endpoints')
ax.set_ylabel('Average Response Time (ms)')
ax.set_title('ReliQuary Performance: Sequential vs Concurrent Requests')
ax.set_xticks(x)
ax.set_xticklabels(valid_endpoints, rotation=45, ha='right')
ax.legend()

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

plt.tight_layout()
plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Create detailed sequential performance chart
plt.figure(figsize=(12, 8))

# Box plot for response time distribution
fig, ax = plt.subplots(figsize=(12, 8))

# Prepare data for box plot (only valid endpoints)
valid_sequential_data = [sequential_data[ep]['times'] for ep in valid_endpoints]
valid_concurrent_data = [concurrent_data[ep]['times'] for ep in valid_endpoints]

# Create box plots
box_data = []
labels = []
for i, ep in enumerate(valid_endpoints):
    box_data.append(valid_sequential_data[i])
    labels.append(f"{ep}\n(Seq)")
    box_data.append(valid_concurrent_data[i])
    labels.append(f"{ep}\n(Conc)")

box_plot = ax.boxplot(box_data, labels=labels, patch_artist=True)
ax.set_ylabel('Response Time (ms)')
ax.set_title('Response Time Distribution: Sequential vs Concurrent')
ax.tick_params(axis='x', rotation=45)

# Color the boxes
colors = ['lightblue', 'lightcoral'] * len(valid_endpoints)
for patch, color in zip(box_plot['boxes'], colors):
    patch.set_facecolor(color)

plt.tight_layout()
plt.savefig('response_time_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Create success rate chart
plt.figure(figsize=(10, 6))
valid_success_rates = [sequential_data[ep]['success_rate'] for ep in valid_endpoints]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(valid_endpoints, valid_success_rates, color='green', alpha=0.7)

ax.set_xlabel('Endpoints')
ax.set_ylabel('Success Rate (%)')
ax.set_title('ReliQuary Success Rates by Endpoint')
ax.set_ylim(0, 100)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('success_rates.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations generated successfully!")
print("- performance_comparison.png: Sequential vs Concurrent performance")
print("- response_time_distribution.png: Detailed response time distributions")
print("- success_rates.png: Success rates by endpoint")