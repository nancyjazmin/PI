from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    emissions = None
    if request.method == 'POST':
        # Obtén los datos del formulario
        distance = float(request.form['distance'])
        fuel_efficiency = float(request.form['fuel_efficiency'])
        fuel_type = request.form['fuel_type']
        meat_consumption = float(request.form['meat_consumption'])
        lightbulbs = int(request.form['lightbulbs'])

        # Factores de emisión en kg CO2 por litro de combustible
        fuel_emission_factors = {
            'gasoline': 2.31,
            'diesel': 2.68,
            'electric': 0.0  # Para vehículos eléctricos
        }
        
        # Factores de emisión adicionales
        meat_emission_factor = 27  # kg CO2 por kg de carne (promedio)
        lightbulb_emission_factor = 0.42  # kg CO2 por foco por día (promedio)

        # Calcula las emisiones de CO2
        travel_emissions = (distance / fuel_efficiency) * fuel_emission_factors.get(fuel_type, 0)
        meat_emissions = meat_consumption * meat_emission_factor
        lightbulb_emissions = lightbulbs * lightbulb_emission_factor

        # Emisiones totales
        emissions = travel_emissions + meat_emissions + lightbulb_emissions

        return render_template('index.html', emissions=emissions)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
