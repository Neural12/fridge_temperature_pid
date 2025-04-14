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
time_steps = 1440  


P = 0.5
I = 0.1
D = 0.05


volume = 0.40  
density = 1.225  # Levegő sűrűsége (kg/m^3)
specific_heat = 1005  # Levegő specifikus hőkapacitása (J/kg°C)
mass = volume * density  # Hűtő tömege (kg)


pid = PIDController(P, I, D)


temperature = initial_temperature
temperatures = []
errors = []
outputs = []
energy_consumption = []  
door_openings = []  
external_temperature_changes = [] 
times = np.linspace(0, time_steps - 1, time_steps)


external_temperature_changes = np.sin(times / 10) * 5 + 25  # szinuszos változás a külső hőmérsékleten

# Ajtónyitás paraméterek
heat_gain_per_opening = 1.0  


derivative_errors = []  
integral_errors = []  

# Szimuláció
for t in range(time_steps):
    
    external_temp = external_temperature_changes[t]  
    
    
    door_opening_frequency = random.randint(1, 5)  # Napi ajtónyitások száma véletlenszerűen 1 és 5 között
    if random.random() < door_opening_frequency / time_steps:
        temperature += heat_gain_per_opening  
        door_openings.append(t)  
    
   
    control_output = pid.control(setpoint, temperature)

    # Külső hőmérséklet hatása a belső hőmérsékletre
    temperature += control_output - (temperature - external_temp) * 0.01 

    # Hiba és kimenet tárolása
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


# Egy ábrán ábrázolás (derivált, integrált hiba és PID kimenet)
plt.figure(figsize=(8, 6))

# Derivált hiba ábrázolása
plt.subplot(3, 1, 1)
plt.plot(times, derivative_errors, label="Derivált hiba", color='red')
plt.title(f"Derivált hiba időbeli alakulása (D={D})")
plt.xlabel("Idő (perc)")
plt.ylabel("Derivált hiba")
plt.grid(True)
plt.legend()

# Integrált hiba ábrázolása
plt.subplot(3, 1, 2)
plt.plot(times, integral_errors, label="Integrált hiba", color='blue')
plt.title(f"Integrált hiba időbeli alakulása (I={I})")
plt.xlabel("Idő (perc)")
plt.ylabel("Integrált hiba")
plt.grid(True)
plt.legend()

# PID kimenet ábrázolása
plt.subplot(3, 1, 3)
plt.plot(times, outputs, label="PID Kimenet", color='green')
plt.title(f"PID Kimenet (P={P})") 
plt.xlabel("Idő (percek)")
plt.ylabel("PID Kimenet")
plt.legend()

plt.tight_layout()
plt.show()




plt.figure(figsize=(8, 6))
plt.plot(times, temperatures, label="Hőmérséklet (valós)")
plt.axhline(y=setpoint, color='r', linestyle='--', label="Cél hőmérséklet")

# Minimum, maximum és átlag hőmérséklet meghatározása
min_temp = min(temperatures)
max_temp = max(temperatures)
avg_temp = np.mean(temperatures)

# Összenergiafogyasztás kiszámítása
# total_energy = sum(energy_consumption)

# Szöveg hozzáadása a grafikonhoz
plt.text(0.8 * max(times), min_temp + 2, 
         f"Min: {min_temp:.2f}°C\nMax: {max_temp:.2f}°C\nÁtlag: {avg_temp:.2f}°C\n", 
        #  Összenergia: {total_energy:.2f} Wh
         color='blue', fontsize=12)

plt.title("Hőmérséklet-változás")
plt.xlabel("Idő (percek)")
plt.ylabel("Hőmérséklet (°C)")
plt.legend()
plt.show()





# Hiba grafikon külön ablakban
plt.figure(figsize=(8, 6))
plt.plot(times, errors, label="Hiba (Cél - Valós)", color='orange')
plt.title("Hiba változása")
plt.xlabel("Idő (percek)")
plt.ylabel("Hiba (°C)")
plt.legend()
plt.show()



# Energiafogyasztás grafikon külön ablakban
plt.figure(figsize=(8, 6))
plt.plot(times, energy_consumption, label="Energiafogyasztás (Wh)")
plt.title(f"Energiafogyasztás változás ({total_energy_consumption:.2f} Wh/Nap)")
plt.xlabel("Idő (percek)")
plt.ylabel("Energiafogyasztás (Wh)")
plt.legend()
plt.show()

