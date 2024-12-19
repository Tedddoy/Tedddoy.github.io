const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');
allSideMenu.forEach(item=> {
    const li = item.parentElement;

    item.addEventListener('click', function () {
        allSideMenu.forEach(i=> {
            i.parentElement.classList.remove('active');
        })
        li.classList.add('active');
    })
});

// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
    sidebar.classList.toggle('hide');
})


// search
const searchInput = document.getElementById('search-input');
const serviceTable = document.querySelector('.table-data table');
const originalRows = Array.from(serviceTable.querySelectorAll('tbody tr'));

searchInput.addEventListener('input', () => {
const searchTerm = searchInput.value.toLowerCase();
const filteredRows = originalRows.filter(row => {
    const serviceCell = row.querySelector('td:first-child'); 
    const service = serviceCell.textContent.toLowerCase();
    return service.includes(searchTerm);
});
serviceTable.querySelector('tbody').innerHTML = ''; 
filteredRows.forEach(row => serviceTable.querySelector('tbody').appendChild(row));
});


// filter
const categoryFilter = document.getElementById('category-filter'); 

categoryFilter.addEventListener('change', () => {
    const selectedCategory = categoryFilter.value;
    const filteredRows = originalRows.filter(row => {
        const categoryCell = row.querySelector('td:nth-child(4)'); 
        const category = categoryCell.textContent.trim(); 
        return selectedCategory === '' || category === selectedCategory; 
    });
    updateTable(filteredRows);
});

function updateTable(filteredRows) {
    const tableHeader = serviceTable.querySelector('thead');
    serviceTable.innerHTML = ''; 
    serviceTable.appendChild(tableHeader); 

    const tableBody = document.createElement('tbody');
    filteredRows.forEach(row => tableBody.appendChild(row));
    serviceTable.appendChild(tableBody);
}

function toggleFilterDropdown() {
    categoryFilterDropdown.classList.toggle('open');
}

// Modal Functions for Service Details
const serviceModal = document.getElementById('serviceModal');
const serviceName = document.getElementById('serviceName');
const servicePrice = document.getElementById('servicePrice');
const serviceAvailability = document.getElementById('serviceAvailability');
const serviceCategory = document.getElementById('serviceCategory');
const serviceDescription = document.getElementById('serviceDescription');

function openServiceModal(name, price, availability, category, description) {
    serviceName.textContent = name;
    servicePrice.textContent = price;
    serviceAvailability.textContent = availability;
    serviceCategory.textContent = category;
    serviceDescription.textContent = description;
    serviceModal.style.display = 'block';
}

function closeServiceModal() {
    serviceModal.style.display = 'none';
}

// Modal Functions for Add Service
const addServiceModal = document.getElementById('addServiceModal');

function openAddServiceModal() {
    addServiceModal.style.display = 'block';
}

function closeAddServiceModal() {
    addServiceModal.style.display = 'none';
}

// Modal Functions for Edit Service
function openEditServiceModal(serviceId, name, price, description, availability, categoryId) {
    document.getElementById('editServiceForm').action = `/update_service/${serviceId}/`;
    document.getElementById('editServiceName').value = name;
    document.getElementById('editServicePrice').value = price;
    document.getElementById('editServiceDescription').value = description;
    document.getElementById('editServiceAvailability').value = availability;
    document.getElementById('editServiceCategory').value = categoryId;
    document.getElementById('editServiceModal').style.display = 'block';
}
function closeEditServiceModal() { document.getElementById('editServiceModal').style.display = 'none'; }

// Modal Function for add therapist

function openAssignTherapistModal(serviceId, serviceName) {
    // Set service data in the modal
    document.getElementById("assignServiceId").value = serviceId;
    document.getElementById("serviceName").textContent = serviceName;

    // Show the modal
    document.getElementById("assignTherapistModal").style.display = "block";
}

function closeAssignTherapistModal() {
    document.getElementById("assignTherapistModal").style.display = "none";
}
