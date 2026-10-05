import logging
import time
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional, Any
import urllib.request
import urllib.parse
import json

from app.schemas.weather import WeatherData

logger = logging.getLogger("agripulse.services.weather")

# India Meteorological Department (IMD) Normal Annual Rainfall (mm) & Approximate Coordinates
# Based on IMD Long Period Averages (LPA) and District Agro-Climatic profiles
DISTRICT_CLIMATE_DATABASE: Dict[str, Dict[str, Tuple[float, float, float]]] = {
    # State -> { District: (Latitude, Longitude, Normal Annual Rainfall in mm) }
    "Andhra Pradesh": {
        "Anantapur": (14.6819, 77.6006, 560.0),
        "Chittoor": (13.2172, 79.1003, 934.0),
        "East Godavari": (16.9891, 82.2475, 1210.0),
        "Guntur": (16.3067, 80.4365, 876.0),
        "Kadapa": (14.4673, 78.8242, 700.0),
        "Krishna": (16.1809, 81.1303, 1030.0),
        "Kurnool": (15.8281, 78.0373, 670.0),
        "Nellore": (14.4426, 79.9865, 1080.0),
        "Prakasam": (15.5057, 80.0499, 830.0),
        "Srikakulam": (18.2949, 83.8938, 1140.0),
        "Visakhapatnam": (17.6868, 83.2185, 1200.0),
        "Vizianagaram": (18.1067, 83.3956, 1130.0),
        "West Godavari": (16.7107, 81.0952, 1150.0),
    },
    "Arunachal Pradesh": {
        "Changlang": (27.1350, 95.7360, 2600.0),
        "East Kameng": (27.3200, 93.0300, 2400.0),
        "East Siang": (28.0667, 95.3333, 3500.0),
        "Lohit": (27.8000, 96.1667, 2800.0),
        "Papum Pare": (27.1200, 93.6200, 2900.0),
        "Tawang": (27.5861, 91.8594, 1800.0),
        "West Kameng": (27.2600, 92.4200, 2200.0),
        "West Siang": (28.1667, 94.7500, 3100.0),
    },
    "Assam": {
        "Baksa": (26.6500, 91.5900, 2200.0),
        "Barpeta": (26.3200, 91.0000, 2100.0),
        "Cachar": (24.8333, 92.8000, 3100.0),
        "Darrang": (26.4500, 92.0300, 2000.0),
        "Dibrugarh": (27.4728, 94.9120, 2750.0),
        "Goalpara": (26.1800, 90.6200, 2400.0),
        "Golaghat": (26.5200, 93.9700, 2150.0),
        "Jorhat": (26.7509, 94.2037, 2050.0),
        "Kamrup": (26.3100, 91.6000, 1850.0),
        "Kamrup Metropolitan": (26.1445, 91.7362, 1800.0),
        "Karbi Anglong": (26.0000, 93.5000, 1600.0),
        "Karimganj": (24.8700, 92.3500, 3200.0),
        "Kokrajhar": (26.4000, 90.2700, 2800.0),
        "Lakhimpur": (27.2300, 94.1000, 3100.0),
        "Nagaon": (26.3500, 92.6800, 1750.0),
        "Nalbari": (26.4400, 91.4400, 2100.0),
        "Sivasagar": (26.9826, 94.6300, 2300.0),
        "Sonitpur": (26.6300, 92.8000, 2100.0),
        "Tinsukia": (27.5000, 95.3667, 2850.0),
    },
    "Bihar": {
        "Araria": (26.1500, 87.5200, 1400.0),
        "Aurangabad": (24.7500, 84.3700, 1050.0),
        "Begusarai": (25.4200, 86.1300, 1180.0),
        "Bhagalpur": (25.2500, 87.0000, 1190.0),
        "Bhojpur": (25.5600, 84.6600, 1020.0),
        "Darbhanga": (26.1700, 85.9000, 1220.0),
        "East Champaran": (26.6500, 84.9200, 1320.0),
        "Gaya": (24.7955, 85.0002, 1080.0),
        "Gopalganj": (26.4700, 84.4400, 1150.0),
        "Katihar": (25.5300, 87.5800, 1300.0),
        "Madhubani": (26.3500, 86.0800, 1250.0),
        "Muzaffarpur": (26.1209, 85.3647, 1200.0),
        "Nalanda": (25.2000, 85.5200, 1060.0),
        "Patna": (25.5941, 85.1376, 1100.0),
        "Purnia": (25.7800, 87.4700, 1380.0),
        "Rohtas": (24.9500, 84.0200, 1020.0),
        "Samastipur": (25.8600, 85.7800, 1190.0),
        "Saran": (25.7800, 84.7500, 1100.0),
        "Siwan": (26.2200, 84.3600, 1080.0),
        "Vaishali": (25.6800, 85.2200, 1150.0),
        "West Champaran": (27.1500, 84.4700, 1450.0),
    },
    "Chhattisgarh": {
        "Bastar": (19.0700, 81.9600, 1450.0),
        "Bilaspur": (22.0797, 82.1409, 1280.0),
        "Dantewada": (18.9000, 81.3500, 1500.0),
        "Durg": (21.1900, 81.2800, 1220.0),
        "Janjgir-Champa": (22.0100, 82.5700, 1300.0),
        "Kanker": (20.2700, 81.4900, 1380.0),
        "Korba": (22.3500, 82.6800, 1350.0),
        "Raigarh": (21.9000, 83.4000, 1400.0),
        "Raipur": (21.2514, 81.6296, 1320.0),
        "Rajnandgaon": (21.1000, 81.0300, 1250.0),
        "Surguja": (23.1200, 83.2000, 1420.0),
    },
    "Goa": {
        "North Goa": (15.4989, 73.8278, 3000.0),
        "South Goa": (15.2832, 73.9862, 3100.0),
    },
    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714, 750.0),
        "Amreli": (21.6000, 71.2200, 620.0),
        "Anand": (22.5645, 72.9289, 820.0),
        "Banaskantha": (24.1700, 72.4300, 600.0),
        "Bharuch": (21.7051, 72.9959, 900.0),
        "Bhavnagar": (21.7645, 72.1519, 650.0),
        "Dang": (20.8300, 73.6800, 1900.0),
        "Gandhinagar": (23.2156, 72.6369, 780.0),
        "Jamnagar": (22.4707, 70.0577, 580.0),
        "Junagadh": (21.5222, 70.4579, 850.0),
        "Kheda": (22.7500, 72.6800, 810.0),
        "Kutch": (23.2420, 69.6669, 380.0),
        "Mehsana": (23.5880, 72.3693, 680.0),
        "Navsari": (20.9467, 72.9520, 1400.0),
        "Patan": (23.8500, 72.1200, 550.0),
        "Porbandar": (21.6417, 69.6293, 680.0),
        "Rajkot": (22.3039, 70.8022, 600.0),
        "Sabarkantha": (23.5400, 72.9800, 750.0),
        "Surat": (21.1702, 72.8311, 1200.0),
        "Surendranagar": (22.7200, 71.6400, 520.0),
        "Vadodara": (22.3072, 73.1812, 930.0),
        "Valsad": (20.6100, 72.9300, 1850.0),
    },
    "Haryana": {
        "Ambala": (30.3782, 76.7767, 950.0),
        "Bhiwani": (28.7800, 76.1300, 420.0),
        "Faridabad": (28.4089, 77.3178, 650.0),
        "Gurugram": (28.4595, 77.0266, 620.0),
        "Hisar": (29.1492, 75.7217, 430.0),
        "Jhajjar": (28.6100, 76.6500, 520.0),
        "Jind": (29.3200, 76.3200, 510.0),
        "Karnal": (29.6857, 76.9905, 720.0),
        "Kurukshetra": (29.9695, 76.8783, 760.0),
        "Panipat": (29.3909, 76.9635, 630.0),
        "Rohtak": (28.8955, 76.6066, 550.0),
        "Sirsa": (29.5300, 75.0300, 320.0),
        "Sonipat": (28.9931, 77.0151, 620.0),
        "Yamunanagar": (30.1290, 77.2674, 1050.0),
    },
    "Himachal Pradesh": {
        "Bilaspur": (31.3300, 76.7600, 1250.0),
        "Chamba": (32.5500, 76.1200, 1400.0),
        "Hamirpur": (31.6800, 76.5200, 1300.0),
        "Kangra": (32.1000, 76.2700, 1950.0),
        "Kullu": (31.9579, 77.1095, 1100.0),
        "Mandi": (31.7087, 76.9320, 1450.0),
        "Shimla": (31.1048, 77.1734, 1380.0),
        "Sirmaur": (30.5500, 77.3000, 1550.0),
        "Solan": (30.9045, 77.0967, 1320.0),
        "Una": (31.4700, 76.2700, 1150.0),
    },
    "Jharkhand": {
        "Bokaro": (23.6700, 86.1500, 1320.0),
        "Dhanbad": (23.7957, 86.4304, 1300.0),
        "Dumka": (24.2600, 87.2500, 1400.0),
        "East Singhbhum": (22.8000, 86.2000, 1450.0),
        "Hazaribagh": (23.9800, 85.3500, 1250.0),
        "Palamu": (24.0300, 84.0700, 1150.0),
        "Ranchi": (23.3441, 85.3096, 1390.0),
        "West Singhbhum": (22.5700, 85.8000, 1420.0),
    },
    "Karnataka": {
        "Bagalkot": (16.1800, 75.7000, 560.0),
        "Ballari": (15.1394, 76.9214, 610.0),
        "Belagavi": (15.8497, 74.4977, 1150.0),
        "Bengaluru Rural": (13.2200, 77.5800, 880.0),
        "Bengaluru Urban": (12.9716, 77.5946, 920.0),
        "Bidar": (17.9100, 77.5200, 850.0),
        "Chamarajanagar": (11.9200, 76.9400, 760.0),
        "Chikkaballapur": (13.4300, 77.7300, 740.0),
        "Chikkamagaluru": (13.3161, 75.7720, 1850.0),
        "Chitradurga": (14.2300, 76.4000, 570.0),
        "Dakshina Kannada": (12.8700, 75.0000, 3950.0),
        "Davanagere": (14.4644, 75.9218, 650.0),
        "Dharwad": (15.4589, 75.0078, 770.0),
        "Gadag": (15.4300, 75.6300, 610.0),
        "Hassan": (13.0072, 76.1032, 1050.0),
        "Haveri": (14.8000, 75.4000, 750.0),
        "Kalaburagi": (17.3297, 76.8343, 780.0),
        "Kodagu": (12.3375, 75.8069, 2750.0),
        "Kolar": (13.1367, 78.1291, 740.0),
        "Koppal": (15.3500, 76.1500, 580.0),
        "Mandya": (12.5200, 76.9000, 700.0),
        "Mysuru": (12.2958, 76.6394, 780.0),
        "Raichur": (16.2000, 77.3500, 620.0),
        "Ramanagara": (12.7200, 77.2800, 830.0),
        "Shivamogga": (13.9299, 75.5681, 1800.0),
        "Tumakuru": (13.3409, 77.1010, 690.0),
        "Udupi": (13.3409, 74.7421, 4100.0),
        "Uttara Kannada": (14.8000, 74.5000, 2800.0),
        "Vijayapura": (16.8300, 75.7100, 590.0),
        "Yadgir": (16.7700, 77.1300, 730.0),
    },
    "Kerala": {
        "Alappuzha": (9.4981, 76.3388, 2950.0),
        "Ernakulam": (9.9816, 76.2999, 3100.0),
        "Idukki": (9.8500, 76.9800, 3600.0),
        "Kannur": (11.8745, 75.3704, 3400.0),
        "Kasaragod": (12.5102, 74.9852, 3550.0),
        "Kollam": (8.8932, 76.6141, 2600.0),
        "Kottayam": (9.5916, 76.5222, 3050.0),
        "Kozhikode": (11.2588, 75.7804, 3450.0),
        "Malappuram": (11.0732, 76.0740, 2800.0),
        "Palakkad": (10.7867, 76.6548, 2250.0),
        "Pathanamthitta": (9.2648, 76.7870, 2750.0),
        "Thiruvananthapuram": (8.5241, 76.9366, 1820.0),
        "Thrissur": (10.5276, 76.2144, 3050.0),
        "Wayanad": (11.6854, 76.1320, 3250.0),
    },
    "Madhya Pradesh": {
        "Balaghat": (21.8000, 80.1800, 1380.0),
        "Betul": (21.9000, 77.9000, 1080.0),
        "Bhopal": (23.2599, 77.4126, 1120.0),
        "Chhindwara": (22.0500, 78.9300, 1100.0),
        "Dewas": (22.9600, 76.0500, 980.0),
        "Dhar": (22.6000, 75.3000, 850.0),
        "Gwalior": (26.2183, 78.1828, 800.0),
        "Hoshangabad": (22.7500, 77.7200, 1300.0),
        "Indore": (22.7196, 75.8577, 960.0),
        "Jabalpur": (23.1815, 79.9864, 1250.0),
        "Khargone": (21.8200, 75.6100, 830.0),
        "Mandsaur": (24.0700, 75.0700, 820.0),
        "Raisen": (23.3300, 77.7800, 1200.0),
        "Ratlam": (23.3300, 75.0300, 890.0),
        "Rewa": (24.5300, 81.3000, 1100.0),
        "Sagar": (23.8300, 78.7300, 1180.0),
        "Satna": (24.5800, 80.8300, 1050.0),
        "Sehore": (23.2000, 77.0800, 1150.0),
        "Ujjain": (23.1765, 75.7885, 900.0),
    },
    "Maharashtra": {
        "Ahmednagar": (19.0952, 74.7480, 580.0),
        "Akola": (20.7002, 77.0082, 780.0),
        "Amravati": (20.9320, 77.7523, 850.0),
        "Aurangabad": (19.8762, 75.3433, 725.0),
        "Beed": (18.9891, 75.7601, 660.0),
        "Bhandara": (21.1700, 79.6500, 1320.0),
        "Buldhana": (20.5300, 76.1800, 750.0),
        "Chandrapur": (19.9615, 79.2961, 1200.0),
        "Dhule": (20.9000, 74.7800, 670.0),
        "Gadchiroli": (20.1800, 80.0000, 1420.0),
        "Gondia": (21.4600, 80.2000, 1350.0),
        "Hingoli": (19.7200, 77.1500, 890.0),
        "Jalgaon": (21.0077, 75.5626, 690.0),
        "Jalna": (19.8400, 75.8800, 710.0),
        "Kolhapur": (16.7050, 74.2433, 1020.0),
        "Latur": (18.4088, 76.5604, 790.0),
        "Mumbai": (19.0760, 72.8777, 2400.0),
        "Nagpur": (21.1458, 79.0882, 1050.0),
        "Nanded": (19.1383, 77.3210, 890.0),
        "Nandurbar": (21.3700, 74.2300, 850.0),
        "Nashik": (19.9975, 73.7898, 810.0),
        "Osmanabad": (18.1700, 76.0400, 760.0),
        "Palghar": (19.6967, 72.7699, 2250.0),
        "Parbhani": (19.2600, 76.7700, 820.0),
        "Pune": (18.5204, 73.8567, 750.0),
        "Raigad": (18.5158, 73.1822, 3100.0),
        "Ratnagiri": (16.9902, 73.3120, 3200.0),
        "Sangli": (16.8524, 74.5815, 620.0),
        "Satara": (17.6805, 73.9932, 920.0),
        "Sindhudurg": (16.1200, 73.7000, 3350.0),
        "Solapur": (17.6599, 75.9064, 650.0),
        "Thane": (19.2183, 72.9781, 2500.0),
        "Wardha": (20.7453, 78.6022, 1020.0),
        "Washim": (20.1100, 77.1300, 820.0),
        "Yavatmal": (20.3888, 78.1204, 910.0),
    },
    "Odisha": {
        "Balasore": (21.4900, 86.9300, 1580.0),
        "Cuttack": (20.4625, 85.8828, 1450.0),
        "Ganjam": (19.3800, 85.0500, 1300.0),
        "Kalahandi": (19.9100, 83.1200, 1350.0),
        "Khordha": (20.1800, 85.6200, 1480.0),
        "Koraput": (18.8100, 82.7100, 1520.0),
        "Mayurbhanj": (21.9300, 86.7300, 1600.0),
        "Puri": (19.8135, 85.8312, 1400.0),
        "Sambalpur": (21.4669, 83.9812, 1480.0),
        "Sundargarh": (22.1200, 84.0300, 1420.0),
    },
    "Punjab": {
        "Amritsar": (31.6340, 74.8723, 700.0),
        "Bathinda": (30.2110, 74.9455, 420.0),
        "Faridkot": (30.6700, 74.7500, 440.0),
        "Firozpur": (30.9200, 74.6100, 480.0),
        "Gurdaspur": (32.0400, 75.4000, 880.0),
        "Hoshiarpur": (31.5300, 75.9100, 920.0),
        "Jalandhar": (31.3260, 75.5762, 710.0),
        "Ludhiana": (30.9010, 75.8573, 680.0),
        "Mansa": (29.9800, 75.3800, 390.0),
        "Moga": (30.8100, 75.1700, 520.0),
        "Patiala": (30.3398, 76.3869, 690.0),
        "Sangrur": (30.2400, 75.8400, 540.0),
    },
    "Rajasthan": {
        "Ajmer": (26.4499, 74.6399, 520.0),
        "Alwar": (27.5530, 76.6346, 640.0),
        "Banswara": (23.5461, 74.4349, 920.0),
        "Barmer": (25.7500, 71.4000, 275.0),
        "Bharatpur": (27.2152, 77.5030, 660.0),
        "Bhilwara": (25.3500, 74.6300, 620.0),
        "Bikaner": (28.0229, 73.3119, 260.0),
        "Chittorgarh": (24.8887, 74.6269, 740.0),
        "Churu": (28.2900, 74.9600, 350.0),
        "Ganganagar": (29.9200, 73.8800, 250.0),
        "Jaipur": (26.9124, 75.7873, 600.0),
        "Jaisalmer": (26.9157, 70.9083, 190.0),
        "Jalore": (25.3500, 72.6100, 420.0),
        "Jhalawar": (24.5900, 76.1600, 950.0),
        "Jhunjhunu": (28.1300, 75.4000, 480.0),
        "Jodhpur": (26.2389, 73.0243, 360.0),
        "Kota": (25.2138, 75.8648, 800.0),
        "Nagaur": (27.2000, 73.7400, 390.0),
        "Pali": (25.7700, 73.3200, 480.0),
        "Sikar": (27.6100, 75.1400, 460.0),
        "Sri Ganganagar": (29.9200, 73.8800, 250.0),
        "Tonk": (26.1600, 75.7800, 610.0),
        "Udaipur": (24.5854, 73.7125, 650.0),
    },
    "Tamil Nadu": {
        "Chennai": (13.0827, 80.2707, 1400.0),
        "Coimbatore": (11.0168, 76.9558, 650.0),
        "Cuddalore": (11.7500, 79.7500, 1350.0),
        "Dharmapuri": (12.1300, 78.1600, 880.0),
        "Dindigul": (10.3600, 77.9800, 820.0),
        "Erode": (11.3410, 77.7172, 700.0),
        "Kanchipuram": (12.8342, 79.7036, 1250.0),
        "Kanyakumari": (8.0883, 77.5385, 1450.0),
        "Madurai": (9.9252, 78.1198, 850.0),
        "Nagapattinam": (10.7600, 79.8400, 1380.0),
        "Nilgiris": (11.4100, 76.7000, 1900.0),
        "Salem": (11.6643, 78.1460, 920.0),
        "Thanjavur": (10.7870, 79.1378, 1100.0),
        "Tiruchirappalli": (10.7905, 78.7047, 840.0),
        "Tirunelveli": (8.7139, 77.7567, 810.0),
        "Vellore": (12.9165, 79.1325, 1020.0),
    },
    "Telangana": {
        "Adilabad": (19.6641, 78.5320, 1080.0),
        "Hyderabad": (17.3850, 78.4867, 820.0),
        "Karimnagar": (18.4386, 79.1288, 950.0),
        "Khammam": (17.2473, 80.1514, 1050.0),
        "Mahabubnagar": (16.7488, 77.9982, 630.0),
        "Medak": (18.0454, 78.2612, 880.0),
        "Nalgonda": (17.0577, 79.2684, 750.0),
        "Nizamabad": (18.6725, 78.0941, 1020.0),
        "Ranga Reddy": (17.4300, 78.3500, 820.0),
        "Warangal": (17.9689, 79.5941, 980.0),
    },
    "Uttar Pradesh": {
        "Agra": (27.1767, 78.0081, 680.0),
        "Aligarh": (27.8974, 78.0880, 750.0),
        "Allahabad": (25.4358, 81.8463, 980.0),
        "Ayodhya": (26.7922, 82.1998, 1020.0),
        "Bareilly": (28.3670, 79.4304, 1050.0),
        "Gorakhpur": (26.7606, 83.3732, 1220.0),
        "Jhansi": (25.4484, 78.5685, 850.0),
        "Kanpur Nagar": (26.4499, 80.3319, 850.0),
        "Lucknow": (26.8467, 80.9462, 950.0),
        "Mathura": (27.4924, 77.6737, 600.0),
        "Meerut": (28.9845, 77.7064, 840.0),
        "Moradabad": (28.8386, 78.7733, 970.0),
        "Muzaffarnagar": (29.4727, 77.7085, 880.0),
        "Saharanpur": (29.9640, 77.5460, 960.0),
        "Varanasi": (25.3176, 82.9739, 1050.0),
    },
    "Uttarakhand": {
        "Dehradun": (30.3165, 78.0322, 2050.0),
        "Haridwar": (29.9457, 78.1642, 1180.0),
        "Nainital": (29.3919, 79.4542, 1750.0),
        "Pithoragarh": (29.5800, 80.2200, 1450.0),
        "Udham Singh Nagar": (28.9800, 79.4000, 1350.0),
    },
    "West Bengal": {
        "Bankura": (23.2300, 87.0700, 1400.0),
        "Bardhaman": (23.2324, 87.8615, 1350.0),
        "Birbhum": (23.8500, 87.6200, 1380.0),
        "Darjeeling": (27.0410, 88.2663, 2800.0),
        "Hooghly": (22.9000, 88.3900, 1500.0),
        "Howrah": (22.5958, 88.2636, 1600.0),
        "Jalpaiguri": (26.5400, 88.7200, 3150.0),
        "Kolkata": (22.5726, 88.3639, 1650.0),
        "Malda": (25.0000, 88.1500, 1420.0),
        "Murshidabad": (24.1800, 88.2700, 1380.0),
        "Nadia": (23.4700, 88.5500, 1450.0),
        "North 24 Parganas": (22.7200, 88.4800, 1620.0),
        "Paschim Bardhaman": (23.6800, 86.9800, 1320.0),
        "Paschim Medinipur": (22.4200, 87.3200, 1550.0),
        "Purba Bardhaman": (23.2324, 87.8615, 1350.0),
        "Purba Medinipur": (21.9400, 87.7800, 1680.0),
        "Purulia": (23.3300, 86.3600, 1280.0),
        "South 24 Parganas": (22.1800, 88.5500, 1750.0),
    },
    "Delhi": {
        "New Delhi": (28.6139, 77.2090, 750.0),
        "Central Delhi": (28.6400, 77.2200, 750.0),
        "North Delhi": (28.7000, 77.1500, 740.0),
        "South Delhi": (28.5300, 77.2100, 760.0),
        "East Delhi": (28.6300, 77.2900, 750.0),
        "West Delhi": (28.6600, 77.0800, 730.0),
    },
    "Jammu and Kashmir": {
        "Anantnag": (33.7300, 75.1500, 820.0),
        "Baramulla": (34.2000, 74.3400, 850.0),
        "Jammu": (32.7266, 74.8570, 1150.0),
        "Srinagar": (34.0837, 74.7973, 710.0),
        "Udhampur": (32.9300, 75.1400, 1350.0),
    },
    "Ladakh": {
        "Kargil": (34.5539, 76.1349, 280.0),
        "Leh": (34.1526, 77.5771, 115.0),
    },
    "Puducherry": {
        "Puducherry": (11.9416, 79.8083, 1350.0),
        "Karaikal": (10.9254, 79.8380, 1400.0),
        "Mahe": (11.7000, 75.5300, 3200.0),
        "Yanam": (16.7300, 82.2100, 1220.0),
    },
    "Chandigarh": {
        "Chandigarh": (30.7333, 76.7794, 1050.0),
    }
}

