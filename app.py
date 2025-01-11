from flask import Flask, request, jsonify, render_template, send_from_directory
from paddleocr import PaddleOCR
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize Flask app
app = Flask(__name__, 
    static_url_path='/static', 
    static_folder='static',
    template_folder='templates'
)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# File path for storing results
CSV_FILE = "market_prices.csv"

# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Product", "Price", "Date"]).to_csv(CSV_FILE, index=False)

# Ensure required directories exist
for directory in ['static', 'uploads', 'templates']:
    os.makedirs(directory, exist_ok=True)

def extract_text_from_image(image_path):
    """Extract text from the image using PaddleOCR."""
    ocr_result = ocr.ocr(image_path, cls=True)
    raw_text = " ".join([line[1][0] for line in ocr_result[0]])
    return raw_text

def parse_extracted_text(raw_text):
    """Parse the extracted text to get product names, prices, and dates."""
    # Split the text into lines
    lines = raw_text.split(" ")
    data = []
    today = datetime.now().strftime("%Y-%m-%d")  # Current date
    
    # Iterate through the lines and parse products and prices
    for i in range(len(lines)):
        try:
            # Product names are words; prices are numeric
            if lines[i].isalpha():
                product = lines[i]
                # Get the next numeric value as the price
                price = float(lines[i + 1].replace("Rs", "").replace(",", "").strip())
                data.append({"Product": product, "Price": price, "Date": today})
        except (ValueError, IndexError):
            continue  # Skip if no price is found or parsing fails

    return data

