(function(){
    const presets = {
        saas: {fixed_costs:10000, price:20, variable_cost:5, initial_sales:100, monthly_growth:0.06, months:24},
        freemium: {fixed_costs:7000, price:10, variable_cost:2, initial_sales:500, monthly_growth:0.05, months:18},
        ecommerce: {fixed_costs:8000, price:50, variable_cost:30, initial_sales:300, monthly_growth:0.04, months:12},
        marketplace: {fixed_costs:12000, price:5, variable_cost:2, initial_sales:1000, monthly_growth:0.08, months:12},
        consulting: {fixed_costs:3000, price:200, variable_cost:20, initial_sales:10, monthly_growth:0.03, months:12},
        hardware: {fixed_costs:25000, price:300, variable_cost:150, initial_sales:50, monthly_growth:0.02, months:24}
    };

    const descriptions = {
        saas: 'SaaS: recurring revenue model — lower initial sales, steady growth and high lifetime value.',
        freemium: 'Freemium: many free users, small conversion to paid — focuses on volume and conversion.',
        ecommerce: 'E‑commerce: product sales with per-unit margins and faster turnover.',
        marketplace: 'Marketplace: high volume, low take-rate per transaction — growth scales with network effects.',
        consulting: 'Consulting: small number of high-ticket clients with strong margins.',
        hardware: 'Hardware: large upfront costs and higher variable costs with slower growth.'
    };

    function toQuery(obj){
        return Object.keys(obj).map(k => encodeURIComponent(k) + '=' + encodeURIComponent(obj[k])).join('&');
    }

    function formatKES(n){
        try{
            const num = Number(n);
            return 'KES ' + num.toLocaleString('en-KE');
        }catch(e){
            return 'KES ' + n;
        }
    }

    document.addEventListener('DOMContentLoaded', function(){
        const start = document.getElementById('start-btn');
        const demo = document.getElementById('demo-btn');
        const select = document.getElementById('persona-select');

        // Helper to clean numeric string (strip KES, commas, spaces)
        function cleanNumberString(s){
            if(s === null || s === undefined) return '';
            return String(s).replace(/[^0-9.\-]/g,'');
        }

        if(start){
            start.addEventListener('click', function(){
                const persona = select.value || 'saas';
                const params = {};
                // collect values from preview inputs if present
                const preview = document.getElementById('persona-defaults');
                if(preview){
                    preview.querySelectorAll('input[data-key]').forEach(inp => {
                        const k = inp.dataset.key;
                        let raw = cleanNumberString(inp.value);
                        let val;
                        if(k === 'monthly_growth') val = parseFloat(raw || 0);
                        else val = Number(raw || 0);
                        params[k] = val;
                    });
                }
                // fallback to presets
                const base = presets[persona] || presets.saas;
                Object.keys(base).forEach(k => { if(!(k in params)) params[k] = base[k]; });
                const qs = toQuery(params);
                // Navigate to simulator with GET params to prefill
                window.location.href = '/simulator' + '?' + qs;
            });
        }

        // update description when persona changes
        function updateDesc(){
            const descEl = document.getElementById('persona-desc');
            if(!descEl) return;
            const p = select.value || 'saas';
            descEl.textContent = descriptions[p] || 'Select a persona to see a short description and defaults.';
        }

        if(select){
            select.addEventListener('change', updateDesc);
        }

        // update preview inputs for selected persona (editable)
        function updatePreview(){
            const preview = document.getElementById('persona-defaults');
            if(!preview) return;
            const p = select.value || 'saas';
            const params = presets[p] || presets.saas;
            preview.innerHTML = '';
            Object.keys(params).forEach(k => {
                const wrap = document.createElement('div');
                wrap.style.display = 'flex';
                wrap.style.flexDirection = 'column';
                wrap.style.marginRight = '8px';

                    const input = document.createElement('input');
                    input.type = 'number';
                    input.step = (k === 'monthly_growth') ? '0.01' : '1';
                    input.value = params[k];
                    input.dataset.key = k;
                    input.className = 'preview-input';

                const label = document.createElement('small');
                label.className = 'text-small';
                label.style.marginTop = '6px';
                if(['fixed_costs','price','variable_cost'].includes(k)){
                    const formatted = formatKES(params[k]);
                    label.textContent = k.replace(/_/g,' ') + ' • ' + formatted;
                } else {
                    label.textContent = k.replace(/_/g,' ');
                }

                // For monetary fields, add a KES prefix container
                if(['fixed_costs','price','variable_cost'].includes(k)){
                    const prefixWrap = document.createElement('div');
                    prefixWrap.className = 'input-with-prefix';
                    const prefix = document.createElement('span');
                    prefix.className = 'input-prefix';
                    prefix.textContent = 'KES';
                    prefixWrap.appendChild(prefix);
                    prefixWrap.appendChild(input);
                    wrap.appendChild(prefixWrap);
                } else {
                    wrap.appendChild(input);
                }
                wrap.appendChild(label);
                preview.appendChild(wrap);
            });
        }
        if(select){
            select.addEventListener('change', updatePreview);
        }

        // Input masking: show formatted value on blur, raw numeric on focus
        function formatForDisplayNumeric(n){
            if(n === '' || n === null || n === undefined) return '';
            const num = Number(String(n).replace(/[^0-9.\-]/g,''));
            if(isNaN(num)) return '';
            return 'KES ' + num.toLocaleString('en-KE');
        }

        const previewRoot = document.getElementById('persona-defaults');
        if(previewRoot){
            previewRoot.addEventListener('focusin', function(ev){
                const t = ev.target;
                if(t && t.tagName === 'INPUT'){
                    // on focus, remove formatting
                    t.value = cleanNumberString(t.value);
                }
            });
            previewRoot.addEventListener('focusout', function(ev){
                const t = ev.target;
                if(t && t.tagName === 'INPUT'){
                    const k = t.dataset.key;
                    if(['fixed_costs','price','variable_cost'].includes(k)){
                        // format with KES prefix and commas
                        t.value = formatForDisplayNumeric(t.value);
                    }
                }
            });
        }

        if(demo){
            demo.addEventListener('click', function(){
                const params = presets.saas;
                window.location.href = '/simulator' + '?' + toQuery(params);
            });
        }

        // Small entrance animation
        const hero = document.querySelector('.hero');
        if(hero){
            hero.style.opacity = '0';
            hero.style.transform = 'translateY(10px)';
            setTimeout(()=>{
                hero.style.transition = 'all 400ms ease';
                hero.style.opacity = '1';
                hero.style.transform = 'translateY(0)';
            }, 80);
        }
        updateDesc();
        updatePreview();

        // Walkthrough modal on first visit
        const modal = document.getElementById('walkthrough-modal');
        const seen = localStorage.getItem('seen_walkthrough');
        function closeModal(){
            if(modal) modal.style.display = 'none';
        }
        if(modal && !seen){
            modal.style.display = 'block';
            const closeBtn = document.getElementById('walk-close');
            const startBtn = document.getElementById('walk-start');
            const dont = document.getElementById('dont-show');
            closeBtn && closeBtn.addEventListener('click', closeModal);
            startBtn && startBtn.addEventListener('click', function(){
                if(dont && dont.checked) localStorage.setItem('seen_walkthrough', '1');
                // forward to simulator using current preview values
                start && start.click();
            });
        }
    });
})();