plt.figure(figsize=(12, 10))
plt.plot([total_energy_consumption] * time_steps, label="Összes energiafogyasztás")
plt.title(f"Összes energiafogyasztás: {total_energy_consumption:.2f} Wh")
plt.legend()
plt.show()

# Hőmérséklet grafikon külön ablakban, ajtónyitások utáni hőmérsékletkülönbséggel
plt.figure(figsize=(8, 6))
plt.plot(times, temperatures, label="Hőmérséklet (valós)")

# Ajtónyitások pontos időpontjainak ábrázolása szórt pontokkal
plt.scatter(door_openings, [temperatures[t] for t in door_openings], color='purple', label='Ajtónyitás', zorder=5)

# Cél hőmérséklet
plt.axhline(y=setpoint, color='r', linestyle='--', label="Cél hőmérséklet")

# Ajtónyitások után mennyi hőmérséklet-emelkedés történt
for i in range(len(door_openings) - 1):
    temp_increase = temperatures[door_openings[i + 1]] - temperatures[door_openings[i]]
    
    plt.text(door_openings[i], temperatures[door_openings[i]] + 0.5, f"+{temp_increase:.2f}°C", color='blue', fontsize=10)

plt.title("Hőmérséklet változás és ajtónyitások hatása")
plt.xlabel("Idő (percek)")
plt.ylabel("Hőmérséklet (°C)")
plt.legend()
plt.show()







# Energiafogyasztás grafikon, ajtónyitások utáni energiafogyasztás változásával
plt.figure(figsize=(8, 6))
plt.plot(times, energy_consumption, label="Energiafogyasztás (Wh)", color='orange')

plt.scatter(door_openings, [energy_consumption[t] for t in door_openings], color='purple', label='Ajtónyitás', zorder=5)

plt.axhline(y=setpoint, color='r', linestyle='--', label="Cél hőmérséklet")

for i in range(len(door_openings) - 1):
    energy_increase = energy_consumption[door_openings[i + 1]] - energy_consumption[door_openings[i]]
    
    plt.text(door_openings[i], energy_consumption[door_openings[i]] + 0.8, f"+{energy_increase:.2f} Wh", color='blue', fontsize=10)

plt.title("Energiafogyasztás és Ajtónyitások Hatása")
plt.xlabel("Idő (percek)")
plt.ylabel("Energiafogyasztás (Wh)")
plt.legend()
plt.show()






# Kiíratás a terminálba
print(f"Összes energiafogyasztás egy napra: {total_energy_consumption:.2f} Wh")
print(f"Átlagos energiafogyasztás: {average_energy_consumption:.2f} Wh")

print("Hőmérséklet változása (valós és cél hőmérséklet):")
for t in range(time_steps):
    print(f"Idő: {t+1} perc, Hőmérséklet: {temperatures[t]:.2f} °C, Cél hőmérséklet: {setpoint} °C, Különbség: {temperatures[t] - setpoint:.2f} °C")

print("\nHiba változása (Cél - Valós):")
for t in range(time_steps):
    print(f"Idő: {t+1} perc, Hiba: {errors[t]:.2f} °C")

print("\nPID kimenet változása:")
for t in range(time_steps):
    print(f"Idő: {t+1} perc, PID kimenet: {outputs[t]:.2f}")

print("\nEnergiafogyasztás változása (Wh):")
for t in range(time_steps):
    print(f"Idő: {t+1} perc, Energiafogyasztás: {energy_consumption[t]:.4f} Wh")

print(f"\nÖsszes energiafogyasztás egy napra: {total_energy_consumption:.2f} Wh")
print(f"Átlagos energiafogyasztás: {average_energy_consumption:.2f} Wh")

def simulate_scenarios():
    # Paraméterek, amelyeket változtatunk
    external_temps = [25, 30, 35]  # Külső hőmérsékletek
    volumes = [0.5, 1.0, 2.0]      # Hűtő űrtartalma

    energy_results = {}

    # Színek a három csoporthoz (1, 4, 7), (2, 5, 8), (3, 6, 9)
    colors = ['blue', 'green', 'red'] 

    for ext_temp in external_temps:
        for vol in volumes:
            # Új szimuláció minden paraméter kombinációra
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

    # Eredmények ábrázolása
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

    plt.title("Energiafogyasztás különböző paraméterekkel")
    plt.ylabel("Energiafogyasztás (Wh)")
    plt.xticks(rotation=25)
    plt.tight_layout()
    plt.show()

simulate_scenarios()