# Weather code descriptions from WMO Weather Interpretation Codes
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


class WeatherService:
    """
    Agro-meteorological and climate intelligence service.
    Retrieves real-time atmospheric readings and official IMD normal rainfall statistics.
    """

    @classmethod
    def _find_district_coords(cls, state: str, district: str) -> Tuple[float, float, float]:
        """
        Resolves latitude, longitude, and IMD normal annual rainfall for a state and district.
        """
        # 1. Exact lookup
        state_data = DISTRICT_CLIMATE_DATABASE.get(state)
        if state_data:
            if district in state_data:
                return state_data[district]
            # Case-insensitive match in state
            for d_name, info in state_data.items():
                if d_name.lower().strip() == district.lower().strip():
                    return info

        # 2. Case-insensitive search across all states
        for s_name, d_map in DISTRICT_CLIMATE_DATABASE.items():
            if s_name.lower().strip() == state.lower().strip():
                for d_name, info in d_map.items():
                    if d_name.lower().strip() == district.lower().strip():
                        return info

        # 3. Global district search
        for s_name, d_map in DISTRICT_CLIMATE_DATABASE.items():
            for d_name, info in d_map.items():
                if d_name.lower().strip() == district.lower().strip():
                    return info

        # 4. Regional Fallback based on State
        default_state_averages: Dict[str, Tuple[float, float, float]] = {
            "Maharashtra": (19.75, 75.71, 1050.0),
            "Gujarat": (22.25, 71.19, 820.0),
            "Karnataka": (15.31, 75.71, 1150.0),
            "Punjab": (31.14, 75.34, 650.0),
            "Tamil Nadu": (11.12, 78.65, 950.0),
            "Uttar Pradesh": (26.84, 80.94, 900.0),
            "West Bengal": (22.98, 87.85, 1500.0),
            "Madhya Pradesh": (22.97, 78.65, 1050.0),
            "Rajasthan": (27.02, 74.21, 550.0),
            "Kerala": (10.85, 76.27, 2900.0),
            "Andhra Pradesh": (15.91, 79.74, 900.0),
            "Telangana": (18.11, 79.01, 950.0),
            "Bihar": (25.09, 85.31, 1150.0),
            "Odisha": (20.95, 85.09, 1450.0),
            "Assam": (26.20, 92.93, 2200.0),
            "Haryana": (29.05, 76.08, 600.0),
            "Himachal Pradesh": (31.10, 77.17, 1350.0),
        }

        for s_name, fallback_info in default_state_averages.items():
            if s_name.lower() in state.lower():
                return fallback_info

        # Default Central India coordinates & National normal rainfall
        return (21.1458, 79.0882, 1083.0)

    @classmethod
    def get_weather(cls, state: str, district: str) -> WeatherData:
        """
        Fetches live ambient meteorological readings and IMD normal rainfall for a location.
        """
        state_clean = state.strip()
        district_clean = district.strip()
        location_name = f"{district_clean}, {state_clean}, India"

        lat, lon, annual_rainfall = cls._find_district_coords(state_clean, district_clean)

        # Default fallback values based on seasonal normals
        temperature: float = 27.5
        humidity: float = 65.0
        weather_desc: str = "Clear weather"
        source: str = "Open-Meteo Weather API & IMD Climate Normals"

        # Attempt to query live weather from Open-Meteo API
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat:.4f}&longitude={lon:.4f}&"
                f"current=temperature_2m,relative_humidity_2m,weather_code&"
                f"timezone=auto"
            )
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AgriPulse-AI/1.0 (Precision Agriculture Research Platform)"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode("utf-8"))
                    current = payload.get("current", {})
                    if "temperature_2m" in current and current["temperature_2m"] is not None:
                        temperature = round(float(current["temperature_2m"]), 1)
                    if "relative_humidity_2m" in current and current["relative_humidity_2m"] is not None:
                        humidity = round(float(current["relative_humidity_2m"]), 1)
                    if "weather_code" in current and current["weather_code"] is not None:
                        w_code = int(current["weather_code"])
                        weather_desc = WMO_WEATHER_CODES.get(w_code, "Partly cloudy")
                    logger.info(
                        f"Retrieved live weather for {location_name}: "
                        f"{temperature}°C, {humidity}%, {weather_desc}"
                    )
        except Exception as e:
            logger.warning(
                f"Live weather API fetch failed for {location_name} ({e}). "
                f"Using district seasonal climate baseline."
            )
            source = "IMD District Agro-Climatic Normal Profile"
            # Estimate realistic ambient temperature and humidity based on latitude and rainfall
            if annual_rainfall > 2000:
                humidity = 82.0
                temperature = 25.0
            elif annual_rainfall < 500:
                humidity = 35.0
                temperature = 31.0
            else:
                humidity = 62.0
                temperature = 28.0

        # Calculate agriculturally relevant crop-cycle rainfall (derived from annual precipitation)
        # In typical Indian agro-climatic conditions, seasonal crop cycle accounts for ~15-25% of annual rainfall
        crop_cycle_rainfall = round(min(295.0, max(35.0, annual_rainfall * 0.18)), 1)

        now_iso = datetime.now(timezone.utc).isoformat()

        return WeatherData(
            state=state_clean,
            district=district_clean,
            location_name=location_name,
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            temperature=temperature,
            humidity=humidity,
            annual_rainfall=round(annual_rainfall, 1),
            rainfall=round(annual_rainfall, 1), # Full annual rainfall passed as primary metric
            weather_condition=weather_desc,
            source=source,
            fetched_at=now_iso
        )
