from scenarios import list_scenarios

scenario_names = list_scenarios()
print("Scenario names:", scenario_names)

# Build scenarios table HTML
if scenario_names:
    rows = ''.join('<tr><td><strong>{0}</strong></td><td><a href="/scenarios/delete/{0}" class="btn-sm" onclick="return confirm(\'Delete {0}?\')">Delete</a></td></tr>'.format(name) for name in scenario_names)
    scenarios_table = '<table><thead><tr><th>Scenario Name</th><th>Action</th></tr></thead><tbody>' + rows + '</tbody></table>'
    print("Table created successfully")
    
    # Build load section
    options = ''.join('<option value="{0}">{0}</option>'.format(name) for name in scenario_names)
    load_section = '<div class="card" style="margin-block-start: 20px;"><h3>Load Saved Scenario</h3><form action="/scenarios/load" method="post"><div class="form-group"><select name="scenario_name" required>' + options + '</select></div><button type="submit">Load</button></form></div>'
    print("Load section created successfully")
else:
    scenarios_table = '<p class="text-muted">No scenarios saved yet.</p>'
    print("No scenarios")

print("\nTest passed!")
