from flask import Flask, request, jsonify, render_template
import numpy as np
from scipy.fft import fft

app = Flask(__name__, template_folder='template')

# Function to calculate fault frequencies
def calculate_frequencies(nb, rpm):
    bpfo = 0.4 * nb * rpm
    bpfi = 0.6 * nb * rpm
    bsf = 0.2 * nb * rpm
    ftf = 0.4 * rpm
    return bpfo, bpfi, bsf, ftf

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/fault', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form input data
            rpm = float(request.form['load'])
            vibration_data = list(map(float, request.form['temperature'].split()))

            # Set number of balls
            nb = 8

            # Calculate fault frequencies
            bpfo, bpfi, bsf, ftf = calculate_frequencies(nb, rpm)

            # Perform FFT on the vibration magnitude data
            vibration_magnitude = np.sqrt(np.array(vibration_data) ** 2)
            fft_values = fft(vibration_magnitude)
            frequencies = np.fft.fftfreq(len(fft_values))

            # Compare with calculated fault frequencies
            fault_frequencies = [bpfo, bpfi, bsf, ftf]
            print(f"Calculated Fault Frequencies: BPFO={bpfo} Hz, BPFI={bpfi} Hz, BSF={bsf} Hz, FTF={ftf} Hz")

            # Check for matching frequencies in FFT results
            threshold = 50  # Example threshold
            detected_faults = []

            for ff in fault_frequencies:
                if any(abs(ff - freq) < threshold for freq in frequencies):
                    if ff == bpfo:
                        detected_faults.append("Outer Race Fault")
                    elif ff == bpfi:
                        detected_faults.append("Inner Race Fault")
                    elif ff == bsf:
                        detected_faults.append("Ball Fault")
                    elif ff == ftf:
                        detected_faults.append("Cage Fault")

            if detected_faults:
                faults = ', '.join(detected_faults)
            else:
                faults = "No faults detected."

            return render_template('result.html', faults=faults)
        except Exception as e:
            return jsonify({'message': f'Error processing data: {e}'}), 500

    return render_template('predict.html')

@app.route('/trends')
def trends():
    return "Performance Trends Page"  # Placeholder

if __name__ == '__main__':
    app.run(debug=True)
