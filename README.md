# Små-materiel Eftersynsrapport App

A Streamlit web application for generating equipment inspection reports for small machinery/materials (Små-materiel) at Nordic Maskin & Rail P/S.

## Features

- Interactive equipment inspection checklist
- PDF report generation with custom templates
- Visual status indicators (OK, Fejl, Ikke relevant)
- Equipment disposal tracking
- Danish language interface

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)

### Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/smaa-eftersyn-app.git
   cd smaa-eftersyn-app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Local Development
```bash
streamlit run smaa_eftersyn_app.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Network Sharing
To allow others on your network to access the app:
```bash
streamlit run smaa_eftersyn_app.py --server.headless true --server.address 0.0.0.0
```

### Deployment to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set the main file path to `smaa_eftersyn_app.py`
6. Click Deploy!

## File Structure

```
smaa-eftersyn-app/
├── smaa_eftersyn_app.py          # Main Streamlit application
├── requirements.txt              # Python dependencies
├── Små-materiel_eftersyn_template2.pdf  # PDF template
├── Green check mark.jpg          # OK status icon
├── Red X.jpg                     # Error status icon
├── Pink diamond.png              # Not relevant status icon
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Dependencies

- `streamlit` - Web app framework
- `PyMuPDF` (fitz) - PDF manipulation library

## Checklist Items

The app includes inspection checklists for:
- Mechanical parts
- Safety equipment
- Operating controls
- Hydraulics and pneumatics
- Chains and belts
- Lubrication and maintenance
- Brakes (if applicable)
- Oil level
- Unusual noises and vibrations
- Documentation in Trace Tool
- Label application (month and year)

## Equipment Information

The app captures:
- Company information (Nordic Maskin & Rail P/S)
- Equipment details (machine number, manufacturer, model, serial number, year)
- Technician name
- Inspection results
- Comments for failed items
- Disposal actions (if equipment is discarded)

## Output

Generated reports are saved as PDF files in the `Eftersynsrapporter/` directory with timestamps and equipment identifiers in the filename.

## Customization

### Adding New Checklist Items
Edit the `CHECK_ITEMS` list in `smaa_eftersyn_app.py`.

### Changing Icons
Replace the image files (`Green check mark.jpg`, `Red X.jpg`, `Pink diamond.png`) with your preferred icons.

### Modifying PDF Template
Replace `Små-materiel_eftersyn_template2.pdf` with your custom template. The app expects specific field names for PDF form filling.

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **PDF generation fails**
   - Check that the PDF template file exists and is not corrupted
   - Verify icon files are present

3. **Icons not displaying**
   - Ensure image files are in the same directory as the app
   - Check file permissions

4. **Port already in use**
   - Streamlit uses port 8501 by default. Use `--server.port` to specify a different port:
     ```bash
     streamlit run smaa_eftersyn_app.py --server.port 8502
     ```

### Windows-Specific Issues

- If you encounter encoding issues, ensure your terminal/command prompt uses UTF-8 encoding
- For network sharing on Windows, you may need to configure Windows Firewall

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary to Nordic Maskin & Rail P/S. All rights reserved.

## Support

For support or questions, contact the development team at Nordic Maskin & Rail P/S.