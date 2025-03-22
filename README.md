# WhatsApp Chat Analyzer

A Streamlit-based web application that analyzes WhatsApp chat data and provides various insights including message statistics, activity patterns, word clouds, and emoji analysis.

## Features

- 📊 Message Statistics
  - Total messages count
  - Total words count
  - Media shared count
  - Links shared count

- 📈 Timeline Analysis
  - Monthly message timeline
  - Daily message timeline
  - Weekly activity map
  - Monthly activity map

- 👥 User Analysis
  - Most active users
  - User-wise message distribution
  - Activity heatmap

- 📝 Content Analysis
  - Word cloud generation
  - Most common words
  - Emoji usage analysis

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/anil-02k/whatsapp_chat_analyser.git
cd whatsapp_chat_analyser
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Export your WhatsApp chat:
   - Open WhatsApp
   - Go to the chat you want to analyze
   - Click the three dots menu (⋮)
   - Select "More" > "Export chat"
   - Choose "Without media"
   - Make sure "Include date" is selected
   - Save the exported file

2. Run the application:
```bash
streamlit run app.py
```

3. Open your web browser and go to the URL shown in the terminal (usually http://localhost:8501)

4. Upload your exported WhatsApp chat file using the file uploader in the sidebar

5. Select a user from the dropdown menu to analyze their messages, or choose "Overall" for group analysis

6. Click "Show Analysis" to view the insights

## Project Structure

```
whatsapp_chat_analyser/
├── app.py              # Main Streamlit application
├── helper.py           # Helper functions for data analysis
├── preprocessor.py     # WhatsApp chat data preprocessing
├── stop_hinglish.txt   # Stop words for word cloud
└── requirements.txt    # Python package dependencies
```

## Dependencies

- streamlit
- pandas
- matplotlib
- seaborn
- wordcloud
- emoji
- urlextract

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Anil Kumar
- GitHub: [anil-02k](https://github.com/anil-02k)
