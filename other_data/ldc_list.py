# LDC list from the UN Official website [https://unctad.org/topic/least-developed-countries/list]
import pycountry
country_names = [
    "Afghanistan", "Angola", "Benin", "Burkina Faso", "Burundi", "Central African Republic", "Chad", "Comoros", 
    "Congo, The Democratic Republic of the", "Djibouti", "Eritrea", "Ethiopia", "Gambia", "Guinea", "Guinea-Bissau", 
    "Lesotho", "Liberia", "Madagascar", "Malawi", "Mali", "Mauritania", "Mozambique", "Niger", "Rwanda", 
    "Sao Tome and Principe", "Senegal", "Sierra Leone", "Somalia", "South Sudan", "Sudan", "Togo", "Uganda", 
    "Tanzania, United Republic of", "Zambia", "Bangladesh", "Cambodia", "Lao People's Democratic Republic", 
    "Myanmar", "Nepal", "Timor-Leste", "Yemen", "Haiti", "Kiribati", "Solomon Islands", "Tuvalu"
]
# Convert country names to ISO 3166-1 alpha-3 codes
ldc_countries = []
for name in country_names:
    try:
        country = pycountry.countries.get(name=name)
        ldc_countries.append(country.alpha_3)
    except Exception as e:
        print(f"Could not find ISO code for {name}: {e}")
