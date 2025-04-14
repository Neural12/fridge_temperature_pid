import numpy as np
import matplotlib.pyplot as plt
import random

class PIDController:
    def __init__(self, P, I, D):
        self.Kp = P  
        self.Ki = I 
        self.Kd = D  

        self.prev_error = 0
        self.integral = 0

    def control(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.prev_error

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.prev_error = error

        return output

setpoint = 5  
initial_temperature = 15  
external_temperature = 25  
time_steps = 1440  # Number of minutes in a day

P = 0.5
I = 0.1
D = 0.05

volume = 0.40  
density = 1.225  # Air density (kg/m^3)
specific_heat = 1005  # Air specific heat capacity (J/kg°C)
mass = volume * density  # Fridge air mass (kg)

pid = PIDController(P, I, D)

temperature = initial_temperature
temperatures = []
errors = []
outputs = []
energy_consumption = []  
door_openings = []  
external_temperature_changes = [] 
times = np.linspace(0, time_steps - 1, time_steps)

external_temperature_changes = np.sin(times / 10) * 5 + 25  # Sinusoidal change in external temperature

# Door opening parameters
heat_gain_per_opening = 1.0  

derivative_errors = []  
integral_errors = []  

# Simulation
for t in range(time_steps):
    
    external_temp = external_temperature_changes[t]  
    
    # Random number of door openings per day: 1 to 5
    door_opening_frequency = random.randint(1, 5)  
    if random.random() < door_opening_frequency / time_steps:
        temperature += heat_gain_per_opening  
        door_openings.append(t)  
    
    control_output = pid.control(setpoint, temperature)

    # Effect of external temperature on internal temperature
    temperature += control_output - (temperature - external_temp) * 0.01 

    # Store error and output
    temperatures.append(temperature)
    errors.append(setpoint - temperature)
    outputs.append(control_output)

    derivative_errors.append(pid.prev_error - errors[-1]) 
    integral_errors.append(pid.integral)  

    temp_difference = temperature - setpoint  
    external_temp_difference = external_temp - setpoint  
    
    if temp_difference > 0:  
        cooling_power = temp_difference * 10 * volume 
        cooling_power += external_temp_difference * 7 * volume 
        cooling_power = max(cooling_power, 0)  
    else:
        cooling_power = 0  

    energy_consumption.append(cooling_power * (1/3600))  
    
    delta_T = cooling_power * (1/3600) / (mass * specific_heat)  
    temperature -= delta_T  

total_energy_consumption = np.sum(energy_consumption)
average_energy_consumption = np.mean(energy_consumption)

# Plot: derivative, integral error and PID output
plt.figure(figsize=(8, 6))

# Derivative error
plt.subplot(3, 1, 1)
plt.plot(times, derivative_errors, label="Derivative Error", color='red')
plt.title(f"Derivative Error Over Time (D={D})")
plt.xlabel("Time (minutes)")
plt.ylabel("Derivative Error")
plt.grid(True)
plt.legend()

# Integral error
plt.subplot(3, 1, 2)
plt.plot(times, integral_errors, label="Integral Error", color='blue')
plt.title(f"Integral Error Over Time (I={I})")
plt.xlabel("Time (minutes)")
plt.ylabel("Integral Error")
plt.grid(True)
plt.legend()

# PID Output
plt.subplot(3, 1, 3)
plt.plot(times, outputs, label="PID Output", color='green')
plt.title(f"PID Output (P={P})") 
plt.xlabel("Time (minutes)")
plt.ylabel("PID Output")
plt.legend()

plt.tight_layout()
plt.show()

# Temperature chart
plt.figure(figsize=(8, 6))
plt.plot(times, temperatures, label="Temperature (actual)")
plt.axhline(y=setpoint, color='r', linestyle='--', label="Target Temperature")

# Determine min, max, and average temperatures
min_temp = min(temperatures)
max_temp = max(temperatures)
avg_temp = np.mean(temperatures)

# Add text to chart
plt.text(0.8 * max(times), min_temp + 2, 
         f"Min: {min_temp:.2f}°C\nMax: {max_temp:.2f}°C\nAvg: {avg_temp:.2f}°C\n", 
         color='blue', fontsize=12)

plt.title("Temperature Variation")
plt.xlabel("Time (minutes)")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.show()

# Error chart
plt.figure(figsize=(8, 6))
plt.plot(times, errors, label="Error (Target - Actual)", color='orange')
plt.title("Error Over Time")
plt.xlabel("Time (minutes)")
plt.ylabel("Error (°C)")
plt.legend()
plt.show()

# Energy consumption chart
plt.figure(figsize=(8, 6))
plt.plot(times, energy_consumption, label="Energy Consumption (Wh)")
plt.title(f"Energy Consumption Over Time ({total_energy_consumption:.2f} Wh/day)")
plt.xlabel("Time (minutes)")
plt.ylabel("Energy Consumption (Wh)")
plt.legend()
plt.show()

plt.figure(figsize=(12, 10))
plt.plot([total_energy_consumption] * time_steps, label="Total Energy Consumption")
plt.title(f"Total Energy Consumption: {total_energy_consumption:.2f} Wh")
plt.legend()
plt.show()

# Temperature chart with door openings
plt.figure(figsize=(8, 6))
plt.plot(times, temperatures, label="Temperature (actual)")

plt.scatter(door_openings, [temperatures[t] for t in door_openings], color='purple', label='Door Opening', zorder=5)
plt.axhline(y=setpoint, color='r', linestyle='--', label="Target Temperature")

# Show temperature increases after door openings
for i in range(len(door_openings) - 1):
    temp_increase = temperatures[door_openings[i + 1]] - temperatures[door_openings[i]]
    plt.text(door_openings[i], temperatures[door_openings[i]] + 0.5, f"+{temp_increase:.2f}°C", color='blue', fontsize=10)

plt.title("Temperature Change and Impact of Door Openings")
plt.xlabel("Time (minutes)")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.show()

# Energy consumption chart with door opening impacts
plt.figure(figsize=(8, 6))
plt.plot(times, energy_consumption, label="Energy Consumption (Wh)", color='orange')

plt.scatter(door_openings, [energy_consumption[t] for t in door_openings], color='purple', label='Door Opening', zorder=5)
plt.axhline(y=setpoint, color='r', linestyle='--', label="Target Temperature")

for i in range(len(door_openings) - 1):
    energy_increase = energy_consumption[door_openings[i + 1]] - energy_consumption[door_openings[i]]
    plt.text(door_openings[i], energy_consumption[door_openings[i]] + 0.8, f"+{energy_increase:.2f} Wh", color='blue', fontsize=10)

plt.title("Energy Consumption and Door Opening Impact")
plt.xlabel("Time (minutes)")
plt.ylabel("Energy Consumption (Wh)")
plt.legend()
plt.show()

# Console output
print(f"Total daily energy consumption: {total_energy_consumption:.2f} Wh")
print(f"Average energy consumption: {average_energy_consumption:.2f} Wh")

print("Temperature changes (actual vs target):")
for t in range(time_steps):
    print(f"Time: {t+1} min, Temp: {temperatures[t]:.2f} °C, Target: {setpoint} °C, Diff: {temperatures[t] - setpoint:.2f} °C")

print("\nError over time (Target - Actual):")
for t in range(time_steps):
    print(f"Time: {t+1} min, Error: {errors[t]:.2f} °C")

print("\nPID Output over time:")
for t in range(time_steps):
    print(f"Time: {t+1} min, PID Output: {outputs[t]:.2f}")

print("\nEnergy consumption over time (Wh):")
for t in range(time_steps):
    print(f"Time: {t+1} min, Energy: {energy_consumption[t]:.4f} Wh")

print(f"\nTotal daily energy consumption: {total_energy_consumption:.2f} Wh")
print(f"Average energy consumption: {average_energy_consumption:.2f} Wh")

def simulate_scenarios():
    # Parameters to vary
    external_temps = [25, 30, 35]  # External temperatures
    volumes = [0.5, 1.0, 2.0]      # Fridge volumes

    energy_results = {}

    # Color scheme for groups
    colors = ['blue', 'green', 'red'] 

    for ext_temp in external_temps:
        for vol in volumes:
            # New simulation for each parameter combination
            pid = PIDController(P, I, D)
            temperature = setpoint  
            total_energy = 0
            energy_per_step = []
            
            for t in range(time_steps):
                control_output = pid.control(setpoint, temperature)  
                temperature += control_output - (temperature - ext_temp) * 0.01  
                
                temp_diff = temperature - setpoint  
                if temp_diff > 0:
                    cooling_power = temp_diff * 10 * vol
                    cooling_power = max(cooling_power, 0)
                else:
                    cooling_power = 0

                energy_per_step.append(cooling_power * (1 / 3600))  
                total_energy += np.sum(energy_per_step)  
                
            energy_results[(ext_temp, vol)] = total_energy

    # Plot results
    plt.figure(figsize=(10, 8))
    
    for i, ((ext_temp, vol), energy) in enumerate(energy_results.items()):
        if i % 3 == 0:
            color = 'blue'    
        elif i % 3 == 1:
            color = 'green'  
        else:
            color = 'red'

        label = f"{ext_temp}°C, V: {vol}m³"
        bar = plt.bar(label, energy, color=color)

        for rect in bar:
            plt.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), f"{energy:.2f} Wh",
                     ha='center', va='bottom', fontsize=9, color='black')

    plt.title("Energy Consumption for Various Parameters")
    plt.ylabel("Energy Consumption (Wh)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.show()

simulate_scenarios()
