document.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM fully loaded and parsed");

    const form = document.getElementById('form'); 
    
    const phoneInput = document.getElementById('id_phone_number');
    const emailInput = document.getElementById('id_email');

    console.log("Znaleziono telefon:", phoneInput);
    console.log("Znaleziono email:", emailInput);


    function showError(input, message) {
        input.classList.add('is-invalid'); 
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback error-message'; 
        errorDiv.innerText = message;
        input.parentNode.appendChild(errorDiv); 
    }

    function clearErrors() {
        document.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(msg => {
            msg.remove();
        });
    }

    form.addEventListener('submit', (e) => {
        clearErrors(); 
        let hasErrors = false; 

        const phoneNumber = document.getElementById('id_phone_number');
        const email = document.getElementById('id_email');
        
        const phone = /^[0-9]{9}$/;

        if (phoneNumber && !phone.test(phoneNumber.value.trim())) {
            showError(phoneNumber, 'Podaj poprawny numer telefonu 9 cyfr.');
            hasErrors = true;
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (email && !emailRegex.test(email.value.trim())) {
            showError(email, 'Podaj poprawny adres email.');
            hasErrors = true;
        }
        

        if (hasErrors) {
            e.preventDefault();
        }
    });
});