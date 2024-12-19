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

const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
    if(this.checked) {
        document.body.classList.add('dark');
        } else {
            document.body.classList.remove('dark');
        }
    })

    const searchInput = document.getElementById('search-input');
    const serviceTable = document.querySelector('.table-data table');
    const originalRows = Array.from(serviceTable.querySelectorAll('tbody tr'));

    searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase();
    const filteredRows = originalRows.filter(row => {
    const usernameCell = row.querySelector('td:first-child'); 
    const username = usernameCell.textContent.toLowerCase();
    const nameCell = row.querySelector('td:nth-child(2)');
    const name = nameCell.textContent.toLowerCase();
        return username.includes(searchTerm) || name.includes(searchTerm);
    });
    serviceTable.querySelector('tbody').innerHTML = ''; 
    filteredRows.forEach(row => serviceTable.querySelector('tbody').appendChild(row));
    });

    const roleFilter = document.getElementById('role-filter'); 
    roleFilter.addEventListener('change', () => {
    const selectedRole = roleFilter.value;
    const filteredRows = originalRows.filter(row => {
    const roleCell = row.querySelector('td:nth-child(3)'); 
    const role = roleCell.textContent.trim(); 
        return selectedRole === '' || role.toLowerCase() === selectedRole; 
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

    const serviceModal = document.getElementById('userModal');
    const userUsername = document.getElementById('userUsername');
    const userFirstname = document.getElementById('userFirstname');
    const userLastname = document.getElementById('userLastname');
    const userEmail = document.getElementById('userEmail');
    const userBirthday = document.getElementById('userBirthday');

    function openModal(username, first_name, last_name, email, birthdate, profilePicture, contact_info = 'N/A', address = 'N/A') {
        document.getElementById('userUsername').textContent = username;
        document.getElementById('userFirstname').textContent = first_name;
        document.getElementById('userLastname').textContent = last_name;
        document.getElementById('userEmail').textContent = email;
        document.getElementById('userBirthday').textContent = birthdate;
        document.getElementById('userContactInfo').textContent = contact_info;
        document.getElementById('userAddress').textContent = address;
        document.getElementById('userProfilePicture').src = profilePicture || 'path/to/default/picture.jpg';
    
        document.getElementById('userModal').style.display = 'block';
    }

    function closeModal() {
        document.getElementById('userModal').style.display = 'none';
    }

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        const modal = document.getElementById('userModal');
        if (event.target == modal) {
            closeModal();
        }
    }

    function openAddUserModal() {
        document.getElementById("addUserModal").style.display = "block";
    }

    function closeAddUserModal() {
        document.getElementById("addUserModal").style.display = "none";
    }

    function showSpecialization() {
        var roleSelect = document.getElementById("role");
        var specializationDiv = document.getElementById("specialization");
        var subjectDiv = document.getElementById("subject");
            
        if (roleSelect.value === "therapist") {
            specializationDiv.style.display = "block";
            subjectDiv.style.display = "none";
        } else if (roleSelect.value === "educator") {
            subjectDiv.style.display = "block";
            specializationDiv.style.display = "none";
        } else {
            specializationDiv.style.display = "none";
            subjectDiv.style.display = "none";
        }
    }

    function openEditUserModal(userId, firstName, lastName, username, email, role) {
        const editUserForm = document.getElementById("editUserForm");
        editUserForm.action = `/edit_user/${userId}/`;  // Ensure userId is appended correctly
    
        // Populate the form fields with user data
        document.getElementById("first_name").value = firstName;
        document.getElementById("last_name").value = lastName;
        document.getElementById("username").value = username;
        document.getElementById("email").value = email;
        document.getElementById("role").value = role;
    
        // Show the modal
        document.getElementById("editUserModal").style.display = "block";
    }

    function closeEditUserModal() {
        document.getElementById('editUserModal').style.display = 'none';
    }

    function toggleFieldsBasedOnRole() {
        const role = document.getElementById('role').value;
        document.getElementById('specializationGroup').style.display = role === 'therapist' ? 'block' : 'none';
        document.getElementById('subjectGroup').style.display = role === 'educator' ? 'block' : 'none';
    }

    // Hide the modal when clicking outside of it
    window.onclick = function(event) {
        const modal = document.getElementById('editUserModal');
        if (event.target == modal) {
            closeEditUserModal();
        }
    };