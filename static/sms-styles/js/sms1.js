document.addEventListener('DOMContentLoaded', function () {
    const serverSelect = document.getElementById('server-id');
    const serviceSelect = document.getElementById('service-id');
    const buyButton = document.getElementById('buy-numbers');
    const token = document.getElementById('token').value;
    const numbersContainer = document.getElementById('numbers-container');

    function showError(message) {
        numbersContainer.innerHTML = `<div class="bg-red-100 text-red-700 p-4 rounded">${message}</div>`;
    }

    function getFlagEmoji(countryCode) {
        if (!countryCode) return '';
        const codePoints = countryCode.toUpperCase().split('').map(c => 127397 + c.charCodeAt(0));
        return String.fromCodePoint(...codePoints);
    }

    serverSelect.addEventListener('change', async () => {
        const serverId = serverSelect.value;
        if (!serverId) return;

        serviceSelect.disabled = true;
        serviceSelect.innerHTML = '<option disabled selected>Loading services...</option>';
        numbersContainer.innerHTML = '';

        try {
            const response = await fetch(`/api/service/getService.php?server=${serverId}`);
            const data = await response.json();

            if (!Array.isArray(data) || data.length === 0) {
                serviceSelect.innerHTML = '<option disabled selected>No services available</option>';
                showError('No services found for this server.');
                return;
            }

            serviceSelect.innerHTML = '<option disabled selected>Select Service</option>';
            data.forEach(service => {
                const option = document.createElement('option');
                option.value = service.project_code;
                option.textContent = `${service.project_name} - ₦${service.new_cost}`;
                option.dataset.name = service.project_name;
                option.dataset.cost = service.new_cost;
                serviceSelect.appendChild(option);
            });

            serviceSelect.disabled = false;
        } catch (error) {
            console.error('Service fetch error:', error);
            showError('Failed to load services.');
        }
    });

    serviceSelect.addEventListener('change', () => {
        buyButton.disabled = !serviceSelect.value;
    });

    buyButton.addEventListener('click', async () => {
    const serverId = serverSelect.value;
    const serviceCode = serviceSelect.value;
    const serviceOpt = serviceSelect.selectedOptions[0];

    if (!serverId || !serviceCode) {
        showError('Please select both server and service.');
        return;
    }

    const serviceName = encodeURIComponent(serviceOpt.dataset.name);
    const cost = encodeURIComponent(serviceOpt.dataset.cost);

    buyButton.disabled = true;
    numbersContainer.innerHTML = `<div class="text-blue-600">Processing purchase...</div>`;

    try {
        const response = await fetch(`/api/service/buynumber1.php?server=${serverId}&service=${serviceCode}&service_name=${serviceName}&service_price=${cost}&token=${token}`);
        const result = await response.json();

        if (parseInt(result.status) !== 200) {
            showError(result.message || 'Purchase failed.');
            return;
        }

        numbersContainer.innerHTML = `
            <div class="bg-green-100 text-green-800 p-4 rounded">
                <h3 class="font-bold mb-2">Number Purchased!</h3>
                <p><strong>Service:</strong> ${serviceOpt.dataset.name}</p>
                <p><strong>Cost:</strong> ₦${serviceOpt.dataset.cost}</p>
                <p><strong>Number:</strong> ${result.data?.number || 'N/A'}</p>
            </div>
        `;
    } catch (error) {
        console.error('Buy number error:', error);
        showError('An error occurred while purchasing.');
    } finally {
        buyButton.disabled = false;

        }
    });
});
