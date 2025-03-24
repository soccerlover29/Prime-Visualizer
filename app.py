from flask import Flask, render_template, request, redirect, url_for, flash
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)
app.secret_key = "some_secret_key"  # Needed for flashing error messages

def find_factors(num):
    """Return a list of all factors of num."""
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    return factors

def create_circle(n):
    """Create n points in a circle."""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [(np.cos(angle), np.sin(angle)) for angle in angles]

def get_best_factor_pair(n):
    """Find the factor pair (a, b) of n with the smallest |a - b|."""
    best_diff = n
    best_pair = (1, n)
    for d in range(2, int(np.sqrt(n)) + 1):
        if n % d == 0:
            a, b = d, n // d
            if abs(a - b) < best_diff:
                best_diff = abs(a - b)
                best_pair = (a, b)
    return (min(best_pair), max(best_pair))

def create_composite_shape(n):
    """Arrange n in groups based on the 'best' factor pair."""
    a, b = get_best_factor_pair(n)
    big_radius = 1.0
    small_radius = 0.3
    
    dots = []
    cluster_angles = np.linspace(0, 2 * np.pi, b, endpoint=False)
    for angle_c in cluster_angles:
        cx = big_radius * np.cos(angle_c)
        cy = big_radius * np.sin(angle_c)
        dot_angles = np.linspace(0, 2 * np.pi, a, endpoint=False)
        for angle_d in dot_angles:
            x = cx + small_radius * np.cos(angle_d)
            y = cy + small_radius * np.sin(angle_d)
            dots.append((x, y))
    return dots

def generate_plot(start, end):
    """Generates the matplotlib figure for numbers in range and returns it as a base64 string."""
    num_plots = end - start + 1
    cols = 3
    rows = (num_plots + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(9, 3 * rows))
    
    if rows == 1:
        axs = np.array(axs).reshape(-1)
    else:
        axs = np.array(axs).flatten()
    
    i = 0
    for n in range(start, end + 1):
        ax = axs[i]
        if n == 2:
            dots = [(0, 0)]
        elif n == 3:
            dots = [(0, 0), (1, 0), (0.5, 0.87)]
        elif n == 1:
            dots = [(0, 0)]  # Special case for 1
        else:
            factors = find_factors(n)
            if len(factors) == 2:  # Prime number
                dots = create_circle(n)
            else:  # Composite number
                dots = create_composite_shape(n)
        
        for (x, y) in dots:
            ax.scatter(x, y, s=50, alpha=0.8, color=np.random.rand(3,))
        ax.set_title(f'{n}', fontsize=12)
        ax.axis('equal')
        ax.axis('off')
        i += 1

    for j in range(i, len(axs)):
        axs[j].axis('off')
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    encoded = base64.b64encode(image_png).decode('utf-8')
    plt.close(fig)
    return encoded

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if "range" in request.form:
            range_input = request.form.get("range")
            try:
                start_str, end_str = range_input.split('-')
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start < 1 or end < 1 or start > end:
                    flash("Please enter a valid range (e.g., 5-10).")
                    return redirect(url_for('index'))
                image = generate_plot(start, end)
                return render_template("result.html", image=image)
            except Exception:
                flash("Please enter a valid range (e.g., 5-10).")
                return redirect(url_for('index'))
        
        if "single" in request.form:
            single_input = request.form.get("single")
            try:
                n = int(single_input.strip())
                if n < 1:
                    flash("Please enter a valid number (greater than 0).")
                    return redirect(url_for('index'))
                image = generate_plot(n, n)
                return render_template("result.html", image=image)
            except Exception:
                flash("Please enter a valid number.")
                return redirect(url_for('index'))
                
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