def update_csv(data, csv_file=CSV_FILE):
    """Update the CSV file with new data."""
    try:
        df_new = pd.DataFrame(data)
        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_updated = df_new
        df_updated.to_csv(csv_file, index=False)
        print(f"Successfully updated CSV with {len(data)} new entries")
    except Exception as e:
        print(f"Error updating CSV: {str(e)}")
        raise

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle image upload and text extraction."""
    print("\n=== Starting new upload ===")
    try:
        # Check if file is present in request
        if "image" not in request.files:
            print("No image file in request")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["image"]
        
        # Check if file is selected
        if file.filename == "":
            print("Empty filename")
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            print("Invalid file type")
            return jsonify({"error": "Invalid file type. Please upload an image file."}), 400

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        print(f"Upload directory: {upload_dir}")

        # Save the uploaded image with a unique filename
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = os.path.join(upload_dir, filename)
        print(f"Saving image to: {image_path}")
        file.save(image_path)

        try:
            # Extract text from image
            raw_text = extract_text_from_image(image_path)
            if not raw_text:
                print("No text detected in image")
                return jsonify({"error": "No text detected in image"}), 400

            # Parse the extracted text
            parsed_data = parse_extracted_text(raw_text)
            if not parsed_data:
                print("No valid prices detected")
                return jsonify({"error": "No valid prices detected"}), 400

            # Update CSV file
            update_csv(parsed_data)

            return jsonify({
                "success": True,
                "message": f"Successfully extracted {len(parsed_data)} prices",
                "data": parsed_data
            })

        finally:
            # Clean up the uploaded file
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Cleaned up temporary file: {image_path}")
            except Exception as e:
                print(f"Error cleaning up file: {str(e)}")

    except Exception as e:
        print(f"Error in upload route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analysis')
def get_analysis():
    """Get price analysis data."""
    try:
        df = pd.read_csv(CSV_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get latest prices
        latest_prices = df.sort_values('Date').groupby('Product').last()
        
        # Calculate price changes
        price_changes = []
        for product in df['Product'].unique():
            product_data = df[df['Product'] == product].sort_values('Date')
            if len(product_data) >= 2:
                old_price = product_data.iloc[-2]['Price']
                new_price = product_data.iloc[-1]['Price']
                change = ((new_price - old_price) / old_price) * 100
            else:
                change = 0
                
            price_changes.append({
                'product': product,
                'current_price': latest_prices.loc[product, 'Price'],
                'change_percentage': round(change, 2)
            })
            
        # Get market summary
        summary = {
            'total_products': len(df['Product'].unique()),
            'avg_price': round(df['Price'].mean(), 2),
            'price_trend': 'Up' if sum(p['change_percentage'] for p in price_changes) > 0 else 'Down',
            'last_updated': df['Date'].max().strftime('%Y-%m-%d')
        }
        
        return jsonify({
            "success": True,
            "data": {
                "price_changes": price_changes,
                "summary": summary
            }
        })
    except Exception as e:
        print(f"Error in price analysis: {str(e)}")
        return jsonify({"error": "Error getting analysis"}), 500

@app.route('/predict/<product>')
def get_prediction(product):
    """Get price predictions for a product."""
    try:
        df = pd.read_csv(CSV_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get product data, case-insensitive match
        product_data = df[df['Product'].str.lower() == product.lower()].sort_values('Date')
        
        # Check if we have enough data
        if len(product_data) < 2:
            print(f"Insufficient data for {product}")
            return jsonify({
                "error": f"Insufficient data for {product}. Need at least 2 data points."
            }), 400
            
        # Prepare data for prediction - convert to numpy array first
        date_nums = (product_data['Date'] - product_data['Date'].min()).dt.days
        X = np.array(date_nums).reshape(-1, 1)
        y = np.array(product_data['Price'].values)
        
        # Train model with some regularization
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future dates (next 7 days)
        last_date = product_data['Date'].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=7)
        future_X = np.array((future_dates - product_data['Date'].min()).days).reshape(-1, 1)
        
        # Make predictions
        predictions = model.predict(future_X)
        
        # Ensure predictions are non-negative and within reasonable bounds
        min_price = max(0, product_data['Price'].min() * 0.5)  # 50% of min historical price
        max_price = product_data['Price'].max() * 1.5  # 150% of max historical price
        predictions = np.clip(predictions, min_price, max_price)
        
        # Create figure with improved styling
        fig = go.Figure()
        
        # Add historical data with better styling
        fig.add_trace(go.Scatter(
            x=product_data['Date'],
            y=product_data['Price'],
            name='Historical',
            mode='lines+markers',
            line=dict(color='#3498db', width=2),
            marker=dict(size=8),
            hovertemplate='%{x}<br>Price: ₹%{y:.2f}<extra></extra>'
        ))
        
        # Add predictions with better styling
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions,
            name='Predicted',
            mode='lines+markers',
            line=dict(color='#2ecc71', width=2, dash='dash'),
            marker=dict(size=8),
            hovertemplate='%{x}<br>Predicted: ₹%{y:.2f}<extra></extra>'
        ))
        
        # Update layout with better styling
        fig.update_layout(
            title=dict(
                text=f'{product.title()} Price Trend and Prediction',
                font=dict(size=24)
            ),
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            showlegend=True,
            template='plotly_white',
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white"),
            margin=dict(l=20, r=20, t=60, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif"),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#f0f0f0',
                tickformat='%Y-%m-%d'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#f0f0f0',
                tickprefix='₹',
                tickformat='.2f'
            )
        )
        
        # Add confidence interval
        std_dev = np.std(product_data['Price'])
        upper_bound = predictions + std_dev
        lower_bound = predictions - std_dev
        
        # Clip confidence intervals
        upper_bound = np.clip(upper_bound, min_price, max_price)
        lower_bound = np.clip(lower_bound, min_price, max_price)
        
        # Add confidence intervals to plot
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=upper_bound,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=lower_bound,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(46, 204, 113, 0.2)',
            fill='tonexty',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Prepare prediction data with confidence intervals
        prediction_data = []
        for date, pred, upper, lower in zip(future_dates, predictions, upper_bound, lower_bound):
            prediction_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(float(pred), 2),
                'upper_bound': round(float(upper), 2),
                'lower_bound': round(float(lower), 2)
            })
        
        # Calculate trend indicators
        current_price = product_data['Price'].iloc[-1]
        avg_prediction = np.mean(predictions)
        trend = 'Up' if avg_prediction > current_price else 'Down'
        change_percent = ((avg_prediction - current_price) / current_price) * 100
        
        return jsonify({
            "success": True,
            "data": {
                "predictions": prediction_data,
                "plot": fig.to_json(),
                "trend": {
                    "direction": trend,
                    "change_percent": round(change_percent, 2),
                    "current_price": round(float(current_price), 2),
                    "predicted_avg": round(float(avg_prediction), 2)
                }
            }
        })
    except Exception as e:
        print(f"Error in price prediction: {str(e)}")
        return jsonify({
            "error": f"Error generating prediction: {str(e)}"
        }), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
