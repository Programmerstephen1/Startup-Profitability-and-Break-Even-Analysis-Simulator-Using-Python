import urllib.request
import urllib.parse
import time

presets = {
    'saas': {'fixed_costs':10000, 'price':20, 'variable_cost':5, 'initial_sales':100, 'monthly_growth':0.06, 'months':24},
    'freemium': {'fixed_costs':7000, 'price':10, 'variable_cost':2, 'initial_sales':500, 'monthly_growth':0.05, 'months':18},
    'ecommerce': {'fixed_costs':8000, 'price':50, 'variable_cost':30, 'initial_sales':300, 'monthly_growth':0.04, 'months':12},
    'marketplace': {'fixed_costs':12000, 'price':5, 'variable_cost':2, 'initial_sales':1000, 'monthly_growth':0.08, 'months':12},
    'consulting': {'fixed_costs':3000, 'price':200, 'variable_cost':20, 'initial_sales':10, 'monthly_growth':0.03, 'months':12},
    'hardware': {'fixed_costs':25000, 'price':300, 'variable_cost':150, 'initial_sales':50, 'monthly_growth':0.02, 'months':24},
}

base = 'http://127.0.0.1:5000/'
with open('persona_urls.txt', 'w', encoding='utf8') as out:
    for name, params in presets.items():
        qs = urllib.parse.urlencode(params)
        url = base + '?' + qs
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                content = r.read().decode('utf8')
            fname = f'persona_{name}.html'
            with open(fname, 'w', encoding='utf8') as f:
                f.write(content)
            out.write(f"{name} -> {url}\n")
            print(f"Saved {fname}")
        except Exception as e:
            out.write(f"{name} -> ERROR: {e}\n")
        time.sleep(0.2)
print('ALL_DONE')
