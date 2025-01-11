# Market Price Scanner - भारतीय बाजार मूल्य स्कैनर

A Flask-based web application that uses PaddleOCR to detect and extract prices from images of market boards in multiple Indian languages.

## Features

- 🔍 Real-time price detection from images
- 🌐 Support for 10 Indian languages:
  - English
  - Hindi (हिंदी)
  - Marathi (मराठी)
  - Gujarati (ગુજરાતી)
  - Punjabi (ਪੰਜਾਬੀ)
  - Bengali (বাংলা)
  - Tamil (தமிழ்)
  - Telugu (తెలుగు)
  - Kannada (ಕನ್ನಡ)
  - Malayalam (മലയാളം)
- 📱 Mobile-friendly interface with camera support
- 📊 Historical price tracking with CSV storage
- 🖼️ Drag-and-drop image upload
- 📝 Raw text extraction display

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Hackaton_Frint
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload an image using one of these methods:
   - Drag and drop an image onto the upload area
   - Click the upload area to select a file
   - Use the "Take Photo" button to capture using your device's camera

4. Select your preferred language from the dropdown menu

5. View the results:
   - Detected prices will be displayed in a list format
   - Raw extracted text is shown below the prices
   - Historical data is stored in `market_prices.csv`

## Project Structure

```
Hackaton_Frint/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── market_prices.csv   # Historical price data
├── uploads/           # Temporary image storage
└── templates/
    └── index.html     # Frontend interface
```

## Dependencies

- Python 3.8+
- Flask 2.3.3
- PaddleOCR 2.9.1
- PaddlePaddle 2.5.1
- NumPy 1.26.4
- Pandas
- Other dependencies listed in requirements.txt

## Data Storage

The application stores detected prices in `market_prices.csv` with the following format:
- Product: Name of the item
- Price: Detected price in INR
- Date: Date of detection (YYYY-MM-DD)

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile browsers with camera support

## Contributing

Feel free to open issues and pull requests for:
- Adding support for more languages
- Improving price detection accuracy
- Enhancing the user interface
- Adding new features

## License

[Your License Here]
