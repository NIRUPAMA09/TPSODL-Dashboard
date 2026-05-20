# TPSODL GIS Arrear Dashboard

Interactive GIS-based arrear monitoring dashboard for utility corporations using:
- Flask
- Folium
- Heatmaps
- Smart Search
- Authentication
- Geospatial Analytics
- Customer Mapping
- Interactive Filters

# Live Features

✅ Interactive arrear heatmap  
✅ Smart search by account number  
✅ Dark mode / light mode GIS view  
✅ Login/logout authentication  
✅ CSV upload pipeline  
✅ Auto-zoom customer markers  
✅ Popup analytics windows  
✅ Region-wise arrear filtering  
✅ Responsive dashboard UI  
✅ Downloadable reports  

# Dashboard Preview

## Heatmap View
- Zoomed-out → only density heatmap
- Zoomed-in → customer markers appear automatically

## Smart Search
Search customer accounts like:
```text
acc_25
```
and auto-zoom directly to customer location.

# CSV Format

Upload CSV files in this format:

```csv
point_name,latitude,longitude,due_date,arrear_amount,status
acc_25,19.30549812,84.81856537,18-06-2022,10457,Pending
```

# Default Login Credentials

```text Instances
admin / admin123
officer1 / officer123
officer2 / officer456
```

# Technologies Used

- Python
- Flask
- Folium
- Pandas
- Waitress
- Gunicorn
- HTML/CSS
- JavaScript
- GIS Mapping
- Heatmap Visualization


# Local Setup

## 1. Clone Repository

```bash
git clone YOUR_REPO_LINK
```

## 2. Install Requirements
```bash
pip install -r requirements.txt
```

## 3. Run on Windows

```bash
python run_waitress.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# Deployment

Deployed using:

- Render
- Gunicorn
- Flask Production Server

# Core Functionalities

## GIS Heatmap Analytics

Visualize arrear concentration density across utility regions.

## Smart Customer Search

Locate account numbers instantly.

## Region Classification

Customers are automatically sorted into:

- North
- Central
- South

## Popup Analytics

Each customer marker shows:

- Due date
- Arrear amount
- Region
- Status
- Coordinates

# Future Enhancements

- PostgreSQL/PostGIS integration
- Outage-risk analytics
- Role-based admin access
- Division/subdivision polygon overlays
- Real-time feeder monitoring
- Mobile PWA support
-

# Developed For

Utility GIS analytics and arrear monitoring systems under data provided by TPSODL(Tata Power Southern Odisha Limited).

# Project Type

GIS + Analytics + Dashboard Engineering + Utility Tech
